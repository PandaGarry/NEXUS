# ТЗ-NX-004 — Autonomous Execution Engine

**Status:** PROPOSED — owner review required  
**Version:** 0.1  
**Date:** 2026-11-14  
**Scope:** private exchange connectivity, durable order command processing, order lifecycle, execution event ingestion, reconciliation and operational recovery for NEXUS Crypto v1.  
**Dependencies:** NX-ADR-001, NX-ADR-002, NX-ADR-004, NX-ADR-005, NX-ARCH-001, NX-SEC-001, ТЗ-NX-001, ТЗ-NX-005, ТЗ-NX-006.  
**Implementation:** NOT STARTED.

## 1. Purpose

Define an autonomous execution subsystem that can safely translate independently approved commands into exchange requests, preserve every command and outcome durably, ingest fills and account events, and reconcile local state against venue evidence.

The engine must assume network ambiguity, asynchronous exchange behavior, partial fills, duplicate/out-of-order messages, process restarts, rate limits and venue-specific retention. Its primary safety objective is not to maximize order throughput; it is to prevent untracked, duplicated or unauthorized exposure and to make uncertainty explicit and contained.

## 2. Scope

In scope:
- authenticated private exchange adapters and capability contracts;
- durable command acceptance, transactional outbox and dispatch;
- immutable order/command/client identifiers and idempotency scopes;
- order, cancel and amend state machines;
- private order/execution/account event ingestion;
- exact order/fill normalization and immutable execution records;
- reconciliation of orders, fills, balances and positions;
- startup, reconnect, timeout and failure recovery;
- rate-limit, circuit-breaker and kill-switch enforcement;
- credential/signing isolation and execution audit trail;
- adapter certification and operational monitoring.

Out of scope:
- strategy generation or market prediction;
- risk policy authoring or risk approval (ТЗ-NX-005);
- authoritative portfolio accounting and P&L (ТЗ-NX-006);
- public market-data ingestion (ТЗ-NX-001);
- UI-specific order-entry behavior;
- withdrawal, transfer, wallet management or any asset movement outside trading;
- unattended live authorization or a claim that any exchange adapter is already implemented.

## 3. Non-negotiable invariants

1. No exchange command is dispatched without a valid, scoped, unexpired Risk Engine approval bound to the exact command payload.
2. No strategy, AI component, browser client or desktop client has direct access to private exchange credentials or signing operations.
3. No command is sent before its immutable intent and outbox record are durably committed.
4. A timeout or lost response is not evidence of rejection. Ambiguous outcomes become UNKNOWN and are reconciled before any retry that could duplicate exposure.
5. An acknowledgement is not a fill. Only normalized execution evidence creates a fill record.
6. A cancel request is not a cancellation. Only authoritative venue state confirms cancellation; fills may race with cancellation.
7. Duplicate events cannot duplicate fills, fees or ledger effects.
8. Exact price, quantity, fee and currency semantics follow NX-ADR-005; unknown instrument rules block dispatch.
9. Any unresolved reconciliation discrepancy, stale account state, private-stream integrity loss or risk-service outage blocks new risk-increasing commands.
10. Every external side effect and state transition is reconstructible from immutable audit evidence.
11. Kill switch and account-level halt cannot be bypassed by retries, AI instructions or alternate clients.
12. No exactly-once execution guarantee is claimed across an external exchange boundary.

## 4. Trust boundaries and components

Logical modules (not a mandate for one microservice per module):
- **Command Intake:** accepts canonical commands only from authenticated internal callers.
- **Approval Validator:** verifies signed Risk Engine approval, payload digest, account/instrument scope, policy version, expiry and one-time use.
- **Durable Command Store + Outbox:** commits intent, approval reference and dispatch record atomically.
- **Dispatcher:** leases eligible outbox records and performs bounded network dispatch.
- **Venue Adapter:** owns venue-specific serialization, signing request construction, endpoint semantics, rate limits and normalization.
- **Private Event Gateway:** maintains private streams and captures raw event evidence.
- **Order State Projector:** applies validated transitions to canonical order state.
- **Reconciliation Worker:** compares local state with venue REST/WS snapshots and history.
- **Execution Health Controller:** manages account/venue circuit states and kill-switch policy.
- **Audit/Telemetry:** stores immutable event lineage and operational evidence.

