# NX-RESEARCH-013 — Bybit V5 Public Market-Data Vertical Slice Qualification

**As-of date:** 2026-11-14  
**Status:** TECHNICAL RESEARCH ONLY / BYBIT NOT SELECTED AS NEXUS v1 VENUE / NO PRIVATE ACCESS OR TRADING AUTHORIZATION  
**Scope:** Official Bybit V5 public market-data contracts, first bounded data-recorder slice, and impact on current NEXUS ADRs  
**Repository baseline:** `PandaGarry/NEXUS`; reviewed on the PR #16 architecture branch `engineering/rust-execution-domain-conformance-v0`. This record deliberately does not claim a branch commit SHA that was not independently resolved from the connector metadata.  
**Official documentation reviewed:** Bybit V5 documentation pages linked in §10; live documentation, accessed 2026-11-14. Vendor documentation has no immutable source commit in the pages reviewed.

## 1. Executive decision

Bybit V5 is technically capable of supporting a narrow public-data prototype for trades and a reconstructible L2 order book. The strongest initial book contract is the full-depth REST snapshot plus WebSocket delta stream, because Bybit explicitly documents update-ID continuity and the snapshot/delta bridge procedure.

This is a **technical qualification only**. It does not select Bybit for NEXUS v1, establish account or product eligibility, or authorize private account access, credentials, testnet orders or live trading.

The repository's current venue decisions take precedence:
- NX-RESEARCH-003 says no first venue is selected and its Coinbase/Kraken comparison is preliminary.
- NX-RESEARCH-009 supersedes that historical shortlist for the documented RF-resident scenario: Bybit Global and OKX Global are technical research candidates only; exact legal entity, residency/KYC, product classification and account eligibility remain unresolved.
- NX-ADR-007 requires an exact venue-entity + account + product + instrument eligibility record. Public API reachability or a working WebSocket is not an eligibility decision.

Accordingly, the first technical fixture may use `category=linear`, `symbol=BTCUSDT` solely to validate the feed contract. This is not a recommendation to trade BTCUSDT perpetuals and is not a venue-selection decision.

## 2. Repository audit: current state versus the proposed slice

### 2.1 What already exists and should be reused

| Existing artifact | Current state | Decision for the data slice |
|---|---|---|
| NX-ADR-001 Unified Market Event Contract | PROPOSED; canonical envelope, provenance, exact values, distinct timestamps, sequence and quality lineage are specified | Keep as the normalization target; add Bybit fixtures only after schema review |
| NX-ADR-004 Market Data Recovery State Machine | PROPOSED; stream states, invalidation and recovery semantics are defined | Keep; use it to drive explicit book validity and recovery |
| NX-ADR-005 Instrument Specification & Exact Arithmetic | PROPOSED; reference models exist for exact numeric and instrument rules | Keep exact decimal strings and versioned instrument metadata; no binary float |
| NX-ADR-003 Simulation Fidelity & Strategy Validation | PROPOSED; distinguishes bars, replay, execution simulation, local paper and sandbox | Keep; do not present a data recorder or paper fill model as proof of alpha |
| NX-REF-DOMAIN-001..010 and numeric fixtures | Test-only reference work | Reuse as oracles where applicable; do not promote them to production authority |
| NX-ADR-002 Execution Integrity & Reconciliation | PROPOSED; durable outbox, Risk reservation, one-time approval, unknown outcomes and reconciliation | Preserve its invariants for a later private-execution slice; no order code in this work |
| NX-ADR-008 G1 technical baseline | Selected for G1 design/evaluation, not production | PostgreSQL remains a transactional-state candidate; CBOR/COSE are not needed for public market-data capture |
| HEGC / auth-catalog / Egress reference work in PR #16 | Reference models and disposable PostgreSQL fixtures; no production runtime or network fence | Freeze expansion; do not put these mechanisms in the public data path |

### 2.2 What does not exist yet

The reviewed branch documents architecture and reference models, not a running market-data product. No production Rust workspace, Bybit adapter, WebSocket supervisor, snapshot/delta book synchronizer, trade recorder, deterministic raw replay, data-quality monitor, strategy engine or production persistence deployment is established by the reviewed artifacts.

