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

## Explicit limitations

- no exchange connectivity, credentials, orders or persistence;
- no production performance or memory claims;
- no division, rounding, square roots or transcendental operations;
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

The GitHub Actions workflow runs both reference suites on Python 3.11, 3.12 and 3.13. A workflow definition is not evidence of a pass; consult the run attached to the exact PR HEAD. No production, multi-process or live-exchange guarantees are claimed.
