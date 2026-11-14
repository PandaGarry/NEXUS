# ТЗ-NX-001 — Market Data Infrastructure

**Status:** PROPOSED — requires owner review  
**Date:** 2026-11-14  
**Related decisions:** NX-ADR-001 (Unified Market Event Contract), NX-ADR-004 (Market Data Recovery State Machine), NX-ADR-005 (Instrument Specification & Exact Arithmetic)  
**Phase:** Foundation / Core Architecture  
**Implementation status:** NOT STARTED

## 1. Goal

Specify an autonomous, durable, exchange-neutral market-data subsystem for NEXUS Crypto. It must collect and normalize market data independently of Desktop/Web client sessions, preserve raw exchange evidence, detect incomplete or stale streams, reconstruct valid state after disconnect/restart, and expose quality-aware data to analytics, strategies, simulation and risk.

This document defines requirements and acceptance criteria. It is not an implementation plan approval and does not certify any exchange adapter.

## 2. Scope

### In scope
- Public exchange market-data adapters.
- Spot and perpetual market channels selected for the initial release.
- WebSocket and REST ingestion, snapshots and historical backfill.
- Raw payload capture and canonical event normalization.
- Trades, L1/L2 order books, ticker/mark/index prices, candles, funding, open interest and liquidations where supported.
- Event timestamps, receive/process timestamps, deduplication and sequence integrity.
- Durable event log, replay, checkpointing and recovery.
- Instrument specification integration and metadata versioning.
- Per-channel health, quality, metrics and audit records.
- Read-only operation and deterministic replay.

### Out of scope
- Authenticated private account streams and order execution (separate requirements; NX-ADR-002).
- Strategy decisions, order generation and portfolio/risk policy.
- User-facing chart rendering and UI state.
- Claims of exchange-wide coverage before per-channel certification.
- Live trading activation.

## 3. Product and deployment requirements

1. Ingestion runs as a continuously operating backend service, not inside a browser tab or desktop process.
2. Desktop and Web clients consume the same canonical backend state and cannot be the source of truth for collection.
3. Loss of all clients must not stop configured collection.
4. Multiple service instances must not create uncontrolled duplicate subscriptions or divergent book state; ownership/partitioning and fencing must be explicit.
5. Every service restart enters recovery; no order-book stream is exposed as LIVE_VALID until snapshot/replay validation completes.
6. Exchange adapters are isolated behind typed contracts; a venue-specific parser cannot directly mutate shared canonical state.
7. No secrets are required for public channels. If an exchange requires credentials for a public-data endpoint, that dependency must be explicitly reviewed and scoped.
8. Infrastructure choices (message broker, column store, distributed cache) remain open until throughput, durability and operational requirements justify them.

## 4. Supported event families

Each venue capability is declared per `venue + market_type + instrument + channel`, not as a single boolean per exchange.

| Event family | Minimum payload | Required semantics |
|---|---|---|
| Trade | price, quantity, instrument, aggressor | BUY / SELL / UNKNOWN; preserve source and confidence |
| Order book L1/L2 | bid/ask levels or top-of-book | snapshot/delta/full-replacement semantics; sequence/checksum where available |
| Ticker | last, bid/ask, volume if provided | units, event time and source |
| Mark/index | price and reference kind | never conflate mark, index and last |
| Candle | OHLCV, interval, open/close times | volume unit, final/in-progress status, source |
| Funding | rate, next funding time, interval, settlement currency where supplied | preserve venue-native rate unit and normalization formula |
| Open Interest | value, unit, contract/instrument | preserve native unit and conversion provenance |
| Liquidation | side, price, quantity, time, order/position semantics if supplied | distinguish actual event from inferred estimate |

Unsupported or unavailable fields are null with a reason/status; they are never fabricated as zero.

## 5. Canonical event contract

All normalized events must include, as applicable:

- `event_id`: deterministic or source-backed deduplication identity;
- `event_type` and schema version;
- `venue_id`, `market_type`, `instrument_id`, native instrument ID;
- `exchange_event_time` (nullable), `received_at`, `processed_at`;
- source connection ID and connection generation;
- channel and source sequence metadata (scope, first/last/previous IDs);
- exact price/quantity values and units, or raw decimal strings before exact conversion;
- instrument specification version;
- raw payload reference and payload hash;
- quality state and diagnostic reason;
- adapter version and normalization version.

