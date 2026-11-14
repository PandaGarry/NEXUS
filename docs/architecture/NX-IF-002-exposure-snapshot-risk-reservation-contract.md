# NX-IF-002 — Exposure Snapshot & Risk Reservation Contract

**Date:** 2026-11-14  
**Status:** PROPOSED — normative interface draft; not accepted  
**Work package:** NX-ARCH-REVIEW-001 / WP-B  
**Applies to:** NX-IF-001, NX-ADR-002, NX-ADR-005, ТЗ-NX-003, ТЗ-NX-004, ТЗ-NX-005, ТЗ-NX-006, NX-ARCH-001  
**Baseline commit:** `86b1d873dd948139bfaaa91b5cee372b364c28ec`  
**Implementation status:** NOT STARTED

## 1. Purpose and scope

This contract defines how NEXUS represents economic exposure while commands move through Strategy, Risk, Execution, venue state and Ledger. It establishes:

- a single, versioned exposure view with mutually exclusive ownership buckets;
- stable identity and lineage for each exposure item;
- authority boundaries between Execution, Ledger and Risk;
- durable reservations for concurrent risk-increasing commands;
- atomic capacity checks, fencing and replay-safe state transitions;
- conservative treatment of partial fills, ambiguous outcomes, external activity and stale state;
- recovery and reconciliation requirements;
- acceptance criteria and negative/concurrency/fault test scenarios.

This document is an interface contract, not a choice of database, message broker, lock service, valuation formula, numeric risk limit or venue adapter. It does not authorize live trading.

## 2. Normative language and invariants

The terms MUST, MUST NOT, SHOULD and MAY are normative.

1. Every economically relevant position, order remainder, pending command or unresolved exposure MUST be represented in exactly one authoritative exposure bucket for a given snapshot scope and version.
2. A lifecycle transition MUST move or transform exposure atomically in the authoritative Risk projection. It MUST NOT create a gap in which the old bucket is removed before the new bucket is committed.
3. The same venue order/fill observed through multiple sources MUST be correlated to one exposure lineage, not added as independent exposure.
4. Missing, stale, contradictory or unbounded exposure MUST NOT be treated as zero.
5. Risk-increasing authorization MUST fail closed when the required exposure scope cannot be bounded or its snapshot is not current enough under the approved policy.
6. A reservation MUST be durable before the corresponding RiskApprovalCapability is issued.
7. Concurrent reservation requests MUST serialize against the same authoritative risk scope and capacity version. A process-local mutex or best-effort distributed lock alone is insufficient.
8. An approval MUST bind to the exact reservation, command digest, account/scope, instrument-spec version, policy version, exposure version and halt epoch defined by NX-IF-001.
9. A reservation MUST NOT be released solely because a local timeout, cancel request, cancel acknowledgement, client disconnect or lease expiry occurred.
10. A dispatch with ambiguous outcome MUST retain conservative exposure until authoritative reconciliation resolves it.
11. A fill MUST transfer exposure from order/reservation state to position/ledger-pending state exactly once, including partial fills and duplicate/corrected events.
12. No risk policy may invent missing instrument multipliers, contract units, margin values, valuation marks or collateral eligibility.
13. AI, Strategy and clients MUST NOT create, mutate, release or override reservations directly.
14. All amounts use the exact representations and immutable Instrument Specification versions required by NX-ADR-005. Binary floating point MUST NOT be canonical.
15. This contract does not claim exactly-once delivery across a venue boundary; it requires idempotent internal state transitions and reconciliation.

## 3. Domain model and identity

### 3.1 Risk scope

A `RiskScope` identifies the exact capacity pool against which concurrent requests compete. It contains:

- `risk_scope_id` — stable internal identifier;
- `scope_type` — ACCOUNT, SUBACCOUNT, VENUE_ACCOUNT, PORTFOLIO or an explicitly configured hierarchy node;
- `account_id` and optional `subaccount_id`;
- `venue_id` and market/account mode where applicable;
- `parent_scope_id` and policy-defined aggregation membership;
- `scope_config_version` and `policy_version`.

A reservation request MUST name every applicable scope whose hard limits can be affected. A single order may consume capacity in multiple scopes (for example, instrument, account and portfolio). All required reservations MUST succeed atomically as one logical authorization, or none may be issued. The implementation may use a single transactional store or a rigorously specified multi-scope coordination protocol; it MUST NOT partially reserve one scope and silently omit another.

