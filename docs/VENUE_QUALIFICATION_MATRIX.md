# NEXUS — venue qualification matrix

**Last reviewed:** 2026-11-17 (Kraken Spot amend semantics re-check)  
**Purpose:** compare candidate venues without making any venue the architectural center or assuming user eligibility.  
**Status convention:** YES / NO / UNKNOWN. Every non-UNKNOWN claim is scoped to an exact API/product and backed by a dated source. A documented public feed does not prove account eligibility or production readiness.

## 1. Candidate universe (not a live-venue ranking)

| Candidate | Why it is in the research universe | Current role | Selection status |
|---|---|---|---|
| Bybit | Concrete V5 full-depth public stream and linear derivatives market; first live raw capture succeeded | Reference adapter experiment #1; M2 is the active implementation priority | Not selected for trading |
| Kraken Spot WS v2 + Unified WS (Derivatives) | Spot L2 snapshot+CRC32; new Unified WS supports Spot/Derivatives, derivatives private streams and order entry; legacy Derivatives WS v1 deprecated for 2027-03-01 | Protocol/terms research candidate; specific amend/cancel behaviors are documented, but broader execution/recovery semantics remain unqualified | Not selected for trading |
| Bitstamp | Public REST order book, WS v2 feeds, documented derivatives API examples for BTC/USD-PERP; commercial data-license route published | Protocol, market availability and data-rights qualification candidate | Not selected for trading |
| Coinbase Advanced Trade | Distinct API/product family and useful comparator; do not conflate with Coinbase Exchange API | Alternative technical adapter candidate | Not selected |
| OKX | Tick-level trades + historical high-resolution L2 since 2023-03; snapshot + seqId/prevSeqId live book model | Leading HYP-001 historical-L2 research candidate; no recorder until Bybit M2 | Not selected; terms restrictive |
| Tardis.dev | Historical tick-level trades and incremental L2 datasets across venues, including Bitstamp; current ToS permits personal/research use and tightly scoped derived-data distribution | Historical research data provider candidate | Not selected; terms restrict third-party platform use |
| Amberdata | Market-data API with published commercial-use FAQ; redistribution requires custom license | Commercial/internal data-provider candidate | Not selected; exact NEXUS rights unconfirmed |
| Binance | Potentially useful large-scale spot/derivatives API comparator | Discovery backlog; no qualification claim here | Unknown |
| Domestic brokers / listed derivatives venues | May offer a materially different legal, clearing and instrument model | Separate broker/venue adapter research | Not selected |

**Sequencing decision (2026-11-15):** Bybit M2 remains NOT ACCEPTED and its live-evidence gate is separately BLOCKED pending terms clarification. The second-recorder pre-M2 path is proposed in ADR-005, but is not owner-approved. PR #19 `MILESTONES.md` still says no second recorder implementation until Bybit M2 is accepted. Until the owner resolves this conflict, the stricter M2-first gate controls. OKX remains a historical-L2 research candidate; Kraken is a Spot snapshot/checksum contrast; Bitstamp is a potential delta + externally seeded snapshot contrast. No second adapter is selected or started.

## 2. Evidence-backed public-data snapshot (checked 2026-11-15)

