# NX-ARCH-REVIEW-001 — Cross-Specification Contract Review

**Date:** 2026-11-14  
**Status:** PROPOSED — design review memo, not an accepted ADR  
**Scope:** NX-ARCH-001, NX-ADR-001..005, ТЗ-NX-001..006, NX-SEC-001  
**Baseline branch:** `docs/project-foundation`  
**Baseline commit verified:** `d38e9dfecaf522ea24d89b4a2cd148a2f92244dd`

## 1. Purpose and bounded scope

This review checks whether the current proposed architecture and six core specifications can compose into one safe command, data and financial-state lifecycle. It does not re-audit Tradoor, select infrastructure, approve a venue, define owner risk limits, or authorize implementation.

Review is limited to:
- authority and trust boundaries;
- canonical command/approval identity;
- concurrent exposure and reservation lifecycle;
- order/fill/ledger event ownership;
- freshness, reconciliation and recovery;
- exact arithmetic and version lineage;
- halt, cancellation and risk-reduction semantics.

## 2. Executive result

**Architecture synthesis is directionally coherent, but interface readiness is BLOCKED.**

The documents consistently separate Strategy, Risk, Execution, Ledger and AI authority. They also consistently reject unknown-as-zero, blind retry, acknowledgement-as-fill and stale-state authorization.

However, the specifications are still predominantly logical contracts. They do not yet define one interoperable canonical command schema, a complete reservation/approval protocol, a single source-of-truth matrix for pending exposure, or end-to-end recovery semantics across Risk, Execution and Ledger. These are design blockers, not implementation bugs.

No component implementation, schema conformance test, runtime test or deployment test was performed in this review.

## 3. Cross-specification findings

### F-01 — Canonical command identity is not yet a single normative contract

NX-ARCH-001 and ТЗ-NX-005 require approval bound to an exact payload digest; ТЗ-NX-004 independently lists execution-relevant fields and revalidation. The Strategy specification emits TradeIntent, while the Execution specification accepts a canonical command. A normative transformation and versioned schema between TradeIntent → OrderIntent/Command → signed approval are not yet defined.

**Required resolution:** define a canonical, versioned command envelope and deterministic serialization/canonicalization rules. Explicitly include environment, account/subaccount, venue, market type, instrument native ID and immutable spec version, side/position side, order type, quantity, price/trigger fields, time-in-force, reduce-only/close semantics, client intent identity, expiry and all execution-affecting flags. Unknown or unsupported fields must reject, not disappear during digest construction.

### F-02 — Risk reservation and durable dispatch need a crash-safe lifecycle

ТЗ-NX-005 requires concurrent approvals to reserve exposure. ТЗ-NX-004 requires command + approval reference + outbox to persist before dispatch. The documents do not yet specify how a reservation is atomically associated with a durable command, how it survives crashes, or how it is released/consumed after rejection, expiry, cancellation, partial fill, fill or OUTCOME_UNKNOWN.

**Required resolution:** specify reservation states and transitions, durable reservation IDs, fencing/version checks, lease/expiry behavior, and reconciliation rules. A reservation must remain conservatively active while an exchange outcome is ambiguous. No approval may be issued against a stale aggregate exposure version.

### F-03 — Pending exposure ownership can double-count or omit risk

ТЗ-NX-005 consumes positions, open orders, pending outbox commands and unresolved outcomes. ТЗ-NX-006 exposes OpenOrderAndPendingExposure joined with Execution. ТЗ-NX-004 owns command/outbox and order lifecycle. Without a field-level ownership matrix, the same order may be counted in both Execution and Risk reservation state, or omitted during transitions between outbox, venue acknowledgement and private order events.

**Required resolution:** define one canonical exposure aggregation view with stable command/order identities and mutually exclusive lifecycle buckets. State explicitly which component owns each bucket and the watermark/transaction boundary at which an item moves between buckets. Add invariants preventing both gaps and double counting.

### F-04 — Ledger and Execution cannot assume a shared transaction

ТЗ-NX-004 persists commands and private execution events; ТЗ-NX-006 journals fills, fees, funding and account changes. The architecture does not establish a distributed atomic transaction between their stores.

**Required resolution:** use durable event handoff with inbox/outbox, idempotent consumer offsets and explicit delivery guarantees. Execution's normalized fill evidence and Ledger's posted financial event must be separately traceable. A fill is not considered financially reconciled merely because Execution received it. Failure between event persistence and ledger posting must recover without loss or duplicate posting.

