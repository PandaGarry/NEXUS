# NX-OWNER-DECISIONS-001 — Critical Owner Decision Register

**Date:** 2026-11-14  
**Status:** PROPOSED — OD-01/04 accepted, OD-15 partially accepted; G1 technical baselines selected for OD-08/09/10/12 under delegated technical authority; production and owner-only decisions remain open  
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
| OD-08 | Canonical serialization and signing | **G1 TECHNICAL BASELINE SELECTED:** RFC 8949 restricted deterministic CBOR; SHA-256 domain-separated digest; untagged embedded-payload four-element COSE_Sign1 with protected alg=-19 and 1–64-byte kid only, empty unprotected map, deterministic-CBOR capability payload and fixed external AAD; RFC 9864 fully specified Ed25519, reject deprecated polymorphic EdDSA (-8). Token-supplied kid/alg/issuer/audience are untrusted until verification; local bounded key registry only; public OKP/Ed25519 verifier key only. Exact libraries, non-exportable key custody, rotation/revocation and security/jurisdictional review remain gated | G1/G3 | No production RiskApprovalCapability or live signing |
| OD-09 | Durable storage and transaction boundaries | **G1 TECHNICAL BASELINE SELECTED:** PostgreSQL 18 evaluation target, one primary, service-owned schemas/roles and separate Risk/Command/Ledger local ACID transactions; no distributed transaction or automatic failover before fencing proof | G1 | No production durability or financial-correctness claim until isolation, crash, backup/restore and egress proofs pass |
| OD-10 | Freshness and recovery policy | **G1 TECHNICAL BASELINE SELECTED:** source-specific EvidenceRequirementSet/FreshnessPolicy, explicit completeness/watermarks and monotonic elapsed-time; no global TTL; unknown/unconfigured mandatory evidence fails closed. Numeric thresholds, retention, clock uncertainty and RTO/RPO remain owner/domain decisions | G1/G2 | Mandatory unconfigured evidence blocks risk-increasing authorization |
| OD-11 | Accounting policy | Approve chart of accounts, fee/funding/interest/settlement treatment, realized-P&L precedence, timezone/session boundaries, precision and residual-dust policy | G1/G2 | Ledger remains proposed; unknown categories stay suspense/UNKNOWN |
| OD-12 | Emergency operations governance | **SAFE V1 BASELINE SELECTED:** single Owner; halt is always available; resume is Owner-only with step-up and READY RecoveryBarrier; no automatic cancel-all/flatten, no offline emergency order plan; break-glass is containment-only. Identity provider/step-up mechanism and any future second-operator dual control remain open | G1/G3 | Emergency order workflows remain disabled; no automatic order or protective-order mutation |
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

No other OD item is recorded as owner-accepted. The G1 baselines for OD-08/09/10/12 below are technical-lead selections under the owner's expanded delegation, not production approvals. Venue/product selection, numeric Risk limits, accounting policy, production key custody, operator identity, emergency venue semantics and live-trading authorization remain gated and fail closed.

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


## 3B. Delegated technical baselines selected on 2026-11-14

The owner subsequently instructed the technical lead to perform the deeper project/upstream audit, resolve technical questions independently and choose the safest suitable solutions. The following bounded G1 baselines are therefore **selected by delegated technical authority**. They are not represented as owner acceptance of production risk, legal compliance, credentials, live trading or deployment.

### OD-08 — Canonical bytes, digest and approval signature

- **G1 baseline:** RFC 8949 core deterministic CBOR under the strict NEXUS profile in NX-ADR-008; command map keys are schema-defined ASCII text names only; reject non-ASCII/unknown/duplicate keys, invalid UTF-8, tags, indefinite lengths and all floats; use exact strings/typed values for financial data and signed 64-bit integers only for declared control metadata.
- **Digest:** SHA-256 over a fixed NEXUS command-domain separator and deterministic command bytes.
- **Capability signature:** COSE_Sign1 with fully specified COSE Ed25519 algorithm (-19, RFC 9864); local policy fixes alg=-19 and rejects token-selected algorithm negotiation, deprecated polymorphic EdDSA (-8), Ed448 and key/algorithm mismatch. COSE key type is public OKP / Ed25519 only. Protected kid and token-supplied issuer/audience are untrusted lookup hints until verification succeeds; candidate lookup is bounded to a local versioned registry and never dereferences token-supplied URLs. Bind lookup to locally expected issuer, audience, algorithm, purpose, validity/revocation state and registry generation; after signature verification, signed claims must match the same local context. Exactly one eligible key must resolve or fail closed. Execution receives only a 32-byte public x key; private d material remains inside Risk signing authority. Require a 64-byte Ed25519 signature. Risk signing authority is isolated and asymmetric.
- **Not selected:** exact encoder/decoder crates, key custody provider/HSM/KMS, production key ceremony, rotation windows and jurisdictional acceptance. These require exact-version security review and cross-language vectors before implementation or production.