PR #16 is a broad stacked architecture foundation. Keep it Draft and parent-dependent; do not add the Bybit data implementation to it. This work belongs in a separate, narrow child PR based on the #16 branch until the stack is integrated.

### 2.3 Keep / simplify / defer / implement

| Decision | Items |
|---|---|
| KEEP | Independent Risk authority; single Execution Gateway; strategy/AI cannot send directly; credential isolation; exact arithmetic; immutable command identity; durable outbox; idempotency; explicit OUTCOME_UNKNOWN; reconciliation; freshness and recovery barriers |
| SIMPLIFY FOR THE FIRST DATA SLICE | Public-only feed; one venue endpoint family; one category and one symbol fixture; append-only raw capture; no account state, no private streams, no database service dependency; explicit quality state rather than a broad platform framework |
| DEFER | COSE/Ed25519 command approvals, deterministic-CBOR implementation, capability runtime, HEGC expansion, production authorization-catalog manifest, AI Orchestrator, UI/Desktop/Web, WASM, broker/message bus, ClickHouse, multi-venue support, NautilusTrader/Hummingbot integration, paper order simulation |
| IMPLEMENT NEXT | Bybit public trade capture; full-depth book snapshot/delta synchronization; exact raw-payload persistence; deterministic replay; gap/reset/duplicate/reconnect fault tests; quality and latency metrics |

Deferring implementation does not revoke the future security boundary. No strategy, AI or analytics process will be granted direct exchange credentials or a direct order path.

## 3. Bybit V5 public market-data contract

### 3.1 WebSocket connection

For the technical fixture:
- Mainnet public linear endpoint: `wss://stream.bybit.com/v5/public/linear`.
- Testnet public linear endpoint: `wss://stream-testnet.bybit.com/v5/public/linear`.
- Subscribe to `publicTrade.BTCUSDT` and `orderbook.full.BTCUSDT`.
- Send the application heartbeat `{"op":"ping"}` every 20 seconds as recommended by Bybit.
- Reconnect after disconnect, but treat reconnect as a new connection generation. Never assume the previous in-memory book remains valid.
- Mainnet hostname can be regional and depends on the account registration site. The public-data prototype must not hardcode a regional private-account hostname as a general production rule.

Public topics do not require authentication. No API key is needed for this data-only slice.

### 3.2 Full-depth order book: required synchronization

Bybit's full-depth stream is delta-only, with a 200 ms push frequency for linear contracts. It does not send an initial WebSocket snapshot. Initialize via REST `GET /v5/market/full_orderbook?category=linear&symbol=BTCUSDT`, then apply buffered WebSocket deltas from `orderbook.full.BTCUSDT`.

The documented algorithm is normative for the adapter:

1. Connect and subscribe to the full-depth WebSocket topic.
2. Buffer deltas immediately; retain each delta's `u` and `seq`.
3. If `u` continuity breaks while buffering, discard the buffer and restart buffering. If `seq` decreases, discard that delta.
4. Fetch the REST full-depth snapshot.
5. If snapshot `seq` is older than the first buffered delta, fetch again. Discard buffered deltas with `seq` older than the snapshot. If equal `seq` but different `u`, fetch again.
6. Initialize from the snapshot only when both `seq` and `u` match a buffered delta. Apply subsequent buffered deltas, then continue live.
7. For every subsequent delta: ignore `u` lower than current; if `u` is greater than current + 1, invalidate the book and restart synchronization; `u=1` is a reinitialization signal and also forces resynchronization.
8. Apply price-level changes exactly: insert/update non-zero quantity; delete the level when quantity is zero.

Important distinctions:
- `u` is consecutive within a session and is the continuity detector.
- `seq` is monotonically increasing but is not guaranteed to be consecutive. Never flag a gap solely because `seq` skipped a number.
- Bybit's full-depth snapshot returns up to 10,000 levels per side; deeper levels are not known from the initial snapshot unless later introduced by deltas.
- Both REST full-depth and WebSocket full-depth exclude Retail Price Improvement (RPI) orders. The local book is therefore not the entire executable liquidity picture. This limitation must travel with data-quality metadata and any Order Flow projection.

