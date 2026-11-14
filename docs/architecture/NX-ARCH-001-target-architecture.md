# NX-ARCH-001 — Target Architecture & Deployment Topology

**Status:** PROPOSED — owner review required  
**Version:** 0.1  
**Date:** 2026-11-14  
**Scope:** logical architecture, trust boundaries, runtime responsibilities, data ownership, critical flows, failure isolation and deployment decision points for NEXUS Crypto v1.  
**Authority:** synthesis of the current project charter, NX-ADR-002..005, NX-SEC-001, ТЗ-NX-001 and NX-RESEARCH-001/002. This document does not supersede owner decisions or approve implementation.

## 1. Executive decision

NEXUS should be designed as a **modular, server-authoritative trading system with selectively isolated processes**. It should not begin as either a browser-centric application or a blanket microservice/Kubernetes deployment.

The first deployment must preserve these independent safety boundaries:

1. **Risk authority:** a deterministic Risk Engine independently validates every risk-increasing command.
2. **Execution authority:** execution dispatch and exchange signing are isolated from AI, analytics and client processes.
3. **Credential authority:** exchange credentials are held by a vault/signing boundary; no client, strategy or AI component receives raw secrets.
4. **Financial authority:** immutable execution/account events and exact-arithmetic ledger are the canonical source for balances, positions, fees, funding and realized P&L.
5. **Market-data authority:** ingestion and normalization run server-side; browser/Desktop disconnection cannot stop data capture, recovery or autonomous execution.

Desktop and Web are two clients of one backend and one account/portfolio state. The execution system must continue operating when both clients are closed.

## 2. Product and architecture invariants

- Initial product scope: Crypto. Initial venue list and market types remain an owner decision.
- Autonomous mode is the target operating mode, but autonomy is introduced only after read-only, paper, shadow and limited-live gates.
- All risk-increasing commands are fail-closed when required market data, instrument metadata, account state, risk state or execution state is stale, invalid, incomplete or unknown.
- AI Orchestrator may research, rank, explain and submit typed proposals. It cannot sign, hold exchange secrets, bypass Risk Engine or directly dispatch exchange orders.
- Risk approval is bound to the exact immutable command payload, account, instrument, size, limits, expiry and policy version. Any payload mutation invalidates approval.
- Execution acknowledgements are not fills. Ambiguous outcomes become OUTCOME_UNKNOWN and require reconciliation; never blindly resend.
- Canonical prices, quantities, fees, balances, margin and P&L use exact decimal/fixed-point/integer representations. Floating point may be used only for non-authoritative analytics where explicitly permitted.
- Historical orders, fills and ledger events retain instrument-spec and policy versions.
- Browser/Desktop state is a view/cache, not the authoritative trading state.
- No live trading, real credentials, order placement, or risk-limit changes are authorized by this architecture proposal.

## 3. Logical architecture

### 3.1 Client and access layer

**Web Client** and **Desktop Client** share the same public API and realtime gateway.

Responsibilities:
- authentication UX, MFA/step-up flows and session lifecycle;
- charting, order-flow visualization, strategy configuration and portfolio presentation;
- explicit user commands, alerts and operator controls;
- client-side caching and reconnect/resubscribe.

Non-responsibilities:
- no authoritative order lifecycle, ledger, risk calculation or autonomous scheduler;
- no exchange API secrets or signing;
- no assumption that the client remains online for automation to run.

A client reconnect must rebuild its view from backend snapshots plus ordered updates; it must not replay commands merely because a response was not observed.

### 3.2 Edge API, identity and realtime gateway

Responsibilities:
- authenticate users and devices;
- enforce RBAC/tenant/account authorization and request limits;
- expose versioned REST/gRPC-style command/query contracts (protocol choice TBD);
- provide WebSocket/SSE-style subscriptions (transport choice TBD);
- validate request shape and idempotency keys before routing;
- enforce step-up authentication for sensitive account, credential and policy changes.

The gateway is not a trust authority for trade approval. It cannot bypass Risk Engine or Execution.

### 3.3 Market Data Infrastructure

