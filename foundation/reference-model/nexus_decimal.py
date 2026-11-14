"""Exact, dependency-free decimal reference model for NEXUS conformance tests.

This is a test oracle, not a production trading component. It deliberately
supports only exact operations; rounding and division require an explicit,
separately approved policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import gcd
import re


class DecimalValueError(ValueError):
    """Base class for invalid exact-decimal operations."""


class InvalidDecimal(DecimalValueError):
    pass


class InexactQuantization(DecimalValueError):
    pass


class InvalidStep(DecimalValueError):
    pass


class DivisionByZero(DecimalValueError):
    pass


class InexactDivision(DecimalValueError):
    pass


class RoundingMode(str, Enum):
    """Explicit quotient rounding policy; no implicit default is provided."""

    UNNECESSARY = "UNNECESSARY"
    DOWN = "DOWN"          # toward zero
    UP = "UP"              # away from zero
    FLOOR = "FLOOR"        # toward negative infinity
    CEILING = "CEILING"    # toward positive infinity
    HALF_UP = "HALF_UP"    # ties away from zero
    HALF_EVEN = "HALF_EVEN"  # ties to even


_PATTERN = re.compile(r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)$")


def _pow10(power: int) -> int:
    if power < 0:
        raise ValueError("power must be non-negative")
    return 10 ** power


@dataclass(frozen=True, slots=True)
class ExactDecimal:
    """A finite base-10 value represented as coefficient * 10**(-scale)."""

    coefficient: int
    scale: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.coefficient, int) or isinstance(self.coefficient, bool):
            raise TypeError("coefficient must be an integer")
        if not isinstance(self.scale, int) or isinstance(self.scale, bool) or self.scale < 0:
            raise ValueError("scale must be a non-negative integer")
        coefficient, scale = self.coefficient, self.scale
        if coefficient == 0:
            object.__setattr__(self, "scale", 0)
            return
        while scale and coefficient % 10 == 0:
            coefficient //= 10
            scale -= 1
        object.__setattr__(self, "coefficient", coefficient)
        object.__setattr__(self, "scale", scale)

    @classmethod
    def parse(cls, text: str) -> "ExactDecimal":
        if not isinstance(text, str) or not _PATTERN.fullmatch(text):
            raise InvalidDecimal(f"invalid decimal literal: {text!r}")
        sign = -1 if text.startswith("-") else 1
        unsigned = text[1:] if text[:1] in "+-" else text
        whole, dot, fraction = unsigned.partition(".")
        whole = whole or "0"
        digits = (whole + fraction).lstrip("0") or "0"
        return cls(sign * int(digits), len(fraction) if dot else 0)

    def __str__(self) -> str:
        sign = "-" if self.coefficient < 0 else ""
        digits = str(abs(self.coefficient))
        if self.scale == 0:
            return sign + digits
        digits = digits.rjust(self.scale + 1, "0")
        return sign + digits[:-self.scale] + "." + digits[-self.scale:]

    def _aligned(self, other: "ExactDecimal") -> tuple[int, int, int]:
        scale = max(self.scale, other.scale)
        return (
            self.coefficient * _pow10(scale - self.scale),
            other.coefficient * _pow10(scale - other.scale),
            scale,
        )

    def __add__(self, other: "ExactDecimal") -> "ExactDecimal":
        if not isinstance(other, ExactDecimal):
            return NotImplemented
        left, right, scale = self._aligned(other)
        return ExactDecimal(left + right, scale)

    def __sub__(self, other: "ExactDecimal") -> "ExactDecimal":
        if not isinstance(other, ExactDecimal):
            return NotImplemented
        left, right, scale = self._aligned(other)
        return ExactDecimal(left - right, scale)

    def __mul__(self, other: "ExactDecimal") -> "ExactDecimal":
        if not isinstance(other, ExactDecimal):
            return NotImplemented
        return ExactDecimal(self.coefficient * other.coefficient, self.scale + other.scale)

    def compare(self, other: "ExactDecimal") -> int:
        if not isinstance(other, ExactDecimal):
            raise TypeError("other must be ExactDecimal")
        left, right, _ = self._aligned(other)
        return (left > right) - (left < right)

    def divide_exact(self, other: "ExactDecimal") -> "ExactRational":
        """Return an exact reduced rational; never rounds or truncates."""
        if not isinstance(other, ExactDecimal):
            raise TypeError("other must be ExactDecimal")
        if other.coefficient == 0:
            raise DivisionByZero("division by zero")
        numerator = self.coefficient * _pow10(other.scale)
        denominator = other.coefficient * _pow10(self.scale)
        return ExactRational(numerator, denominator)

    def quantize_exact(self, target_scale: int) -> "ExactDecimal":
        """Represent at target scale only if no information is discarded."""
        if not isinstance(target_scale, int) or isinstance(target_scale, bool) or target_scale < 0:
            raise ValueError("target_scale must be a non-negative integer")
        if target_scale >= self.scale:
            return ExactDecimal(self.coefficient * _pow10(target_scale - self.scale), target_scale)
        divisor = _pow10(self.scale - target_scale)
        if self.coefficient % divisor:
            raise InexactQuantization(
                f"{self} cannot be represented exactly at scale {target_scale}"
            )
        return ExactDecimal(self.coefficient // divisor, target_scale)

    def is_multiple_of(self, step: "ExactDecimal") -> bool:
        if not isinstance(step, ExactDecimal):
            raise TypeError("step must be ExactDecimal")
        if step.coefficient <= 0:
            raise InvalidStep("step must be positive")
        left, right, _ = self._aligned(step)
        return left % right == 0



@dataclass(frozen=True, slots=True)
class ExactRational:
    """Reduced exact rational used for intermediate division results."""

    numerator: int
    denominator: int

    def __post_init__(self) -> None:
        if not isinstance(self.numerator, int) or isinstance(self.numerator, bool):
            raise TypeError("numerator must be an integer")
        if not isinstance(self.denominator, int) or isinstance(self.denominator, bool):
            raise TypeError("denominator must be an integer")
        if self.denominator == 0:
            raise DivisionByZero("rational denominator cannot be zero")
        numerator, denominator = self.numerator, self.denominator
        if denominator < 0:
            numerator, denominator = -numerator, -denominator
        divisor = gcd(abs(numerator), denominator)
        object.__setattr__(self, "numerator", numerator // divisor)
        object.__setattr__(self, "denominator", denominator // divisor)

    def to_decimal_exact(self) -> ExactDecimal:
        """Convert only when the reduced denominator has factors 2 and/or 5."""
        remainder = self.denominator
        twos = fives = 0
        while remainder % 2 == 0:
            remainder //= 2
            twos += 1
        while remainder % 5 == 0:
            remainder //= 5
            fives += 1
        if remainder != 1:
            raise InexactDivision(
                "rational has a non-terminating base-10 expansion; choose an explicit quantization policy"
            )
        scale = max(twos, fives)
        coefficient = self.numerator * (2 ** (scale - twos)) * (5 ** (scale - fives))
        return ExactDecimal(coefficient, scale)

    def quantize(self, target_scale: int, rounding: RoundingMode) -> ExactDecimal:
        """Quantize at an explicit scale and explicit rounding mode."""
        if not isinstance(target_scale, int) or isinstance(target_scale, bool) or target_scale < 0:
            raise ValueError("target_scale must be a non-negative integer")
        if not isinstance(rounding, RoundingMode):
            raise TypeError("rounding must be an explicit RoundingMode")
        scaled_numerator = self.numerator * _pow10(target_scale)
        sign = -1 if scaled_numerator < 0 else 1
        quotient, remainder = divmod(abs(scaled_numerator), self.denominator)
        if remainder:
            if rounding is RoundingMode.UNNECESSARY:
                raise InexactDivision("quantization would discard a non-zero remainder")
            increment = False
            if rounding is RoundingMode.UP:
                increment = True
            elif rounding is RoundingMode.DOWN:
                increment = False
            elif rounding is RoundingMode.CEILING:
                increment = sign > 0
            elif rounding is RoundingMode.FLOOR:
                increment = sign < 0
            elif rounding in (RoundingMode.HALF_UP, RoundingMode.HALF_EVEN):
                doubled = remainder * 2
                if doubled > self.denominator:
                    increment = True
                elif doubled < self.denominator:
                    increment = False
                elif rounding is RoundingMode.HALF_UP:
                    increment = True
                else:
                    increment = quotient % 2 == 1
            if increment:
                quotient += 1
        return ExactDecimal(sign * quotient, target_scale)
