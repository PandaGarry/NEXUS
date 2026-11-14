# NX-ARCH-REVIEW-005 — Revocation, Freshness & Control-Plane Outage Objectives

**Date:** 2026-11-14  
**Status:** PROPOSED ENGINEERING BASELINE — numeric objectives are recommendations only; OD-10 and owner/security acceptance remain OPEN  
**Scope:** NX-ARCH-008/009 revocation requirements, NX-IF-004 freshness/recovery, NX-IF-005 halt propagation, NX-SEC-001 credential isolation  
**Related:** NX-ARCH-REVIEW-003, NX-ARCH-REVIEW-004, NX-OWNER-DECISIONS-001

## 1. Purpose and separation of concerns

Existing contracts require revocation generations, bounded authorization freshness, cancellation/containment of in-flight work, source-specific freshness policies and fail-closed recovery. They intentionally do not set numeric values. OD-10 explicitly reserves source thresholds, completeness/retention, clock uncertainty, retry budgets and RTO/RPO for owner decision.

This proposal turns those open requirements into measurable candidate profiles without accepting them as policy. It keeps four independent clocks/states separate:

1. **Authorization freshness:** whether a user/workload grant and its revocation generation are current.
2. **Data freshness:** whether market/account/order/fill/Ledger evidence is current and complete for a specific operation.
3. **Control propagation:** whether a halt/revocation reached every enforcement boundary and stale workload is unable to act.
4. **Recovery readiness:** whether evidence, reconciliation and dependencies are sufficient to reopen an exact scope.

A fresh authorization does not make stale financial evidence safe. A fresh data snapshot does not grant permission. A halt request is not proof of halt enforcement. A healthy process is not a READY RecoveryBarrier.

## 2. Existing normative constraints

- NX-ARCH-008: revoked/quarantined modules deny new work; in-flight behavior needs bounded cancellation/containment; no indefinite stale approval cache.
- NX-ARCH-009: stale or unknown grant generation is invalid; privileged actions never fail open; cache invalidation is not proof of secret/process/network revocation; ALLOW is request-scoped.
- NX-IF-004: freshness is per source, scope and operation; unconfigured mandatory evidence blocks risk-increasing authorization; elapsed age uses monotonic time and explicit clock quality; READY RecoveryBarrier is scoped.
- NX-IF-005: halt epochs are durable and monotonic; each dispatch boundary checks the current epoch immediately before send; a boundary that does not acknowledge must be isolated/disabled; HALTED is not fully enforced while an unisolated dispatcher can still send.
- NX-SEC-001: credentials are isolated; revocation/rotation and incident containment require tested procedures; no live enablement before evidence-based acceptance.
- NX-OWNER-DECISIONS-001: OD-10 remains OPEN. No numeric freshness, recovery or RTO/RPO values are accepted.

## 3. Proposed authorization freshness profiles

The following values are **candidate engineering targets for discussion**, not production guarantees or approved SLOs.

| Data/action class | Candidate authorization check | Candidate cache bound | Candidate revocation objective | Failure behavior |
|---|---|---:|---:|---|
| PUBLIC / low-sensitivity INTERNAL read | Validate signed current registry/grant generation; cache only immutable definitions and bounded read authorization | Up to 30 seconds | Propagate revocation to all healthy enforcement points within 30 seconds; hard containment deadline 60 seconds | At cache expiry or unknown generation, deny; if a node misses hard deadline, quarantine/disable that workload path |
| PERSONAL read | Online subject/resource authorization for each request; do not reuse a prior ALLOW across requests | No reusable positive ALLOW cache | New requests denied after authoritative revocation; active stream/job cancellation target ≤5 seconds after local revocation receipt | If authority unavailable or generation uncertain, deny; terminate stream/job where supported |
| FINANCIAL_RESTRICTED read/export | Online current authorization per request and per page/chunk boundary; export job rechecks before each irreversible publication/download step | No reusable positive ALLOW cache | New reads/exports denied after revocation; active export cancellation target ≤2 seconds after local receipt and before next chunk/publication | Fail closed; quarantine export worker if cancellation cannot be confirmed |
| State-changing module operation | Online current authorization and domain-owner transaction check for every operation; request-scoped decision only | No positive ALLOW cache | No new side effect after the owner boundary observes revocation; queued jobs must revalidate before each side effect | Deny on outage/unknown generation; committed effects remain auditable and are reconciled, not falsely rolled back |
| SECRET / signing / venue credential | Not grantable to optional modules | Not applicable | Immediate independent secret/workload/network containment under incident runbook | No optional-module access; containment must not rely only on cache invalidation |

