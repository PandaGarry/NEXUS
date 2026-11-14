# NX-ARCH-004 — Rust Execution & Cross-Language Conformance Boundary

**Status:** PROPOSED — architecture/owner review required  
**Version:** 0.1  
**Date:** 2026-11-14  
**Work item:** GitHub Issue #15  
**Branch:** `engineering/rust-execution-domain-conformance-v0`  
**Base:** `ab6976933cb4de9b5320b73531034d02edc53907`  
**Related:** NX-ARCH-001/003, NX-ADR-002/005/007, NX-IF-001..005, NX-SEC-001, NX-REF-EXEC-001/002, NX-REF-VENUE-001/002, NX-REF-DOMAIN-001..010, NX-RESEARCH-006..009, ТЗ-NX-004..006.

## 1. Purpose and decision boundary

This document proposes a bounded implementation architecture for the first Rust-based NEXUS execution/domain components and a language-neutral conformance harness.

It does **not** approve a production runtime, select an exchange, authorize credentials or orders, select numeric production limits, or make NautilusTrader an execution authority. It does not claim that a Rust workspace or production implementation already exists.

The immediate objective is to convert existing Python reference evidence into a language-independent contract that a future Rust implementation must satisfy before it can be considered for read-only or paper integration.

## 2. Proposed architectural decisions

| ID | Proposed decision | Status |
|---|---|---|
| RUST-01 | Rust is the candidate implementation language for bounded domain and trusted execution-boundary components; final toolchain/profile remains subject to reproducible-build review. | PROPOSED |
| RUST-02 | Python reference models remain independent mathematical/protocol oracles; they are not imported into or trusted by production runtime. | PROPOSED |
| RUST-03 | Shared behavior is specified by versioned language-neutral fixtures and explicit rejection classes, not by matching implementation internals. | PROPOSED |
| RUST-04 | Venue adapters are untrusted protocol translators and cannot hold independent command authority or bypass trusted egress. | PROPOSED |
| RUST-05 | Risk, reservation, command durability, egress authorization, Ledger posting and recovery remain separately owned boundaries under NX-IF-001..005. | PROPOSED |
| RUST-06 | NautilusTrader may be evaluated for bounded reuse only after an adapter/authority conformance proof; it is not the source of NEXUS authorization or durable-before-dispatch guarantees. | PROPOSED |

No decision in this table is owner-accepted by publication alone.

## 3. Trust and authority model

The target command path is:

`Strategy / AI -> TradeIntent -> Risk evaluation + atomic durable reservation -> signed RiskApprovalCapability -> command coordinator atomically consumes approval and durably commits command/outbox -> dispatcher durably records attempt -> trusted egress gate -> venue adapter -> venue`

The response path is:

`venue events / REST evidence -> adapter normalization -> canonical execution inbox -> deduplication + reconciliation -> Ledger posting -> projection watermark -> Risk exposure transition`

Mandatory invariants:

1. Strategy, AI, UI and analytics processes cannot access private venue credentials or direct private venue network egress.
2. A TradeIntent is not an order. It becomes dispatchable only after payload-bound authorization and durable command/reservation state are committed.
3. The trusted egress boundary revalidates account scope, command identity, payload digest, approval revision, reservation state, venue eligibility record/revision/epoch, halt epoch and dispatcher authority immediately before network send.
4. Adapter code cannot mint authorization, increase risk limits, release reservations, classify its own ambiguous outcome as safe to retry, or bypass egress through an alternate HTTP/WebSocket client.
5. A transport timeout after a possible send is `OUTCOME_UNKNOWN`, not a rejection. No blind retry is permitted. Reconciliation must establish venue state or preserve uncertainty and exposure.
6. Fills and fees are immutable evidence. Ledger owns accounting effects; Risk exposure is not released merely because an adapter reports a terminal-looking status.
7. Recovery and authority transfer require independently enforced old-egress fencing. A database lease, process-local mutex, local epoch check or expired token alone is not a network fence.

The exact durable transaction, signer, network enforcement point, storage and deployment design remain OPEN.

## 4. Component boundaries

### 4.1 Domain kernel

The pure domain layer owns validated, immutable types and deterministic calculations:

- Instrument identity and immutable InstrumentSpec version.
- Dimensional AssetAmount, Money, Price, Notional and instrument-scoped ContractCount.
- Exact decimal and rational operations with explicit bounded admission.
- Explicit operation-specific rounding only at a qualified boundary.
- Canonical numeric wire parsing and serialization.

It must not depend on exchange SDKs, network clients, wall-clock access, databases, UI types or strategy code.

### 4.2 Command and authorization boundary

The command gateway accepts only a canonical command envelope linked to:

- exact account and venue scope;
- immutable payload digest and schema version;
- Risk approval identity/revision and validity window;
- reservation identity/version;
- eligibility record identity/revision/epoch;
- halt/authority epoch;
- unique command and attempt identifiers.

The ordering is normative and follows NX-IF-001/002:

