# NX-EXP-001 — Alpha Research Track: Trade-Flow Imbalance Baseline

**Status:** pre-registered falsification experiment; no alpha claim  
**Created:** 2026-11-14  
**Target first report:** 2026-11-28, or explicitly marked blocked if a valid dataset cannot be obtained  
**Owner:** NEXUS research workstream (analysis implementation); owner approval required for venue/account-specific fee and eligibility assumptions

## Objective

Run a small, falsifiable strategy experiment in parallel with data engineering. The objective is not to produce a profitable bot by the deadline; it is to determine whether a simple public-data hypothesis deserves further research after realistic execution costs. The prior expectation is deliberately conservative: short-horizon BTCUSDT taker-flow imbalance is a heavily studied signal and may have no residual edge after spread, fees and impact.

## HYP-001 — short-horizon taker-flow imbalance

**Primary hypothesis/configuration (confirmatory):** On linear BTCUSDT, a 5-second taker-notional imbalance with absolute threshold 0.20 predicts the direction of the next 3-second mid-price move, and retains positive net expectancy under executable-side fills and measured costs.

For each completed 1-second bucket:

- signed notional = sum(price × size) for taker buys minus sum(price × size) for taker sells;
- total notional = sum(price × size) for all trades;
- imbalance = signed notional / total notional;
- primary configuration is frozen now: 5-second rolling window, absolute imbalance threshold 0.20, 3-second forward horizon;
- decision timestamp is the end of the completed bucket; no feature may use trades or book events timestamped after that decision point;
- only one primary configuration is confirmatory. It is not to be replaced by whichever configuration looks best.

**Secondary exploratory grid:** windows 1s / 5s, thresholds 0.10 / 0.20 / 0.30, horizons 1s / 3s / 5s (18 total combinations, including the primary). All non-primary combinations are exploratory, must be labelled as such, and cannot independently justify a positive alpha claim. If inferential p-values are reported for the grid, apply Holm–Bonferroni correction across all 18 tests and also disclose the unadjusted values. No selecting the best of 18 and reporting it as if pre-specified.

## Data qualification