### F-05 — Freshness needs a composable vector, not one generic timestamp

ADR-001, ADR-004, ТЗ-NX-005 and ТЗ-NX-006 all require timestamps, quality and watermarks, but there is no common freshness contract across market data, instrument specs, private account/order streams, Ledger projections, risk reservations and reconciliation.

**Required resolution:** define a versioned StateEvidence/FreshnessVector with per-source as-of time, receive/processing time, sequence or cursor watermark, connection generation, quality, reconciliation watermark, spec/policy/projection version and configured maximum age. Risk policy decides which components are mandatory for each command class. Missing vector elements remain UNKNOWN.

### F-06 — Cancel, amend and risk-reducing actions require a separate authorization matrix

ADR-002 and ТЗ-NX-004 state that cancel/reduce behavior is policy-controlled; ТЗ-NX-005 does not yet provide a complete command-class matrix. A cancel can remove a protective order; an amend can increase exposure; reduce-only can be rejected or behave differently by venue/account mode; a close command can race with fills or create a reverse position if semantics are wrong.

**Required resolution:** classify CREATE, AMEND, CANCEL, CLOSE, REDUCE_ONLY, CANCEL_ALL and emergency actions separately. Define when each needs fresh Risk approval, what evidence proves it reduces risk, venue capability prerequisites, fill/cancel race handling, and what to do when the position or order state is UNKNOWN. No generic bypass for reduce-only or cancellation.

### F-07 — Kill switch is an intent/state protocol, not a single boolean

Risk and Execution documents both mention kill switches, but the cross-service state propagation, acknowledgement and recovery protocol is not yet normative.

**Required resolution:** define HALT_REQUESTED → HALT_PROPAGATING → HALTED → RECOVERY_REVIEW → RESUMING states, scope hierarchy, monotonic halt generation/epoch, durable audit, behavior of already-dispatched commands, treatment of unknown orders, and explicit owner/operator authorization for resume. A stale service must not accept commands from an earlier epoch.

### F-08 — Risk calculations need an explicit valuation and uncertainty contract

ТЗ-NX-005 consumes exposure, margin, collateral, P&L, funding and stress inputs. ТЗ-NX-006 intentionally separates cash, collateral equity, margin equity and valuation estimates. The specifications do not yet pin the approved mark/index/FX hierarchy, haircuts, stale-price fallback, inverse/quanto valuation boundary or aggregation policy for cross-venue collateral.

**Required resolution:** create a versioned valuation contract with units, currencies, source priority, timestamps, quality, haircuts, contract formula version and account-mode semantics. If the policy cannot calculate a conservative bound, return UNKNOWN and deny risk-increasing activity. Stress scenarios must be labeled scenarios, not forecasts.

### F-09 — Instrument and policy version changes must invalidate approvals predictably

ADR-005 versions instrument specs; ТЗ-NX-005 versions policies and approvals; ТЗ-NX-004 validates approval immediately before dispatch. The cross-service rule for a spec/policy update between approval and dispatch is not fully specified.

**Required resolution:** approval binds immutable spec and policy versions plus the relevant state version. Execution rechecks current allowed versions immediately before dispatch. Material spec/policy change invalidates approval and reservation or requires explicit compatibility proof; never silently reinterpret an approved quantity or price.

### F-10 — External/manual activity and unknown account events need a defined quarantine path

ADR-002 and ТЗ-NX-006 require detection of external/manual orders and unknown financial events. ТЗ-NX-005 requires complete exposure. The end-to-end response to an externally created order, unsupported position mode, unknown fee/funding event or incomplete account snapshot needs one shared quarantine contract.

**Required resolution:** define scope escalation (instrument → account → venue → portfolio), evidence retention, operator resolution workflow, and exact conditions for releasing the hold. Unknown exposure must be included conservatively or force a wider halt.

### F-11 — Strategy decision lineage must survive command transformations

ТЗ-NX-003 records strategy artifact, DecisionContext and TradeIntent. ТЗ-NX-004 records command/order identities. ТЗ-NX-005 records evaluation and approval. ТЗ-NX-006 attributes financial outcomes. The required end-to-end lineage is described but not yet standardized.

