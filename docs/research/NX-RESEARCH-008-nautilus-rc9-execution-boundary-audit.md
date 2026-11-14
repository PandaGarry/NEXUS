# NX-RESEARCH-008 — NautilusTrader v2.0.0rc9 Execution Boundary Source Audit

**Status:** SOURCE-CONFIRMED CRITICAL GAPS — TEST-ONLY CANDIDATE  
**Review date:** 2026-11-14  
**Upstream baseline:** `v2.0.0rc9`, commit `da6b57aefdd62b44f675e434ffcfefca7f4025dd`  
**NEXUS baseline:** PR #10, branch `foundation/domain-kernel-reference-v0`  
**Scope:** Targeted source/documentation audit of execution routing, risk routing, cache persistence and restart dispatch state.  
**Decision class:** Research evidence only; no adoption, license or production decision.

## 1. Executive result

The exact v2.0.0rc9 source confirms the two principal architectural blockers already suspected in the earlier develop-branch assessment:

1. **No durable-before-dispatch guarantee:** execution policy explicitly says persistence enqueue failures are logged without blocking the client call; successful enqueue does not mean backing-store commit. Cache writes are best-effort and do not propagate persistence failures into command processing.
2. **RiskEngine is not a universal non-bypassable command authorization boundary:** submit routes may go through OrderEmulator or ExecutionAlgorithm instead of RiskEngine; cancel and query commands can route directly to other execution components. The exact v2.0.0rc9 docs state this routing explicitly.

A third important finding is confirmed: the execution engine's dispatched-order marker is process-local and absent after restart. The documentation states that after restart a still-INITIALIZED dispatched order can be treated like an unrouted order until later client or venue evidence resolves it. This reinforces the need for NEXUS-owned durable command identity and reconciliation before any resend.

**Recommendation:** Do not adopt NautilusTrader v2.0.0rc9 as NEXUS's autonomous execution authority. It may remain an isolated test-only runtime candidate for data, strategy replay and selected adapter behavior. Any future execution integration must be behind a NEXUS-owned durable outbox and non-bypassable gateway, and must prove that strategies and algorithms cannot access direct venue dispatch.

## 2. Immutable source identity and reviewed paths

- Upstream tag: `v2.0.0rc9`
- Commit: `da6b57aefdd62b44f675e434ffcfefca7f4025dd`
- Release: https://github.com/nautechsystems/nautilus_trader/releases/tag/v2.0.0rc9

Reviewed source paths:
- `docs/concepts/execution/index.md` — routing topology and RiskEngine boundary.
- `docs/concepts/execution/policies.md` — persistence-before-transport, unknown outcomes, dispatch record and restart semantics.
- `crates/common/src/cache/mod.rs` — cache persistence policy.
- `crates/execution/src/engine/mod.rs` — dispatch and process-local dispatched-order tracking.
- `crates/risk/src/engine/mod.rs` — RiskEngine command handlers and routing.
- `crates/live/src/execution/submission.rs` — live submission support surface (targeted read; not a complete adapter audit).

This is a targeted path review, not a complete line-by-line review of all execution algorithms, emulators, venue adapters, concurrency paths or database implementations. All unreviewed behavior remains UNKNOWN.

## 3. Finding F1 — persistence is not durable-before-dispatch

**Evidence:**
- `docs/concepts/execution/policies.md`, lines 175–191: for built-in execution submissions, the engine selects/validates the client, attempts to enqueue the resolved order-to-client origin for persistence, then calls the selected ExecutionClient. Enqueue failures are logged without blocking the client call; successful enqueue does not mean the backing store committed the order/origin.
- Same document, lines 199–200: process failure can occur after venue receipt but before local order/origin become durable; reconciliation may recover only if the venue reports the order, while incomplete venue history may prevent reconstruction.
- `crates/common/src/cache/mod.rs`, lines 20–34: all cache writes log persistence failures without propagating them or interrupting event/command processing; successful cache call confirms neither queue admission nor durable storage.

**NEXUS impact:** FAIL against NX-ADR-002 / NX-IF-001 / NX-IF-003. NEXUS requires durable command + scoped Risk approval before any external side effect. A cache enqueue is not a transactional outbox commit.

**Required treatment:** NEXUS persists canonical command, immutable identity, payload digest, Risk approval, account/venue/instrument/spec/policy versions and reservation in its own durable transaction before dispatch. The venue adapter receives only a persisted, authorized command. No direct strategy/algorithm route may call the adapter independently.

## 4. Finding F2 — built-in RiskEngine is bypassable by design

**Evidence:**
- `docs/concepts/execution/index.md`, lines 49–55: submit routes to OrderEmulator for emulated orders, to ExecutionAlgorithm when `exec_algorithm_id` is set, and to RiskEngine otherwise. Modify routes to an active ExecutionAlgorithm when applicable, otherwise RiskEngine. Cancel/query commands may route directly to OrderEmulator, ExecutionAlgorithm or ExecutionEngine.
- Same document, lines 188–192: RiskEngine sits on submit/modify path, but cancel/query commands route directly and do not pass through RiskEngine.
- Same document, lines 310–312: `RiskEngineConfig.bypass` can disable trading-state enforcement.
- `crates/risk/src/engine/mod.rs`, lines 584 onward and 874 onward: submit and modify handlers include bypass paths that forward commands directly to execution.

