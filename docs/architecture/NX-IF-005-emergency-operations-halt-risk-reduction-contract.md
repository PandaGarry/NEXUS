# NX-IF-005 — Emergency Operations, Halt & Risk-Reduction Authorization Contract

**Date:** 2026-11-14  
**Status:** PROPOSED — normative interface draft; not accepted  
**Work package:** NX-ARCH-REVIEW-001 / WP-E  
**Applies to:** NX-IF-001..004, NX-ADR-002, NX-ADR-005, NX-SEC-001, ТЗ-NX-004, ТЗ-NX-005, NX-ARCH-001  
**Baseline commit:** `92a27e4f0e3627fc773ec5f780d3840c406f7386`  
**Implementation status:** NOT STARTED

## 1. Purpose and scope

This contract defines how NEXUS halts risk-increasing activity, controls cancel/amend/close/reduce operations, authorizes emergency workflows and resumes a halted scope. It closes the final WP-E design gaps:

- a durable, monotonic, hierarchical `HaltState` protocol;
- explicit command classification and authorization matrix for CREATE, AMEND, CANCEL, CLOSE, REDUCE_ONLY, CANCEL_ALL and FLATTEN workflows;
- safe treatment of protective orders, in-flight commands, fill/cancel races and uncertain positions;
- bounded emergency action plans with explicit target sets and venue/account capability prerequisites;
- operator identity, step-up authentication, dual control and break-glass governance;
- independent final-dispatch enforcement, audit and recovery requirements;
- venue capability evidence and conformance/fault scenarios.

This is a logical interface contract, not a venue-specific implementation, kill-switch product, credential design, policy configuration or trading authorization. It does not choose numeric limits, roles assigned to actual people, dual-control thresholds, order types, venue shortlist or emergency order parameters. It does not authorize live trading.

## 2. Normative language and safety invariants

The terms MUST, MUST NOT, SHOULD and MAY are normative.

1. A halt MUST block new risk-increasing approvals and prevent queued, not-yet-dispatched risk-increasing commands in the affected scope from reaching the venue.
2. Halt activation MUST be possible through a separately authenticated control path and MUST NOT depend on AI, Strategy, market-data health or successful Risk evaluation.
3. Every halt activation, scope expansion, policy change, emergency command and resume MUST be durable, monotonic where safety requires, attributable and auditable.
4. A stale service instance, queued command or approval from an earlier halt epoch MUST NOT dispatch after a newer halt epoch is authoritative.
5. A halt does not cancel orders already accepted by a venue. Already-dispatched commands remain subject to reconciliation; their exposure cannot be assumed to have disappeared.
6. Cancel, amend, close, reduce-only, cancel-all and flatten are separate command workflows. None is inherently safe solely because of its label or a caller-supplied flag.
7. A command is RISK_REDUCING only when the independent Risk Engine can prove that its worst-case effect does not increase any applicable exposure, leverage, margin, concentration or loss dimension under current venue/account semantics.
8. Unknown classification is treated as risk-increasing and denied unless a narrowly scoped, owner-approved emergency policy explicitly defines the permitted action and evidence requirements.
9. A reduce-only flag, close-position flag, cancel acknowledgement or local position estimate is not proof that an action reduced exposure.
10. Risk-reducing actions remain authenticated, scoped, rate-limited, audited and routed through Execution. No client, AI component or strategy may call a venue directly.
11. A cancel may remove a protective order and increase worst-case loss. Cancel-all MUST NOT blindly cancel protective orders unless an approved plan explicitly includes them.
12. A close/flatten workflow MUST account for working orders and in-flight fills so it cannot overshoot, reverse a position or create an unintended opposite-side position.
13. An ambiguous emergency command outcome remains UNKNOWN and requires reconciliation; no blind resend.
14. Risk Engine outage MUST NOT prevent an authorized halt activation. It does prevent ordinary new risk approvals. Emergency execution during Risk outage is allowed only under a pre-approved, tightly bounded emergency policy whose validity can be independently verified; absent such a policy, no emergency order is dispatched.
15. Resume is a separate privileged operation. It MUST NOT follow automatically from reconnect, service restart, elapsed time or successful cancel request.
16. No generic emergency bypass may weaken NX-IF-001 command binding, NX-IF-002 reservation integrity, NX-IF-003 Ledger handoff, NX-IF-004 recovery barriers or NX-SEC-001 credential isolation.

## 3. Domain model

