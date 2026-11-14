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


def _digits_upper_bound(value: int) -> int:
    """Conservative decimal digit upper bound without converting a huge int to str."""
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
        for name, value in (
            ("max_input_chars", self.max_input_chars),
            ("max_coefficient_digits", self.max_coefficient_digits),
            ("max_scale", self.max_scale),
            ("max_rational_numerator_digits", self.max_rational_numerator_digits),
            ("max_rational_denominator_digits", self.max_rational_denominator_digits),
            ("max_intermediate_digits", self.max_intermediate_digits),
            ("max_power10_exponent", self.max_power10_exponent),
        ):
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
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
        if _digits_upper_bound(value.coefficient) > self.limits.max_coefficient_digits:
            raise NumericLimitExceeded(f"{label} coefficient exceeds configured digit budget")
        return value

    def _check_rational(self, value: ExactRational) -> ExactRational:
        if not isinstance(value, ExactRational):
            raise TypeError("value must be ExactRational")
        if _digits_upper_bound(value.numerator) > self.limits.max_rational_numerator_digits:
            raise NumericLimitExceeded("rational numerator exceeds configured digit budget")
        if _digits_upper_bound(value.denominator) > self.limits.max_rational_denominator_digits:
            raise NumericLimitExceeded("rational denominator exceeds configured digit budget")
        return value

    def _check_intermediate(self, digits: int, operation: str) -> None:
        if digits > self.limits.max_intermediate_digits:
            raise NumericLimitExceeded(f"{operation} exceeds intermediate digit budget")

    def _check_power10(self, exponent: int, base_digits: int, operation: str) -> None:
        if exponent < 0 or exponent > self.limits.max_power10_exponent:
            raise NumericLimitExceeded(f"{operation} power-of-ten exponent exceeds configured maximum")
        self._check_intermediate(base_digits + exponent, operation)

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
        left_digits = _digits_upper_bound(left.coefficient) + scale - left.scale
        right_digits = _digits_upper_bound(right.coefficient) + scale - right.scale
        self._check_power10(scale - left.scale, _digits_upper_bound(left.coefficient), "addition alignment")
        self._check_power10(scale - right.scale, _digits_upper_bound(right.coefficient), "addition alignment")
        self._check_intermediate(max(left_digits, right_digits) + 1, "addition")
        return self._check_decimal(left + right, "addition result")

    def subtract(self, left: ExactDecimal, right: ExactDecimal) -> ExactDecimal:
        self._check_decimal(left, "left")
        self._check_decimal(right, "right")
        scale = max(left.scale, right.scale)
        left_digits = _digits_upper_bound(left.coefficient) + scale - left.scale
        right_digits = _digits_upper_bound(right.coefficient) + scale - right.scale
        self._check_power10(scale - left.scale, _digits_upper_bound(left.coefficient), "subtraction alignment")
        self._check_power10(scale - right.scale, _digits_upper_bound(right.coefficient), "subtraction alignment")
        self._check_intermediate(max(left_digits, right_digits) + 1, "subtraction")
        return self._check_decimal(left - right, "subtraction result")

    def multiply(self, left: ExactDecimal, right: ExactDecimal) -> ExactDecimal:
        self._check_decimal(left, "left")
        self._check_decimal(right, "right")
        scale = left.scale + right.scale
        if scale > self.limits.max_scale:
            raise NumericLimitExceeded("multiplication result scale exceeds configured maximum")
        self._check_intermediate(
            _digits_upper_bound(left.coefficient) + _digits_upper_bound(right.coefficient),
            "multiplication",
        )
        return self._check_decimal(left * right, "multiplication result")

    def divide_exact(self, numerator: ExactDecimal, denominator: ExactDecimal) -> ExactRational:
        self._check_decimal(numerator, "numerator")
        self._check_decimal(denominator, "denominator")
        if denominator.coefficient == 0:
            # Preserve the oracle's typed division-by-zero error.
            return numerator.divide_exact(denominator)
        num_digits = _digits_upper_bound(numerator.coefficient) + denominator.scale
        den_digits = _digits_upper_bound(denominator.coefficient) + numerator.scale
        self._check_power10(denominator.scale, _digits_upper_bound(numerator.coefficient), "division numerator")
        self._check_power10(numerator.scale, _digits_upper_bound(denominator.coefficient), "division denominator")
        self._check_intermediate(max(num_digits, den_digits), "division")
        if num_digits > self.limits.max_rational_numerator_digits:
            raise NumericLimitExceeded("division numerator pre-reduction exceeds rational digit budget")
        if den_digits > self.limits.max_rational_denominator_digits:
            raise NumericLimitExceeded("division denominator pre-reduction exceeds rational digit budget")
        return self._check_rational(numerator.divide_exact(denominator))

    def quantize_rational(
        self, value: ExactRational, target_scale: int, rounding: RoundingMode
    ) -> ExactDecimal:
        self._check_rational(value)
        if not isinstance(target_scale, int) or isinstance(target_scale, bool) or target_scale < 0:
            raise ValueError("target_scale must be a non-negative integer")
        if target_scale > self.limits.max_scale:
            raise NumericLimitExceeded("quantization target scale exceeds configured maximum")
        self._check_power10(
            target_scale, _digits_upper_bound(value.numerator), "rational quantization"
        )
        return self._check_decimal(value.quantize(target_scale, rounding), "quantization result")
