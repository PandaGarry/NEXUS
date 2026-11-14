# NX-ADR-004 — Market Data Recovery State Machine

**Status:** PROPOSED — requires owner review  
**Date:** 2026-11-14  
**Scope:** Public market-data stream integrity and recovery: trades, order books, ticker/reference streams, funding/OI/liquidation streams. Private account/order streams are governed separately by NX-ADR-002 and are not implicitly covered here.  
**Evidence baseline:** Tradoor `tradoor-terminal/tradoor` commit `39a1826816f973ff46c15a848ad1cbe3be7b1dc8`; see NX-RESEARCH-002. This ADR defines NEXUS requirements; it does not claim Tradoor already meets them.

## Context

A WebSocket being connected does not mean its data is complete or safe to consume. Streams can be delayed, duplicated, reordered, dropped, restarted, throttled or silently stale. Order-book deltas are especially dangerous: one missing update can corrupt all subsequent depth and derived Order Flow.

The Tradoor source audit observed venue-dependent sequence coverage. Binance, OKX and Deribit pass sequence metadata into the shared browser BookSync path; several adapters do not. The caller can resubscribe after a detected gap, but a sequence-less incremental stream cannot reliably detect an omitted delta. Binance/Aster snapshot bridging is stronger than generic resubscription. NEXUS must model integrity explicitly rather than expose a single connected/disconnected flag.

## Decision

NEXUS ingestion maintains a per-stream state machine, keyed by at least:

`venue + market_type + instrument_id + channel + connection_generation`

For order books, sequence scope and snapshot lineage are part of the key. State is persisted or reconstructible from durable raw events and a versioned recovery checkpoint.

### States

| State | Meaning | Consumer policy |
|---|---|---|
| DISCONNECTED | No active transport | No new data |
| CONNECTING | Transport/session establishment in progress | No new data |
| SUBSCRIBING | Subscription sent; acknowledgement/data not yet sufficient | No trusted data |
| AWAITING_SNAPSHOT | Snapshot required or requested | Book unavailable |
| SYNCHRONIZING | Snapshot received; buffered deltas being validated/bridged | Book unavailable |
| LIVE_VALID | Sequence/freshness/semantic checks pass | Eligible for downstream use |
| LIVE_DEGRADED | Data is usable only with explicit limitations (e.g. no venue sequence) | Strategy-specific policy; risk-increasing decisions may be blocked |
| STALE | Freshness deadline exceeded | Not eligible for new risk decisions |
| GAP_DETECTED | Sequence gap, checksum mismatch, invalid bridge or impossible update | Invalidate book immediately |
| RECOVERING | Resubscribe/resnapshot/replay underway | No risk-increasing use |
| HALTED | Repeated/structural failure or operator/policy stop | Manual or policy-controlled recovery |

### Required transitions

- DISCONNECTED → CONNECTING → SUBSCRIBING.
- SUBSCRIBING → AWAITING_SNAPSHOT for snapshot-based books; otherwise SYNCHRONIZING/LIVE_DEGRADED only when the venue protocol defines a safe bootstrap.
- A valid snapshot → SYNCHRONIZING; buffered deltas must bridge exactly according to the venue's documented sequence rules.
- Successful bridge and freshness checks → LIVE_VALID.
- A venue without sequence/checksum support may reach LIVE_DEGRADED only if its protocol supplies whole-book replacement or another documented integrity guarantee. Sequence-less incremental deltas must not be labelled LIVE_VALID.
- Any sequence gap, checksum mismatch, invalid update range, impossible book mutation, timestamp regression beyond policy, or malformed payload → GAP_DETECTED; invalidate the book before publishing further derived state.
- GAP_DETECTED → RECOVERING → AWAITING_SNAPSHOT/SUBSCRIBING; never silently continue from the corrupted state.
- Freshness deadline exceeded → STALE; recovery begins according to channel policy.
- Repeated recovery failures, schema drift, rate-limit ban, or inconsistent venue responses → HALTED or extended DEGRADED according to a bounded retry policy; emit an operator alert.
- Socket close, heartbeat timeout, subscription rejection and process restart must all cause explicit state transitions.

## Protocol-specific recovery

Each venue adapter must declare a protocol capability record:

- snapshot source: REST / WebSocket snapshot / full-book replacement / none;
- delta sequence fields and their semantics (first, last, previous, generation);
- checksum algorithm, input ordering and precision, if available;
- snapshot bridge rule;
- whether updates are incremental or full replacement;
- heartbeat and liveness mechanism;
- event-time and receive-time semantics;
- rate limits and retry/backoff constraints;
- maximum buffer size and overflow behavior;
- known blind spots and confidence.

A generic recovery engine executes adapter-provided rules. It must not invent sequence semantics or assume all venues use the same update IDs.

### Snapshot + delta algorithm (normative)

