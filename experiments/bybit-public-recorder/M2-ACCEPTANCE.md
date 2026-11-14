# Bybit M2 acceptance checklist — live REST snapshot + delta synchronization

**Status:** NOT STARTED / NOT ACCEPTED  
**Plan date:** 2026-11-15  
**Target:** 2026-11-28  
**Scope:** public market data only; Bybit V5 linear BTCUSDT; no credentials, private endpoints, account access or orders.

This checklist is a release gate, not a claim that M2 is implemented. Every checked item must link to a commit, CI run, fixture, raw journal or reproducible report.

## 0. Evidence and accounting

- [ ] Re-open the original 10-minute artifact before its 2026-11-28 expiry; preserve a private local copy.
- [ ] Reconcile exactly 11,177 journal records. Report mutually exclusive counts for `publicTrade` topic frames, `orderbook.full` topic frames, subscription/control acknowledgements, pong/ping frames, malformed/non-JSON frames and any other records. Counts must sum exactly to total records; do not infer the unexplained 30.
- [ ] Keep the original artifact private until Bybit data terms and redistribution rights have been reviewed. Do not commit raw exchange data to the public repository by default.
- [ ] Add synthetic/minimal protocol fixtures to the repository only where licensing and terms permit; fixtures must be clearly labelled synthetic if synthetic.
- [ ] Record the Actions runner region as an environment fact only. Do not use hosted-runner wall/monotonic timing as a production latency benchmark.

## 1. REST snapshot acquisition

- [ ] Use the documented public endpoint `GET /v5/market/full_orderbook?category=linear&symbol=BTCUSDT` (not the top-of-book endpoint).
- [ ] Validate HTTP status, JSON shape, `retCode == 0`, `result.s`, `result.u`, `result.seq`, both sides and decimal levels.
- [ ] Journal the exact REST response body before parsing, with request URL (no secrets), HTTP status, local UTC wall time, monotonic receive time and connection generation.
- [ ] Bound HTTP timeout, response bytes, retries and snapshot request rate. Never silently accept an error body as a snapshot.
- [ ] Preserve explicit metadata that RPI orders are excluded.

## 2. Snapshot / buffered-delta bridge

- [ ] Subscribe to `orderbook.full.BTCUSDT` first and buffer raw deltas before requesting the REST snapshot.
- [ ] Validate every buffered event is a full-depth `type=delta` for the expected symbol.
- [ ] While buffering, require consecutive `u` within a connection generation; on discontinuity, discard the buffer and restart synchronization.
- [ ] If `seq` decreases, discard that delta as specified by Bybit; never sort events to hide wire-order problems.
- [ ] If snapshot `seq` is less than the first usable buffered delta `seq`, fetch a newer snapshot.
- [ ] Discard buffered deltas with `seq` lower than the snapshot `seq`.
- [ ] Require a buffered delta with both `seq` and `u` exactly equal to the snapshot watermark. If same `seq` has a different `u`, retry snapshot; do not guess.
- [ ] Initialize from the REST snapshot, then apply only deltas after the exact matching watermark in original receive order.
- [ ] Bound the delta buffer. Overflow invalidates synchronization and starts a clean resync.
- [ ] Do not expose a book to downstream consumers until the complete bridge succeeds.

## 3. Runtime continuity and fail-closed behavior

- [ ] For live updates, ignore stale `u` values below the local watermark.
- [ ] On `u` gap (`u > local_u + 1`), invalidate and resynchronize.
- [ ] On `u=1`, invalidate immediately and restart the documented snapshot synchronization procedure.
- [ ] On disconnect, reconnect, connection-generation change, malformed JSON/event, wrong symbol/topic, invalid decimal, crossed/locked book or buffer overflow, mark the book invalid.
- [ ] A reconnect must never inherit a `LIVE_VALID` book from the previous connection.
- [ ] No strategy or analytics consumer may read a book while invalid or synchronizing.
- [ ] If snapshot acquisition repeatedly fails or cannot catch up, remain unavailable; never fall back to a stale book.

## 4. Replay and deterministic tests

- [ ] Journal WS frames and REST snapshot responses in one append-only, checksum-verified event journal with explicit record kinds.
- [ ] Replay must reconstruct the same valid/invalid state transitions and final book fingerprint from the recorded ordered events.
- [ ] Test exact watermark match; snapshot older than first delta; same `seq` / different `u`; `seq` decrease; `u` gap; `u=1` reset; duplicate/stale delta; malformed response; nonzero `retCode`; invalid levels; crossed book; buffer overflow; disconnect/reconnect; REST timeout.
- [ ] Include at least one fixture based on a legally retainable, redacted/synthetic protocol example and document its provenance.
- [ ] Assert no book is marked valid before exact snapshot alignment and all post-watermark deltas are applied.

## 5. Live evidence

- [ ] Capture a real public session with REST snapshot + WS deltas and a valid synchronized book.
- [ ] Record snapshot `u/seq`, matching delta `u/seq`, applied delta count, resync count, invalidation reason and final watermark.
- [ ] Demonstrate a controlled disconnect/reconnect or observed reconnect and prove the book becomes invalid then valid only after a new bridge.
- [ ] Demonstrate an injected `u=1` reset and an injected `u` gap; both must force resync.
- [ ] Keep hosted-runner timing out of latency claims. Any latency study requires a controlled, geographically relevant host, synchronized wall clock and monotonic elapsed-time measurements.

## 6. Acceptance decision

M2 is accepted only when all required sections above are complete, unit tests pass on Python 3.11/3.12/3.13, live evidence is archived with a reproducible replay, and the evidence register links the exact commit and CI run. Any uncompleted item remains explicitly open; target dates are not silently moved.

## Official protocol references checked 2026-11-15

- Bybit full-depth WebSocket and synchronization procedure: https://bybit-exchange.github.io/docs/v5/websocket/public/full-ob
- Bybit full-depth REST snapshot: https://bybit-exchange.github.io/docs/v5/market/full-ob
