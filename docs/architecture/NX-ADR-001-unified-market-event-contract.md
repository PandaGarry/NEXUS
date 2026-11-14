# NX-ADR-001 — Unified Market Event Contract

**Status:** PROPOSED — requires owner review  
**Version:** 0.1  
**Date:** 2026-11-14  
**Scope:** Canonical event envelope and semantic rules for public market data consumed by storage, replay, analytics, strategies, simulation and risk. Private account/order events are related but governed by separate contracts under NX-ADR-002 and the financial-ledger specification.  
**Evidence baseline:** NX-RESEARCH-002 (Tradoor source audit and venue metadata review), NX-ADR-004 (stream integrity/recovery), NX-ADR-005 (instrument identity/exact arithmetic), and ТЗ-NX-001. Venue-specific field semantics must still be confirmed against official API documentation and fixtures before an adapter is marked CONFIRMED.

## 1. Context and problem

A common JSON shape is not enough to make market data exchange-neutral. Venues differ in instrument identifiers, units, event-time precision, sequence scopes, snapshot/delta semantics, trade aggressor conventions, contract quantities, funding intervals and correction behavior. If adapters flatten these differences prematurely, downstream components may silently compare incompatible values or treat incomplete data as complete.

The Tradoor audit found concrete examples of inconsistent timestamp population and event coverage between server and browser parsers, venue-specific quantity conversion, and incomplete shared instrument metadata. A canonical contract must preserve source facts and provenance while exposing normalized semantics with explicit quality and uncertainty.

This ADR defines the event contract and semantic invariants. It does not claim existing Tradoor or NEXUS code conforms.

## 2. Decision

NEXUS will use a **versioned, typed canonical market-event envelope** with:
- immutable event identity and source provenance;
- explicit venue, market type, instrument identity and channel;
- separate exchange event time, local receive time and processing time;
- exact numeric representation and explicit units/currency;
- sequence/checksum metadata without inventing continuity;
- stream quality and recovery lineage;
- schema, adapter and instrument-spec versions;
- raw-payload linkage;
- typed payloads whose semantics are not inferred from field names alone.

Canonical events are append-only. Corrections, busts or retractions are represented as new events referencing the event being corrected; stored history is never silently overwritten.

## 3. Event envelope

Every canonical market event MUST carry the following logical envelope. Wire encoding and field names may be mapped to a selected serialization format, but semantic meaning is normative.

| Field | Type / rule | Meaning |
|---|---|---|
| `event_id` | globally unique immutable ID | NEXUS identity for this accepted canonical event |
| `event_type` | closed/versioned enum | trade, book_snapshot, book_delta, ticker, mark_price, index_price, candle, funding, open_interest, liquidation, venue_status or a future registered type |
| `schema_version` | semantic schema version | Version of the canonical payload contract |
| `venue_id` | stable registry ID | Exchange/venue, not a display label |
| `market_type` | enum | spot, linear_perpetual, inverse_perpetual, quanto, option or another explicitly registered type |
| `native_instrument_id` | exact venue identifier | Venue-native instrument identity as received |
| `instrument_id` | stable NEXUS ID | Internal identity mapped by Instrument Specification Registry |
| `instrument_spec_version` | immutable version or UNKNOWN | Exact instrument rules used to interpret units/contract quantities; required where interpretation depends on it |
| `channel` | registered channel ID | trades, order_book, ticker, mark_price, index_price, candles, funding, open_interest, liquidations, etc. |
| `source_event_id` | nullable string | Venue-native event/trade/update identifier, preserved without coercion |
| `source_sequence` | nullable structured value | Native sequence/update ID plus declared scope and semantics; never a fabricated receive-order counter |
| `exchange_event_time` | nullable timestamp with source precision | Time assigned by venue; missing stays missing |
| `receive_time` | mandatory UTC timestamp | Local wall-clock time at ingress, accompanied by clock-quality metadata |
| `process_time` | mandatory UTC timestamp | Time canonical acceptance/processing completed |
| `monotonic_receive_ns` | optional monotonic duration/counter | Local elapsed-time measurement for latency/freshness; not a cross-host timestamp |
| `clock_quality` | enum/object | local synchronization source, estimated offset/uncertainty and status |
| `quality` | enum | VALID, DEGRADED, STALE, UNSYNCHRONIZED, INVALID or UNKNOWN |
| `stream_state` | NX-ADR-004 state | DISCONNECTED through LIVE_VALID/HALTED as applicable at acceptance |
| `connection_generation` | integer/version | Distinguishes reconnect/recovery generations |
| `book_version` | nullable immutable version | Identifies a validated derived book state for book events |
| `raw_payload_ref` | immutable reference/hash | Link to preserved raw payload and capture metadata |
| `adapter_id` / `adapter_version` | stable ID/version | Adapter implementation that produced the canonical event |
| `ingest_region` | optional deployment metadata | Ingress location for latency/debugging, not market identity |
| `deduplication_key` | deterministic scoped key | Idempotency identity based on venue/channel/native event semantics |
| `correction_of` | nullable event ID/reference | Links correction, bust or retraction to the original event |
| `attributes` | typed, schema-governed extension | Only registered extension fields; no untyped semantic dumping ground |

