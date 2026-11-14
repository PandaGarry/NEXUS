# NX-RESEARCH-006 — Reference Platform Fit Assessment

**Status:** IN PROGRESS — evidence-backed first pass; no upstream component selected for integration  
**Review date:** 2026-11-14  
**NEXUS baseline:** PR #10 branch `foundation/domain-kernel-reference-v0`  
**Assessment scope:** NautilusTrader execution/trading runtime as the first deep candidate; role boundaries for Tradoor, LEAN and Hummingbot  
**Decision class:** Research recommendation only; not an ADR, owner approval, dependency pin or license opinion

## 1. Executive result

NautilusTrader is a serious candidate for reuse of selected trading-runtime capabilities. It is **not approved as the complete NEXUS trading core**.

Its documented strengths are material:
- Rust-native event-driven kernel with Python control/orchestration interfaces;
- shared domain model for orders, positions, instruments and accounts;
- market-data and execution engines with adapter boundaries;
- event-sourced order lifecycle and explicit handling of unknown command outcomes;
- startup and recurring execution reconciliation;
- backtesting over L1/L2/L3 data with configurable fill, liquidity-consumption and queue assumptions.

The same primary documentation exposes several material differences from NEXUS contracts:
1. The built-in RiskEngine is a useful validation layer, not an independent NEXUS authorization boundary. Some cancel/query routes bypass it; order paths can branch through emulators and execution algorithms.
2. The built-in cache persistence is asynchronous. The execution policy explicitly says persistence failures are logged and sending does not wait for durable storage. This does not satisfy NEXUS's required durable-before-dispatch outbox boundary.
3. NautilusTrader does not promise universal exactly-once delivery/application. It has scoped trade-ID deduplication and unknown-outcome handling, but those guarantees depend on retained state and venue adapter semantics.
4. Numeric value types use bounded integer precision modes (128-bit / up to 16 decimal places, or 64-bit / up to 9). This differs from the unbounded Python reference oracle and is not yet proven sufficient for every NEXUS instrument, fee, funding and accounting domain.
5. Its reconciliation is valuable, but cannot replace NEXUS's separate ledger journal, exposure reservations, freshness barrier and cross-contract handoff.
6. The inspected README/MIGRATION_V2 guide describes the v2 Rust/PyO3 transition; legacy v1 is on `develop_v1` and receives only critical security backports for approximately three months after cutover, with no feature/parity work. This increases API migration and version-selection risk.

**Recommendation:** keep NautilusTrader as the leading *candidate execution/runtime component* for a controlled compatibility prototype, behind NEXUS-owned command authorization, durable outbox, independent Risk Engine, ledger and recovery barriers. Do not fork, vendor or connect it to a live account yet. A narrow source audit and conformance spike must decide whether to embed selected crates, use it as a process boundary, or reject it.

## 2. Evidence and review method

This pass uses official documentation and a pinned source-inspection snapshot: upstream commit `97ecbafd6621241a2222ef5a31cf887c6d96d950` on the `develop` branch, observed on 2026-11-14. This SHA is an evidence anchor for the inspected source, not an approved release/dependency pin. The `develop` branch and `latest` documentation are moving targets.

Primary references:
- Repository and overview: https://github.com/nautechsystems/nautilus_trader
- Architecture: https://nautilustrader.io/docs/latest/concepts/architecture/
- Execution: https://nautilustrader.io/docs/latest/concepts/execution/
- Execution policies: https://nautilustrader.io/docs/latest/concepts/execution/policies/
- Execution reconciliation: https://nautilustrader.io/docs/latest/concepts/execution/reconciliation/
- Value types: https://nautilustrader.io/docs/latest/concepts/value-types/
- Backtest data and venues: https://nautilustrader.io/docs/latest/concepts/backtesting/data-and-venues/
- Fill models: https://nautilustrader.io/docs/latest/concepts/backtesting/fill-models/
- License at inspected snapshot: https://github.com/nautechsystems/nautilus_trader/blob/97ecbafd6621241a2222ef5a31cf887c6d96d950/LICENSE
- v2 migration guide at inspected snapshot: https://github.com/nautechsystems/nautilus_trader/blob/97ecbafd6621241a2222ef5a31cf887c6d96d950/MIGRATION_V2.md