The signing boundary should be a dedicated least-privilege component or vault-backed adapter boundary. It accepts only approved, canonical payloads and cannot create or modify trading intent. The AI Orchestrator cannot call it directly.

## 5. Canonical command contract

The canonical command envelope must include:
- `nexus_command_id` — globally unique immutable ID;
- `nexus_order_id` — immutable NEXUS order identity (for create; referenced for amend/cancel);
- `command_type` — CREATE, AMEND, CANCEL, or separately approved control command;
- account ID/reference, venue, market type and native instrument ID;
- internal instrument ID and immutable Instrument Specification version;
- exact price/quantity/trigger fields and explicit units/currencies;
- side, order type, time-in-force, reduce-only/close-position semantics where applicable;
- canonical payload digest and schema version;
- strategy/intent/evaluation correlation IDs where applicable;
- Risk Engine approval ID, policy version, approval signature and approved payload digest;
- creation time, not-after deadline and idempotency scope;
- actor/service identity and authorization context.

All decimals are transmitted as canonical decimal strings or integer ticks/lots according to the adapter contract. Binary floating-point is not accepted as the authoritative order representation.

An approval is invalid if any execution-relevant field differs from the approved payload, including account, instrument, side, quantity, price, trigger, order type, time-in-force, reduce-only flag or expiry.

## 6. Identity and idempotency

NEXUS maintains separate immutable identifiers:
- `nexus_command_id`: one logical create/amend/cancel operation;
- `nexus_order_id`: one logical order lifecycle;
- `client_order_id`: venue-specific correlation ID;
- `venue_order_id`: exchange-assigned order ID;
- `venue_execution_id`: exchange-assigned execution/fill identity.

Requirements:
- IDs are generated and persisted before dispatch.
- Client IDs follow each venue's allowed format, length and uniqueness scope.
- Internal uniqueness is enforced by NEXUS and is never delegated to the venue.
- Reusing a venue client ID after terminal status is not assumed safe; adapter policy must reflect current documented venue semantics.
- An amend/cancel command has its own command ID and references the target order.
- Retries of a proven-safe idempotent request reuse the same persisted command and idempotency key; they do not create a new logical command.
- A new logical order always receives a new NEXUS order and command ID.
- Venue idempotency guarantees are recorded per endpoint, account mode and product type, including retention and duplicate response behavior.

The system must not infer idempotency merely because a venue accepts a client-order identifier.

## 7. Durable intake and transactional outbox

Command acceptance sequence:
1. Authenticate caller and authorize account/operation scope.
2. Validate schema, deadline, instrument status and exact tick/lot/notional rules.
3. Verify current account/venue execution health and no halt/kill switch.
4. Verify Risk Engine approval signature, payload digest, scope, policy version, expiry and replay protection.
5. In one durable database transaction, persist the immutable command, order aggregate/event, approval reference and outbox record.
6. Return an internal durable-acceptance receipt. This receipt means NEXUS accepted responsibility for processing; it does not mean the exchange accepted the order.
7. Dispatcher claims the outbox record using a lease/fencing token and records attempt metadata before network I/O.
8. Adapter signs and dispatches only the exact committed payload.
9. Persist transport result and raw response. Classify the result as definitive accepted, definitive rejected, or ambiguous.
10. Consume private events and reconcile before advancing the canonical state where venue semantics require it.

Outbox guarantees durable at-least-once processing attempts. It does not guarantee exactly-once exchange effects. Lease expiry must not permit concurrent duplicate dispatch; stale workers are fenced from committing newer state.

## 8. Order and command state machines

### 8.1 Order lifecycle

Canonical states:
- CREATED
- VALIDATED
- RISK_APPROVED
- PERSISTED
- DISPATCH_PENDING
- DISPATCHED
- ACKNOWLEDGED
- WORKING
- PARTIALLY_FILLED
- FILLED
- CANCEL_PENDING
- CANCELED
- REJECTED
- EXPIRED
- OUTCOME_UNKNOWN
- RECONCILIATION_REQUIRED
- QUARANTINED