Responsibilities:
- connect to public venue feeds and REST snapshots;
- normalize trades, L1/L2 books, tickers, candles, mark/index, funding, OI and liquidation events where available;
- maintain per-stream recovery state from NX-ADR-004;
- validate sequence/checksum, freshness and snapshot/delta continuity;
- persist raw/provenance-aware and canonical events for replay;
- publish data-quality and feed-health state.

Ownership:
- owns market-data connection state, raw capture metadata, canonical market events and stream health;
- does not own account balances or private order state.

A stream that cannot establish continuity must remain degraded/unsynchronized and cannot silently be promoted to LIVE_VALID. Public market data and private account/execution streams are separate capability classes and security zones.

### 3.4 Instrument Specification Registry

Responsibilities:
- version venue-native instrument rules and internal instrument identity;
- store tick/price precision, significant-figure rules, quantity step/lot, min/max quantity/notional, contract model, multiplier, settlement currency, leverage/margin tiers, status and provenance;
- provide a validated immutable spec version to analytics, risk, execution and ledger.

Unknown mandatory fields are UNKNOWN, not guessed defaults. Unsupported contract models are non-tradable. This registry implements the data contract in NX-ADR-005; storage technology is TBD.

### 3.5 Analytics and Order Flow

Responsibilities:
- derive Footprint, Delta/CVD, DOM, Tape, volume/delta profiles, TPO and related studies from canonical data;
- expose formula/version metadata, data coverage and quality;
- support replay and deterministic recomputation where feasible.

Analytics must not mutate canonical market events or ledger state. Browser rendering may use local acceleration, but authoritative calculations used by strategies/risk must be reproducible server-side or through a separately validated deterministic library. Formula correctness requires golden datasets and independent tests before acceptance.

### 3.6 Quant & Strategy Engine

Responsibilities:
- strategy lifecycle, parameter/configuration versioning and deterministic decision context;
- historical research, walk-forward and out-of-sample evaluation;
- paper, replay and shadow decision modes;
- emit typed **TradeIntent** proposals with evidence/context, expiry and strategy version.

The Strategy Engine cannot directly submit exchange orders. A strategy output is an intent, not an authorization. It must not access signing credentials. Simulation/research runtime may be isolated from live execution runtime and must not share mutable state with production accounts.

### 3.7 Independent Risk Engine

Responsibilities:
- evaluate every risk-increasing TradeIntent or manual command;
- enforce account, instrument, exposure, leverage, concentration, loss, drawdown, rate, order-size and operational-state limits;
- validate freshness/quality of market data and account reconciliation;
- apply deterministic policies and produce an auditable decision;
- support global/account/strategy/instrument kill switches and safe shutdown.

Input is a versioned command proposal plus authoritative snapshots (account, positions, open orders, instrument spec, market quality, limits and policy version).

Output is either **DENY** with reason codes or a short-lived **RiskApproval** cryptographically/structurally bound to the exact command digest and relevant versions. Risk Engine fails closed if dependencies are unavailable or inconsistent. It must not rely on an AI-generated risk assessment.

Risk Engine must be isolated as a separately controlled runtime/process boundary from Strategy, AI and Execution. It may initially be a separately deployed process rather than a network microservice; the isolation and contract are mandatory, deployment technology is not.

### 3.8 Durable Command Coordinator and Execution Engine

Responsibilities:
- accept only RiskApproval-bound commands;
- persist command intent and outbox record before dispatch;
- assign immutable command/client-order identifiers and enforce idempotency;
- manage order state machine from NX-ADR-002;
- dispatch to venue-specific private execution adapters;
- process acknowledgements, partial fills, fills, cancels, rejects and corrections;
- classify ambiguous outcomes as OUTCOME_UNKNOWN;
- trigger reconciliation and controlled recovery.

Execution adapter capability is per venue and per market type. It must encode exact signing, request schemas, rate limits, idempotency behavior, client-order-ID support and exchange-specific order semantics. An adapter acknowledgement means accepted/received according to venue semantics, not filled.

The dispatcher and signer boundary are isolated from AI and ordinary application services. Signing should expose a narrow operation over an already risk-approved canonical payload; it must not expose raw API secrets or generic arbitrary-request signing.

### 3.9 Credential Vault and Signing Boundary