**Required resolution:** standard correlation lineage: strategy artifact/version → evaluation/context digest → TradeIntent ID → canonical command ID → risk evaluation/approval/reservation ID → venue order/client ID → fill IDs → ledger journal transaction IDs. Manual/external actions remain explicitly unattributed rather than being assigned to a strategy.

### F-12 — Recovery ordering across services is not yet specified

Each specification defines local recovery, but not the system-wide recovery barrier. Restarting Execution before Ledger/Risk has reconciled can expose stale state; restarting Risk with lost reservations can authorize excess exposure.

**Required resolution:** define startup/reconnect barrier: restore durable stores → ingest/reconcile venue account/orders/fills → rebuild Ledger projections → rebuild open/pending exposure and reservations → validate policy/spec versions → publish healthy state → only then enable risk-increasing authorization. Any incomplete stage keeps affected scope halted.

## 4. Proposed normative interface set

The following contracts are required before implementation. WP-A..WP-E now have proposed design artifacts:

1. **CanonicalTradeCommand v1** — proposed in [NX-IF-001](NX-IF-001-canonical-trade-command-risk-approval-contract.md); not accepted, implemented or conformance-tested.
2. **StateEvidenceVector v1 / RecoveryBarrier v1** — proposed in [NX-IF-004](NX-IF-004-state-evidence-freshness-recovery-barrier-contract.md); per-source provenance, freshness, quality, watermarks, quarantine and dependency-aware recovery gates. Not accepted, implemented or conformance-tested.
3. **ExposureSnapshot v1** — proposed in [NX-IF-002](NX-IF-002-exposure-snapshot-risk-reservation-contract.md); exclusive bucket ownership, source authority, quality, lineage and monotonic scope versions. Not accepted or implemented.
4. **RiskReservation v1** — proposed in [NX-IF-002](NX-IF-002-exposure-snapshot-risk-reservation-contract.md); durable lifecycle, atomic multi-scope capacity reservation, fencing, conservative expiry and evidence-based release. Not accepted or implemented.
5. **RiskApprovalCapability v1** — signature over command digest, scope, spec/policy versions, exposure snapshot/reservation version, halt epoch, nonce, issue/expiry and one-time consumption.
6. **ExecutionOutcomeEvent v1** — durable command/order/fill/cancel/reject/unknown transitions with native evidence and deduplication scope.
7. **ExecutionEvent / LedgerPosting v1** — proposed in [NX-IF-003](NX-IF-003-execution-event-ledger-posting-contract.md); canonical fill identity, durable outbox/inbox, atomic journal posting, corrections and projection watermark handoff. Not accepted, implemented or conformance-tested.
8. **ReconciliationStatus v1** — per-scope watermarks, discrepancies, quarantine and explicit release evidence.
9. **HaltState v1 / EmergencyActionPlan v1** — proposed in [NX-IF-005](NX-IF-005-emergency-operations-halt-risk-reduction-contract.md); scoped monotonic halt epochs, operation-class authorization, bounded emergency plans, protective-order handling and controlled resume. Not accepted, implemented or conformance-tested.

These are proposed design artifacts, not existing implemented schemas.

## 5. Required system invariants

- No risk-increasing dispatch without a valid approval bound to the exact canonical command and current policy/spec/state versions.
- Risk approval and reservation are durable and recoverable; ambiguous dispatch keeps exposure reserved.
- Each open/pending/unknown exposure item is counted exactly once in the authoritative exposure snapshot.
- An order acknowledgement never creates a fill or financial posting.
- Each fill/account event is ingested and posted idempotently with immutable lineage.
- Ledger/Risk/Execution health is evaluated by per-scope watermarks and quality, not a single global healthy flag.
- Any material UNKNOWN, stale state, unreconciled discrepancy or stale halt epoch blocks risk-increasing commands for the affected scope.
- Cancel/amend/close/reduce actions follow explicit venue/account-mode semantics and cannot bypass state validation.
- Restart does not restore authorization until the full recovery barrier passes.
- AI and Strategy cannot change policy, issue approvals, mutate reservations, sign exchange requests or bypass Execution.

## 6. Bounded follow-up work packages

