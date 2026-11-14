# ТЗ-NX-005 — Independent Risk Engine

**Status:** PROPOSED — owner review required  
**Version:** 0.1  
**Date:** 2026-11-14  
**Scope:** deterministic, independent pre-trade and continuous portfolio risk authorization for NEXUS Crypto v1.  
**Dependencies:** NX-ADR-001, NX-ADR-002, NX-ADR-003, NX-ADR-004, NX-ADR-005, NX-ARCH-001, NX-SEC-001, ТЗ-NX-003, ТЗ-NX-004, ТЗ-NX-006.  
**Implementation:** NOT STARTED.

## 1. Purpose and safety objective

The Risk Engine is the independent authority that decides whether a proposed operation is permitted under the active risk policy and the current verified account, portfolio and market state. It protects capital and system integrity; it is not a strategy optimizer and must not attempt to maximize returns.

The engine evaluates risk before dispatch and continuously after fills, market moves, funding, account changes and data-quality events. It must be deterministic for the same canonical inputs, policy version and calculation version. It must fail closed for risk-increasing operations whenever required evidence is missing, stale, contradictory or unreconciled.

**No live risk-increasing activity is permitted while risk limits are UNCONFIGURED.** No numeric user-specific limits are implied by this specification.

## 2. Scope

In scope:
- pre-trade authorization of canonical TradeIntent/order commands;
- deterministic exposure, margin, leverage, concentration and loss-limit calculations;
- global, account, venue, market, instrument, strategy and order-level policy evaluation;
- continuous risk monitoring and state transitions;
- risk-increasing / risk-reducing classification with explicit proof requirements;
- signed, payload-bound, expiring, replay-resistant approvals;
- kill switch, scoped halts, alerts and controlled recovery;
- risk state persistence, recovery, audit and observability;
- scenario and stress checks with explicit assumptions and limitations;
- integration contracts with Execution, Ledger, Instrument Registry and Market Data.

Out of scope:
- strategy generation, signal quality or trade profitability;
- order dispatch, signing or exchange credentials;
- authoritative accounting and P&L ownership (ТЗ-NX-006);
- exchange-specific order semantics implementation (ТЗ-NX-004);
- discretionary override by AI, strategy or execution services;
- automatic changes to owner-configured hard limits.

## 3. Non-negotiable invariants

1. Every risk-increasing command requires a valid approval bound to its exact canonical payload, account, instrument, policy version and expiry.
2. Missing, stale, contradictory or unreconciled exposure is UNKNOWN, never zero.
3. UNCONFIGURED limits mean no live risk-increasing authorization.
4. Risk Engine outage, unhealthy calculation state, stale account/position/market data, unresolved reconciliation, unknown instrument rules or active halt means deny risk-increasing activity.
5. AI Orchestrator, strategy runtime, execution adapter and clients cannot create, modify, disable or relax hard limits.
6. Risk approval does not grant permission to bypass Execution validation, authentication, venue rules or the kill switch.
7. Risk Engine never dispatches, signs or places orders and has no exchange trading credentials.
8. The exact arithmetic and instrument semantics defined by NX-ADR-005 are mandatory; floating point is not authoritative for money, price, quantity, margin or P&L.
9. A risk-reducing classification is not an automatic exemption. It requires verified position mode, current position, pending orders, venue semantics and proof that worst-case exposure cannot increase.
10. Approvals are immutable evidence. Changed payload, policy, state version, account scope or expired approval requires a new evaluation.
11. Concurrent approvals must reserve or account for aggregate pending exposure; two individually valid decisions must not jointly breach a limit.
12. Every decision is reproducible from immutable inputs, policy and calculation versions.
13. A hard-limit breach cannot be waived by an AI instruction, strategy priority, retry or alternate client.
14. Emergency controls are durable, monotonic until authorized reset and independently audited.

## 4. Trust boundaries and logical components

