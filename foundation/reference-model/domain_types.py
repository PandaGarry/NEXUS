"""Dimension-safe financial reference types for NEXUS.

Test-only reference model. It deliberately supports a small set of explicit
operations and does not implement FX conversion, derivatives, margin, fees,
or accounting policy.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import TypeVar

from nexus_decimal import ExactDecimal


class DomainTypeError(ValueError):
    """Base class for invalid domain values or dimensional operations."""


class InvalidUnitCode(DomainTypeError):
    pass


class DimensionMismatch(DomainTypeError):
    pass


_CODE = re.compile(r"^[A-Z0-9][A-Z0-9._-]{0,15}$")
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")


def _code(name: str, value: str) -> None:
    if not isinstance(value, str) or not _CODE.fullmatch(value):
        raise InvalidUnitCode(f"{name} must be a canonical uppercase unit code")


def _identifier(name: str, value: str) -> None:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise InvalidUnitCode(f"{name} must be a canonical identifier")


def _decimal(name: str, value: ExactDecimal) -> None:
    if not isinstance(value, ExactDecimal):
        raise TypeError(f"{name} must be ExactDecimal")


T = TypeVar("T", bound="_SameUnitAmount")


class _SameUnitAmount:
    unit: str
    amount: ExactDecimal

    def _same_unit(self: T, other: T) -> None:
        if type(self) is not type(other) or self.unit != other.unit:
            raise DimensionMismatch("amounts must have the same dimension and unit")

    def __add__(self: T, other: T) -> T:
        if not isinstance(other, _SameUnitAmount):
            return NotImplemented
        self._same_unit(other)
        return type(self)(self.unit, self.amount + other.amount)

    def __sub__(self: T, other: T) -> T:
        if not isinstance(other, _SameUnitAmount):
            return NotImplemented
        self._same_unit(other)
        return type(self)(self.unit, self.amount - other.amount)

    def compare(self, other: T) -> int:
        self._same_unit(other)
        return self.amount.compare(other.amount)


@dataclass(frozen=True, slots=True)
class AssetAmount(_SameUnitAmount):
    """An amount of a named asset; not a derivative contract count."""

    asset_code: str
    amount: ExactDecimal

    def __post_init__(self) -> None:
        _code("asset_code", self.asset_code)
        _decimal("amount", self.amount)

    @property
    def unit(self) -> str:
        return self.asset_code


@dataclass(frozen=True, slots=True)
class Money(_SameUnitAmount):
    """A cash/accounting amount denominated in one currency or asset code."""

    currency_code: str
    amount: ExactDecimal

    def __post_init__(self) -> None:
        _code("currency_code", self.currency_code)
        _decimal("amount", self.amount)

    @property
    def unit(self) -> str:
        return self.currency_code


@dataclass(frozen=True, slots=True)
class Notional(_SameUnitAmount):
    """A calculated quote-denominated notional, distinct from cash Money."""

    quote_asset: str
    amount: ExactDecimal

    def __post_init__(self) -> None:
        _code("quote_asset", self.quote_asset)
        _decimal("amount", self.amount)

    @property
    def unit(self) -> str:
        return self.quote_asset


@dataclass(frozen=True, slots=True)
class ContractCount:
    """A count of contracts for one instrument; never an asset quantity."""

    instrument_id: str
    count: ExactDecimal

    def __post_init__(self) -> None:
        _identifier("instrument_id", self.instrument_id)
        _decimal("count", self.count)


@dataclass(frozen=True, slots=True)
class Price:
    """Quote-asset units per one base-asset unit."""

    base_asset: str
    quote_asset: str
    quote_per_base: ExactDecimal

    def __post_init__(self) -> None:
        _code("base_asset", self.base_asset)
        _code("quote_asset", self.quote_asset)
        _decimal("quote_per_base", self.quote_per_base)
        if self.base_asset == self.quote_asset:
            raise DimensionMismatch("base and quote assets must differ")
        if self.quote_per_base.coefficient <= 0:
            raise DomainTypeError("price must be positive")

    def notional_for(self, quantity: AssetAmount) -> Notional:
        if not isinstance(quantity, AssetAmount):
            raise TypeError("quantity must be AssetAmount; contract counts are not spot quantities")
        if quantity.asset_code != self.base_asset:
            raise DimensionMismatch(
                f"price base {self.base_asset} does not match quantity asset {quantity.asset_code}"
            )
        return Notional(self.quote_asset, self.quote_per_base * quantity.amount)