The initial hierarchy and whether portfolio-wide cross-venue aggregation is enabled are owner decisions. Until configured, an unconfigured parent scope MUST NOT be interpreted as unlimited capacity.

### 3.2 Exposure item

An `ExposureItem` is the canonical identity of one economic obligation or holding. Minimum fields:

- `exposure_item_id` — immutable NEXUS identifier;
- `root_lineage_id` — stable lineage across command/order/fill/position transitions;
- `source_type` and `source_identity` — NEXUS command, venue order, execution/fill, ledger position, external order/position or reconciliation case;
- `account_id`, `venue_id`, market type and canonical instrument identity;
- `instrument_spec_version`;
- `owner_bucket` and `bucket_version`;
- exact remaining quantity/notional/margin/collateral dimensions required by policy, with explicit units/currency;
- side, position side/index, order semantics and reduce-only/close flags where relevant;
- valuation evidence and quality, when valuation is required;
- source timestamps, receive/processing timestamps and source watermarks;
- correlation IDs, predecessor/successor item IDs and raw evidence references;
- `status`, `reason_codes` and `last_transition_id`.

The identity of an exposure item MUST NOT be a display symbol, price/size/timestamp tuple, or mutable venue field alone. Venue-native IDs are namespaced by venue, account, market type and documented uniqueness scope. If no stable native identity exists, a documented composite identity and confidence/limitations are required; ambiguous matches enter quarantine.

### 3.3 ExposureSnapshot

An immutable `ExposureSnapshot` is a coherent risk view for a specific scope and evaluation point. It includes:

- schema version, snapshot ID, risk scope and parent-scope versions;
- monotonic `snapshot_version` and `fencing_token`;
- creation/as-of time, source event watermarks and projection offsets;
- account, venue, instrument-spec and policy versions;
- health/quality state and explicit completeness coverage;
- per-bucket totals and item references;
- unknowns, discrepancies, quarantined identities and their conservative bounds;
- valuation inputs, currency/unit dimensions and calculation version;
- previous snapshot reference and transition/event range.

A snapshot MUST distinguish at least COMPLETE, DEGRADED, STALE, INCOMPLETE, UNSYNCHRONIZED and INVALID. A numerically populated snapshot is not automatically complete. The risk policy determines which quality states are acceptable for a particular command class. Missing components remain UNKNOWN and must be surfaced, not silently omitted.

A snapshot is immutable once published. Corrections create a new version with lineage to the prior snapshot and the correction evidence. Versions MUST be monotonic within a risk scope; stale writers MUST be fenced out.

## 4. Exposure bucket ownership

### 4.1 Exclusive bucket set

For each exposure item, exactly one of the following buckets is authoritative at a given snapshot version:

| Bucket | Meaning | Primary source authority |
|---|---|---|
| `CONFIRMED_POSITION` | Venue-confirmed position represented in the reconciled Ledger position projection | Ledger, reconciled against venue account/position evidence |
| `WORKING_ORDER_REMAINDER` | Accepted/open order's unfilled remaining quantity | Execution order state, reconciled against venue open-order evidence |
| `PRE_DISPATCH_RESERVATION` | Risk capacity held for an approved command not yet known to have reached the venue | Risk reservation store |
| `DISPATCH_OUTCOME_UNKNOWN` | Command may have reached the venue; acceptance/rejection/fill is unresolved | Execution command state + Risk reservation |
| `FILL_PENDING_LEDGER` | Execution evidence confirms a fill, but the corresponding Ledger position/journal projection has not yet committed/reconciled | Execution fill journal; Ledger posting watermark |
| `EXTERNAL_ORDER_REMAINDER` | Venue order not attributable to a known NEXUS command | Venue reconciliation + Execution quarantine |
| `EXTERNAL_POSITION` | Venue position not attributable/reconciled to a known NEXUS fill lineage | Venue account/position evidence + Ledger quarantine |
| `UNKNOWN_EXPOSURE` | A discrepancy or incomplete source implies exposure that cannot yet be classified or bounded precisely | Reconciliation case with conservative Risk treatment |

The bucket is a projection ownership state, not a claim that every source has equal authority. Raw venue evidence, normalized Execution facts and posted Ledger facts remain separately retained.

### 4.2 Authority and responsibility matrix