Logical components (not a requirement for one microservice per component):
- **Policy Registry:** versioned owner-controlled policy and limit hierarchy.
- **State Aggregator:** obtains normalized positions, balances, open orders, pending commands, fills and market state from trusted sources.
- **Exposure Calculator:** computes current, pending and post-trade exposure using exact instrument specifications.
- **Scenario Evaluator:** evaluates bounded adverse scenarios and liquidation/margin headroom.
- **Policy Evaluator:** applies deterministic hard limits, soft thresholds and scope precedence.
- **Approval Issuer:** creates signed capability only after all gates pass.
- **Risk Monitor:** reevaluates risk on relevant state changes and periodic checkpoints.
- **Halt Controller:** manages global and scoped halt states and kill-switch integration.
- **Audit/Telemetry:** persists inputs, outputs, reason codes, versions and transitions.

Risk Engine is a separate trust boundary from Strategy, AI Orchestrator, Execution and clients. It may read Ledger and market/account data but cannot mutate accounting records or issue exchange commands. The signing key for approvals is isolated from exchange signing keys. Execution validates approval authenticity and payload binding independently.

## 5. Input data contract and freshness

A risk evaluation consumes a versioned immutable `RiskEvaluationContext` containing:

- evaluation ID, request ID, correlation ID and schema version;
- canonical proposed command / TradeIntent and its cryptographic payload digest;
- account, venue, market type, instrument ID and Instrument Specification version;
- strategy identity/version and originating actor/service;
- current positions with side, size, entry basis, mark/reference price, margin mode and position mode;
- balances, collateral eligibility, liabilities, equity and margin values;
- open orders, pending outbox commands, cancel/amend states and unresolved outcomes;
- fills, fees, funding and realized/unrealized P&L references from Ledger;
- market prices, mark/index/oracle data, book/depth and quality state as required by policy;
- exchange account configuration, leverage/risk tiers and product constraints;
- timestamps, source IDs, sequence/watermark, reconciliation status and freshness budgets;
- active policy version, calculation version and risk-state version.

Each source field carries provenance, observed-at time, received-at time, processing time, quality and source version. Freshness is evaluated per field and per venue/product; one generic TTL is not sufficient.

Required source gates:
- positions and open orders are current and reconciled;
- balances/collateral and account configuration are current;
- market reference data meets the policy freshness and quality requirement;
- Instrument Specification is active, complete and version-pinned;
- Ledger has no unresolved critical discrepancy affecting equity, exposure, fees or P&L;
- pending commands and ambiguous outcomes are included in worst-case exposure;
- all required venue risk tiers and margin semantics are known.

If a field required by the selected policy is absent, stale, invalid or contradictory, evaluation returns DENY with a specific reason code. The system must not substitute last-known values beyond their explicit freshness budget or silently assume zero.

## 6. Canonical contracts

### 6.1 RiskEvaluationRequest

Required fields:
- `risk_request_id`, `schema_version`;
- canonical command type and full execution-relevant payload;
- account and instrument identity;
- payload digest;
- requested evaluation deadline;
- strategy/intent correlation identifiers;
- caller identity and authorization context.

The request must be canonicalized before hashing. Canonicalization rules define field ordering, decimal representation, omitted/null semantics, enum casing and schema version. Two semantically different commands must never share a digest.

### 6.2 RiskDecision

Required fields:
- `decision_id`, `risk_request_id`, `decision` = APPROVE / DENY / REQUIRE_REVIEW;
- stable reason codes and human-readable diagnostics;
- payload digest, account/instrument scope and command type;
- policy ID/version and calculation engine version;
- evaluated state version and source watermarks;
- current and projected exposure summaries;
- limit values, utilization and units;
- scenario results and assumptions where applicable;
- issued-at, expires-at and nonce;
- approval capability/signature only for APPROVE;
- audit evidence reference.

REQUIRE_REVIEW is not executable approval. Unknown values or warnings must not be coerced to APPROVE.