1. Canonicalize the immutable command and compute its digest.
2. Risk evaluates current evidence and atomically commits the required `PRE_DISPATCH_RESERVATION` across all affected scopes.
3. Only after that durable reservation commit may Risk issue a short-lived `RiskApprovalCapability` bound to the exact command digest, reservation, scope and versions.
4. The command coordinator validates the capability and atomically consumes its single-use authorization while committing the command and outbox record. The reservation remains held in `PRE_DISPATCH_RESERVATION`; it is not released or counted twice.
5. The dispatcher durably claims the outbox attempt under a monotonic fencing token and commits a pre-egress attempt marker. That marker moves the conservative exposure bucket from `PRE_DISPATCH_RESERVATION` to `DISPATCH_OUTCOME_UNKNOWN` before the external side effect. It is not evidence that bytes were sent: a crash between marker and socket write is deliberately treated as potentially sent until reconciled, preventing premature release of exposure.
6. Immediately before the network side effect, trusted egress revalidates the approval-consumption evidence, active reservation, exact persisted payload/digest, current halt epoch, eligibility record/revision/epoch, command/attempt identity and dispatcher fence. Only the trusted egress boundary can transmit the persisted canonical payload and record transport evidence.

Cross-contract review is now harmonized: NX-IF-002 requires the reservation commit to precede approval issuance; NX-IF-001 requires single-use approval consumption to be durable and atomic with dispatch eligibility; NX-ADR-002 now states both boundaries explicitly. The production store and transaction semantics remain unselected and require a separate implementation design proof.

### 4.3 Trusted egress

The trusted egress service is the only process permitted to reach private order endpoints. It must enforce fencing outside the adapter process, such that a paused or partitioned stale worker cannot send after authority revocation.

A successful pre-send check is not sufficient if the worker can be paused between check and send. The chosen network enforcement mechanism must make revocation effective at the actual egress point or terminate/revoke the old sender's ability to reach it.

No provider, proxy, sidecar, host supervisor or cloud control plane is selected in this document.

### 4.4 Venue adapter

An adapter translates canonical commands/events and reports evidence. It declares capabilities by exact venue legal entity, product family, account mode and API version.

Required adapter outputs distinguish at least:

- `DEFINITELY_NOT_SENT` — transport evidence proves no request could have reached the venue;
- `VENUE_REJECTED` — authenticated venue response identifies a rejection;
- `VENUE_ACCEPTED` — authenticated evidence identifies venue acceptance, subject to subsequent order lifecycle events;
- `OUTCOME_UNKNOWN` — send may have occurred but authoritative result is not established.

The adapter must not collapse these states into a boolean success/error. Retry classification is operation- and venue-specific, documented, versioned and tested. Unknown outcomes are reconciled, not blindly retried.

Capabilities include client-order-ID semantics, idempotency scope, query-by-client-ID support, event identity, sequencing, replay, correction/bust semantics, rate limits, precision/quantity rules, cancel/replace behavior and reconciliation coverage. Unknown capability means unsupported for the relevant operation.

## 5. Rust domain and numeric implementation constraints

The Python arbitrary-precision reference models remain the independent oracle. Rust production candidates must be evaluated against NX-REF-DOMAIN-001..010, including canonicalization, exact arithmetic, dimensional rejection, rational preservation, bounded preflight and wire vectors.

A single decimal crate must not be assumed to satisfy every domain requirement. Evaluate separately:

1. bounded decimal representation for finite decimal values;
2. checked integer arithmetic and explicit overflow behavior;
3. exact reduced rational intermediates where division is non-terminating;
4. typed dimensional wrappers carrying asset/currency/instrument/spec identity;
5. canonical wire representation and input/output resource budgets;
6. operation-specific rounding at named policy boundaries.

Binary floating point is prohibited as authoritative storage/calculation for prices, quantities, balances, fees, funding, margin, notional and P&L. If an upstream venue transmits IEEE-754 values, conversion must occur at the adapter boundary under an explicit, loss-aware rule; a float must never be silently promoted to exact venue truth.

Production numeric limits, maximum input sizes, maximum coefficient/scale, rational growth limits, overflow policy and resource budgets require a separate reviewed profile. The test-only NumericLimits in NX-REF-DOMAIN-007 are not production defaults.

## 6. Cross-language conformance contract

Golden fixtures are language-neutral inputs and expected outcomes. Rust and Python must agree on:

- canonical accepted representation;
- exact result values and units;
- normalized rejection/error class;
- boundary behavior at configured numeric limits;
- malformed, oversized and non-canonical wire input rejection;
- idempotent replay and duplicate identity handling;
- deterministic ordering where ordering is part of the contract.

The harness must not compare incidental error strings, debug formatting, hash-map iteration order or implementation-specific exception types.

Each fixture has a stable ID, schema version, operation, input, expected result or rejection class, and provenance. Fixture changes require versioning and review. Existing vectors are synthetic mathematics, not venue qualification.

## 7. Failure-injection and adversarial matrix

