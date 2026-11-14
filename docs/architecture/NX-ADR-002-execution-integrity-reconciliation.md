# NX-ADR-002 — Execution Integrity & Reconciliation

**Status:** PROPOSED — requires owner review  
**Date:** 2026-11-14  
**Scope:** Private exchange account connectivity, order command lifecycle, execution events, idempotency, reconciliation and restart recovery.  
**Evidence baseline:** NX-RESEARCH-002, including Tradoor source pass at `6ab38775f8f95a2b0237d8663a15405fa00465c6` and official venue API documentation cited there. This ADR defines NEXUS requirements; it does not claim an exchange adapter exists or has been tested.

## Context

A trading API is asynchronous and failure-prone. A request can reach an exchange even when the client times out before receiving its response. A WebSocket can disconnect after an order is accepted but before its acknowledgement or fill is observed. Private streams may duplicate, delay or reorder messages. Partial fills can arrive before a REST response; cancellation can race with a fill. Restarting the process must not erase knowledge of commands that may already have reached the exchange.

A successful HTTP response is not necessarily a fill. Venue client-order IDs are useful correlation keys but their uniqueness and retention rules differ. Therefore neither a transport response nor a venue order ID alone can be the authoritative NEXUS order state.

## Decision

NEXUS will use a durable, event-driven execution state machine with a transactional command outbox, immutable internal identifiers, asynchronous event ingestion and explicit reconciliation. The execution service does not decide whether an order is safe; every risk-increasing command must carry a valid approval from the independent Risk Engine.

### 1. Identity and persistence

Every order intent receives:
- immutable `nexus_order_id` (globally unique);
- immutable `nexus_command_id` for each create/amend/cancel action;
- venue-compatible `client_order_id`, generated and persisted before dispatch;
- account, venue, market type and canonical instrument identity;
- exact quantity/price and instrument-spec version;
- strategy/run correlation, risk decision ID and policy version;
- creation time, expiry/deadline and idempotency scope.

Persist the intent, risk approval reference and outbox command atomically before any network dispatch. A command is never sent directly from an uncommitted in-memory request.

### 2. Order lifecycle

The canonical lifecycle is:

`CREATED → VALIDATED → RISK_APPROVED → PERSISTED → DISPATCHED → ACKNOWLEDGED`

Possible subsequent states:
- `PARTIALLY_FILLED`
- `FILLED`
- `CANCEL_PENDING`
- `CANCELED`
- `REJECTED`
- `EXPIRED`
- `OUTCOME_UNKNOWN`
- `RECONCILIATION_REQUIRED`

Rules:
- State transitions are append-only events with validated transition rules.
- `ACKNOWLEDGED` means venue acceptance/recognition only; it does not mean filled.
- A fill is represented by one or more immutable execution records. Partial fills accumulate; they are never collapsed into a single mutable fill.
- A cancel acknowledgement does not erase prior fills. Fill/cancel races are resolved from venue order and execution evidence.
- `OUTCOME_UNKNOWN` is mandatory when dispatch may have reached the venue but no definitive result was received.
- `OUTCOME_UNKNOWN` and `RECONCILIATION_REQUIRED` block duplicate create dispatch until resolved or explicitly quarantined.
- Terminal states are not rewritten; corrections are new compensating events linked to the original evidence.

### 3. No blind resend / idempotency

- Never retry a create command after a timeout, broken connection or ambiguous 5xx solely because no response was received.
- First query by venue order ID/client order ID where supported, inspect private order/execution streams, and reconcile open orders/fills/positions.
- Retry only when the adapter can prove the original command was not accepted, or when the venue documents a safe idempotency contract and the same persisted idempotency key is reused.
- A new logical order always receives a new NEXUS order ID and command ID.
- Client-order IDs are not assumed globally unique or historically unique across venues. NEXUS uniqueness is enforced independently.

### 4. Transactional outbox and dispatch

1. Validate the order against the current Instrument Specification Registry.
2. Obtain a signed, scoped approval from the Risk Engine.
3. In one database transaction persist the order intent, approval reference and outbox command.
4. Dispatcher claims the outbox record with a lease and durable attempt metadata.
5. Before sending, confirm the approval remains valid and the account/venue circuit is not halted.
6. Dispatch exactly the persisted command payload; record request hash, attempt, timestamps and transport result.
7. Convert ambiguous transport outcomes to `OUTCOME_UNKNOWN`; never convert absence of response to rejection.
8. Consume private events and REST reconciliation into the canonical state machine.

The outbox provides durable at-least-once dispatch attempts, not magical exactly-once exchange execution. Exactly-once effects cannot be assumed across an external exchange boundary.

### 5. Execution event integrity

Each venue adapter must preserve raw payload and normalize:
- venue execution/trade ID and order ID/client order ID;
- event and transaction timestamps with original units;
- instrument identity and spec version;
- side, exact price, exact quantity, fee amount and fee currency;
- maker/taker or liquidity role where available;
- execution type/status and correction/bust semantics;
- source connection/generation and payload hash.

Deduplication uses venue-defined execution identity within its documented scope. If the venue lacks a stable execution ID, use a documented composite identity and mark confidence/limitations; do not silently deduplicate on price+size+timestamp alone.

Unknown or malformed fields remain UNKNOWN. Never fabricate fee, side, fill quantity or event time.

### 6. Reconciliation

