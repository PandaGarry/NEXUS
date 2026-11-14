"""Explicitly bounded exact-numeric reference context.

This is a test-only policy wrapper around the arbitrary-precision mathematical
oracle. Limits are mandatory caller inputs; no production profile is implied.
"""
from __future__ import annotations

from dataclasses import dataclass

from nexus_decimal import ExactDecimal, ExactRational, RoundingMode
from numeric_wire import parse_decimal as parse_decimal_wire, parse_rational as parse_rational_wire


class NumericLimitExceeded(ValueError):
    """An operation would exceed the explicitly configured numeric budget."""


def _decimal_digit_count(value: int) -> int:
    """Exact decimal digit count without converting a huge int to str."""
    magnitude = abs(value)
    if magnitude == 0:
        return 1
    # Start from a close lower estimate, then correct by exact integer comparison.
    # This avoids Python's configurable int-to-string digit limit.
    digits = ((magnitude.bit_length() - 1) * 30103) // 100000 + 1
    while magnitude >= 10 ** digits:
        digits += 1
    while digits > 1 and magnitude < 10 ** (digits - 1):
        digits -= 1
    return digits


@dataclass(frozen=True, slots=True)
class NumericLimits:
    max_input_chars: int
    max_coefficient_digits: int
    max_scale: int
    max_rational_numerator_digits: int
    max_rational_denominator_digits: int
    max_intermediate_digits: int
    max_power10_exponent: int

    def __post_init__(self) -> None:
        positive_limits = (
            ("max_input_chars", self.max_input_chars),
            ("max_coefficient_digits", self.max_coefficient_digits),
            ("max_rational_numerator_digits", self.max_rational_numerator_digits),
            ("max_rational_denominator_digits", self.max_rational_denominator_digits),
            ("max_intermediate_digits", self.max_intermediate_digits),
        )
        for name, value in positive_limits:
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        for name, value in (("max_scale", self.max_scale),
                            ("max_power10_exponent", self.max_power10_exponent)):
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.max_intermediate_digits < max(
            self.max_coefficient_digits,
            self.max_rational_numerator_digits,
            self.max_rational_denominator_digits,
        ):
            raise ValueError("max_intermediate_digits must cover all configured value digit limits")
        if self.max_power10_exponent > self.max_intermediate_digits:
            raise ValueError("max_power10_exponent cannot exceed max_intermediate_digits")


