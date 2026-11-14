import unittest

from nexus_decimal import ExactDecimal as D
from instrument_spec import (
    Applicability, ContractType, IncompleteSpecification, InstrumentSpec,
    InstrumentStatus, InvalidOrderValue, MarketType, SpecError,
    UnsupportedContractModel,
)


def dec(value):
    return D.parse(value)


def spec(**overrides):
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
        tick_size=dec("0.1"),
        quantity_step=dec("0.001"),
        min_quantity=dec("0.001"),
        max_quantity=dec("10"),
        min_notional=dec("5"),
        min_notional_applicability=Applicability.REQUIRED,
        contract_multiplier=None,
        quantity_unit="BTC",
        source_id="demo:instrument-catalogue:v1",
        raw_payload_sha256="a" * 64,
        fetched_at_ms=1794650000000,
        effective_at_ms=None,
    )
    values.update(overrides)
    return InstrumentSpec(**values)


class InstrumentSpecTests(unittest.TestCase):
    def test_accepts_valid_exact_limit_order(self):
        spec().validate_limit_order(dec("50000.1"), dec("0.001"))

    def test_rejects_off_tick_price(self):
        with self.assertRaisesRegex(InvalidOrderValue, "tick_size"):
            spec().validate_limit_order(dec("50000.05"), dec("0.001"))

    def test_rejects_off_step_quantity(self):
        with self.assertRaisesRegex(InvalidOrderValue, "quantity_step"):
            spec().validate_limit_order(dec("50000"), dec("0.0015"))

    def test_rejects_below_minimum_quantity(self):
        with self.assertRaisesRegex(InvalidOrderValue, "min_quantity"):
            spec().validate_limit_order(dec("50000"), dec("0.0005"))

    def test_rejects_above_maximum_quantity(self):
        with self.assertRaisesRegex(InvalidOrderValue, "max_quantity"):
            spec().validate_limit_order(dec("50000"), dec("10.001"))

    def test_rejects_below_minimum_notional(self):
        with self.assertRaisesRegex(InvalidOrderValue, "min_notional"):
            spec().validate_limit_order(dec("1000"), dec("0.001"))

    def test_unknown_min_notional_blocks_tradability(self):
        value = spec(min_notional=None, min_notional_applicability=Applicability.UNKNOWN)
        self.assertIn("min_notional_applicability_unknown", value.tradability_blockers)
        with self.assertRaises(IncompleteSpecification):
            value.validate_limit_order(dec("50000"), dec("0.001"))

    def test_not_applicable_is_explicit(self):
        value = spec(min_notional=None, min_notional_applicability=Applicability.NOT_APPLICABLE)
        self.assertEqual(value.tradability_blockers, ())
        value.validate_limit_order(dec("50000"), dec("0.001"))

    def test_suspended_instrument_fails_closed(self):
        value = spec(status=InstrumentStatus.SUSPENDED)
        with self.assertRaises(IncompleteSpecification):
            value.validate_limit_order(dec("50000"), dec("0.001"))

    def test_unknown_contract_fails_closed(self):
        value = spec(contract_type=ContractType.UNKNOWN)
        with self.assertRaises(IncompleteSpecification):
            value.validate_limit_order(dec("50000"), dec("0.001"))

    def test_inverse_contract_requires_multiplier_and_is_not_supported(self):
        with self.assertRaisesRegex(SpecError, "multiplier"):
            spec(contract_type=ContractType.INVERSE)
        value = spec(contract_type=ContractType.INVERSE, contract_multiplier=dec("100"))
        self.assertIn("contract_model_not_supported_by_reference_validator",
                      value.tradability_blockers)
        with self.assertRaises(IncompleteSpecification):
            value.validate_limit_order(dec("50000"), dec("0.001"))

    def test_quantity_max_must_not_be_below_min(self):
        with self.assertRaisesRegex(SpecError, "below min_quantity"):
            spec(max_quantity=dec("0.0001"))

    def test_metadata_provenance_is_validated(self):
        with self.assertRaisesRegex(SpecError, "sha256"):
            spec(raw_payload_sha256="not-a-hash")

    def test_required_min_notional_cannot_be_missing(self):
        with self.assertRaisesRegex(SpecError, "required min_notional"):
            spec(min_notional=None)

    def test_negative_and_zero_order_values_are_rejected(self):
        with self.assertRaises(InvalidOrderValue):
            spec().validate_limit_order(dec("0"), dec("0.001"))
        with self.assertRaises(InvalidOrderValue):
            spec().validate_limit_order(dec("50000"), dec("-0.001"))


if __name__ == "__main__":
    unittest.main()
