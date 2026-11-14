# NEXUS product-first milestones — public market-data prototype

**Plan date:** 2026-11-14  
**Scope owner:** NEXUS engineering / research workstream  
**Status:** targets, not claims of completed live verification

## M1 — working raw recorder and replay (target 2026-11-21)

- Public-only connection to Bybit V5 linear WebSocket; no credentials or private endpoint.
- Capture publicTrade.BTCUSDT and orderbook.full.BTCUSDT raw frames before parsing.
- Every frame has UTC wall time, monotonic receive time, connection generation and SHA-256.
- Application heartbeat every 20 seconds; bounded reconnect backoff.
- Replay verifies every raw checksum and reproduces the same ordered frame stream.
- Acceptance: at least a 60-minute live smoke session, one observed reconnect or controlled disconnect/reconnect, zero corrupt journal lines, all deterministic tests green.
- This gate proves capture plumbing only; it does not prove book correctness or feed completeness.

## M2 — live book reconstruction and first alpha report (target 2026-11-28)

- Fetch REST full-depth snapshot and bridge buffered WebSocket deltas per Bybit's current u / seq procedure.
- Invalidate on update-ID gap, u=1, stale connection, malformed event or bounded-buffer overflow.
- Expose a book as valid only after snapshot bridge; preserve RPI exclusion metadata.
- Compare replayed book to a fixture/fresh snapshot at the same u and seq.
- Publish HYP-001 result or an explicit archive/data-coverage blocker.
- No strategy is allowed to consume a book outside the valid state.

## M3 — seven-day endurance (target start 2026-11-28; report target 2026-12-05)

- Run continuous capture only after M1/M2 acceptance.
- Pair endurance with fault injection; seven days alone is not a reliability proof.
- Report reconnects, sequence gaps, resets, resync duration, raw archive integrity, duplicate trades, write latency, disk growth and replay divergence.
- Any silent drop, checksum failure or unbounded queue invalidates the run.

## Scope controls

- Python is a disposable evidence-gathering spike. No Rust port until measured throughput, correctness and maintenance requirements justify it.
- No UI, AI orchestration, multi-venue layer, database server, ClickHouse, private API, order entry or live trading.
- Dates are reviewed explicitly if an external blocker occurs; they are not silently moved.
