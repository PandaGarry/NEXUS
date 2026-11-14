# NX-OWNER-DECISIONS-001 — Critical Owner Decision Register

**Date:** 2026-11-14  
**Status:** PROPOSED — register with owner-directed decisions OD-01, OD-04 and OD-15 accepted; remaining decisions open/deferred  
**Scope:** Phase 0 architecture closure and safe implementation-readiness gates  
**Baseline:** WP-E head `c44510810fca9de4a79d5728235b46ef6784770b`  
**Related:** NX-ARCH-REVIEW-001, NX-IF-001..005, NX-ADR-001..005, NX-ARCH-001, ТЗ-NX-001..006, NX-SEC-001

## 1. Purpose

WP-A..WP-E now have proposed interface design artifacts. The remaining blockers are no longer a lack of broad conceptual documentation; they are explicit owner choices, venue-specific evidence, implementation decisions and conformance proof.

This register consolidates the highest-impact decisions scattered across the architecture and interface contracts. It is intentionally bounded. It is not a questionnaire that must all be answered in one sitting, and it does not authorize implementation or live trading.

Each decision has:
- the choice the owner must make;
- a conservative proposed starting point for discussion;
- the gate at which it becomes mandatory;
- the safe behavior while it remains unresolved.

Recommendations are not decisions. On 2026-11-14 the owner explicitly delegated conservative technical baseline choices to the technical lead (“proceed as you think is right”). This delegation is recorded for bounded architecture-scope decisions only; it does not authorize live trading, credentials, risk-limit values, PR merges or irreversible financial actions. Accepted decisions below are limited to the selected first-release scope and previously explicit product constraints.

## 2. Decision priority and gates

- **G0 — Architecture baseline:** required to freeze the first-release scope and avoid designing incompatible interfaces.
- **G1 — Read-only / paper implementation:** required before selecting concrete persistence, adapter, simulation and operational behavior for the first safe prototype.
- **G2 — Sandbox / shadow certification:** required before connecting test or read-only private account sources and certifying venue behavior.
- **G3 — Limited live authorization:** required before any real risk-increasing order. G3 requires separate explicit approval and evidence; it is not implied by completion of G0–G2.

A decision may be deferred to a later gate only if the earlier phase can safely operate without it. Deferred items remain visible and cannot be silently defaulted.

## 3. Critical owner decisions

