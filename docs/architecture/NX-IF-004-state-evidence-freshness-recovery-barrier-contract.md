# NX-IF-004 — State Evidence, Freshness & Recovery Barrier Contract

**Date:** 2026-11-14  
**Status:** PROPOSED — normative interface draft; not accepted  
**Work package:** NX-ARCH-REVIEW-001 / WP-D  
**Applies to:** NX-ADR-001, NX-ADR-002, NX-ADR-004, NX-ADR-005, NX-IF-001, NX-IF-002, NX-IF-003, ТЗ-NX-001, ТЗ-NX-003, ТЗ-NX-004, ТЗ-NX-005, ТЗ-NX-006, NX-ARCH-001  
**Baseline commit:** `c20d6e1a008b0dda361659c01059ef3e69f96770`  
**Implementation status:** NOT STARTED

## 1. Purpose and scope

This contract defines how NEXUS represents the freshness, integrity, completeness and recovery status of state consumed by Risk, Execution, Strategy and Ledger. It closes the cross-service gap between local recovery mechanisms by defining:

- a versioned, provenance-preserving `StateEvidenceVector` with per-source watermarks and quality;
- explicit freshness evaluation without substituting timestamps or treating missing evidence as healthy;
- source-specific degradation, quarantine and reconciliation propagation;
- a dependency-aware `RecoveryBarrier` that prevents premature authorization after restart, reconnect, gap or restore;
- deterministic rules for invalidating snapshots, approvals and reservations when their evidence becomes stale or changes;
- fault scenarios, conformance requirements and owner decisions.

This is an interface and lifecycle contract. It does not select storage, broker, scheduler, database, clock service, retry values, freshness thresholds, venues or numeric risk limits. It does not authorize live trading.

**Boundary:** NX-ADR-004 remains the public market-data stream state machine. Private account/order/fill stream integrity and venue reconciliation remain under NX-ADR-002 and ТЗ-NX-004/006. NX-IF-004 composes their evidence; it does not replace their protocol-specific recovery rules or claim that one generic sequence algorithm applies to all feeds.

## 2. Normative language and system invariants

The terms MUST, MUST NOT, SHOULD and MAY are normative.

1. Every risk-relevant input MUST carry source identity, scope, provenance, freshness evidence, quality and a version/watermark appropriate to that source.
2. A missing timestamp, watermark, sequence, completeness declaration or quality value MUST remain UNKNOWN; it MUST NOT be synthesized from receive order or treated as zero/healthy.
3. Freshness MUST be evaluated per source and per scope. A single global `healthy` flag or maximum timestamp MUST NOT stand in for a coherent evidence set.
4. Event time, local receive time, processing time and evaluation time MUST remain distinct. Receive time MUST NOT silently replace missing exchange event time.
5. A source can be connected and stale, disconnected with a last-known snapshot, or current but incomplete. Transport, quality, freshness and reconciliation are separate dimensions.
6. A consumer MUST declare the evidence requirements for each operation/command class. An absent or unconfigured requirement policy MUST fail closed for risk-increasing authorization.
7. Any material gap, invalid sequence, stale dependency, unresolved reconciliation discrepancy or unknown exposure MUST invalidate the affected derived state before it is used for new risk authorization.
8. A recovery barrier MUST be scoped. Failure in one instrument/account/venue MUST NOT silently mark unrelated scopes healthy; neither may a healthy sub-scope hide an unhealthy parent scope whose limits apply.
9. Restart, reconnect, snapshot restore or replay MUST NOT restore authorization merely because services are running. The required durable state, source reconciliation and projection watermarks must pass the configured barrier.
10. A state transition that changes a source watermark, quality, scope generation, instrument spec or policy version MUST invalidate dependent snapshots/approvals unless compatibility is explicitly proven.
11. Risk reservations remain conservative while an execution outcome or source state is ambiguous. Local timeout, lease expiry or lost connection is not proof that exposure disappeared.
12. AI, Strategy and clients MUST NOT mark evidence valid, clear quarantine, waive a barrier or mutate authoritative source watermarks.
13. Recovery and operator overrides MUST be durable, attributable, versioned and auditable.
14. No component may claim exactly-once delivery across an exchange boundary. Internal consumers MUST be idempotent and use source-specific deduplication identities.
15. This contract does not define a blanket bypass for cancellation, close or risk-reducing actions. Their authorization and emergency semantics are reserved for WP-E and remain subject to venue/account-mode evidence.