### 3.1 HaltScope

A `HaltScope` identifies the exact domain in which new risk-increasing activity is stopped:

- GLOBAL_SYSTEM;
- PORTFOLIO;
- VENUE_ACCOUNT;
- ACCOUNT / SUBACCOUNT;
- VENUE;
- INSTRUMENT;
- STRATEGY;
- any explicitly configured parent/child scope.

Every scope has a stable internal ID, parent IDs, configuration version and policy version. A parent halt applies to all configured descendants. A child halt does not automatically halt its parent unless a policy-defined escalation rule or unknown shared exposure requires escalation. If the affected scope cannot be bounded, escalate to the nearest configured parent and block there.

The effective halt is the most restrictive active state across all applicable ancestors and the target scope. A healthy child cannot override a halted parent.

### 3.2 HaltState

A durable `HaltState` contains:

- schema version, halt event ID and current monotonic `halt_epoch`;
- scope ID, scope type and parent-scope epochs;
- state and transition version;
- trigger type, reason codes, severity and source evidence;
- actor identity, actor role, authentication/step-up evidence and request channel;
- effective time, acknowledgement/propagation watermarks and expiry/review metadata (if policy supports time-bounded review);
- list of invalidated approvals/queued commands and affected recovery cases;
- linked incident, EmergencyActionPlan and audit event IDs.

A halt epoch MUST increase monotonically for the authoritative scope. Epoch reuse or rollback is forbidden. The authoritative epoch must be durably stored and checked at the final dispatch boundary. A service that cannot establish the current epoch MUST fail closed for risk-increasing dispatch.

### 3.3 Halt state machine

States:

- `ACTIVE` — no halt is active for this scope; normal policy applies.
- `HALT_REQUESTED` — authenticated halt request accepted for processing; risk-increasing dispatch is denied immediately at the receiving control boundary.
- `HALT_PROPAGATING` — new epoch is durable and is being enforced by Risk, Command Coordinator, Execution dispatchers and relevant scopes.
- `HALTED` — all required enforcement acknowledgements are recorded or any non-acknowledging boundary is isolated so it cannot dispatch.
- `RECOVERY_REVIEW` — incident cause is contained; source reconciliation, Ledger/Risk reconstruction and operator review are underway.
- `RESUME_REQUESTED` — an authorized resume request has passed initial identity/scope validation but no scope is yet reopened.
- `RESUMING` — new epoch and policy are propagating; dispatch remains blocked until all gates pass.
- `ACTIVE` — normal operation resumes only after explicit final authorization and successful enforcement acknowledgement.

A request does not equal successful propagation. After the epoch is durably committed, the scope remains HALT_PROPAGATING until every required boundary acknowledges the new generation or is positively isolated. If a boundary misses the configured policy deadline, the system MUST keep enforcement pending, isolate/disable that boundary or treat it as unavailable, and MUST NOT transition to HALTED or report HALTED as fully enforced while an unisolated dispatcher can still send orders.

Transitions are append-only. A repeated halt request is idempotent with respect to the same incident/scope but MUST NOT decrease or reuse the epoch. A wider halt increments the affected parent epoch and invalidates descendant approvals. A narrower halt cannot clear an ancestor halt.

### 3.4 EmergencyActionPlan

An `EmergencyActionPlan` is a versioned, owner-approved policy artifact. It defines:

- permitted trigger conditions and halt scopes;
- allowed operation classes and target-selection rules;
- required source evidence and minimum RecoveryBarrier/FreshnessPolicy versions;
- whether Risk Engine must be online or a pre-authorized offline policy may be used;
- instrument/account/position-mode/venue capability prerequisites;
- protected-order handling and explicit exclusions;
- quantity/notional/price/slippage/time bounds;
- rate-limit priority and retry policy;
- operator authorization and dual-control requirements;
- stop conditions, maximum attempts and reconciliation/closure criteria;
- policy version, approval, effective time, digest and review date.

An EmergencyActionPlan MUST NOT contain reusable exchange signatures or credentials. A plan is not an order and does not imply automatic execution. Each action is instantiated as a separately identified command with a fresh evidence check and immutable digest.

### 3.5 EmergencyCommand and authorization

An `EmergencyCommand` is a normal immutable CanonicalTradeCommand subtype with additional references:

- `incident_id`, `halt_epoch`, `emergency_plan_id/version`;
- `target_set_id/version` for bounded multi-order workflows;
- `operator_action_id` and authenticated actor identity where operator-initiated;
- `state_evidence_vector_id/version` and `recovery_barrier_id/generation`;
- explicit `risk_classification`, RiskDecision and scoped authorization reference;
- reason code, deadline and correlation lineage.

Emergency commands still pass through canonical validation, durable command/outbox, Execution adapter, exact payload approval and reconciliation. The emergency policy may define a constrained authorization capability for a specified operation, but it MUST be bound to the exact command digest, scope, halt epoch, target set, instrument spec, evidence vector, policy version, expiry and audience. It is never a broad “emergency mode” permission.

## 4. Command classification and authorization matrix

### 4.1 Classification rule

Risk Engine evaluates the complete worst-case effect of the command against the current reconciled state. It considers gross/net exposure, position side/mode, pending order remainders, reservations, possible fills during the action, protective-order effects, margin/collateral, liquidation risk, concentration and fees/slippage where material.

If the effect cannot be bounded, classification is UNKNOWN and the command is denied under ordinary policy. A caller-supplied `reduce_only=true` does not change this rule.

### 4.2 Baseline authorization matrix

| Command class | Default classification | Required authorization/evidence | Halt behavior |
|---|---|---|---|
| CREATE / new exposure | RISK_INCREASING | NX-IF-001 approval, active WP-B reservation, READY WP-D barrier, current account/market/spec evidence | Deny in halted scope |
| AMEND — quantity/price/side/trigger/TIF or flags may worsen risk | RISK_INCREASING or UNKNOWN | New complete effective command, fresh Risk evaluation/reservation, venue amend semantics and race handling | Deny in halted scope |
| AMEND — proven strict risk reduction | Candidate RISK_REDUCING, never presumed | Risk proof, target order state, venue atomicity/priority semantics, bounded resulting parameters | Only through approved emergency/normal reduction policy |
| CANCEL — ordinary order | UNKNOWN until evaluated | Target identity/state, whether it is protective, pending fills and effect on worst-case exposure | No blanket cancel; plan/policy decides |
| CANCEL — unprotected risk-increasing remainder | Candidate RISK_REDUCING | Venue cancel capability, current order/fill evidence, exact target and reconciliation | May be permitted by approved emergency plan |
| CANCEL — protective order | Potentially RISK_INCREASING | Explicit protective-order classification and owner-approved plan | Deny unless plan explicitly authorizes removal |
| REDUCE_ONLY | Candidate RISK_REDUCING, not inherently safe | Current confirmed position, position mode, other working/pending reductions, venue reduce-only capability and worst-case quantity bound | May be permitted under emergency policy |
| CLOSE / close-position | UNKNOWN until evaluated | Position identity/mode, venue close semantics, bounded quantity, pending orders/fills and proof no reversal | May be permitted only with explicit plan and fresh evidence |
| CANCEL_ALL | UNKNOWN | Immutable bounded target set, per-order protection classification, pagination/completeness and venue capability | Never unbounded or implicit |
| FLATTEN workflow | Multi-step plan, not a primitive order | Repeated reconcile → calculate residual → authorize bounded reduce → dispatch → reconcile; explicit stop/overshoot rules | Only under a dedicated approved plan |
| HALT request / activation | Control-plane action, no trading exposure | Authenticated permitted actor or accepted policy trigger; durable epoch increment and audit | Request is accepted through the independent Control Plane; fully-enforced HALTED requires authoritative durable epoch commit plus boundary acknowledgement/isolation. If the halt store is unavailable/uncertain, Egress denies final authorization and the request remains pending |
| RESUME | Privileged control-plane action | Recovery gates, reconciled state, current policy, step-up and dual control where required | Never automatic |

This matrix is the conservative default. Owner-approved venue/account-mode policy may narrow or refine it but MUST NOT weaken the system invariants.

### 4.3 Risk-reduction proof

A command is proven RISK_REDUCING only when all applicable conditions hold:

1. The account and position mode are authoritative and current.
2. The exact position identity, signed quantity and instrument specification are known.
3. All working orders, pending creates/amends/cancels, reservations and unknown outcomes that can affect the same position are included.
4. The proposed command's worst-case fills cannot exceed the currently reducible quantity after accounting for concurrent commands and in-flight fills.
5. Venue reduce-only/close semantics are documented and certified for the exact product, account mode and API endpoint.
6. The operation cannot reverse the position, open the opposite side, increase gross exposure, increase leverage/margin or remove a protective control without explicit policy authorization.
7. Price/trigger/TIF and partial-fill behavior are bounded; unknown order behavior is not assumed favorable.
8. A current StateEvidenceVector and applicable RecoveryBarrier satisfy the command's requirement set.
9. Risk Engine issues a scoped approval bound to the exact command, evidence, halt epoch and policy.
10. The command is durably persisted and dispatched through Execution; outcomes are reconciled.

