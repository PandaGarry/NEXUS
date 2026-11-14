# NEXUS product-first milestones — public market-data prototype

**Plan date:** 2026-11-14  
**Scope owner:** NEXUS engineering / research workstream  
**Status:** first real-feed gate passed; M1/M2/M3 remain open

## Interim gate — first real bytes

**PASS — 2026-11-14**

- Hosted GitHub Actions run #10 connected to the public Bybit linear WebSocket and captured approximately 10 minutes.
- 11,177 raw journal records: 8,149 publicTrade.BTCUSDT messages and 2,998 orderbook.full.BTCUSDT messages, plus protocol/control frames.
- One connection generation; both expected topics present; replay and the workflow acceptance check passed.
- The downloaded artifact was independently inspected: 11,177 valid JSONL lines, no malformed records, no missing SHA-256 fields and no digest mismatches.
- Raw artifact (retention until 2026-11-28): https://github.com/PandaGarry/NEXUS/actions/runs/43637091666/artifacts/14131465205
- The first order-book messages were deltas. This is expected for the full-depth stream contract and reinforces that REST snapshot + buffered delta bridge is required before a book can be considered synchronized.
- This gate proves public-feed reachability and raw capture/replay plumbing only. It does not prove snapshot synchronization, reconnect recovery, feed completeness, long-run reliability or trading eligibility.

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
