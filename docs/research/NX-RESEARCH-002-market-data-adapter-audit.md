# NX-RESEARCH-002 — Tradoor market-data adapter audit (initial bounded pass)

**Checked:** 2026-11-14  
**Tradoor repository:** https://github.com/tradoor-terminal/tradoor  
**Audited source revision:** `39a1826816f973ff46c15a848ad1cbe3be7b1dc8`  
**Prior baseline:** `57c9c513e8e014b0226ed72b365d79a75474cd82`  
**Method:** GitHub source inspection at immutable commit URLs; compared server-side and browser-side paths. No local build, live exchange connection, runtime test, or packet capture was performed.  
**Status:** OBSERVED — initial bounded source audit, not a complete per-venue certification.

## 1. Executive findings

1. Tradoor's primary market-data path is browser-to-exchange. `bins/server/src/main.rs` explicitly describes the server as a small API beside static files and says market data normally does not pass through it; the browser streams directly from exchanges and reads historical partitions. The server relay is a fallback when a browser network blocks an exchange. This is not a server-side autonomous market-data service suitable for NEXUS without substantial extraction/replacement.
2. Order Flow (prints and DOM book) is explicitly page-owned. `web/src/lib/orderflow.ts` says its hub belongs to the page, and `web/src/engine/orderflow-streams.ts` describes sockets for browser DOM/tape/footprint panels. Closing the page therefore removes this Order Flow collection path.
3. Book integrity is uneven by venue. Binance, OKX and Deribit adapters carry sequence fields that the shared `BookSync` can validate. Several other adapters parse snapshots/deltas without forwarding sequence identifiers; their incremental books cannot be proven gap-free by the generic sequence check.
4. There are two separate trade parsers with materially different coverage. The server-side parser in `bins/server/src/trades.rs` feeds alerts/flow and assigns zero event time for Kraken Spot and Coinbase Spot; Lighter's server parser reads `market_stats` only, with zero quantity/time and no aggressor side. The browser Order Flow parser has richer Kraken/Coinbase timestamps and a distinct Lighter `trade` channel. These findings must not be generalized across both paths.
5. Open Interest exists as a server recorder, but it is polling-based and only covers eight named venue/market families. It polls every 15 seconds, records minute rows, and marks observations stale after two hours. Its calculations use `f64`; historical reach and venue support differ.
6. A server-side liquidation collector exists for 11 perpetual venues, with one socket per venue and 24-hour retention. Hyperliquid is explicitly absent from the liquidation venue list because its public feed is described as unavailable.
7. The inspected server module list includes `open_interest`, `liquidations`, `trades`, and `flow`, but no funding collector module. Funding-rate collection/normalization is **not implemented in the inspected Tradoor server collectors and remains UNKNOWN at application level**. Official venue APIs do expose funding data for at least Bybit and Hyperliquid; this proves exchange capability, not Tradoor integration. Do not infer collection from paper-trading funding settlement.

## 2. Source inventory

