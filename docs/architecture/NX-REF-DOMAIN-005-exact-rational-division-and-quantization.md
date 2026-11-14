# NX-REF-DOMAIN-005 — Exact Rational Division & Explicit Quantization

**Status:** TEST-ONLY REFERENCE / PROPOSED NUMERIC CONTRACT  
**Authority:** None. Does not authorize order prices, quantities, risk values or ledger postings.

## 1. Purpose

Finite base-10 decimals are not closed under division: values such as 1/3 have no finite decimal representation. Silently truncating or rounding a quotient would make a mathematical operation depend on an unstated policy. This slice preserves the exact quotient as a reduced rational until a caller explicitly requests decimal quantization.

## 2. Exact division

`ExactDecimal.divide_exact(other)` returns `ExactRational(numerator, denominator)`.

- Division by zero raises `DivisionByZero`.
- Numerator and denominator are reduced by their greatest common divisor.
- Denominator is always positive; sign is carried by numerator.
- No decimal precision, scale or rounding is selected by division.
- The rational representation uses arbitrary-precision integers in this test oracle only.

## 3. Exact finite-decimal conversion

`ExactRational.to_decimal_exact()` succeeds only when the reduced denominator has no prime factors other than 2 and 5. It returns the exact finite base-10 value.

For a non-terminating decimal expansion (e.g. 1/3), it raises `InexactDivision`. It never chooses a scale or rounds.

## 4. Explicit quantization

`ExactRational.quantize(target_scale, rounding)` requires both a non-negative integer scale and an explicit `RoundingMode`:

| Mode | Meaning |
|---|---|
| UNNECESSARY | Reject if any remainder would be discarded |
| DOWN | Toward zero |
| UP | Away from zero |
| FLOOR | Toward negative infinity |
| CEILING | Toward positive infinity |
| HALF_UP | Nearest; ties away from zero |
| HALF_EVEN | Nearest; ties to even |

No default mode exists. Rounding behavior is symmetric and tested for positive and negative values. The operation is mathematically deterministic, but this document does **not** assign any mode to exchange tick normalization, fees, funding, margin, P&L, liquidation or accounting. Those policies require separate domain decisions and must not inherit a generic default.

## 5. Verification

The dedicated suite covers reduced ratios, sign normalization, zero division, terminating/non-terminating conversion, all rounding modes, tie behavior, scale validation, large integers, language-neutral golden vectors and 1,000 deterministic rational quantization property cases.

CI runs the suite independently on Python 3.11, 3.12 and 3.13. Passing this reference suite is not production-language or cross-language conformance.

## 6. Explicit limitations

- No bounded numeric representation, coefficient/scale limits or overflow policy.
- No instrument-specific rounding policy or tick/lot normalization.
- No inverse/quanto P&L, fees, funding, margin, collateral or FX policy.
- No production use; no risk or execution authority.
- No claim that arbitrary rational intermediates are safe to persist or serialize without a separately versioned contract.

## 7. Exit boundary

Before production adoption, define bounded rational/decimal behavior, canonical serialization, operation-specific rounding ownership, maximum intermediate growth, cross-language golden-vector conformance and independent property/fuzz tests.