This is consistent with the engine's intended command decomposition; it is not being characterized as an upstream defect.

**NEXUS impact:** FAIL as the sole NEXUS authorization layer. The NEXUS RiskApprovalCapability must be required at the last non-bypassable gateway for every state-changing command. Cancel, reduce-only, close, cancel-all and emergency actions need explicit NX-IF-005 policy rather than informal exceptions.

**Required treatment:** no user strategy, AI component, execution algorithm or emulator receives raw venue client access. Only a narrow adapter gateway can dispatch, and it verifies command digest, account scope, venue, instrument/spec version, risk policy version, reservation, halt epoch, audience and expiry. Emergency commands use their own bounded authorization rules.

## 5. Finding F3 — dispatch marker is process-local and not restart-safe

**Evidence:**
- `docs/concepts/execution/policies.md`, lines 94–104: dispatched orders remain locally initialized until the first client status event; the dispatch record is process-local, cleared on reset and absent after restart. A still-initialized dispatched order is treated as an unrouted order after restart until client events or venue cancel/expiry evidence resolves it.
- `crates/execution/src/engine/mod.rs`, around `handle_submit_order` and `mark_orders_dispatched` (source snapshot above): execution dispatch state is marked in cache after the client submit call returns.

**NEXUS impact:** CRITICAL recovery concern. If NEXUS delegates resend decisions to process-local dispatch state, restart could erase evidence that a command was already sent. This is exactly the ambiguous-outcome scenario NEXUS must preserve as OUTCOME_UNKNOWN.

**Required treatment:** NEXUS durable outbox/inbox state is authoritative across restart. No submit retry is allowed solely because an upstream runtime reports an order as initialized or absent from an in-memory dispatched set. Startup must reconcile venue open orders, order history, fills, positions and ledger watermarks before releasing a recovery barrier.

## 6. Finding F4 — retry and deduplication remain at-least-once / scoped

**Evidence:**
- `docs/concepts/execution/policies.md`, lines 16–20: state-changing command retries are allowed only when safe; not all adapters conform; delivery is not exactly once; repeated fill `trade_id` is rejected but no blanket exactly-once guarantee exists across event types or lost retained state.
- Lines 156–163: documentation explicitly notes transient failures can send some commands twice, including on Bybit, OKX and Kraken Spot (not a complete census).
- Lines 117–118: timeouts, disconnects, cancellation, missing acknowledgements and parse failures after transmission usually leave outcome unknown.

**NEXUS impact:** upstream retry semantics cannot be treated as global idempotency. Each venue adapter needs a capability matrix for client IDs, idempotency keys, lookup endpoints, private streams and retry-safe commands.

**Required treatment:** durable canonical command identity, venue-specific retry policy, duplicate fill identity, durable inbox, correction/bust handling and reconciliation remain NEXUS-owned.

## 7. R6-C conformance gate

Before any execution integration experiment is accepted, implement a fake ExecutionClient and deterministic fault harness around a gateway boundary. The harness must prove:

1. Risk approval missing, expired, wrong-scope, wrong-digest or wrong-halt-epoch blocks every state-changing command.
2. No emulator, algorithm, strategy, callback or direct client reference can bypass the gateway.
3. Durable outbox transaction failure prevents adapter invocation.
4. Process crash after durable commit but before send safely resumes from persisted state.
5. Process crash after send but before acknowledgement yields OUTCOME_UNKNOWN; no blind resend.
6. Duplicate command delivery does not create duplicate side effects where the venue contract claims idempotency; otherwise it is blocked pending reconciliation.
7. Duplicate/late fills are durably deduplicated and ledger posting remains atomic.
8. Cancel/modify denied, rejected, unknown and acknowledged states remain distinct.
9. Cancel-all target set is immutable and bounded; concurrent new orders cannot silently enter the target set.
10. Startup reconciliation cannot mark an account ready from missing/null position evidence or incomplete order history.

**Exit condition:** all 10 scenarios pass against the exact pinned source/runtime or the integration is rejected. No production credentials or live venue calls are permitted in this gate.

## 8. Current disposition

- NautilusTrader v2.0.0rc9: **TEST-ONLY CANDIDATE**.
- Reuse of backtest/replay and selected data capabilities: **POSSIBLE, NOT APPROVED**.
- Reuse as NEXUS execution authority: **REJECTED FOR CURRENT ARCHITECTURE**.
- NEXUS Risk Engine, durable outbox, ledger and recovery barrier: **MUST REMAIN NEXUS-OWNED**.
- Stable v2 release qualification: **PENDING**.
- Live credentials, orders and production deployment: **NOT AUTHORIZED**.

This assessment is bounded. Reopen only when a stable upstream release, a proposed integration boundary or a concrete conformance prototype changes the evidence.