| Public-data capability | Bybit V5 linear | Kraken Spot WS v2 | Coinbase Advanced Trade | OKX V5 | Binance public data / USD-M |
|---|---|---|---|---|---|
| Public trades channel documented | YES | YES | UNKNOWN in this snapshot | YES | YES — raw trades and aggTrades |
| Trade ID documented | YES — execution ID `i` | YES — `trade_id`, unique per book | UNKNOWN | YES — `tradeId` | YES — trade `id`, aggTrade ID |
| Trade event timestamp documented | YES — milliseconds | YES — RFC3339 | UNKNOWN | YES — milliseconds | YES — Spot microseconds since 2025-01-01; Futures milliseconds |
| L2 book documented | YES — full depth | YES — aggregated L2 | UNKNOWN in this snapshot | YES — 400 levels on standard `books` channel | Public depth stream; exact channel contract not qualified here |
| WS initial book snapshot | NO — full-depth stream is delta-only | YES — snapshot sent by default | UNKNOWN | YES — full snapshot | UNKNOWN in this snapshot |
| WS incremental updates | YES — delta-only | YES — update messages | UNKNOWN | YES — every 100 ms on `books` | YES — public diff-depth stream |
| Continuity evidence documented | YES — update ID `u` and cross sequence `seq` | YES — CRC32 checksum over top 10 bids/asks | UNKNOWN | YES — `prevSeqId` + `seqId`; checksum deprecated | UNKNOWN in this snapshot |
| REST snapshot required for initial book | YES | NO for documented WS snapshot flow | UNKNOWN | NO for documented WS snapshot flow | UNKNOWN in this snapshot |
| Public L3 / order-level feed entitlement | UNKNOWN | UNKNOWN for Spot; separate FIX examples show Futures L3 | UNKNOWN | UNKNOWN | UNKNOWN |
| Historical trade archive | Public BTCUSDT daily CSV listing from 2020-03-25; completeness/freshness unverified | Spot Time & Sales from each pair's first trade through 2026-09-30 | UNKNOWN | Tick-level trades from 2021-09 | Daily/monthly Spot and Futures trades/aggTrades; per-symbol coverage must be inventoried |
| Historical L2 archive | UNKNOWN — official path/schema not validated | UNKNOWN — Time & Sales only; no L2 evidence | UNKNOWN | Portal advertises high-resolution L2 from 2023-03; archive sample not validated | NO per-level L2 evidence; `bookDepth` is percentage-band aggregate depth |
| Live public smoke evidence in NEXUS | YES — 10-minute raw capture/replay | NO | NO | NO | NO |

### Bybit V5 linear evidence

- **Execution/reconciliation compatibility notice (checked 2026-11-16):** Bybit first announced this change for 2026-11-12, then posted a postponement to **2026-12-03** in its official API Announcements channel; the rendered channel view does not expose the postponement post's exact calendar date. From 2026-12-03, `GET /v5/order/history` and `GET /v5/spread/order/history` will no longer return `Cancelled`, `Rejected` or `Deactivated` orders by default when `orderStatus` is omitted. Pass `orderStatus` explicitly to retrieve these terminal states; they remain queryable only within the most recent 24 hours. The REST history endpoint also warns that order creation/cancellation data may be delayed and recommends the private WebSocket stream for real-time status. The V5 changelog page checked on 2026-11-16 still shows dated entries only through 2026-11-09, so this announcement should be rechecked for a formal changelog update. This does not affect the public recorder/M2, but a future private Bybit adapter must include explicit-status recovery, private-stream ingestion and a contract fixture before implementation. Sources: [official Bybit API Announcements](https://t.me/s/bybit_api_announcements), [Get Order History](https://bybit-exchange.github.io/docs/v5/order/order-list) and [V5 changelog](https://bybit-exchange.github.io/docs/changelog/v5).

- Full-depth WS topic `orderbook.full.{symbol}` is explicitly delta-only; no initial snapshot is sent. A REST full-depth snapshot must be obtained and aligned with buffered deltas.
- Bybit's official V5 changelog notes that its trading and matching engine migrated to AWS Tokyo (`apne1-az4`) on 2026-11-12. The latest English V5 changelog entries through 2026-11-09 concern Spot margin/strategy/account endpoints, not the BTCUSDT linear full-depth book/trade contract; no schema change to the current recorder channels was identified. This is an infrastructure observation, not a latency or venue-selection conclusion.
- Official synchronization requires consecutive `u` within a session, discarding a delta whose `seq` decreases, discarding deltas older than the REST snapshot `seq`, and matching both `seq` and `u` before applying subsequent deltas.
- `u=1` is a reinitialization signal. `seq` is monotonic but not necessarily consecutive.
- Full-depth stream and REST snapshot exclude RPI orders.
- Public historical trade archive: the official `public.bybit.com/trading/BTCUSDT/` directory lists daily CSVs beginning 2020-03-25; the listing inspected did not establish current completeness/freshness. Bybit Learn says downloadable historical public data may include order-book snapshots, but no official L2 archive path/schema/depth/date range has been validated by NEXUS. A third-party downloader points to `quote-saver.bycsi.com/orderbook/linear`; treat it as an unverified discovery lead, not official completeness or license evidence.
- Bybit API Terms & Conditions (support page last updated 2026-10-20) grant a limited revocable API license for development/testing/support (Section 5.1), prohibit API/Service Data availability or performance benchmarking (6.6), prohibit repackaging/reselling Service Data (6.7), and prohibit commercial exploitation (6.9). Section 2.3 says API use requires API-key identity verification; applicability to technically unauthenticated public market-data endpoints requires clarification. NEXUS therefore keeps raw data private and gates future automated live capture pending explicit terms review.
- NEXUS run #10 captured 8,149 public trade messages, 2,998 full-depth delta messages, 29 pong replies and 1 subscription acknowledgement = 11,177 records exactly. Independent inspection found zero malformed lines and zero raw SHA-256 mismatches. One connection generation was observed.