If any condition is false or UNKNOWN, it is not proven risk-reducing.

### 4.4 Amend and cancel-replace

AMEND is a new immutable command. The canonical payload MUST describe the complete resulting order state, not a mutable partial patch.

Venue adapter capability declares:

- native amend versus cancel-replace;
- atomicity and old/new order identity mapping;
- priority loss and queue consequences;
- whether quantity may increase/decrease;
- fills accepted during amendment;
- behavior on timeout/partial response;
- whether the old order remains live after a failed replacement.

If the venue only supports cancel-replace, model two linked commands and their independent outcomes. The old order's exposure remains until cancellation is confirmed; the replacement's exposure is reserved before dispatch. Never assume atomic replacement or release the old reservation on a cancel request.

### 4.5 Cancel and cancel-all

A cancel request is asynchronous. Target order remains exposure-bearing until authoritative terminal order state and final cumulative fills are reconciled.

CANCEL_ALL MUST first create an immutable target set from a complete, scoped order snapshot. The target set records source watermark, retrieval time, pagination coverage, included/excluded order IDs, protective-order classification and selection-policy version. Every selected order receives a separately tracked cancel command; partial success is represented explicitly.

A target set is stale if order state or source watermark changes before dispatch. Rebuild and re-evaluate the target set; do not silently expand it. An unbounded venue “cancel all” endpoint may be used only if the adapter proves exact scope equivalence to the approved target set and its protective-order policy.

No cancel-all result is considered complete until all target orders and fills are reconciled. Protective orders are excluded by default unless the plan explicitly includes them with an owner-approved rationale.

### 4.6 Close, reduce-only and flatten

A REDUCE_ONLY command requires the actual venue position mode and confirmed position. The maximum command quantity is bounded by reducible exposure after subtracting other live/pending reduction quantities and accounting for fills racing with cancellation. If the venue's reduce-only semantics are not certified, the command is unsupported.

CLOSE/close-position is not universally equivalent across venues. It may close one leg, all legs, a net position or a venue-defined quantity. The adapter must document the exact semantics and position index requirements.

FLATTEN is a controlled workflow:
1. halt new risk-increasing activity in the target scope;
2. reconcile orders, fills, positions and reservations;
3. apply the approved protective-order policy;
4. compute a bounded residual position from confirmed state;
5. create one scoped reduce/close command with a quantity not exceeding the proven reducible amount;
6. dispatch and reconcile all fills/remaining position;
7. repeat only after a new evidence vector and Risk authorization;
8. stop on ambiguity, stale state, unsupported venue semantics, rate-limit exhaustion or any potential reversal.

FLATTEN MUST NOT be an unbounded loop or a one-click instruction that assumes success. Residual dust, minimum size and contract rounding are explicit outcomes; do not invent a final quantity.

## 5. Halt activation and propagation

### 5.1 Activation sources

A halt may be requested by:

- an authenticated Owner or authorized Incident Commander / Risk Operator within assigned scope;
- Risk policy when a configured hard condition is met;
- Execution or reconciliation policy when a configured integrity/security condition requires immediate containment;
- security incident response through the documented break-glass path.

AI and Strategy may raise a typed halt request/alert with evidence and rationale. They cannot directly mutate HaltState, choose a broader permission scope, override a denial or authorize resume. Policy may accept an automated request only within pre-approved trigger rules.

### 5.2 Activation sequence

1. Authenticate actor/trigger and validate allowed scope. Halt activation does not require a trading approval.
2. Atomically advance the authoritative halt epoch and persist the HALT_REQUESTED event with reason/evidence.
3. Immediately deny new risk-increasing approvals at Risk and invalidate affected unconsumed capabilities.
4. Propagate the new epoch to Command Coordinator, all Execution dispatchers and applicable child scopes.
5. Stop queued risk-increasing commands before network dispatch; preserve their durable records and reservations for explicit resolution.
6. Inventory already-dispatched commands and open orders. Mark ambiguous outcomes UNKNOWN and reconcile; do not assume they were canceled.
7. Execute only the actions in an active EmergencyActionPlan with required authorization.
8. Record acknowledgement from each enforcement boundary. If a boundary does not acknowledge or cannot prove current epoch, isolate/disable it; the scope remains blocked.
9. Publish HALTED only when all required boundaries acknowledge the epoch or are proven unable to dispatch.