1. Mark current book unusable and increment connection generation.
2. Subscribe to the delta stream and buffer incoming deltas before requesting the snapshot, unless the venue's official protocol requires the reverse order.
3. Fetch/receive the authoritative snapshot and record snapshot sequence, event time, receive time and raw payload reference.
4. Discard buffered deltas that are strictly older than the snapshot according to venue-specific rules.
5. Find the first delta that bridges the snapshot exactly; apply only a contiguous valid chain.
6. Validate checksum if supplied, crossed/negative/duplicate levels, price/quantity constraints, and freshness.
7. Atomically publish a new book version and mark LIVE_VALID only after all checks pass.
8. On any ambiguity, overflow, missing bridge or checksum mismatch, discard the candidate book and restart recovery with bounded backoff.

The order of subscribe and snapshot is adapter-defined because venue protocols differ. The invariant is that no unaccounted update can be silently skipped between the snapshot and the published state.

### Sequence-less feeds

- Full-book replacement: may be LIVE_DEGRADED or LIVE_VALID only if the adapter demonstrates that every message is a complete authoritative book and freshness/order checks are adequate.
- Incremental feed without sequence/checksum: maximum state is LIVE_DEGRADED; expose the limitation to consumers. It is not suitable for strategies requiring queue/depth integrity unless separately validated.
- Never manufacture a sequence number from receive order and present it as exchange continuity.

## Time and quality requirements

Every event stores exchange event time (nullable), local receive time, processing time, and clock-quality metadata separately. Missing exchange time remains missing; receive time is not substituted invisibly. Track clock offset/uncertainty and monotonic local duration for staleness.

Quality is orthogonal to transport state:
- VALID
- DEGRADED
- STALE
- UNSYNCHRONIZED
- INVALID
- UNKNOWN

A connected socket can carry STALE or INVALID data. A disconnected stream can have a last-known state but cannot be represented as live.

## Downstream and risk policy

- Chart rendering may optionally show stale/last-known data with an explicit indicator.
- Order Flow calculations must reset or mark intervals contaminated by gaps; do not bridge cumulative delta through missing trades as if complete.
- Strategies declare required channels and minimum quality/state.
- Risk Engine receives feed health independently and can veto risk-increasing commands when required inputs are stale, invalid, unsynchronized or below the strategy's declared confidence.
- Recovery must not create synthetic trades or synthetic depth.
- After process restart, no book is LIVE_VALID until a valid snapshot/replay reconstruction is completed.
- Private account/order stream health is independently reconciled under NX-ADR-002; public market-data health cannot establish account state.

## Observability

Per stream, record:
- state and transition reason;
- last exchange event time / receive time / processing time;
- age and clock uncertainty;
- reconnect count, recovery duration, failed recovery count;
- sequence gaps, duplicate/out-of-order events, checksum failures;
- buffer depth/overflow;
- dropped/invalid event counts;
- current snapshot ID/sequence and book version;
- venue adapter capability/version and schema version.

State transitions and operator actions are append-only audit events.

## Alternatives considered

1. **Connected/disconnected boolean:** rejected; it cannot express stale, unsynchronized or sequence-less degraded feeds.
2. **Generic reconnect and continue:** rejected; reconnect does not prove a book is synchronized.
3. **One universal sequence rule:** rejected; venue protocols use different sequence scopes and snapshot-bridge semantics.
4. **Always trust full-book frames:** rejected unless the protocol guarantees replacement semantics and freshness/order are validated.

## Consequences and risks

- More explicit adapter work and state complexity.
- Strategies must declare data-quality requirements.
- Some venues/channels may be unavailable to high-integrity strategies until their protocols are proven.
- Sequence-less feeds may remain display-only/degraded.
- Recovery tests require recorded raw fixtures and fault injection.

## Acceptance criteria

1. A sequence gap invalidates the published book before any further downstream use.
2. Snapshot/delta recovery passes venue-specific bridge tests, including updates arriving during snapshot fetch.
3. Checksum mismatch, malformed payload, buffer overflow and reconnect all force a safe recovery path.
4. Sequence-less incremental feeds cannot be marked LIVE_VALID.
5. Full-book feeds are tested for stale, duplicate, reordered and regressing messages.
6. Event time, receive time and processing time remain distinct; missing exchange time remains null.
7. Cumulative Delta/Footprint marks or resets intervals contaminated by missing trades.
8. Process restart requires snapshot/replay reconstruction before LIVE_VALID.
9. Risk Engine blocks risk-increasing commands when a required feed is STALE, INVALID, UNSYNCHRONIZED or below the strategy's minimum quality.
10. Recovery transitions, retry exhaustion and operator overrides are auditable.
11. Tests include deterministic recorded fixtures for Binance, OKX, Deribit and at least one sequence-less venue.
12. No runtime/CI pass is claimed until tests are actually executed and evidence is recorded.

## Open decisions for owner review

- Which venues/channels are required for the first crypto release?
- Should sequence-less full-book feeds be eligible for selected strategies after separate validation, or remain display-only?
- What are the initial freshness thresholds per channel and timeframe?
- What retry exhaustion threshold triggers HALTED versus prolonged DEGRADED?
