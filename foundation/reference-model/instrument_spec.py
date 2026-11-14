"""Venue-neutral instrument specification reference model.

Test-only conformance aid. It validates metadata completeness and exact price /
quantity rules; it is not an exchange adapter, risk engine, or order authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Optional

from nexus_decimal import ExactDecimal, InvalidStep


class SpecError(ValueError):
    """Base class for invalid instrument specifications."""


class IncompleteSpecification(SpecError):
    pass


class UnsupportedContractModel(SpecError):
    pass


class InvalidOrderValue(SpecError):
    pass


class MarketType(str, Enum):
    SPOT = "SPOT"
    PERPETUAL = "PERPETUAL"
    FUTURE = "FUTURE"


class ContractType(str, Enum):
    SPOT = "SPOT"
    LINEAR = "LINEAR"
    INVERSE = "INVERSE"
    QUANTO = "QUANTO"
    UNKNOWN = "UNKNOWN"


class InstrumentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELISTING = "DELISTING"
    DELISTED = "DELISTED"
    UNKNOWN = "UNKNOWN"


class Applicability(str, Enum):
    REQUIRED = "REQUIRED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"


_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _identifier(name: str, value: str) -> None:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise SpecError(f"{name} must be a non-empty canonical identifier")


@dataclass(frozen=True, slots=True)
class InstrumentSpec:
    """Immutable, versioned snapshot of venue-published instrument rules.

    Decimal inputs must be canonical decimal strings. Raw venue payload storage,
    signature/authenticity, effective-time ordering and persistence are outside
    this reference model.
    """

    instrument_id: str
    venue_id: str
    market_type: MarketType
    native_instrument_id: str
    base_asset: str
    quote_asset: str
    settlement_asset: str
    contract_type: ContractType
    status: InstrumentStatus
    spec_version: int
    tick_size: ExactDecimal
    quantity_step: ExactDecimal
    min_quantity: ExactDecimal
    max_quantity: Optional[ExactDecimal]
    min_notional: Optional[ExactDecimal]
    min_notional_applicability: Applicability
    contract_multiplier: Optional[ExactDecimal]
    quantity_unit: str
    source_id: str
    raw_payload_sha256: str
    fetched_at_ms: int
    effective_at_ms: Optional[int] = None

    def __post_init__(self) -> None:
        for name in ("instrument_id", "venue_id", "native_instrument_id",
                     "base_asset", "quote_asset", "settlement_asset",
                     "quantity_unit", "source_id"):
            _identifier(name, getattr(self, name))
        if not isinstance(self.market_type, MarketType):
            raise SpecError("market_type must be MarketType")
        if not isinstance(self.contract_type, ContractType):
            raise SpecError("contract_type must be ContractType")
        if not isinstance(self.status, InstrumentStatus):
            raise SpecError("status must be InstrumentStatus")
        if not isinstance(self.min_notional_applicability, Applicability):
            raise SpecError("min_notional_applicability must be Applicability")
        if isinstance(self.spec_version, bool) or not isinstance(self.spec_version, int) or self.spec_version < 1:
            raise SpecError("spec_version must be a positive integer")
        if isinstance(self.fetched_at_ms, bool) or not isinstance(self.fetched_at_ms, int) or self.fetched_at_ms <= 0:
            raise SpecError("fetched_at_ms must be a positive integer")
        if self.effective_at_ms is not None and (
            isinstance(self.effective_at_ms, bool) or not isinstance(self.effective_at_ms, int)
            or self.effective_at_ms <= 0
        ):
            raise SpecError("effective_at_ms must be a positive integer when supplied")
        if not _SHA256.fullmatch(self.raw_payload_sha256):
            raise SpecError("raw_payload_sha256 must be 64 lowercase hexadecimal characters")
        for name in ("tick_size", "quantity_step", "min_quantity"):
            value = getattr(self, name)
            if not isinstance(value, ExactDecimal) or value.coefficient <= 0:
                raise SpecError(f"{name} must be a positive ExactDecimal")
        for name in ("max_quantity", "min_notional", "contract_multiplier"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, ExactDecimal):
                raise SpecError(f"{name} must be ExactDecimal or None")
            if value is not None and value.coefficient <= 0:
                raise SpecError(f"{name} must be positive")
        if self.max_quantity is not None and self.max_quantity.compare(self.min_quantity) < 0:
            raise SpecError("max_quantity cannot be below min_quantity")
        if self.min_notional_applicability is Applicability.REQUIRED:
            if self.min_notional is None:
                raise SpecError("required min_notional is missing")
        elif self.min_notional_applicability is Applicability.NOT_APPLICABLE:
            if self.min_notional is not None:
                raise SpecError("NOT_APPLICABLE min_notional must not carry a value")
        elif self.min_notional is not None:
            raise SpecError("UNKNOWN min_notional cannot carry an assumed value")
        if self.contract_type in (ContractType.LINEAR, ContractType.INVERSE, ContractType.QUANTO):
            if self.contract_multiplier is None:
                raise SpecError("contract multiplier is required for derivative contracts")
        elif self.contract_type is ContractType.SPOT and self.contract_multiplier is not None:
            raise SpecError("spot instrument must not carry a contract multiplier")

    @property
    def tradability_blockers(self) -> tuple[str, ...]:
        blockers = []
        if self.status is not InstrumentStatus.ACTIVE:
            blockers.append("instrument_status_not_active")
        if self.contract_type is ContractType.UNKNOWN:
            blockers.append("contract_type_unknown")
        if self.min_notional_applicability is Applicability.UNKNOWN:
            blockers.append("min_notional_applicability_unknown")
        if self.contract_type in (ContractType.INVERSE, ContractType.QUANTO):
            blockers.append("contract_model_not_supported_by_reference_validator")
        return tuple(blockers)

    def validate_limit_order(self, price: ExactDecimal, quantity: ExactDecimal) -> None:
        """Validate exact tick/lot/min/max/min-notional constraints only.

        This does not authorize execution and does not calculate exposure, fees,
        margin, leverage, buying power, price bands or account risk.
        """
        if self.tradability_blockers:
            raise IncompleteSpecification(", ".join(self.tradability_blockers))
        if not isinstance(price, ExactDecimal) or price.coefficient <= 0:
            raise InvalidOrderValue("price must be a positive ExactDecimal")
        if not isinstance(quantity, ExactDecimal) or quantity.coefficient <= 0:
            raise InvalidOrderValue("quantity must be a positive ExactDecimal")
        try:
            if not price.is_multiple_of(self.tick_size):
                raise InvalidOrderValue("price is not an exact multiple of tick_size")
            if not quantity.is_multiple_of(self.quantity_step):
                raise InvalidOrderValue("quantity is not an exact multiple of quantity_step")
        except InvalidStep as exc:
            raise IncompleteSpecification("invalid instrument step") from exc
        if quantity.compare(self.min_quantity) < 0:
            raise InvalidOrderValue("quantity is below min_quantity")
        if self.max_quantity is not None and quantity.compare(self.max_quantity) > 0:
            raise InvalidOrderValue("quantity exceeds max_quantity")
        if self.min_notional is not None:
            notional = price * quantity
            if notional.compare(self.min_notional) < 0:
                raise InvalidOrderValue("price * quantity is below min_notional")