### 3.1 Recommended conservative starting profile

For a first non-production, read-only module prototype:

- Permit at most PUBLIC/INTERNAL read access, with a maximum 30-second authorization snapshot age.
- Do not include PERSONAL or FINANCIAL_RESTRICTED fields in the prototype unless the source owner explicitly approves the fields and online authorization path.
- Require an online current grant-generation check for every state-changing operation; do not create such operations in the first prototype.
- Use a 30-second revocation propagation target and a 60-second hard containment deadline only as measurable test targets. If a workload misses the deadline, remove it from service, revoke its workload identity and isolate its network path; do not silently extend the deadline.
- Treat these as acceptance candidates only after threat review, load/partition testing and owner approval. A measured p99 is not a hard upper bound; report p50/p95/p99/max and timeout/failure distributions separately.

This profile is deliberately narrow and does not imply that a production service can meet the target before implementation and measurement.

## 4. In-flight work and side-effect semantics

Revocation cannot retroactively undo a committed transaction or a side effect already accepted by an external system. Contracts must distinguish:

1. request received;
2. authorization evaluated;
3. work queued;
4. transaction started;
5. durable commit completed;
6. external side effect started/accepted;
7. completion or ambiguous outcome reconciled.

Required behavior:

- A queued job rechecks current generation immediately before each side effect.
- A worker receiving revocation stops dequeuing new work and cancels cancellable work.
- If cancellation cannot be acknowledged before the configured deadline, the workload is quarantined and its credentials/routes are independently revoked or isolated.
- A transaction already committed is not described as rolled back. Its durable result is audited and reconciled.
- For any external side effect with uncertain outcome, preserve the source contract's ambiguity state; never retry blindly.
- Revocation does not bypass NX-IF-001/002/003/004/005, and module revocation must not become an alternative route into protected financial operations.

## 5. Control-plane outage matrix

| Failure | PUBLIC / INTERNAL read | PERSONAL / FINANCIAL_RESTRICTED read | State-changing module work | Protected execution domains |
|---|---|---|---|---|
| Registry unavailable, cached snapshot still within candidate bound | May continue only if artifact, audience, generation and expiry are verifiable and policy permits | Deny unless an owner-approved online authorization path is still available | Deny | Independent of registry; enforce own domain state and security gates |
| Authorization service timeout/indeterminate | No soft allow; only bounded low-risk stale-read exception if explicitly approved | Deny | Deny | Risk/Execution do not call module authorization/Billing synchronously |
| Revocation generation unknown/stale | Deny when snapshot exceeds approved age | Deny | Deny | Protected domains use authoritative own epochs/state |
| Revocation event delivered to some but not all workers | Affected worker may serve only within explicitly approved low-risk window; missed hard deadline means quarantine | Deny at stale worker | Deny at stale worker | Halt/dispatch boundaries require independent current epoch check; stale dispatcher isolated |
| Audit sink unavailable | Low-risk read may be policy-limited only if security review explicitly permits; otherwise deny | Deny for privileged or restricted operations | Deny | Protected actions follow their own durable audit requirements; no silent loss |
| Workload identity/secret revocation cannot be confirmed | Stop module admission and isolate affected workload | Deny | Deny | No failover to a stale signer/egress process; CREATE remains blocked until positive fencing/reconciliation |
| HEGC process unavailable | Low-risk reads follow independent policy | Deny privileged/restricted operations | Deny | No new EgressBoundaryAuthorization grant; halt request may remain pending; gate-committed attempts remain in-flight/reserved until socket initiation is observed or sender is fenced; do not report fully enforced HALTED |
| HEGC authoritative store unavailable/uncertain | No effect on unrelated reads | Deny | Deny | Egress denies all new final gates; no cached-epoch soft allow; halt remains pending until durable epoch commit and boundary acknowledgements/isolation |
| HEGC integrity/workload identity compromised | Quarantine affected control-plane trust domain | Deny | Deny | Egress independently verifies Risk approval/reservation and fails closed on uncertain control state; isolate HEGC and positively fence stale Egress/control processes before any recovery |