| ID | Decision | Proposed conservative starting point | Required by | If unresolved |
|---|---|---|---|---|
| OD-01 | First-release venue/account scope | **ACCEPTED:** one venue + one dedicated account/subaccount for v1; no multi-venue portfolio aggregation in the first release | G0 | Closed for v1 scope; exact venue selection remains OD-03 |
| OD-02 | Product and account mode | One explicitly selected product family and one documented position/account mode; defer mixed spot/derivative and cross-margin semantics | G0 | Unsupported modes remain out of scope |
| OD-03 | Venue shortlist and API capabilities | Select venue only after official API review for public data, private orders/fills, balances/positions, history retention, cancel/amend/reduce semantics and rate limits | G0/G2 | Capability remains UNKNOWN; affected operation disabled |
| OD-04 | Risk-scope hierarchy | **ACCEPTED:** account/subaccount is the sole initial hard-limit and reservation scope; strategy/instrument constraints may be narrower child constraints; no cross-venue or shared portfolio scope in v1 | G0 | Closed for v1 scope; unsupported parent scopes remain disabled |
| OD-05 | Manual/external activity | Detect and quarantine external/manual orders and positions; do not attribute them to a strategy; choose later whether manual trading is prohibited or routed through NEXUS | G1/G2 | Unknown external exposure blocks affected risk-increasing scope |
| OD-06 | Numeric risk policy | Owner must set hard limits for order notional/quantity, gross/net exposure, leverage/margin, concentration, daily loss, drawdown and halt triggers; no numeric defaults are invented | G3 | Live risk-increasing authorization is blocked |
| OD-07 | Valuation, collateral and FX | Approve mark/index/FX source hierarchy, freshness, haircuts, collateral eligibility and inverse/quanto calculation policy; initially avoid cross-currency/cross-venue collateral if not fully modeled | G1/G3 | Material valuation remains UNKNOWN/PARTIAL; risk approval blocked |
| OD-08 | Canonical serialization and signing | Select canonical serialization, digest/signature envelope, key custody, rotation and revocation only after security review and cross-language golden vectors | G1/G3 | No production RiskApprovalCapability or live signing |
| OD-09 | Durable storage and transaction boundaries | Choose storage/event-log/inbox-outbox/reservation transaction model from workload and failure requirements; prove atomic multi-scope reservation and journal posting before relying on it | G1 | No implementation may claim durable reservation or financial correctness |
| OD-10 | Freshness and recovery policy | Set source-specific thresholds, completeness/retention requirements, clock uncertainty, retry budgets and RTO/RPO per operation/scope | G1/G2 | Mandatory unconfigured evidence blocks risk-increasing authorization |
| OD-11 | Accounting policy | Approve chart of accounts, fee/funding/interest/settlement treatment, realized-P&L precedence, timezone/session boundaries, precision and residual-dust policy | G1/G2 | Ledger remains proposed; unknown categories stay suspense/UNKNOWN |
| OD-12 | Emergency operations governance | Assign halt/resume roles, step-up method, dual-control scopes, protective-order policy, permitted emergency actions and whether any offline emergency plan is allowed | G1/G3 | Halt remains available; emergency order workflows remain disabled unless specifically pre-approved |
| OD-13 | Venue emergency capabilities | Certify native amend/cancel-replace, cancel-all scope, reduce-only/close-position, partial-fill races, rate-limit priority and reconciliation behavior per exact account mode | G2/G3 | Unsupported/unknown emergency command classes remain disabled |
| OD-14 | Simulation and strategy-validation target | Select a layered approach only after matching fidelity needs: historical research, book replay, execution simulation and paper/shadow are separate acceptance targets | G1 | No profitability or execution-fidelity claim; no live strategy promotion |
| OD-15 | Deployment and availability objectives | **PARTIALLY ACCEPTED:** server-side autonomous execution; Desktop+Web are clients of one backend and authoritative state. Hosting provider/region, operator access details, backup/restore and RTO/RPO remain open | G0/G1 | Core topology invariant closed; production deployment remains blocked |



## 3A. Owner-directed decisions recorded on 2026-11-14

The owner delegated conservative technical baseline choices to the technical lead and explicitly instructed the project to proceed using professional judgment. The following bounded decisions are therefore recorded as ACCEPTED for NEXUS v1 architecture scope:

### OD-01 — Single venue and dedicated account

- **Decision:** NEXUS v1 targets exactly one exchange venue and one dedicated account or subaccount.
- **Excluded from v1 baseline:** simultaneous multi-venue execution, shared cross-venue collateral, and portfolio-wide exposure aggregation across venues.
- **Rationale:** minimizes adapter, reconciliation, instrument-specification, ledger, risk-reservation and operational failure domains while proving the complete end-to-end lifecycle.
- **Trade-off:** multi-venue diversification and consolidated portfolio controls are deferred; this is an explicit scope reduction, not a permanent product limitation.
- **Review trigger:** after one venue/account passes adapter certification, recovery, accounting and risk conformance; multi-venue scope requires a new ADR and owner review.
- **Authority:** owner instruction in the project conversation dated 2026-11-14 delegating technical choices and authorizing the conservative recommended baseline.

### OD-04 — Account/subaccount as the initial risk boundary

- **Decision:** the initial authoritative hard-limit, exposure and reservation scope is the dedicated account/subaccount. Instrument and strategy limits may be implemented as narrower child constraints, but no cross-venue/shared portfolio parent is enabled in v1.
- **Rationale:** aligns the risk reservation transaction boundary with one independently reconciled account and avoids pretending that independent venue accounts share atomic collateral or state.
- **Fail-closed rule:** any unconfigured parent scope or external activity that can affect the account's economic exposure remains UNKNOWN and blocks affected risk-increasing authorization.
- **Review trigger:** only after multi-account aggregation, valuation, collateral and atomic reservation semantics have separate evidence.