### OD-09 — Persistence and transaction ownership

- **G1 baseline:** PostgreSQL 18 is the leading evaluation target, using one logical primary, separate service-owned schemas/roles and no shared application superuser.
- **Transaction model:** Risk reservation, Command approval-consumption/outbox and Ledger inbox/journal posting are separate local ACID transactions with explicit durable handoff and reconciliation. No distributed ACID transaction and no broker as source of truth.
- **Risk concurrency:** evaluate SERIALIZABLE plus deterministic scope-row locking, unique idempotency constraints and state-version guards; retry the entire transaction on serialization failure within a finite budget. Unknown commit is reconciled by durable identity, never blindly retried.
- **Serialization point:** Risk owns the derived exposure projection, source watermarks, scope-state version and reservation totals. Risk projection updates and reservations update the same Risk-owned scope-state record; Ledger remains journal owner and cannot write Risk state directly. All applicable pre-provisioned scope rows are processed in deterministic scope-ID order and all-scope reservations commit atomically.
- **Projection fan-out:** every projection event updates all affected pre-provisioned scope-state rows, including parent/account aggregates and changed child scopes, in one Risk transaction. Scope membership/configuration changes serialize in a privileged transaction and advance scope_config_version; stale scope-set calculations fail closed.
- **Root guard and valuation inputs:** every v1 reservation/projection transaction includes the account/root scope-state row and rechecks its scope_config_version after acquiring the full lock set. Market/index/FX/fee/collateral inputs are immutable versioned snapshots bound to the reservation/capability; market-data ticks do not rewrite scope-state rows per tick. Stale or invalid valuation inputs block dispatch.
- **Logical state versioning:** scope-state records carry scope_config_version, monotonic scope_state_version, exposure_projection_version, reservation_aggregate_version, source-watermark-vector reference/version, fencing_generation and last_transition_id; physical schema remains unselected.
- **Uniqueness:** 23505 is not blindly retried. Expected idempotency collisions are resolved in a new authoritative-primary transaction by digest equality; unrelated unique/exclusion violations fail closed.
- **Failure semantics:** stale/incomplete projection, missing scope state or unresolved primary/commit authority blocks risk-increasing approval. SQLSTATE 40001/40P01 retries the whole transaction from a fresh snapshot with bounded attempts; same request identity + same digest returns the original result, different digest is a conflict. See NX-ADR-008 §5.3 and NX-IF-002 §6.4.
- **Failover:** no automatic or active-active failover in G1. Backup/restore/PITR and old-primary fencing must be proven before any failover design can be selected.
- **Not selected:** exact PostgreSQL patch, hosting provider, replication topology, backup retention and RTO/RPO.

### OD-10 — Freshness and recovery

- **G1 baseline:** per-source/per-scope/per-operation EvidenceRequirementSet and FreshnessPolicy, explicit sequence/cursor/watermark/completeness/clock-quality evidence, monotonic elapsed-time and fail-closed UNKNOWN handling.
- No global TTL. RecoveryBarrier remains scope- and dependency-aware; process restart or socket reconnect is not readiness.
- Numeric freshness thresholds, retention, clock uncertainty, retry budgets and RTO/RPO remain source-owner/owner decisions; affected risk-increasing operation stays blocked until configured and evidenced.

### OD-12 — Emergency operations

- **V1 safe baseline:** one Owner identity; authenticated scoped halt can be requested without a trade approval; resume requires Owner step-up, reason/evidence and READY RecoveryBarrier.
- No automatic cancel-all, flatten or protective-order removal; no offline emergency order plan; emergency order workflows remain disabled until exact venue/account-mode semantics are certified.
- Break-glass is limited to halt/isolation/credential-route containment and cannot create orders, mint approvals, relax Risk limits or transfer assets.
- Dual control is not simulated with one human. If a second independent operator is later introduced, high-impact resume/emergency actions require a separately reviewed two-person policy. Identity provider and step-up mechanism remain unselected.

These choices close the technical direction for G1 design. They do not close OD-03, OD-06, OD-07, OD-11, OD-13, numeric operating thresholds, production deployment or G3 authorization.



### OD-08 standards correction — RFC 9864

A current IETF standards check found that the older COSE EdDSA identifier (-8) is polymorphic and has been deprecated by RFC 9864 (October 2025). The selected G1 profile therefore uses the fully specified COSE Ed25519 identifier **-19**. Verification rejects -8, Ed448, wrong key type/curve, algorithm/key mismatch and substitution. The protected kid is not treated as an authority by itself; issuer- and purpose-bound key-registry resolution must yield exactly one eligible key or fail closed. Exact COSE library/provider interoperability remains an open qualification gate.