### 6.3 Approval capability

An approval capability must be cryptographically signed and bind at minimum:
- exact payload digest and canonical schema version;
- command type, account, venue, market type and instrument;
- maximum approved quantity, notional and exposure delta;
- side, order type, price/trigger bounds, time-in-force and reduce-only semantics;
- policy ID/version and calculation version;
- state version / reservation reference;
- issued-at, expiry, nonce and unique approval ID;
- permitted execution service identity and environment.

Execution must verify signature, scope, expiry, payload digest, policy status, state/reservation validity and one-time use immediately before dispatch. Any material change invalidates approval. The capability must not be reusable for a different order, account, instrument or environment.

## 7. Risk classification

Every command is classified as one of:

- **RISK_INCREASING:** can increase gross/net exposure, leverage, margin usage, liquidation risk, concentration or worst-case loss.
- **RISK_REDUCING:** proven to reduce or not increase all relevant exposure dimensions under current state and venue semantics.
- **RISK_NEUTRAL:** administrative/read-only operation with no market or account exposure effect.
- **UNKNOWN:** cannot be safely classified.

Unknown classification is treated as risk-increasing for authorization and denied if any required evidence is missing.

A reduce-only flag supplied by a caller is not sufficient proof. The classifier must verify:
- actual position mode (net/one-way vs hedge/long-short);
- current signed position and position identity;
- all open and pending orders that may consume the same reducible quantity;
- venue-specific reduce-only / close-position behavior for this product and account mode;
- whether the operation can reverse, open the opposite side or increase margin;
- worst-case fills under concurrent orders and races.

A close-position or cancel operation can still have side effects and must be validated according to its real venue semantics. Canceling orders may reduce pending exposure but does not erase already executed fills. Risk-reducing actions remain subject to authorization, rate limits, audit and safe execution controls.

## 8. Exposure and financial calculations

The engine must calculate at least:
- gross notional by instrument, venue, account and portfolio;
- net directional exposure where instruments and currencies allow meaningful aggregation;
- long/short exposure separately where hedge mode permits simultaneous sides;
- initial and maintenance margin utilization;
- leverage at position, account and portfolio scopes;
- collateral and haircut-adjusted eligible equity;
- pending-order worst-case exposure, including simultaneous fills;
- concentration by instrument, underlying, venue, strategy and correlated group;
- realized/unrealized P&L and daily loss/drawdown inputs from Ledger;
- funding and fee liabilities when known and material;
- liquidation distance/headroom using venue-specific estimates and conservative stress assumptions.

Calculations must respect linear, inverse and quanto contract models, contract multipliers, settlement currencies, tick/lot precision, fee currencies, collateral conversion and account margin mode. No universal notional or P&L formula may be applied across contract types.

All amounts carry currency and valuation source. Cross-currency aggregation requires an explicit conversion source, timestamp, quality and haircut policy. If a conversion is unavailable or stale, the affected aggregate is UNKNOWN and the relevant limit cannot PASS.

The authoritative financial ledger remains ТЗ-NX-006. Risk Engine may maintain a derived, versioned risk projection but must reconcile its inputs to Ledger and never become a second accounting source of truth.

## 9. Policy hierarchy and limits

Policy scopes:
1. system/global;
2. portfolio;
3. account;
4. venue;
5. market type;
6. instrument / underlying group;
7. strategy;
8. individual order.

The most restrictive applicable hard limit wins. A narrower scope may tighten but never relax a parent hard limit. Explicitly configured exceptions require owner authorization, bounded scope, expiry and audit; AI and strategies cannot author them.

Policy must distinguish:
- **hard limits:** deterministic deny/halt conditions;
- **soft thresholds:** warnings, reduced sizing or REQUIRE_REVIEW; never override hard limits;
- **operational gates:** data freshness, reconciliation, service health, instrument status and kill switch.

