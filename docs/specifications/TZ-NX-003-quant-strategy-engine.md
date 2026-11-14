# ТЗ-NX-003 — Quant & Strategy Engine

**Status:** PROPOSED — owner review required  
**Version:** 0.1  
**Date:** 2026-11-14  
**Scope:** strategy definition, deterministic evaluation, research, simulation integration, validation, promotion and production decision proposals for NEXUS Crypto v1.  
**Dependencies:** NX-ADR-001, NX-ADR-003, NX-ADR-004, NX-ADR-005, NX-ADR-002, NX-ARCH-001, ТЗ-NX-001, ТЗ-NX-002, future ТЗ-NX-004/005/006.  
**Implementation:** NOT STARTED.

## 1. Purpose

Define a reproducible Quant & Strategy Engine that converts validated market/account context into versioned, auditable strategy decisions and typed trade-intent proposals. The engine must support research through controlled simulation and shadow operation without acquiring execution authority.

The Strategy Engine is not an exchange gateway, portfolio ledger, risk authority or order router. Its output is a proposal. Only the independent Risk Engine may authorize risk-increasing activity; only the Execution Engine may dispatch an approved command.

## 2. Scope

In scope:
- immutable, versioned strategy artifacts and configuration;
- strategy lifecycle, permissions and promotion gates;
- deterministic event-driven evaluation and state recovery;
- typed input contracts with market-data quality/freshness requirements;
- versioned indicators, features and formula dependencies;
- research datasets, experiment provenance and reproducible runs;
- integration with historical, replay, execution-simulation, paper and shadow modes;
- bias/leakage controls, chronological validation and overfitting governance;
- typed TradeIntent output, expiry, evidence and traceability;
- operational monitoring, pause/retire controls and failure handling.

Out of scope:
- exchange API credentials, signing and direct order placement;
- risk-limit calculation or approval authority;
- authoritative account balances, positions, fees, funding or P&L ledger;
- selection of a specific scripting language, notebook product, database, broker or compute platform;
- claims of profitability, production readiness or autonomous live authorization.

## 3. Normative invariants

1. Strategy code has no access to exchange credentials, vault, signer or private exchange endpoints.
2. Strategy output cannot be interpreted as an order or authorization.
3. All risk-increasing intents pass the independent Risk Engine and the Execution Engine's approval validation.
4. Strategy/AI cannot alter, bypass or override risk policy, kill switches, reconciliation holds or data-quality blocks.
5. A strategy run is bound to immutable strategy, configuration, feature/formula, dataset, instrument-spec and engine versions.
6. Missing, stale, invalid, unsynchronized or unknown mandatory inputs fail closed: no new risk-increasing intent.
7. No future information may enter a decision at time t. Event-time and availability/receive-time semantics must be preserved.
8. Financial values and order quantities use the exact representations required by NX-ADR-005; floating point is non-authoritative unless explicitly permitted for bounded analytics.
9. Replaying the same immutable inputs and versions must reproduce the same decisions, subject to explicitly recorded nondeterministic components.
10. A passing backtest is not permission to deploy or trade live.

## 4. Strategy artifact and lifecycle

A Strategy Artifact is an immutable, content-addressed package containing:
- strategy ID and semantic version;
- source/package digest and declared runtime/API compatibility;
- author/owner and creation metadata;
- typed input and output schema versions;
- parameter schema, defaults, bounds and validation rules;
- feature/indicator dependencies with exact versions;
- required venues, market types, instruments and channels;
- required data quality, freshness, coverage and warm-up conditions;
- state schema and migration compatibility;
- resource limits and execution permissions;
- test suite references and validation evidence;
- dependency/license manifest and provenance.

Changing source, parameters that affect behavior, feature definitions, runtime compatibility or required data semantics creates a new immutable version. Existing experiment/deployment records retain the exact prior version. Mutable labels and notes may be metadata but cannot mutate the artifact.

