# NEXUS — venue qualification matrix

**Last reviewed:** 2026-11-15  
**Purpose:** compare candidate venues without making any venue the architectural center or assuming user eligibility.  
**Status convention:** YES / NO / UNKNOWN. Every non-UNKNOWN claim is scoped to an exact API/product and backed by a dated source. A documented public feed does not prove account eligibility or production readiness.

## 1. Candidate universe (not a live-venue ranking)

| Candidate | Why it is in the research universe | Current role | Selection status |
|---|---|---|---|
| Bybit | Concrete V5 full-depth public stream and linear derivatives market; first live raw capture succeeded | Reference adapter experiment #1; M2 is the active implementation priority | Not selected for trading |
| Kraken Spot WebSocket v2 | Spot L2 stream sends a WS snapshot and updates with CRC32 checksum; materially contrasts with Bybit full-depth delta-only + REST snapshot model | Protocol/terms research candidate #2; no recorder implementation until Bybit M2 passes | Not selected for trading |
| Coinbase Advanced Trade | Distinct API/product family and useful comparator; do not conflate with Coinbase Exchange API | Alternative technical adapter candidate | Not selected |
| OKX | Tick-level trades + historical high-resolution L2 since 2023-03; snapshot + seqId/prevSeqId live book model | Leading HYP-001 historical-L2 research candidate; no recorder until Bybit M2 | Not selected; terms restrictive |
| Binance | Potentially useful large-scale spot/derivatives API comparator | Discovery backlog; no qualification claim here | Unknown |
| Domestic brokers / listed derivatives venues | May offer a materially different legal, clearing and instrument model | Separate broker/venue adapter research | Not selected |

**Sequencing decision (2026-11-15):** finish and accept Bybit M2 before writing a second recorder. OKX is now the leading historical-L2 research candidate for HYP-001; Kraken remains a strong Spot protocol/checksum contrast and full historical Time & Sales source. Neither is a committed implementation. This avoids two incomplete adapters and lets the second adapter be selected on both protocol contrast and research-data coverage.

## 2. Evidence-backed public-data snapshot (checked 2026-11-15)

| Public-data capability | Bybit V5 linear | Kraken Spot WS v2 | Coinbase Advanced Trade | OKX V5 |
|---|---|---|---|---|
| Public trades channel documented | YES | YES | UNKNOWN in this snapshot | YES |
| Trade ID documented | YES — execution ID `i` | YES — `trade_id`, unique per book | UNKNOWN | YES — `tradeId` |
| Trade event timestamp documented | YES — milliseconds | YES — RFC3339 | UNKNOWN | YES — milliseconds |
| L2 book documented | YES — full depth | YES — aggregated L2 | UNKNOWN in this snapshot | YES — 400 levels on standard `books` channel |
| WS initial book snapshot | NO — full-depth stream is delta-only | YES — snapshot sent by default | UNKNOWN | YES — full snapshot |
| WS incremental updates | YES — delta-only | YES — update messages | UNKNOWN | YES — every 100 ms on `books` |
| Continuity evidence documented | YES — update ID `u` and cross sequence `seq` | YES — CRC32 checksum over top 10 bids/asks | UNKNOWN | YES — `prevSeqId` + `seqId`; checksum deprecated |
| REST snapshot required for initial book | YES | NO for documented WS snapshot flow | UNKNOWN | NO for documented WS snapshot flow |
| Public L3 / order-level feed entitlement | UNKNOWN | UNKNOWN for Spot; separate FIX examples show Futures L3 | UNKNOWN | UNKNOWN |
| Historical trade archive | Public BTCUSDT daily CSV listing from 2020-03-25; completeness/freshness unverified | Spot Time & Sales from each pair's first trade through 2026-09-30 | UNKNOWN | Tick-level trades from 2021-09 |
| Historical L2 archive | UNKNOWN — official path/schema not validated | UNKNOWN — Time & Sales only; no L2 evidence | UNKNOWN | Portal advertises high-resolution L2 from 2023-03; archive sample not validated |
| Live public smoke evidence in NEXUS | YES — 10-minute raw capture/replay | NO | NO | NO |