Limit dimensions include:
- max order quantity and notional;
- max gross/net exposure;
- max account/portfolio leverage;
- max initial/maintenance margin utilization;
- min liquidation headroom;
- max instrument/underlying/venue/strategy concentration;
- max correlated exposure where correlation methodology is approved;
- max daily realized loss, total daily loss and drawdown;
- max open orders and pending exposure;
- max concurrent strategies and aggregate risk reservations;
- max funding/fee burden where reliable inputs exist.

No numeric values are hard-coded by this specification. Policy state is UNCONFIGURED until the owner supplies and approves a complete policy for the intended account, product and mode. UNCONFIGURED blocks live risk-increasing operations. There is no implicit permissive default.

## 10. Concurrent approvals and reservations

Pre-trade approvals must prevent races:
- evaluation reads a consistent versioned state snapshot;
- approval atomically creates a bounded risk reservation or equivalent concurrency-control record;
- reservation accounts for worst-case pending fills and is visible to subsequent evaluations;
- reservation is bound to approval ID, payload digest, account and instrument;
- reservation is consumed, reduced or released only from authoritative command/order/fill/cancel evidence;
- expired approval does not automatically release a reservation while exchange outcome is ambiguous;
- dispatcher revalidates reservation and current risk state immediately before send;
- simultaneous fills and partial fills are projected conservatively.

If atomic reservation is unavailable, the system must serialize approvals for the affected risk scope. Optimistic evaluation without a reservation or serialization proof is not acceptable.

## 11. Scenario and stress evaluation

Policy may require bounded scenarios such as:
- adverse price gaps and mark/index divergence;
- spread widening, book-depth reduction and slippage;
- partial fills and simultaneous fills of all open orders;
- funding-rate shock and fee changes;
- volatility expansion and correlation increase;
- collateral haircut or conversion-rate shock;
- exchange outage, stale private stream and delayed cancellation;
- leverage/risk-tier changes and liquidation buffer compression.

Each scenario records inputs, shock parameters, model version, assumptions and limitations. Scenario outputs are stress estimates, not forecasts or guarantees. Correlation and liquidity models must have documented lookback, sampling, missing-data behavior and conservative fallback. If required scenario inputs are unavailable, the policy decides whether to deny or reduce permitted size; the engine must not invent a precise result.

## 12. Decision algorithm and failure behavior

Deterministic evaluation order:
1. authenticate caller and validate request schema/canonical payload;
2. validate account/venue/product authorization and environment;
3. load active immutable policy and calculation version;
4. check kill switch, halt scopes and engine health;
5. validate Instrument Specification and venue account mode;
6. validate source freshness, quality and reconciliation watermarks;
7. build current exposure including open orders and unresolved commands;
8. classify proposed command;
9. compute post-trade and worst-case exposure including concurrent reservations;
10. run applicable hard limits and required stress scenarios;
11. evaluate soft thresholds and operator-review requirements;
12. atomically reserve risk capacity;
13. issue signed, payload-bound approval or explicit denial;
14. persist full decision evidence and emit audit event.

Failure outcomes:
- malformed/unauthorized request: DENY;
- missing policy or UNCONFIGURED limits: DENY risk-increasing;
- stale/unknown data, unresolved ledger/reconciliation, unknown instrument semantics: DENY risk-increasing;
- Risk Engine unavailable or internal consistency failure: no approval; Execution must fail closed;
- hard-limit breach: DENY and optionally trigger scoped HALT according to policy;
- soft threshold: APPROVE only if policy explicitly allows; otherwise REQUIRE_REVIEW;
- timeout during approval issuance: caller receives no executable approval; query by request ID before creating a new evaluation;
- state changes after evaluation: invalidate or re-evaluate approval/reservation before dispatch.

No fail-open mode is permitted for risk-increasing commands.

## 13. Continuous monitoring and risk states

Per system, portfolio, account, venue and instrument scope maintain:
- UNCONFIGURED
- NORMAL
- WARNING
- RESTRICTED
- HALTED
- RECOVERY_PENDING
- QUARANTINED

