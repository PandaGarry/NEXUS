"""Tests for the dimension-safe domain reference types."""
import unittest

from nexus_decimal import ExactDecimal as D
from domain_types import (
    AssetAmount, ContractCount, DimensionMismatch, DomainTypeError,
    InvalidUnitCode, Money, Notional, Price,
)


class DomainTypesTests(unittest.TestCase):
    def test_price_times_matching_asset_amount_yields_quote_notional(self):
        price = Price("BTC", "USDT", D.parse("65000.25"))
        qty = AssetAmount("BTC", D.parse("0.125"))
        self.assertEqual(price.notional_for(qty), Notional("USDT", D.parse("8125.03125")))

    def test_price_rejects_wrong_base_asset(self):
        with self.assertRaises(DimensionMismatch):
            Price("BTC", "USDT", D.parse("10")).notional_for(AssetAmount("ETH", D.parse("1")))

    def test_price_rejects_contract_count(self):
        with self.assertRaises(TypeError):
            Price("BTC", "USDT", D.parse("10")).notional_for(ContractCount("BTC-PERP", D.parse("1")))

    def test_price_requires_positive_value(self):
        with self.assertRaises(DomainTypeError):
            Price("BTC", "USDT", D.parse("0"))

    def test_price_rejects_same_base_and_quote(self):
        with self.assertRaises(DimensionMismatch):
            Price("BTC", "BTC", D.parse("1"))

    def test_asset_amount_addition_same_asset(self):
        self.assertEqual(AssetAmount("BTC", D.parse("1.2")) + AssetAmount("BTC", D.parse("0.3")), AssetAmount("BTC", D.parse("1.5")))

    def test_asset_amount_rejects_cross_asset_addition(self):
        with self.assertRaises(DimensionMismatch):
            _ = AssetAmount("BTC", D.parse("1")) + AssetAmount("ETH", D.parse("1"))

    def test_money_addition_same_currency(self):
        self.assertEqual(Money("USD", D.parse("10.25")) + Money("USD", D.parse("0.75")), Money("USD", D.parse("11")))

    def test_money_rejects_cross_currency_addition(self):
        with self.assertRaises(DimensionMismatch):
            _ = Money("USD", D.parse("10")) + Money("EUR", D.parse("10"))

    def test_money_and_notional_are_not_interchangeable(self):
        with self.assertRaises(DimensionMismatch):
            _ = Money("USDT", D.parse("10")) + Notional("USDT", D.parse("10"))

    def test_notional_subtraction_preserves_quote_unit(self):
        self.assertEqual(Notional("USDT", D.parse("12")) - Notional("USDT", D.parse("2")), Notional("USDT", D.parse("10")))

    def test_contract_counts_are_instrument_scoped(self):
        self.assertNotEqual(ContractCount("BTC-PERP", D.parse("2")), ContractCount("ETH-PERP", D.parse("2")))

    def test_contract_count_has_no_implicit_asset_conversion(self):
        with self.assertRaises(TypeError):
            Price("BTC", "USDT", D.parse("10")).notional_for(ContractCount("BTC-PERP", D.parse("1")))

    def test_unit_codes_must_be_canonical(self):
        with self.assertRaises(InvalidUnitCode):
            AssetAmount("btc", D.parse("1"))

    def test_amounts_require_exact_decimal(self):
        with self.assertRaises(TypeError):
            Money("USD", 1)  # type: ignore[arg-type]

    def test_signed_asset_amounts_support_position_deltas(self):
        self.assertEqual(AssetAmount("BTC", D.parse("1")) + AssetAmount("BTC", D.parse("-1")), AssetAmount("BTC", D.parse("0")))


if __name__ == "__main__":
    unittest.main()