Proposed lifecycle:
- DRAFT — editable research work; cannot be deployed;
- VALIDATING — deterministic/static/data-contract checks running;
- VALIDATED — required tests and research gates passed for a stated scope;
- APPROVED — explicit owner approval for a named operating mode and scope;
- PAPER — paper execution only;
- SHADOW — live data, decisions recorded, no orders;
- DEPLOYED — eligible for an explicitly authorized operating mode;
- PAUSED — no new intents; state and evidence retained;
- RETIRED — no new runs/deployments; historical records remain readable;
- REJECTED — failed or withdrawn with reason.

Lifecycle transitions are explicit, authorized and audited. VALIDATED does not imply APPROVED; APPROVED does not imply live authorization. Live eligibility requires a separate owner-approved release gate and the independent risk/execution controls.

## 5. Input and decision-time contract

Each evaluation receives a versioned DecisionContext:
- evaluation ID, strategy ID/version and deployment ID;
- venue, market type, instrument ID and immutable instrument-spec version;
- canonical market events and source/provenance references;
- event timestamp, venue timestamp, receive timestamp and processing timestamp where available;
- stream recovery state, quality state, sequence/checksum status and freshness;
- feature values with formula/version, input window, warm-up status and quality;
- account/portfolio snapshot references where explicitly required, including snapshot version/time and reconciliation status;
- strategy configuration version;
- deterministic clock/replay position and run mode.

The strategy declares required inputs and maximum tolerated age/coverage. The runtime must reject incomplete contexts and record the reason. It must not silently substitute zero, stale values, last-known values or another venue's data unless that behavior is explicitly declared, versioned and tested.

Event-time and availability-time are distinct. A datum is usable only after it would have been observable by the strategy in the modeled/live environment. Corrections and late events must not rewrite earlier decisions; they create new event lineage and may affect subsequent state according to a declared correction policy.

## 6. Strategy output contract

The only trading-related output is a typed **TradeIntent** proposal. Minimum fields:
- immutable intent ID and idempotency key;
- strategy ID/version, deployment ID and evaluation ID;
- account reference and instrument identity/spec version;
- direction / exposure effect;
- intent type (e.g. open, reduce, close; exact enum finalized with ТЗ-NX-004/005);
- requested quantity or bounded sizing instruction using exact decimal representation;
- optional limit/trigger constraints, time-in-force preference and execution urgency as preferences only;
- decision timestamp, expiry/deadline and maximum acceptable input age;
- rationale/evidence references, feature snapshot digest and relevant market-event offsets;
- confidence/score only when its semantics and calibration are documented; it is never a risk approval;
- strategy state/version and deterministic decision digest.

The contract must distinguish a target exposure proposal from an order instruction. The final command/order schema is owned by ТЗ-NX-004. Strategy output cannot choose or weaken risk limits, override account controls or demand arbitrary signing.

Non-trading outputs (observations, alerts, state updates and diagnostics) use separate typed schemas and cannot be routed to execution.

## 7. Runtime and state model

- Event-driven evaluation is the default; scheduled evaluation is permitted only with an explicit clock and missed-run policy.
- Each strategy instance has isolated state, resource budget, input subscription and output channel.
- State updates are versioned and persisted with event offsets/checkpoints. Restart resumes from a verified checkpoint plus deterministic replay; if continuity cannot be proven, the instance enters RECOVERY_REQUIRED and emits no risk-increasing intent.
- Duplicate events are deduplicated by canonical event identity; out-of-order and late events follow explicit per-feature policies.
- State schema migrations are versioned, tested and reversible or fail closed.
- Backpressure, CPU/memory exhaustion, timeout, panic/crash, invalid output and dependency failure pause the affected instance and alert.
- Strategy runtime is sandboxed with least privilege, bounded CPU/memory/time, controlled filesystem/network access and pinned dependencies.
- No strategy may open arbitrary network connections or spawn unbounded processes.
- Live and research environments do not share mutable account state, secrets or execution capabilities.

The first implementation should be a modular runtime with isolated strategy processes/workers where justified. This specification does not mandate one microservice per strategy or a specific orchestration platform.