| Component | Owns | MUST NOT claim |
|---|---|---|
| Strategy / AI | TradeIntent and rationale | Position, order, reservation or authoritative exposure |
| Execution | Canonical command dispatch state, venue order lifecycle, normalized fill evidence and native IDs | Posted Ledger balance/position truth; Risk capacity |
| Ledger | Immutable financial journal, posted balances, position and accounting projections | Whether an unposted command is safe; whether a reservation is valid |
| Risk Engine | Risk policy, reservation state, exposure aggregation/snapshot, authorization and halt decision | Venue execution truth without Execution/reconciliation evidence |
| Venue adapter / reconciliation | Raw/private venue order, fill, balance and position evidence with source watermarks | NEXUS command intent or internal approval validity |

The Risk Engine is the sole publisher of the authoritative `ExposureSnapshot` used for authorization. It consumes source-owned facts and preserves their provenance. It MUST NOT rewrite Execution or Ledger source records to make its projection appear consistent.

### 4.3 Ownership transitions and no-gap/no-double-count rule

A transition is a single logical Risk projection transaction that:

1. validates the incoming event identity, source authority, expected prior bucket/version and scope fencing token;
2. records the event in a durable inbox/journal with deduplication identity;
3. closes or reduces the prior bucket amount;
4. creates or increases the successor bucket amount;
5. updates affected scope totals and monotonic snapshot/projection version;
6. records transition evidence and commits before publishing the new snapshot.

If the source event arrives before the destination projection is ready, the item remains in the prior conservative bucket or moves to `FILL_PENDING_LEDGER`; it MUST NOT disappear. Replaying the same event MUST be idempotent. A correction/bust is a new linked event and produces a compensating transition; it does not mutate historical evidence.

### 4.4 Canonical lifecycle mapping

| Event / condition | From | To | Release / transfer rule |
|---|---|---|---|
| Risk request accepted and capacity reserved | none | PRE_DISPATCH_RESERVATION | Reserve worst-case bounded exposure before approval |
| Dispatcher commits the durable pre-egress attempt marker before any network side effect | PRE_DISPATCH_RESERVATION | DISPATCH_OUTCOME_UNKNOWN | Move the full conservative reservation before the send boundary; the marker is not proof that bytes were sent, and exposure remains held until authoritative venue outcome/reconciliation |
| Venue confirms order is working | DISPATCH_OUTCOME_UNKNOWN | WORKING_ORDER_REMAINDER | Transfer to remaining open-order exposure; do not count both |
| Venue definitively rejects before any fill | reservation / unknown | released | Release only with authoritative rejection and no-fill evidence |
| Fill confirmed, Ledger not yet posted | working order / unknown | FILL_PENDING_LEDGER for filled portion; remainder stays WORKING_ORDER_REMAINDER | Atomically split filled and remaining quantities |
| Fill posted and reconciled in Ledger | FILL_PENDING_LEDGER | CONFIRMED_POSITION | Transfer only for the matching fill lineage and posted watermark |
| Venue confirms cancel and final cumulative fills | WORKING_ORDER_REMAINDER | released for unfilled remainder; filled portion follows fill path | Cancel acknowledgement alone is insufficient without final order/fill evidence |
| Cancel requested, pending or response lost | working order | unchanged or DISPATCH_OUTCOME_UNKNOWN for unresolved cancel state | Retain exposure; reconcile order and fills |
| NEXUS restart with uncertain dispatch | reservation / unknown | DISPATCH_OUTCOME_UNKNOWN | Restore reservation and reconcile before new risk-increasing authorization |
| Unattributed venue order/position found | none | EXTERNAL_ORDER_REMAINDER / EXTERNAL_POSITION | Quarantine; include conservatively until resolved |
| Unexplained discrepancy or incomplete account state | affected item(s) | UNKNOWN_EXPOSURE or scope quarantine | Block risk-increasing actions when conservative bound is not sufficient |

A command may create several exposure items (for example, a working order plus fee/margin reserve) but each economic component has its own identity and must not be duplicated across buckets. The same economic amount must not be represented simultaneously as both an active reservation and a working-order remainder.

## 5. RiskReservation contract

### 5.1 Minimum fields

A durable `RiskReservation` contains:

- `reservation_id`, schema version and immutable `reservation_request_id`;
- `risk_scope_id(s)` and scope configuration versions;
- canonical command ID and exact command digest from NX-IF-001;
- account, venue, market type, instrument ID and immutable spec version;
- policy version and exposure snapshot ID/version;
- exact reserved dimensions (quantity, notional, margin, fee/cost buffer, collateral impact or other policy-defined dimensions), each with units/currency;
- conservative valuation assumptions and their evidence/version;
- lifecycle state, state version and fencing token;
- created/updated/expiry timestamps and expiry policy;
- actor/service, reason codes, correlation lineage and audit evidence;
- consumed amount, remaining amount and linked fill/order/exposure item IDs;
- release evidence and reconciliation references, if terminal.

A reservation MUST be scoped to one immutable command digest. Repricing, quantity change, side change, instrument/spec change, account change, position-mode change or any other execution-affecting amendment requires a new command and a new evaluation/reservation. It cannot mutate the old reservation in place.

### 5.2 Lifecycle

Canonical states:

- `REQUESTED` — request received; no capacity held yet.
- `RESERVED` — capacity transaction committed; eligible for an approval capability.
- `PARTIALLY_CONSUMED` — one or more fills have transferred part of the reserved exposure; remaining order exposure is still reserved/working.
- `CONSUMED` — all reserved amount has transferred to authoritative fill/position exposure or the reservation has otherwise been fully accounted for.
- `RELEASE_PENDING` — terminal evidence has been observed but release transaction/reconciliation is not complete.
- `RELEASED` — remaining amount released with recorded authoritative evidence.
- `EXPIRED` — reservation expired before dispatch, with durable proof the command was never dispatched and cannot still be dispatched.
- `INVALIDATED` — approval/policy/spec/snapshot compatibility invalidated; remaining capacity stays held until safe release is proven.
- `RECONCILIATION_REQUIRED` — command/order/fill outcome is ambiguous or inconsistent; conservative capacity remains held.

Allowed transitions are explicit and version-checked. No terminal state may be reopened by an old event. A late authoritative fill after a prior local expiry/release is a critical reconciliation incident: restore the exposure, invalidate affected approvals and halt the relevant scope pending review. The system must preserve the original erroneous transition and append compensating evidence.

### 5.3 Reservation sizing

The Risk Engine computes a conservative reservation from the canonical command and current instrument/account state. The calculation is policy- and instrument-specific and may include:

- worst-case fill quantity and order remainder;
- price bounds, trigger behavior and market-order book-walk assumptions;
- fee and funding/carry buffers where applicable;
- slippage/adverse movement buffers;
- initial/maintenance margin and leverage tier effects;
- collateral eligibility, haircuts, FX and settlement currency;
- other simultaneous pending commands and existing working orders.

This contract intentionally does not prescribe numeric limits or one universal formula. The policy MUST define the valuation model, conservative bound, rounding direction, source freshness and uncertainty handling for each supported instrument/account mode. If a conservative bound cannot be computed, the request is rejected or quarantined; UNKNOWN is not a zero reserve.

A reduce-only/close request is not automatically assigned zero exposure. The system must validate current position, position mode, venue reduce-only/close semantics, remaining closeable quantity, existing close orders and concurrent fills. It must prevent accidental position flip. If the venue/account semantics or position state are uncertain, the action is not treated as safely risk-reducing.

## 6. Atomic capacity reservation and concurrency

### 6.1 Required transaction

For each affected risk scope, the logical operation MUST:

1. read a consistent current exposure projection and its version/fencing token;
2. validate snapshot quality, policy/spec versions and all applicable hard limits;
3. calculate conservative incremental reservation requirements;
4. verify capacity including all existing positions, working orders, pending/unknown commands, external exposure and reservations;
5. write the reservation(s), updated scope capacity/version and idempotency record atomically;
6. commit before issuing the RiskApprovalCapability.

The capacity check and reservation write MUST be one serializable/linearizable logical operation. Two simultaneous requests cannot both consume the same remaining capacity based on the same stale snapshot.

### 6.2 Permitted implementation patterns

A future implementation may use:

- serializable database transactions with explicit scope-row/version locking;
- compare-and-swap on a monotonic scope version combined with atomic reservation writes and bounded retry;
- a consensus/transactional coordination service whose failure and fencing semantics are formally specified.

A Redis-style lease or process-local mutex MAY be an optimization, but MUST NOT be the sole correctness mechanism. Lease expiry without fencing can allow an old holder to write after a new holder has acquired the lock. Every write must validate a monotonic fencing token or equivalent transaction version at the authoritative store.

