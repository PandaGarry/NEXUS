import unittest

from nexus_decimal import DivisionByZero, ExactDecimal, ExactRational, InvalidStep, RoundingMode
from numeric_wire import serialize_decimal, serialize_rational
from bounded_numeric import BoundedNumericContext, NumericLimitExceeded, NumericLimits, _decimal_digit_count


def context(**overrides):
    values = dict(
        max_input_chars=64,
        max_coefficient_digits=12,
        max_scale=8,
        max_rational_numerator_digits=16,
        max_rational_denominator_digits=16,
        max_intermediate_digits=24,
        max_power10_exponent=12,
    )
    values.update(overrides)
    return BoundedNumericContext(NumericLimits(**values))


def d(value):
    return ExactDecimal.parse(value)


class BoundedNumericTests(unittest.TestCase):
    def test_limits_are_mandatory_positive_and_consistent(self):
        with self.assertRaises(ValueError):
            NumericLimits(0, 4, 4, 8, 8, 8, 4)
        with self.assertRaises(ValueError):
            NumericLimits(8, 4, 4, 8, 8, 7, 4)
        with self.assertRaises(ValueError):
            NumericLimits(8, 4, 4, 8, 8, 8, 9)

    def test_context_has_no_implicit_global_profile(self):
        with self.assertRaises(TypeError):
            BoundedNumericContext()

    def test_zero_scale_and_zero_power_budget_are_valid(self):
        ctx = context(max_scale=0, max_power10_exponent=0)
        self.assertEqual(ctx.parse_decimal("123"), d("123"))
        self.assertEqual(ctx.add(d("1"), d("2")), d("3"))
        with self.assertRaises(NumericLimitExceeded):
            ctx.parse_decimal("1.0")

    def test_parse_accepts_within_explicit_limits(self):
        ctx = context()
        self.assertEqual(ctx.parse_decimal("123.4500"), d("123.45"))

    def test_parse_rejects_input_length_before_decimal_parse(self):
        with self.assertRaisesRegex(NumericLimitExceeded, "character"):
            context(max_input_chars=5).parse_decimal("123456")

    def test_parse_rejects_scale_before_decimal_parse(self):
        with self.assertRaisesRegex(NumericLimitExceeded, "scale"):
            context(max_scale=2).parse_decimal("1.234")

    def test_parse_rejects_coefficient_digit_budget(self):
        with self.assertRaisesRegex(NumericLimitExceeded, "coefficient"):
            context(max_coefficient_digits=3).parse_decimal("1234")

    def test_decimal_digit_budget_boundary_is_exact(self):
        ctx = context(max_coefficient_digits=3)
        self.assertEqual(ctx.parse_decimal("999"), d("999"))
        with self.assertRaises(NumericLimitExceeded):
            ctx.parse_decimal("1000")

    def test_integer_digit_counter_matches_decimal_representation(self):
        import random
        rng = random.Random(20261114)
        values = [0, 1, 9, 10, 99, 100, 10**100 - 1, 10**100, 10**100 + 1]
        values.extend(rng.getrandbits(rng.randint(1, 2048)) for _ in range(500))
        for value in values:
            with self.subTest(value_bits=value.bit_length()):
                self.assertEqual(_decimal_digit_count(value), len(str(abs(value))))

    def test_bounded_wire_parse_enforces_character_and_numeric_limits(self):
        ctx = context(max_input_chars=32, max_coefficient_digits=3)
        self.assertEqual(ctx.parse_decimal_wire(serialize_decimal(d("123"))), d("123"))
        with self.assertRaises(NumericLimitExceeded):
            ctx.parse_decimal_wire(serialize_decimal(d("1234")))
        rational_ctx = context(max_rational_numerator_digits=4)
        with self.assertRaises(NumericLimitExceeded):
            rational_ctx.parse_rational_wire(serialize_rational(ExactRational(123456, 1)))

    def test_compare_and_step_validation_are_bounded(self):
        ctx = context()
        self.assertEqual(ctx.compare(d("1.0001"), d("1")), 1)
        self.assertTrue(ctx.is_multiple_of(d("1.25"), d("0.05")))
        self.assertFalse(ctx.is_multiple_of(d("1.23"), d("0.05")))
        with self.assertRaises(InvalidStep):
            ctx.is_multiple_of(d("1"), d("0"))

    def test_exact_terminating_conversion_is_bounded(self):
        self.assertEqual(context().to_decimal_exact(ExactRational(1, 8)), d("0.125"))

    def test_exact_conversion_rejects_scale_over_budget(self):
        with self.assertRaisesRegex(NumericLimitExceeded, "scale"):
            context(max_scale=2).to_decimal_exact(ExactRational(1, 8))

    def test_add_exact_within_budget(self):
        ctx = context()
        self.assertEqual(ctx.add(d("1.25"), d("0.005")), d("1.255"))

    def test_add_accepts_exact_result_at_digit_budget_boundary(self):
        ctx = context(max_coefficient_digits=3, max_scale=0,
                      max_rational_numerator_digits=3, max_rational_denominator_digits=3,
                      max_intermediate_digits=3, max_power10_exponent=0)
        self.assertEqual(ctx.add(d("100"), d("200")), d("300"))
        self.assertEqual(ctx.subtract(d("300"), d("200")), d("100"))

    def test_add_rejects_only_when_carry_exceeds_intermediate_budget(self):
        ctx = context(max_coefficient_digits=3, max_scale=0,
                      max_rational_numerator_digits=3, max_rational_denominator_digits=3,
                      max_intermediate_digits=3, max_power10_exponent=0)
        with self.assertRaisesRegex(NumericLimitExceeded, "addition"):
            ctx.add(d("999"), d("1"))

    def test_add_preflights_alignment_before_power_of_ten(self):
        ctx = context(max_power10_exponent=2)
        with self.assertRaisesRegex(NumericLimitExceeded, "exponent"):
            ctx.add(d("1"), d("0.0001"))

    def test_add_preflights_intermediate_growth(self):
        ctx = context(max_intermediate_digits=8, max_rational_numerator_digits=8,
                      max_rational_denominator_digits=8, max_coefficient_digits=8)
        with self.assertRaisesRegex(NumericLimitExceeded, "addition"):
            ctx.add(d("99999999"), d("99999999"))

    def test_subtract_exact_within_budget(self):
        self.assertEqual(context().subtract(d("100"), d("0.01")), d("99.99"))

    def test_multiply_accepts_small_product_at_minimum_digit_budget(self):
        ctx = context(max_input_chars=8, max_coefficient_digits=1, max_scale=0,
                      max_rational_numerator_digits=1, max_rational_denominator_digits=1,
                      max_intermediate_digits=1, max_power10_exponent=0)
        self.assertEqual(ctx.multiply(d("1"), d("1")), d("1"))

    def test_multiply_rejects_scale_growth(self):
        ctx = context(max_scale=7)
        with self.assertRaisesRegex(NumericLimitExceeded, "scale"):
            ctx.multiply(d("0.0001"), d("0.0001"))

    def test_multiply_rejects_intermediate_growth(self):
        ctx = context(max_intermediate_digits=16, max_rational_numerator_digits=8,
                      max_rational_denominator_digits=8, max_coefficient_digits=12)
        with self.assertRaisesRegex(NumericLimitExceeded, "intermediate"):
            ctx.multiply(d("999999999"), d("999999999"))

    def test_divide_exact_within_budget(self):
        self.assertEqual(context().divide_exact(d("1"), d("3")), ExactRational(1, 3))

    def test_divide_preflights_power_of_ten_expansion(self):
        ctx = context(max_power10_exponent=2)
        with self.assertRaisesRegex(NumericLimitExceeded, "exponent"):
            ctx.divide_exact(d("1"), d("0.0001"))

    def test_divide_preflights_unreduced_intermediate_size(self):
        ctx = context(max_rational_numerator_digits=4)
        with self.assertRaisesRegex(NumericLimitExceeded, "pre-reduction"):
            ctx.divide_exact(d("1"), d("0.00001"))

    def test_division_by_zero_preserves_domain_error(self):
        with self.assertRaises(DivisionByZero):
            context().divide_exact(d("1"), d("0"))

    def test_rational_validation_rejects_large_numerator(self):
        with self.assertRaisesRegex(NumericLimitExceeded, "numerator"):
            context(max_rational_numerator_digits=4).validate_rational(ExactRational(100000, 1))

    def test_rational_quantize_within_budget(self):
        self.assertEqual(
            context().quantize_rational(ExactRational(1, 3), 4, RoundingMode.HALF_EVEN),
            d("0.3333"),
        )

    def test_rational_quantize_preflights_scale(self):
        with self.assertRaisesRegex(NumericLimitExceeded, "scale"):
            context(max_scale=4).quantize_rational(ExactRational(1, 3), 5, RoundingMode.DOWN)

    def test_rational_quantize_preflights_intermediate(self):
        ctx = context(max_scale=12, max_intermediate_digits=16, max_rational_numerator_digits=8,
                      max_rational_denominator_digits=8, max_coefficient_digits=12)
        with self.assertRaisesRegex(NumericLimitExceeded, "intermediate"):
            ctx.quantize_rational(ExactRational(12345678, 7), 10, RoundingMode.DOWN)

    def test_zero_rational_is_bounded(self):
        self.assertEqual(context().validate_rational(ExactRational(0, 999)), ExactRational(0, 1))


if __name__ == "__main__":
    unittest.main()