## 8. Features, indicators and formula governance

Every reusable feature/indicator must declare:
- stable ID, semantic version and source digest;
- mathematical definition, units, input fields and aggregation rules;
- warm-up/lookback behavior, missing-data behavior and reset/session rules;
- event-time versus processing-time semantics;
- numerical precision and rounding policy;
- deterministic/golden test vectors and expected outputs;
- compatibility and deprecation policy.

A formula name is not a sufficient definition. Similar names with different seeds, smoothing, session boundaries, price source, sample/population variance or missing-value behavior are distinct versions.

For Order Flow features, the strategy engine consumes validated outputs from the analytics layer specified by ТЗ-NX-002. It must retain formula version, data coverage and quality metadata. Unverified chart-only or browser-only values cannot be treated as authoritative strategy inputs.

## 9. Research and experiment governance

An Experiment Record must capture:
- hypothesis and pre-registered success/failure criteria;
- immutable strategy artifact and parameter search space;
- dataset ID, source, venue/instrument universe, time range, sampling and quality exclusions;
- point-in-time instrument universe and delisted/expired instruments where relevant;
- feature/formula and engine versions;
- simulation mode and fidelity level;
- fee, funding, spread, slippage, latency, partial-fill, queue and impact assumptions;
- train/validation/test windows, embargo/purge policy and all transformations;
- random seeds and nondeterministic settings;
- full parameter search history, trial count and selection method;
- metrics, raw trades/fills, diagnostics and known limitations;
- code, configuration and result digests.

Experiments must be reproducible from immutable inputs. A result without provenance is not eligible as validation evidence. Researchers must not silently change the hypothesis or success criteria after seeing holdout results.

## 10. Bias and overfitting controls

Required controls:
- chronological splits; never random-shuffle time series for ordinary financial validation;
- point-in-time availability for market events, instrument universe and metadata;
- no look-ahead through candle completion, revised data, late events, future funding, future listings or post-event corrections;
- survivorship/delisting and symbol-mapping controls;
- purge/embargo around overlapping labels/holding periods where leakage can cross split boundaries;
- training-only fit for normalizers, scalers, feature selection and model calibration;
- validation data used for model selection only under a recorded protocol;
- a sealed out-of-sample holdout not repeatedly queried during tuning;
- walk-forward evaluation across multiple regimes;
- record all trials, not only the best run;
- compare against simple baselines and ablations;
- stress across volatility, liquidity, spread, funding and market regimes;
- report parameter stability and performance dispersion, not only best-case metrics.

No universal numeric minimum for sample size, number of folds, holdout duration or Sharpe threshold is fixed here. Those values depend on strategy horizon, data frequency, instrument universe and statistical power and must be specified in a strategy-specific validation plan before experiments. A threshold must not be selected after observing the desired result.

## 11. Simulation and execution realism

The engine must integrate with the modes and fidelity levels defined in NX-ADR-003:
- historical bar evaluation;
- event/order-book replay;
- execution simulation;
- local paper;
- exchange sandbox;
- live shadow;
- limited live only after separate authorization.

Each run must declare its fidelity level and limitations. The execution model must account for relevant fees, funding, spread, slippage, latency, order type, partial fills, cancellation/rejection behavior and queue assumptions. Limit orders cannot be assumed filled merely because price touched. Marketable orders must consume available liquidity under the selected model; market impact limitations must be explicit.

Replay-based simulation cannot claim full market impact if the historical book is not modified by simulated orders. Queue position on MBP data is an estimate, not an observed fact. Accelerated simulation modes that omit queue position, order-response latency or partial fills must be labelled lower fidelity and cannot replace the full-fidelity validation required by the strategy's execution profile.

Simulation outputs must include gross and net results, fee/funding breakdown, turnover, exposure, drawdown, fill ratio, rejected/canceled/partial orders, latency assumptions, capacity limits and sensitivity to execution assumptions. Unrealistic or missing execution assumptions block promotion.

## 12. Validation and promotion gates

