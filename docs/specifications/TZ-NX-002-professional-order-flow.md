# ТЗ-NX-002 — Professional Order Flow & Market Microstructure Analytics

**Status:** PROPOSED — requires owner review  
**Version:** 0.1  
**Date:** 2026-11-14  
**Phase:** Professional Analytics / Core Architecture  
**Implementation status:** NOT STARTED  
**Related decisions:** NX-ADR-001, NX-ADR-004, NX-ADR-005, NX-ARCH-001  
**Research baseline:** NX-RESEARCH-002 and official ATAS documentation listed in §15. ATAS is a behavioral/functional benchmark, not a source-code or pixel-copy target.

## 1. Goal

Specify a professional, data-quality-aware Order Flow subsystem. It must turn canonical trades and order-book events into reproducible Footprint, Delta/CVD, DOM, Tape, Volume Profile and TPO views, with explicit semantics, provenance, missing-data handling and measurable performance requirements.

Every displayed number must be explainable: source events, classification rules, instrument units, aggregation interval, session calendar, price grouping and formula version.

## 2. Scope

### In scope
- Trade aggressor-side classification and confidence/coverage.
- Footprint/cluster aggregation by price level and bar/session.
- Bid, Ask, Volume, Trades, Delta and derived ratios.
- Bid/Ask and stacked imbalance.
- Cumulative Delta / CVD and session Delta.
- DOM ladder, depth aggregation, validated snapshots and incremental updates.
- Historical liquidity visualization where depth history supports it.
- Time & Sales / Tape, filters and optional trade aggregation.
- Volume Profile, Delta Profile, Bid/Ask Profile and TPO.
- POC, Value Area, VAH/VAL, TPO POC, Single Prints and Initial Balance.
- Cluster search and metric-threshold alerts.
- Replay, quality overlays, golden datasets and independent formula verification.
- Shared analytics contracts for Web and Desktop.

### Out of scope
- Exchange order placement, order management or execution permissions.
- Strategy signal generation or profitability claims.
- Predictive claims that passive absorption, spoofing, intent or institutional activity are directly observable facts.
- Full proprietary feature parity with ATAS or copying its implementation/assets.
- Private account/order analytics except where separately specified.

## 3. Core principles

1. Source truth before visualization; never repair missing trades/depth by inventing data.
2. Aggressor side is not price direction. Prefer documented venue fields; inferred classification is a separately labelled mode.
3. Contract quantity, base quantity, quote volume and notional are distinct units.
4. Every metric carries data quality and coverage.
5. Same canonical inputs, spec, configuration, session calendar and formula version produce identical results.
6. Semantic formula changes require a new formula/config version.
7. DOM depth is displayed liquidity, not guaranteed executable liquidity.
8. Web and Desktop consume the same versioned calculation contracts.
9. Order Flow is read-only and cannot submit/cancel orders.
10. ATAS is a functional benchmark, not an oracle for numerical correctness.

## 4. Inputs and calculation context

Inputs:
- Canonical Trade, Book Snapshot/Delta, Ticker/Mark/Index, Candle and Instrument Spec from NX-ADR-001.
- Stream state, quality and recovery lineage from NX-ADR-004.
- Exact tick, lot, contract and unit semantics from NX-ADR-005.
- Session calendar, timezone and profile-period configuration.
- Historical raw/canonical event references and replay version manifest.

Every calculation pins venue, market type, instrument, spec version, input channels, event-time range, session/bar boundaries, aggregation and classification versions, price grouping, volume unit, quality and coverage. Unknown mandatory metadata makes the result unavailable or explicitly DEGRADED; it must not trigger a guessed multiplier, side or timezone.

## 5. Normative metric semantics

### 5.1 Trade-side classification

- Prefer venue-provided aggressor/taker side only where official documentation defines its meaning.
- Preserve native field and raw value; normalize to BUY, SELL or UNKNOWN.
- A quote-test/tick-rule classifier may exist as a separate fallback mode with explicit provenance and coverage.
- Never silently mix authoritative and inferred classifications.
- Report classified volume and UNKNOWN-side volume/count per bar/session.
- UpTick/DownTick describes price movement relative to prior prints; it is not aggressor side.

### 5.2 Bid, Ask, Volume and Delta

For trades classified by aggressor side at a price level:
- Ask Volume = sum of exact quantities for aggressive BUY trades.
- Bid Volume = sum of exact quantities for aggressive SELL trades.
- Classified Volume = Ask Volume + Bid Volume.
- Total Observed Volume also includes UNKNOWN-side trades, reported separately.
- Delta = Ask Volume − Bid Volume.
- Delta/Volume is defined only for a nonzero denominator with matching unit and scope.