This is a bounded documentation and targeted source-discovery pass against upstream snapshot `97ecbafd6621241a2222ef5a31cf887c6d96d950`, not a complete source audit, build, security review, performance benchmark, adapter certification or live test. Any behavior not explicitly established below remains UNKNOWN.

## 3. Fit against NEXUS contracts

| NEXUS boundary | NautilusTrader evidence | Fit | Required NEXUS treatment |
|---|---|---|---|
| Market data | DataEngine routes quotes, trades, bars, books and custom data through client adapters | Candidate / partial | Verify channel semantics, sequence recovery, timestamps, provenance, freshness and adapter capability per venue |
| Instrument/value model | Price, Quantity and Money value types; standard/high precision modes | Partial | Compare every target venue's tick/lot/contract/settlement constraints; no implicit precision downgrade; retain NEXUS canonical instrument-spec version |
| Order lifecycle | Event-sourced order state with transition and identity checks | Strong reference | Map event model to NX-ADR-002 and NX-IF-001/003; preserve NEXUS command IDs and evidence lineage |
| Pre-trade risk | Built-in RiskEngine validates precision, bounds, reduce-only, notional, balance/margin, rate and trading-state constraints | Partial | NEXUS independent Risk Engine remains authoritative; Nautilus checks are defense-in-depth only |
| Command routing | Submit/modify may route via OrderEmulator or ExecutionAlgorithm before RiskEngine; cancel/query can bypass RiskEngine | Gap | Place NEXUS authorization at a non-bypassable gateway; explicitly classify cancel/reduce-only/emergency paths under NX-IF-005 |
| Durable dispatch | Cache attempts asynchronous enqueue before client call; send does not wait for durable storage | Critical gap | NEXUS durable outbox must commit and fsync/transactionally persist before any venue dispatch; adapter must only receive already-authorized persisted commands |
| Ambiguous outcomes | Unknown outcomes remain in-flight for stream/query/poll/reconciliation; retries require safety proof | Good pattern / partial | Preserve NEXUS OUTCOME_UNKNOWN; own stable semantic command ID, venue idempotency evidence and retry gate |
| Deduplication | Repeated fill trade IDs are guarded; no universal exactly-once guarantee, dependent on retained cache state | Partial | NEXUS canonical fill identity, durable inbox, correction/bust handling and ledger idempotency remain separate |
| Reconciliation | Startup and recurring order/position reconciliation; unresolved reports can block actor startup; missing position report is not flat | Strong reference / partial | Integrate as venue-state evidence only; reconcile against NEXUS ledger/exposure snapshots and freshness barriers |
| Ledger/accounting | Position and account projections are part of runtime; reconciliation may synthesize state from reports | Not equivalent | NEXUS immutable balanced journal, fee/funding accounting, valuation policy and correction lineage remain authoritative |
| Backtesting | L1/L2/L3 matching, book walk, liquidity consumption, optional queue tracking and fill models | Strong research candidate | Calibrate against venue-specific data; do not equate replay fills with executable market truth |
| Multi-venue | Framework supports multiple venues and cross-venue strategies | Out of v1 scope | Do not enable multi-venue execution or cross-venue collateral in NEXUS v1 |

### 3.1 Independent Risk Engine boundary

The documented Nautilus RiskEngine checks a useful set of order invariants, including instrument precision, quantity bounds, reduce-only behavior, notional constraints, cash-account balance impact, rate limits and trading-state restrictions.

However, its command graph is not equivalent to the NEXUS approval contract. The documentation states that cancel and query commands can route directly to other execution components and do not pass through the RiskEngine. Submission and modification can also branch through emulation or execution algorithms.

This is not necessarily a defect in NautilusTrader's intended design. It means NEXUS must not delegate its final authorization boundary to the built-in RiskEngine. NEXUS must own a non-bypassable adapter/gateway boundary that validates a payload-bound RiskApprovalCapability for every state-changing command, with explicitly specified emergency and risk-reduction exceptions.

### 3.2 Durable outbox boundary