The simpler `orderbook.{depth}.{symbol}` stream sends an initial snapshot and deltas, and also documents `u=1` as a reset. It is a possible lower-complexity fallback, but the full-depth channel has the more explicit published snapshot-bridge and continuity procedure. For the first integrity-focused recorder, use full-depth unless measured bandwidth/storage or downstream requirements justify a documented alternative.

### 3.3 Public trades

Subscribe to `publicTrade.BTCUSDT`. Preserve at least:
- trade ID `i`;
- symbol `s`;
- taker side `S`;
- price `p` and size `v` as exact strings;
- trade time `T`;
- outer message timestamp `ts`;
- cross sequence `seq`;
- block-trade and RPI flags `BT` and `RPI` where present;
- local receive and durable-write timestamps added by NEXUS.

Bybit documents that a Spot/Futures message can contain up to 1,024 trades and multiple messages may carry the same `seq`. Therefore:
- deduplicate individual trades by the venue trade ID `i`, not by `seq`;
- do not assume one message equals one trade;
- do not assume `seq` uniquely identifies a trade or message;
- retain message boundaries and original payload for audit/replay.

The REST `/v5/market/recent-trade` endpoint is a recent-history endpoint (up to 1,000 for linear products), not a complete arbitrary-range historical backfill API. Bybit points users to downloadable historical archives. Archive acquisition, licensing/terms, coverage and integrity must be separately verified before relying on it for research history.

### 3.4 Instrument metadata and exact values

Before interpreting a symbol, query `GET /v5/market/instruments-info?category=linear&symbol=BTCUSDT` and preserve the returned metadata version/snapshot, including:
- symbol status, base/quote/settlement coins;
- tick size and price bounds;
- quantity step, minimum and maximum order quantity;
- minimum notional;
- contract-specific fields and funding interval where applicable.

Metadata must be refreshed and versioned. A tick/lot change is a reason to invalidate or requalify a book snapshot and order-validation context. Prices and sizes arrive as decimal strings: never convert them through IEEE-754 binary floating point in the canonical event, replay or financial calculations.

### 3.5 Time semantics

Keep independent fields:
- exchange message generation time `ts`;
- matching-engine book time `cts`;
- trade execution time `T`;
- local receive time;
- local processing time;
- durable-write time.

Do not overwrite one with another or silently compare clocks without tracking clock offset/uncertainty. Persist UTC timestamps plus original exchange millisecond values.

## 4. Execution API observations for a later phase (not implementation scope)

These findings are recorded now so the later private adapter is not designed from assumptions:

- `POST /v5/order/create` is asynchronous. An HTTP acknowledgement means the request was accepted for processing, not that the order is filled or even that the final order state is known. Confirm through the private order/execution streams and reconciliation.
- `orderLinkId` is user-defined, must be unique, and is limited to 36 characters for ordinary spot/futures/perpetual order endpoints. NEXUS must persist its client ID before dispatch and bind it to one immutable internal command.
- The private order stream can emit two `Filled` messages in a cancel-vs-fill race. The event reducer must be idempotent and use the documented status/reject/cancel fields rather than treating every message as a new fill.
- The private execution stream can contain multiple executions for one order in a message. Use `execId` as the execution identity; retain order ID, client ID, fee, fee currency, execution price/quantity/time and sequence.
- `GET /v5/order/realtime` is useful for active orders and a bounded recent closed-order cache (up to 500). Bybit notes that after service restart, closed UTA order records should be queried through order history. Order history itself has time-window and delivery caveats. It is not safe to reconcile only from one endpoint.
- `GET /v5/execution/list` is required in the eventual fill-reconciliation set. Bybit notes that equal `execTime` rows may have sorting issues; sort with the documented composite fields rather than assuming time alone is a total order.
- `POST /v5/order/cancel-all` is asynchronous. For futures, the documented operation cancels up to 500 orders and may choose 500 randomly when more than 500 are open. A successful acknowledgement is not proof that every order is cancelled. Reconcile all orders afterward.
- Cancel-all does not flatten an open position. Emergency cancellation, reduce-only risk reduction and position flattening are distinct operations and need separately certified venue semantics.
- The account mode, margin mode, position mode, leverage, settlement asset, risk limits and instrument specification must be queried/qualified; never assume one-way mode or a particular UTA configuration.

