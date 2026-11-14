import unittest

from nexus_decimal import ExactDecimal, ExactRational
from numeric_wire import (
    NumericWireError, parse_decimal, parse_rational,
    serialize_decimal, serialize_rational,
)


class NumericWireTests(unittest.TestCase):
    def test_wire_parsers_require_and_enforce_input_budget(self):
        with self.assertRaises(TypeError):
            parse_decimal("nxd1:1:0")
        with self.assertRaises(NumericWireError):
            parse_decimal("nxd1:123456:0", max_chars=8)
        with self.assertRaises(NumericWireError):
            parse_rational("nxr1:123456:1", max_chars=8)

    def test_decimal_round_trip_and_canonical_zero(self):
        for value in (ExactDecimal.parse("0"), ExactDecimal.parse("-12.3400"),
                      ExactDecimal.parse("0.000001")):
            encoded = serialize_decimal(value)
            self.assertEqual(parse_decimal(encoded, max_chars=128), value)
        self.assertEqual(serialize_decimal(ExactDecimal.parse("-0.00")), "nxd1:0:0")

    def test_rational_round_trip(self):
        for value in (ExactRational(1, 3), ExactRational(-7, 20),
                      ExactRational(0, 999), ExactRational(10**80 + 1, 7)):
            self.assertEqual(parse_rational(serialize_rational(value), max_chars=256), value)

    def test_decimal_rejects_unknown_version_and_wrong_shape(self):
        for value in ("nxd2:1:0", "nxd1:1", "nxd1:1:0:extra"):
            with self.subTest(value=value), self.assertRaises(NumericWireError):
                parse_decimal(value, max_chars=128)

    def test_decimal_rejects_noncanonical_integer_and_scale(self):
        for value in ("nxd1:+1:0", "nxd1:01:0", "nxd1:-0:0", "nxd1:1:00"):
            with self.subTest(value=value), self.assertRaises(NumericWireError):
                parse_decimal(value)

    def test_decimal_rejects_non_normalized_coefficient_scale(self):
        with self.assertRaisesRegex(NumericWireError, "normalized"):
            parse_decimal("nxd1:120:2", max_chars=128)

    def test_rational_rejects_unknown_version_and_wrong_shape(self):
        for value in ("nxr2:1:3", "nxr1:1", "nxr1:1:3:extra"):
            with self.subTest(value=value), self.assertRaises(NumericWireError):
                parse_rational(value, max_chars=128)

    def test_rational_rejects_noncanonical_sign_and_denominator(self):
        for value in ("nxr1:+1:3", "nxr1:01:3", "nxr1:-0:1",
                      "nxr1:1:0", "nxr1:1:-3", "nxr1:1:03"):
            with self.subTest(value=value), self.assertRaises(NumericWireError):
                parse_rational(value)

    def test_rational_rejects_unreduced_fraction(self):
        with self.assertRaisesRegex(NumericWireError, "reduced"):
            parse_rational("nxr1:2:6", max_chars=128)

    def test_rational_rejects_zero_not_normalized(self):
        with self.assertRaisesRegex(NumericWireError, "reduced"):
            parse_rational("nxr1:0:7", max_chars=128)


if __name__ == "__main__":
    unittest.main()
