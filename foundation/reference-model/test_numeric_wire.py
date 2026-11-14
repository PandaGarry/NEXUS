import unittest
import json
from pathlib import Path

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

    def test_language_neutral_numeric_wire_golden_vectors(self):
        vectors = json.loads(
            Path(__file__).with_name("numeric-wire-golden-v1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(vectors["version"], "1.0.0")
        for case in vectors["cases"]:
            with self.subTest(vector=case["id"]):
                kind = case["kind"]
                if kind == "decimal":
                    value = parse_decimal(case["wire"], max_chars=256)
                    self.assertEqual(str(value.coefficient), case["expected_coefficient"])
                    self.assertEqual(value.scale, case["expected_scale"])
                    self.assertEqual(serialize_decimal(value), case["wire"])
                elif kind == "rational":
                    value = parse_rational(case["wire"], max_chars=256)
                    self.assertEqual(str(value.numerator), case["expected_numerator"])
                    self.assertEqual(str(value.denominator), case["expected_denominator"])
                    self.assertEqual(serialize_rational(value), case["wire"])
                elif kind == "decimal_invalid":
                    with self.assertRaises(NumericWireError):
                        parse_decimal(case["wire"], max_chars=256)
                elif kind == "rational_invalid":
                    with self.assertRaises(NumericWireError):
                        parse_rational(case["wire"], max_chars=256)
                else:
                    self.fail(f"unsupported wire vector kind: {kind}")

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
                parse_decimal(value, max_chars=128)

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
                parse_rational(value, max_chars=128)

    def test_rational_rejects_unreduced_fraction(self):
        with self.assertRaisesRegex(NumericWireError, "reduced"):
            parse_rational("nxr1:2:6", max_chars=128)

    def test_rational_rejects_zero_not_normalized(self):
        with self.assertRaisesRegex(NumericWireError, "reduced"):
            parse_rational("nxr1:0:7", max_chars=128)


    def test_numeric_wire_errors_expose_stable_classes_and_preserve_base_type(self):
        cases = (
            (lambda: parse_decimal("nxd2:1:0", max_chars=128),
             "NUMERIC.UNSUPPORTED_WIRE_VERSION"),
            (lambda: parse_decimal("nxd1:1", max_chars=128),
             "NUMERIC.INVALID_WIRE"),
            (lambda: parse_decimal("nxd1:01:0", max_chars=128),
             "NUMERIC.NON_CANONICAL"),
            (lambda: parse_decimal("nxd1:123456:0", max_chars=8),
             "NUMERIC.RESOURCE_LIMIT"),
            (lambda: parse_rational("nxr2:1:3", max_chars=128),
             "NUMERIC.UNSUPPORTED_WIRE_VERSION"),
            (lambda: parse_rational("nxr1:1", max_chars=128),
             "NUMERIC.INVALID_WIRE"),
            (lambda: parse_rational("nxr1:2:6", max_chars=128),
             "NUMERIC.NON_CANONICAL"),
            (lambda: parse_rational("nxr1:123456:1", max_chars=8),
             "NUMERIC.RESOURCE_LIMIT"),
        )
        for operation, expected_class in cases:
            with self.subTest(expected_class=expected_class, operation=operation):
                with self.assertRaises(NumericWireError) as caught:
                    operation()
                self.assertEqual(caught.exception.error_class, expected_class)


    def test_decimal_scale_obeys_explicit_resource_budget(self):
        with self.assertRaises(NumericWireError) as caught:
            parse_decimal("nxd1:1:129", max_chars=128)
        self.assertEqual(caught.exception.error_class, "NUMERIC.RESOURCE_LIMIT")

        with self.assertRaises(NumericWireError) as caught:
            parse_decimal("nxd1:1:5", max_chars=128, max_scale=4)
        self.assertEqual(caught.exception.error_class, "NUMERIC.RESOURCE_LIMIT")

        with self.assertRaises(ValueError):
            parse_decimal("nxd1:1:0", max_chars=128, max_scale=-1)

    def test_integer_conversion_budget_failures_are_stable_resource_errors(self):
        oversized_integer = "9" * 5000
        with self.assertRaises(NumericWireError) as caught:
            parse_decimal(f"nxd1:{oversized_integer}:0", max_chars=6000)
        self.assertEqual(caught.exception.error_class, "NUMERIC.RESOURCE_LIMIT")

        with self.assertRaises(NumericWireError) as caught:
            parse_rational(f"nxr1:{oversized_integer}:1", max_chars=6000)
        self.assertEqual(caught.exception.error_class, "NUMERIC.RESOURCE_LIMIT")


if __name__ == "__main__":
    unittest.main()