### OD-15 — Server-authoritative autonomous runtime and shared clients

- **Decision:** ACCEPTED for the core architecture: autonomous execution, market-data capture, recovery, Risk and Ledger state run server-side; Web and Desktop are clients of one backend and one authoritative account/portfolio state. Execution continues when both clients are closed.
- **Still open:** hosting provider, deployment region, operational staffing, backup/restore objectives, RPO/RTO and production availability targets.
- **Authority:** this restates the user's earlier explicit Desktop + Web and Autonomous product decisions; it does not authorize production deployment.

No other OD item is inferred to be accepted by the delegation. In particular, venue/product selection, numeric risk limits, signing algorithms, financial accounting policy, emergency operator roles and live-trading authorization remain open and fail closed.

## 4. Recommended sequencing

The following sequence minimizes rework while keeping capital safety ahead of convenience:

1. **OD-01..04:** freeze first-release venue/account/product/risk scope. This constrains data adapters, instrument registry, ledger and exposure aggregation.
2. **OD-05, OD-11:** decide external activity and financial accounting boundaries before Ledger and reconciliation implementation.
3. **OD-07, OD-09, OD-10:** decide valuation, durable transaction semantics and freshness/recovery policy before Risk and Execution implementation.
4. **OD-08:** approve cryptographic/canonicalization choices with security review and golden vectors before signing/approval implementation.
5. **OD-12..13:** define emergency governance and certify exact venue behavior before enabling emergency order workflows.
6. **OD-14..15:** select simulation and deployment targets using the agreed scope and measured requirements.
7. **OD-06:** configure numeric risk limits before any limited-live gate. These values are owner-controlled and are never inferred by the project team.

This order is a recommendation, not a rigid dependency where independent work must wait unnecessarily. Safe read-only research and pure deterministic unit/golden-test design may proceed without live risk limits.

## 5. Non-negotiable interim defaults

Until an accepted decision explicitly changes them:

- no live credentials or live order placement;
- no withdrawal/transfer permissions for trading keys;
- no live risk-increasing authorization;
- no assumed venue/account/product capability;
- no unknown-as-zero treatment for exposure, balances, fees, positions, timestamps or watermarks;
- no automatic release of reservations after timeout or local expiry if dispatch may have occurred;
- no blind retry after ambiguous venue outcome;
- no automatic cancel-all or flatten on halt;
- no bypass of Risk, Execution, Ledger reconciliation, RecoveryBarrier or audit;
- no merge of chained architecture PRs without explicit owner approval;
- no prototype readiness claim until the required gates have evidence.

## 6. Decision record format

For each OD item, the accepted record must include:

1. decision ID and exact scope;
2. selected option and rejected alternatives;
3. rationale and known trade-offs;
4. effective date and owner/approver;
5. affected ADRs/specifications/interfaces;
6. migration or compatibility impact;
7. verification evidence required and evidence references;
8. review trigger and conditions for revisiting.

A verbal preference or an unverified assumption does not close a decision. Update the relevant source-of-truth document and decision log after approval.

## 7. Exit criteria for this register

This register is considered administratively complete when:
- every OD item is ACCEPTED, DEFERRED with a named later gate, or explicitly REJECTED;
- no critical G0 decision remains ambiguous before architecture baseline freeze;
- every G3 safety decision is owner-approved before limited-live consideration;
- affected ADR/specifications and the roadmap reflect the accepted decision;
- required conformance, security, accounting and venue evidence is linked;
- unresolved items remain visible as BLOCKED/UNKNOWN rather than being silently defaulted.

## 8. Verification status

This register derives from the current WP-A..WP-E design drafts. OD-01 and OD-04 are accepted under the owner's explicit delegation dated 2026-11-14; OD-15 is partially accepted based on earlier explicit product decisions. All other choices remain open/deferred and are not inferred. No code, tests, builds, benchmarks, venue connections, credentials, orders, risk-limit changes or live trading were performed.

**Prototype Readiness remains BLOCKED pending owner decisions and evidence-based gates.**