@dataclass(frozen=True, slots=True)
class BoundedNumericContext:
    limits: NumericLimits

    def _check_decimal(self, value: ExactDecimal, label: str = "decimal") -> ExactDecimal:
        if not isinstance(value, ExactDecimal):
            raise TypeError(f"{label} must be ExactDecimal")
        if value.scale > self.limits.max_scale:
            raise NumericLimitExceeded(f"{label} scale exceeds configured maximum")
        if _decimal_digit_count(value.coefficient) > self.limits.max_coefficient_digits:
            raise NumericLimitExceeded(f"{label} coefficient exceeds configured digit budget")
        return value

    def _check_rational(self, value: ExactRational) -> ExactRational:
        if not isinstance(value, ExactRational):
            raise TypeError("value must be ExactRational")
        if _decimal_digit_count(value.numerator) > self.limits.max_rational_numerator_digits:
            raise NumericLimitExceeded("rational numerator exceeds configured digit budget")
        if _decimal_digit_count(value.denominator) > self.limits.max_rational_denominator_digits:
            raise NumericLimitExceeded("rational denominator exceeds configured digit budget")
        return value

    def _check_intermediate(self, digits: int, operation: str) -> None:
        if digits > self.limits.max_intermediate_digits:
            raise NumericLimitExceeded(f"{operation} exceeds intermediate digit budget")

    def _check_power10(self, exponent: int, base_digits: int, operation: str) -> None:
        if exponent < 0 or exponent > self.limits.max_power10_exponent:
            raise NumericLimitExceeded(f"{operation} power-of-ten exponent exceeds configured maximum")
        self._check_intermediate(base_digits + exponent, operation)

    def _preflight_signed_sum(self, left: int, right: int, operation: str) -> None:
        """Reject same-sign sums that would exceed the intermediate digit budget."""
        if left == 0 or right == 0 or (left < 0) != (right < 0):
            return
        exclusive_limit = 10 ** self.limits.max_intermediate_digits
        if abs(left) >= exclusive_limit - abs(right):
            raise NumericLimitExceeded(f"{operation} exceeds intermediate digit budget")

    def _preflight_product(self, left: int, right: int) -> None:
        """Check the exact product bound using division before multiplying."""
        if left == 0 or right == 0:
            return
        max_product = (10 ** self.limits.max_intermediate_digits) - 1
        if abs(left) > max_product // abs(right):
            raise NumericLimitExceeded("multiplication exceeds intermediate digit budget")

    def parse_decimal(self, literal: str) -> ExactDecimal:
        if not isinstance(literal, str):
            raise TypeError("literal must be str")
        if len(literal) > self.limits.max_input_chars:
            raise NumericLimitExceeded("decimal input exceeds configured character limit")
        unsigned = literal[1:] if literal[:1] in "+-" else literal
        _, dot, fraction = unsigned.partition(".")
        if dot and len(fraction) > self.limits.max_scale:
            raise NumericLimitExceeded("decimal input scale exceeds configured maximum")
        return self._check_decimal(ExactDecimal.parse(literal), "parsed decimal")

    def validate_decimal(self, value: ExactDecimal) -> ExactDecimal:
        return self._check_decimal(value)

    def parse_decimal_wire(self, encoded: str) -> ExactDecimal:
        value = parse_decimal_wire(encoded, max_chars=self.limits.max_input_chars)
        return self._check_decimal(value, "wire decimal")

    def parse_rational_wire(self, encoded: str) -> ExactRational:
        value = parse_rational_wire(encoded, max_chars=self.limits.max_input_chars)
        return self._check_rational(value)

    def validate_rational(self, value: ExactRational) -> ExactRational:
        return self._check_rational(value)

    def add(self, left: ExactDecimal, right: ExactDecimal) -> ExactDecimal:
        self._check_decimal(left, "left")
        self._check_decimal(right, "right")
        scale = max(left.scale, right.scale)
        left_digits = _decimal_digit_count(left.coefficient) + scale - left.scale
        right_digits = _decimal_digit_count(right.coefficient) + scale - right.scale
        self._check_power10(scale - left.scale, _decimal_digit_count(left.coefficient), "addition alignment")
        self._check_power10(scale - right.scale, _decimal_digit_count(right.coefficient), "addition alignment")
        self._check_intermediate(max(left_digits, right_digits), "addition operands")
        left_scaled, right_scaled, _ = left._aligned(right)
        self._preflight_signed_sum(left_scaled, right_scaled, "addition")
        return self._check_decimal(left + right, "addition result")

    def subtract(self, left: ExactDecimal, right: ExactDecimal) -> ExactDecimal:
        self._check_decimal(left, "left")
        self._check_decimal(right, "right")
        scale = max(left.scale, right.scale)
        left_digits = _decimal_digit_count(left.coefficient) + scale - left.scale
        right_digits = _decimal_digit_count(right.coefficient) + scale - right.scale
        self._check_power10(scale - left.scale, _decimal_digit_count(left.coefficient), "subtraction alignment")
        self._check_power10(scale - right.scale, _decimal_digit_count(right.coefficient), "subtraction alignment")
        self._check_intermediate(max(left_digits, right_digits), "subtraction operands")
        left_scaled, right_scaled, _ = left._aligned(right)
        self._preflight_signed_sum(left_scaled, -right_scaled, "subtraction")
        return self._check_decimal(left - right, "subtraction result")

    def multiply(self, left: ExactDecimal, right: ExactDecimal) -> ExactDecimal:
        self._check_decimal(left, "left")
        self._check_decimal(right, "right")
        scale = left.scale + right.scale
        if scale > self.limits.max_scale:
            raise NumericLimitExceeded("multiplication result scale exceeds configured maximum")
        self._preflight_product(left.coefficient, right.coefficient)
        return self._check_decimal(left * right, "multiplication result")

    def divide_exact(self, numerator: ExactDecimal, denominator: ExactDecimal) -> ExactRational:
        self._check_decimal(numerator, "numerator")
        self._check_decimal(denominator, "denominator")
        if denominator.coefficient == 0:
            # Preserve the oracle's typed division-by-zero error.
            return numerator.divide_exact(denominator)
        num_digits = _decimal_digit_count(numerator.coefficient) + denominator.scale
        den_digits = _decimal_digit_count(denominator.coefficient) + numerator.scale
        self._check_power10(denominator.scale, _decimal_digit_count(numerator.coefficient), "division numerator")
        self._check_power10(numerator.scale, _decimal_digit_count(denominator.coefficient), "division denominator")
        self._check_intermediate(max(num_digits, den_digits), "division")
        if num_digits > self.limits.max_rational_numerator_digits:
            raise NumericLimitExceeded("division numerator pre-reduction exceeds rational digit budget")
        if den_digits > self.limits.max_rational_denominator_digits:
            raise NumericLimitExceeded("division denominator pre-reduction exceeds rational digit budget")
        return self._check_rational(numerator.divide_exact(denominator))

    def compare(self, left: ExactDecimal, right: ExactDecimal) -> int:
        self._check_decimal(left, "left")
        self._check_decimal(right, "right")
        scale = max(left.scale, right.scale)
        self._check_power10(scale - left.scale, _decimal_digit_count(left.coefficient), "comparison alignment")
        self._check_power10(scale - right.scale, _decimal_digit_count(right.coefficient), "comparison alignment")
        return left.compare(right)

    def is_multiple_of(self, value: ExactDecimal, step: ExactDecimal) -> bool:
        self._check_decimal(value, "value")
        self._check_decimal(step, "step")
        scale = max(value.scale, step.scale)
        self._check_power10(scale - value.scale, _decimal_digit_count(value.coefficient), "step alignment")
        self._check_power10(scale - step.scale, _decimal_digit_count(step.coefficient), "step alignment")
        return value.is_multiple_of(step)

    def to_decimal_exact(self, value: ExactRational) -> ExactDecimal:
        self._check_rational(value)
        remainder = value.denominator
        twos = fives = 0
        while remainder % 2 == 0:
            remainder //= 2
            twos += 1
        while remainder % 5 == 0:
            remainder //= 5
            fives += 1
        if remainder != 1:
            # Delegate to the oracle for its stable domain-specific exception.
            return value.to_decimal_exact()
        scale = max(twos, fives)
        if scale > self.limits.max_scale:
            raise NumericLimitExceeded("exact decimal conversion scale exceeds configured maximum")
        growth = max(scale - twos, scale - fives)
        self._check_intermediate(_decimal_digit_count(value.numerator) + growth, "exact decimal conversion")
        return self._check_decimal(value.to_decimal_exact(), "exact decimal conversion result")

    def quantize_rational(
        self, value: ExactRational, target_scale: int, rounding: RoundingMode
    ) -> ExactDecimal:
        self._check_rational(value)
        if not isinstance(target_scale, int) or isinstance(target_scale, bool) or target_scale < 0:
            raise ValueError("target_scale must be a non-negative integer")
        if target_scale > self.limits.max_scale:
            raise NumericLimitExceeded("quantization target scale exceeds configured maximum")
        self._check_power10(
            target_scale, _decimal_digit_count(value.numerator), "rational quantization"
        )
        return self._check_decimal(value.quantize(target_scale, rounding), "quantization result")
