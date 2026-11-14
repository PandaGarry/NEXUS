# NEXUS Exact Decimal and Execution-Gateway Reference Models

**Status:** Experimental conformance aids; not production code.

## Exact decimal oracle

The root of this directory contains a dependency-free Python reference implementation and language-neutral golden vectors for exact decimal parsing and arithmetic.

Run from this directory:

```bash
python -m unittest -v
```

## Execution gateway reference slice

The `execution-gateway/` directory contains a deliberately narrow executable model of the NEXUS command authorization and durable dispatch boundary.

Run:

```bash
cd execution-gateway
python -m unittest -v
```

The current model supports only one command class: `CREATE` in a test fixture. Its 23-test suite includes independent SQLite-connection concurrency races for one-time approval consumption and single-command dispatch claiming. It demonstrates:
- canonical command digest binding;
- test-only approval authentication and exact scope binding;
- expiry and current halt-epoch checks at intake and immediately before adapter invocation;
- active reservation binding and atomic one-time approval consumption with outbox persistence;
- no adapter invocation before transaction commit;
- durable `DISPATCHING` marker before the external call;
- conservative `OUTCOME_UNKNOWN` recovery after a crash/timeout;
- acknowledgement is not represented as a fill;
- unsupported command classes fail closed rather than inheriting CREATE semantics.

The suite also contains an intentionally passing **unsafe counterexample**: a stale worker pauses immediately before network send, recovery marks its command OUTCOME_UNKNOWN, and the worker then resumes and sends anyway. Conditional state transitions reject late ACK, stale pre-send rejection and adapter-error updates after recovery; stale ACKs and dispatch errors are recorded separately, preserving OUTCOME_UNKNOWN. The test still documents the unresolved egress-fencing defect; it is not a safety guarantee. It demonstrates why local SQLite state and a self-checked lease token cannot fence a stale process that still has direct venue egress access.

## Explicit limitations

- SQLite is a local transaction-boundary test fixture, not the selected production database or a deployment durability guarantee.
- HMAC is used only to make approval verification executable in tests. It is not the selected production signature scheme or key custody design.
- The fake adapter has no network or exchange behavior.
- The model does not implement exposure calculation, reservation capacity accounting, Risk policy evaluation, real signer isolation, venue reconciliation, fill/ledger posting, private streams, rate limits, cancel/replace, emergency actions or multi-process fencing or stale-worker egress isolation.
- The suite includes two independent SQLite connections racing to consume one approval and to claim one command; this verifies only local SQLite transaction serialization, not distributed leases or cross-host fencing. The model narrows but does not eliminate the halt/dispatch race between a final local check and an external network side effect. Production requires an authoritative fenced dispatch boundary and venue-specific recovery semantics.
- Python object encapsulation is not a security boundary. Strategies/AI must not be co-located with or granted access to production adapter credentials.
- No production, Rust/WASM, distributed, performance, fuzz or live-exchange conformance is claimed.

Never import this model into a production trading service. Production implementation must independently satisfy NX-IF-001/002/003/005 and NX-ADR-002, with reviewed database transactions, cryptographic custody, concurrency controls, adapter certification and fault-injection evidence.
