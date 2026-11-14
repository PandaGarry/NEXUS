# NX-ADR-003 — Simulation Fidelity & Strategy Validation

**Status:** PROPOSED — requires owner review  
**Date:** 2026-11-14  
**Scope:** Backtesting, market replay, execution simulation, paper/sandbox operation, strategy validation and research integrity.  
**Evidence baseline:** NX-RESEARCH-001 (HFTBacktest / LEAN / ABIDES landscape) and NX-RESEARCH-002 (Tradoor paper simulator source audit). This ADR defines NEXUS requirements; it does not select or integrate a simulation engine.

## Context

A strategy can appear profitable because a simulator fills orders unrealistically, omits fees/funding, assumes future data, leaks information across validation windows, or tunes parameters repeatedly against the test set. A candle-level backtest cannot establish order-book execution quality. A replay simulator with a static historical book cannot fully reproduce market impact. A paper simulator is not automatically equivalent to exchange execution.

The inspected Tradoor training simulator uses simplified fill assumptions (market orders at last trade; limit orders on touch) and floating-point financial values. HFTBacktest documents useful latency/queue models but also explicitly describes replay limitations, including no market impact from the simulated order and imperfect partial-fill realism against an unchanged historical book. LEAN offers modular reality models; ABIDES is an agent-based market simulator with a different research purpose.

## Decision

NEXUS separates simulation modes and declares fidelity explicitly. No result may be described as live-like or production-grade without matching evidence.

### 1. Simulation modes

| Mode | Purpose | What it can establish | What it cannot establish |
|---|---|---|---|
| Historical bar backtest | Broad strategy screening | Signal logic and coarse portfolio behavior | Intrabar queue, realistic fills or market impact |
| Event/order-book replay | Microstructure and execution research | Behavior against recorded trades/books with declared queue/latency assumptions | Full counterfactual market impact if historical book is immutable |
| Execution simulation | Compare order types, routing and risk policies | Modeled fees, latency, slippage, queue and partial fills within model limits | Exchange truth unless calibrated and validated |
| Local paper | End-to-end system and state-machine validation | Internal pipeline, risk controls, persistence, recovery and accounting | Actual venue fills/liquidity |
| Exchange sandbox/testnet | Protocol and integration validation | Authentication, request schema, order lifecycle and stream handling supported by sandbox | Production liquidity, market impact or identical matching behavior |
| Live shadow/read-only | Production data and decision monitoring without orders | Live data quality, latency and decision trace | Execution outcomes |
| Live limited capital | Controlled operational validation | Actual venue execution under approved limits | General future profitability |

Results from different modes must never be merged without preserving their mode and fidelity metadata.

### 2. Fidelity levels

- **L0 — Signal-only:** no order execution model; useful only for signal diagnostics.
- **L1 — Top-of-book:** bid/ask, spread, taker fees, marketable order sizing against observed displayed liquidity, latency and conservative slippage assumptions.
- **L2 — Market-by-price depth:** L2 depth, order size, book walk, queue approximation, partial fills, cancellations, fees, funding and event timing.
- **L3 — Market-by-order / agent model:** L3 queue position where data exists, order-level events, agent interactions and calibrated market impact assumptions.

Every run records the actual level available per venue/instrument/time segment. Missing depth or sequence quality downgrades the run; the system must not silently substitute a higher fidelity label.

### 3. Required execution model

A simulation configuration must declare:
- data source, venue, market type, instrument-spec version and raw dataset hash;
- event-time semantics, missing-data policy, sequence/book quality and clock alignment;
- order types, time-in-force, latency distributions and network/processing assumptions;
- spread, fees, maker/taker classification, funding settlements and settlement currency;
- slippage, market impact and marketable-order book-walk model;
- queue-position model and cancellation assumptions;
- partial-fill behavior, order expiry, rejection, rate limits and disconnects;
- liquidation, margin and risk-limit model where derivatives are involved;
- random seed and deterministic replay controls.

No limit order may be considered filled merely because the market price touched its limit. Fill requires a declared model for queue priority, traded volume through price, order arrival time and available liquidity. If evidence is insufficient, use conservative no-fill/partial-fill assumptions and mark the limitation.

Market orders must consume available depth and account for slippage; they must not fill unlimited size at last trade or top-of-book price.

### 4. Costs and financial correctness