Rules:
- State transitions are append-only, versioned and validated.
- ACKNOWLEDGED means only that the venue has acknowledged/accepted the request according to its endpoint semantics.
- WORKING requires evidence that the order is live/resting where the venue exposes that state.
- FILLED requires execution quantity to satisfy the venue-normalized terminal semantics; cumulative quantity alone must be reconciled against executions.
- PARTIALLY_FILLED can transition to WORKING, CANCEL_PENDING, CANCELED, FILLED, OUTCOME_UNKNOWN or RECONCILIATION_REQUIRED.
- Cancel/fill races must preserve all fills received before or after cancel acknowledgement.
- REJECTED is allowed only with definitive venue rejection or pre-dispatch local rejection; transport ambiguity is not rejection.
- EXPIRED must identify whether expiration was local-before-dispatch or venue-confirmed.
- OUTCOME_UNKNOWN and RECONCILIATION_REQUIRED block duplicate create dispatch.
- QUARANTINED blocks new risk-increasing activity for the affected scope until explicit resolution.
- Terminal states are not overwritten; corrections and busts are new linked events.

### 8.2 Command lifecycle

Each command has its own lifecycle:
- RECEIVED
- VALIDATING
- REJECTED_LOCAL
- APPROVAL_VERIFIED
- PERSISTED
- READY_TO_DISPATCH
- DISPATCH_ATTEMPTED
- ACKNOWLEDGED
- REJECTED_BY_VENUE
- OUTCOME_UNKNOWN
- RECONCILING
- RESOLVED

A cancel command resolving as accepted does not imply the target order is canceled. The order lifecycle is updated only from authoritative order/execution evidence.

### 8.3 Amend semantics

Amend may be implemented by native amend or cancel-replace depending on venue capability. The adapter must declare:
- atomicity/replace semantics;
- whether priority is lost;
- whether quantity reduction/increase is allowed;
- whether fills may occur during amend;
- how the old/new venue order IDs are correlated;
- ambiguous outcome recovery.

If the venue lacks a safe atomic amend operation, NEXUS must model cancel-replace as two linked commands with explicit exposure and race handling. It must not silently emulate atomicity.

## 9. Ambiguous outcomes and retry policy

Ambiguity cases include timeout, connection reset after request write, gateway 5xx, malformed response, process crash after send, lost acknowledgement and private stream disconnect.

Required handling:
1. Mark command/order OUTCOME_UNKNOWN.
2. Freeze retry of any create that could increase exposure.
3. Query by venue order ID/client ID where supported.
4. Inspect private order and execution streams with overlap.
5. Query order history and executions using venue-supported time/cursor windows.
6. Reconcile open orders, fills, balances and positions.
7. Resolve only when authoritative evidence establishes accepted, rejected, filled, canceled or absent.
8. If the venue's query/history retention or eventual consistency prevents resolution, quarantine and require operator/owner workflow; do not guess.

A retry is allowed only if:
- evidence proves the original request never left the trusted dispatch boundary or was definitively rejected before venue acceptance; or
- venue documentation guarantees safe idempotency for the exact endpoint and the same persisted idempotency identity is reused; and
- the Risk Engine approval remains valid and all health gates pass.

Backoff is bounded, jittered and endpoint-specific. Retrying must not exceed venue/account rate limits or outlive command expiry.

## 10. Private events, fills and normalization

Adapters must preserve raw request/response and private event payloads with:
- venue, account scope, endpoint/channel and connection generation;
- venue event/transaction timestamps with original units;
- local receive and processing timestamps;
- raw payload hash and secure raw-payload reference;
- native order/client/execution IDs;
- event type, status, correction/bust indicator;
- normalized instrument identity and spec version;
- exact execution price, quantity, fee amount/currency and liquidity role when supplied;
- source sequence/update ID where available.