Fields marked nullable remain explicitly null/UNKNOWN where the venue does not provide them. They must not be filled with receive time, zero, a guessed sequence or a guessed instrument rule.

### 3.1 Identity and deduplication

- `event_id` is generated by NEXUS and remains stable across storage, replay and downstream delivery.
- `source_event_id` is not assumed globally unique. Its scope (venue, market, channel, instrument, session or sequence generation) is declared by the adapter.
- `deduplication_key` is derived from documented venue semantics. If no stable native identity exists, the adapter declares the weaker deduplication strategy and its limitations; it must not claim perfect deduplication.
- Identical payloads are not automatically duplicates: two legitimate trades can have equal price, size and timestamp.
- Duplicate delivery must not produce duplicate canonical effects. Raw capture may retain repeated frames for forensic purposes, while canonical acceptance links or rejects duplicates idempotently.

### 3.2 Time semantics

All timestamps are UTC instants with preserved source precision and explicit origin. The original raw timestamp representation is retained in raw capture metadata.

- Exchange event time is source-provided and may be absent.
- Receive time is captured at the ingress boundary.
- Process time is when validation/normalization completes.
- These values are never substituted for one another.
- Clock offset and uncertainty are tracked; wall-clock time is not used as a substitute for monotonic elapsed-time measurement.
- Out-of-order event time is not automatically a data error: policy is channel- and venue-specific.
- Freshness thresholds are configured per channel/venue and are evaluated using receive age plus source/clock quality, not a single universal threshold.

## 4. Typed payload contracts

Each event type has a separately versioned payload. The following semantic requirements are mandatory; final wire schemas are specified in implementation contracts.

### 4.1 Trade

Required:
- native trade ID when supplied;
- exact price;
- exact native quantity;
- explicit quantity unit (base, quote, contracts, lots or venue-specific unit);
- aggressor/taker side as BUY, SELL, UNKNOWN or NOT_PROVIDED;
- maker/taker interpretation and source field mapping;
- trade condition/type where available.

Rules:
- Unknown aggressor side remains UNKNOWN; it is not inferred from price movement.
- Contract quantity is not assumed to equal base quantity.
- Aggregated trade messages must declare whether they represent one trade or a batch and preserve constituent identity/range where available.
- Corrections/busts are separate referenced events.
- Delta/CVD calculations must disclose treatment of UNKNOWN side and missing trade coverage.

### 4.2 Order book snapshot and delta

Required:
- side, exact price and exact quantity;
- quantity unit and price currency;
- snapshot/delta semantics;
- native sequence/update identifiers and scope where provided;
- snapshot lineage/book version;
- checksum metadata where available.

Rules:
- A zero quantity in a delta means deletion only when the venue protocol defines it that way.
- A snapshot is a full replacement only when official protocol semantics confirm it.
- Deltas cannot be applied without the corresponding validated snapshot lineage and bridge rules.
- Sequence-less incremental updates cannot be marked LIVE_VALID.
- A canonical book state is not inferred from a stream of events unless the recovery engine confirms continuity under NX-ADR-004.
- Price levels are keyed using exact tick/spec semantics, not binary floating-point keys.

### 4.3 Ticker, mark and index prices

Each price type is a distinct event type or explicitly typed subtype; last traded price, mark price, index price, oracle price and best bid/ask must not be conflated.

Fields include exact price, quote currency, source reference, optional bid/ask, source time and venue-specific calculation metadata where available. A mark/index value is not treated as an executable price.

### 4.4 Candles

Fields include interval, open/close boundary convention, open/high/low/close, volume and volume unit, trade count if supplied, final/partial flag, source and aggregation method.

Rules:
- Native exchange candles and NEXUS-aggregated candles are distinguishable.
- Interval boundaries and timezone are explicit (UTC alignment or venue-defined alignment).
- Partial candles may be updated; each update is a new versioned event or update event, never an invisible mutation.
- Volume unit and contract conversion semantics are explicit.
- Missing intervals are represented as gaps, not fabricated zero-volume candles unless a separate derived-series policy explicitly creates synthetic bars marked as such.

### 4.5 Funding

Fields include exact funding rate, rate unit/period convention, funding timestamp or interval, settlement asset/currency where known, mark/reference price if supplied, and source endpoint/channel.

