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
| Bybit V5 | Linear USDT contracts | BTCUSDT | Primary confirmatory | Public raw smoke exists; synchronized L2 and historical archive coverage remain unverified |
| Bybit V5 | Linear USDT contracts | ETHUSDT, SOLUSDT | Exploratory instrument robustness only | Not yet captured or qualified |
| Bybit V5 | Spot | BTCUSDT, ETHUSDT | Exploratory spot-vs-derivative comparison | Not yet captured or qualified; do not pool with linear contracts |
| Kraken Spot WS v2 | Spot | XBT/USD, ETH/USD | Cross-venue exploratory replication candidate | Full Spot Time & Sales archive documented through 2026-09-30; WS docs reviewed; historical side semantics and data-use terms remain open; no historical L2 evidence |
| Coinbase Advanced Trade | Spot | BTC-USD, ETH-USD | Alternative cross-venue exploratory replication candidate | Protocol qualification not complete |
| OKX | Spot / USDT perpetual | BTC-USDT, ETH-USDT; BTC-USDT-SWAP, ETH-USDT-SWAP | Discovery backlog | Not qualified; exact API/product evidence required |
| Binance | Spot / USDⓈ-M perpetual | BTCUSDT, ETHUSDT | Discovery backlog | Not qualified; exact API/product evidence required |

These are candidates, not assertions that the feeds, archives, account access or products are available to the owner. Candidate inclusion does not imply recommendation, eligibility or permission to redistribute data.

### Kraken historical-data note (checked 2026-11-15)

Kraken publishes complete Spot Time & Sales data for each pair from its first trade through 2026-09-30. The CSV schema is `timestamp, price, volume, type, order_type, misc, trade_id`; the complete archive is split into approximately 2 GB parts with published SHA-256 checksums. This is useful for exploratory trade-flow work on XBT/USD and ETH/USD, but it is not historical L2. The historical `type` values (`b`/`s`) must be verified against WS v2 taker-side semantics before using them as signed taker flow. Historical data availability does not establish redistribution rights or account eligibility.

Official source: https://support.kraken.com/in/articles/360047543791-downloadable-historical-market-data-time-and-sales-


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