A bar with material UNKNOWN-side volume cannot present Delta as complete without coverage disclosure.

### 5.3 Footprint / cluster aggregation

A cluster is a price bucket within a defined bar or time interval. Aggregation identity includes instrument, spec version, bar/session, price bucket and classification version.

Supported content:
- Volume; Trades; Volume + Trades; Volume + Delta; Delta; Centered Delta; Bid × Ask; split Bid/Ask; None.

Supported display modes:
- Full Row; Bid/Ask Profile; Volume Profile; Trades Profile; Delta Profile; Bid/Ask Ladder; Positive/Negative Delta Profile.

Price grouping:
- Exact tick-aligned integer ticks are the default.
- Multi-tick grouping is an explicit integer multiple of tick size or a separately defined range-bucketing rule.
- Adaptive grouping may be used for visualization only if the mapping is visible, stable and versioned.
- Changing grouping invalidates cached results.
- Time, range and event-based bars require deterministic boundaries and event ordering. Missing intervals remain gaps.

### 5.4 Bid/Ask imbalance

A standard diagonal comparison mode:
- buy-side: Ask at price P compared with Bid at the immediately lower price bucket;
- sell-side: Bid at P compared with Ask at the immediately higher price bucket.

For ratio threshold R, highlight only if numerator ≥ denominator × R, denominator policy permits the comparison, and minimum volume and absolute-difference filters pass.

Configuration includes ratio, minimum level volume, minimum difference, zero-denominator policy, diagonal or same-level comparison, tick grouping, stacked-level count and minimum data quality.

A zero denominator must not silently produce infinity or an automatic imbalance. Zero handling is explicit and tested.

### 5.5 Cumulative Delta / CVD

CVD is the cumulative sum of accepted classified trade Delta in deterministic event order from an explicit anchor.

Modes:
- continuous accumulation;
- session reset using a versioned session calendar;
- custom-session reset;
- per-bar Delta and cumulative series.

Anchor, timezone and reset boundaries are explicit. Late trades/corrections trigger deterministic recomputation or append-only correction handling. Unknown-side volume and data gaps remain visible. No continuity is claimed across missing trade coverage.

### 5.6 DOM and depth ladder

DOM includes best bid/ask, spread, configurable depth, exact price/size, optional tick grouping, cumulative bid/ask depth, derived depth ratios, feed state, quality, update age and sequence/checksum health.

Rules:
- Only a book reconstructed under NX-ADR-004 may be LIVE_VALID.
- Sequence-less incremental books remain DEGRADED and cannot feed features requiring reliable continuity.
- Snapshot replacement and delta semantics are adapter-specific.
- Quantities retain venue units and instrument-spec version.
- Displayed liquidity is not a guarantee that orders remain available or that visible depth equals total liquidity.
- Depth coverage, snapshot cadence and dropped-update limitations are disclosed.

### 5.7 Liquidity Map / historical depth

Historical resting liquidity may be rendered only where historical order-book events are sufficiently complete. Every level carries quantity/unit, sampling interval, book quality and coverage. Smoothing/interpolation is labelled visualization-only. Trade prints cannot be used as a substitute for resting order-book history.

### 5.8 Time & Sales / Tape

Tape includes event time, receive time, price, exact quantity/unit, optional normalized notional, aggressor side/classification source and time-aligned best bid/ask context when available.

Filters may include volume/notional range, side, price, time, venue, instrument and trade condition. Aggregated prints are optional and retain constituent event references, aggregation window, key and count. A row must distinguish one native trade from a synthetic group.

### 5.9 Volume Profile and Delta Profile

For a selected period and price bucket:
- Volume Profile = sum of observed trade volume.
- Bid/Ask Profile = separate classified aggressive sell/buy volume.
- Delta Profile = Ask − Bid.
- Trades Profile = trade count.

Supported periods: session, day, week, month, custom fixed range and visible/anchored range. Boundaries/timezone and tick grouping are explicit.

POC may use Volume, Trades, Delta, Positive Delta, Negative Delta, Bid or Ask. Tie-breaking is deterministic and documented. Value Area algorithm, target percentage, expansion order and equal-level handling are versioned. VAH/VAL are distinct outputs. No undocumented universal Value Area algorithm is assumed.

### 5.10 TPO / Market Profile

TPO counts configured time sub-periods in which a price bucket was visited under an explicit rule. It is not volume.

Requirements:
- versioned session calendar, timezone and sub-period length;
- explicit trade-based or bar-range-based level-visit rule;
- separate TPO POC and TPO Value Area;
- configurable letters/blocks rendering;
- defined Single Prints and unfinished-period handling;
- Initial Balance start/duration;
- deterministic split/merge recalculation.

