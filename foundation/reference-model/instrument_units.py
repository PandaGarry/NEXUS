"""Explicit instrument-unit semantics for spot, linear and inverse contracts.

Test-only reference model. It binds a separately declared unit interpretation
to one exact immutable InstrumentSpec version; it never guesses from a venue
symbol or an opaque quantity_unit string.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from nexus_decimal import ExactDecimal
from domain_types import AssetAmount, ContractCount, DimensionMismatch, Notional, Price, RationalAssetAmount
from instrument_spec import ContractType, InstrumentSpec, MarketType


class UnitModelError(ValueError):
    """Base error for instrument quantity-unit interpretation."""


class UnitModelMismatch(UnitModelError):
    pass


class UnsupportedUnitModel(UnitModelError):
    pass


class QuantityKind(str, Enum):
    ASSET_AMOUNT = "ASSET_AMOUNT"
    CONTRACT_COUNT = "CONTRACT_COUNT"


class MultiplierDimension(str, Enum):
    NONE = "NONE"
    BASE_ASSET_PER_CONTRACT = "BASE_ASSET_PER_CONTRACT"
    QUOTE_ASSET_PER_CONTRACT = "QUOTE_ASSET_PER_CONTRACT"


@dataclass(frozen=True, slots=True)
class InstrumentUnitModel:
    """Explicit unit interpretation pinned to an InstrumentSpec version.

    The multiplier dimension is part of the type contract:
    - LINEAR: base-asset units per contract.
    - INVERSE: quote-asset units per contract.
    - QUANTO: intentionally unsupported pending a three-currency model.
    """

    instrument_id: str
    spec_version: int
    venue_id: str
    native_instrument_id: str
    market_type: MarketType
    contract_type: ContractType
    base_asset: str
    quote_asset: str
    settlement_asset: str
    quantity_unit_identifier: str
    quantity_kind: QuantityKind
    multiplier_dimension: MultiplierDimension
    contract_multiplier: ExactDecimal | None

    def __post_init__(self) -> None:
        if not isinstance(self.spec_version, int) or isinstance(self.spec_version, bool) or self.spec_version < 1:
            raise UnitModelError("spec_version must be a positive integer")
        for name in ("instrument_id", "venue_id", "native_instrument_id",
                     "base_asset", "quote_asset", "settlement_asset",
                     "quantity_unit_identifier"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise UnitModelError(f"{name} must be non-empty")
        if not isinstance(self.market_type, MarketType):
            raise UnitModelError("market_type must be MarketType")
        if not isinstance(self.contract_type, ContractType):
            raise UnitModelError("contract_type must be ContractType")
        if not isinstance(self.quantity_kind, QuantityKind):
            raise UnitModelError("quantity_kind must be QuantityKind")
        if not isinstance(self.multiplier_dimension, MultiplierDimension):
            raise UnitModelError("multiplier_dimension must be MultiplierDimension")
        if self.contract_multiplier is not None:
            if not isinstance(self.contract_multiplier, ExactDecimal) or self.contract_multiplier.coefficient <= 0:
                raise UnitModelError("contract_multiplier must be a positive ExactDecimal")
        if self.contract_type is ContractType.QUANTO:
            raise UnsupportedUnitModel("QUANTO requires a separately specified three-currency valuation model")
        if self.contract_type is ContractType.UNKNOWN:
            raise UnsupportedUnitModel("UNKNOWN contract type cannot have a tradable unit model")
        if self.contract_type is ContractType.SPOT:
            if self.market_type is not MarketType.SPOT:
                raise UnitModelMismatch("SPOT unit model requires SPOT market type")
            if self.quantity_kind is not QuantityKind.ASSET_AMOUNT:
                raise UnitModelMismatch("SPOT quantity must be an asset amount")
            if self.quantity_unit_identifier != self.base_asset:
                raise UnitModelMismatch("SPOT quantity unit must explicitly equal base asset")
            if self.multiplier_dimension is not MultiplierDimension.NONE or self.contract_multiplier is not None:
                raise UnitModelMismatch("SPOT must not carry a contract multiplier")
        elif self.contract_type is ContractType.LINEAR:
            if self.market_type is MarketType.SPOT:
                raise UnitModelMismatch("LINEAR contract cannot use SPOT market type")
            if self.quantity_kind is not QuantityKind.CONTRACT_COUNT:
                raise UnitModelMismatch("LINEAR quantity must be a contract count")
            if self.multiplier_dimension is not MultiplierDimension.BASE_ASSET_PER_CONTRACT:
                raise UnitModelMismatch("LINEAR multiplier must be base-asset units per contract")
            if self.contract_multiplier is None:
                raise UnitModelMismatch("LINEAR contract multiplier is required")
        elif self.contract_type is ContractType.INVERSE:
            if self.market_type is MarketType.SPOT:
                raise UnitModelMismatch("INVERSE contract cannot use SPOT market type")
            if self.quantity_kind is not QuantityKind.CONTRACT_COUNT:
                raise UnitModelMismatch("INVERSE quantity must be a contract count")
            if self.multiplier_dimension is not MultiplierDimension.QUOTE_ASSET_PER_CONTRACT:
                raise UnitModelMismatch("INVERSE multiplier must be quote-asset units per contract")
            if self.contract_multiplier is None:
                raise UnitModelMismatch("INVERSE contract multiplier is required")
            if self.settlement_asset != self.base_asset:
                raise UnitModelMismatch("this inverse model requires settlement in the base asset")

    @classmethod
    def from_explicit_mapping(
        cls,
        spec: InstrumentSpec,
        *,
        quantity_kind: QuantityKind,
        multiplier_dimension: MultiplierDimension,
    ) -> "InstrumentUnitModel":
        """Bind a caller-reviewed unit interpretation to one immutable spec.

        This method checks consistency; it does not infer quantity_kind or
        multiplier_dimension from the venue's opaque quantity_unit field.
        """
        if not isinstance(spec, InstrumentSpec):
            raise TypeError("spec must be InstrumentSpec")
        return cls(
            instrument_id=spec.instrument_id,
            spec_version=spec.spec_version,
            venue_id=spec.venue_id,
            native_instrument_id=spec.native_instrument_id,
            market_type=spec.market_type,
            contract_type=spec.contract_type,
            base_asset=spec.base_asset,
            quote_asset=spec.quote_asset,
            settlement_asset=spec.settlement_asset,
            quantity_unit_identifier=spec.quantity_unit,
            quantity_kind=quantity_kind,
            multiplier_dimension=multiplier_dimension,
            contract_multiplier=spec.contract_multiplier,
        )

    def validate_against(self, spec: InstrumentSpec) -> None:
        expected = (
            self.instrument_id, self.spec_version, self.venue_id,
            self.native_instrument_id, self.market_type, self.contract_type,
            self.base_asset, self.quote_asset, self.settlement_asset,
            self.quantity_unit_identifier, self.contract_multiplier,
        )
        actual = (
            spec.instrument_id, spec.spec_version, spec.venue_id,
            spec.native_instrument_id, spec.market_type, spec.contract_type,
            spec.base_asset, spec.quote_asset, spec.settlement_asset,
            spec.quantity_unit, spec.contract_multiplier,
        )
        if actual != expected:
            raise UnitModelMismatch("unit model does not match this exact InstrumentSpec snapshot")

    def asset_amount(self, quantity: ExactDecimal) -> AssetAmount:
        if self.quantity_kind is not QuantityKind.ASSET_AMOUNT:
            raise UnitModelMismatch("instrument quantity is contracts, not an asset amount")
        return AssetAmount(self.base_asset, quantity)

    def contract_count(self, quantity: ExactDecimal) -> ContractCount:
        if self.quantity_kind is not QuantityKind.CONTRACT_COUNT:
            raise UnitModelMismatch("instrument quantity is an asset amount, not contracts")
        return ContractCount(self.instrument_id, quantity)

    def linear_base_exposure(self, contracts: ContractCount) -> AssetAmount:
        self._require_contracts(contracts)
        if self.contract_type is not ContractType.LINEAR:
            raise UnsupportedUnitModel("base exposure conversion is only defined here for LINEAR")
        multiplier = self._require_multiplier()
        return AssetAmount(self.base_asset, contracts.count * multiplier)

    def linear_notional(self, contracts: ContractCount, price: Price) -> Notional:
        self._require_contracts(contracts)
        if self.contract_type is not ContractType.LINEAR:
            raise UnsupportedUnitModel("linear notional is unavailable for this contract type")
        if (price.base_asset, price.quote_asset) != (self.base_asset, self.quote_asset):
            raise DimensionMismatch("price assets do not match the instrument unit model")
        return price.notional_for(self.linear_base_exposure(contracts))

    def inverse_quote_notional(self, contracts: ContractCount) -> Notional:
        self._require_contracts(contracts)
        if self.contract_type is not ContractType.INVERSE:
            raise UnsupportedUnitModel("inverse quote notional is unavailable for this contract type")
        multiplier = self._require_multiplier()
        return Notional(self.quote_asset, contracts.count * multiplier)

    def inverse_base_exposure(self, contracts: ContractCount, price: Price) -> RationalAssetAmount:
        """Return exact base exposure without imposing a decimal rounding policy."""
        self._require_contracts(contracts)
        if self.contract_type is not ContractType.INVERSE:
            raise UnsupportedUnitModel("inverse base exposure is unavailable for this contract type")
        if (price.base_asset, price.quote_asset) != (self.base_asset, self.quote_asset):
            raise DimensionMismatch("price assets do not match the instrument unit model")
        quote_notional = self.inverse_quote_notional(contracts)
        return RationalAssetAmount(
            self.base_asset,
            quote_notional.amount.divide_exact(price.quote_per_base),
        )

    def _require_multiplier(self) -> ExactDecimal:
        if self.contract_multiplier is None:
            raise UnitModelMismatch("contract multiplier is missing")
        return self.contract_multiplier

    def _require_contracts(self, contracts: ContractCount) -> None:
        if not isinstance(contracts, ContractCount):
            raise TypeError("contracts must be ContractCount")
        if contracts.instrument_id != self.instrument_id:
            raise DimensionMismatch("contract count belongs to a different instrument")