Official sources:
- Full-depth WS and synchronization: https://bybit-exchange.github.io/docs/v5/websocket/public/full-ob
- V5 API changelog and 2026-11-12 Tokyo infrastructure migration notice: https://bybit-exchange.github.io/docs/changelog/v5
- Full-depth REST snapshot: https://bybit-exchange.github.io/docs/v5/market/full-ob
- Trade channel: https://bybit-exchange.github.io/docs/v5/websocket/public/trade
- Historical BTCUSDT trade listing: https://public.bybit.com/trading/BTCUSDT/
- Bybit Learn historical market-data note: https://www.bybit.com/en/learn/bybit-guide/how-to-create-a-bybit-api-key
- Unverified third-party L2 archive lead: https://github.com/Anton495/bybit-data-downloader
- API Terms & Conditions: https://www.bybit.com/en/help-center/article/API-Terms?category=ae1012f19fad1c184e
- API agreement PDF: https://www.bybit.com/common-static/compliance/legal/BYBIT/df1923006718fbba8ba70d7d762b9866.pdf

### Kraken Spot WebSocket v2 evidence

- `book` is aggregated L2, with supported depths 10, 25, 100, 500 and 1,000.
- A snapshot is sent on subscription by default; updates follow. Each message carries a CRC32 checksum.
- The checksum is always calculated over the top 10 price levels regardless of subscribed depth. It validates only the top 10 levels, not the entire subscribed depth.
- For checksum construction, parse price and quantity without floating-point precision loss; remove decimal points and leading zeroes from each string; concatenate the top 10 asks in ascending price order, then the top 10 bids in descending price order; compute CRC32 and compare as an unsigned 32-bit integer.
- Apply all price-level updates in a message before calculating the checksum. Remove zero-quantity levels and truncate to subscribed depth; the feed does not send zero-quantity updates for levels falling out of scope.
- Trade events include taker side, quantity, price, per-book `trade_id` and RFC3339 timestamp; a message may batch multiple trades.
- Kraken's downloadable Spot Time & Sales archive covers every public trade for each pair from its first trade through 2026-09-30. Its seven CSV fields are `timestamp, price, volume, type, order_type, misc, trade_id`; the full archive is split into roughly 2 GB parts with published SHA-256 checksums. This is trade history, not L2 history.
- Do not assume historical CSV `type` (`b`/`s`) has identical aggressor/taker semantics to the WS v2 `side` until that mapping is verified. If it is not equivalent, it cannot be used as signed taker-flow input for HYP-001.
- The Kraken WS FAQ says public market-data feeds are unauthenticated and current-only; a book snapshot is sent on subscription and a heartbeat arrives at 1 Hz when no other messages arrive.
- Terms caveat: Kraken's API guide says prior permission is required for certain uses, including non-personal commercial use of data from public endpoints, and directs requests to `marketdata@kraken.com`. The global Terms limit use and third-party distribution of Kraken content. Personal internal research, retention and any later redistribution require separate terms review; no redistribution right is inferred.
- This is L2, not proof of Spot L3/order-level access.

Official sources:
- Book L2: https://docs.kraken.com/api/docs/websocket-v2/book
- Book checksum v2 algorithm: https://docs.kraken.com/exchange/guides/websockets/book-checksum-v2
- Trades: https://docs.kraken.com/api/docs/websocket-v2/trade
- Public feed FAQ / heartbeat / current-only scope: https://support.kraken.com/articles/360022326871-kraken-websocket-api-frequently-asked-questions
- Historical Spot Time & Sales archive: https://support.kraken.com/in/articles/360047543791-downloadable-historical-market-data-time-and-sales-
- API terms / prior permission for certain commercial public-data uses: https://docs-legacy.kraken.com/api/docs/guides/global-intro/
- Global Terms: https://www.kraken.com/legal/global-terms