TPO counts must never be labelled or combined as volume.

### 5.11 Cluster Search and alerts

Search conditions may target Volume, Trades, Bid, Ask, Delta, Delta/Volume, POC, imbalance, stacked imbalance, price location within bar, session/time and relative thresholds. Alerts are metric-threshold notifications only; they are not trading signals and cannot initiate execution.

## 6. Data quality and coverage

Every bar, cluster, profile and metric carries VALID, DEGRADED, STALE, UNSYNCHRONIZED, INVALID or UNKNOWN quality plus measurable coverage where possible:
- classified vs unknown-side trade volume;
- missing time intervals;
- book gaps/checksum failures;
- snapshot/update age;
- source capability status;
- late/corrected event count;
- raw persistence lag/failure.

Trade gaps contaminate Delta/CVD and trade-derived profiles. Book gaps invalidate depth state until recovery. Last-known chart values may be shown with stale markers; strategies must receive quality metadata. Missing inputs are unavailable/UNKNOWN, not fabricated zero. Cross-venue aggregation requires compatible units, contract conversions, time semantics and quality.

## 7. Configuration and UX requirements

Configuration is versioned and serializable, with global defaults and per-chart overrides.

Controls include:
- content/mode, colors and heatmap scaling;
- tick grouping and aggregation;
- imbalance ratio, volume/difference filters, zero policy and stacked rules;
- CVD anchor/session reset;
- profile period/session/timezone;
- POC metric and Value Area algorithm/percentage;
- TPO sub-period, Single Prints and Initial Balance;
- Tape filters and aggregation;
- DOM depth count/grouping/display mode;
- quality overlays and stale/degraded visibility;
- alerts and saved templates.

Users can synchronize crosshair/time/price across charts, Footprint, DOM, Tape and profiles. Tooltips expose metric definitions, source/derived status and formula/config version. The UI must avoid enabling every visual element by default. Web/Desktop share configuration with version/conflict rules.

## 8. Performance and scalability

Numeric targets must be set from an approved benchmark workload; no performance claim is made here. Benchmark dimensions:
- simultaneous instruments/charts and concurrent clients;
- trades/sec, depth updates/sec and depth levels;
- historical range and replay speed;
- footprint bars/clusters per viewport;
- Tape rate and filter complexity;
- memory per chart/instrument;
- cold start, reconnect, backfill and correction recomputation.

Requirements:
- incremental live aggregation;
- bounded memory and configurable retention;
- backpressure and visible lag/drop metrics;
- no unbounded per-trade UI allocations;
- viewport virtualization/level-of-detail;
- server-side canonical calculations with client rendering acceleration;
- cache keys include spec, formula, session, grouping and quality versions;
- overload degrades presentation explicitly, never silently corrupts calculations.

Latency, CPU, memory and chart-count thresholds remain TBD until reference hardware and workload are approved.

## 9. Security and isolation

- Read-only access to canonical market events; no credentials or signing permissions.
- Alerts cannot call execution APIs.
- No secrets in logs, metrics, payloads or client state.
- Historical data access is authorized.
- AI summaries are labelled hypotheses, not canonical facts.
- User-supplied formulas/scripts, if ever introduced, require a separate sandbox specification.

## 10. Failure and recovery

- Stream transitions follow NX-ADR-004.
- Trade gap: mark affected bars/profiles incomplete; recompute only from corrected/replayed data.
- Book gap: invalidate DOM/liquidity map and recover by venue protocol.
- Schema drift: quarantine invalid payloads, preserve raw evidence and alert.
- Storage lag: expose lag and apply configured backpressure/fail policy.
- Restart: rebuild from checkpoint plus canonical replay, validating version manifests.
- Replay mismatch: stop deterministic certification and preserve a reproducible failure bundle.
- Web/Desktop mismatch: compare server result, formula version and input context; do not silently patch one client.

## 11. Verification strategy

Golden datasets must independently verify:
- side mapping and UNKNOWN handling;
- Bid/Ask/Volume/Delta arithmetic and exact units;
- tick grouping and bar boundaries;
- diagonal/same-level imbalance, zero denominators and stacked levels;
- CVD anchors, sessions, daylight-saving boundaries and late trades;
- book snapshots/deltas, gaps, duplicates, checksum failures and recovery;
- DOM aggregation/cumulative depth;
- Volume Profile POC/Value Area ties and boundaries;
- TPO sub-period inclusion, POC/VA, Single Prints and Initial Balance;
- Tape aggregation and constituent traceability;
- corrections, stale/partial inputs and replay determinism.

