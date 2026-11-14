# NEXUS Exact Decimal Reference Oracle

**Status:** Experimental conformance aid; not production code.

This directory contains a dependency-free Python reference implementation used to generate/check expected results for the future production domain kernel.

## Run

From this directory:

```bash
python -m unittest -v  # 10 tests, including shared golden vectors
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
- no financial units/currencies/contracts yet;
- no bounded-overflow simulation;
- no claim of production, Rust/WASM or backend conformance.

Never import this package into a production trading service. Production code must independently implement the approved contract and pass shared golden vectors, property tests and integration tests.


## Execution gateway reference slice

See [execution-gateway/README.md](execution-gateway/README.md) and [NX-REF-EXEC-001](../../docs/architecture/NX-REF-EXEC-001-command-gateway-reference-conformance.md). This is a test-only Python/SQLite conformance model with a fake adapter. Run its suite with:

```bash
cd execution-gateway
python -m unittest -v
```

The GitHub Actions workflow runs both reference suites on Python 3.11, 3.12 and 3.13. Run [#43588330433](https://github.com/PandaGarry/NEXUS/actions/runs/43588330433) passed on current exact HEAD `31c99f0b4a0591a41d97afa265145567cf1ddbd3` (10 exact-decimal tests + 17 gateway tests on each runtime). This is reference-model CI only; no production, multi-process or live-exchange guarantees are claimed.