Execution identity:
- Prefer documented venue execution/trade ID within its documented uniqueness scope.
- If no stable ID exists, use a venue-specific documented composite key and mark confidence/limitations.
- Never deduplicate only by price, size and timestamp without a venue-specific proof.
- Corrections, trade busts and fee adjustments are new linked events; never mutate original evidence.

One order may produce many execution records. The system must preserve each fill, cumulative quantities, remaining quantity and fee currency. Unknown fields remain UNKNOWN, not zero.

## 11. Reconciliation engine

Reconciliation is continuous and event-triggered, not merely a startup task.

Triggers:
- process start;
- private stream connect/reconnect or generation change;
- sequence gap, dropped-message suspicion or stale heartbeat;
- ambiguous create/amend/cancel outcome;
- unexpected order/fill/position event;
- periodic account checkpoint;
- operator-initiated reconciliation;
- before resuming after HALTED/QUARANTINED.

Evidence sources:
- persisted NEXUS commands/orders/outbox;
- venue open orders and per-order query;
- order history;
- execution/trade history;
- balances and positions;
- fee/funding/account transaction history;
- private stream offsets, sequence/update IDs and connection generation.

Requirements:
- Use overlapping query windows and stable cursors/IDs to handle pagination, clock skew and eventual consistency.
- Persist request parameters, response hashes, cursor, adapter version, retrieval time and reconciliation watermark.
- Compare venue state with NEXUS state at a defined consistency boundary.
- Detect external/manual orders and positions; classify them as EXTERNAL and do not silently bind to a strategy.
- Distinguish venue truth, execution truth and NEXUS command intent until differences are resolved.
- Missing historical records outside venue retention must be recorded as a limitation; never infer no fill from an empty expired query.
- Unresolved differences create a discrepancy record and halt affected risk-increasing activity.
- Resume requires a clean reconciliation result or an explicitly approved, scoped exception that cannot suppress unknown exposure.

## 12. Account and venue health state

Per account + venue + product scope, maintain:
- DISCONNECTED
- CONNECTING
- AUTHENTICATING
- SUBSCRIBING
- SNAPSHOT_REQUIRED
- SYNCHRONIZING
- HEALTHY
- DEGRADED
- HALTED
- QUARANTINED

HEALTHY requires valid authentication, current private streams or an approved fallback, fresh account/order/position snapshots, no unresolved critical discrepancy, functioning rate-limit state and a healthy Risk Engine approval path.

A stream disconnect or gap moves the scope to DEGRADED/HALTED according to impact. After reconnect, subscriptions alone do not restore HEALTHY: snapshot/history reconciliation and event continuity checks are required.

## 13. Risk approval and kill switch integration

- Risk Engine approval is bound cryptographically to the exact canonical payload digest, account, instrument, operation, max quantity/notional/exposure, policy version and expiry.
- Approval is single-use or has a rigorously defined bounded-use scope; replay is rejected.
- Any payload change requires new approval.
- Approval is revalidated immediately before dispatch.
- Risk Engine unavailable, stale approval, policy mismatch, account halt, stale position snapshot or reconciliation hold means no risk-increasing dispatch.
- Reduce-only/close commands are not automatically exempt: their semantics must be verified against venue position mode and current position state.
- Kill switch immediately blocks new risk-increasing commands and prevents queued outbox commands from dispatching.
- Cancel-all, reduce-only or emergency actions follow a separately approved playbook. No assumption is made that a cancel-all request succeeded.
- Kill-switch state is durable, monotonic until authorized reset, and audited. Strategy/AI cannot reset it.

## 14. Rate limits, retries and circuit breakers

Each adapter maintains versioned limits by endpoint, account/subaccount, instrument/product and IP/connection where the venue defines them.

Requirements:
- centralized coordination across workers/replicas sharing the same account or API key;
- parse rate-limit headers/codes and update local budget;
- prioritize emergency cancel/reduce and reconciliation queries under an approved policy;
- bounded exponential backoff with jitter for retryable idempotent requests;
- no automatic retry for ambiguous non-idempotent create;
- circuit breaker on repeated transport/auth/rate-limit failures;
- credential-expiry and clock-skew alarms;
- adapter must not assume one venue's limit scope applies to another endpoint.

