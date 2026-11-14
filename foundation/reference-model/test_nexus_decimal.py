import unittest
import json
import random
from fractions import Fraction
from pathlib import Path

from nexus_decimal import (
    ExactDecimal,
    InexactQuantization,
    InvalidDecimal,
    InvalidStep,
)


class ExactDecimalTests(unittest.TestCase):
    def d(self, value: str) -> ExactDecimal:
        return ExactDecimal.parse(value)

    def test_parse_and_canonical_format(self):
        cases = {
            "0012.3400": "12.34",
            "+0.000": "0",
            "-.125": "-0.125",
            "100": "100",
            "0.00000001": "0.00000001",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(str(self.d(source)), expected)

    def test_rejects_exponent_whitespace_and_non_decimal(self):
        for source in ("1e-8", " 1", "1 ", "NaN", "Infinity", "1,25", ""):
            with self.subTest(source=source):
                with self.assertRaises(InvalidDecimal):
                    self.d(source)

    def test_exact_add_subtract(self):
        self.assertEqual(str(self.d("0.1") + self.d("0.02")), "0.12")
        self.assertEqual(str(self.d("100") - self.d("0.0001")), "99.9999")
        self.assertEqual(str(self.d("-2.5") + self.d("1.25")), "-1.25")

    def test_exact_multiply(self):
        self.assertEqual(str(self.d("12.5") * self.d("0.08")), "1")
        self.assertEqual(str(self.d("-0.2") * self.d("3")), "-0.6")

    def test_compare_without_float(self):
        self.assertEqual(self.d("1.000000000000000001").compare(self.d("1")), 1)
        self.assertEqual(self.d("-2").compare(self.d("-1.99")), -1)
        self.assertEqual(self.d("3.00").compare(self.d("3")), 0)

    def test_exact_quantize(self):
        self.assertEqual(str(self.d("1.25").quantize_exact(4)), "1.25")
        self.assertEqual(str(self.d("1.2500").quantize_exact(2)), "1.25")
        with self.assertRaises(InexactQuantization):
            self.d("1.251").quantize_exact(2)

    def test_step_validation(self):
        self.assertTrue(self.d("1.25").is_multiple_of(self.d("0.05")))
        self.assertFalse(self.d("1.23").is_multiple_of(self.d("0.05")))
        with self.assertRaises(InvalidStep):
            self.d("1").is_multiple_of(self.d("0"))
        with self.assertRaises(InvalidStep):
            self.d("1").is_multiple_of(self.d("-0.1"))
        with self.assertRaises(TypeError):
            self.d("1").is_multiple_of("0.1")  # type: ignore[arg-type]

    def test_large_values_and_scales(self):
        a = self.d("999999999999999999999999999999.99999999")
        b = self.d("0.00000001")
        self.assertEqual(str(a + b), "1000000000000000000000000000000")

    def test_zero_normalizes(self):
        self.assertEqual(str(self.d("-0.000000")), "0")


    def test_language_neutral_golden_vectors(self):
        vector_path = Path(__file__).with_name("golden-vectors-v1.json")
        vectors = json.loads(vector_path.read_text(encoding="utf-8"))
        self.assertEqual(vectors["version"], "1.0.0")
        for case in vectors["cases"]:
            with self.subTest(vector=case["id"]):
                op = case["op"]
                if op == "parse":
                    actual = str(self.d(case["input"]))
                elif op == "add":
                    actual = str(self.d(case["a"]) + self.d(case["b"]))
                elif op == "subtract":
                    actual = str(self.d(case["a"]) - self.d(case["b"]))
                elif op == "multiply":
                    actual = str(self.d(case["a"]) * self.d(case["b"]))
                elif op == "compare":
                    actual = self.d(case["a"]).compare(self.d(case["b"]))
                elif op == "quantize_exact":
                    actual = str(self.d(case["a"]).quantize_exact(case["scale"]))
                elif op == "multiple_of":
                    actual = self.d(case["a"]).is_multiple_of(self.d(case["step"]))
                else:
                    self.fail(f"unsupported golden vector operation: {op}")
                self.assertEqual(actual, case["expected"])


    def test_deterministic_exact_arithmetic_properties(self):
        rng = random.Random(20261114)

        def literal(coefficient: int, scale: int) -> str:
            sign = "-" if coefficient < 0 else ""
            digits = str(abs(coefficient))
            if scale == 0:
                return sign + digits
            digits = digits.rjust(scale + 1, "0")
            return sign + digits[:-scale] + "." + digits[-scale:]

        def fraction(value: ExactDecimal) -> Fraction:
            return Fraction(value.coefficient, 10 ** value.scale)

        for index in range(1000):
            left_text = literal(rng.randint(-(10 ** 25), 10 ** 25), rng.randint(0, 18))
            right_text = literal(rng.randint(-(10 ** 25), 10 ** 25), rng.randint(0, 18))
            left, right = self.d(left_text), self.d(right_text)
            left_f, right_f = Fraction(left_text), Fraction(right_text)

            with self.subTest(property_case=index):
                self.assertEqual(fraction(left + right), left_f + right_f)
                self.assertEqual(fraction(left - right), left_f - right_f)
                self.assertEqual(fraction(left * right), left_f * right_f)
                self.assertEqual(left.compare(right), (left_f > right_f) - (left_f < right_f))
                self.assertEqual(self.d(str(left)), left)
                self.assertEqual(self.d(str(right)), right)

                positive_step = ExactDecimal(abs(right.coefficient) or 1, right.scale)
                step_f = fraction(positive_step)
                self.assertEqual(left.is_multiple_of(positive_step),
                                 (left_f / step_f).denominator == 1)

                target_scale = rng.randint(0, 18)
                if target_scale >= left.scale:
                    self.assertEqual(fraction(left.quantize_exact(target_scale)), left_f)
                else:
                    divisor = 10 ** (left.scale - target_scale)
                    if left.coefficient % divisor == 0:
                        self.assertEqual(fraction(left.quantize_exact(target_scale)), left_f)
                    else:
                        with self.assertRaises(InexactQuantization):
                            left.quantize_exact(target_scale)


if __name__ == "__main__":
    unittest.main()