NEXUS NX-ADR-002 / NX-IF-001 / NX-IF-003 require a durable command record and risk approval to exist before external dispatch. The NautilusTrader execution policy describes an asynchronous cache enqueue: persistence is attempted before transport, but persistence failure is logged and the send does not wait for durable storage.

Therefore, the default NautilusTrader dispatch path cannot be treated as satisfying the NEXUS durable-outbox invariant. A wrapper that persists first may still be insufficient if the built-in strategy/engine APIs can dispatch around it. This needs a source-level proof of a single enforceable integration point, or an adapter architecture that makes direct dispatch inaccessible to strategies.

### 3.3 Unknown outcomes and reconciliation

NautilusTrader's explicit unknown-outcome handling is aligned with NEXUS's refusal to blindly resend after an ambiguous timeout. Its reconciliation model also correctly distinguishes an explicit flat-position report from a missing/null report, and can prevent actors from starting while covered reconciliation remains unresolved.

Important limitations remain:
- command delivery is not exactly once;
- some adapter retry behavior is explicitly documented as not fully conformant;
- duplicate protection is scoped rather than universal;
- recovery depends on retained cache evidence and venue history;
- a position reconciliation result is not a substitute for complete fill economics or an immutable financial journal.

NEXUS should reuse these patterns and tests, not delegate its global recovery barrier or accounting authority.

### 3.4 Exact numeric compatibility

The upstream repository documents two precision modes for core `Price`, `Quantity` and `Money` values:
- high precision: 128-bit integers, up to 16 decimal places;
- standard precision: 64-bit integers, up to 9 decimal places.

The default Python wheels are documented as high precision; pure Rust crates default to standard precision unless the `high-precision` feature is enabled.

This is materially better than floating-point authoritative financial values, but it is not equivalent to an unbounded exact-decimal model. Before adoption, NEXUS must test:
- maximum coefficient and scale for every selected venue/instrument;
- prices, base/quote quantities, contract sizes and multipliers;
- fees, rebates, funding, margin, notional and P&L;
- multiplication/addition overflow boundaries;
- conversions between currencies and instrument units;
- serialization round-trips and Python/Rust parity;
- historical instrument-spec versions and precision changes.

No precision mode is approved by this research memo. The NEXUS domain kernel must specify bounded production limits and fail-closed overflow behavior before any such decision.

## 4. Backtesting and simulation assessment

NautilusTrader offers a meaningful simulation surface: L1/L2/L3 book types, book walking for depth data, liquidity-consumption controls, queue-position modeling and configurable fill models.

Its own documentation also states that historical data cannot reveal how a simulated order would have interacted with other market participants. Important examples:
- default limit-on-touch eligibility can be 1.0 unless configured otherwise;
- historical book liquidity may be reused across simulated orders unless liquidity consumption is enabled;
- queue tracking estimates visible queue, not hidden orders or all venue-specific priority rules;
- L1 execution necessarily relies on more assumptions than L2/L3;
- a reproducible random seed covers the fill model's random draws, not every source of nondeterminism.

Therefore:
- use NautilusTrader as a serious candidate for deterministic event-driven strategy replay and execution simulation;
- require venue-specific queue, latency, partial-fill, fee, funding, rejection and rate-limit models;
- preserve independent NEXUS simulation fidelity labels and calibration evidence;
- never promote a strategy based on a single optimistic default fill model.

## 5. Version maturity and upstream governance

The inspected upstream README and `MIGRATION_V2.md` describe an active v2 transition: v2 uses the Rust core and PyO3 Python package on `develop`; legacy v1 is maintained on `develop_v1` for critical security backports only for approximately three months after cutover, with no feature or parity work. This is a meaningful integration risk because NEXUS would need to choose between adopting the transitioning v2 API and maintaining a legacy v1 integration with a restricted maintenance horizon.

Before selecting a baseline, NEXUS must compare a released/tagged v2 candidate with the exact `develop` snapshot, inspect migration completeness for the required Rust/Python APIs and adapters, and pin the supported toolchain plus dependency graph. The source-inspection SHA in this memo is not itself a release recommendation.

## 6. Licensing and upstream governance