Halt activation must be fast and fail-safe. The implementation may propagate asynchronously, but each dispatch boundary must independently check the current epoch before sending. A stale cached epoch is insufficient.

#### 5.2.1 Halt race with the final Trusted Egress gate

The final Trusted Egress send-authorization transaction and the authoritative halt-epoch transition MUST serialize against the **same authoritative halt-state record/generation**. A cached epoch, asynchronous notification or process-local mutex is not sufficient.

The halt transition is owned by the independently authorized emergency Control Plane, not by the Risk Engine process. A Risk Engine/application outage therefore does not prevent the Control Plane from committing a halt epoch when the authoritative halt-state store is available. If that durable store is unavailable or its authority is uncertain, Egress cannot commit its final authorization gate and MUST deny new sends; the halt request may be recorded as pending, but the system MUST NOT claim HALTED as fully enforced until the epoch is durably committed and every dispatch boundary acknowledges it or is positively isolated. This distinguishes Risk-service failure from authoritative control-store failure and does not invent an offline bypass.

- If the halt-epoch transaction commits before the EgressBoundaryAuthorization transaction, the final gate MUST observe the newer epoch and deny the attempt. No socket-write initiation is permitted for that attempt.
- If the EgressBoundaryAuthorization transaction commits first, that attempt is logically **dispatch-committed / in-flight** at that commit, even if the process is descheduled before the socket-write call. A later halt cannot retroactively revoke that already committed one-time authorization. The attempt remains potentially sent, its full conservative reservation remains held, and it MUST be reconciled. No claim is made that a halt request prevents every network byte from being emitted after the wall-clock time of the halt request.
- The Egress boundary MUST track every gate-committed attempt until socket-write initiation is observed or the old Egress process/host/path is positively fenced. It MUST NOT acknowledge the new halt epoch while an earlier gate-committed attempt could still resume and initiate a socket write. If the attempt cannot be drained or its sender cannot be positively fenced, the boundary is not acknowledged and the scope cannot be reported HALTED as fully enforced.
- Once every boundary has acknowledged the new epoch or has been positively isolated, no stale or queued attempt may initiate a new socket write. Venue processing/acceptance of a request already initiated before that acknowledgement remains an in-flight external effect and is handled by reconciliation; halt does not recall bytes already sent or cancel venue orders.

This defines the linearization order, not an exactly-once network guarantee. If a future operational requirement demands that no socket-write initiation occur after the halt transaction commits even for an earlier gate-committed attempt, the transport/egress architecture must provide a stronger independently fenced cancellation/serialization mechanism and prove it under process pause, host partition and crash tests; PostgreSQL transaction ordering alone cannot make that claim.


### 5.3 In-flight and protective orders

Halt does not imply cancel-all. The system classifies open orders into at least:

- unprotected exposure-increasing orders;
- protective stop/limit orders;
- take-profit/exit orders;
- reduce-only orders;
- unknown/unclassified orders.

Policy defines whether each class is retained, canceled or replaced. Unknown orders are not silently treated as non-protective. Orders already accepted by the venue remain live until confirmed terminal; Risk includes their remaining exposure during the incident.

## 6. Emergency action while Risk Engine is unavailable

The default is fail closed: Risk Engine unavailability blocks new risk-increasing commands and ordinary risk-reducing commands that require a fresh classification.

An owner may approve a constrained EmergencyActionPlan for a narrowly defined failure mode. Such a plan:

- is immutable/versioned and approved before the incident;
- permits only enumerated operations, venues, account modes, instruments, scopes and quantity/price/time bounds;
- binds to an exact policy digest and halt-epoch behavior;
- requires fresh minimum evidence from an independent source path;
- is verifiable by Execution without AI interpretation or unrestricted Risk bypass;
- cannot create new exposure, reverse a position, relax limits or withdraw/transfer assets;
- records every invocation and has bounded attempts and expiry;
- stops on unknown position, unknown working orders, stale evidence, venue capability mismatch, ambiguous outcome or any limit breach.