Responsibilities:
- encrypted secret storage, access policy, rotation, revocation and audit;
- narrowly scoped signing operations for approved venue/account requests;
- enforce trade-only permissions where supported; withdrawal permission must never be requested;
- protect credentials from clients, logs, analytics, strategies and AI.

The exact vault/KMS/HSM product is TBD. The architectural boundary is mandatory. Secret material must never enter repository content, application logs, telemetry, prompts or client bundles.

### 3.10 Private Account Events, Reconciliation and Financial Ledger

Private venue streams and REST reconciliation feed an account-state pipeline.

Responsibilities:
- normalize private order, fill, balance, position, fee, funding and account events;
- deduplicate fills and preserve corrections/reversals as new events;
- reconcile local state against venue snapshots at startup, reconnect and periodic intervals;
- detect manual/external orders and account drift;
- write immutable journal/ledger events with exact arithmetic and source provenance;
- derive balances, positions, realized/unrealized P&L, fees, funding and equity projections.

The ledger is the canonical financial record, not a mutable UI cache. Reconciliation discrepancies block risk-increasing activity until resolved or explicitly waived under a controlled owner-approved procedure. The precise accounting model, journal schema and treatment of exchange-specific adjustments require ТЗ-NX-006.

### 3.11 AI Orchestrator

Responsibilities:
- coordinate research, summaries, strategy explanation and supervised workflow;
- rank candidate strategies and market contexts;
- generate typed proposals for Strategy/Risk workflow;
- explain Risk Engine decisions and surface operational anomalies;
- manage tool access through least-privilege policies.

Prohibited:
- access to raw exchange credentials, vault APIs or signing keys;
- direct private exchange API access;
- direct order dispatch;
- modifying risk policy or limits;
- overriding DENY, stale-data blocks, kill switches or reconciliation blocks;
- treating its own output as RiskApproval.

AI output is untrusted input. All values must be schema-validated and independently checked by deterministic components.

### 3.12 Observability and Operations

Cross-cutting capabilities:
- structured logs, metrics, traces and audit events with correlation IDs;
- health and data-quality dashboards;
- alerting for stale feeds, sequence gaps, unknown order outcomes, reconciliation drift, risk denials, signer/vault anomalies and kill-switch activation;
- backups, restore verification, key rotation and incident response;
- deployment configuration and policy version tracking.

Audit records must be tamper-evident and must exclude secrets. Operational telemetry is not a substitute for immutable financial records.

## 4. Trust boundaries and failure domains

| Boundary | Inside | Outside / untrusted | Required control |
|---|---|---|---|
| TB-1 Client | Web/Desktop session | Browser extensions, local device, network | MFA, short-lived sessions, RBAC, request validation |
| TB-2 Public market data | Feed adapters and normalizer | Venue public endpoints, network | schema validation, sequence/freshness checks, rate limits |
| TB-3 Private venue connectivity | Private adapter runtime | Venue private API and network | isolated egress, scoped credentials, signed requests, reconciliation |
| TB-4 Risk authority | Risk Engine and policy bundle | AI, strategies, gateway, execution caller | independent deterministic evaluation, signed/bound approval |
| TB-5 Signing authority | Vault and signer | all application and client processes | narrow signing API, policy checks, audit, rotation |
| TB-6 Financial record | Ledger and reconciliation | exchange snapshots, external/manual activity | append-only events, exact arithmetic, deduplication, discrepancy hold |
| TB-7 AI/tooling | AI Orchestrator and allowlisted tools | model output, external content, user-provided prompts | no secrets, no signing, schema validation, allowlists |
| TB-8 Research/simulation | Historical datasets and simulation runtime | live account and execution environment | separate credentials/state, dataset provenance, no live dispatch |

A compromise or outage in one boundary must not silently grant authority in another. In particular, a compromised client or AI component cannot create an executable order without a valid RiskApproval and execution-side validation.

## 5. Canonical command and event flow

### 5.1 Risk-increasing order flow