For multiple scopes, either one atomic transaction covers all affected scopes or a formally specified coordinator provides all-or-nothing commit, durable recovery and prevention of partially authorized commands. Sagas that temporarily reserve only some scopes MUST NOT issue an approval or permit dispatch until every required scope is committed.

### 6.3 Idempotency and replay

- Repeated identical reservation request IDs return the original committed result; they do not create additional capacity consumption.
- Reuse of a request ID with a different command digest or scope is rejected as an idempotency conflict.
- A crash after reservation commit but before approval response is recovered by reading the durable request/result; it MUST NOT reserve again.
- A crash after approval issuance but before dispatch leaves the reservation active until dispatch state is proven or expiry is safely established.
- A stale writer, duplicate event or lower fencing token cannot overwrite a newer reservation/snapshot state.
- Reservation and approval IDs are never reused.

## 7. Event handling and edge cases

### 7.1 Concurrent commands

All commands that can affect a shared limit compete against the same scope version. This includes commands from different strategies, AI sessions, desktop/web clients, manual operator actions routed through NEXUS and different instruments when a portfolio/account limit is shared.

Per-instrument locks alone are insufficient for account/portfolio limits. A risk scope hierarchy must be explicit and every applicable parent scope included in the atomic reservation operation.

### 7.2 Partial fills and fill-in-transit

On each authoritative fill:

- deduplicate using venue execution identity and its documented namespace;
- validate the linked order/command lineage and instrument spec;
- reduce the order remainder/reservation by the exact filled amount;
- create a `FILL_PENDING_LEDGER` item for the confirmed fill until Ledger posting is visible at the required watermark;
- move that fill lineage to `CONFIRMED_POSITION` only after Ledger's idempotent posting/projection is committed and reconciled;
- keep unfilled remainder in `WORKING_ORDER_REMAINDER`;
- update all affected scope totals atomically.

A duplicate fill cannot consume the reservation twice. A correction/bust must reference the original fill and use a compensating transition. If fill identity or quantity is ambiguous, quarantine and preserve a conservative bound.

### 7.3 Cancel, amend, reject and expiry

A cancel request or cancel acknowledgement is not proof that remaining quantity cannot fill. Release only after authoritative terminal order state and overlapping fill reconciliation establish final cumulative executed quantity and unfilled remainder.

An amend is a new command. Capacity for the amended order must be reserved before the amendment is dispatched; the old reservation/order exposure remains until the venue confirms the amendment outcome. If amendment outcome is unknown, reserve the conservative maximum of old and proposed exposure without double-counting their shared lineage.

A rejection releases only the unfilled reservation after authoritative rejection and proof no fill was accepted. An expiry is safe only before dispatch or after authoritative venue expiry plus final fill reconciliation. Local wall-clock expiry never proves venue non-acceptance.

### 7.4 OUTCOME_UNKNOWN and disconnection

For a request that may have reached the venue, the reservation moves to or remains in `DISPATCH_OUTCOME_UNKNOWN` / `RECONCILIATION_REQUIRED`. The system must query venue order state, private order/fill streams and relevant account/position snapshots using documented overlap windows and watermarks. Until resolved:

- keep the full conservative remaining exposure reserved;
- block duplicate create dispatch;
- block risk-increasing commands in any scope whose limits cannot be bounded;
- do not infer rejection from absence in one eventually consistent endpoint;
- do not release on a stream disconnect, timeout or missing acknowledgement.

### 7.5 External/manual orders and positions

External activity is not silently attributed to a NEXUS strategy. Each external order/position receives a stable quarantine identity and contributes to exposure. If it may correspond to a NEXUS command, correlate by documented native IDs and evidence; do not count both the external item and the NEXUS pending item once equivalence is established. If equivalence is uncertain, the affected scope is DEGRADED/UNKNOWN and must be blocked unless a conservative upper bound can safely cover all plausible states.

### 7.6 Crash and restart

Risk recovery MUST restore, in order:

1. durable reservation journal and idempotency records;
2. latest committed scope versions/fencing tokens;
3. Execution command/outbox/order/fill state and private stream watermarks;
4. Ledger journal and position/balance projections with posting watermarks;
5. venue open orders, recent fills, balances and positions through reconciliation;
6. exclusive bucket assignments and exposure projections;
7. policy/spec compatibility and current halt epoch.

Only after all required stages are complete may the relevant scope become eligible for new risk-increasing authorization. Any incomplete or contradictory stage remains quarantined. A restarted process must not initialize reservations to empty or reconstruct them only from currently visible open orders.