| Scenario | Required authoritative outcome |
|---|---|
| Crash before durable command commit | No dispatch is possible; no reservation is consumed without the atomic commit contract. |
| Crash after commit but before send | Command remains recoverable; dispatcher may claim it only under current authority and fencing. |
| Crash after send before ACK | Preserve `OUTCOME_UNKNOWN`; reconcile; never blind-retry. |
| Delayed ACK after recovery | Record as stale observation; it cannot overwrite newer authoritative state. |
| Duplicate venue event | Idempotent event identity prevents duplicate fill/fee/Ledger effect. |
| Partial fill then cancel | Preserve fill exposure; reconcile residual quantity and cancel outcome separately. |
| Cancel/fill race | Both facts are retained; final exposure derives from canonical fills and reconciled remaining order state. |
| Eligibility suspension during dispatch | Egress fencing prevents a stale sender from reaching venue after suspension takes effect. |
| Old worker resumes after failover | Old worker cannot send or mutate authoritative state. |
| Duplicate command/attempt ID | Reject or return the exact prior durable outcome; never create a second side effect. |
| Numeric budget exceeded | Reject before unbounded allocation/arithmetic expansion; no truncation or implicit rounding. |
| Unknown instrument metadata/capability | Fail closed for affected order operation. |

The Python reference models cover selected protocol/math cases only. The matrix is not evidence that these properties are implemented in production.

## 8. NautilusTrader evaluation policy

Three integration paths remain under evaluation:

- **Selective library reuse:** reuse narrowly scoped, reviewed components while NEXUS retains command, Risk, Ledger, recovery and egress authority.
- **Out-of-tree adapter integration:** use an upstream runtime only as a market/event or adapter host behind NEXUS-owned interfaces and fencing.
- **Full runtime adoption:** deferred unless exact-version source audit and adversarial conformance prove that all required NEXUS authority and durability invariants remain enforceable.

Popularity, Rust implementation, adapter count or upstream CI status is not sufficient evidence. Each exact upstream version and adapter path requires source-pinned review. No dependency is approved by this document.

## 9. Implementation sequence and gates

1. **Contract freeze candidate:** review NX-ARCH-004 with NX-IF-001..005 and NX-ARCH-003; resolve contradictions and owner decisions.
2. **Workspace readiness:** only after applicable G0D/G1 approval, establish pinned Rust toolchain, Cargo workspace, lockfile, dependency/license policy, reproducible CI and security scanning.
3. **Pure domain slice:** implement a small Rust crate for canonical scalar parsing, exact arithmetic, bounded admission and dimensional wrappers; run existing golden vectors.
4. **Differential tests:** run Python and Rust against the same fixtures; add deterministic property and malformed-input cases.
5. **Command protocol reference:** implement a non-networking state-machine model with crash/replay/concurrency tests.
6. **Egress design proof:** select a concrete enforcement architecture and demonstrate stale-worker network denial under adversarial pause/resume and partition tests. No live venue required.
7. **Adapter certification:** only after a venue/product/account is independently legally and technically qualified; sandbox/read-only first.
8. **Paper/shadow gate:** separate owner authorization and evidence review; no live trading implication.

No production workspace is created by this documentation-only change. If the current repository remains documentation/reference-model-only, that is an explicit G0D readiness blocker, not permission to bypass the gate.

## 10. Acceptance criteria

- [ ] Owner/architecture review accepts or revises RUST-01..06.
- [ ] NX-ARCH-004 is cross-reviewed against NX-IF-001..005, NX-ARCH-003, NX-ADR-002/005/007 and NX-SEC-001.
- [ ] Threat model maps direct egress, stale worker, compromised adapter, replay, secret exposure and numeric resource exhaustion to controls and tests.
- [ ] Production Rust toolchain/workspace decision is made under the relevant readiness gate.
- [ ] Rust domain implementation passes all applicable language-neutral golden vectors.
- [ ] Python/Rust differential tests agree on values, units and rejection classes.
- [ ] Bounded resource and overflow behavior are tested under the approved production profile.
- [ ] Command state-machine tests cover crash/replay/duplicate/concurrency and OUTCOME_UNKNOWN.
- [ ] A concrete independently enforced egress fence passes stale-worker adversarial network tests.
- [ ] Exact commit SHA, toolchain versions, dependency lock, CI run and test counts are recorded.
- [ ] Architecture index, roadmap, status, checklist and changelog are updated.
- [ ] No live credentials, private account connectivity, orders, transfers, deposits, withdrawals, production deployment or live-trading authorization.

## 11. Bounded cross-contract review note

A targeted readback of NX-IF-001..005, NX-ARCH-003, NX-ADR-002/005/007 and NX-SEC-001 found no remaining blocking authority-order contradiction in the reviewed path. The prior ADR-002 sequencing gap is closed in documentation: reservation is durably committed before approval issuance; single-use approval consumption is atomic with durable command/outbox commit; and the pre-egress attempt marker moves exposure conservatively into `DISPATCH_OUTCOME_UNKNOWN`. This is a documentation consistency result only, not runtime or distributed-fencing evidence; no production implementation exists to test.

## 12. Current disposition

**DOCUMENTATION DESIGN DRAFT ONLY.** This change does not add Rust source, Cargo workspace, production numeric types, production adapter, signer, persistence, trusted egress, venue connectivity or executable trading capability.

Prototype readiness remains BLOCKED. Live trading remains NOT AUTHORIZED.