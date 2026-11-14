# HYP-001 research universe — pre-registration addendum

**Created:** 2026-11-15  
**Status:** candidate universe registered; only one confirmatory configuration is active.  
**Primary specification:** see [NX-EXP-001](NX-EXP-001-alpha-trade-flow-imbalance.md). Its parameters were frozen in the single reviewable commit [9895842](https://github.com/PandaGarry/NEXUS/commit/9895842a7c892260ffa03a175bb3bc39bc6f5146) on 2026-11-14. The venue/instrument candidate universe was registered on 2026-11-15 before any HYP-001 out-of-sample result. Do not modify the primary parameters after inspecting out-of-sample data.

## 1. Confirmatory test — frozen

| Field | Frozen value |
|---|---|
| Venue / API | Bybit V5 |
| Product family | Linear USDT contract |
| Instrument | BTCUSDT |
| Feature | 5-second taker-notional imbalance |
| Signal threshold | Absolute imbalance >= 0.20 |
| Forward horizon | 3 seconds |
| Primary target | Direction and net expectancy of the next 3-second mid-price move, with executable-side costs where valid L2 exists |
| Statistical role | Sole confirmatory configuration |

This primary configuration remains unchanged. A change to venue, product family, instrument, feature window, threshold, horizon, label or cost model is not a harmless parameter substitution: it creates a separate exploratory stratum or a new hypothesis version.

## 2. Candidate universe — registered before results

| Venue | Exact product family | Candidate instruments | Role | Current data / implementation status |
|---|---|---|---|---|
| Bybit V5 | Linear USDT contracts | BTCUSDT | Primary confirmatory | Official public daily trade CSV listing starts 2020-03-25; current archive freshness/schema need inspection; historical L2 path remains unverified |
| Bybit V5 | Linear USDT contracts | ETHUSDT, SOLUSDT | Exploratory instrument robustness only | Not yet captured or qualified |
| Bybit V5 | Spot | BTCUSDT, ETHUSDT | Exploratory spot-vs-derivative comparison | Not yet captured or qualified; do not pool with linear contracts |
| Kraken Spot WS v2 | Spot | XBT/USD, ETH/USD | Cross-venue exploratory replication candidate | Full Spot Time & Sales archive documented through 2026-09-30; WS docs reviewed; historical side semantics and data-use terms remain open; no historical L2 evidence |
| Coinbase Advanced Trade | Spot | BTC-USD, ETH-USD | Alternative cross-venue exploratory replication candidate | Protocol qualification not complete |
| OKX V5 | Spot / USDT perpetual | BTC-USDT, ETH-USDT; BTC-USDT-SWAP, ETH-USDT-SWAP | Leading historical-L2 research candidate; implementation deferred until Bybit M2 | Official portal lists tick trades since 2021-09 and high-resolution L2 since 2023-03; protocol sequence semantics reviewed; terms are personal/non-commercial and restrictive |
| Binance | Spot / USDⓈ-M perpetual | BTCUSDT, ETHUSDT | Discovery backlog | Not qualified; exact API/product evidence required |

These are candidates, not assertions that the feeds, archives, account access or products are available to the owner. Candidate inclusion does not imply recommendation, eligibility or permission to redistribute data.

### Kraken historical-data note (checked 2026-11-15)

Kraken publishes complete Spot Time & Sales data for each pair from its first trade through 2026-09-30. The CSV schema is `timestamp, price, volume, type, order_type, misc, trade_id`; the complete archive is split into approximately 2 GB parts with published SHA-256 checksums. This is useful for exploratory trade-flow work on XBT/USD and ETH/USD, but it is not historical L2. The historical `type` values (`b`/`s`) must be verified against WS v2 taker-side semantics before using them as signed taker flow. Historical data availability does not establish redistribution rights or account eligibility.

Official source: https://support.kraken.com/in/articles/360047543791-downloadable-historical-market-data-time-and-sales-


### OKX historical data and protocol note (checked 2026-11-15)

OKX's official historical-data portal lists tick-level trade history from September 2021, high-resolution L2 from March 2023, perpetual funding rates from March 2022 and candlesticks from July 2023. This makes OKX the strongest currently documented candidate for historical L2 replication of HYP-001, subject to archive inspection and terms.

Current V5 order-book protocol:
- `books`: initial full snapshot of 400 levels, then incremental updates every 100 ms.
- `books-l2-tbt`: 400 levels / 10 ms; `books50-l2-tbt`: 50 levels / 10 ms. Both are restricted to VIP4+ trading-fee tiers; do not assume access.
- Use `prevSeqId` + `seqId` for continuity. Initial snapshot has `prevSeqId=-1`; a normal update's `prevSeqId` matches the prior `seqId`. After maintenance, `seqId` may reset lower than `prevSeqId`, after which normal sequencing resumes.
- JSON book-channel checksum was deprecated in production from 2026-06-23; the field remains but is always zero. Do not use it as integrity evidence.
- For personal historical-data access, OKX's historical-data terms explicitly allow personal retention and development of one's own trading strategy, but prohibit redistribution and disclaim completeness/accuracy. The API Agreement further restricts Market Data to personal, non-commercial use and prohibits redistribution, competing data/analytics products and commercialized AI model training without written consent.

Sources:
- Historical market data: https://www.okx.com/historical-data
- V5 API and book channel: https://www.okx.com/docs-v5/en/
- Checksum deprecation notice: https://www.okx.com/en-sg/help/okx-order-book-channels-checksum-field-deprecation
- API Agreement: https://www.okx.com/help/okx-api-agreement
- Historical data terms: https://www.okx.com/help/historicaldata-terms-and-conditions

OKX is a research candidate, not a venue recommendation or authorization. Archive completeness, instrument coverage, actual downloadable schemas, personal account eligibility and local product eligibility remain to be verified.

### Bybit historical archive note (checked 2026-11-15)

The official Bybit Learn guide says downloadable historical public market data can include order-book snapshots, K-lines, trades and funding rates, and links to the public data portal. The accessible public directory currently exposes `trading/`, `spot/`, `kline_for_metatrader4/`, `premium_index/` and `spot_index/`; the `trading/BTCUSDT/` listing contains daily CSV files beginning 2020-03-25 and, in the listing inspected, extends through 2025-11-16. This verifies a public BTCUSDT trade-archive listing, not a current complete archive through today.

Important caveats:
- The accessible `public.bybit.com` directory does not expose an obvious order-book archive path. Although the Bybit Learn guide mentions order-book snapshots, NEXUS has not located or validated an official L2 archive manifest, file schema, depth or date range. A third-party downloader points to `quote-saver.bycsi.com/orderbook/linear`, but its author explicitly says it is unaffiliated with Bybit; treat this only as a discovery lead, not evidence of completeness or license. Historical L2 remains UNKNOWN until a sample and official terms are verified.
- Before using the trade CSV for HYP-001, download a permitted sample privately and verify timestamp precision, trade IDs, taker-side semantics, duplicate handling, row ordering, missing days and schema changes. Do not infer semantics from filenames.
- The directory listing is not proof that every day is complete or that the archive is current. No raw archive data is committed to the repository.

Sources:
- Third-party archive discovery lead (not an official Bybit source): https://github.com/Anton495/bybit-data-downloader
- Bybit Learn guide: https://www.bybit.com/en/learn/bybit-guide/how-to-create-a-bybit-api-key (historical data description and public portal link)
- Public Bybit data root: https://public.bybit.com/
- BTCUSDT trade archive listing: https://public.bybit.com/trading/BTCUSDT/

## 3. Comparability and statistical rules

- The Bybit Linear BTCUSDT primary remains the only confirmatory HYP-001 test.
- Every other venue/instrument/product-family combination is a separately labelled exploratory stratum. Do not combine spot and perpetual data into one pooled estimate.
- Do not treat BTC/USD, BTC-USD and BTCUSDT as identical instruments. Record quote currency, contract multiplier, tick/lot size, trading schedule, fee schedule, funding and timestamp semantics.
- If inferential p-values are reported across the registered exploratory grid, disclose all tested combinations and apply an appropriate family-wise or false-discovery correction. The existing 18-combination parameter grid remains subject to Holm–Bonferroni as specified in NX-EXP-001.
- Cross-venue comparisons require synchronized event-time semantics, local receive-time provenance, instrument metadata and venue-specific cost assumptions. Do not compare hosted-runner latency.
- If an instrument lacks trade-level IDs, taker-side semantics or reliable timestamps, it is excluded from HYP-001 rather than silently approximated.
- If synchronized L2 is unavailable, report predictive association only. Do not report executable net alpha using mid-price fills or inferred depth.
- Any new feature family, signal definition or material label change receives a new hypothesis ID and preregistration before examining its out-of-sample results.

## 4. Data qualification gate per candidate

Before collecting or analysing a candidate, record:

1. Exact venue, API version, product family, native instrument identifier and quote currency.
2. Official public trade channel and field semantics: stable trade ID, taker/aggressor side, price, quantity, exchange timestamp and batching behavior.
3. Book model: L2/L3, snapshot/delta semantics, sequence/checksum, resynchronization, depth limits and known exclusions.
4. Historical archive availability, date range, granularity, schema, missing intervals and whether data are trades, candles or L2.
5. Market-data terms, retention and redistribution restrictions.
6. Runtime evidence and test commit; public endpoint reachability is not account eligibility.
7. Venue-specific fee, tick/lot, contract and funding metadata needed for cost calculations.

Unknown fields remain UNKNOWN. A candidate is not promoted into an active test merely because a public endpoint responds.

## 5. Freeze and change control

- The primary configuration in NX-EXP-001 is frozen and must remain unchanged in the confirmatory experiment.
- This addendum registers the candidate universe and comparability rules; it does not authorize additional recorders or broaden the current engineering milestone.
- Bybit M2 remains the active engineering priority. Kraken/Coinbase/OKX/Binance protocol research may proceed without implementation, but no second recorder starts before M2 acceptance.
- Any amendment must be a dated, reviewable commit made before the affected data/results are inspected. Preserve prior versions and explain whether the amendment changes the confirmatory test or only adds an exploratory stratum.