## 3. Domain model

### 3.1 EvidenceScope

An `EvidenceScope` identifies the exact state domain for which evidence is asserted:

- `scope_type`: PORTFOLIO, VENUE_ACCOUNT, SUBACCOUNT, INSTRUMENT, STREAM, ORDER, POSITION, LEDGER_PROJECTION or explicitly configured hierarchy node;
- stable internal scope ID and parent scope IDs;
- venue, account/subaccount, market type, instrument and channel identifiers where applicable;
- account mode / position mode where relevant;
- scope configuration version and applicable policy version.

A source assertion MUST name its scope and the parent scopes whose completeness or limits it affects. Scope inheritance MUST be explicit; an instrument-level healthy feed does not prove account-level reconciliation.

### 3.2 StateEvidenceVector

A `StateEvidenceVector` is an immutable, versioned collection of source evidence evaluated for one scope and one decision point. It is not a single timestamp and is not a mutable shared cache.

Minimum envelope:

- `schema_version`, `vector_id`, `vector_version`;
- `scope_id`, `scope_type`, parent-scope versions;
- `evaluated_at` and monotonic evaluation sequence;
- `consumer`, `operation_class` and declared requirement-policy version;
- source evidence entries, each with source type, source identity and source scope;
- aggregate completeness/quality result plus explicit missing, stale, contradictory and quarantined requirements;
- instrument-spec, risk-policy, projection and adapter/schema versions relevant to the evaluation;
- previous vector reference, transition reason and correlation lineage.

Each source entry MUST include, where applicable:

- source owner/component and venue/channel/endpoint;
- source event time (nullable), local receive time, processing time and evaluation time;
- monotonic local age measurement and clock-quality/uncertainty metadata;
- sequence range, cursor, journal offset, projection watermark, snapshot ID/version or other source-native continuity marker;
- connection generation/session epoch where applicable;
- source quality, transport/recovery state and reconciliation state as separate fields;
- completeness declaration and coverage (including pagination/history window boundaries);
- raw evidence reference and payload digest;
- adapter, schema, normalization and calculation versions;
- instrument specification and policy versions where relevant;
- deduplication/correction lineage and last successful reconciliation reference;
- explicit limitations and reason codes.

Fields not applicable to a source MUST be marked NOT_APPLICABLE with a reason. Missing fields MUST be UNKNOWN, not omitted in a way that implies validity.

### 3.3 Source domains and authority

| Evidence domain | Authoritative owner | Required evidence examples |
|---|---|---|
| Public market data | Market Data / venue adapter under ТЗ-NX-001 and NX-ADR-004 | Stream state, sequence/checksum or documented limitation, event/receive age, snapshot/book version, gap/recovery state |
| Instrument specification | Versioned registry under NX-ADR-005 | Immutable spec version, venue source/provenance, effective time, validation status |
| Private orders and executions | Execution under NX-ADR-002 / ТЗ-NX-004 | Private stream generation/sequence where supported, REST reconciliation cursor, order/fill watermarks, unresolved outcomes |
| Account balances and positions | Venue evidence plus Ledger reconciliation under ТЗ-NX-006 | Snapshot time, pagination coverage, transaction cursor, position/balance comparison, discrepancy state |
| Ledger journal and projections | Ledger under NX-IF-003 / ТЗ-NX-006 | Durable journal watermark, inbox/outbox progress, projection watermark, snapshot/replay integrity |
| Risk reservations and exposure | Risk under NX-IF-002 / ТЗ-NX-005 | Reservation version/fencing token, exposure snapshot version, exclusive bucket coverage, unknown exposure and reconciliation state |
| Risk policy and approvals | Risk under NX-IF-001 / ТЗ-NX-005 | Immutable policy version, halt epoch, approval validity and consumption state |
| Clock/time service | Platform time subsystem | UTC wall-clock quality, monotonic clock continuity, measured offset/uncertainty; never a substitute for source event time |

