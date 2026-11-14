# NEXUS product-first milestones — public market-data prototype

**Plan date:** 2026-11-14  
**Scope owner:** NEXUS engineering / research workstream  
**Status:** targets, not claims of completed live verification

## Interim gate — first real bytes (target before 2026-11-20)

- Run the recorder from an internet-enabled host (user PC or VPS) against the public Bybit linear WebSocket.
- Capture at least 10 consecutive minutes of actual publicTrade.BTCUSDT and orderbook.full.BTCUSDT frames.
- Preserve the original raw journal, exact command/configuration, UTC start/end, host OS/Python version, connection generations and replay summary.
- Verify replay and every per-frame digest. Label the digest as an accidental-corruption check, not tamper-proof evidence.
- Do not commit credentials, private data, machine secrets or unreviewed large raw dumps. Keep the raw evidence as a GitHub Actions artifact or a separately retained evidence bundle; commit only a small, sanitized, representative fixture if licensing, terms and size permit.
- Acceptance: real frames from the actual exchange endpoint, both expected topics observed, no invented/synthetic fixture, replay succeeds. If no connection is possible, record the exact blocker and leave the gate open.

## M1 — working raw recorder and replay (target 2026-11-21)

- Public-only connection to Bybit V5 linear WebSocket; no credentials or private endpoint.
- Capture publicTrade.BTCUSDT and orderbook.full.BTCUSDT raw frames before parsing.
- Every frame has UTC wall time, monotonic receive time, connection generation and SHA-256.
- Application heartbeat every 20 seconds; bounded reconnect backoff.
- Replay verifies every raw checksum and reproduces the same ordered frame stream.
- Acceptance: at least a 60-minute live smoke session, one observed reconnect or controlled disconnect/reconnect, zero corrupt journal lines, all deterministic tests green, and the 10-minute real-data interim gate already passed.
- This gate proves capture plumbing only; it does not prove book correctness or feed completeness.

## M2 — live book reconstruction and first alpha report (target 2026-11-28)

- Fetch REST full-depth snapshot and bridge buffered WebSocket deltas per Bybit's current u / seq procedure.
- Invalidate on update-ID gap, u=1, stale connection, malformed event or bounded-buffer overflow.
- Expose a book as valid only after snapshot bridge; preserve RPI exclusion metadata.
- Compare replayed book to a fixture/fresh snapshot at the same u and seq.
- Verify official archive inventory: trade-level vs candle-only, categories, symbols, date range, timestamps, IDs, and whether any L2 history is actually present.
- Publish HYP-001 result or an explicit archive/data-coverage blocker. Primary config is fixed; secondary grid is exploratory with Holm–Bonferroni correction.
- No strategy is allowed to consume a book outside the valid state.

## M3 — seven-day endurance (target start 2026-11-28; report target 2026-12-05)

- Run continuous capture only after M1/M2 acceptance.
- Pair endurance with fault injection; seven days alone is not a reliability proof.
- Report reconnects, sequence gaps, resets, resync duration, raw archive integrity, duplicate trades, write latency, disk growth and replay divergence.
- Any silent drop, checksum failure or unbounded queue invalidates the run.
- Venue/account/jurisdiction eligibility must be verified against the user's actual circumstances and current official terms before any venue selection or account-connected work. Public-data capture does not imply trading eligibility.

## Scope controls

- Python is a disposable evidence-gathering spike. No Rust port until measured throughput, correctness and maintenance requirements justify it.
- No UI, AI orchestration, multi-venue layer, database server, ClickHouse, private API, order entry or live trading.
- Dates are reviewed explicitly if an external blocker occurs; they are not silently moved.
