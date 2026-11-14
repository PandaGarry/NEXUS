# NEXUS Exact Decimal Reference Oracle

**Status:** Experimental conformance aid; not production code.

This directory contains a dependency-free Python reference implementation used to generate/check expected results for the future production domain kernel.

## Run

From this directory:

```bash
python -m unittest -v  # run the exact-decimal suite; see workflow for isolated suite counts
```

## Scope

- strict decimal parsing (no exponent notation);
- canonical decimal formatting;
- exact comparison, addition, subtraction and multiplication;
- exact quantization only when no non-zero digits are discarded;
- language-neutral golden vectors in `golden-vectors-v1.json` (version 1.0.0).
- positive-step divisibility for tick/lot checks.

The model uses arbitrary-precision integer coefficients. This is intentionally different from a bounded production representation so it can act as an independent mathematical oracle.

- exact rational division with reduced numerator/denominator;
- exact finite-decimal conversion only for terminating base-10 expansions;
- explicit quantization requiring a named rounding mode (UNNECESSARY, DOWN, UP, FLOOR, CEILING, HALF_UP, HALF_EVEN);
- language-neutral division vectors in `division-golden-vectors-v1.json`.

## Explicit limitations

- no exchange connectivity, credentials, orders or persistence;
- no production performance or memory claims;
- no production rounding policy for exchange normalization, fees, funding, margin, P&L or accounting; no square roots or transcendental operations;
- typed financial dimensional wrappers and instrument quantity semantics exist as test-only references; no production integration;
- no approved production numeric limits or fixed-width overflow policy; the separate bounded reference context uses explicit synthetic limits only;
- no claim of production, Rust/WASM or backend conformance.

Never import this package into a production trading service. Production code must independently implement the approved contract and pass shared golden vectors, property tests and integration tests.


## Execution gateway reference slice

See [execution-gateway/README.md](execution-gateway/README.md) and [NX-REF-EXEC-001](../../docs/architecture/NX-REF-EXEC-001-command-gateway-reference-conformance.md). This is a test-only Python/SQLite conformance model with a fake adapter. Run its suite with:

```bash
cd execution-gateway
python -m unittest -v
```

The GitHub Actions workflow runs both reference suites on Python 3.11, 3.12 and 3.13. Run [#43588330433](https://github.com/PandaGarry/NEXUS/actions/runs/43588330433) passed on current exact HEAD `31c99f0b4a0591a41d97afa265145567cf1ddbd3` (10 exact-decimal tests + 17 gateway tests on each runtime). This is reference-model CI only; no production, multi-process or live-exchange guarantees are claimed.


## Exact rational division extension

Run `python -m unittest -v test_exact_division.py` from this directory. The dedicated suite contains 18 tests, including language-neutral vectors and 1,000 deterministic rational quantization property cases. GitHub Actions PR run [#43594118145](https://github.com/PandaGarry/NEXUS/actions/runs/43594118145) passed exact PR HEAD `a46b49a2cbb7a5960ce483f93a736a3fbc945554` on Python 3.11, 3.12 and 3.13: eight isolated suites, 127 tests per runtime / 381 matrix executions. This remains a test-only oracle.


Latest full reference workflow: [#43594275808](https://github.com/PandaGarry/NEXUS/actions/runs/43594275808) passed current PR HEAD `a47085efd19826d9fea6edcaf2245dd689a288e8` on Python 3.11–3.13: 129 tests per runtime / 387 matrix executions across eight isolated suites.


## Bounded numeric context and canonical wire

Run `python -m unittest -v test_bounded_numeric.py` for mandatory caller-supplied budgets, preflight checks and bounded operations. Run `python -m unittest -v test_numeric_wire.py` for versioned canonical scalar wire encoding. `NumericLimits` has no default profile; zero scale/zero power-of-ten are valid limits, while digit and input budgets must be positive. These modules are reference-only and do not establish production resource safety or a selected production profile.


Latest verified PR matrix: [#43595199511](https://github.com/PandaGarry/NEXUS/actions/runs/43595199511) passed exact PR HEAD `fddd03f59baa159d8ed345691221c2446b0f60e3` on Python 3.11–3.13. Ten isolated suites, 172 tests per runtime / 516 matrix executions; bounded numeric 32 per runtime and numeric wire 11 per runtime. Shared numeric wire vectors are in `numeric-wire-golden-v1.json`.


Canonical wire fixtures: `numeric-wire-golden-v1.json` (version 1.0.0) provides language-neutral valid/invalid decimal and rational cases, including integers beyond JavaScript's exact-number range. Run with `python -m unittest -v test_numeric_wire.py`.


The bounded context separates raw decimal literal input size (`max_input_chars`) from encoded scalar wire size (`max_wire_chars`). Both are mandatory independent budgets.