Trade aggressor is an enum BUY / SELL / UNKNOWN, never a default boolean. Missing event time remains null. Exchange time must not be replaced by local receive time without an explicit separate field.

## 6. Data correctness and arithmetic

1. Raw payloads are persisted before or atomically with canonical acceptance; a failure to preserve required raw evidence is observable and follows a documented fail policy.
2. Decimal values are parsed from original decimal strings into exact representations. Binary floating-point is not the canonical value for price, quantity, funding, OI, fee or money.
3. Price and quantity conversion requires an active Instrument Specification version.
4. Contract quantity, base quantity, quote notional and settlement units are explicit.
5. Missing multiplier or unit conversion is UNKNOWN and blocks dependent calculations.
6. Duplicate source events are idempotently rejected or linked to the existing canonical event.
7. Out-of-order events are handled by channel-specific policy; they are not silently reordered if doing so would change market semantics.
8. Zero is a valid numeric value only when supplied as zero by the source; missing values remain missing.

## 7. Order-book integrity and recovery

Implement NX-ADR-004 state machine per stream. At minimum:

- DISCONNECTED, CONNECTING, SUBSCRIBING, AWAITING_SNAPSHOT, SYNCHRONIZING, LIVE_VALID, LIVE_DEGRADED, STALE, GAP_DETECTED, RECOVERING, HALTED.
- Adapter declares snapshot source, sequence fields and scope, checksum rules, bridge rules, update semantics, heartbeat, freshness threshold, buffer limits and retry limits.
- Snapshot + delta streams are buffered and bridged according to the venue protocol.
- A gap/checksum mismatch/invalid bridge immediately invalidates the book.
- Sequence-less incremental feeds cannot be LIVE_VALID.
- Full-book replacement feeds require explicit protocol evidence plus freshness/order validation.
- Restart requires snapshot or deterministic replay reconstruction before LIVE_VALID.
- Cumulative Delta/Footprint intervals affected by missing trades are marked incomplete or reset.

## 8. Market-data capability registry

For every channel, persist:

- venue, market type, instrument family, channel;
- supported event fields and native units;
- event-time source and precision;
- sequence/checksum semantics;
- snapshot/delta/full-book semantics;
- authentication requirements;
- rate limits and subscription limits;
- reconnect and resnapshot behavior;
- historical availability and retention;
- tested source revision, documentation URL and verification date;
- status: CONFIRMED, OBSERVED, UNKNOWN, NOT_SUPPORTED, NOT_TESTED;
- known limitations and confidence.

A capability may be CONFIRMED only with authoritative protocol documentation plus source/fixture evidence; runtime-dependent guarantees require recorded integration test evidence. README claims alone are insufficient.

## 9. Persistence, replay and retention

- Raw exchange payloads and canonical events are logically distinct.
- Every canonical event points to its raw source or an explicit reason raw retention is unavailable.
- Event log supports deterministic replay by venue, instrument, channel and time range.
- Checkpoints include schema/adapter/spec versions and last accepted sequence.
- Replay must reproduce identical canonical events and book state from the same raw input and software versions.
- Retention and archival policies are configurable per event family and jurisdiction/security requirements.
- Database technology and broker selection are intentionally not prescribed in this specification; architecture ADR must justify the choice against measured workload and failure model.

## 10. Health, observability and operations

Per stream expose:
- current recovery state and quality;
- last event/receive/process time and data age;
- event throughput and dropped/invalid/duplicate counts;
- sequence gaps and checksum failures;
- reconnects, recovery duration and retry exhaustion;
- queue/buffer depth and overflow;
- raw-payload persistence lag/failures;
- adapter/schema/spec version;
- historical backfill lag and missing ranges.

Alert on stale critical streams, repeated gaps, schema drift, rate-limit bans, persistence failures, clock anomalies and unexpected capability changes.

## 11. Security and isolation

- Public ingestion processes have no trading permission and no withdrawal permission.
- Adapter processes cannot access private account credentials unless separately approved for a distinct private-data service.
- Network egress is restricted to configured venue endpoints and required infrastructure.
- Raw payload retention must not accidentally capture secrets or private account data.
- Operator overrides and manual recovery actions are authenticated and audited.
- Risk Engine consumes health state through a read-only contract; market-data processes cannot approve orders or alter risk limits.