If the plan's prerequisites are not met, no emergency order is sent. A halt can still be activated and maintained. This contract does not assume that a pre-authorized offline emergency plan exists.

## 7. Resume and controlled reopening

Resume is separate from incident containment and must pass the WP-D RecoveryBarrier.

Minimum gates:

1. halt cause is identified and contained or accepted under a documented residual-risk decision;
2. durable state, outbox/inbox, journal, reservation and audit stores are valid;
3. private order/fill/account state is reconciled with explicit coverage and retention boundaries;
4. Ledger postings and projections are current and reconciled;
5. Risk ExposureSnapshot includes every known order, position, reservation, external item and unknown exposure;
6. no unresolved critical discrepancy remains, or an owner-approved exception explicitly preserves a conservative bound and scope restriction;
7. instrument specification and active policy versions are valid;
8. StateEvidenceVector and RecoveryBarrier are READY for the exact scope/operation class;
9. all dispatch boundaries are online, authenticated and enforcing the current halt epoch;
10. the proposed resumed command classes and limits are explicitly stated;
11. authorized operator performs step-up authentication and records rationale/evidence;
12. dual approval is obtained for configured high-impact scopes;
13. a new monotonic halt epoch is published and acknowledged before the scope becomes ACTIVE.

Resume MUST NOT clear unrelated halts or quarantine cases. A narrower scope may resume only if all applicable parent scopes are ACTIVE and all inherited gates pass. Any failure returns the scope to HALTED or RECOVERY_REVIEW.

## 8. Operator authorization and separation of duties

Logical role capabilities (actual assignment is an owner decision):

| Role | Permitted actions | Prohibited actions |
|---|---|---|
| Owner | Approve emergency policies, high-impact resume, role/threshold configuration and explicitly reserved owner actions | Cannot bypass immutable audit or source reconciliation |
| Incident Commander | Request scoped/global halt, initiate approved incident plan, coordinate containment | Cannot alter risk limits or approve own high-impact resume where dual control applies |
| Risk Operator | Review risk state, reconcile exposure exceptions, request/approve permitted scope recovery | Cannot access venue secrets or bypass Execution |
| Execution Operator | Inspect commands/orders, initiate approved cancel/reduce workflow and reconciliation | Cannot mint Risk approvals, change policies or access raw signing keys |
| Auditor | Read evidence, decisions and audit history | No mutation/dispatch authority |
| AI / Strategy / Client | Submit proposal or halt request with evidence; read authorized status | No direct halt-state mutation, approval signing, secret access, policy activation or resume |

All privileged operations require authenticated human identity, resource-level RBAC and least privilege. Step-up authentication is required for halt reset/resume, emergency plan activation and other owner-defined high-impact operations. Dual control applies to configured high-impact scopes; the initiating actor cannot be the sole approver.

Break-glass access is separate, time-limited, strongly authenticated, alerted and reviewed after use. It does not grant withdrawal rights or permission to bypass risk/Execution boundaries. Actual role names, identity provider, step-up method, dual-control threshold and emergency contacts are owner decisions.

## 9. Venue capability registry

No venue-specific emergency capability is assumed until documented and tested for exact product/account mode.

Each adapter must publish a versioned capability record containing:

- venue, API version, endpoint and account/position mode;
- supported order types and exact reduce-only/close-position semantics;
- native amend, cancel-replace and atomicity/priority behavior;
- cancel-one and cancel-all scope semantics, pagination and protective-order implications;
- client-order ID and idempotency guarantees;
- private stream order/fill identity, sequence/cursor and reconciliation endpoints;
- rate limits and emergency-query/cancel priorities;
- minimum quantity, step, tick, notional and contract rules from NX-ADR-005;
- partial-fill and cancel/fill race behavior;
- response ambiguity and recovery queries;
- source URL, retrieval date, pinned documentation/API version, adapter version;
- fixture/test evidence, limitations, confidence and owner certification.

Capability status is one of VERIFIED, PARTIAL, UNSUPPORTED or UNKNOWN. README/API marketing claims are not capability evidence. UNKNOWN/UNSUPPORTED blocks the affected command class for that venue/account mode.

## 10. Audit, alerts and observability

Every halt/emergency/resume event records:

- actor/trigger identity, role, authentication and approval chain;
- scope, old/new epoch, policy and EmergencyActionPlan versions/digests;
- reason, incident and evidence references;
- exact command/target-set digests and per-order results;
- risk classification, decision, reservation and approval IDs;
- dispatch attempts, venue responses, native IDs and timestamps;
- current position/order/fill state and reconciliation watermarks;
- stop condition, exception, operator override and closure proof.