A strategy may advance only through explicit gates:

**G0 — Artifact integrity**
- immutable artifact digest, schema validation, pinned dependencies and license/security scan;
- no credentials, arbitrary network or direct execution capability.

**G1 — Logic correctness**
- unit/golden tests, edge cases, state-machine tests, deterministic replay;
- no look-ahead in event-time tests; no invalid/missing-input silent fallback.

**G2 — Research validity**
- pre-registered hypothesis, dataset provenance, chronological validation, leakage controls, complete trial history;
- baselines, regime/stress tests and documented limitations.

**G3 — Execution robustness**
- appropriate simulation fidelity for strategy horizon/capacity;
- fees, funding, slippage, latency, partial fills, queue and failure scenarios;
- sensitivity analysis and explicit capacity bounds.

**G4 — Paper and shadow**
- paper run with production-like data path and independent risk simulation;
- live shadow with no order dispatch, comparing decisions to observed market/account context;
- monitoring of data gaps, runtime errors, drift and decision latency.

**G5 — Owner and operational approval**
- explicit owner approval for exact strategy version, account, venue, instrument scope and mode;
- Risk Engine policy, Execution controls, ledger/reconciliation, kill switch and rollback verified;
- separate authorization for any limited-live progression.

Passing a gate applies only to the exact artifact, configuration, dataset scope, engine version and operating mode tested. Material changes invalidate affected evidence.

## 13. Interfaces with adjacent systems

- **Market Data (ТЗ-NX-001 / ADR-001/004):** consumes canonical versioned events and quality/recovery state; cannot promote invalid feeds.
- **Order Flow (ТЗ-NX-002):** consumes formula-versioned features and coverage metadata; no dependency on browser memory.
- **Instrument Registry (ADR-005):** consumes immutable instrument-spec versions; unknown mandatory rules block tradable intents.
- **Risk Engine (ТЗ-NX-005):** receives TradeIntent for independent decision; Strategy Engine cannot read or mutate private risk policy beyond allowed capability metadata.
- **Execution (ТЗ-NX-004 / ADR-002):** receives only risk-approved canonical commands; Strategy Engine has no direct interface to private adapters.
- **Ledger (ТЗ-NX-006):** reads derived/account snapshots as versioned inputs; never writes authoritative balances, positions or P&L.
- **AI Orchestrator:** may request research and propose strategy configuration changes through audited workflow; AI output is untrusted and cannot promote/deploy a strategy or authorize an order.
- **Desktop/Web:** configuration, monitoring and results UI only; closing clients does not stop an authorized server-side deployment.

## 14. Security, observability and failure handling

Security:
- strategy runtime receives only allowlisted data and scoped internal APIs;
- no exchange secrets, signer, withdrawal capability or direct private API;
- signed/content-addressed artifacts and dependency pinning;
- sandbox resource/network/filesystem limits;
- tenant/account isolation and authorization on every deployment/configuration action;
- audit of artifact creation, validation, approval, deployment, pause, parameter changes and emitted intents.

Observability:
- per-strategy health, run duration, event lag, input freshness/coverage, dropped/duplicate/out-of-order events;
- decision counts, intent expiry/rejection, runtime errors, CPU/memory and queue depth;
- artifact/config/engine/data digests and correlation IDs;
- alert on stale inputs, state divergence, replay mismatch, drift, repeated invalid output or unexpected intent volume.

Failure behavior:
- invalid or missing mandatory data → no risk-increasing intent;
- state checkpoint/replay mismatch → RECOVERY_REQUIRED;
- strategy timeout/crash/resource breach → pause instance;
- expired intent → reject downstream;
- artifact/config digest mismatch → refuse deployment;
- Risk Engine unavailable → no risk-increasing command;
- reconciliation hold/kill switch → no risk-increasing command;
- ambiguous strategy result → record UNKNOWN/ERROR; never infer a trade.

## 15. Test strategy