## 8. Snapshot freshness, policy and invalidation

An approval/reservation binds to immutable versions of:

- canonical command digest;
- instrument specification;
- risk policy and scope configuration;
- exposure snapshot and reservation state;
- account/position mode;
- halt epoch;
- source freshness/reconciliation watermarks required by policy.

A material change to any bound version invalidates the approval for dispatch. The reservation does not automatically vanish: it remains held or enters `INVALIDATED` / `RECONCILIATION_REQUIRED` until a safe transition is committed. A fresh evaluation may atomically replace or resize it only after proving that the old command cannot dispatch and that no venue-side exposure was created.

Snapshot age thresholds, allowed source lag and policy behavior are owner-configurable and venue/account-mode-specific. No universal TTL is assumed here.

## 9. Observability and audit

For every request, decision, reservation, consumption, release, transition and reconciliation action, record:

- actor/service identity and authorization context;
- request, command, approval, reservation, exposure-item and scope IDs;
- prior/new state and versions/fencing token;
- exact amount/dimension/currency and calculation/policy/spec versions;
- source evidence, timestamps, watermarks and payload hashes;
- idempotency/deduplication result;
- reason codes, failure/retry classification and reconciliation case;
- correlation lineage through venue order, fills and Ledger postings.

Required metrics include reservation age by state, reserved vs consumed capacity, scope utilization, rejected concurrency conflicts, stale-writer/fencing rejections, unknown exposure, unresolved external activity, fill-to-ledger lag, reconciliation drift, expired-before-dispatch reservations, and scopes halted by incomplete exposure.

Logs and audit records MUST NOT contain API secrets, signatures or raw credential material.

## 10. Failure behavior

| Failure | Required behavior |
|---|---|
| Risk store unavailable | No new risk-increasing approval; existing reservations remain durable |
| Snapshot stale/incomplete | Reject or quarantine according to policy; never substitute zero |
| Concurrent reservation conflict | One transaction wins; loser rereads and reevaluates |
| Fencing/version mismatch | Reject stale write; reload authoritative state |
| Crash after reservation commit | Recover same reservation by idempotency key |
| Crash after dispatch | Treat unresolved command as unknown; retain reserve and reconcile |
| Duplicate fill | Deduplicate; no second consumption or position increment |
| Fill before order acknowledgement | Record fill lineage; do not wait for REST ack to recognize authoritative execution |
| Cancel/fill race | Reconcile final cumulative fills; retain exposure until resolved |
| Ledger posting delayed | Keep fill in FILL_PENDING_LEDGER |
| External order/position | Quarantine and include conservatively |
| Instrument/policy version changes | Invalidate approval; do not silently reinterpret reservation |
| Unknown contract/valuation/collateral rule | Block affected risk-increasing scope |

## 11. Conformance and acceptance criteria

The design is ready for implementation only when the following are testable against an agreed schema and persistence model:

1. Two simultaneous requests competing for the same remaining capacity cannot both commit beyond the limit.
2. Requests affecting overlapping parent/child scopes commit all required reservations atomically or none.
3. A stale snapshot/version cannot authorize a reservation after a newer exposure event commits.
4. A stale fencing token cannot write after lease expiry or ownership transfer.
5. Replaying an identical reservation request returns the same result without additional consumption.
6. Reusing a request ID with a different command digest is rejected.
7. Crash after reservation commit but before response recovers the original reservation.
8. Crash after dispatch with lost response retains full conservative exposure and blocks blind resend.
9. Working-order acceptance transfers reservation to order remainder without a gap or double count.
10. Partial fill splits filled and remaining quantities exactly; duplicate fill consumes only once.
11. Fill remains in FILL_PENDING_LEDGER until the matching Ledger posting watermark is committed.
12. Cancel request/ack without final order/fill evidence does not release remaining exposure.
13. Rejection/expiry releases only after authoritative evidence and proof no fill can still occur.
14. External/manual orders and positions are discovered, quarantined and included in risk.
15. A late fill after a locally expired/released reservation restores exposure and triggers scope halt/review.
16. Unknown instrument multiplier, stale mark, unknown collateral eligibility or missing account mode blocks unsafe capacity calculation.
17. Reduce-only/close racing fills and other close orders cannot reverse the position or bypass risk validation.
18. Restart rebuilds reservations and exclusive exposure buckets before publishing healthy authorization state.
19. Corrected/busted fills create linked compensating transitions without deleting historical evidence.
20. Snapshot versions are monotonic and stale writers are fenced across process/replica boundaries.
21. Audit data can reconstruct each exposure item from originating command/order/fill/ledger/external evidence.
22. Risk Engine outage or loss of reservation authority prevents new risk-increasing approval.