## 15. Credential and signing security

- API keys are trade/read only, withdrawal disabled; use IP allowlisting where supported.
- Secrets reside in vault/KMS/HSM-backed storage, never in source, desktop/browser storage, strategy artifacts, prompts, logs or ordinary database rows.
- Signing boundary exposes a narrow operation requiring validated approval; it cannot sign arbitrary caller-provided payloads.
- Key rotation/revocation and emergency disable are documented and tested.
- Per-account and per-venue isolation limits blast radius.
- All privileged operations require strong authentication and audited authorization.
- Production credentials are not used in development, tests, replay or screenshots.
- No real key or live order is required to implement or test the initial read-only/paper system.

## 16. Observability and incident handling

Metrics:
- outbox depth/age and lease expiries;
- commands by state, age and endpoint;
- OUTCOME_UNKNOWN and QUARANTINED counts/age;
- private stream lag, disconnects, sequence gaps and reconnects;
- order acknowledgement, fill and cancel latency;
- reconciliation drift and unresolved discrepancy age;
- duplicate event detection and correction/bust volume;
- rate-limit budget, rejects, retries and circuit-breaker state;
- approval failures, expired approvals and kill-switch state.

Every command and transition must be traceable by command/order/account correlation IDs and include actor, service version, adapter version, payload hash, approval ID, timestamps, reason and source evidence.

Incident playbooks required for:
- unknown create outcome;
- private stream loss or authentication expiry;
- position/order mismatch;
- duplicate or contradictory execution events;
- suspected credential compromise;
- exchange outage or prolonged rate limiting;
- kill-switch activation and controlled recovery.

## 17. Testing and adapter certification

No venue is certified by implementing a generic REST interface. Certification is per venue, account mode, product type, endpoint and API version.

Required test groups:
- canonical command schema and exact arithmetic;
- approval signature, payload binding, expiry and replay rejection;
- durable outbox crash points before/after commit, lease and dispatch;
- timeout-after-venue-acceptance and lost-response scenarios;
- process crash immediately after request write;
- duplicate, delayed, reordered and corrected private events;
- partial fills, cancel/fill races, amend races and reduce-only behavior;
- venue rejection, insufficient margin, invalid tick/lot, post-only rejection;
- rate limits, clock skew, auth expiry and reconnect;
- pagination, history retention and eventual consistency;
- restart recovery with pending/unknown commands;
- reconciliation mismatch and external/manual orders;
- kill switch with queued commands and concurrent workers;
- secret redaction and signer authorization boundary;
- end-to-end proof that strategy/AI/client cannot bypass Risk Engine.

Testing ladder:
1. deterministic unit/contract tests;
2. fault-injected adapter tests with recorded fixtures;
3. exchange testnet/sandbox where semantics are sufficiently representative;
4. local paper with the same command/state pipeline;
5. read-only live shadow for data/reconciliation comparison;
6. limited live only after separate owner authorization and all release gates.

Testnet success is not evidence of production liquidity, matching-engine behavior, rate-limit equivalence or financial correctness.

## 18. Acceptance criteria

- [ ] Every order command is durably persisted before dispatch.
- [ ] No dispatch occurs without valid payload-bound Risk Engine approval.
- [ ] Internal order/command IDs are immutable and unique.
- [ ] Venue client-ID behavior is documented and tested per adapter.
- [ ] Ambiguous create outcomes never trigger blind duplicate submission.
- [ ] ACKNOWLEDGED is never interpreted as FILLED.
- [ ] Cancel acknowledgement is never interpreted as confirmed CANCELED.
- [ ] Partial fills and cancel/amend races preserve all execution evidence.
- [ ] Duplicate/corrected events cannot duplicate or erase fills.
- [ ] Exact instrument rules and financial decimal semantics are enforced.
- [ ] Reconnect/restart invokes reconciliation before risk-increasing dispatch.
- [ ] External orders/positions and venue/local discrepancies are detected.
- [ ] Stale account state, stream gaps, unresolved discrepancies and Risk Engine outage fail closed.
- [ ] Kill switch blocks queued and new risk-increasing commands.
- [ ] Rate limits are coordinated across workers and retries are bounded.
- [ ] Secrets and signing authority are isolated from AI, strategy and clients.
- [ ] Adapter certification covers each supported venue/product/account mode.
- [ ] Audit trail reconstructs each command, dispatch, acknowledgement, fill and reconciliation.
- [ ] Fault-injection and end-to-end safety tests pass before any live eligibility.