1. Strategy Engine or authorized user creates a typed TradeIntent.
2. Command Coordinator validates schema, identity, idempotency key and instrument reference.
3. Coordinator obtains current market-quality, account, position, open-order and instrument-spec snapshots.
4. Risk Engine independently evaluates the exact proposed command and current policy.
5. On DENY, command is persisted as denied with reason codes; no dispatch occurs.
6. On approval, RiskApproval binds the canonical payload digest, account, instrument, quantity/price constraints, policy/spec versions and expiry.
7. Coordinator atomically persists the command and durable outbox record.
8. Execution Engine revalidates approval, digest, expiry, kill-switch and current operational gates.
9. Isolated signer signs the exact canonical venue request; adapter dispatches it.
10. Acknowledgement is recorded as acknowledgement only. Private events and reconciliation determine order/fill truth.
11. Fill events are deduplicated, journaled and applied to derived portfolio state.
12. Reconciliation compares local state with venue state; discrepancies trigger hold and investigation.

### 5.2 Market-data flow

Public venue feed → adapter → snapshot/sequence recovery → normalized canonical event → durable capture/event log → quality/freshness state → analytics and strategy subscriptions → client realtime gateway.

No browser-resident ring buffer is a canonical data source. Replay must preserve event provenance and deterministic ordering metadata.

### 5.3 Recovery flow

On disconnect, sequence gap, checksum mismatch, stale data or process restart:
- mark stream degraded/stale/unsynchronized;
- block dependent risk-increasing commands;
- reconnect with bounded backoff;
- fetch authoritative snapshot and bridge deltas according to venue protocol;
- validate continuity and freshness;
- publish LIVE_VALID only after recovery criteria pass;
- otherwise remain blocked and alert.

For execution ambiguity:
- mark OUTCOME_UNKNOWN;
- query venue by client order ID/order ID and reconcile open orders/fills;
- do not resend until outcome is resolved and idempotency semantics are proven.

## 6. Deployment topology — proposed baseline

### 6.1 Initial deployment shape

Use a **modular backend with a small number of separately isolated runtimes**:

- **Client tier:** Web and Desktop applications.
- **Public application tier:** API/realtime gateway and user-facing query services.
- **Core trading tier:** market-data ingestion, instrument registry, analytics/strategy runtime, command coordinator.
- **Safety tier:** independent Risk Engine runtime.
- **Execution tier:** private venue adapters and dispatcher.
- **Secrets tier:** vault/KMS and isolated signer.
- **Financial tier:** private event processor, reconciliation and ledger.
- **Data tier:** relational transactional store, append-only event/archive storage, cache/time-series/read models as justified by measured workload.
- **Operations tier:** metrics/logs/traces, alerting, backups and deployment control.

This is a logical isolation map, not a mandate for one container per box. Begin with the fewest deployable units that preserve trust boundaries, independent lifecycle and failure containment. Split services when security, scaling, availability or ownership requires it. Kubernetes, service mesh, Kafka and any named cloud provider are **not selected**.

### 6.2 Persistence responsibilities

Storage products remain TBD pending workload and operational evaluation. Required logical stores:

- transactional state for users, policies, commands, orders and outbox;
- append-only event/journal store for market and private events;
- exact financial ledger and derived portfolio read models;
- historical market-data archive/replay store;
- instrument-spec and strategy/policy version registry;
- secrets vault outside ordinary application database;
- tamper-evident audit trail.

Atomicity is required between durable command persistence and outbox creation. Event publication must be retryable and idempotent. The architecture must not assume distributed transactions across venue APIs and internal stores.

### 6.3 Network and identity

- Separate public ingress from private venue egress.
- Only execution adapters may reach private exchange endpoints; only signer may access signing material.
- Risk Engine accepts authenticated service-to-service requests and returns bounded approvals/denials.
- Workload identities are distinct per runtime; no shared all-powerful service credential.
- Encrypt network traffic and sensitive data at rest; exact cryptographic and key-management standards are specified in NX-SEC-001 implementation design.
- Egress allowlists, secret redaction and least-privilege policies are mandatory.
- Admin and credential changes require MFA/step-up and immutable audit events.

### 6.4 Availability and disaster recovery