The later adapter must follow NX-ADR-002: no automatic retry of order mutations after ambiguous delivery, explicit `OUTCOME_UNKNOWN`, durable reservation/command state, one logical transmission per authorization, and reconciliation before any retry decision.

## 5. First vertical slice — bounded scope

### 5.1 Deliverable

A headless, read-only Bybit public-data recorder and deterministic replay tool. It must prove that NEXUS can:
1. connect to the public linear market stream;
2. record trades and a locally reconstructed full-depth BTCUSDT book;
3. detect sequence gaps, resets, stale data and disconnects;
4. resynchronize from a fresh REST snapshot without exposing an invalid book as live;
5. preserve exact source payloads and timestamp provenance;
6. replay recorded input deterministically and reproduce the same book/trade state;
7. report data-quality and latency metrics.

This is a research fixture, not an order-entry service, strategy runtime, production deployment or venue approval.

### 5.2 Deliberate exclusions

No API keys, private account stream, wallet/position query, order create/amend/cancel, transfers, funding, withdrawals, testnet order, mainnet order, strategy automation, AI, UI, multi-venue abstraction beyond the minimum canonical envelope, broker, database deployment, or production authorization-catalog work.

### 5.3 Storage experiment

Do not force all raw market data into PostgreSQL by assumption. For the first recorder:
- write append-only, UTC-partitioned raw JSONL segments with original payloads and an explicit segment manifest/checksum;
- write normalized event records separately, preserving a link to the raw segment/offset or event hash;
- measure bytes/sec, write latency, fsync/rotation cost, replay throughput and disk growth;
- compare the measured workload with Parquet conversion and PostgreSQL ingestion before choosing long-term storage.

PostgreSQL remains the preferred candidate for transactional command/order/risk/ledger state in NX-ADR-008. It is not yet deployed and need not be introduced merely to store this first public feed. ClickHouse remains deferred until measurements justify it.

### 5.4 Engineering and test gates

The implementation must include deterministic fixtures for:
- valid initial snapshot + buffered bridge + subsequent deltas;
- snapshot older than first buffered delta;
- equal `seq` but mismatched `u`;
- duplicate delta;
- lower `u` stale delta;
- `u` gap and recovery;
- `u=1` reset;
- decreasing `seq`;
- zero-size level deletion and insertion/update;
- reconnect during snapshot bridge;
- buffer overflow / bounded memory;
- malformed decimal, crossed/invalid book, unknown symbol and metadata-version change;
- duplicate trade ID across reconnect;
- multiple trades in one message and repeated `seq`;
- clock skew / out-of-order event timestamps;
- disk-full / partial-write / restart / corrupt segment;
- replay determinism and raw-to-normalized traceability.

A seven-day continuous recording run is a useful endurance gate, not proof of reliability. It must be paired with fault injection and recovery tests. Record at least:
- connection uptime and reconnect count;
- trade duplicates and malformed events;
- book gaps, resets, resync count and resync duration;
- time spent in each ADR-004 stream state;
- exchange-to-local receive and receive-to-durable-write latency distributions;
- buffer high-water mark and dropped frames (target zero silent drops);
- raw archive coverage, segment checksum failures and replay divergence.

A book is usable by downstream analytics only in `LIVE_VALID` (or an explicitly approved degraded mode). While `AWAITING_SNAPSHOT`, `SYNCHRONIZING`, `GAP_DETECTED`, `RECOVERING`, `STALE` or `HALTED`, it must not be exposed as a trustworthy complete book.

## 6. ADR and roadmap disposition