Transitions are driven by versioned policy and evidence. Examples:
- approaching soft threshold → WARNING;
- hard limit reached or breached → RESTRICTED/HALTED per policy;
- stale account state, market data integrity loss or reconciliation discrepancy → RESTRICTED/HALTED;
- unknown exposure or inconsistent projection → QUARANTINED;
- kill switch → HALTED;
- clean recovery evidence and authorized reset → RECOVERY_PENDING then NORMAL.

The most restrictive active state across applicable scopes governs the command. State changes are durable, monotonic where safety requires, and audited. Restart does not clear HALTED or QUARANTINED. Recovery requires fresh snapshots, reconciliation, policy validity and explicit authorization where configured.

## 14. Kill switch and emergency controls

Kill-switch levels:
- global system;
- portfolio;
- account;
- venue/account;
- instrument;
- strategy.

Activation immediately:
- denies new risk-increasing approvals;
- invalidates unconsumed approvals in affected scope;
- prevents queued execution commands from dispatching;
- records actor, reason, scope, timestamp and evidence;
- emits high-priority alert.

Emergency cancel-all, reduce-only or flatten actions are separate command workflows governed by ТЗ-NX-004 and venue semantics. The Risk Engine may authorize a pre-defined emergency policy but does not execute it. It must not assume cancel-all or flatten succeeded. Exposure remains open until confirmed by executions, positions and reconciliation.

Reset requirements:
- strong operator authentication and step-up authorization;
- explicit scope and reason;
- current reconciled account/position/order state;
- no unresolved critical discrepancy;
- active policy and risk engine healthy;
- two-person approval for configured high-impact scopes;
- append-only audit event.

AI, strategies and ordinary service identities cannot activate a reset or relax a halt. They may request activation; activation policy determines whether the request is accepted.

## 15. Policy lifecycle and governance

Policy lifecycle:
- DRAFT → VALIDATED → OWNER_APPROVED → ACTIVE → SUPERSEDED / REVOKED.
- Every version is immutable and includes author, approver, scope, effective time, expiry/review date, rationale and policy digest.
- Activation is atomic and audited.
- A policy update cannot retroactively change the basis of an already dispatched order; it may invalidate pending approvals and trigger re-evaluation of open exposure.
- AI may propose a policy change as a review artifact only; it cannot approve or activate it.
- Emergency tightening may be automated only within pre-approved policy rules; automated relaxation is prohibited.

Initial account configuration must explicitly record venue, account mode, product family, margin mode, position mode, collateral set, allowed instruments, allowed order types and all required limits. Any missing mandatory field leaves that scope UNCONFIGURED.

## 16. Security and availability

- Risk Engine has no exchange API key, withdrawal capability or signing authority for exchange requests.
- Approval-signing key is separate from exchange signer and protected by KMS/HSM or equivalent managed key boundary.
- Approval verification is available to Execution independently; no shared mutable in-memory trust.
- Service-to-service authentication, least privilege, mTLS or equivalent, RBAC and audit are required.
- Policy writes require owner/operator role with MFA/step-up and immutable audit.
- Secrets, payloads and account identifiers are redacted from ordinary logs; evidence storage is access-controlled.
- Clock synchronization and monotonic deadline handling are required for expiry.
- High availability must not permit split-brain approvals or duplicate risk reservations; use consensus/transactional coordination or scoped serialization.
- Backup/restore must preserve policy versions, halt state, reservations, nonce/replay state and decision audit.
- If state consistency cannot be established after restart or failover, risk-increasing approvals remain disabled until recovery completes.

## 17. Observability and audit

Metrics:
- approvals/denials/review requests by reason and scope;
- policy version and calculation version in use;
- exposure and limit utilization by scope;
- stale/unknown input counts and age;
- pending reservation count/age and capacity utilization;
- hard/soft threshold crossings;
- risk state transitions and halt duration;
- approval expiry, replay and signature failures;
- calculation latency and deterministic replay mismatches;
- ledger/reconciliation discrepancy age;
- kill-switch activations and reset attempts.