- Market data, strategies and execution must be independently restartable.
- Startup is not permission to trade: account reconciliation, instrument specs, risk policy and feed health must reach valid states first.
- On partial dependency failure, fail closed for new risk; risk-reducing cancel/close actions require explicitly specified safe policies and cannot be assumed automatically safe.
- Backups must include transactional state, ledger, event offsets/provenance, strategy/policy versions and configuration; secrets use separate vault backup/restore procedures.
- Recovery objectives (RPO/RTO), deployment region, redundancy and retention remain owner/operations decisions and must be set before production.

## 7. Interface contracts (logical; schemas to be specified)

| Contract | Producer → Consumer | Minimum content / invariant |
|---|---|---|
| CanonicalMarketEvent | Market Data → Event Store / Analytics | venue, market type, instrument ID, channel, event/receive/process time, sequence, payload, quality, provenance |
| InstrumentSpecVersion | Registry → Risk / Execution / Ledger | immutable identity, exact price/size rules, contract and settlement semantics, version, effective time, source |
| TradeIntent | Strategy/User → Coordinator | account, strategy/version, instrument/spec version, side, order constraints, size, expiry, rationale/reference IDs |
| RiskApproval | Risk → Coordinator/Execution | command digest, scope, limits, policy version, spec version, expiry, decision ID |
| ExecutionCommand | Coordinator → Execution | immutable IDs, approved digest, canonical payload, idempotency key, deadline |
| VenueOrderEvent | Adapter → Order State | native IDs, client ID, venue status, timestamps, cumulative/last fill, fee, raw provenance |
| PrivateAccountEvent | Adapter → Reconciliation/Ledger | account, event type, native ID, exact amount/asset, source timestamp, dedupe key, correction reference |
| LedgerEntry | Reconciliation → Ledger | immutable journal ID, debit/credit postings, currency, exact amount, source event, spec and accounting-policy versions |
| OperationalState | Components → Risk / Observability | health, freshness, quality, reconciliation state, kill-switch and version metadata |

Transport format, schema registry, RPC protocol and event broker are TBD. Contracts must be versioned and backward-compatibility rules defined before implementation.

## 8. Key invariants and failure behavior

- No valid feed state → no dependent risk-increasing command.
- No authoritative instrument spec → instrument is non-tradable.
- No reconciled account state → no risk-increasing command.
- No RiskApproval bound to exact payload → no execution.
- Expired/changed approval → reject and re-evaluate.
- No durable command/outbox record → no dispatch.
- Ambiguous venue outcome → OUTCOME_UNKNOWN; reconcile, never blind resend.
- Duplicate private event → no duplicate ledger effect.
- Financial mismatch → hold affected account/instrument and alert.
- AI unavailable → deterministic strategies and manual controls may continue only under explicitly configured policy; AI is not a safety dependency.
- Risk Engine unavailable → fail closed for new risk.
- Signer/vault unavailable or suspicious → disable new orders; retain safe operational controls.
- Client unavailable → backend automation continues; client reconnect rebuilds state from backend.

Cancel/close semantics during degraded states must be separately specified per venue and risk policy. Do not assume every risk-reducing action is safe or always executable.

## 9. Alternatives considered

| Alternative | Decision | Reason |
|---|---|---|
| Browser-centric execution | Reject | client lifetime/network cannot own autonomous execution or financial truth |
| One large monolith with shared credentials | Reject | insufficient trust/failure isolation for Risk, signer and ledger |
| Microservice per domain from day one | Defer | operational overhead without measured need; modular boundaries first |
| AI with direct exchange API access | Reject | violates credential isolation and independent risk authority |
| One universal database/event platform selected now | Defer | workload, retention, replay and operational requirements not yet benchmarked |
| Kubernetes/service mesh by default | Defer | premature infrastructure commitment |
| Reuse Tradoor paper execution as live foundation | Reject | scoped source audit found simplified fills and f64 financial arithmetic; insufficient execution/ledger semantics |

## 10. Dependencies and traceability

- NX-ADR-002: execution lifecycle, durable outbox, idempotency and reconciliation.
- NX-ADR-003: simulation fidelity, research modes and validation.
- NX-ADR-004: market-data stream recovery and quality.
- NX-ADR-005: instrument metadata and exact arithmetic.
- NX-SEC-001: threat model, credential isolation, identity and incident controls.
- ТЗ-NX-001: public market-data ingestion and recovery.
- NX-RESEARCH-001: simulation landscape and fidelity limitations.
- NX-RESEARCH-002: Tradoor market-data, order-flow, paper execution, venue metadata and licensing findings.