| Work package | Scope | Exit criteria |
|---|---|---|
| WP-A Command & approval contracts | NX-IF-001 design draft exists | Owner/security decisions, canonicalization/digest selection, golden vectors and conformance evidence remain open |
| WP-B Exposure & reservation | NX-IF-002 design draft published | Owner decisions, persistence/transaction design, schema conformance and concurrency/fault evidence remain open |
| WP-C Execution ↔ Ledger | [NX-IF-003](NX-IF-003-execution-event-ledger-posting-contract.md) design draft exists | Owner accounting decisions, schema/transaction selection, golden accounting fixtures, inbox/outbox conformance, replay and fault evidence remain open |
| WP-D Freshness & recovery | [NX-IF-004](NX-IF-004-state-evidence-freshness-recovery-barrier-contract.md): StateEvidenceVector, FreshnessPolicy, RecoveryCase and RecoveryBarrier | Owner thresholds/venue scope, policy and persistence decisions, schema conformance, restart/replay/reconciliation fault evidence |
| WP-E Emergency operations | [NX-IF-005](NX-IF-005-emergency-operations-halt-risk-reduction-contract.md): HaltState, command classification, EmergencyActionPlan, operator authorization and resume | Owner roles/thresholds, venue/account-mode capability certification, persistence/control-plane decisions, race/fault and adapter conformance evidence |

No additional broad research is required to close these design gaps; targeted official venue documentation is needed only for the initially selected venue/account-mode capabilities.

## 7. Owner decisions still required

The consolidated, gate-based owner decision register is [NX-OWNER-DECISIONS-001](NX-OWNER-DECISIONS-001-critical-owner-decision-register.md). It groups the cross-contract decisions into OD-01..OD-15, identifies when each is required (G0–G3), proposes conservative starting points and defines safe behavior while unresolved. The following are the cross-cutting decisions already visible in this review:

1. Initial venue/account-mode shortlist and whether first release is single-account/single-venue.
2. Whether Risk Engine and Command Coordinator share a transactional store or use a separately specified reservation protocol.
3. Initial portfolio scope and cross-account collateral aggregation policy.
4. Approved valuation/mark/FX hierarchy and conservative haircuts.
5. Operator roles and dual-control thresholds for halt/resume and manual reconciliation.
6. Retention and recovery objectives for command, raw evidence, journal and audit stores.

No numeric risk limits are invented. UNCONFIGURED remains a hard block for live risk-increasing activity. The register is not owner approval; each selected option must be explicitly accepted and reflected in the relevant ADR/specification.

## 8. Review disposition and verification limits

**Disposition: BLOCKED. WP-A (NX-IF-001), WP-B (NX-IF-002), WP-C (NX-IF-003), WP-D (NX-IF-004) and WP-E (NX-IF-005) design drafts published; all require owner/security/accounting/operations review, owner decisions and conformance evidence. Interface readiness remains BLOCKED until the required owner decisions and conformance evidence are complete.**

Verified in this review:
- all reviewed source documents were fetched from the named branch;
- the six specifications, five ADRs and proposed NX-IF-001..005 contracts exist in the branch;
- NX-IF-005 defines scoped halt epochs, command-class authorization, protective-order handling, bounded emergency plans and privileged resume; it remains a proposed contract with no implementation or venue certification;
- NX-IF-004 defines a composable evidence vector and scoped recovery barrier; it consumes NX-ADR-004 public market-data state and NX-ADR-002 / ТЗ-NX-004/006 private execution and reconciliation evidence without replacing their protocol rules;
- Draft PR #3 was created and its response confirmed `open`, `draft=true`, `merged=false`, with base `docs/wp-b-exposure-reservations` and head `docs/wp-c-execution-ledger-handoff`;
- WP-C branch was compared against `docs/wp-b-exposure-reservations`: base `7a44dccf33222f1487832bb6fee0b8b7cd492ce5`, head `8acabe263b110cbcdc431a458c2be80fa048bf1b` at the time of comparison, 10 commits ahead and 0 behind; the file-level diff contained the NX-IF-003 contract and its integration updates.

Not verified:
- CI, tests, builds, benchmarks or runtime behavior;
- any schema implementation or cross-service conformance.
No source code, exchange connection, credentials, risk limits, live trading, PR merge or default-branch change was performed.

## 9. References

- NX-ARCH-001 — Target Architecture & Deployment Topology.
- NX-ADR-001..005 — canonical events, execution integrity, simulation, recovery and instrument arithmetic.
- ТЗ-NX-001..006 — market data, order flow, quant, execution, risk and ledger.
- NX-SEC-001 — Threat Model & Credential Isolation.
- NX-RESEARCH-002 — Market Data & Exchange Adapter Audit.