Every decision records canonical request digest, input snapshot references, source watermarks, policy and engine versions, calculation outputs, limits, scenario assumptions, reason codes, reservation, signature metadata and actor. Audit records are append-only and sufficient to reproduce the decision without exposing secrets.

## 18. Testing strategy

Required test groups:
- golden tests for linear, inverse and quanto exposure, P&L and margin;
- exact arithmetic, tick/lot rounding and currency conversion;
- boundary tests at, below and above every hard/soft limit;
- scope inheritance and most-restrictive precedence;
- unknown/stale/missing/conflicting data always fail closed;
- open-order and simultaneous-fill worst-case exposure;
- concurrency race tests for reservations and approval issuance;
- payload mutation, wrong account/instrument, expired approval and replay rejection;
- signature tampering and key rotation;
- risk service outage, timeout, split-brain and restart recovery;
- policy activation, supersession, revocation and rollback controls;
- reduce-only classification across net/hedge modes and venue-specific semantics;
- kill switch with queued commands, active workers and concurrent approvals;
- stress scenarios and deterministic replay;
- Ledger discrepancy and reconciliation-hold propagation;
- AI/strategy/client bypass attempts;
- audit completeness, redaction and access control.

Testing ladder:
1. pure deterministic unit/golden tests;
2. contract tests against Ledger, Market Data, Instrument Registry and Execution;
3. property-based and fuzz tests for arithmetic, canonicalization and policy boundaries;
4. concurrency/fault-injection tests;
5. recorded market/account replay;
6. exchange sandbox/testnet integration for venue semantics;
7. read-only shadow evaluation with no order authority;
8. separately authorized limited-live readiness only after all gates.

A testnet or backtest pass does not prove production risk safety.

## 19. Acceptance criteria

- [ ] UNCONFIGURED policy denies all live risk-increasing commands.
- [ ] Missing or ambiguous exposure is never treated as zero.
- [ ] Every approval is signed, expiring, single-use and bound to exact payload/account/instrument/policy.
- [ ] Execution independently validates approval and reservation before dispatch.
- [ ] Concurrent approvals cannot collectively exceed configured limits.
- [ ] All applicable scopes use most-restrictive hard-limit precedence.
- [ ] Unknown/stale/unreconciled inputs and Risk Engine outage fail closed.
- [ ] Exact arithmetic and instrument-specific contract models are used.
- [ ] Open and pending orders are included in worst-case exposure.
- [ ] Reduce-only is proven against current position and venue/account mode; no caller-flag bypass.
- [ ] Daily loss, drawdown, margin, leverage, concentration and order limits have tested semantics.
- [ ] Scenario assumptions and limitations are explicit and reproducible.
- [ ] Kill switch invalidates approvals and blocks queued risk-increasing dispatch.
- [ ] Halt state, policy versions, reservations and replay protection survive restart.
- [ ] AI, strategy and client identities cannot alter limits or bypass Risk Engine.
- [ ] Every decision is auditable and deterministically reproducible.
- [ ] Contract, golden, property, concurrency and fault-injection tests pass before live eligibility.

## 20. Open owner decisions

1. Initial venue, account-mode, margin-mode and product shortlist.
2. Owner-defined hard limits and soft thresholds for each account and portfolio scope.
3. Daily loss/drawdown calculation boundary, reset timezone and treatment of transfers/fees/funding.
4. Approved collateral set, haircuts and FX conversion sources.
5. Initial correlation groups and whether correlation-based limits are enabled at launch.
6. Stress scenario parameters and policy per missing scenario input.
7. Kill-switch levels, emergency playbook and two-person reset requirements.
8. Approval TTL, reservation expiry and serialization scope.
9. Operator roles, approval workflow and incident escalation.
10. Required read-only shadow duration and evidence threshold before any later live review.

