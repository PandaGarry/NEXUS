"""Tests for explicit, version-pinned instrument quantity unit models."""
import unittest

from nexus_decimal import ExactDecimal as D
from domain_types import AssetAmount, ContractCount, DimensionMismatch, Notional, Price
from instrument_spec import (
    Applicability, ContractType, InstrumentSpec, InstrumentStatus, MarketType,
)
from instrument_units import (
    InstrumentUnitModel, MultiplierDimension, QuantityKind,
    UnitModelMismatch, UnsupportedUnitModel,
)


def d(value):
    return D.parse(value)


def make_spec(**overrides):
    values = dict(
        instrument_id="nexus:demo:BTC-USDT",
        venue_id="demo",
        market_type=MarketType.SPOT,
        native_instrument_id="BTC-USDT",
        base_asset="BTC",
        quote_asset="USDT",
        settlement_asset="USDT",
        contract_type=ContractType.SPOT,
        status=InstrumentStatus.ACTIVE,
        spec_version=1,
        tick_size=d("0.1"),
        quantity_step=d("0.001"),
        min_quantity=d("0.001"),
        max_quantity=d("100"),
        min_notional=d("5"),
        min_notional_applicability=Applicability.REQUIRED,
        contract_multiplier=None,
        quantity_unit="BTC",
        source_id="demo:catalogue:v1",
        raw_payload_sha256="a" * 64,
        fetched_at_ms=1794650000000,
        effective_at_ms=None,
    )
    values.update(overrides)
    return InstrumentSpec(**values)


def linear_spec(**overrides):
    values = dict(
        instrument_id="nexus:demo:BTC-USDT-LINEAR",
        native_instrument_id="BTC-USDT-PERP",
        market_type=MarketType.PERPETUAL,
        contract_type=ContractType.LINEAR,
        quantity_unit="contracts",
        contract_multiplier=d("0.001"),
    )
    values.update(overrides)
    return make_spec(**values)


def inverse_spec(**overrides):
    values = dict(
        instrument_id="nexus:demo:BTC-USD-INVERSE",
        native_instrument_id="BTC-USD-PERP",
        market_type=MarketType.PERPETUAL,
        contract_type=ContractType.INVERSE,
        base_asset="BTC",
        quote_asset="USD",
        settlement_asset="BTC",
        quantity_unit="contracts",
        contract_multiplier=d("100"),
    )
    values.update(overrides)
    return make_spec(**values)