NX-ADR-001 (Unified Market Event Contract) is still missing from the branch and remains a prerequisite to finalize canonical event schemas. NX-ADR-006 and detailed specs for Order Flow, Quant, Execution, Risk and Ledger remain outstanding.

## 11. Owner decisions required before implementation

### 11.1 Accepted v1 scope constraints (owner-directed, 2026-11-14)

The owner delegated conservative technical baseline choices to the technical lead. The following constraints are accepted for the v1 architecture baseline and are also recorded in [NX-OWNER-DECISIONS-001](NX-OWNER-DECISIONS-001-critical-owner-decision-register.md):

1. **One venue and one dedicated account/subaccount.** No multi-venue execution, cross-venue collateral or portfolio-wide cross-venue aggregation in v1.
2. **Account/subaccount risk boundary.** This is the initial authoritative hard-limit, exposure and reservation scope. Strategy/instrument limits may be narrower child constraints. Unconfigured parent scopes fail closed.
3. **Server-authoritative autonomous runtime.** Market data, execution, Risk, Ledger and recovery run independently of client sessions.
4. **One shared backend and authoritative state for Desktop + Web.** Both are clients, not separate trading systems; closing both clients does not stop autonomous execution.

These decisions reduce the first-release failure domain. They do not choose a venue, product family, account mode, deployment provider/region, storage technology, numeric risk limits or production availability objectives.

### 11.2 Remaining decisions



1. Initial venue and market type. Select only after jurisdiction/account eligibility and official API/capability evidence; options remain out of v1 scope unless separately approved.
2. Exact dedicated account/subaccount model, account mode and operator identity model for the selected venue.
3. Deployment ownership and target environment (self-hosted, cloud, hybrid), region and availability expectations.
4. Recovery objectives (RPO/RTO), data retention and backup policy.
5. Initial data scale: symbols, depth, event throughput, replay horizon and expected concurrent charts/clients.
6. Authentication and identity provider expectations.
7. Operator policy for cancel/close actions during degraded market data, Risk outage or reconciliation mismatch.
8. Whether any external users/tenants are in scope; current proposal assumes a personal system and does not design multi-tenant isolation as a requirement.
9. Priority between fastest first safe paper release and broader venue coverage.

Remaining decisions are deliberately not guessed. They affect deployment sizing, operational cost and detailed acceptance criteria, but do not invalidate the accepted v1 safety boundaries above.

## 12. Acceptance criteria for architecture review

- [ ] Every logical component has one accountable responsibility and explicit non-responsibilities.
- [ ] AI, Risk, signer, execution and ledger trust boundaries are independently described.
- [ ] Desktop/Web are clients of one server-authoritative state; automation survives client shutdown.
- [ ] Every risk-increasing command follows the RiskApproval-bound durable-outbox path.
- [ ] Unknown order outcomes and restart/reconnect reconciliation are covered.
- [ ] Market-data quality/recovery gates are connected to risk admission.
- [ ] Exact arithmetic and instrument-spec versioning are preserved across execution and ledger.
- [ ] Data ownership, persistence responsibilities and event provenance are defined.
- [ ] Failure modes, safe defaults, observability, backup and recovery are specified.
- [ ] TBD technology choices are explicit and not disguised as decisions.
- [ ] Related ADRs/specs are consistent and owner decisions are tracked.
- [ ] Owner review and architecture readiness gate are recorded before implementation.

## 13. Verification status and limitations

This is a **design proposal**, not an implemented architecture. No service, database, broker, vault, signer, exchange adapter or deployment platform is selected or integrated by this document. No NEXUS build, runtime, security, load, recovery or benchmark test is claimed. Source observations are limited to the scopes and exact revisions recorded in NX-RESEARCH-001/002; they are not a full audit of all upstream branches.

**Current status remains: Prototype Readiness BLOCKED.** Owner approval, NX-ADR-001, remaining specifications, evidence registers and readiness review are still required.