A rate such as 0.01% must not be normalized to 0.01 without an explicit scale. Predicted/indicative funding and settled/historical funding are distinct event types or status values. Funding cadence and settlement semantics are venue- and instrument-specific.

### 4.6 Open interest

Fields include exact value, native unit (contracts/base/quote/currency), conversion reference and timestamp if a normalized notional is derived, source timestamp, and sampling method (stream/polling).

Raw venue OI and derived USD/base notional are separate values. Do not compare or aggregate across venues until unit and contract semantics are resolved.

### 4.7 Liquidations

Fields include exact price and quantity, quantity unit, side/direction, venue-native event ID/time where supplied, instrument and market type, and whether the record is an individual event, aggregated report or inferred estimate.

Reported liquidation feeds are not assumed complete or equivalent across venues. The capability registry records coverage and limitations.

### 4.8 Venue status and reference metadata

Operational status, trading halt, maintenance, mark/index reference and other non-trade events use explicit typed payloads. Instrument rule changes themselves are owned by NX-ADR-005's versioned registry and referenced by events where relevant; they are not silently embedded as mutable defaults.

## 5. Numeric representation and units

- Preserve original numeric strings/raw values.
- Canonical price, quantity, rate, volume, OI, funding and monetary values use exact decimal/fixed-point or integer tick/lot representation with explicit scale.
- No binary floating-point is permitted as the canonical event value for price, quantity, volume, funding, OI or money.
- Every quantity has a declared unit and, where applicable, contract/spec version.
- Every monetary value has currency.
- Percentages, ratios and rates carry an explicit scale and period convention.
- Derived values retain formula/version, input event references, conversion reference and calculation time.
- Missing is null/UNKNOWN; it is not zero.
- Display formatting is downstream and cannot mutate canonical values.

NX-ADR-005 governs instrument-level precision, contract multipliers and trading-rule semantics. This ADR governs event representation and unit disclosure.

## 6. Ordering, sequence and replay

- Source sequence is preserved as a typed value with venue-defined scope; adapters must document wrap/reset/generation behavior.
- NEXUS receive order is recorded separately from venue sequence and event time.
- No global total order across independent venues/channels is implied.
- Replay ordering uses a deterministic composite policy: source sequence within its documented scope when valid; otherwise preserved capture/receive ordering with explicit weaker guarantees. Event-time sorting alone is not a safe replay order.
- Replay records adapter, schema, instrument-spec and normalizer versions.
- Given identical raw inputs and pinned versions, normalization and deterministic downstream book reconstruction must be reproducible.
- Late events and corrections are appended and handled by downstream correction/recomputation policy; prior events are not rewritten.

## 7. Quality and capability semantics

Quality is orthogonal to transport state as defined in NX-ADR-004.

- VALID: required semantics and integrity checks passed for the declared capability.
- DEGRADED: usable only with explicitly recorded limitations.
- STALE: freshness threshold exceeded.
- UNSYNCHRONIZED: ordering/sequence/book continuity is not established.
- INVALID: malformed, contradictory or failed integrity checks.
- UNKNOWN: evidence is insufficient to assign a stronger status.

A channel capability registry must record, per venue/market/instrument family/channel:
- fields and units available;
- source and event-time semantics;
- native IDs and sequence/checksum behavior;
- snapshot/delta/full-replacement semantics;
- precision and contract-unit conversion;
- polling/stream cadence and rate limits;
- historical/backfill availability;
- correction/bust semantics;
- tested adapter and schema versions;
- authoritative documentation URL and verification date;
- status CONFIRMED / OBSERVED / UNKNOWN / NOT_SUPPORTED / NOT_TESTED;
- limitations and confidence.

README statements or a field merely existing in source code are not sufficient to mark runtime capability CONFIRMED. Runtime claims require integration evidence.

## 8. Raw capture, provenance and retention

- Raw venue payload and canonical event are separate logical records.
- Canonical event points to raw payload reference/hash, endpoint/channel, capture time, adapter version and decode status.
- Raw payload is preserved before or atomically with canonical acceptance according to the persistence contract in ТЗ-NX-001.
- If raw persistence fails, the system records an explicit ingestion failure and applies a documented fail policy; it must not silently publish an event as fully auditable.
- Sensitive private account payloads are outside this public market-data contract and follow security/data-retention controls in NX-ADR-002/NX-SEC-001.
- Retention, archive tier and compression are configurable per event family; no single retention duration is prescribed here.

## 9. Downstream compatibility and change management

- Schema versions are explicit and semantic. A field rename that preserves meaning may be a compatible schema evolution; a unit, timestamp, nullability or ordering semantic change is breaking.
- Unknown extension fields are preserved in raw payload. Canonical consumers ignore unregistered fields rather than guessing their meaning.
- Breaking changes require a new schema version, migration/replay plan and consumer compatibility review.
- Adapters pin a schema version and publish conformance fixtures.
- Golden fixtures cover normal, boundary, missing-field, duplicate, out-of-order, malformed, correction and precision cases.
- Each event family has independent conformance tests and a documented owner.
- Strategy and Risk consumers declare required event types, fields, quality levels and freshness thresholds.