Test layers: unit, property-based, adapter fixture, ingestion-to-analytics integration, fault injection, deterministic replay, Web/Desktop parity, load/soak and visual regression. Expected values are independently calculated and reviewed. ATAS screenshots alone are insufficient evidence.

## 12. Acceptance criteria

1. Footprint supports Volume, Trades, Bid×Ask, Delta and combined modes with exact units.
2. UNKNOWN aggressor-side volume is preserved and reported.
3. Delta is Ask minus Bid under a documented classifier.
4. Imbalance has explicit comparison mapping, thresholds, minimum volume/difference and zero policy.
5. Stacked imbalance is deterministic/configurable.
6. CVD supports continuous/session/custom modes and correction handling.
7. DOM is LIVE_VALID only after NX-ADR-004 recovery criteria pass.
8. DOM/Liquidity Map disclose depth coverage, quality and age; smoothing is visualization-only.
9. Tape distinguishes native/aggregated prints and UpTick/DownTick from aggressor side.
10. Volume Profile supports periods, grouping, POC metric, Value Area algorithm/percentage and VAH/VAL.
11. TPO is distinct from volume and supports sub-period, TPO POC/VA, Single Prints and Initial Balance.
12. Search/alerts have no execution side effects.
13. Outputs expose formula/config/spec versions and provenance.
14. Missing/stale/invalid inputs are not silently converted to zero or valid output.
15. Pinned replay produces identical results.
16. Golden fixtures cover arithmetic, boundaries, missing, duplicate, late, correction and recovery cases.
17. Web/Desktop show matching canonical values for identical calculation contexts.
18. Approved performance targets pass before release.
19. Security review confirms no path from analytics to signer or execution credentials.
20. Metric definitions, limitations, user settings and venue coverage are documented.

## 13. Release blockers

Release is blocked if authoritative metrics use binary floating-point, UNKNOWN side is hidden, book continuity is assumed without recovery, session/profile boundaries are ambiguous, synthetic events are unmarked, results lack provenance/versioning, clients disagree, required tests fail, overload silently corrupts data, or analytics can access signing/execution credentials.

## 14. Proposed implementation sequence

1. Lock event and instrument-spec contracts (NX-ADR-001/005).
2. Implement exact-arithmetic primitives and golden fixtures.
3. Implement trade classification with per-venue capability declarations.
4. Implement Footprint/Delta and CVD.
5. Implement Volume Profile and TPO.
6. Implement Tape filters/aggregation.
7. Implement validated DOM/depth analytics.
8. Add historical liquidity only for venues with adequate depth capture.
9. Add Cluster Search, alerts, synchronized layouts and templates.
10. Run independent formula review, replay, fault injection, parity and performance gates.

## 15. Open decisions

- Initial venues/instruments and spot/perpetual market types.
- Session calendar policy for 24/7 crypto and user-defined sessions.
- Acceptable classifier per venue where aggressor side is absent.
- Default Value Area algorithm and tie-breaking.
- Whether historical full-depth capture is required for first release.
- Reference hardware, simultaneous chart count, history horizon and latency targets.
- Cross-venue consolidated Tape/Profile in first release or deferred.
- Global defaults versus per-chart overrides.

## 16. Benchmark references

Official ATAS documentation consulted on 2026-11-14:
- Footprint settings/modes and imbalance filters: https://help.atas.net/en/support/solutions/articles/72000606631
- Footprint display modes: https://help.atas.net/en/support/solutions/articles/72000602349
- Cluster Statistics: https://help.atas.net/en/support/solutions/articles/72000602624
- CVD: https://help.atas.net/en/support/solutions/articles/72000602360
- Volume Profile & TPO, POC, Value Area, Single Prints and Initial Balance: https://help.atas.net/en/support/solutions/articles/72000602305
- DOM Trader and Liquidity Map: https://help.atas.net/en/support/solutions/articles/72000602463
- Smart Tape: https://help.atas.net/en/support/solutions/articles/72000602608
- DOM depth settings: https://help.atas.net/en/support/solutions/articles/72000602625

These sources establish documented functional concepts, not source-code access, numerical equivalence or runtime certification.

## 17. Verification status

Requirements specification only. No NEXUS Order Flow module, formula library, chart, DOM, Tape, profile engine, alert engine or benchmark suite is implemented or verified. No parity, runtime, performance or profitability claim is made.

**Status remains PROPOSED; implementation NOT STARTED.** Owner review, venue selection, formula decisions, golden datasets and architecture readiness gates are required before implementation.