These are acceptance requirements, not tests already executed.

## 12. Owner decisions required

The following decisions are intentionally not guessed:

1. Initial deployment scope: one venue/account/subaccount or multiple venues/accounts from first release.
2. Risk-scope hierarchy and whether portfolio-wide limits aggregate across venues and strategies.
3. Spot/perpetual coexistence, hedge-mode vs one-way mode, netting and offset/hedge recognition policy.
4. Whether cross-margin is supported initially; approved collateral currencies, haircuts and concentration rules.
5. Valuation hierarchy for mark/index/FX, stale-price bounds and conservative market-order impact assumptions.
6. Treatment and upper-bound policy for pending/unknown external orders and positions.
7. Reservation TTL and expiry policy for pre-dispatch commands; never infer release after dispatch from TTL alone.
8. Maximum acceptable source lag and reconciliation watermarks by venue/account mode.
9. Transactional store, isolation level, multi-scope atomicity mechanism and disaster-recovery objectives.
10. Policy for emergency close/reduce actions when exact position or venue reduce-only semantics are uncertain.
11. Retention periods for reservation journal, raw venue evidence and audit lineage.
12. Whether manual orders are prohibited, routed through NEXUS, or allowed with mandatory quarantine/reconciliation.

Numeric risk limits, leverage caps, daily loss thresholds and drawdown limits remain owner-configured. UNCONFIGURED means no live risk-increasing authorization.

## 13. Dependencies and related contracts

- [NX-IF-001 — Canonical Trade Command & Risk Approval Contract](NX-IF-001-canonical-trade-command-risk-approval-contract.md): command digest, approval capability and one-time consumption.
- [NX-ADR-002 — Execution Integrity & Reconciliation](NX-ADR-002-execution-integrity-reconciliation.md): durable outbox, order/fill identity, ambiguous outcomes and reconciliation.
- [NX-ADR-005 — Instrument Specification & Exact Arithmetic](NX-ADR-005-instrument-specification-exact-arithmetic.md): immutable instrument versions, units and exact arithmetic.
- [ТЗ-NX-003 — Quant & Strategy Engine](../specifications/TZ-NX-003-quant-strategy-engine.md): TradeIntent is proposal-only.
- [ТЗ-NX-004 — Autonomous Execution Engine](../specifications/TZ-NX-004-autonomous-execution-engine.md): command/outbox/order lifecycle and private execution evidence.
- [ТЗ-NX-005 — Independent Risk Engine](../specifications/TZ-NX-005-independent-risk-engine.md): policy, exposure, reservation and approval authority.
- [ТЗ-NX-006 — Portfolio & Financial Ledger](../specifications/TZ-NX-006-portfolio-financial-ledger.md): posted financial journal and position projections.
- [NX-ARCH-REVIEW-001](NX-ARCH-REVIEW-001-cross-specification-contract-review.md): cross-service findings and WP-B closure criteria.

## 14. Disposition and verification limits

**WP-B design draft published; acceptance remains BLOCKED pending owner/security review, resolution of owner decisions and conformance design.**

This artifact defines a proposed contract only. No database isolation behavior, distributed transaction, reservation service, exposure calculator, signer, exchange adapter, integration test, concurrency test, fault test or runtime behavior has been implemented or verified. No live credentials, exchange connections, orders or risk-limit changes were used or performed.


## WP-D evidence and recovery composition

ExposureSnapshot MUST expose the source-specific event/cursor/journal/projection watermarks, connection generations, quality, completeness and reconciliation references required by [NX-IF-004](NX-IF-004-state-evidence-freshness-recovery-barrier-contract.md). A numerically populated snapshot is not authorization-ready unless its EvidenceRequirementSet passes for the requested operation class. RecoveryBarrier rebuilds exposure only after Execution, Ledger and venue evidence have reached the required recovery stages. Stale fencing generations, incomplete child scopes or unknown external exposure keep affected reservations conservative and block risk-increasing authorization. This is a proposed contract link; no implementation is claimed.