| Area | Immutable source |
|---|---|
| Server topology and module registration | [bins/server/src/main.rs](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/bins/server/src/main.rs) |
| Public venue crate registry | [crates/venues/src/lib.rs](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/crates/venues/src/lib.rs) |
| Instrument catalogue model | [crates/venues/src/catalog.rs](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/crates/venues/src/catalog.rs#L7-L75) |
| Binance product metadata parser | [crates/venues/src/binance.rs](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/crates/venues/src/binance.rs#L160-L195) |
| Server trade stream and parser | [bins/server/src/trades.rs](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/bins/server/src/trades.rs#L192-L304) |
| Browser stream contracts and protocol | [web/src/engine/streams.ts](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/web/src/engine/streams.ts#L1-L115) |
| Browser venue-specific Order Flow protocols | [orderflow-streams.ts](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/web/src/engine/orderflow-streams.ts#L1-L230) and [orderflow-venues.ts](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/web/src/engine/orderflow-venues.ts#L1-L270) |
| Browser book synchronization and DOM state | [web/src/lib/orderflow.ts](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/web/src/lib/orderflow.ts#L306-L362) and [Flow caller/recovery](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/web/src/lib/orderflow.ts#L480-L565) |
| Open Interest recorder | [bins/server/src/open_interest.rs](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/bins/server/src/open_interest.rs#L1-L100) and [venue parsing/normalization](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/bins/server/src/open_interest.rs#L130-L230) |
| Server liquidation collector | [bins/server/src/liquidations.rs](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/bins/server/src/liquidations.rs#L1-L150) |

The latest Tradoor commit at the time of this pass was `39a1826`, a Frost Script crate/path rename. Its inspected diff did not alter the market-data files above. The audit is pinned to that latest observed revision, not to a moving branch name.

## 3. Market-data topology and autonomy

**CONFIRMED from source comments/module wiring:**
- Chart candles/trades are normally received directly by the browser worker from exchange WebSockets.
- Order Flow sockets and state are owned by the page.
- The server relay is a browser fallback, not the normal central ingestion plane.
- Server-side collectors independently exist for Open Interest and selected liquidations.

**NEXUS consequence:** retain Tradoor as a chart/UI and selected analytics reference. Do not treat its current browser stream architecture as the NEXUS autonomous market-data backend. NEXUS needs its own continuously running ingestion service, durable raw/canonical event capture, health state, and replay path.

## 4. Trade coverage and parser discrepancies

The shared browser event contract represents `PrintMsg` with time, price, quantity and a boolean aggressor-buy flag. It does not represent UNKNOWN aggressor explicitly; NEXUS must not copy that limitation. The following are source observations, not independent validation against live exchange packets.

| Venue / market | Browser Order Flow path | Server `trades.rs` path | Initial finding |
|---|---|---|---|
| Binance Spot/Perp | `aggTrade`; event time `T`; taker side derived from buyer-maker flag `m` | `aggTrade`; time `T`; same aggressor inference | OBSERVED supported in both paths |
| Bybit Spot/Perp | `publicTrade`; `T,p,v,S` | `publicTrade`; `T,p,v,S` | OBSERVED supported in both paths |
| OKX Spot/Perp | `trades`; `ts,px,sz,side` | Venue parser handles OKX trade frames | OBSERVED; units need instrument-aware validation |
| Hyperliquid Perp | `trades`; `time,px,sz,side` | Server generic parser behavior requires separate confirmation | Browser path observed; server coverage UNKNOWN |
| Bitget Spot/Perp | `trade`; `ts,price,size,side` | Venue parser present in server trade collector | OBSERVED; contract units require metadata validation |
| Kraken Spot | ISO timestamp parsed with `Date.parse` in browser | Server parser sets `at: 0` | CONFIRMED path divergence; server event-time defect candidate |
| Kraken Perp | `trade` and `trade_snapshot`; exchange time | Server reads `time` | OBSERVED in both paths; snapshot semantics need dedup review |
| Coinbase Spot | `match.time` parsed as ISO timestamp | Server parser sets `at: 0` | CONFIRMED path divergence; server event-time defect candidate |
| Lighter Perp | Dedicated `trade/{market}` channel; `timestamp,price,size,is_maker_ask` | `market_stats` only; emits last price with qty=0, buy=false, at=0 | CONFIRMED path divergence; server parser is not suitable for Delta/Footprint |
| Gate Spot/Perp | Trade channel; timestamp and side/size parsing | Server parser present | OBSERVED; perp size is contracts in inspected parser |
| HTX Spot/Perp | `trade.detail`; timestamp, price, amount, direction | Server parser present | OBSERVED; perp amount/contract units require validation |
| Bitfinex Spot/Perp | `te` event plus initial recent trades; signed amount determines taker side | Server channel adapter filters duplicate `te/tu` forms | OBSERVED; replay/dedup semantics need golden tests |
| Deribit Perp | `trades.*`; timestamp, price, amount, direction | Server parser present | OBSERVED; amount unit conversion differs by instrument family |
| Bitstamp | `live_trades`; microtimestamp | Server parser present | OBSERVED; spot/perp time-unit conversion is venue-specific |
| Aster Spot/Perp | Binance-compatible aggregate trade stream | Server parser uses Binance-compatible path | OBSERVED; venue-specific compatibility needs validation |

### Material correctness issues

- Server Kraken Spot parser reads the trade but writes event time as zero, despite the browser parser parsing the ISO timestamp.
- Server Coinbase Spot parser reads the match but writes event time as zero, despite the browser parser parsing `time`.
- Server Lighter trade path subscribes to `market_stats`, emits `qty=0`, `buy=false`, `at=0`; browser Order Flow separately supports a real trade stream. Treating server output as trades would fabricate zero-volume, non-directional prints.
- Browser event contract uses a boolean aggressor flag, so it cannot express missing/ambiguous aggressor classification. NEXUS canonical contract should use BUY / SELL / UNKNOWN with provenance/confidence.
- Several parsers convert numeric strings to JavaScript/Rust floating-point values. This is acceptable for display/research prototypes only, not as the canonical financial representation.

## 5. Order-book synchronization

The browser `BookMsg` contract has optional `first`, `last`, and `prev` sequence fields. `BookSync` checks Binance snapshot bridging (`first/last`) and checks a delta's `prev` against the last sequence when both are available. If a checked gap occurs it marks the book unsynchronized and returns `gap`. The browser caller must be audited separately for retry/resnapshot behavior.

| Venue | Snapshot / update shape in inspected parser | Sequence carried into shared book contract | Initial integrity assessment |
|---|---|---|---|
| Binance Spot | REST depth snapshot + WS depth updates | `U/u` mapped to first/last | Sequence bridge check implemented |
| Binance Perp | REST depth snapshot + WS depth updates | `U/u/pu` mapped to first/last/prev | Sequence continuity check implemented |
| OKX | Snapshot + deltas | `seqId/prevSeqId` mapped to last/prev | Sequence continuity check implemented |
| Deribit | Snapshot + deltas | `change_id/prev_change_id` mapped to last/prev | Sequence continuity check implemented |
| Bybit | Snapshot + deltas; update ID 1 treated as reset | No sequence forwarded | Gap detection not established |
| Bitget | Snapshot + deltas | No sequence forwarded | Gap detection not established |
| Kraken Spot | Snapshot + deltas | No sequence forwarded | Gap detection not established |
| Kraken Perp | Full snapshot then per-level updates | No sequence forwarded | Gap detection not established |
| Gate Spot/Perp | Whole-book messages | No sequence forwarded | Full-book replacement path; freshness/order still needs validation |
| HTX Spot/Perp | Whole depth messages | No sequence forwarded | Full-book replacement path; freshness/order still needs validation |
| Hyperliquid | Whole L2 book per message | No sequence forwarded | Full-book replacement path; freshness/order still needs validation |
| Lighter | Subscribed snapshot then updates | No sequence forwarded | Gap detection not established |
| Coinbase | Level2 batch snapshot + updates | No sequence forwarded | Gap detection not established |
| Bitstamp | Whole order-book messages | No sequence forwarded | Full-book replacement path; freshness/order still needs validation |
| Aster | Binance-compatible snapshot/delta path | Binance-style sequence fields | Sequence bridge check implemented in shared path |

**Recovery behavior observed in the caller:** Binance/Aster (the REST-snapshot group) hold stream changes, fetch a REST depth snapshot, bridge by update IDs, and retry the snapshot after a detected gap or fetch failure. For other venues, a detected `gap` causes the page to unsubscribe and resubscribe after 300 ms, expecting a fresh whole-book response. Socket state leaving `live` marks the book unsynchronized; REST-snapshot venues fetch again when the socket returns. However, where the adapter supplies no sequence fields, an omitted delta cannot produce a `gap` signal. The resubscribe path therefore does not prove continuity for sequence-less incremental feeds.

**Important distinction:** a parser accepting a book frame is not proof of a continuously synchronized book. For venues without forwarded sequence identifiers, the current code cannot prove delta continuity using the shared `BookSync` sequence checks. Full-book feeds reduce this particular dependency but still require monotonicity/freshness checks and robust reconnect handling.

## 6. Open Interest, liquidations, funding

### Open Interest

The server recorder defines eight families: Binance USDT/USD, Bybit USDT/USD, OKX USDT/USD, Deribit USD and Hyperliquid USD. It polls every 15 seconds and stores minute observations; values are normalized to base-coin units. The source explicitly says Deribit and Hyperliquid do not provide historical OI history, so those are current readings recorded forward. It keeps minute rows for seven days, five-minute rows through 35 days, and hourly rows up to 400 days where the venue supports the history. A reading older than two hours is treated as stale.

Limitations:
- It is a selected-venue recorder, not a unified event stream.
- A 15-second poll cannot capture all intraminute changes.
- Historical coverage differs by venue and market family.
- Numeric calculations use `f64`; not suitable as NEXUS exact financial source of truth.
- The Bybit parser prefers `singleOpenInterest`, otherwise halves `openInterest`; that normalization requires golden tests against current venue semantics.

### Liquidations

The server collector has 11 perpetual venues: Binance, Bybit, OKX, Bitget, Gate, HTX, Bitfinex, Lighter, Aster, Deribit and Kraken. It uses one WebSocket per venue, venue-specific heartbeat/silence/retry settings, batched writes and a 24-hour retention window. Hyperliquid is excluded in the source because its public liquidation feed is described as unavailable. This is meaningful server-side functionality, but it is a bounded liquidation collector, not a general market-data ingestion architecture.

### Funding

The inspected server module registry has `open_interest` and `liquidations` but no funding collector module. The training simulator's funding settlement does not establish live funding-rate collection. Official APIs do expose funding data for at least Bybit (historical `fundingRate` + timestamp and per-instrument funding interval) and Hyperliquid (current funding in `metaAndAssetCtxs`, historical `fundingHistory`, and predicted funding). This confirms exchange-side public capability, not Tradoor application integration. Tradoor funding collection/normalization remains **NOT OBSERVED / UNKNOWN** in the inspected application code; other venues still require dedicated endpoint-by-endpoint research.

## 7. Instrument metadata and quantity normalization

The shared `Product` catalogue model contains canonical market/venue/symbol/base/quote/kind, optional native symbol/name, optional `price_decimals`, 24h quote volume, last price and percentage change. It does **not** carry the trading-rule fields required to validate an order: exact tick size, quantity/lot step, min/max quantity, min notional, contract value/multiplier, settlement currency, linear/inverse flag, price bands, or leverage/margin tiers.

The Binance product parser inspects `PRICE_FILTER.tickSize` to derive `price_decimals`; the inspected parser does not populate LOT_SIZE `stepSize` or `minQty` into the shared Product model. This catalogue is suitable for symbol search and chart display, not for authoritative order validation.

Browser Order Flow quantity normalization is selective:
- OKX perpetuals read `ctVal` from public instrument metadata.
- Gate perpetuals read `quanto_multiplier`.
- HTX perpetuals estimate coins-per-contract from one monthly candle's `amount / vol`.
- Other venues default to a multiplier of 1 in the generic helper unless a protocol performs its own conversion.
- Deribit has a separate conversion: USD-sized perpetual amounts are divided by price; underscore-named USDC instruments are treated as coin amounts.

This is an analytics/display conversion path, not a canonical instrument-specification service. The HTX ratio-from-candle method is an estimate derived from traded data rather than a stable contract-rule record; the fallback-to-1 behavior can conceal missing metadata. NEXUS must never use these fallbacks to validate or size live orders.

Additional arithmetic observation: the inspected catalogue parser, OI parser and browser book/print structures use floating-point numbers. Decimal precision cannot be reconstructed reliably after arbitrary binary-float operations. NEXUS needs versioned exact tick/lot/contract metadata and integer tick/lot or fixed-point values from ingestion through risk and execution.

**Evidence:** [Product model](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/crates/venues/src/catalog.rs#L7-L75), [Binance metadata extraction](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/crates/venues/src/binance.rs#L160-L195), [Order Flow contract-size conversion](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/web/src/lib/orderflow.ts#L391-L430), [Deribit size conversion](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/web/src/engine/orderflow-venues.ts#L130-L152).

### Per-venue metadata parser coverage (source-level summary)

| Venue family | Fields retained by Tradoor Product parser | Key rule fields omitted from Product |
|---|---|---|
| Binance Spot/Perp | tick decimal count derived from PRICE_FILTER.tickSize | LOT_SIZE step/min/max, min notional, price bounds, order types, margin asset/contract details |
| Bybit Spot/Linear Perp | tick decimal count from priceFilter.tickSize; symbol/base/quote | lotSizeFilter qtyStep/min/max/minNotional, leverageFilter, fundingInterval, settleCoin |
| OKX Spot/Linear SWAP | tick decimal count from tickSz; filters linear USDT/USDC swaps | lotSz/minSz/max sizes, ctVal/ctMult, ctValCcy, leverage and risk tiers |
| Deribit Perp | tick decimal count from tick_size; base/quote | contract size, amount step/minimum, settlement and margin rules |
| Gate Spot/Perp | spot precision or order_price_round precision | amount precision, quanto multiplier and min contract/risk rules |
| Bitget Spot/Perp | pricePrecision/pricePlace | quantity step/minimum, contract value, settlement/margin constraints |
| Kraken Spot/Perp | pair_decimals or tickSize precision | lot decimals/minimum and complete contract/settlement rules |
| HTX Spot/Perp | tpp or price_tick precision | amount precision, contract_size, minimum volume and margin rules |
| Lighter Perp | price_decimals | quantity step/precision and full market trading constraints |
| Hyperliquid Perp | max price decimal places derived from 6 − szDecimals | five-significant-figure rule, separate size step and margin tiers are not represented in Product |
| Coinbase Spot | quote_increment-derived price decimals | base_increment, minimum size/funds and maximum size |
| Bitfinex Spot/Perp | no explicit tick; source comments describe five significant figures | exact price/amount steps and contract/margin constraints |

The omitted-field list is a parser-to-Product comparison, not a claim that the exchange API lacks those fields. Official endpoint documentation confirms several omitted fields exist. Exact mapping and semantics must be validated with venue documentation and captured fixtures before any adapter is approved for execution.

### Hyperliquid precision semantics — correction after official-doc verification

The initial interpretation that the parser incorrectly assigns size precision to price precision was too strong and is withdrawn. Hyperliquid's official rule states that perpetual prices may have up to five significant figures and no more than `6 - szDecimals` decimal places; size itself is rounded to `szDecimals`. Therefore Tradoor's calculation `6 - szDecimals` is consistent with the documented maximum decimal-place constraint for perp prices.

However, a single `price_decimals` field still does not fully represent the rule: it omits the five-significant-figures constraint, keeps size step/precision implicit, and cannot express separate spot/perp maximum decimal bases (spot uses MAX_DECIMALS 8). NEXUS must model venue-specific price precision rules and quantity precision independently, including significant-figure constraints where applicable.

**Evidence:** [Tradoor Hyperliquid parser lines 51–69](https://github.com/tradoor-terminal/tradoor/blob/39a1826816f973ff46c15a848ad1cbe3be7b1dc8/crates/venues/src/hyperliquid.rs#L51-L69); [Hyperliquid official Tick and Lot Size rules](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/tick-and-lot-size).

## 8. Private execution boundary

The inspected topology and venue source registry establish public market-data parsing, not authenticated private account streams or order placement. No evidence in this bounded pass establishes signed private REST, authenticated user streams, order lifecycle tracking, fill reconciliation or safe retry semantics for the listed venues. Mark all such capabilities **UNKNOWN**, not supported or unsupported, until their own source-level audit is complete.

## 9. NEXUS decisions implied by this audit (proposed, not owner-approved)

1. Do not use Tradoor's browser Order Flow hub as NEXUS's autonomous feed.
2. Keep chart/UI reuse separate from backend market-data ingestion.
3. Define a canonical event contract with explicit UNKNOWN aggressor, exchange/event/receive/process timestamps, integer ticks/lots or fixed-point decimals, instrument metadata version, sequence scope, quality state and raw-payload reference.
4. Treat each venue + market type + channel as a separate capability row; never infer private execution from public WS support.
5. For sequence-less delta feeds, require a documented recovery/freshness policy and mark confidence/quality degraded when continuity cannot be proven.
6. Add golden packet fixtures and differential tests for the Kraken/Coinbase timestamp divergence and Lighter server/browser trade divergence.
7. Audit contract-size conversion, inverse/linear units and exact arithmetic before reusing any quantity normalization.
8. Keep funding and private execution UNKNOWN until evidence is gathered.

## 10. Official API documentation cross-check (2026-11-14)

The following official references confirm that several instrument/funding fields exist at the exchange API level but are not carried into Tradoor's shared catalogue/parser:

- Binance USDⓈ-M `exchangeInfo` documents `PRICE_FILTER`, `LOT_SIZE`, `minQty`, `maxQty`, `stepSize`, notional and order filters. Tradoor's Binance Product parser currently extracts only tick decimals from `PRICE_FILTER.tickSize`. [Official Binance docs](https://developers.binance.info/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data).
- Bybit `/v5/market/instruments-info` exposes `priceFilter`, `lotSizeFilter`, `fundingInterval`, `settleCoin`, leverage filters and pagination. Tradoor's parser extracts price tick decimals and selected display fields, but not the lot/risk/funding metadata. [Official Bybit docs](https://bybit-exchange.github.io/docs/v5/market/instrument).
- Bybit `/v5/market/funding/history` exposes historical `fundingRate` and `fundingRateTimestamp`. This confirms public API capability; no Tradoor collector was found in the inspected server source. [Official Bybit docs](https://bybit-exchange.github.io/docs/v5/market/history-fund-rate).
- OKX public instrument metadata includes `tickSz`, `lotSz`, `minSz`, `ctType`, `ctVal`, `ctValCcy`, `settleCcy`; Tradoor filters to linear USDT/USDC swaps and retains tick decimals but not contract/lot metadata in Product. [Official OKX docs](https://my.okx.com/docs-v5/en/).
- Hyperliquid `metaAndAssetCtxs` includes `funding`, `openInterest`, `markPx`, `oraclePx`; its `meta` provides `szDecimals` and margin tables. Tradoor's current parser uses mark/volume/previous price for catalogue rows but does not map funding/OI from this context. [Official Hyperliquid perpetual API docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals).

These references are protocol capability evidence, not runtime tests or proof of all current venue account/region eligibility.

## 11. Scope closure and next bounded work

This pass closes only the first source-topology/trade/book/OI/liquidation scan. It does **not** close the full exchange capabilities matrix.

Next bounded package:
- inspect the browser `BookSync` caller and reconnection/resnapshot lifecycle;
- complete a per-venue instrument-rule audit: exact tick/lot sizes, min/max quantity/notional, contract multiplier, settlement, inverse/linear semantics and margin tiers;
- locate and audit funding-rate support (or confirm its absence within the server/browser source tree);
- enumerate private API/order/user-stream capabilities separately;
- produce a normalized per-venue capability matrix with evidence and explicit UNKNOWN cells.

**Not performed:** local tests, CI, live exchange connectivity tests, packet capture, benchmark, security review, private API certification, or legal/license review.


## 10. Bounded follow-up — funding and private execution capability (2026-11-14)

**Scope:** Four priority derivatives venues (Binance USDⓈ-M, Bybit linear/inverse, OKX SWAP, Hyperliquid perps); Tradoor source paths reviewed at HEAD `6ab38775f8f95a2b0237d8663a15405fa00465c6`. This is a source/documentation capability audit only. No credentials, live account, signed request, order, sandbox session, packet capture, or runtime test was used.

### 10.1 Tradoor revision check

The new Tradoor HEAD `6ab3877` changes only `web/src/components/IndicatorPicker.tsx` (adds a Community showcase link). It does not change the previously audited market-data or execution-related files. The audit baseline for this follow-up is therefore `6ab38775f8f95a2b0237d8663a15405fa00465c6`; prior market-data observations remain pinned to `39a1826` unless re-read at this HEAD.

### 10.2 Funding capability — venue API vs Tradoor integration

| Venue | Public current/next funding capability | Historical capability | Tradoor application integration |
|---|---|---|---|
| Binance USDⓈ-M | `GET /fapi/v1/premiumIndex`: latest funding rate, next funding time, mark/index price and response time. `GET /fapi/v1/fundingInfo` supplies adjusted interval/cap/floor for affected symbols. | `GET /fapi/v1/fundingRate`: funding rate/time, mark price, rate type; up to 1000 rows; request-weight/rate constraints apply. | NOT OBSERVED in inspected server collectors / venue registry. |
| Bybit linear/inverse | `GET /v5/market/tickers`: fundingRate, nextFundingTime, fundingIntervalHour, mark/index, OI. | `GET /v5/market/funding/history`: rate and funding timestamp; linear/inverse; max 200 rows/request; instrument endpoint supplies interval. | NOT OBSERVED in inspected server collectors / venue registry. |
| OKX SWAP | Official API catalogue exposes public funding-rate endpoints; exact live-field/interval mapping and current endpoint behavior remain to be independently captured in a fixture before implementation. | Funding history endpoint exists in public API surface; exact pagination/retention contract remains OPEN for this pass. | NOT OBSERVED in inspected server collectors / venue registry. |
| Hyperliquid perps | `POST /info` type `metaAndAssetCtxs` returns per-asset funding, markPx, oraclePx and openInterest alongside perp universe metadata. | Separate historical funding retrieval and retention contract not yet verified in this bounded pass. | NOT OBSERVED in inspected server collectors / venue registry. |

**Interpretation constraints:**
- These are venue API capabilities, not proof that Tradoor ingests, persists, normalizes, or reconciles funding.
- Funding rate is a dimensionless rate whose application to cash flow depends on venue contract model, settlement currency, position sign/notional convention, and the actual settlement timestamp. Never multiply a rate by a generic display notional without an instrument-specific formula.
- Current/indicative rate, predicted rate, and settled historical rate are distinct event types. Store source kind, observation time, settlement time, interval, raw value, and instrument-spec version separately.
- Do not assume a fixed 8-hour interval. Binance exposes interval adjustments; Bybit exposes interval per instrument; other venues require their own metadata semantics.
- Funding settlement must ultimately reconcile to private account ledger events, not be inferred solely from public funding-rate observations.

### 10.3 Private account and execution capability — inspected Tradoor paths

| Capability | Tradoor source evidence | Status |
|---|---|---|
| Exchange private REST signing / secret handling | `crates/venues/src/lib.rs` explicitly describes the crate as public API URLs/parsers. No private signed trading client was observed in the inspected venue crate. | NOT OBSERVED |
| Place/amend/cancel exchange orders | `bins/server/src/relay.rs` allow-lists public market-data routes only; tests explicitly reject Binance `/fapi/v1/order`, OKX `/api/v5/trade/order`, and Deribit private trading routes. | NOT OBSERVED; relay is explicitly not an execution proxy |
| Private account/order WebSockets | Inspected server and browser stream registries expose public market-data paths; no private account/order adapter was observed in those paths. | NOT OBSERVED |
| Fills / partial fills / order lifecycle | No exchange-private fill/order event adapter observed in inspected paths. Paper simulator is separate and does not establish live exchange execution. | UNKNOWN / NOT OBSERVED |
| Account balances / positions | `bins/server/src/account.rs` and `session.rs` implement Telegram-linked application identity and browser sessions, not exchange account authentication or positions. | NOT OBSERVED |
| Reconciliation / restart recovery | No exchange order/fill reconciliation path observed in inspected execution-related paths. | NOT OBSERVED |
| Secret vault / scoped key permissions | No exchange API-key vault or key-permission management observed in inspected paths. | NOT OBSERVED |

This does **not** claim mathematical proof that no private-execution code exists anywhere in every branch or historical revision. It records the result of the bounded source paths reviewed and the explicit public-only design of the venue crate and relay.

### 10.4 Official private API capability baseline (not Tradoor implementation)

- **Binance USDⓈ-M:** signed TRADE/USER_DATA endpoints use API key + HMAC SHA-256 signature and timestamp/recvWindow. The order endpoint is asynchronous; private user-data streams include `ORDER_TRADE_UPDATE` and `ACCOUNT_UPDATE`. User-data listen keys require keepalive; the stream has a 24-hour connection lifecycle. The user stream is important for fills/account changes but must be reconciled against REST snapshots after reconnect.
- **Bybit V5:** `POST /v5/order/create` accepts a user-defined `orderLinkId`; acknowledgement is explicitly asynchronous and the docs direct clients to WebSocket for order status. The private execution topic reports executions including partial fills; private topics require authentication. A successful create response is not a final fill.
- **OKX V5:** private REST signing requires API key, secret, passphrase, timestamp and HMAC-SHA256/Base64 signature. Private WebSocket has explicit login and private account/order/position channels. `clOrdId` is user-defined and can be used for query/cancel/amend while pending, but uniqueness is not enforced historically; NEXUS must keep its own globally unique immutable command ID and cannot rely on venue client IDs as the only idempotency mechanism.
- **Hyperliquid:** public `/info` supports read-only account queries such as open orders and user fills (up to 2000 recent fills per response; by-time query also has documented result/history caps). Trading is a separate signed exchange-action path; public `/info` queries are not evidence of a private order stream or of an idempotent create-order API. Exact order submission/cancel/signing/reconnect contract remains for a dedicated follow-up before adapter design.

### 10.5 NEXUS implications / required controls

1. Keep public market data, private account state, and order command transport as separate adapter interfaces and security domains.
2. Treat REST order acknowledgements as command acceptance only where the venue says so; order state and fills arrive asynchronously.
3. Persist an immutable NEXUS command ID and client order ID before dispatch. On timeout or connection loss, mark outcome UNKNOWN and query/reconcile before any retry; never blindly resend.
4. Deduplicate executions using venue execution/trade IDs, preserve raw events, and model partial fills, corrections, busts and out-of-order updates.
5. On startup/reconnect, reconcile open orders, recent fills, positions, balances and ledger events against venue snapshots with explicit watermarks; do not declare account state healthy until differences are resolved or quarantined.
6. API keys must be least-privilege (trade/read only, no withdrawal), IP-restricted where supported, encrypted in a vault, redacted from logs, and unavailable to the AI Orchestrator.
7. Funding accounting belongs in the financial ledger and must be tied to actual exchange settlement/account events; public rates are forecasts/market observations, not cash ledger entries.

### 10.6 Exit criteria and remaining UNKNOWN

This bounded pass closes the initial four-venue capability survey, not production adapter certification. Before an adapter implementation is specified, capture versioned official fixtures for:
- OKX funding current/history response, interval semantics and pagination;
- Hyperliquid historical funding and complete signed order/cancel/update lifecycle;
- exact private order/execution/account stream schemas and reconnect/replay limits for all selected venues;
- exchange-specific order query retention, client-ID constraints, duplicate behavior, rate limits and error ambiguity.

No live trading capability is approved by this memo. The venue shortlist itself remains a proposed research priority, not an owner-approved launch scope.