A consumer may read evidence from multiple owners, but MUST preserve each owner's assertion and provenance. It MUST NOT rewrite source evidence to force a composite vector into a healthy state.

### 3.4 Quality, transport, freshness and reconciliation

These dimensions are orthogonal.

**Transport/recovery state** is source-specific (for public books, use NX-ADR-004 states; for private streams, use the states defined by the relevant Execution adapter contract).

**Quality** uses a normalized outer vocabulary:

- `VALID` — required integrity and completeness checks passed;
- `DEGRADED` — usable only under explicitly declared limitations;
- `STALE` — age exceeds the applicable policy or no fresh evidence arrived;
- `UNSYNCHRONIZED` — continuity/bridge/replay has not been proven;
- `INVALID` — evidence failed integrity or semantic validation;
- `INCOMPLETE` — required coverage is missing;
- `QUARANTINED` — conflicting/unknown evidence is isolated pending resolution;
- `UNKNOWN` — insufficient evidence to classify.

**Reconciliation state** uses the source owner's vocabulary and MUST at minimum distinguish NOT_STARTED, IN_PROGRESS, MATCHED, DISCREPANCY, UNKNOWN and NOT_APPLICABLE. A normalized mapping may be added but MUST preserve the native status.

**Freshness** is a policy evaluation over source-specific age and continuity. It MUST NOT be represented as quality alone. A source can be VALID but no longer fresh enough for a particular consumer.

### 3.5 Freshness policy

Freshness thresholds are configuration, not constants embedded in code or guessed during implementation.

A versioned `FreshnessPolicy` MUST define, by source type, scope, operation class and (where relevant) market/timeframe:

- maximum event age and maximum receive age;
- permitted clock uncertainty and event-time regression handling;
- whether source sequence/cursor continuity is mandatory;
- required snapshot/reconciliation age and completeness;
- accepted quality and recovery states;
- permitted degraded modes and explicit excluded use cases;
- behavior when a threshold is unconfigured or the source does not provide the required marker;
- policy version, effective time, owner/approval and audit reference.

Thresholds MUST reflect venue protocol, market cadence, strategy horizon and operation risk. No numeric default is implied by this contract. An unconfigured threshold for a mandatory risk input MUST block risk-increasing authorization.

Age MUST use a monotonic local clock for elapsed duration, with wall-clock/source timestamps retained for provenance. Clock discontinuity or excessive uncertainty makes time-dependent freshness UNKNOWN/UNSYNCHRONIZED until re-established. Do not compare timestamps from unrelated clock domains as if they were perfectly synchronized.

## 4. Evidence requirements and invalidation

### 4.1 Consumer requirement declaration

Every Strategy, Risk and Execution operation MUST declare a versioned `EvidenceRequirementSet`. It identifies mandatory and optional source domains, scope coverage, acceptable quality/reconciliation states, maximum ages, continuity markers and required versions.

Examples (illustrative, not numeric policy):

- A strategy using order-book imbalance requires the relevant book stream to meet its declared sequence/integrity and age policy; a stale chart candle does not satisfy that dependency.
- A risk evaluation requires a complete-enough exposure snapshot, current reservations/fencing, required account/position reconciliation, valid instrument specification and applicable Ledger projection watermark.
- A market order dispatch requires the evidence set bound to the approval to remain compatible at the final pre-dispatch check.
- A portfolio valuation requires every material currency/position component to be covered or explicitly reported UNKNOWN/PARTIAL; a precise aggregate cannot conceal missing accounts.

The consumer MUST reject an operation when a mandatory requirement is missing, UNKNOWN, stale, invalid, unsynchronized, incomplete or quarantined, unless a narrowly scoped policy explicitly permits a degraded mode. Such a policy cannot waive a hard safety invariant in NX-IF-001/002/003 or the relevant ADR.

### 4.2 Dependency and invalidation graph

Derived state records the exact source vector/version from which it was computed. At minimum, dependencies include:

- Footprint/Delta/CVD/DOM derived values → source trades/book evidence and instrument-spec version;
- Strategy DecisionContext → indicator/data versions, data-quality coverage and strategy artifact version;
- ExposureSnapshot → Execution order/fill watermarks, Ledger journal/projection watermarks, venue reconciliation, reservation fencing, instrument specs and valuation evidence;
- RiskApprovalCapability → canonical command digest, exposure snapshot/reservation versions, policy/spec versions, halt epoch and the exact StateEvidenceVector digest;
- Ledger position/account projections → journal watermark, posting-rule and instrument-spec versions, venue reconciliation evidence;
- execution dispatch eligibility → unexpired, unconsumed approval plus unchanged mandatory evidence/version compatibility at dispatch.

A material upstream change MUST mark dependent state as INVALIDATED or REEVALUATION_REQUIRED before it can authorize a new risk-increasing command. A new vector is published; historical vectors remain immutable.

### 4.3 Approval compatibility

NX-IF-001 remains authoritative for approval identity, digest binding, expiry and one-time consumption. WP-D adds the following evidence binding:

- approval references `state_evidence_vector_id`, `vector_version` and canonical vector digest;
- approval records the exact mandatory source entries/watermarks and requirement-policy version used;
- Execution performs a final compatibility check immediately before dispatch;
- any required source generation, watermark, quality, exposure, reservation, spec, policy or halt-epoch change invalidates the approval unless the relevant contract explicitly defines a safe monotonic advancement rule;
- a newer vector is not automatically compatible merely because its timestamp is later;
- an incompatible approval cannot be refreshed or rebound in place; Risk must evaluate a new request and issue a new capability.

The canonical serialization/digest algorithm and cryptographic envelope remain owner/security decisions under NX-IF-001. This document does not choose them.

## 5. RecoveryCase and quarantine

A `RecoveryCase` is a durable record opened when a source or derived state loses required integrity, freshness, completeness or reconciliation.

Minimum fields:

- `recovery_case_id`, schema version, affected scope(s) and parent scopes;
- trigger source/event, reason codes, severity and detected time;
- last-known-good vector/source watermarks and invalidated versions;
- affected derived projections, approvals and reservations;
- current recovery stage, attempts and bounded retry-policy version;
- evidence references, reconciliation discrepancies and operator actions;
- owner component, assigned service/operator and correlation IDs;
- resolution criteria, proof references, closure actor/time and final vector.

Quarantine is scoped to the smallest scope proven safe, then propagated to parent scopes where portfolio/account limits or unknown shared state require it. If the scope cannot be bounded, escalate to the nearest configured parent and block there. Never quarantine only a child while allowing a parent authorization to ignore the child's unknown exposure.

A RecoveryCase MUST NOT be closed by elapsed time, successful socket reconnect, empty REST response without coverage proof, local cancel acknowledgement or operator assertion without recorded evidence. Closure requires source-specific recovery success, reconciliation and publication of a new compatible evidence vector.

## 6. RecoveryBarrier

### 6.1 Purpose and scope

A `RecoveryBarrier` is a durable, versioned authorization gate for a defined scope and operation class. It proves that all required recovery dependencies have reached their configured acceptance state. It is not a global process-start flag.

Minimum fields:

- `barrier_id`, schema version, scope and parent scope versions;
- operation class and EvidenceRequirementSet/FreshnessPolicy versions;
- barrier generation/epoch and fencing token;
- required source domains and their accepted watermarks/versions;
- recovery cases and reconciliation references;
- stage, result, reason codes and last transition ID;
- created/evaluated times, evaluator identity and audit lineage.

States:

- `CLOSED` — no authorization through this barrier;
- `RESTORING_DURABLE_STATE` — durable stores, checkpoints and journals are being validated;
- `RECONCILING_SOURCES` — venue/source snapshots, streams and histories are being reconciled;
- `REBUILDING_PROJECTIONS` — Ledger, exposure and dependent projections are being replayed/rebuilt;
- `VALIDATING_DEPENDENCIES` — policy/spec versions, watermarks, freshness and completeness are checked;
- `READY` — declared requirements pass for the named scope and operation class;
- `BLOCKED` — a required stage failed, is incomplete or exceeded its bounded retry/timeout policy;
- `REVIEW_REQUIRED` — automated evidence is insufficient or a material discrepancy requires authorized human resolution.