### Bybit V5 linear evidence

- Full-depth WS topic `orderbook.full.{symbol}` is explicitly delta-only; no initial snapshot is sent. A REST full-depth snapshot must be obtained and aligned with buffered deltas.
- Official synchronization requires consecutive `u` within a session, discarding a delta whose `seq` decreases, discarding deltas older than the REST snapshot `seq`, and matching both `seq` and `u` before applying subsequent deltas.
- `u=1` is a reinitialization signal. `seq` is monotonic but not necessarily consecutive.
- Full-depth stream and REST snapshot exclude RPI orders.
- Public historical trade archive: the official `public.bybit.com/trading/BTCUSDT/` directory lists daily CSVs beginning 2020-03-25; the listing inspected did not establish current completeness/freshness. Bybit Learn says downloadable historical public data may include order-book snapshots, but no official L2 archive path/schema/depth/date range has been validated by NEXUS. A third-party downloader points to `quote-saver.bycsi.com/orderbook/linear`; treat it as an unverified discovery lead, not official completeness or license evidence.
- Bybit API Terms & Conditions (support page last updated 2026-10-20) grant a limited revocable API license for development/testing/support (Section 5.1), prohibit API/Service Data availability or performance benchmarking (6.6), prohibit repackaging/reselling Service Data (6.7), and prohibit commercial exploitation (6.9). Section 2.3 says API use requires API-key identity verification; applicability to technically unauthenticated public market-data endpoints requires clarification. NEXUS therefore keeps raw data private and gates future automated live capture pending explicit terms review.
- NEXUS run #10 captured 8,149 public trade messages, 2,998 full-depth delta messages, 29 pong replies and 1 subscription acknowledgement = 11,177 records exactly. Independent inspection found zero malformed lines and zero raw SHA-256 mismatches. One connection generation was observed.

Official sources:
- Full-depth WS and synchronization: https://bybit-exchange.github.io/docs/v5/websocket/public/full-ob
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

### OKX V5 evidence

- The official historical-data portal lists tick-level trades from September 2021, high-resolution L2 from March 2023, perpetual funding rates from March 2022 and candlesticks from July 2023.
- Standard `books` sends a 400-level initial full snapshot and incremental updates every 100 ms. `books-l2-tbt` (400 levels / 10 ms) and `books50-l2-tbt` (50 levels / 10 ms) are restricted to VIP4+ fee tiers; do not assume access to these higher-frequency channels.
- Current continuity contract is `prevSeqId` + `seqId`: snapshot has `prevSeqId=-1`; normal incremental `prevSeqId` matches the previous `seqId`; maintenance may reset `seqId` lower than `prevSeqId`, after which normal sequencing resumes.
- JSON order-book checksum was deprecated in production on 2026-06-23; checksum fields remain but are always zero. Do not use checksum as integrity evidence.
- Historical-data terms allow personal use including development of one's own trading strategy, but prohibit redistribution and disclaim completeness/accuracy. The API Agreement limits Market Data to personal, non-commercial use and prohibits redistribution, competing data/analytics products and commercialized AI model training without written consent. No raw OKX data may be published or committed to NEXUS.

Official sources:
- Historical data: https://www.okx.com/historical-data
- V5 API/book sequence semantics: https://www.okx.com/docs-v5/en/
- Checksum deprecation: https://www.okx.com/en-sg/help/okx-order-book-channels-checksum-field-deprecation
- API Agreement: https://www.okx.com/help/okx-api-agreement
- Historical-data terms: https://www.okx.com/help/historicaldata-terms-and-conditions

## 3. Full qualification matrix

The following remain UNKNOWN until exact jurisdiction, account type, product family and API version are identified and evidenced.