### Kraken Spot REST amend semantics (checked 2026-11-17)

- The official `POST /0/private/AmendOrder` endpoint accepts either `txid` or `cl_ord_id` (at least one). A successful response returns a unique `result.amend_id`; it does **not** return a replacement venue order ID. Kraken states that the original venue/client order identifiers remain unchanged and queue priority is maintained where possible. The amend ID identifies the amend operation, not the order.
- NautilusTrader commit [`17b9718`](https://github.com/nautechsystems/nautilus_trader/commit/17b97189bccbeb8c9da57bcfdec888ea46b70361) (2026-11-17) fixed a client-side false failure: an amend submitted by client order ID alone could succeed at Kraken, but the adapter raised `MissingOrderId` because the response did not echo a venue order ID. The fix preserves a supplied venue ID or returns `None` when only the client ID was supplied.
- **NEXUS implication:** a future Kraken adapter must retain its internal/client order identity and any known venue order ID, treat `amend_id` as an amend acknowledgement rather than an order ID, and not classify a successful response as failure merely because no venue order ID is echoed. If the request outcome is ambiguous, use the client ID plus private events/order queries for reconciliation. Exact amend retry/idempotency, amend-ID retention and full recovery semantics remain UNKNOWN.
- Affects NX-ADR-002 / future Kraken adapter qualification only. This is source/documentation evidence, not NEXUS implementation or exchange-runtime verification.

Official sources:
- Kraken Amend Order: https://docs.kraken.com/api-reference/trading/amend-order
- NautilusTrader integration regression/fix: https://github.com/nautechsystems/nautilus_trader/commit/17b97189bccbeb8c9da57bcfdec888ea46b70361

### Kraken Derivatives Unified WebSocket and execution notes (release notes 2026-11-12)

- Kraken deprecated the legacy Derivatives WebSocket v1 endpoint `wss://futures.kraken.com/ws/v1`; existing integrations continue until **2027-03-01**. New derivatives integrations should use the Unified WebSocket, which carries Spot and Derivatives on one connection; set `asset_class=derivatives` on each derivatives subscription/order message.
- The Unified WebSocket supports `add_order`, `amend_order`, `cancel_order`, `cancel_all` and `cancel_after`. It authenticates with a token from `GetWebSocketsToken` requested using a Kraken Spot API key, rather than a Derivatives API key. Kraken's Rust SDK release note says it covers derivatives market data, private executions/positions/margin/balances, order entry, token refresh, reconnects and order-book checksums. These are official capability statements, not NEXUS runtime verification.
- **Kill-switch implication:** the 2026-11-12 release notes say `POST /cancelallorders` now reports a `CANCEL` event in `orderEvents` for each trigger order cancelled, while `status` can remain `noOrdersToCancel` when only trigger orders were cancelled. A future adapter must inspect per-order events and reconcile; it must not treat `status` alone as proof that nothing was cancelled.
- Kraken also states that Spot transfers through `POST /transfer` require the withdrawal permission, while `POST /withdrawal` and `GET /transfers` are deprecated for removal on 2026-11-30. Funds transfer is outside NEXUS scope: retain the no-withdrawal key policy and do not grant withdrawal permission for market data or trading.
- This changes future Kraken adapter qualification only. It does not affect the Bybit public recorder/M2, and it does not establish account/jurisdiction eligibility, idempotency, snapshot consistency or full reconciliation semantics.

Official source: https://docs.kraken.com/exchange/changelog (12 November 2026 release notes); Unified WS reference: https://docs.kraken.com/exchange/api-reference/unified-ws/ticker.

### Bitstamp API v2 / WebSocket v2 evidence (checked 2026-11-15)

- The official API reference documents REST order book `GET /api/v2/order_book/{market_symbol}/`, with `group=0/1/2` options (ungrouped price levels, grouped-by-price default, or order IDs not grouped at price). It also links the official WebSocket API v2 guide. The official WS page is currently not machine-readable in this review; exact channel payload, timestamp fields, sequence/event identifiers, snapshot semantics and reconnect guarantees therefore remain UNKNOWN until manually verified against the published protocol specification.
- Bitstamp's own API reference contains multiple `BTC/USD-PERP` examples and identifies it as `market_type: PERPETUAL` in derivatives responses. This proves the instrument is represented in the documented API, not that it is currently active, publicly order-book accessible, available to every legal entity/account, or sufficiently liquid. The live `markets` response and the relevant WS channel must be checked before instrument selection.
- The official 2026-11-09 changelog added `matching` to `GET /api/v2/markets/` and clarified that `trading` now represents order-entry availability. During a no-matching halt, `trading=Enabled` and `matching=Disabled`: limit orders may be placed/cancelled but are not matched, while instant/market orders are rejected. During a full halt both are Disabled. A future adapter must model order-entry and matching availability separately; do not infer matching/fills from `trading=Enabled` alone.
- The same API reference says derivatives markets are returned by public endpoints such as `/api/v2/markets/` and `/api/v2/ticker/{market_symbol}/` (changelog 2025-06-16). It documents public derivatives funding-rate endpoints. Market listing is not an account-eligibility determination.
- The official API page states companies seeking commercial use of Bitstamp exchange data should contact `partners@bitstamp.net` for a commercial Data License Agreement, and says commercial redistribution/incorporation is possible under that agreement. The page does not establish whether an individual developer can contract on the same terms; ask directly rather than assuming an entity is required or not.
- Independent Tardis capture documentation reports that Bitstamp `live_orders` and `diff_order_book` subscriptions do not provide an initial full-book snapshot; Tardis obtains a REST snapshot and inserts it as a generated snapshot event. Treat this as a useful independent observation, not official protocol proof. Tardis's own collection process is not a substitute for a NEXUS live protocol test.
- Architectural implication: Bitstamp may provide a third book-bootstrap pattern (WS deltas + REST seed) but this is not yet a confirmed third continuity model. Do not describe it as timestamp-only or sequence-free: the official WS schema and continuity fields have not been qualified.

Official sources:
- API v2 reference, REST book, market list, derivatives examples, licensing and changelog: https://www.bitstamp.net/api/
- Official WebSocket API v2 guide: https://www.bitstamp.net/websocket/v2/
- Robinhood announcement confirming acquisition closed 2025-06-02: https://robinhood.com/newsroom/robinhood-completes-acquisition-of-bitstamp/
- Independent capture/snapshot observation: https://docs.tardis.dev/historical-data-details/bitstamp

### Binance Public Data evidence

- The official Binance Public Data repository documents daily/monthly Spot and USD-M/COIN-M Futures archives. Raw `trades` and `aggTrades` include trade IDs, price, quantity, timestamps and `isBuyerMaker`; `aggTrades` compresses same-price/same-taker-side fills within 100 ms. Prefer raw `trades` for HYP-001 when complete archives exist.
- Spot timestamps are microseconds from 2025-01-01 onward; Futures examples use milliseconds. Timestamp-unit changes must be handled explicitly.
- Futures `bookDepth` is not a per-level order book: the official repository's issue #447 explains it as cumulative depth and notional at percentage bands from mid-price. It cannot reconstruct BBO, spread or price-level queue depth.
- Binance Vision Dataset Terms v1.0 (2026-08-26) license data under CC BY-NC-SA 4.0 for non-commercial use. Permitted use includes personal non-production historical backtesting; live proprietary trading execution, automated commercial order generation and commercial trading products are expressly prohibited. Non-commercial derivative redistribution requires attribution and the identical ShareAlike license.

Official sources:
- Data archive schema: https://github.com/binance/binance-public-data
- Dataset terms: https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md
- `bookDepth` meaning: https://github.com/binance/binance-public-data/issues/447
- `aggTrades` and `isBuyerMaker` semantics: https://developers.binance.com/docs/derivatives/coin-margined-futures/market-data/rest-api/Compressed-Aggregate-Trades-List
### OKX V5 evidence

- The official historical-data portal lists tick-level trades from September 2021, high-resolution L2 from March 2023, perpetual funding rates from March 2022 and candlesticks from July 2023.
- Standard `books` sends a 400-level initial full snapshot and incremental updates every 100 ms. `books-l2-tbt` (400 levels / 10 ms) and `books50-l2-tbt` (50 levels / 10 ms) are restricted to VIP4+ fee tiers; do not assume access to these higher-frequency channels.
- Current continuity contract is `prevSeqId` + `seqId`: snapshot has `prevSeqId=-1`; normal incremental `prevSeqId` matches the previous `seqId`; maintenance may reset `seqId` lower than `prevSeqId`, after which normal sequencing resumes.
- JSON order-book checksum was deprecated in production on 2026-06-23; checksum fields remain but are always zero. Do not use checksum as integrity evidence.
- OKX's public-internet WebSocket port 8443 retirement date was 2026-10-31; the announced Colo retirement date is 2026-11-16 (today). Use the default TLS port 443. OKX states connections on 8443 fail after the applicable date; NEXUS has not run a connectivity test against either port.
- On 2026-11-13 OKX launched SBE order-entry and private order/fill services in demo; production is expected in early December. JSON APIs remain unaffected. SBE order entry currently supports CASH/CROSS modes; private `orders`/`fills` channels do not send an initial snapshot, and `fills` requires VIP4+. These are future adapter qualification details, not a current NEXUS integration decision.
- Historical-data terms allow personal use including development of one's own trading strategy, but prohibit redistribution and disclaim completeness/accuracy. The API Agreement limits Market Data to personal, non-commercial use and prohibits redistribution, competing data/analytics products and commercialized AI model training without written consent. No raw OKX data may be published or committed to NEXUS.

Official sources:
- Historical data: https://www.okx.com/historical-data
- V5 API/book sequence semantics: https://www.okx.com/docs-v5/en/
- API changelog, port 8443 retirement and SBE demo-service notice: https://www.okx.com/docs-v5/log_en/
- Checksum deprecation: https://www.okx.com/en-sg/help/okx-order-book-channels-checksum-field-deprecation
- API Agreement: https://www.okx.com/help/okx-api-agreement
- Historical-data terms: https://www.okx.com/help/historicaldata-terms-and-conditions

## 3. Historical-data providers and licensing (separate from exchange execution)

These providers can support research-data acquisition without becoming execution venues. A provider's licence does not automatically clear upstream exchange rights beyond the provider's express grant, nor does a personal/research licence imply permission to expose data or data-powered functionality to NEXUS customers.

| Provider | Evidence-backed scope | Storage / personal research | External/commercial product | Qualification status |
|---|---|---|---|---|
| Tardis.dev | Historical raw exchange-native feeds and normalized tick-level trades, incremental L2, snapshots, quotes and derivatives fields; Bitstamp history page lists BTCUSD incremental L2 and trades from 2019-07 | Current ToS (modified 2026-10-28) expressly includes an individual as Customer; Permitted Use includes personal and research use; Clause 9.1 permits download/store/copy and create Derived Data; Clause 9.4 grants continuing rights to lawfully downloaded data subject to surviving restrictions | Clause 9.2 prohibits exposing data/manipulated data or data-powered feed/API/analytics/charting/backtesting functionality to non-Customer Users. Clause 9.3 permits qualifying Derived Data externally as charts/statistics/reports or products aggregated at intervals >=10 minutes (with each measure/instrument datapoint at least 10 minutes apart), except Coinbase data. Coinbase-derived data has stricter prohibitions, including AI/ML use. This is not a blanket SaaS licence | Strong personal HYP-001 candidate; commercial NEXUS rights require a separate interpretation/contract |
| Amberdata | Official online market-data FAQ publishes API/WS usage limits and commercial-use FAQ | Standard licence says commercial use is allowed; exact historical depth, symbols, retention and account scope need product-level confirmation | Standard licence prohibits redistribution/resale/sublicensing; custom licence needed for redistribution. API keys are single-tenant and tied to purchasing organization | Candidate for internal commercial analytics; not cleared for customer-facing NEXUS |
| Kaiko / other institutional vendors | Discovery backlog; no current contract or exact product scope reviewed in this pass | UNKNOWN | UNKNOWN; request explicit rights for internal research, derived outputs, display, redistribution, multi-tenant use, retention and post-termination use | Not qualified |

### Tardis terms details (reviewed 2026-11-15)

- The current Terms page explicitly dates its modification to 2026-10-28; do not rely on older indexed copies dated 2023.
- An individual can be the Customer and, where the Customer is an individual, is a Customer User. Permitted Use expressly includes personal and research purposes.
- Clauses 9.1 and 9.4 support access, download, storage/copying and continued use of lawfully downloaded data/Derived Data after subscription expiry, subject to the stated surviving restrictions and licensor rights.
- Clause 9.2 prohibits redistribution/resale/sublicensing or making raw/Manipulated Data available to non-Customer Users, and prohibits providing non-Customer Users a product/service or functionality using the data (examples include data feed, API, analytics, charting and backtesting platforms).
- Clause 9.3 allows external Derived Data only in specified charts/statistics/reports or data products aggregated at >=10-minute intervals with consecutive points >=10 minutes apart for each measure and instrument. It expressly excludes Coinbase data from this permission.
- Clause 9.5 permits use of AI tools/agents for the Permitted Use and own models for Customer Users, but prohibits using the data to train/improve a foundation model offered to non-Customer Users or distributing models trained on the data to non-Customer Users. Clause 23 imposes stricter Coinbase-specific AI/ML restrictions.
- Clause 9.6 permits confidential cloud/IT/data-processing service providers acting on the Customer's behalf for Permitted Use. This does not grant access to arbitrary external collaborators or customers.
- Thus Tardis is a promising individual research/replay source, not a general licence for a public or multi-user trading platform. Obtain written clarification before product use.

Provider sources:
- Tardis Terms (modified 2026-10-28): https://docs.tardis.dev/legal/terms-of-service
- Tardis Bitstamp historical coverage and snapshot notes: https://docs.tardis.dev/historical-data-details/bitstamp
- Tardis normalized tick-level CSV data types: https://docs.tardis.dev/downloadable-csv-files/data-types
- Amberdata market-data licensing FAQ: https://www.amberdata.io/online-market-data-ordering-faq

## 4. Full qualification matrix

The following remain UNKNOWN until exact jurisdiction, account type, product family and API version are identified and evidenced.

| Qualification dimension | Bybit | Coinbase | Kraken | OKX | Binance |
|---|---|---|---|---|---|
| Owner's jurisdiction / KYC eligibility | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Exact serving legal entity / ToS | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Spot eligibility | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Perpetual swap eligibility | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Dated futures / expiry semantics | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Historical trade archive coverage / start date | YES — public BTCUSDT daily CSV listing begins 2020-03-25; current freshness/completeness unverified | UNKNOWN | YES — Spot Time & Sales from each pair's first trade through 2026-09-30 | YES — tick-level trades from 2021-09 | YES — daily/monthly Spot/Futures trade archives; coverage varies by symbol |
| Historical L2 archive coverage | UNKNOWN | UNKNOWN | UNKNOWN — no L2 shown in Time & Sales archive | YES — high-resolution L2 from 2023-03 | NO per-level L2 evidence; percentage-band `bookDepth` only |
| Private order/fill/account streams | UNKNOWN | UNKNOWN | PARTIAL — Kraken's 2026-11-12 release notes say Unified WS supports derivatives private streams and order entry; exact event/snapshot/recovery semantics remain unqualified | UNKNOWN | UNKNOWN |
| REST reconciliation for unknown order outcome | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Client order ID constraints / idempotency semantics | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Timeout / duplicate-submit behavior | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Rate limits and recovery limits | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Sandbox / testnet availability and differences | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Cancel-on-disconnect behavior | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Reduce-only semantics | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| API key permission separation / no-withdrawal scope | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| IP allowlisting | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Fees / funding / settlement specification | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Market-data license / redistribution restrictions | UNKNOWN — API terms restrict benchmarking, resale and commercial exploitation; public-endpoint/API-key applicability needs clarification | UNKNOWN | UNKNOWN — prior permission for certain non-personal commercial public-data uses; redistribution scope needs confirmation | YES — personal non-commercial use only; no redistribution/competing analytics without written consent | YES — CC BY-NC-SA 4.0 non-commercial; no live proprietary execution or commercial order generation |
| Specification change / deprecation policy | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

## 5. Evidence record required for each cell

Every qualified cell must record:
- venue and exact product family (spot, linear perpetual, inverse perpetual, dated future, etc.);
- exact API family/version and endpoint/channel;
- answer: YES / NO / UNKNOWN;
- official source URL and source publication/update date where available;
- date checked;
- test evidence (fixture, sandbox, live public stream, account-level test) and environment;
- limitations, exceptions and unresolved dependencies;
- reviewer and next revalidation trigger.

A general venue help page does not prove a specific API feature. A public endpoint does not prove account eligibility. A sandbox does not prove production behavior. A source document does not prove runtime feed continuity.

## 6. Qualification stages

1. **Public data-only:** public feed availability, terms/data rights, schema, timestamps, trade IDs, snapshot/delta continuity, resync, historical coverage and rate limits.
2. **Sandbox/test execution:** exact product and sandbox eligibility; client order ID constraints; order lifecycle; timeout/duplicate behavior; private streams; reconciliation; reduce-only and cancel semantics.
3. **Personal live eligibility:** owner's actual residence/citizenship where relevant, KYC/account type, serving entity, exact product availability, API automation terms, fee tier, key permissions and local legal requirements. This gate is independent from public data research.
4. **Production approval:** adapter conformance, risk/execution/reconciliation gates, emergency operations, observability, backup/restore and explicit owner authorization.

The lack of a live-eligible venue does not block public data research. The lack of historical L2 does not justify pretending that L2 history exists; it changes which experiments can be concluded.

## 7. Architecture rule: first concrete, second contrasting, then abstract

- Adapter #1 remains concrete and venue-specific while Bybit M2 technical work continues; its live gate remains separate from code/test work.
- A second adapter may be authorized before Bybit M2 acceptance only after explicit technical-readiness and data-rights gates are met; it is not automatically authorized by the calendar or Bybit silence.
- Compare Kraken Spot WS v2 (snapshot + CRC32), Bitstamp (REST seed + WS channels; exact WS contract still UNKNOWN), and OKX (snapshot + prevSeqId/seqId) as materially different candidates. Coinbase Advanced Trade remains an alternative.
- Compare both implementations and their failure/recovery models before defining a generic adapter interface.
- Only then define the smallest shared contracts supported by both. Do not force a lowest-common-denominator interface that erases useful venue-specific guarantees.
- Keep raw source frames, source timestamps and venue-specific evidence. Normalize only into a shared layer with explicit provenance and loss annotations.

## 8. Core data identity principles (target, not current implementation claim)

Future normalized records should carry:
- venue_id;
- internal instrument_id, with a versioned mapping to venue-native symbol/product identifiers;
- exchange event time (and source timestamp semantics);
- local UTC receive wall time;
- host-local monotonic receive time (only comparable within the same host boot);
- connection generation/session identifier;
- raw source reference / payload digest;
- source-specific continuity evidence.

Each adapter owns its own parser and continuity proof. The core consumes a venue-neutral statement of continuity/validity, not Bybit's `u` or `seq`, Coinbase's sequence semantics, or Kraken's checksum as if they were interchangeable.

## 9. Order command contract (future execution scope)

The domain-level command identity should be stable and idempotent. Each venue adapter maps it to the venue's client-order identifier subject to that venue's length, character, uniqueness and retention constraints. After an ambiguous submit timeout, the common process is **reconcile before retry**; the actual lookup endpoints, cursor semantics and duplicate behavior are adapter-specific. This is a design target, not implemented functionality.

## 10. References and current evidence

- Existing preliminary comparison: [NX-RESEARCH-003 — Coinbase/Kraken shortlist (PR #14 branch)](https://github.com/PandaGarry/NEXUS/blob/research/russia-venue-eligibility-v0/docs/research/NX-RESEARCH-003-first-venue-shortlist.md) (documentation research only; contains historical and jurisdiction-dependent conclusions that must be revalidated before selection).
- Bybit recorder prototype: [PR #19](https://github.com/PandaGarry/NEXUS/pull/19).
- Bybit public-feed API research: [PR #17](https://github.com/PandaGarry/NEXUS/pull/17).
- Second adapter qualification issue: [Issue #21](https://github.com/PandaGarry/NEXUS/issues/21).
- Current M2 acceptance checklist: [M2-ACCEPTANCE.md](https://github.com/PandaGarry/NEXUS/blob/prototype/bybit-public-data-recorder-python-v0/experiments/bybit-public-recorder/M2-ACCEPTANCE.md).

## 11. Explicit non-goals

This matrix does not select a live venue, infer the user's residence, authorize account connection, or establish legal advice. No credentials, private API, order placement or live trading are part of the current data-only work.
