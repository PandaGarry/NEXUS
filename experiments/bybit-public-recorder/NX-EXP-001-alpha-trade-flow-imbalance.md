# NX-EXP-001 — Alpha Research Track: Trade-Flow Imbalance Baseline

**Status:** pre-registered falsification experiment; no alpha claim  
**Created:** 2026-11-14  
**Target first report:** 2026-11-28, or explicitly marked blocked if a valid dataset cannot be obtained  
**Owner:** NEXUS research workstream (analysis implementation); owner approval required for venue/account-specific fee and eligibility assumptions

## Objective

Run a small, falsifiable strategy experiment in parallel with data engineering. The objective is not to produce a profitable bot by the deadline; it is to determine whether a simple public-data hypothesis deserves further research after realistic execution costs.

## HYP-001 — short-horizon taker-flow imbalance

**Hypothesis:** On linear BTCUSDT, unusually one-sided taker notional flow over a short rolling window contains predictive information about the next 1–5 second mid-price move.

For each completed 1-second bucket:

- signed notional = sum(price × size) for taker buys minus sum(price × size) for taker sells;
- total notional = sum(price × size) for all trades;
- imbalance = signed notional / total notional;
- pre-register windows of 1s and 5s, thresholds 0.10 / 0.20 / 0.30, and forward horizons 1s / 3s / 5s;
- no feature may use trades or book events timestamped after the decision point.

The fixed parameter grid is for a small train-only selection. The selected configuration is frozen before each out-of-sample fold. No repeated tuning on the final holdout.

## Data qualification

Primary candidate: Bybit's official historical data download page:

https://www.bybit.com/en/derivative-activity/history-data

Bybit's V5 recent-trade endpoint is not an arbitrary-range history service; the official API documentation points to downloadable archives. The archive page is dynamically rendered, so product/category/date coverage must be inspected and recorded before the experiment begins.

Minimum required for an executable-cost conclusion:

- timestamped public trades with trade IDs, side, price and size;
- synchronized L2 quotes or book snapshots sufficient to estimate entry/exit bid/ask and market impact;
- documented missing intervals, time zone and product specification;
- exact instrument metadata for the period.

If only trades or candles are available, HYP-001 may be evaluated for *predictive association*, but it must not be described as executable net alpha. No assumed fill at mid-price.

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
- report trade count, turnover, average holding time, gross/net expectancy, profit factor, drawdown, adverse excursion, fee/spread/impact decomposition and sensitivity to parameter perturbation;
- include no-trade and naive direction baselines;
- do not use random train/test shuffling for time series.

## Stop / continue criteria

**Timebox:** two calendar weeks from the first date on which a complete, validated dataset is available; first report target is 2026-11-28. If usable historical data is not available by that date, publish the blocker and do not silently extend the timebox.

**Reject HYP-001** if any of the following holds:

1. net expectancy is non-positive in at least two of three or more walk-forward OOS folds at the verified fee/cost assumptions;
2. the block-bootstrap 95% confidence interval for aggregate OOS net expectancy includes zero or is negative;
3. the apparent edge disappears under a 1.5× measured-cost stress or small pre-registered parameter perturbations;
4. the conclusion depends on mid-price fills or incomplete/unverified book data.

A rejected hypothesis is closed. Any new idea must be registered as a new hypothesis with its own fixed features, parameters, costs and stop rule; do not endlessly retune HYP-001.

## Relationship to the recorder

The recorder is not a prerequisite for the first historical-trades screening, but it is required for validating current book quality, spread/impact assumptions and subsequent replay-based tests. Infrastructure and alpha research proceed in parallel, with separate evidence.

No private API, credentials, account access, orders, testnet execution or live trading are part of this experiment.