Required before acceptance:
- schema and contract compatibility tests for DecisionContext and TradeIntent;
- golden tests for feature/indicator definitions and numeric edge cases;
- deterministic replay tests across restart/checkpoint boundaries;
- event-time/availability-time tests proving no future leakage;
- duplicate, late, corrected, missing, stale and out-of-order event tests;
- state migration and crash-recovery tests;
- property-based tests for invariants and invalid configuration rejection;
- sandbox escape, resource exhaustion and unauthorized network/filesystem access tests;
- experiment reproducibility and digest verification;
- bias/leakage test fixtures and walk-forward protocol tests;
- execution-model conformance tests against known scenarios;
- end-to-end test proving that Strategy Engine cannot dispatch and every risk-increasing intent is independently gated.

Performance tests must define workload before thresholds: event rate, number of active strategies, feature graph complexity, instrument count, state size and latency percentile. No unsupported throughput/latency target is asserted in this draft.

## 16. Acceptance criteria

- [ ] Strategy artifacts are immutable, versioned and content-addressed.
- [ ] Lifecycle transitions and permissions are explicit and audited.
- [ ] DecisionContext includes provenance, event/availability time, quality and spec versions.
- [ ] Mandatory stale/invalid/unknown inputs fail closed.
- [ ] TradeIntent is typed, expiring, traceable and cannot be dispatched directly.
- [ ] Strategy runtime has no exchange credentials, signer or private execution access.
- [ ] Feature definitions include mathematical semantics and golden tests.
- [ ] State recovery and deterministic replay are verified.
- [ ] Research records preserve complete experiment provenance and all trials.
- [ ] Chronological, point-in-time, leakage, survivorship and overfitting controls are enforced.
- [ ] Simulation fidelity and execution assumptions are explicit and appropriate to strategy horizon.
- [ ] Paper/shadow and promotion gates are implemented and evidence-backed.
- [ ] Risk Engine, Execution and Ledger interfaces preserve their independent authority.
- [ ] Failure, security, observability and resource-isolation tests pass.
- [ ] Owner approves the exact strategy scope and operating mode before deployment.

## 17. Open owner decisions

1. Initial strategy runtime language(s) and whether user-authored scripting is allowed in v1.
2. Initial strategy types/horizons and target decision cadence.
3. Initial venue/instrument universe and required data retention for research.
4. Whether research notebooks are in-product or external and how artifacts are imported/signed.
5. Required holdout/walk-forward protocol defaults by strategy horizon.
6. Strategy-level exposure target semantics versus quantity intent; finalize with Risk/Execution specs.
7. Operational deployment limits: max concurrent strategies, compute budget and alerting policy.

These decisions do not authorize implementation of live execution. The runtime and contract design can proceed while platform choices remain open, provided they do not weaken the safety invariants.

## 18. Evidence and references

Primary references consulted on 2026-11-14:
- QuantConnect LEAN Research Guide — look-ahead bias, point-in-time data, walk-forward validation and paper testing: https://www.quantconnect.com/docs/v2/writing-algorithms/key-concepts/research-guide
- QuantConnect Backtesting Research Guide — parameter search and out-of-sample controls: https://www.quantconnect.com/docs/v2/cloud-platform/backtesting/research-guide
- HftBacktest Order Fill — replay limitations, no market impact, partial-fill caveats and queue models: https://hft.readthedocs.io/en/latest/order_fill.html
- HftBacktest Accelerated Backtesting — explicit accuracy trade-offs when queue position, response latency and partial fills are omitted: https://hftbacktest.readthedocs.io/en/latest/tutorials/Accelerated%20Backtesting.html
- ABIDES repository — agent-based discrete-event simulation and configurable pairwise network latency: https://github.com/abides-sim/abides

These sources inform design constraints; they do not establish that NEXUS has selected, integrated or validated any of these engines.

## 19. Verification status

This document is a requirements proposal. No strategy runtime, research workspace, feature registry, simulator, deployment pipeline, paper/shadow runner or strategy has been implemented or tested in NEXUS. No profitability or production-readiness claim is made.

**Prototype Readiness remains BLOCKED.**
