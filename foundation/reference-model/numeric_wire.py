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
    """Base class for malformed, unsupported or non-canonical numeric wire values.

    Subclasses expose stable machine-readable classes. The base class remains
    catch-compatible with the previous reference API.
    """

    error_class = "NUMERIC.INVALID_WIRE"


class NumericWireMalformedShape(NumericWireError):
    error_class = "NUMERIC.INVALID_WIRE"


class NumericWireUnsupportedVersion(NumericWireError):
    error_class = "NUMERIC.UNSUPPORTED_WIRE_VERSION"


class NumericWireNonCanonical(NumericWireError):
    error_class = "NUMERIC.NON_CANONICAL"


class NumericWireResourceLimit(NumericWireError):
    error_class = "NUMERIC.RESOURCE_LIMIT"


def serialize_decimal(value: ExactDecimal) -> str:
    if not isinstance(value, ExactDecimal):
        raise TypeError("value must be ExactDecimal")
    return f"{_DECIMAL_PREFIX}:{value.coefficient}:{value.scale}"


def _parse_wire_integer(encoded: str, *, field: str) -> int:
    """Parse a regex-validated integer and normalize interpreter digit-budget failures."""
    try:
        return int(encoded)
    except ValueError as exc:
        # The syntax has already been checked. A conversion failure here is a
        # runtime integer-digit/resource ceiling, not malformed wire syntax.
        raise NumericWireResourceLimit(
            f"{field} exceeds the integer parsing resource budget"
        ) from exc


def parse_decimal(
    encoded: str, *, max_chars: int, max_scale: int | None = None
) -> ExactDecimal:
    if not isinstance(encoded, str):
        raise TypeError("encoded value must be str")
    if not isinstance(max_chars, int) or isinstance(max_chars, bool) or max_chars <= 0:
        raise ValueError("max_chars must be a positive integer")
    if max_scale is not None and (
        not isinstance(max_scale, int) or isinstance(max_scale, bool) or max_scale < 0
    ):
        raise ValueError("max_scale must be a non-negative integer")
    if len(encoded) > max_chars:
        raise NumericWireResourceLimit("decimal wire value exceeds input character budget")
    parts = encoded.split(":")
    if len(parts) != 3:
        raise NumericWireMalformedShape("unsupported decimal wire version or shape")
    if parts[0] != _DECIMAL_PREFIX:
        raise NumericWireUnsupportedVersion("unsupported decimal wire version or shape")
    if not _SIGNED_INTEGER.fullmatch(parts[1]):
        raise NumericWireNonCanonical("decimal coefficient is not a canonical integer")
    if not _UNSIGNED_INTEGER.fullmatch(parts[2]):
        raise NumericWireNonCanonical("decimal scale is not a canonical non-negative integer")
    coefficient = _parse_wire_integer(parts[1], field="decimal coefficient")
    scale = _parse_wire_integer(parts[2], field="decimal scale")
    scale_budget = max_chars if max_scale is None else max_scale
    if scale > scale_budget:
        raise NumericWireResourceLimit("decimal scale exceeds configured scale budget")
    value = ExactDecimal(coefficient, scale)
    if serialize_decimal(value) != encoded:
        raise NumericWireNonCanonical("decimal wire value is not normalized")
    return value


def serialize_rational(value: ExactRational) -> str:
    if not isinstance(value, ExactRational):
        raise TypeError("value must be ExactRational")
    return f"{_RATIONAL_PREFIX}:{value.numerator}:{value.denominator}"


def parse_rational(encoded: str, *, max_chars: int) -> ExactRational:
    if not isinstance(encoded, str):
        raise TypeError("encoded value must be str")
    if not isinstance(max_chars, int) or isinstance(max_chars, bool) or max_chars <= 0:
        raise ValueError("max_chars must be a positive integer")
    if len(encoded) > max_chars:
        raise NumericWireResourceLimit("rational wire value exceeds input character budget")
    parts = encoded.split(":")
    if len(parts) != 3:
        raise NumericWireMalformedShape("unsupported rational wire version or shape")
    if parts[0] != _RATIONAL_PREFIX:
        raise NumericWireUnsupportedVersion("unsupported rational wire version or shape")
    if not _SIGNED_INTEGER.fullmatch(parts[1]):
        raise NumericWireNonCanonical("rational numerator is not a canonical integer")
    if not _POSITIVE_INTEGER.fullmatch(parts[2]):
        raise NumericWireNonCanonical("rational denominator is not a canonical positive integer")
    numerator = _parse_wire_integer(parts[1], field="rational numerator")
    denominator = _parse_wire_integer(parts[2], field="rational denominator")
    value = ExactRational(numerator, denominator)
    if serialize_rational(value) != encoded:
        raise NumericWireNonCanonical("rational wire value is not reduced/canonical")
    return value
