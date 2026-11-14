"""Versioned, canonical, language-neutral numeric wire encodings.

The format is deliberately textual: integer coefficients/numerators/denominators
are strings of decimal digits, never JSON floating-point numbers.
"""
from __future__ import annotations

import re

from nexus_decimal import ExactDecimal, ExactRational


_DECIMAL_PREFIX = "nxd1"
_RATIONAL_PREFIX = "nxr1"
_SIGNED_INTEGER = re.compile(r"^(?:0|-[1-9][0-9]*|[1-9][0-9]*)$")
_UNSIGNED_INTEGER = re.compile(r"^(?:0|[1-9][0-9]*)$")
_POSITIVE_INTEGER = re.compile(r"^[1-9][0-9]*$")


class NumericWireError(ValueError):
    """Malformed, unsupported or non-canonical numeric wire value."""


def serialize_decimal(value: ExactDecimal) -> str:
    if not isinstance(value, ExactDecimal):
        raise TypeError("value must be ExactDecimal")
    return f"{_DECIMAL_PREFIX}:{value.coefficient}:{value.scale}"


def parse_decimal(encoded: str) -> ExactDecimal:
    if not isinstance(encoded, str):
        raise TypeError("encoded value must be str")
    parts = encoded.split(":")
    if len(parts) != 3 or parts[0] != _DECIMAL_PREFIX:
        raise NumericWireError("unsupported decimal wire version or shape")
    if not _SIGNED_INTEGER.fullmatch(parts[1]):
        raise NumericWireError("decimal coefficient is not a canonical integer")
    if not _UNSIGNED_INTEGER.fullmatch(parts[2]):
        raise NumericWireError("decimal scale is not a canonical non-negative integer")
    value = ExactDecimal(int(parts[1]), int(parts[2]))
    if serialize_decimal(value) != encoded:
        raise NumericWireError("decimal wire value is not normalized")
    return value


def serialize_rational(value: ExactRational) -> str:
    if not isinstance(value, ExactRational):
        raise TypeError("value must be ExactRational")
    return f"{_RATIONAL_PREFIX}:{value.numerator}:{value.denominator}"


def parse_rational(encoded: str) -> ExactRational:
    if not isinstance(encoded, str):
        raise TypeError("encoded value must be str")
    parts = encoded.split(":")
    if len(parts) != 3 or parts[0] != _RATIONAL_PREFIX:
        raise NumericWireError("unsupported rational wire version or shape")
    if not _SIGNED_INTEGER.fullmatch(parts[1]):
        raise NumericWireError("rational numerator is not a canonical integer")
    if not _POSITIVE_INTEGER.fullmatch(parts[2]):
        raise NumericWireError("rational denominator is not a canonical positive integer")
    value = ExactRational(int(parts[1]), int(parts[2]))
    if serialize_rational(value) != encoded:
        raise NumericWireError("rational wire value is not reduced/canonical")
    return value