## 10. Alternatives considered

1. **Pass venue-native JSON directly to every consumer:** rejected; creates duplicated parsing, inconsistent semantics and hidden venue coupling.
2. **Normalize to a minimal symbol/price/quantity tuple:** rejected; loses units, timestamps, sequence, contract and provenance semantics.
3. **Use one generic event with arbitrary untyped payload:** rejected as the only contract; it prevents reliable schema validation and consumer guarantees. Raw payload remains available separately.
4. **Use receive time as exchange event time when missing:** rejected; falsifies latency and event chronology.
5. **Synthesize sequence numbers for sequence-less feeds:** rejected; fabricates continuity.
6. **Use floating-point numeric fields in canonical events:** rejected; violates exact arithmetic requirements.
7. **Overwrite corrected historical events:** rejected; destroys auditability and deterministic replay.

## 11. Consequences and risks

- More metadata and schema discipline are required at adapters and storage boundaries.
- Some venue feeds will remain DEGRADED/UNKNOWN until official semantics and integration evidence exist.
- Consumers must explicitly handle null/UNKNOWN fields and quality.
- Raw payload retention increases storage cost but preserves audit/replay capability.
- Schema governance and golden fixtures become release-critical.
- Event normalization cannot compensate for missing venue data; limitations must remain visible.
- A canonical contract does not itself guarantee correct adapter implementation, feed continuity or market completeness.

## 12. Related decisions and specifications

- NX-ADR-004 — Market Data Recovery State Machine: stream continuity, recovery and quality states.
- NX-ADR-005 — Instrument Specification & Exact Arithmetic: instrument identity, trading rules, units and exact numeric operations.
- NX-ADR-002 — Execution Integrity & Reconciliation: private order/account event lifecycle and reconciliation.
- NX-ARCH-001 — Target Architecture & Deployment Topology: component ownership and event flow.
- ТЗ-NX-001 — Market Data Infrastructure: ingestion, persistence, replay, observability and acceptance requirements.
- NX-RESEARCH-002 — Tradoor Market Data & Exchange Adapter Audit: scoped source evidence and UNKNOWNs.

## 13. Acceptance criteria

1. Every canonical event carries the required envelope fields or explicit null/UNKNOWN values.
2. Event type and payload schema are versioned and validated.
3. Venue, market type, native instrument ID and stable internal instrument ID are unambiguous.
4. Exchange event time, receive time and process time are distinct and never silently substituted.
5. Numeric values preserve exact source representation, scale, currency and unit.
6. Trade aggressor side and contract quantity semantics remain UNKNOWN when not authoritatively available.
7. Book snapshots/deltas preserve sequence scope, lineage and protocol semantics; no synthetic continuity is introduced.
8. Funding, OI, liquidation and candle units/periods/aggregation semantics are explicit.
9. Deduplication is idempotent within documented source identity scope and does not collapse legitimate equal-valued events.
10. Corrections/busts are append-only and reference prior events.
11. Raw payload provenance is traceable from canonical event.
12. Replay uses pinned adapter/schema/spec versions and is deterministic within declared ordering guarantees.
13. Capability status differentiates source observation from runtime-confirmed behavior.
14. Consumers can gate on quality, freshness and required field availability.
15. Golden fixtures cover normal, boundary, missing, duplicate, out-of-order, malformed and correction cases.
16. Schema evolution and breaking-change policy are documented and enforced.

## 14. Open implementation decisions

- Wire serialization (e.g. Protobuf, Avro, JSON/JSONB or another format) and schema registry.
- Canonical ID generation strategy and distributed uniqueness guarantees.
- Event broker/transport and delivery semantics.
- Raw payload storage format, partitioning, retention and archive policy.
- Exact decimal encoding (scaled integers versus decimal strings/decimal128) by event family.
- Event-time precision/clock synchronization implementation.
- Per-venue capability matrix and initial supported channels.
- Whether candle updates are represented as revisions, append-only updates or finalized-plus-provisional streams.

These are intentionally deferred to implementation specifications and measured workload evaluation. They do not permit weakening the semantic invariants above.

## 15. Verification status

This ADR is a proposed design contract. No NEXUS canonical event library, schema registry, broker, ingestion adapter or conformance suite is implemented or verified by this document. No runtime, load or replay test is claimed. Venue-specific semantics remain UNKNOWN until documented and tested per channel.

**Status remains PROPOSED.** Owner review and alignment with ТЗ-NX-001, NX-ADR-004, NX-ADR-005 and NX-ARCH-001 are required before implementation.