High-priority alerts include halt requested/propagating, unacknowledged dispatcher, stale epoch rejection, emergency command ambiguity, protective order removal, partial cancel-all, reduce/close overshoot risk, failed reconciliation, unauthorized resume attempt, break-glass use and any change to emergency policy.

Audit is append-only and tamper-evident. Logs redact secrets, signatures, authorization headers and unnecessary personal/account data.

## 11. Failure and conformance scenarios

At minimum, test:

1. halt request during high-rate command intake;
2. dispatcher offline or partitioned during halt propagation;
3. stale dispatcher attempts dispatch with an older epoch;
4. Risk Engine unavailable when halt is requested;
5. queued command persisted but not dispatched when halt epoch advances;
6. command sent immediately before halt with response lost;
7. venue accepts an order after local halt due to network race;
8. parent portfolio halt propagates to all child accounts;
9. child instrument halt does not silently clear or weaken parent halt;
10. restart attempts to restore ACTIVE from stale local cache;
11. unconsumed approval replay after halt epoch changes;
12. cancel request accepted but order remains working;
13. fill arrives before, during and after cancel acknowledgement;
14. cancel-all target pagination incomplete or source watermark changes;
15. cancel-all contains a protective order;
16. cancel-all partially succeeds with one target outcome unknown;
17. native amend is non-atomic and a fill occurs during amendment;
18. cancel-replace old order cancels but replacement is rejected;
19. cancel-replace replacement is accepted while old order remains ambiguous;
20. REDUCE_ONLY quantity exceeds position after concurrent fill;
21. hedge-mode close targets the wrong position leg;
22. venue close-position semantics differ from expected net-mode behavior;
23. reduce-only flag is ignored/rejected by venue;
24. flatten workflow attempts a second action before first action reconciliation;
25. minimum size/step rounding leaves residual dust;
26. venue rate limit blocks emergency cancel/reconciliation;
27. Risk Engine unavailable and no approved offline emergency plan exists;
28. offline emergency plan expired, wrong scope or wrong instrument;
29. operator without step-up or required second approver requests resume;
30. RecoveryBarrier is not READY but resume is requested;
31. break-glass action exceeds scope or expiry;
32. AI-generated halt request attempts to directly mutate HaltState;
33. protective-order cancellation increases worst-case loss and is rejected;
34. external/manual order is discovered during emergency workflow;
35. emergency order outcome remains UNKNOWN and no blind resend occurs;
36. halt epoch commits before the final EgressBoundaryAuthorization gate; the gate observes the new generation and denies with zero socket-write initiation;
37. EgressBoundaryAuthorization commits before halt epoch; attempt becomes gate-committed/in-flight and remains reserved until socket-write initiation is observed or sender is positively fenced;
38. Egress process is paused after gate commit but before socket write; halt cannot be acknowledged while that process could resume and initiate the write;
39. process/host/network fencing is unavailable or unproven; the boundary remains unacknowledged and the scope cannot be reported HALTED as fully enforced;
40. halt control store is unavailable or authority is uncertain; Egress denies new final gates and the halt request remains pending rather than claiming successful enforcement;
41. socket write is initiated before boundary acknowledgement but venue accepts/reports the order after acknowledgement; order remains potentially live and is reconciled without blind resend;
42. instrumented actual socket/network boundary proves no stale or queued attempt can initiate a write after the boundary's halt acknowledgement.

## 12. Acceptance criteria