The upstream repository declares LGPL-3.0. This is a weak-copyleft license, but it is not a blanket permission to copy, modify, statically link, distribute or host arbitrary portions without obligations. The exact obligations depend on how NEXUS uses, modifies, links and distributes the upstream components and on the intended deployment/distribution model.

Before integration:
1. pin an immutable upstream release/commit and capture its exact LICENSE and notices;
2. identify crate-level licensing and bundled/transitive dependencies;
3. decide whether NEXUS uses unmodified libraries, modifications, a separate process, or copied code;
4. review source-offer/relinking/notice obligations with qualified counsel;
5. record the result in a dependency/license register.

No legal conclusion is made here.

## 7. Provisional role allocation for reference platforms

| Platform | Provisional NEXUS role | Disposition |
|---|---|---|
| NautilusTrader | Candidate trading runtime, order lifecycle, adapters, replay/backtest | Deep candidate; source audit and conformance spike required; not accepted as full core |
| Tradoor | Chart rendering, Footprint/Order Flow reference, selected public-data ingestion patterns | Candidate subsystem/reference; separate AGPL-3.0-only review and existing NX-RESEARCH-002 findings apply |
| QuantConnect LEAN | Quant research, portfolio simulation and model decomposition reference | Reference first; evaluate selected components only after simulation requirements are mapped |
| Hummingbot | Exchange connector and crypto execution integration patterns | Reference for adapter patterns; not NEXUS's risk, ledger or autonomous-control plane |
| ATAS / TradingView | Functional, formula and interaction benchmarks | Behavioral/UX reference; do not copy proprietary code or assume data/formula parity |

No row authorizes a dependency addition, code copy, fork, license acceptance or product integration.

## 8. Bounded next gates

| Gate | Deliverable | Exit criterion |
|---|---|---|
| R6-A — Immutable upstream baseline | Compare released v2 tag with inspected `develop` snapshot `97ecbafd6621241a2222ef5a31cf887c6d96d950`; pin release, license, crate graph and toolchain | Reproducible supported source snapshot, migration/API assessment and dependency inventory |
| R6-B — Numeric compatibility | Cross-check upstream Price/Quantity/Money implementation and limits against NX-ARCH-003 / NX-ADR-005 | No precision/overflow gap hidden by defaults; explicit supported domain |
| R6-C — Risk and dispatch boundary | Trace every submit/modify/cancel/cancel-all/close path and every adapter dispatch path | Prove NEXUS approval cannot be bypassed and durable persistence precedes every external side effect |
| R6-D — Recovery conformance | Fault tests for timeout-after-send, restart-before-ack, late fill, duplicate fill, snapshot/stream race, external/manual order and missing position report | All NEXUS critical invariants pass or documented incompatibilities reject candidate |
| R6-E — Adapter qualification | Select one eligible venue only after OD/legal/account gates; inspect its exact adapter and API semantics | Capability matrix and venue-specific contract tests |
| R6-F — Simulation calibration | Compare fills against replay fixtures and independent queue/latency assumptions | No strategy promotion from uncalibrated/default optimistic assumptions |
| R6-G — License and integration decision | Legal review plus architecture cost comparison: embedded crates vs process boundary vs own runtime | Explicit adopt/reuse/reference/reject decision in ADR |

**Stop condition:** If R6-C cannot prove an unbypassable NEXUS risk + durable dispatch boundary without a large invasive fork, do not adopt NautilusTrader as the execution core. Keep it as a benchmark and implement the NEXUS execution boundary independently.

## 9. Current disposition

- NautilusTrader: **LEADING CANDIDATE — NOT SELECTED**.
- Full-stack adoption: **REJECTED FOR NOW** (insufficient fit evidence; not a judgment that upstream is low quality).
- Selected-component reuse: **UNDER EVALUATION**.
- NEXUS Risk Engine, durable outbox, Ledger, recovery barriers and AI isolation: **MUST REMAIN NEXUS-OWNED**.
- Live connectivity, credentials, orders, production deployment and risk-limit changes: **NOT AUTHORIZED**.
- Documentation baseline / G0: **NOT FROZEN / BLOCKED**.

This assessment is deliberately bounded. Reopen it only when new source evidence, a selected venue, a concrete prototype result, a material upstream release or a licensing finding changes the decision.