## 12. Failure handling

- WebSocket disconnect: mark state, reconnect with bounded exponential backoff and jitter, resubscribe and recover.
- REST snapshot timeout/429/5xx: preserve invalid state, respect rate limits, retry boundedly, alert on exhaustion.
- Schema change: quarantine unknown payload, preserve raw evidence, mark channel degraded/unknown; do not parse by guess.
- Sequence gap/checksum failure: invalidate and rebuild.
- Storage unavailable: follow explicit durability policy; do not silently drop critical data while reporting healthy.
- Clock drift: record uncertainty and downgrade time-sensitive consumers.
- Instrument spec stale/missing: continue safe display where possible, but block exact quantity/notional-dependent calculations and risk decisions.
- Process restart: recover offsets/checkpoints, rebuild books, then publish health.

## 13. Test strategy

### Unit / golden fixtures
- Every supported adapter has versioned raw payload fixtures for each channel and market type.
- Decimal parsing, unit conversion, event time, aggressor classification and missing/null semantics have golden tests.
- Sequence bridge, duplicates, reordering, checksum and full-book replacement have deterministic fixtures.
- Funding and OI unit normalization are independently tested.
- Instrument spec changes invalidate dependent caches.

### Integration / fault injection
- Disconnect during active book updates.
- Snapshot request racing with delta arrival.
- Missing/duplicate/reordered deltas.
- Checksum mismatch.
- Rate-limit responses and retry-after.
- Partial subscription failure.
- Process crash between raw persistence and canonical commit.
- Database unavailable, queue overflow and recovery after restart.
- Clock drift and timestamp regression.
- Schema evolution / unknown fields.

### Replay and determinism
- Replaying a fixed raw capture yields byte-stable canonical event output where serialization is deterministic and semantically identical state otherwise.
- Same replay inputs and version set produce identical book snapshots and derived events.
- Gaps and unknown fields remain visible in replay; no silent repair.

## 14. Acceptance criteria

1. Collection continues with Desktop and Web clients closed.
2. A configured venue/channel has a machine-readable capability declaration.
3. Every canonical event preserves venue, market type, instrument, event/receive/process time separation, source and schema versions.
4. Trade aggressor supports UNKNOWN and carries provenance/confidence.
5. Missing timestamps/quantities/units are not replaced by zero.
6. Exact numeric parsing is used for canonical price and quantity.
7. Duplicate events do not create duplicate canonical trades/fills/volume.
8. A book gap/checksum mismatch makes the book unusable before downstream publication.
9. Sequence-less incremental books cannot claim LIVE_VALID.
10. Restart/replay reconstructs book state before LIVE_VALID.
11. Raw payload and canonical event persistence failures are observable and follow fail-closed policy for critical channels.
12. Stale/invalid feed health reaches Risk Engine and blocks dependent risk-increasing actions.
13. Recorded fixtures cover every initial-release venue/channel.
14. Backfill/replay and live ingestion use the same normalization contracts.
15. No adapter is declared production-ready without protocol docs, golden fixtures, integration/fault tests and runtime evidence.
16. Runtime/CI/benchmark claims cite actual run IDs, commit SHA, environment and artifacts.

## 15. Open decisions for owner review

- Initial venue shortlist and exact Spot/Perpetual channel scope.
- Initial retention targets for raw trades, book deltas, funding/OI and liquidations.
- Initial freshness thresholds per channel.
- Whether sequence-less full-book feeds are permitted for selected strategies after separate validation.
- Storage and streaming infrastructure selection after workload sizing.
- Whether initial release includes only linear USDT/USDC perpetuals plus spot, deferring inverse/quanto products.


## WP-D — State evidence and recovery barrier

Market Data MUST publish per-stream state, quality, freshness, connection generation, event/receive/processing times, sequence/snapshot watermarks, completeness and recovery-case references in the form composed by [NX-IF-004](../architecture/NX-IF-004-state-evidence-freshness-recovery-barrier-contract.md). Public book/trade recovery continues to follow NX-ADR-004; WP-D consumes those protocol-specific states and MUST NOT replace venue-specific sequence or snapshot semantics with a generic rule. A recovered socket is not sufficient to mark a stream valid or to reopen risk-increasing authorization. No freshness threshold is assumed until an owner-approved versioned policy is configured.