No optional module or entitlement service may become a synchronous dependency of Risk, command acceptance, dispatcher or Trusted Egress. Protected execution must enforce its own halt epoch, current reservation, approval consumption, RecoveryBarrier and egress fencing. HEGC is the sole control-plane serialization authority for halt/final-gate records; it has no venue credentials or socket, and Egress has no direct write access to those records.

## 6. Data freshness and RecoveryBarrier — do not use a global TTL

NX-IF-004 correctly rejects a universal “fresh within N seconds” rule. Thresholds must be versioned by source, scope and operation class. The first implementation-readiness artifact should be a source-specific matrix, not a single global constant.

| Source | Required policy dimensions | Required fail-closed condition |
|---|---|---|
| Public market data | venue/feed, instrument, market type, strategy/operation class, event age, receive age, sequence/checksum, gap recovery, clock uncertainty | Missing/unknown mandatory feed evidence, invalid sequence or freshness beyond approved policy |
| Private orders/fills | venue/account, connection generation, stream sequence/cursor, REST coverage, unresolved order/fill outcomes, retention window | Gap, incomplete history, ambiguous outcome or stale order/position evidence |
| Account balances/positions | exact account/subaccount, snapshot version, source watermark, reconciliation status, external/manual activity | Unknown or unreconciled exposure; no inferred zero balance/position |
| Instrument specification | venue/instrument/version, tick/lot/multiplier/contract unit, effective interval and provenance | Missing, stale or incompatible spec version |
| Ledger projection | journal commit watermark, inbox/outbox offsets, posting-rule version, reconciliation status | Projection lag or discrepancy outside approved policy; do not infer Ledger truth from Execution event alone |
| Risk policy / halt state | immutable policy version, scope, halt epoch, approval validity and consumption state | Unknown/stale policy or halt generation; reject authorization |
| Clock service | monotonic continuity, wall-clock offset and uncertainty, synchronization health | Excessive/unknown uncertainty for any policy that depends on elapsed/event time |

The table deliberately leaves numeric thresholds blank. A source owner must provide venue/protocol retention and semantics; the Risk owner defines operation-specific acceptance; the owner accepts the residual risk. Any unconfigured mandatory threshold remains UNKNOWN and blocks the affected risk-increasing operation.

## 7. Halt propagation and stale dispatcher containment

NX-IF-005 requires every dispatcher to acknowledge the current monotonic halt epoch or be isolated before the system reports HALTED as fully enforced. This review does not assign a numeric halt deadline because it depends on the selected runtime, process topology, network fence and OD-12 emergency governance.

The halt transition is owned by the independently authorized emergency Control Plane, not by the Risk Engine process. Risk application outage therefore need not block a durable halt commit while the authoritative halt-state store remains available. If that store is unavailable or authority is uncertain, Egress cannot commit its final gate and denies new sends; the request remains pending and HALTED is not reported as fully enforced until the epoch is durably committed and all dispatch boundaries acknowledge it or are positively isolated.