1. HaltState is durable, scoped, monotonic and protected against stale writers/epochs.
2. Risk-increasing approvals and queued commands without a committed final EgressBoundaryAuthorization are blocked immediately on a halt request at the authoritative control boundary.
3. The final EgressBoundaryAuthorization and halt-epoch transition serialize on the same authoritative generation: halt-first denies socket initiation; gate-first is an in-flight attempt that remains reserved/reconciliation-gated, and Egress cannot acknowledge the newer halt epoch until the attempt is drained to observed socket initiation or its sender is positively fenced.
4. A non-acknowledging dispatcher is isolated or remains a blocking failure; HALTED is not falsely reported as fully enforced.
5. Already-dispatched orders remain exposed until authoritative venue evidence resolves them.
6. Halt request/activation is possible while Risk Engine is unavailable through the independently authorized Control Plane, provided the authoritative halt-state store is available; if that store is unavailable/uncertain, Egress denies final authorization and the system cannot claim fully-enforced HALTED.
7. No automatic cancel-all or flatten is triggered by halt unless an active approved plan explicitly requires it.
8. Command classes have versioned classification and authorization policy; UNKNOWN is not risk-reducing.
9. AMEND is a new complete immutable command and invalidates prior approval.
10. Cancel-replace is modeled as linked commands with separate exposure and race handling.
11. CANCEL_ALL uses a complete immutable target set and explicit protective-order policy.
12. Cancel acknowledgement does not establish target order terminal state.
13. Risk-reduction proof accounts for position mode, all pending orders/reservations, partial fills, venue semantics and worst-case reversal.
14. CLOSE/REDUCE_ONLY cannot exceed confirmed reducible quantity or reverse exposure.
15. FLATTEN is iterative, bounded and reconciled between every action.
16. EmergencyActionPlan is owner-approved, immutable, scoped, versioned, time-bounded and independently verifiable.
17. Risk Engine outage blocks ordinary emergency trading unless a valid pre-approved constrained plan explicitly permits the exact action.
18. Emergency commands remain subject to canonical payload binding, durable outbox, venue capability checks, rate limits and reconciliation.
19. Resume requires WP-D RecoveryBarrier readiness, reconciled state, current policy, current halt epoch and explicit privileged authorization.
20. Resume cannot clear parent halts, unrelated quarantine or unresolved unknown exposure.
21. Step-up and dual control are enforced for owner-configured high-impact actions.
22. AI/Strategy/client cannot mutate HaltState, sign emergency commands, access credentials or authorize resume.
23. Venue capability registry records source/version/evidence and blocks UNKNOWN command classes.
24. Protective-order behavior is explicit and cannot be silently overridden by cancel-all.
25. Emergency rate-limit prioritization never violates venue limits or suppresses reconciliation evidence.
26. Audit reconstructs every halt, command, target selection, approval, dispatch, fill, reconciliation and resume decision.
27. Failure scenarios cover race, partition, stale epoch, partial cancel, ambiguous result, position-mode mismatch and Risk outage.
28. No implementation, CI, adapter certification, runtime or production-readiness pass is claimed without evidence.
29. Halt epoch and final EgressBoundaryAuthorization serialize against the same authoritative halt-state record/generation; both lock-order outcomes are tested.
30. A gate-committed attempt paused before socket write prevents halt acknowledgement until the write is observed or the old sender is positively fenced.
31. A missing/uncertain halt store or unproven external fence denies new sends and prevents a false HALTED acknowledgement.
32. An already initiated socket write may be accepted by the venue after halt acknowledgement; it remains potentially live, reserved and subject to reconciliation.
33. Tests observe the actual socket/network boundary, not only a database flag or mock adapter call.

## 13. Open owner decisions

1. Initial venue/account-mode/product shortlist and emergency capability priorities.
2. Actual human role assignments, identity provider and step-up authentication method.
3. Which halt scopes and trigger thresholds are enabled at first release.
4. Which command classes are permitted during halt, and whether any pre-approved offline emergency plan is desired.
5. Protective-order classification and default behavior during halt/cancel-all/flatten.
6. Dual-control scopes and thresholds, including who may request versus approve resume.
7. EmergencyActionPlan bounds: allowed instruments, order types, quantity/notional/price/slippage/time limits and stop conditions.
8. Rate-limit priority policy for emergency cancel versus reconciliation and normal private stream recovery.
9. Required venue capability evidence and certification depth before each emergency command class is enabled.
10. Break-glass custody, contacts, notification and post-incident review process.
11. Residual-dust/minimum-order policy and treatment of positions that cannot be flattened safely.
12. Whether halt activation is always system-wide on a credential/signing incident or may be scoped by affected key/account.

Until these are approved and encoded, unsupported or ambiguous emergency operations remain disabled. No default live emergency plan is assumed.

## 14. Verification status

This document is a proposed design contract only. No HaltState store, epoch propagation, kill-switch controller, operator RBAC/MFA workflow, emergency plan executor, venue capability certification, cancel/reduce/close adapter, fault-injection suite or runtime behavior has been implemented or verified. No venue account, live credential or order was used. No risk limit or live-trading control was changed.

**Prototype Readiness remains BLOCKED.**