## 19. Open owner decisions

1. Initial venue/account-mode/product shortlist for the first adapter certification.
2. Initial safe operating mode: local paper only, exchange testnet, or read-only live shadow combination.
3. Durable database/event-log choice and transaction boundaries, finalized in NX-ARCH-001.
4. Kill-switch playbook: cancel open orders, reduce exposure, or staged policy; each action needs venue-specific semantics and owner approval.
5. Operator intervention and quarantine resolution workflow.
6. Whether the first release supports native amend or only cancel-replace for each venue.
7. Retention period for raw private payloads, command audit and reconciliation evidence.
8. Credential vault/signing technology and deployment topology.

These decisions must be explicit before implementation of the affected capability. None authorizes live credentials or order placement.

## 20. Evidence and references

Cross-service exposure ownership and reservation handoff are specified as a proposal in [NX-IF-002](../architecture/NX-IF-002-exposure-snapshot-risk-reservation-contract.md). Execution remains authoritative for command/order/fill evidence; Risk owns the aggregate reservation projection; Ledger owns posted financial state. The interface is not implemented.

Official venue documentation consulted on 2026-11-14:
- Binance USDⓈ-M Futures REST trade API — create/query order, client order ID, order status and historical query limits: https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api
- Binance USDⓈ-M Futures User Data Streams — private order/account events and stream lifecycle: https://developers.binance.com/docs/derivatives/usds-margined-futures/user-data-streams
- Bybit V5 Place Order — orderLinkId, product-specific constraints and asynchronous order semantics: https://bybit-exchange.github.io/docs/v5/order/create-order
- Bybit V5 Execution List — multiple executions per order and execution identity/sorting considerations: https://bybit-exchange.github.io/docs/v5/order/execution
- Bybit V5 Order History — asynchronous updates and history-retention limitations: https://bybit-exchange.github.io/docs/v5/order/order-list
- OKX API v5 — clOrdId uniqueness scope, private orders channel and REST/WebSocket order operations: https://www.okx.com/docs-v5
- OKX order-operation guidance — request acknowledgement versus final cancellation/order state, batch partial success: https://www.okx.com/docs-v5/trick_en/
- Hyperliquid Exchange Endpoint — order placement, TIF and cloid: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint

Venue semantics change. Before implementation, each adapter must pin the exact current API version, endpoint documentation, account mode and product-specific rules. Search results and this specification are not a substitute for that implementation-time certification.

## 20A. Execution-to-Ledger handoff contract (WP-C)\n\nNormalized fills and execution corrections MUST follow [NX-IF-003 — Execution Event & Ledger Posting Contract](../architecture/NX-IF-003-execution-event-ledger-posting-contract.md). Execution owns immutable normalized execution facts, native identity, source evidence and the durable Ledger outbox. It MUST commit the event and outbox atomically before delivery; delivery is at-least-once and Ledger posting acknowledgement is distinct from delivery acknowledgement. A fill remains in WP-B `FILL_PENDING_LEDGER` until Ledger confirms the linked journal posting, the relevant position projection watermark and required reconciliation quality. Execution MUST NOT claim accounting balances/positions as its authority or release Risk exposure based solely on an outbox send or Ledger transport acknowledgement. Corrections and busts are new linked events; original execution evidence is never mutated.\n\n## 21. Verification status

This document is a requirements proposal. No private execution adapter, credential vault, signer, exchange account connection, order placement, reconciliation worker or runtime conformance suite has been implemented or tested in NEXUS. No live trading is authorized.

**Prototype Readiness remains BLOCKED.**