Reconciliation is a first-class service, not a one-time startup query.

Required inputs:
- persisted NEXUS orders and command/outbox history;
- venue open orders and order query endpoints;
- recent executions/fills with overlap windows;
- balances and positions;
- account/ledger transactions, including funding and fees;
- private stream watermarks and connection generations.

Required behavior:
- At process start, account reconnect, stream gap, ambiguous dispatch and periodic checkpoints, fetch authoritative snapshots.
- Use overlapping time windows and stable IDs to cover pagination and eventual consistency.
- Compare expected vs venue state; record every difference.
- Resolve only from authoritative evidence. Otherwise quarantine the order/account state and block risk-increasing commands.
- Record reconciliation watermark, request parameters, response hashes, pagination cursor and adapter version.
- Detect external/manual orders and positions; classify them as external rather than silently adopting them into a strategy.
- Preserve venue truth and NEXUS ledger truth separately until a controlled reconciliation event resolves differences.

### 7. Failure and safety controls

- Private stream disconnect, authentication expiry, sequence gap, stale account snapshot or unresolved command ambiguity marks account execution health DEGRADED/HALTED.
- Cancel requests are themselves asynchronous commands and require reconciliation.
- Rate-limit responses use venue-specific backoff; do not retry non-idempotent create commands blindly.
- Kill switch blocks new risk-increasing orders and can invoke a separately specified cancel/reduce-only policy. It must not assume cancel-all succeeded without confirmation.
- API keys are held in a dedicated vault/signing boundary. The AI Orchestrator cannot read secrets or sign arbitrary requests.
- Keys are least-privilege (read/trade only, no withdrawal) and IP-restricted where supported.
- Logs redact credentials, signatures, passphrases, authorization headers and sensitive account identifiers.

### 8. Observability and audit

Every state transition and command records actor/service, timestamp, correlation IDs, prior/new state, reason, source evidence, risk approval, adapter version and payload hash. Metrics include outbox age, unknown outcomes, unacknowledged orders, stream lag, fill lag, reconciliation drift, rejected commands, rate limits and recovery attempts.

## Alternatives considered

- **Synchronous REST-only execution:** rejected; cannot reliably represent partial fills, disconnect ambiguity or private event timing.
- **In-memory command queue:** rejected; restart can lose commands or duplicate them.
- **Assume venue client ID provides exactly-once execution:** rejected; uniqueness/retention semantics vary and do not eliminate uncertain network outcomes.
- **Let AI call exchange APIs directly:** rejected; bypasses independent risk and durable execution controls.

## Consequences

Positive:
- Ambiguous outcomes become explicit rather than hidden.
- Restart and reconnect can recover from durable state.
- Fills, fees and funding can be reconciled to the financial ledger.
- Risk enforcement is independent from strategy and AI components.

Costs/limitations:
- Requires durable database transactions, outbox worker, private stream adapters and venue-specific reconciliation.
- Venue semantics differ; adapter certification is required per account type, product and endpoint.
- Reconciliation may temporarily halt trading when exchange evidence is delayed or inconsistent.
- No architecture can guarantee zero exchange-side uncertainty; the system must contain it safely.

## Acceptance criteria

1. Every create/amend/cancel command is durably persisted before dispatch.
2. Simulated timeout-after-acceptance never causes blind duplicate create dispatch.
3. Duplicate and out-of-order private execution events do not duplicate ledger fills.
4. Partial fills and cancel/fill races produce correct cumulative quantity and terminal state.
5. Restart with pending and unknown commands triggers reconciliation before new risk-increasing orders.
6. Private stream loss marks account state degraded and invokes bounded recovery.
7. External/manual orders and positions are detected and classified.
8. Risk Engine rejection or stale approval prevents dispatch.
9. Kill switch prevents new risk-increasing dispatch; cancel/reduce actions are independently confirmed.
10. Secrets never appear in logs, persisted command payloads or AI context.
11. Adapter conformance tests cover each venue's ID, order, fill, rate-limit, reconnect and retention semantics.
12. Audit evidence is sufficient to reconstruct every command and state transition.

## Open questions

- Initial owner-approved venue/account-mode shortlist.
- Database/event-store and transactional boundary selection in NX-ARCH-001.
- Per-venue private stream replay/retention limits and snapshot consistency.
- Exact kill-switch policy: cancel open orders, reduce exposure, or both under separately approved rules.
- Whether the first safe prototype uses exchange testnet, local paper, or both.

## Status note

PROPOSED. No private execution adapter, vault, order placement, live credential, exchange account connection or runtime conformance test is implemented or approved by this ADR.


## WP-E — Halt propagation and emergency command semantics

[NX-IF-005 — Emergency Operations, Halt & Risk-Reduction Authorization Contract ](NX-IF-005-emergency-operations-halt-risk-reduction-contract.md) defines the proposed cross-service HaltState/epoch protocol and command-class matrix. Execution MUST check the current authoritative halt epoch immediately before dispatch, stop queued risk-increasing commands on epoch advance, and preserve already-dispatched/ambiguous outcomes for reconciliation. Cancel, amend, close, reduce-only, cancel-all and flatten are distinct commands; none is assumed safe from its name or caller flags. Cancel-all uses a complete immutable target set with explicit protective-order treatment; flatten is iterative and reconciled between bounded actions. This section is a proposed design link; no controller or adapter behavior is implemented.