- Fees use the account's actual or explicitly modeled tier, venue and maker/taker classification.
- Funding is applied only at the documented settlement event and according to contract type, position sign, notional/mark basis and settlement currency.
- Linear, inverse and other contract models use versioned instrument formulas.
- All canonical prices, quantities, fees, balances, margin and P&L use exact decimal/fixed-point/integer representations per NX-ADR-005; approximate analytics must be labeled.
- No omitted cost may be treated as zero unless the run explicitly declares a zero-cost hypothetical baseline.

### 5. Research protocol and leakage prevention

Each strategy experiment separates:
1. training/development data;
2. validation data for model/parameter selection;
3. final untouched test data for one-time evaluation.

Required controls:
- chronological splits; no random shuffle across time for market series;
- purging/embargo where labels or holding periods overlap split boundaries;
- point-in-time instrument universe and delisting/survivorship treatment;
- no future revisions or unavailable-at-the-time metadata;
- feature availability timestamp and strict no-lookahead joins;
- walk-forward evaluation with recorded windows;
- multiple-testing/parameter-search accounting and experiment registry;
- baseline and ablation comparisons;
- out-of-sample drawdown, tail loss, turnover, capacity and cost sensitivity;
- independent final review before performance claims.

Repeatedly tuning against the final test set invalidates it; create a new untouched test period or report the test as contaminated.

### 6. Determinism and reproducibility

A run stores:
- strategy source commit and configuration hash;
- engine, adapter and model versions;
- dataset manifest, checksums and data-quality report;
- instrument-spec versions;
- random seed and clock/latency model;
- full order/fill/fee/funding event log;
- metrics calculation version and output hash.

A deterministic replay of the same immutable inputs and seed must reproduce the same canonical events and metrics within explicitly declared numerical tolerances. Nondeterministic components must be identified.

### 7. Calibration and reality checks

- Compare modeled fills with exchange sandbox and, later, authorized live execution observations.
- Track prediction errors for fill probability, slippage, latency, queue survival and partial-fill ratio by venue/order type/market regime.
- Calibrate only on training/validation observations; preserve holdout data.
- Maintain conservative stress scenarios for volatility spikes, thin books, feed gaps, rate limits, disconnects and funding changes.
- Simulator limitations remain visible in reports; calibration does not convert a replay into a market-impact model.

## Alternatives considered

- **One universal simulator:** rejected; bar backtests, book replay and agent-based simulation answer different questions.
- **Treat paper trading as proof of execution realism:** rejected; internal paper fills cannot validate exchange matching.
- **Always use optimistic fills on touch:** rejected; systematically biases results.
- **Select an engine before defining fidelity requirements:** rejected; engine choice must follow required data, model and acceptance criteria.

## Consequences

Positive:
- Strategy results become comparable only when mode, data and assumptions match.
- Execution assumptions and simulator limitations become explicit.
- Research leakage and overfitting risks are controlled.
- Engine selection can be modular and evidence-based.

Costs/limitations:
- High-fidelity datasets and models are expensive.
- L2 queue position is estimated when MBO/L3 is unavailable.
- Historical replay cannot fully model counterfactual market impact.
- Strategy validation requires disciplined experiment and dataset governance.

## Acceptance criteria

1. Every result is tagged with simulation mode and actual fidelity level.
2. Limit orders are not filled on touch without an explicit queue/trade-through model.
3. Market orders consume declared liquidity and model book walk/slippage.
4. Fees, funding, contract semantics and exact arithmetic are included or explicitly excluded as labeled assumptions.
5. Missing/corrupt/stale market data downgrades or invalidates the run.
6. Train/validation/test splits are chronological and leakage controls are tested.
7. Walk-forward and out-of-sample reports preserve all experiment/configuration metadata.
8. Replaying immutable inputs with the same seed reproduces canonical output.
9. Model calibration and holdout data are separated.
10. Stress tests cover partial fills, latency, disconnects, rate limits, thin books and funding events.
11. Performance claims disclose mode, fidelity, sample period, costs, assumptions and limitations.
12. No simulation result alone authorizes live trading.

## Open questions

- Initial engine composition (candidate landscape is in NX-RESEARCH-001; no engine selected).
- Minimum dataset quality and retention for L1/L2/L3 per launch venue.
- Which latency distributions can be measured from the intended deployment region.
- Whether ABIDES is deferred to later agent-based research rather than core strategy validation.
- Acceptance thresholds for fill-model calibration and strategy robustness.

## Status note

PROPOSED. No simulator has been selected or integrated; no NEXUS strategy backtest, benchmark, profitability test or execution calibration has been run.