Until these are explicitly decided and approved, affected policy scopes remain UNCONFIGURED. This document does not set numeric limits or authorize live trading.

## 21. Dependencies and implementation sequence

- NX-ADR-005 supplies exact instrument/contract arithmetic and immutable spec versions.
- [NX-IF-002](../architecture/NX-IF-002-exposure-snapshot-risk-reservation-contract.md) defines the proposed authoritative ExposureSnapshot, exclusive bucket ownership, atomic reservations, fencing, lifecycle transitions and recovery semantics; it is a design draft, not an implementation.
- NX-ADR-004 and ТЗ-NX-001 supply market-data freshness and recovery quality.
- ТЗ-NX-006 supplies authoritative ledger, equity, P&L, fee and funding facts.
- ТЗ-NX-003 supplies immutable TradeIntent and strategy identity; it has no risk override.
- ТЗ-NX-004 consumes the approval capability and enforces it immediately before dispatch.
- NX-ADR-002 supplies order lifecycle, reconciliation and kill-switch integrity.
- NX-SEC-001 and NX-ARCH-001 define trust boundaries, signer isolation, identity and deployment controls.

Implementation order: policy schema and exact arithmetic contracts → state/input quality gates → exposure calculator and golden tests → policy evaluator → atomic reservations → signed approval capability → continuous monitor/halt state → Execution integration → shadow evaluation and fault-injection certification. Do not implement live order authority as part of the initial Risk Engine milestone.

## 22. Evidence and references

Official venue documentation consulted on 2026-11-14; semantics must be revalidated and pinned per adapter implementation:

- Binance USDⓈ-M Futures Position Information — signed position-risk data and current positions: https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api
- Binance USDⓈ-M Futures account/position mode and margin configuration endpoints — position mode, multi-assets mode, leverage and margin type: https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api
- Bybit V5 Get Position Info — position size, side, leverage, margin and reduce-only state; position sequence context: https://bybit-exchange.github.io/docs/v5/position
- Bybit V5 Set Leverage — product-specific leverage parameters and relationship to risk limits: https://bybit-exchange.github.io/docs/v5/position/leverage
- Bybit V5 Rate Limit — endpoint/product/account-specific limits: https://bybit-exchange.github.io/docs/v5/rate-limit
- OKX API v5 — account configuration, position mode, leverage and positions: https://www.okx.com/docs-v5
- OKX API guidance — margin/leverage scopes vary by account mode and instrument family: https://www.okx.com/docs-v5/trick_en/

These sources demonstrate that account mode, position mode, margin mode, leverage and risk constraints are venue- and product-specific. They do not provide a universal cross-exchange risk formula. NEXUS must normalize capabilities while retaining native semantics and UNKNOWN states.

## 22A. Execution-to-Ledger exposure handoff (WP-C)

Risk consumes the proposed [NX-IF-003 — Execution Event & Ledger Posting Contract](../architecture/NX-IF-003-execution-event-ledger-posting-contract.md) together with [NX-IF-002](../architecture/NX-IF-002-exposure-snapshot-risk-reservation-contract.md). A confirmed Execution fill remains `FILL_PENDING_LEDGER` until the matching Ledger journal transaction, position projection watermark and required reconciliation evidence are visible. Risk MUST transfer the filled quantity to `CONFIRMED_POSITION` atomically within a new ExposureSnapshot version; it MUST NOT infer posting from event delivery, order acknowledgement or journal commit alone when the required projection is still pending. Corrections/busts require a compensating exposure transition and re-evaluation of affected reservations/approvals.

## 23. Verification status

This is a requirements proposal only. No Risk Engine, policy registry, exposure calculator, approval signer, risk reservation, kill-switch controller or risk conformance suite has been implemented or tested in NEXUS. No account limits have been configured. No live trading is authorized.

**Prototype Readiness remains BLOCKED.**
