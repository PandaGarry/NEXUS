# NX-REF-VENUE-002 — Eligibility Egress Fencing Reference Model

**Status:** TEST-ONLY CONCURRENCY REFERENCE / NOT PRODUCTION EGRESS  
**Date:** 2026-11-14  
**Parent decision:** [NX-ADR-007](NX-ADR-007-venue-eligibility-jurisdictional-activation-gate.md)  
**Related reference:** [NX-REF-VENUE-001](NX-REF-VENUE-001-venue-eligibility-evidence-reference-model.md)

## Purpose

NX-REF-VENUE-001 evaluates evidence completeness and freshness. It does not model the race between a live command and an eligibility suspension. NX-REF-VENUE-002 adds a deliberately small single-process reference authority to make the required ordering executable.

The core invariant is:

> A dispatch that linearizes before a suspension may complete or become OUTCOME_UNKNOWN; once the suspension epoch has advanced, an older command cannot begin a new adapter side effect through this authority.

The model does not claim that a venue cancels an already accepted order when eligibility is suspended.

## Model

The 'venue_egress_fencing.py' module defines:
- immutable 'EligibilitySnapshot' bound to record ID, revision, scope digest, epoch, mode and expiry;
- immutable 'EgressCommand' bound to command ID, record ID, revision, scope digest, epoch, expiry and payload digest;
- 'EligibilityEgressAuthority', which serializes state changes and adapter send calls under one process-local lock;
- explicit outcomes: DENIED, SENT, VENUE_REJECTED and OUTCOME_UNKNOWN;
- explicit denial reasons for scope, record, revision, epoch, mode and expiry mismatch.

The command ID is consumed on its first attempted dispatch, including a denied attempt. Reuse is rejected. An adapter exception or unexpected non-boolean result becomes OUTCOME_UNKNOWN; it is not treated as a safe retry.

## Linearization and race semantics

- If dispatch obtains the authority lock first, its final scope/revision/epoch/mode/expiry checks occur before the adapter call. Suspension waits until the call returns. The dispatch is therefore ordered before the suspension epoch change.
- If suspension obtains the lock first, it increments the epoch and sets SUSPENDED. A later command using the old epoch is denied before the adapter is called.
- A command must match the exact current scope digest, record ID, record revision and eligibility epoch.
- A command cannot outlive its eligibility snapshot.
- Duplicate command IDs cannot be resent, including after OUTCOME_UNKNOWN.

This model chooses a simple serialization point so the ordering can be tested. It intentionally does not try to make a remote exchange side effect and a local database transaction atomic.

## Test coverage

The 'test_venue_egress_fencing.py' suite contains 19 deterministic tests:
- current exact-scope dispatch;
- suspended state denial;
- stale command after suspension;
- scope, record, revision and epoch mismatch;
- snapshot and command expiry;
- command expiry later than snapshot expiry;
- one-time command ID consumption after denial;
- ambiguous send becomes OUTCOME_UNKNOWN and cannot be retried;
- explicit venue rejection outcome;
- concurrent send/suspend ordering;
- post-suspension dispatch denial;
- monotonic epoch and immutable scope;
- invalid clock, type confusion and invalid adapter inputs.

## Exact-head CI evidence

- PR #14 head at verification: `ccbf9e86b86a366fb99c55f5d23deccd5755e5f9`.
- GitHub Actions run: [43598800464](https://github.com/PandaGarry/NEXUS/actions/runs/43598800464).
- Python 3.11: 229 tests, SUCCESS.
- Python 3.12: 229 tests, SUCCESS.
- Python 3.13: 229 tests, SUCCESS.
- Total: 687 test executions across the three-runtime matrix.
- Egress fencing suite: 19 tests per runtime (57 executions).

This run used the single, non-duplicated egress-fencing CI step. Evidence applies to the exact SHA above; later source/workflow changes require a new run.

## Critical limitations

- The lock is process-local. It does not fence another process, host, container or stale worker.
- Holding a local lock while a network call runs is a test simplification, not a production architecture recommendation. Production requires a dedicated egress authority that exclusively holds venue credentials, durable dispatch state, bounded adapter timeouts, explicit in-flight tracking and a trusted fencing protocol.
- A process crash or network timeout after the exchange may have accepted a request remains OUTCOME_UNKNOWN. Recovery must reconcile; no blind resend.
- A suspension cannot undo a request already transmitted or cancel a venue-side working order.
- The model has no durable journal, database transaction, crash recovery, network isolation, signing, key vault, multi-region consensus or venue adapter.
- A blocked or dead egress process requires an independently designed operator/process-fencing mechanism; this model does not solve it.
- It does not authorize cancel, close, reduce-only, cancel-all or flatten operations after suspension. Those remain governed by NX-IF-005 and product-specific legal/venue rules.

**Disposition:** test-only concurrency reference. No production egress, venue credentials or live trading capability is implemented.
