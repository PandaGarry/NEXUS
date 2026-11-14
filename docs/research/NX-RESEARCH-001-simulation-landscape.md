# NX-RESEARCH-001 — Simulation systems landscape

**Date checked:** 2026-11-14  
**Status:** OBSERVED — initial source review; not a full code audit  
**Scope:** HFTBacktest, QuantConnect LEAN, ABIDES  
**Purpose:** Identify complementary simulation capabilities for NEXUS; do not select a dependency solely from feature descriptions.

## Executive result

No single candidate covers all NEXUS research and execution-simulation needs. The three systems address different problems:

- **HFTBacktest:** historical market-data replay with explicit feed/order latency and queue-position models. Strong candidate for L2/L3 execution research, but replay does not change the historical market and therefore does not model market impact. Its documented exchange models also have known limitations for liquidity-taking and partial fills.
- **QuantConnect LEAN:** modular algorithmic trading engine with pluggable datafeed, transaction, result and state-setup components; supports customizable fill, fee, slippage and margin/reality models. Strong architecture/research reference; not automatically a high-fidelity crypto microstructure simulator.
- **ABIDES:** agent-based discrete-event simulation with many agents interacting with an exchange and configurable pairwise network latency. Useful for market-behavior and agent-interaction experiments; not a substitute for replaying real exchange order-book data.

**Recommendation:** retain all three as complementary references. Do not adopt any as NEXUS's sole simulation engine. Evaluate whether a narrow HFTBacktest-inspired execution-replay module is justified after the NEXUS canonical event contract and instrument model are fixed.

## Findings

### 1. HFTBacktest

Official documentation:
- https://hft.readthedocs.io/en/latest/index.html
- https://hft.readthedocs.io/en/latest/order_fill.html
- https://hft.readthedocs.io/en/latest/tutorials/Accelerated%20Backtesting.html

Observed capabilities:
- Tick-by-tick replay using full order-book and trade data; docs describe L2 Market-By-Price and L3 Market-By-Order reconstruction.
- Models for feed latency and order latency.
- Queue-position models, including conservative risk-averse and probabilistic models.
- Exchange models with and without partial fills.

Critical limitations explicitly documented:
- The replayed historical market is not modified by the simulated order; market impact is not modeled.
- Liquidity-taking fills can be unrealistic because replayed depth/trades do not change after the simulated fill.
- Partial fills are supported only under defined model conditions; the documentation still warns about unrealistic cases.
- Accelerated mode intentionally omits queue position and order-response latency and uses simplified fill behavior.

NEXUS implication:
- Useful as a reference and possible benchmark for a Level-2 execution replay simulator.
- Any NEXUS model must expose its assumptions, uncertainty and applicability envelope. It must not label replay PnL as capacity-aware or market-impact-aware.
- Need separate stress models for market impact, latency tails, exchange rejects, cancels, partial fills and changing liquidity.

Evidence class: official documentation, not independent benchmark or local runtime test.

### 2. QuantConnect LEAN

Official documentation:
- https://www.quantconnect.com/docs/v2/lean-engine/getting-started
- https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/key-concepts
- https://www.quantconnect.com/docs/v2/writing-algorithms/live-trading/trading-and-orders

Observed architecture:
- Modular engine with separate result processing, datafeed sourcing, transaction processing, realtime event management and algorithm state setup.
- Backtest fill behavior can be customized with fill models; fee, slippage, margin and other reality models are pluggable.
- Live order state is asynchronous and brokerage responses update order/portfolio state.

NEXUS implication:
- Good reference for strategy/research lifecycle, pluggable models and separation of algorithm from transaction processing.
- The model interfaces and default assumptions need careful review before reuse; default reality models are not proof of realistic fills for a particular crypto venue or liquidity regime.
- LEAN's modularity is an architectural reference, not a mandate to port its engine or language.

Evidence class: official documentation, not a full source-code or runtime audit.

### 3. ABIDES

Official repository:
- https://github.com/abides-sim/abides

Observed design:
- Agent-based interactive discrete-event simulation.
- Many trading agents interact with an exchange agent.
- Configurable pairwise network latency between agents and exchange.
- Message-based design inspired by published NASDAQ ITCH/OUCH protocols.

NEXUS implication:
- Useful for experiments involving agent interaction, strategic response, network latency and synthetic market environments.
- Not the primary tool for validating whether a NEXUS order would have filled against a specific historical crypto order book.
- Market realism depends on agent behavior, exchange model and calibration; synthetic outcomes must not be conflated with historical replay.

Evidence class: repository description/README. Source and model calibration audit not yet performed.

## Comparative matrix

| Dimension | HFTBacktest | LEAN | ABIDES |
|---|---|---|---|
| Historical tick/order-book replay | Core focus | Supported by data/engine, depth depends on data/model | Not primary purpose |
| Feed/order latency | Explicit models | Event/data architecture; model-specific | Configurable network latency |
| Queue position | Explicit queue models | Requires suitable transaction/fill model; not established here as core queue simulator | Emerges from exchange/agent simulation model |
| Partial fills | Explicit model, with caveats | Model-dependent | Exchange/agent-model dependent |
| Market impact | Not modeled in replay | Model-dependent; requires custom realism model | Can emerge in agent/exchange simulation, subject to calibration |
| Multi-agent market dynamics | Not primary focus | Not primary focus | Core focus |
| Portfolio/research framework | Specialized HFT replay | Broad modular research/backtest/live engine | Research simulation environment |
| NEXUS role | Execution replay reference | Strategy/research architecture reference | Agent-based research reference |

Unknown means not established by this limited review; it does not mean unsupported.

## Proposed NEXUS simulation layers

1. **L0 — Deterministic unit/contract tests:** order lifecycle, accounting, fee/funding, risk rules and state transitions.
2. **L1 — Bar/trade replay:** rapid strategy screening; explicitly coarse execution assumptions.
3. **L2 — Order-book replay:** sequence-aware L2 book and trade replay; latency and queue-position models; uncertainty labels for estimated fills.
4. **L3 — Execution stress:** latency distributions, partial fills, rejects, cancel races, rate limits, stale data, disconnects, adverse selection and conservative market-impact scenarios.
5. **L4 — Agent-based experiments (optional):** synthetic participant interactions and market response; separate research evidence from historical validation.

This is a proposed taxonomy, not an approved implementation design.

## Decisions and next actions

- [ ] Keep HFTBacktest, LEAN and ABIDES as separate reference systems; no dependency adoption yet.
- [ ] Complete source-level review of HFTBacktest queue, latency, data validation and exchange models.
- [ ] Inspect LEAN transaction/fill model interfaces and crypto brokerage support at source level.
- [ ] Inspect ABIDES exchange, agent, latency and realism modules; assess relevance to crypto rather than assuming equity-market semantics transfer.
- [ ] Map each candidate's license and dependency footprint before any code reuse.
- [ ] After NX-ADR-001 and NX-ADR-005 stabilize, define NEXUS simulation contracts and choose which layer(s) to implement natively.

## Explicit non-claims

- No local tests, benchmarks or builds were run for these projects in this review.
- No claim is made that any candidate accurately predicts live crypto fills.
- No code has been copied or integrated.
- No simulation engine has been selected or approved.