class InstrumentUnitsTests(unittest.TestCase):
    def test_spot_explicit_mapping_creates_base_asset_quantity(self):
        model = InstrumentUnitModel.from_explicit_mapping(
            make_spec(), quantity_kind=QuantityKind.ASSET_AMOUNT,
            multiplier_dimension=MultiplierDimension.NONE,
        )
        self.assertEqual(model.asset_amount(d("0.25")), AssetAmount("BTC", d("0.25")))

    def test_spot_does_not_accept_contract_quantity_kind(self):
        with self.assertRaises(UnitModelMismatch):
            InstrumentUnitModel.from_explicit_mapping(
                make_spec(), quantity_kind=QuantityKind.CONTRACT_COUNT,
                multiplier_dimension=MultiplierDimension.NONE,
            )

    def test_spot_quote_quantity_is_not_guessed(self):
        with self.assertRaises(UnitModelMismatch):
            InstrumentUnitModel.from_explicit_mapping(
                make_spec(quantity_unit="USDT"),
                quantity_kind=QuantityKind.ASSET_AMOUNT,
                multiplier_dimension=MultiplierDimension.NONE,
            )

    def test_linear_contract_quantity_and_multiplier_are_dimensioned(self):
        model = InstrumentUnitModel.from_explicit_mapping(
            linear_spec(), quantity_kind=QuantityKind.CONTRACT_COUNT,
            multiplier_dimension=MultiplierDimension.BASE_ASSET_PER_CONTRACT,
        )
        contracts = model.contract_count(d("125"))
        self.assertEqual(model.linear_base_exposure(contracts), AssetAmount("BTC", d("0.125")))

    def test_linear_contract_notional_uses_base_exposure_and_price(self):
        model = InstrumentUnitModel.from_explicit_mapping(
            linear_spec(), quantity_kind=QuantityKind.CONTRACT_COUNT,
            multiplier_dimension=MultiplierDimension.BASE_ASSET_PER_CONTRACT,
        )
        self.assertEqual(
            model.linear_notional(model.contract_count(d("125")), Price("BTC", "USDT", d("60000"))),
            Notional("USDT", d("7500")),
        )

    def test_linear_rejects_quote_multiplier_dimension(self):
        with self.assertRaises(UnitModelMismatch):
            InstrumentUnitModel.from_explicit_mapping(
                linear_spec(), quantity_kind=QuantityKind.CONTRACT_COUNT,
                multiplier_dimension=MultiplierDimension.QUOTE_ASSET_PER_CONTRACT,
            )

    def test_inverse_multiplier_produces_quote_notional(self):
        model = InstrumentUnitModel.from_explicit_mapping(
            inverse_spec(), quantity_kind=QuantityKind.CONTRACT_COUNT,
            multiplier_dimension=MultiplierDimension.QUOTE_ASSET_PER_CONTRACT,
        )
        self.assertEqual(model.inverse_quote_notional(model.contract_count(d("3"))), Notional("USD", d("300")))

    def test_inverse_rejects_base_multiplier_dimension(self):
        with self.assertRaises(UnitModelMismatch):
            InstrumentUnitModel.from_explicit_mapping(
                inverse_spec(), quantity_kind=QuantityKind.CONTRACT_COUNT,
                multiplier_dimension=MultiplierDimension.BASE_ASSET_PER_CONTRACT,
            )

    def test_inverse_base_exposure_blocks_without_division_policy(self):
        model = InstrumentUnitModel.from_explicit_mapping(
            inverse_spec(), quantity_kind=QuantityKind.CONTRACT_COUNT,
            multiplier_dimension=MultiplierDimension.QUOTE_ASSET_PER_CONTRACT,
        )
        with self.assertRaisesRegex(UnsupportedUnitModel, "exact division"):
            model.inverse_base_exposure(
                model.contract_count(d("3")), Price("BTC", "USD", d("60000"))
            )

    def test_quanto_model_is_explicitly_unsupported(self):
        with self.assertRaises(UnsupportedUnitModel):
            InstrumentUnitModel.from_explicit_mapping(
                make_spec(
                    instrument_id="nexus:demo:BTC-USDT-QUANTO",
                    native_instrument_id="BTC-USDT-QUANTO",
                    market_type=MarketType.PERPETUAL,
                    contract_type=ContractType.QUANTO,
                    quantity_unit="contracts",
                    contract_multiplier=d("0.01"),
                ),
                quantity_kind=QuantityKind.CONTRACT_COUNT,
                multiplier_dimension=MultiplierDimension.BASE_ASSET_PER_CONTRACT,
            )

    def test_model_is_pinned_to_exact_spec_version(self):
        model = InstrumentUnitModel.from_explicit_mapping(
            linear_spec(), quantity_kind=QuantityKind.CONTRACT_COUNT,
            multiplier_dimension=MultiplierDimension.BASE_ASSET_PER_CONTRACT,
        )
        with self.assertRaises(UnitModelMismatch):
            model.validate_against(linear_spec(spec_version=2))

    def test_model_rejects_changed_multiplier_even_same_version(self):
        model = InstrumentUnitModel.from_explicit_mapping(
            linear_spec(), quantity_kind=QuantityKind.CONTRACT_COUNT,
            multiplier_dimension=MultiplierDimension.BASE_ASSET_PER_CONTRACT,
        )
        with self.assertRaises(UnitModelMismatch):
            model.validate_against(linear_spec(contract_multiplier=d("0.01")))

    def test_contract_count_cannot_cross_instrument_boundary(self):
        model = InstrumentUnitModel.from_explicit_mapping(
            linear_spec(), quantity_kind=QuantityKind.CONTRACT_COUNT,
            multiplier_dimension=MultiplierDimension.BASE_ASSET_PER_CONTRACT,
        )
        with self.assertRaises(DimensionMismatch):
            model.linear_base_exposure(ContractCount("other:instrument", d("1")))

    def test_spot_model_cannot_accept_contract_count(self):
        model = InstrumentUnitModel.from_explicit_mapping(
            make_spec(), quantity_kind=QuantityKind.ASSET_AMOUNT,
            multiplier_dimension=MultiplierDimension.NONE,
        )
        with self.assertRaises(UnitModelMismatch):
            model.contract_count(d("1"))

    def test_linear_notional_rejects_mismatched_price_assets(self):
        model = InstrumentUnitModel.from_explicit_mapping(
            linear_spec(), quantity_kind=QuantityKind.CONTRACT_COUNT,
            multiplier_dimension=MultiplierDimension.BASE_ASSET_PER_CONTRACT,
        )
        with self.assertRaises(DimensionMismatch):
            model.linear_notional(model.contract_count(d("1")), Price("ETH", "USDT", d("1000")))

    def test_unit_mapping_is_explicit_and_not_inferred_from_opaque_unit_string(self):
        with self.assertRaises(UnitModelMismatch):
            InstrumentUnitModel.from_explicit_mapping(
                linear_spec(quantity_unit="opaque-lot-code"),
                quantity_kind=QuantityKind.ASSET_AMOUNT,
                multiplier_dimension=MultiplierDimension.NONE,
            )


if __name__ == "__main__":
    unittest.main()