A new recovery event, source regression, generation change, material discrepancy or invalidation MUST advance the barrier generation and close any previously READY barrier for the affected scope before further risk-increasing authorization.

### 6.2 Recovery stages and ordering

The following is a dependency order, not a requirement that unrelated services restart serially. Implementations MAY execute independent branches concurrently but MUST honor dependencies and publish a barrier only after all required branches pass.

1. **Restore durable state:** validate store availability, journal/outbox/inbox durability, checkpoints, idempotency records, reservation state, policy/spec registries, audit chain and backup/snapshot integrity.
2. **Establish source sessions:** connect and subscribe to required public and private streams using their protocol-specific rules; increment connection/session generations; keep data untrusted while synchronizing.
3. **Acquire authoritative source evidence:** obtain required market-data snapshots/bridges, private account/order/position snapshots, fill/transaction history and cursors with explicit coverage and retention boundaries.
4. **Reconcile Execution:** resolve known commands/orders, ambiguous dispatch outcomes, cumulative fills, cancels and external/manual activity. Unknown outcomes remain reserved/quarantined.
5. **Recover Ledger:** drain durable Execution inbox/outbox handoff idempotently; verify journal postings and balances; rebuild projections from a validated snapshot plus journal watermark; reconcile account/position/fee/funding evidence.
6. **Rebuild Risk exposure:** reconstruct exclusive exposure buckets and reservations from source-owned facts; validate fencing/version monotonicity; include external and unknown exposure conservatively; do not infer missing exposure as zero.
7. **Validate dependencies:** confirm current instrument specs, policy versions, valuation inputs, source freshness/quality, projection watermarks, reconciliation completeness and approval invalidation.
8. **Publish barrier:** atomically publish the new evidence vector and READY barrier for the exact scope/operation class. Only then may the relevant risk-increasing authorization path resume.

If a required stage is incomplete, contradictory or outside retention, the barrier remains BLOCKED or REVIEW_REQUIRED. No stage may be skipped because a service reports itself healthy.

### 6.3 Operation-class gating

The barrier is evaluated against a versioned requirement set, not a single universal checklist.

- Risk-increasing CREATE/new exposure: requires all configured market, instrument, account, Execution, Ledger, Risk exposure/reservation and policy evidence applicable to the strategy/command.
- Amend that can increase exposure or worsen price/risk: treated as risk-increasing and requires fresh evaluation.
- Strategy evaluation without dispatch: may use an explicitly declared degraded/read-only evidence policy, but its output remains a proposal and cannot authorize execution.
- Read-only chart/reporting: may display last-known data only with visible age/quality/coverage indicators; it does not change source truth.
- Cancel, reduce-only, close, cancel-all and emergency actions: WP-E must define the command-specific authorization and evidence matrix. WP-D does not silently classify these as safe or provide a blanket bypass. Existing NX-IF/ADR controls remain in force pending WP-E closure.

A READY barrier for one operation class MUST NOT be reused for another class with stronger requirements.

## 7. Interaction with existing contracts

| Contract | WP-D composition rule |
|---|---|
| NX-ADR-001 | Preserve event/receive/process timestamps, sequence scope, provenance and schema evolution |
| NX-ADR-002 | Private execution recovery and reconciliation remain authoritative; ambiguous outcomes remain unresolved exposure |
| NX-ADR-004 | Public market-data state machine remains authoritative; WP-D consumes its states and quality, does not replace it |
| NX-ADR-005 | Instrument-spec version and exact arithmetic are mandatory evidence dependencies |
| NX-IF-001 | Approval binds exact command and additionally references the evidence vector/policy version; no in-place rebinding |
| NX-IF-002 | ExposureSnapshot quality, source watermarks, reservation fencing and exclusive buckets feed the vector and recovery barrier |
| NX-IF-003 | Execution outbox, Ledger inbox, journal commit, projection and reconciliation watermarks remain distinct milestones |
| ТЗ-NX-001 | Publishes public data health, source watermarks, stream generation and recovery evidence |
| ТЗ-NX-004 | Publishes private order/fill/session/reconciliation evidence and resolves unknown dispatch outcomes |
| ТЗ-NX-005 | Owns requirement evaluation, exposure freshness, barrier enforcement and fail-closed authorization |
| ТЗ-NX-006 | Publishes journal/projection/reconciliation evidence and never reports a stale projection as healthy |