| Qualification dimension | Bybit | Coinbase | Kraken | OKX | Binance |
|---|---|---|---|---|---|
| Owner's jurisdiction / KYC eligibility | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Exact serving legal entity / ToS | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Spot eligibility | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Perpetual swap eligibility | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Dated futures / expiry semantics | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Historical trade archive coverage / start date | YES — public BTCUSDT daily CSV listing begins 2020-03-25; current freshness/completeness unverified | UNKNOWN | YES — Spot Time & Sales from each pair's first trade through 2026-09-30 | YES — tick-level trades from 2021-09 | UNKNOWN |
| Historical L2 archive coverage | UNKNOWN | UNKNOWN | UNKNOWN — no L2 shown in Time & Sales archive | YES — high-resolution L2 from 2023-03 | UNKNOWN |
| Private order/fill/account streams | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
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
| Market-data license / redistribution restrictions | UNKNOWN — API terms restrict benchmarking, resale and commercial exploitation; public-endpoint/API-key applicability needs clarification | UNKNOWN | UNKNOWN — prior permission for certain non-personal commercial public-data uses; redistribution scope needs confirmation | NO for redistribution/commercial analytics without written consent; personal non-commercial use only | UNKNOWN |
| Specification change / deprecation policy | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

## 4. Evidence record required for each cell

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

## 5. Qualification stages

1. **Public data-only:** public feed availability, terms/data rights, schema, timestamps, trade IDs, snapshot/delta continuity, resync, historical coverage and rate limits.
2. **Sandbox/test execution:** exact product and sandbox eligibility; client order ID constraints; order lifecycle; timeout/duplicate behavior; private streams; reconciliation; reduce-only and cancel semantics.
3. **Personal live eligibility:** owner's actual residence/citizenship where relevant, KYC/account type, serving entity, exact product availability, API automation terms, fee tier, key permissions and local legal requirements. This gate is independent from public data research.
4. **Production approval:** adapter conformance, risk/execution/reconciliation gates, emergency operations, observability, backup/restore and explicit owner authorization.

The lack of a live-eligible venue does not block public data research. The lack of historical L2 does not justify pretending that L2 history exists; it changes which experiments can be concluded.

## 6. Architecture rule: first concrete, second contrasting, then abstract

- Adapter #1 remains concrete and venue-specific while Bybit M2 is completed.
- OKX is the leading historical-L2 research candidate for HYP-001; Kraken Spot WS v2 remains the leading Spot checksum/protocol contrast. Neither recorder is implemented until Bybit M2 acceptance and terms review. Coinbase Advanced Trade remains an alternative.
- Compare both implementations and their failure/recovery models before defining a generic adapter interface.
- Only then define the smallest shared contracts supported by both. Do not force a lowest-common-denominator interface that erases useful venue-specific guarantees.
- Keep raw source frames, source timestamps and venue-specific evidence. Normalize only into a shared layer with explicit provenance and loss annotations.

## 7. Core data identity principles (target, not current implementation claim)

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

## 8. Order command contract (future execution scope)

The domain-level command identity should be stable and idempotent. Each venue adapter maps it to the venue's client-order identifier subject to that venue's length, character, uniqueness and retention constraints. After an ambiguous submit timeout, the common process is **reconcile before retry**; the actual lookup endpoints, cursor semantics and duplicate behavior are adapter-specific. This is a design target, not implemented functionality.

## 9. References and current evidence

- Existing preliminary comparison: [NX-RESEARCH-003 — Coinbase/Kraken shortlist](research/NX-RESEARCH-003-first-venue-shortlist.md) (documentation research only; contains historical and jurisdiction-dependent conclusions that must be revalidated before selection).
- Bybit recorder prototype: [PR #19](https://github.com/PandaGarry/NEXUS/pull/19).
- Bybit public-feed API research: [PR #17](https://github.com/PandaGarry/NEXUS/pull/17).
- Second adapter qualification issue: [Issue #21](https://github.com/PandaGarry/NEXUS/issues/21).
- Current M2 acceptance checklist: [M2-ACCEPTANCE.md](https://github.com/PandaGarry/NEXUS/blob/prototype/bybit-public-data-recorder-python-v0/experiments/bybit-public-recorder/M2-ACCEPTANCE.md).

## 10. Explicit non-goals

This matrix does not select a live venue, infer the user's residence, authorize account connection, or establish legal advice. No credentials, private API, order placement or live trading are part of the current data-only work.
