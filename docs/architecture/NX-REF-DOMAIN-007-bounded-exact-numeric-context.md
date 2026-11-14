# NX-REF-DOMAIN-007 — Bounded Exact Numeric Context

**Status:** TEST-ONLY REFERENCE / PROPOSED CONFORMANCE CONTRACT  
**Authority:** None. No production numeric profile or financial calculation policy is approved.

## 1. Purpose

The arbitrary-precision decimal/rational oracle establishes mathematical results but is not a safe resource policy for a long-running service. This reference slice adds an explicit context that rejects values and operations before known scale expansion or intermediate growth exceeds caller-supplied budgets.

The arbitrary-precision oracle remains unchanged as the mathematical source of expected results. The bounded context is a separate admission/preflight layer.

## 2. Mandatory limits; no default profile

NumericLimits requires explicit integer budgets. Input/digit/intermediate budgets must be positive; max_scale and max_power10_exponent may be zero (integer-only/no-expansion profiles):

- max_input_chars
- max_coefficient_digits
- max_scale
- max_rational_numerator_digits
- max_rational_denominator_digits
- max_intermediate_digits
- max_power10_exponent

No implicit/default profile exists. A caller must construct a complete limits object. The values used in unit tests are synthetic fixtures only and are not NEXUS production recommendations.

## 3. Checked operations

BoundedNumericContext provides:
- bounded decimal parsing and value validation;
- exact add/subtract with scale-alignment preflight;
- exact multiply with result-scale and intermediate-digit preflight;
- exact rational division with power-of-ten, intermediate and pre-reduction numerator/denominator checks;
- exact compare and positive-step divisibility with bounded alignment;
- exact rational-to-decimal conversion only for terminating values;
- explicit rational quantization with target-scale and intermediate-growth checks;
- bounded canonical decimal/rational wire parsing.

All admitted arithmetic delegates to the arbitrary-precision oracle only after preflight checks. The wrapper does not silently round.

## 4. Conservative admission rules

The context deliberately applies conservative pre-reduction checks to division. A quotient may be rejected when its unreduced numerator or denominator exceeds the configured budget even if a large GCD would reduce the final rational below that budget. This avoids doing an unbounded reduction before the operation is admitted.

Multiplication checks the summed input scales before normalization. Therefore a product whose trailing zeros might later reduce scale can be rejected conservatively. This is intentional for the reference profile; an optimized production implementation may use a proven bounded algorithm, but must preserve the same accepted/rejected behavior or version the contract.

Digit counting is exact for the already materialized integer values. External text parsing is character-limited before integer conversion. This Python reference does not claim to protect an arbitrary process from hostile preconstructed giant Python integers, interpreter-level resource exhaustion, or CPU denial of service.

## 5. Failure behavior

Budget violations raise NumericLimitExceeded; malformed types and invalid limits raise type/value errors; division by zero preserves DivisionByZero; non-terminating exact conversion preserves InexactDivision; quantization still requires a typed explicit RoundingMode.

A caller must treat any limit violation as a rejected calculation. It must not retry with silently expanded limits, truncate, fall back to float, or substitute zero.

## 6. Verification

The dedicated suite covers mandatory limits, no implicit profile, exact digit-budget boundaries and digit-counter cross-checks, input length/scale/coefficient limits, add/subtract/multiply, preflight before alignment and division expansion, conservative pre-reduction rejection, division by zero, rational validation, compare, step validation, exact conversion, explicit quantization and canonical wire integration.

CI runs the suite on Python 3.11, 3.12 and 3.13. This is reference-level conformance, not production resource-safety evidence.

## 7. Explicitly unresolved

- No production limits selected; these depend on venue precision, product scope, workload, latency, memory budgets and threat model.
- No fixed-width integer choice or overflow implementation selected.
- No proof of worst-case CPU/memory cost or hard real-time behavior.
- No operation-specific financial rounding rules.
- No Rust/WASM/backend implementation or cross-language conformance.
- No durable database schema, migration policy or full event envelope integration.

## 8. Exit boundary

Before production adoption, select and justify limits per deployment profile, prove checked arithmetic in the chosen language, add boundary/property/fuzz tests, benchmark worst-case resource use, define overflow/error mapping, and verify cross-language parity against shared vectors.


**CI evidence:** PR run [#43594861745](https://github.com/PandaGarry/NEXUS/actions/runs/43594861745) passed exact PR HEAD `2c0135f1205a27f070b0b6a835aa3c19e904e540` on Python 3.11, 3.12 and 3.13. The bounded suite ran 28 tests per runtime. The complete matrix ran 166 tests per runtime / 498 test executions across ten isolated suites. This remains reference-level evidence only.
