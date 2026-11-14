"""Exact rational division and explicit quantization policy conformance tests."""
import unittest
from fractions import Fraction

from nexus_decimal import (
    DivisionByZero, ExactDecimal, ExactRational, InexactDivision, RoundingMode,
)


def d(value):
    return ExactDecimal.parse(value)


class ExactDivisionTests(unittest.TestCase):
    def test_division_returns_reduced_exact_rational(self):
        self.assertEqual(d("1").divide_exact(d("3")), ExactRational(1, 3))
        self.assertEqual(d("1.20").divide_exact(d("0.30")), ExactRational(4, 1))
        self.assertEqual(d("-2").divide_exact(d("4")), ExactRational(-1, 2))

    def test_rational_normalizes_sign_and_gcd(self):
        self.assertEqual(ExactRational(6, -8), ExactRational(-3, 4))
        self.assertEqual(ExactRational(0, -99), ExactRational(0, 1))

    def test_zero_denominator_rejected(self):
        with self.assertRaises(DivisionByZero):
            d("1").divide_exact(d("0"))
        with self.assertRaises(DivisionByZero):
            ExactRational(1, 0)

    def test_exact_terminating_decimal_conversion(self):
        cases = {
            ("1", "2"): "0.5",
            ("1", "5"): "0.2",
            ("1", "8"): "0.125",
            ("7", "40"): "0.175",
            ("-3", "20"): "-0.15",
            ("12", "3"): "4",
        }
        for (a, b), expected in cases.items():
            with self.subTest(a=a, b=b):
                self.assertEqual(str(d(a).divide_exact(d(b)).to_decimal_exact()), expected)

    def test_non_terminating_decimal_conversion_fails_closed(self):
        for numerator, denominator in ((1, 3), (1, 6), (2, 7), (-5, 11)):
            with self.subTest(numerator=numerator, denominator=denominator):
                with self.assertRaises(InexactDivision):
                    ExactRational(numerator, denominator).to_decimal_exact()

    def test_unnecessary_quantization_requires_exact_result(self):
        self.assertEqual(
            str(ExactRational(1, 8).quantize(3, RoundingMode.UNNECESSARY)), "0.125"
        )
        with self.assertRaises(InexactDivision):
            ExactRational(1, 3).quantize(2, RoundingMode.UNNECESSARY)

    def test_down_rounds_toward_zero_for_both_signs(self):
        self.assertEqual(str(ExactRational(1, 3).quantize(2, RoundingMode.DOWN)), "0.33")
        self.assertEqual(str(ExactRational(-1, 3).quantize(2, RoundingMode.DOWN)), "-0.33")

    def test_up_rounds_away_from_zero_for_both_signs(self):
        self.assertEqual(str(ExactRational(1, 3).quantize(2, RoundingMode.UP)), "0.34")
        self.assertEqual(str(ExactRational(-1, 3).quantize(2, RoundingMode.UP)), "-0.34")

    def test_floor_and_ceiling_are_mathematical_directions(self):
        self.assertEqual(str(ExactRational(1, 3).quantize(2, RoundingMode.FLOOR)), "0.33")
        self.assertEqual(str(ExactRational(-1, 3).quantize(2, RoundingMode.FLOOR)), "-0.34")
        self.assertEqual(str(ExactRational(1, 3).quantize(2, RoundingMode.CEILING)), "0.34")
        self.assertEqual(str(ExactRational(-1, 3).quantize(2, RoundingMode.CEILING)), "-0.33")

    def test_half_up_ties_away_from_zero(self):
        self.assertEqual(str(ExactRational(5, 2).quantize(0, RoundingMode.HALF_UP)), "3")
        self.assertEqual(str(ExactRational(-5, 2).quantize(0, RoundingMode.HALF_UP)), "-3")

    def test_half_even_ties_to_even(self):
        cases = ((5, 2, "2"), (7, 2, "4"), (-5, 2, "-2"), (-7, 2, "-4"))
        for n, den, expected in cases:
            with self.subTest(n=n, den=den):
                self.assertEqual(str(ExactRational(n, den).quantize(0, RoundingMode.HALF_EVEN)), expected)

    def test_half_modes_non_tie(self):
        self.assertEqual(str(ExactRational(124, 100).quantize(1, RoundingMode.HALF_UP)), "1.2")
        self.assertEqual(str(ExactRational(126, 100).quantize(1, RoundingMode.HALF_EVEN)), "1.3")

    def test_rounding_mode_is_mandatory_and_typed(self):
        with self.assertRaises(TypeError):
            ExactRational(1, 3).quantize(2, "HALF_UP")

    def test_target_scale_validation(self):
        for scale in (-1, True, 1.5):
            with self.subTest(scale=scale):
                with self.assertRaises(ValueError):
                    ExactRational(1, 3).quantize(scale, RoundingMode.DOWN)

    def test_exact_zero_quantizes_without_rounding_artifact(self):
        self.assertEqual(str(ExactRational(0, 3).quantize(8, RoundingMode.UNNECESSARY)), "0")

    def test_large_integer_ratio_is_exact(self):
        value = ExactRational(10**80 + 1, 10**40)
        self.assertEqual(value.numerator, 10**80 + 1)
        self.assertEqual(value.denominator, 10**40)

    def test_deterministic_rational_quantization_properties(self):
        import random
        rng = random.Random(20261114)
        modes = tuple(RoundingMode)
        for index in range(1000):
            numerator = rng.randint(-(10**30), 10**30)
            denominator = rng.randint(1, 10**18)
            scale = rng.randint(0, 12)
            rational = ExactRational(numerator, denominator)
            mode = modes[rng.randrange(len(modes))]
            fraction = Fraction(rational.numerator * 10**scale, rational.denominator)
            q, rem = divmod(abs(fraction.numerator), fraction.denominator)
            sign = -1 if fraction.numerator < 0 else 1
            if rem and mode is RoundingMode.UNNECESSARY:
                with self.assertRaises(InexactDivision):
                    rational.quantize(scale, mode)
                continue
            if rem:
                inc = (
                    mode is RoundingMode.UP
                    or (mode is RoundingMode.CEILING and sign > 0)
                    or (mode is RoundingMode.FLOOR and sign < 0)
                )
                if mode in (RoundingMode.HALF_UP, RoundingMode.HALF_EVEN):
                    twice = rem * 2
                    inc = twice > fraction.denominator or (
                        twice == fraction.denominator and (
                            mode is RoundingMode.HALF_UP or q % 2 == 1
                        )
                    )
                if inc:
                    q += 1
            expected = ExactDecimal(sign * q, scale)
            with self.subTest(case=index, mode=mode):
                self.assertEqual(rational.quantize(scale, mode), expected)


if __name__ == "__main__":
    unittest.main()