### 7.1 WP-B exposure handoff

Risk MUST NOT transfer `FILL_PENDING_LEDGER` to `CONFIRMED_POSITION` merely because Execution delivered an event. The transfer remains gated by NX-IF-003's durable Ledger posting, matching journal identity, applied position projection watermark and required venue reconciliation. WP-D adds that the evidence vector must identify all relevant watermarks and their quality at the same evaluation point. A lagging or regressing watermark leaves the amount in the conservative prior bucket or quarantined state.

### 7.2 Cross-source ordering

Source event time alone does not establish cross-service causal order. Use stable IDs, source-specific sequence/cursor, durable commit offsets and explicit predecessor references. If two sources disagree or their ordering cannot be established, retain both facts, open a RecoveryCase and apply conservative exposure; do not choose whichever timestamp is later.

## 8. Observability and audit

Record, by scope and source:

- vector/barrier/recovery-case IDs and versions;
- current and previous source watermarks/generations;
- event, receive, process and evaluation times plus clock uncertainty;
- age distribution and policy threshold result (without exposing secrets);
- quality, transport, reconciliation and completeness dimensions;
- missing/unknown/quarantined requirements and reason codes;
- recovery stage duration, retry count, exhaustion and operator action;
- approval invalidations and reservation state changes caused by evidence changes;
- projection lag, journal/inbox/outbox watermarks and reconciliation discrepancy age;
- barrier transitions, evaluator identity and evidence references.

All state changes and manual decisions are append-only audit events. Logs MUST redact credentials, signatures and sensitive account payloads. Metrics MUST distinguish source lag from internal processing/projection lag.

## 9. Failure and recovery scenarios

At minimum, the conformance suite must cover:

1. process restart with a valid checkpoint but no current venue reconciliation;
2. restart with a missing/corrupt journal or checkpoint hash;
3. public book sequence gap while a strategy is evaluating;
4. sequence-less incremental feed incorrectly presented as LIVE_VALID;
5. private stream disconnect after dispatch but before acknowledgement;
6. acknowledgement received while fill/order state remains unresolved;
7. duplicate, reordered or corrected private fill events;
8. REST pagination overlap, cursor regression and history retention boundary;
9. empty history response with incomplete query coverage;
10. Ledger inbox committed but projection not yet advanced;
11. journal posted but Risk exposure projection remains behind;
12. reservation store restored from an older fencing generation;
13. instrument specification changes between approval and dispatch;
14. risk policy changes between evaluation and dispatch;
15. clock step/backward wall-clock jump or excessive uncertainty;
16. fresh receive time with stale exchange event time;
17. event-time missing while receive time is present;
18. parent portfolio scope has an unknown child account;
19. external/manual order discovered during recovery;
20. venue reports a position inconsistent with Ledger fills;
21. one venue recovers while another venue required by portfolio policy remains blocked;
22. recovery retries exhaust or source remains outside retention;
23. old service instance attempts to publish a READY barrier using a stale generation;
24. previously READY barrier invalidated while an approval is pending dispatch;
25. operator attempts to close a RecoveryCase without source evidence;
26. degraded read-only chart path is visible but risk-increasing dispatch remains blocked.

## 10. Acceptance criteria