The acknowledgement boundary must also account for attempts whose final Trusted Egress authorization committed immediately before the halt epoch. Halt and final egress authorization must serialize against the same authoritative halt-state generation. A halt commit that wins first denies the final gate. A final-gate commit that wins first creates an in-flight attempt that cannot be retroactively revoked; Egress must track it until socket initiation is observed or its sender is positively fenced. The Egress boundary cannot acknowledge the newer halt epoch while a paused pre-halt authorized attempt could still resume and initiate a socket write. Such an attempt remains potentially sent and must be reconciled. Positive fencing proves only that the sender cannot initiate a future write; absent a trusted initiation report, it does not prove no earlier side effect occurred. Keep the attempt OUTCOME_UNKNOWN and its reservation held until venue reconciliation; do not infer DEFINITELY_NOT_SENT from host/process termination. Therefore, HALTED means no stale/queued attempt can newly initiate a send after boundary acknowledgement, not that the venue cannot process requests already initiated before acknowledgement.


Before G1, measure and record separately:

- time from durable halt epoch commit to each enforcement boundary receiving it;
- time to stop new queue claims;
- time to cancel queued but undispatched risk-increasing commands;
- time to prove a stale process cannot reach the venue socket;
- time to revoke workload identity/secret access and network path;
- behavior under partition, paused process, host suspension, clock skew and lost acknowledgement.

A database lease, cache invalidation or successful API response is not proof of external fencing. If a stale Egress process might still transmit, the affected scope remains HALTED and CREATE remains blocked. Takeover requires positive fencing of the old process/host/network path plus reconciliation of every possibly-sent attempt.

## 8. Measurement and acceptance protocol

For each candidate objective, tests must capture:

- event timestamps from a monotonic clock plus wall-clock/uncertainty metadata;
- generation/epoch at issuer, cache, worker and enforcement boundary;
- request and in-flight job state at revocation time;
- whether a side effect occurred after local revocation receipt;
- cancellation acknowledgement and quarantine/fencing result;
- behavior under packet loss, partition, process pause/restart, stale cache, queue backlog and control-plane outage;
- p50/p95/p99/max, missed deadlines, false denials and recovery duration.

Evidence must be observed at the actual API/process/DB/secret/network boundary, not inferred from a mock policy decision. A test must fail if a stale workload can still perform a side effect after the hard containment deadline. Fault-injection should include CAP-08, CAP-16, CAP-17, MOD-05, MOD-15 and MOD-16, plus stale dispatcher/halt cases from NX-IF-005.

## 9. Owner decisions and gates

| Decision | Proposed owner | Gate | Current state |
|---|---|---|---|
| Approve authorization cache profiles and revocation propagation/hard containment objectives | Platform Security + Identity/Registry owners | G0D/G1 | OPEN |
| Approve field classes allowed in first prototype and per-field retention | Source domain owners + Security/Privacy | G0D/G1 | OPEN |
| Approve source-specific freshness thresholds and clock uncertainty | Market Data, Execution, Ledger, Risk owners | G1/G2; OD-10 | OPEN |
| Approve retry budgets, completeness/retention, RTO/RPO | Domain owners + platform operations | G1/G2; OD-10/OD-15 | OPEN |
| Approve halt propagation deadline, operator roles, dual control and containment path | Owner + Security/Operations | G1/G3; OD-12 | OPEN |
| Approve external Egress fencing and authority takeover evidence | Execution + Security + owner | G1/G3; OD-08/09/10/12 | OPEN |

## 10. Disposition

**PROPOSED ENGINEERING BASELINE — NOT ACCEPTED.** The 30-second low-risk authorization snapshot, 60-second hard containment deadline, 5-second PERSONAL-stream cancellation target and 2-second FINANCIAL_RESTRICTED export cancellation target are discussion candidates only. They are not service guarantees, production SLOs or approved policy. No numeric market-data/account/ledger freshness threshold, halt deadline, RTO/RPO or recovery budget is selected.

No executable policy, cache, revocation service, authorization service, module runtime, secret manager, network fence, dependency or production deployment was created. G0D/G1 remain open; OD-10 and OD-12 remain open. No real credentials, venue connection or live trading authority is introduced.
