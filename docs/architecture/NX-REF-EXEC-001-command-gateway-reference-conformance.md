# NX-REF-EXEC-001 — Command Gateway Reference Conformance Slice

**Status:** EXPERIMENTAL REFERENCE MODEL — NOT PRODUCTION IMPLEMENTATION  
**Date:** 2026-11-14  
**Branch:** `foundation/domain-kernel-reference-v0`  
**Related contracts:** NX-IF-001, NX-IF-002, NX-IF-005, NX-ADR-002  
**Scope:** One local Python/SQLite CREATE-command path with a fake adapter. No exchange integration.

## 1. Objective

Turn a bounded subset of the NEXUS command authorization and execution-integrity contracts into executable fault-injection scenarios. The goal is to expose contract ambiguities before selecting a production language, database, signer or venue.

## 2. Modeled sequence

`CanonicalCommand → Approval verification → active reservation check → atomic approval consumption + outbox persistence → durable DISPATCHING marker → fake adapter invocation → ACKNOWLEDGED or OUTCOME_UNKNOWN`

The approval is bound to command ID/digest, account, venue, instrument, instrument-spec version, policy version, reservation, halt epoch, audience and expiry. The command payload is immutable and exact-decimal-only for its represented quantity/price fields.

## 3. Safety properties exercised

1. Invalid signature, wrong digest, wrong scope, expired approval or stale halt epoch blocks intake.
2. Reservation must be active and bound to the command.
3. Approval consumption, reservation consumption and command/outbox insertion commit atomically in the SQLite fixture.
4. Transaction failure before commit leaves no command and makes no adapter call.
5. No adapter call occurs while command state is only PERSISTED.
6. Dispatch first commits a DISPATCHING marker.
7. Process restart while DISPATCHING converts the command to OUTCOME_UNKNOWN; it is never blindly resent.
8. Transport timeout is OUTCOME_UNKNOWN, not rejection.
9. An approval that expires or whose halt epoch changes after persistence is rejected before adapter invocation in the deterministic harness.
10. Unsupported command types are rejected rather than treated as CREATE.
11. Venue acknowledgement is labeled ACCEPTED_NOT_FILLED.
12. Approval and command replay are rejected by durable uniqueness constraints.

## 4. Test scenarios

The test suite currently covers 20 deterministic cases:
- valid approval and one adapter invocation;
- tampered signature;
- command payload mutation;
- account scope mismatch;
- expired approval at intake;
- stale halt epoch at intake;
- released/wrong reservation;
- transaction failure before commit;
- crash after commit but before dispatch;
- crash after durable dispatch marker;
- restart using a new SQLite connection;
- halt epoch advance after persistence;
- approval expiry after persistence;
- unsupported CANCEL command;
- timeout after possible send;
- crash after simulated venue acceptance but before ACK persistence;
- duplicate approval/command replay;\n- two gateway instances concurrently racing to consume the same approval/reservation;\n- two dispatcher instances racing to claim one persisted command while the winning adapter call is held open;
- non-canonical decimal rejection.

## 5. Verification record

Local command:

```bash
cd foundation/reference-model/execution-gateway
python -m unittest -v
```

GitHub Actions run [#43588971888](https://github.com/PandaGarry/NEXUS/actions/runs/43588971888) completed with **success** on exact HEAD `d22d417da0d11dab5b9bb79298edd379eab46867`. Both suites passed on Python 3.11, 3.12 and 3.13: 10 exact-decimal tests and 20 gateway tests in each runtime.

This is CI verification of the checked-in reference model only. It is not production, multi-process, database durability, security or exchange-adapter verification.

## 6. Deliberate exclusions and unresolved risks

- CREATE only. AMEND, CANCEL, CLOSE, REDUCE_ONLY, CANCEL_ALL and FLATTEN require separate complete command schemas and policy matrices.
- Risk decision creation and numeric exposure calculations are not implemented. The reservation row is a pre-created fixture, not a risk engine.
- HMAC test helper is not production cryptography. No production signing key, key rotation, HSM/KMS or signer boundary exists.
- SQLite local transaction semantics are not a production database decision.
- No durable dispatcher lease, cross-host claim fencing, serializable reservation-capacity transaction or distributed halt-epoch authority. The new two-connection/thread tests exercise SQLite's local write serialization only; they are not proof of process supervision, host failure handling or a production multi-worker lease protocol.
- A process crash after DISPATCHING is conservatively unknown even if the network call had not yet happened. This intentional false-positive is safer than a duplicate send.
- A final local halt check cannot fully eliminate the race between local state read and external network side effect. Production needs a single fenced gateway boundary and venue-aware reconciliation.
- No order/fill private stream, ledger journal, reconciliation, rate-limit policy or external/manual order handling.
- No live credentials, venue account, network order, risk limit or production deployment.

## 7. Next conformance gate

Before promoting this model into a production-language prototype:
1. Owner/security review the canonical command and approval schemas.
2. Define the durable reservation/outbox transaction boundary and DB isolation requirements.
3. Define a fenced dispatch protocol for halt epochs and concurrent dispatchers.
4. Add durable dispatcher leases and multi-process race tests.
5. Add crash injection at every transaction/network boundary, including acknowledgement persistence.
6. Add venue capability and reconciliation interfaces without implementing a real venue.
7. Implement the same golden scenarios independently in the selected production language.
8. Prove the adapter is inaccessible to Strategy/AI and every state-changing path passes the gateway.

No production-readiness gate is satisfied by this reference slice.