**Confirmatory primary remains Bybit V5 linear BTCUSDT.** Its feature window, threshold and horizon were frozen in one reviewable commit: [9895842](https://github.com/PandaGarry/NEXUS/commit/9895842a7c892260ffa03a175bb3bc39bc6f5146). The broader pre-registered candidate universe is maintained separately in [RESEARCH-UNIVERSE.md](RESEARCH-UNIVERSE.md). Other venues/instruments are exploratory and cannot replace the primary after results are seen.

### Bybit primary data

- The official public directory [BTCUSDT trade archive](https://public.bybit.com/trading/BTCUSDT/) lists daily CSV files beginning 2020-03-25. The listing inspected on 2026-11-15 is not proof of current completeness/freshness; download and validate a permitted sample before analysis.
- Bybit Learn says downloadable historical public data may include order-book snapshots, K-lines, trades and funding rates: https://www.bybit.com/en/learn/bybit-guide/how-to-create-a-bybit-api-key
- NEXUS has not yet located and validated an official L2 archive manifest/file path, schema, depth or date range. A third-party downloader references `quote-saver.bycsi.com/orderbook/linear`, but this is only a discovery lead and is not official completeness/license evidence: https://github.com/Anton495/bybit-data-downloader
- Therefore trade history is a plausible source for predictive-association screening; historical L2 remains UNKNOWN. Do not report executable net alpha from an assumed historical book.

### Cross-venue exploratory data

- **OKX:** official historical-data portal lists tick-level trades from 2021-09 and high-resolution L2 from 2023-03. This is the strongest documented candidate for an exploratory L2 replication, but it remains a separate stratum and does not replace the Bybit confirmatory primary. Archive sample/schema and exact instrument coverage must be verified. OKX historical/API terms restrict data to personal non-commercial use and prohibit redistribution/competing analytics products without written consent.
- **Kraken Spot:** official Time & Sales archive covers each pair from its first trade through 2026-09-30, but it is trade history, not L2. Historical `type` buy/sell semantics must be verified against WS v2 taker-side semantics before using it as signed flow.
- No Spot/derivative datasets are pooled. BTC/USD, BTC-USD and BTCUSDT are not treated as identical instruments.

### Required validation before analysis

For each dataset, verify trade-level records (not only candles), timestamps and precision, trade IDs, taker-side semantics, price, quantity, ordering, duplicate rows, missing days/intervals, timezone, schema changes, instrument specifications and terms. Preserve raw source files privately with checksums; do not commit or redistribute raw exchange data without explicit rights.

Minimum required for an executable-cost conclusion:

- timestamped public trades with trade IDs, side, price and size;
- synchronized L2 quotes or book snapshots sufficient to estimate entry/exit bid/ask and market impact;
- documented missing intervals, time zone and product specification;
- exact instrument metadata for the period.

If archives contain trades but no L2, the archive can support predictive-association screening only. Executable-cost conclusions then require our own synchronized live capture after the data-terms gate is cleared; otherwise publish an explicit data-coverage blocker. Candles alone do not qualify for this trade-flow hypothesis. No assumed fill at mid-price.

## Execution-cost model

For a taker-entry baseline:

- long entry at the first executable ask after the signal; short entry at the first executable bid;
- exit at the opposing executable side after the pre-registered horizon;
- include actual fee schedule for the relevant product/account tier once verified;
- include observed spread and depth-based impact; report data gaps and unobservable impact explicitly;
- stress costs at 1.0×, 1.5× and 2.0× the measured baseline;
- report gross return, fees, spread, impact, net return and break-even round-trip cost separately.

If the user's actual fee tier is unknown, do not invent it. Publish a sensitivity table and keep the final net-alpha verdict provisional.

## Validation protocol

- chronological train / validation / test split; additionally use at least three rolling walk-forward out-of-sample folds;
- purge overlapping labels and embargo at least the maximum forward horizon around split boundaries;
- use block bootstrap (not IID shuffle) for confidence intervals;
- primary configuration is fixed before looking at OOS results; any secondary model selection occurs on training data only and is reported separately;
- for the primary confirmatory test, report the pre-specified effect estimate and 95% block-bootstrap confidence interval; do not tune the primary threshold/window/horizon after seeing OOS data;
- for the 18-combination secondary grid, report all combinations and apply Holm–Bonferroni to the family of 18 inferential tests;
- report trade count, turnover, average holding time, gross/net expectancy, profit factor, drawdown, adverse excursion, fee/spread/impact decomposition and sensitivity to parameter perturbation;
- include no-trade and naive direction baselines;
- do not use random train/test shuffling for time series.

## Stop / continue criteria

**Timebox:** two calendar weeks from the first date on which a complete, validated dataset is available; first report target is 2026-11-28. If usable historical data is not available by that date, publish the blocker and do not silently extend the timebox.

**Reject HYP-001** if any of the following holds:

1. primary net expectancy is non-positive in at least two of three or more walk-forward OOS folds at the verified fee/cost assumptions;
2. the primary block-bootstrap 95% confidence interval for aggregate OOS net expectancy includes zero or is negative;
3. the apparent edge disappears under a 1.5× measured-cost stress;
4. the conclusion depends on mid-price fills or incomplete/unverified book data;
5. the primary result is unstable to the pre-registered small perturbation analysis.

A rejected hypothesis is closed. Any new idea must be registered as a new hypothesis with its own fixed features, parameters, costs and stop rule; do not endlessly retune HYP-001.

## Relationship to the recorder

The recorder is required for validating current book quality, spread/impact assumptions and replay-based tests. Historical trade archives may support an earlier predictive-association screen only after their actual contents and coverage are verified. Infrastructure and alpha research proceed in parallel, with separate evidence.

No private API, credentials, account access, orders, testnet execution or live trading are part of this experiment.