| Artifact | Required update |
|---|---|
| NX-ADR-001 | Keep canonical event semantics; add exact Bybit field mapping and fixtures only in the implementation PR |
| NX-ADR-004 | Keep recovery state machine; map Bybit `u` continuity and `seq` cross-sequence semantics |
| NX-ADR-005 / NX-REF-DOMAIN | Keep exact decimal and instrument metadata; no float conversion |
| NX-ADR-003 | Research strategy validation in parallel only after trustworthy replay data exists; do not claim alpha |
| NX-ADR-002 | Keep future execution invariants; Bybit private API contract qualification is a separate later work package |
| NX-ADR-007 / NX-RESEARCH-009 | Eligibility remains a hard gate; Bybit technical research does not change venue status |
| NX-ADR-008 | Keep G1 design baseline; no CBOR/COSE or production PostgreSQL work is required for the public data slice |
| PR #16 | Freeze feature scope; do not add Bybit code or new broad subsystems |
| New work | Separate child PR based on PR #16, initially limited to public-data recorder/replay and its tests |

## 7. Readiness and acceptance

The public-data slice can be accepted as a technical prototype only when:
- exact toolchain and dependencies are pinned and license/security reviewed;
- raw capture and normalized events are reproducible;
- book synchronization follows the official snapshot-bridge procedure;
- all deterministic and fault-injection cases pass;
- no invalid/stale book reaches a consumer as `LIVE_VALID`;
- metrics and archive manifests are emitted;
- the recorder can restart and continue without silent loss or duplicate canonical events;
- exact commit CI is green and all docs/checklists point to that commit.

Passing this gate does not pass G0D/G1–G3, does not certify Bybit eligibility, does not prove profitable strategies, and does not authorize live trading.

## 8. Confidence and unresolved questions

**High confidence:** documented Bybit V5 public endpoint paths, message fields, full-depth `u`/`seq` synchronization procedure, RPI exclusion, public trade message batching, order-link ID constraints and the listed order-stream/reconciliation caveats, as they appear in the official pages reviewed on 2026-11-14.

**Medium confidence:** suitability of full-depth 200 ms feed for NEXUS's eventual Order Flow requirements. It must be measured against actual strategy/analytics requirements and ATAS-style depth expectations.

**UNKNOWN / OPEN:**
- exact venue legal entity, user/account jurisdiction and account eligibility;
- whether Bybit is the first venue or only a technical research target;
- intended product and market family for the first production account;
- market-data archive coverage, download automation, licensing and long-term retention;
- whether RPI omission materially affects target Order Flow analytics;
- actual data throughput, latency, reconnect frequency and storage economics from a running recorder;
- fee tier, funding, account mode, leverage and risk-limit settings;
- production API-key policy, IP allowlist, no-withdrawal permission availability and subaccount restrictions;
- production security review and emergency operating procedure.

## 9. Sources and evidence boundary

All vendor facts below are from official Bybit V5 documentation. The documentation itself is mutable; the as-of date is recorded above.

- WebSocket Connect, endpoints, regional hosts, authentication and heartbeat: https://bybit-exchange.github.io/docs/v5/ws/connect
- Full-depth WebSocket order book and exact synchronization procedure: https://bybit-exchange.github.io/docs/v5/websocket/public/full-ob
- Full-depth REST snapshot: https://bybit-exchange.github.io/docs/v5/market/full-ob
- Public trade WebSocket: https://bybit-exchange.github.io/docs/v5/websocket/public/trade
- Recent public trade REST: https://bybit-exchange.github.io/docs/v5/market/recent-trade
- Instruments info: https://bybit-exchange.github.io/docs/v5/market/instrument
- Historical klines: https://bybit-exchange.github.io/docs/v5/market/kline
- Place order and `orderLinkId`: https://bybit-exchange.github.io/docs/v5/order/create-order
- Private order stream and cancel/fill race: https://bybit-exchange.github.io/docs/v5/websocket/private/order
- Private execution stream and `execId`: https://bybit-exchange.github.io/docs/v5/websocket/private/execution
- Realtime open/closed orders: https://bybit-exchange.github.io/docs/v5/order/open-order
- Order history: https://bybit-exchange.github.io/docs/v5/order/order-list
- Execution history: https://bybit-exchange.github.io/docs/v5/order/execution
- Cancel all: https://bybit-exchange.github.io/docs/v5/order/cancel-all
- Account info: https://bybit-exchange.github.io/docs/v5/account/account-info
- Rate limits: https://bybit-exchange.github.io/docs/v5/rate-limit

No live API calls, account access, credentials, orders or external account changes were performed as part of this research.