1. StateEvidenceVector is versioned, immutable and scoped; every source entry preserves provenance and applicable watermarks.
2. Missing event time, cursor, sequence, completeness or quality remains UNKNOWN and is never silently synthesized.
3. Event, receive, processing and evaluation times remain separate; freshness uses monotonic elapsed time and explicit clock quality.
4. Transport state, quality, freshness and reconciliation are represented independently.
5. FreshnessPolicy is versioned and scoped by source/operation; an unconfigured mandatory threshold blocks risk-increasing authorization.
6. Consumer EvidenceRequirementSet identifies mandatory evidence and accepted degraded modes.
7. Every derived snapshot/approval records exact upstream versions and invalidates on incompatible changes.
8. Final pre-dispatch validation rejects an approval whose mandatory evidence vector or versions are incompatible.
9. RecoveryCase records last-known-good state, invalidations, evidence and resolution criteria.
10. Quarantine propagates to parent scopes when shared exposure/limits cannot be bounded.
11. RecoveryBarrier is durable, scoped and generation/fencing protected.
12. Process restart cannot produce READY before required durable-state, source, Execution, Ledger and Risk recovery stages pass.
13. Execution OUTCOME_UNKNOWN retains conservative reservation until authoritative reconciliation.
14. Ledger posting, projection and venue reconciliation watermarks are distinct and independently checked.
15. Risk exposure cannot double-count or omit the WP-B fill-pending handoff during recovery.
16. External orders/positions and unknown financial events remain visible and conservatively represented.
17. Spec/policy/halt-generation changes invalidate incompatible pending approvals.
18. A stale service cannot publish or consume a READY barrier from an older generation.
19. Recovery retry exhaustion, retention limits and operator overrides are auditable and fail closed.
20. A healthy child scope cannot mask an unhealthy parent scope required by policy.
21. A degraded read-only path cannot enable risk-increasing execution.
22. WP-E command classes remain explicitly unresolved; no generic emergency/reduce bypass is introduced.
23. Deterministic fixtures cover at least one sequenced public book, one sequence-limited public feed and private account/order reconciliation for each initially selected venue.
24. Fault-injection tests cover crash points between every durable handoff and projection watermark.
25. No implementation, CI, runtime or production-readiness pass is claimed until corresponding evidence is recorded.

## 11. Open owner decisions

1. Initial venue/account-mode shortlist and required source channels for the first release.
2. Freshness thresholds by channel, market cadence, strategy horizon and operation class.
3. Whether validated sequence-less full-book sources may support selected strategies or remain display-only.
4. Required completeness/retention policy for private order, fill, balance and transaction history.
5. Which account/portfolio scopes must reconcile before first release authorization.
6. Clock source, acceptable uncertainty and behavior during clock-service degradation.
7. Recovery retry budgets, timeout objectives and HALTED versus REVIEW_REQUIRED thresholds.
8. Durable store and transaction boundaries for vectors, barriers, reservations and recovery cases.
9. Recovery objectives (RTO/RPO), raw evidence retention and backup/restore policy.
10. Operator roles and dual-control requirements for resolving quarantine and resuming a scope.
11. Which command classes are included in WP-E and their minimum evidence requirements.

Until these are approved and encoded in versioned policy, no numeric freshness threshold, retry count, recovery objective or live authorization behavior is assumed.

## 12. Verification status

This document is a proposed design contract only. No StateEvidenceVector schema, freshness evaluator, RecoveryCase store, barrier coordinator, adapter integration, database transaction, replay engine, reconciliation worker, fault-injection test or runtime behavior has been implemented or verified. No venue account, live credential or order was used. No risk limit or live-trading control was changed.

**Prototype Readiness remains BLOCKED.**


## WP-E — Emergency operation and resume gate

[NX-IF-005 — Emergency Operations, Halt & Risk-Reduction Authorization Contract ](NX-IF-005-emergency-operations-halt-risk-reduction-contract.md) defines the operation-class matrix and privileged resume protocol that consume this contract's evidence. Emergency commands require a current StateEvidenceVector and an operation-specific RecoveryBarrier; a READY barrier for CREATE cannot be reused for CANCEL, REDUCE_ONLY, CLOSE, CANCEL_ALL or FLATTEN without their own requirement set. Resume requires reconciled source state, valid Ledger/Risk projections, current policy/spec versions, all applicable parent scopes ACTIVE and a new acknowledged halt epoch. WP-D does not grant a blanket emergency bypass.
