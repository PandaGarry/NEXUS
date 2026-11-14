"""Venue-neutral financial math golden-vector conformance tests.

These fixtures prove only exact dimensional arithmetic. They do not define
venue semantics, fee/funding treatment, P&L, margin, accounting or authorization.
"""
import json
import unittest
from fractions import Fraction
from pathlib import Path

from nexus_decimal import ExactDecimal as D, ExactRational
from domain_types import AssetAmount, DimensionMismatch, Notional, Price, RationalAssetAmount
from instrument_spec import Applicability, ContractType, InstrumentSpec, InstrumentStatus, MarketType
from instrument_units import InstrumentUnitModel, MultiplierDimension, QuantityKind


def d(value):
    return D.parse(value)


def make_spec(*, instrument_id, native_id, contract_type, market_type,
              base_asset, quote_asset, settlement_asset, quantity_unit,
              multiplier):
    return InstrumentSpec(
        instrument_id=instrument_id,
        venue_id="demo",
        market_type=market_type,
        native_instrument_id=native_id,
        base_asset=base_asset,
        quote_asset=quote_asset,
        settlement_asset=settlement_asset,
        contract_type=contract_type,
        status=InstrumentStatus.ACTIVE,
        spec_version=1,
        tick_size=d("0.01"),
        quantity_step=d("1") if contract_type is not ContractType.SPOT else d("0.001"),
        min_quantity=d("1") if contract_type is not ContractType.SPOT else d("0.001"),
        max_quantity=None,
        min_notional=None,
        min_notional_applicability=Applicability.NOT_APPLICABLE,
        contract_multiplier=None if multiplier is None else d(multiplier),
        quantity_unit=quantity_unit,
        source_id="synthetic:financial-math-fixtures:v1",
        raw_payload_sha256="a" * 64,
        fetched_at_ms=1,
    )


def spot_model():
    spec = make_spec(
        instrument_id="nexus:demo:BTC-USDT",
        native_id="BTC-USDT",
        contract_type=ContractType.SPOT,
        market_type=MarketType.SPOT,
        base_asset="BTC",
        quote_asset="USDT",
        settlement_asset="USDT",
        quantity_unit="BTC",
        multiplier=None,
    )
    return InstrumentUnitModel.from_explicit_mapping(
        spec, quantity_kind=QuantityKind.ASSET_AMOUNT,
        multiplier_dimension=MultiplierDimension.NONE,
    )


def linear_model():
    spec = make_spec(
        instrument_id="nexus:demo:BTC-USDT-LINEAR",
        native_id="BTC-USDT-PERP",
        contract_type=ContractType.LINEAR,
        market_type=MarketType.PERPETUAL,
        base_asset="BTC",
        quote_asset="USDT",
        settlement_asset="USDT",
        quantity_unit="contracts",
        multiplier="0.001",
    )
    return InstrumentUnitModel.from_explicit_mapping(
        spec, quantity_kind=QuantityKind.CONTRACT_COUNT,
        multiplier_dimension=MultiplierDimension.BASE_ASSET_PER_CONTRACT,
    )


def inverse_model():
    spec = make_spec(
        instrument_id="nexus:demo:BTC-USD-INVERSE",
        native_id="BTC-USD-PERP",
        contract_type=ContractType.INVERSE,
        market_type=MarketType.PERPETUAL,
        base_asset="BTC",
        quote_asset="USD",
        settlement_asset="BTC",
        quantity_unit="contracts",
        multiplier="100",
    )
    return InstrumentUnitModel.from_explicit_mapping(
        spec, quantity_kind=QuantityKind.CONTRACT_COUNT,
        multiplier_dimension=MultiplierDimension.QUOTE_ASSET_PER_CONTRACT,
    )


class FinancialMathFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).with_name("financial-math-golden-v1.json")
        cls.vectors = json.loads(path.read_text(encoding="utf-8"))
        cls.by_id = {case["id"]: case for case in cls.vectors["cases"]}

    def test_fixture_manifest_is_explicitly_non_authorizing(self):
        self.assertEqual(self.vectors["schema_version"], "1.0.0")
        self.assertEqual(self.vectors["authority"], "TEST_ONLY_NON_AUTHORIZING")
        self.assertEqual(self.vectors["rounding"], "NONE")
        self.assertEqual(len(self.by_id), len(self.vectors["cases"]))

    def test_spot_notional_vector(self):
        case = self.by_id["spot-notional-001"]
        quantity = spot_model().asset_amount(d(case["inputs"]["quantity"]["value"]))
        price = Price("BTC", "USDT", d(case["inputs"]["price"]["value"]))
        result = price.notional_for(quantity)
        expected = case["expected"]["notional"]
        self.assertEqual(str(result.amount), expected["value"])
        self.assertEqual(result.quote_asset, expected["unit"])
        self.assertEqual(Fraction(result.amount.coefficient, 10 ** result.amount.scale),
                         Fraction(812503125, 100000))

    def test_linear_contract_notional_vector(self):
        case = self.by_id["linear-contract-notional-001"]
        model = linear_model()
        contracts = model.contract_count(d(case["inputs"]["contracts"]["value"]))
        exposure = model.linear_base_exposure(contracts)
        notional = model.linear_notional(contracts, Price("BTC", "USDT", d("65000.25")))
        self.assertEqual(str(exposure.amount), case["expected"]["base_exposure"]["value"])
        self.assertEqual(exposure.asset_code, "BTC")
        self.assertEqual(str(notional.amount), case["expected"]["notional"]["value"])
        self.assertEqual(notional.quote_asset, "USDT")
        self.assertEqual(Fraction(notional.amount.coefficient, 10 ** notional.amount.scale),
                         Fraction(780003, 1000))

    def test_inverse_contract_exposure_vector_remains_rational(self):
        case = self.by_id["inverse-contract-exposure-001"]
        model = inverse_model()
        contracts = model.contract_count(d(case["inputs"]["contracts"]["value"]))
        quote = model.inverse_quote_notional(contracts)
        exposure = model.inverse_base_exposure(contracts, Price("BTC", "USD", d("65000.25")))
        expected = case["expected"]["base_exposure"]
        self.assertEqual(str(quote.amount), case["expected"]["quote_notional"]["value"])
        self.assertEqual((str(exposure.amount.numerator), str(exposure.amount.denominator)),
                         (expected["numerator"], expected["denominator"]))
        self.assertEqual(exposure.asset_code, expected["unit"])
        # Independent standard-library rational oracle; no decimal rounding.
        self.assertEqual(Fraction(exposure.amount.numerator, exposure.amount.denominator),
                         Fraction(100 * 100, 1) / Fraction(6500025, 100))

    def test_partial_fill_aggregation_vector(self):
        case = self.by_id["partial-fill-weighted-average-001"]
        total_quantity = D.parse("0")
        total_quote = D.parse("0")
        for fill in case["inputs"]["fills"]:
            quantity = D.parse(fill["quantity"]["value"])
            price = D.parse(fill["price"]["value"])
            total_quantity = total_quantity + quantity
            total_quote = total_quote + price * quantity
        weighted_average = total_quote.divide_exact(total_quantity).to_decimal_exact()
        expected = case["expected"]
        self.assertEqual(str(total_quantity), expected["total_quantity"]["value"])
        self.assertEqual(str(total_quote), expected["total_quote_value"]["value"])
        self.assertEqual(str(weighted_average), expected["weighted_average_price"]["value"])
        self.assertEqual(Fraction(total_quote.coefficient, 10 ** total_quote.scale),
                         Fraction(8125085, 1000))
        self.assertEqual(Fraction(weighted_average.coefficient, 10 ** weighted_average.scale),
                         Fraction(1625017, 25))

    def test_price_quantity_dimension_mismatch_fails_closed(self):
        with self.assertRaises(DimensionMismatch):
            Price("BTC", "USDT", d("65000")).notional_for(AssetAmount("ETH", d("1")))

    def test_inverse_contract_count_cannot_cross_instrument_boundary(self):
        model = inverse_model()
        with self.assertRaises(DimensionMismatch):
            model.inverse_quote_notional(
                model.contract_count(d("1")).__class__("nexus:other:BTC-USD", d("1"))
            )


if __name__ == "__main__":
    unittest.main()
