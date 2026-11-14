# NEXUS Bybit public-data recorder spike (Python)

**Status:** experimental public-data prototype; not production and not venue approval.

This short-lived implementation branch starts directly from main, independent of the stacked architecture PR chain. It has no credentials, private endpoints, account access, order entry, or trading functionality.

## Included

- Raw WebSocket frame journal: stores exact frames before parsing, with connection generation, UTC wall clock, monotonic receive clock, and SHA-256.
- Optional live public recorder for publicTrade.{symbol} and orderbook.full.{symbol}, with a 20-second application heartbeat and bounded reconnect backoff.
- Checksum-verified raw replay and topic/connection-generation summary.
- Exact-decimal trade parser and deduplication by trade ID i; repeated seq values remain valid.
- Full-depth snapshot/delta bridge and u continuity/reset guard.
- Deterministic fixtures for snapshot alignment, stale/duplicate deltas, sequence gaps, u=1, deletion, replay equivalence and RPI metadata preservation.

## Run locally

```bash
python -m pip install -e ".[live]"
python -m unittest discover -s tests -v
nexus-bybit-record --symbol BTCUSDT --output data/bybit-public-raw.jsonl --duration 600
nexus-bybit-replay data/bybit-public-raw.jsonl
```

## Real-feed smoke evidence

A push to the prototype branch starts a GitHub Actions public-only smoke job. It attempts a 10-minute capture from the hosted runner, requires both publicTrade.BTCUSDT and orderbook.full.BTCUSDT topics, verifies the journal, and uploads the raw capture plus replay summary as a 14-day workflow artifact. A failed or blocked run is evidence of a blocker, not a passing capture. No credentials or account access are used.

## Milestones

See [MILESTONES.md](experiments/bybit-public-recorder/MILESTONES.md): first real-feed gate before 2026-11-20, 60-minute recorder/replay target 2026-11-21, live snapshot bridge and first alpha report target 2026-11-28, seven-day endurance report target 2026-12-05.

## Alpha research lane

The first falsifiable experiment is pre-registered in [NX-EXP-001](experiments/bybit-public-recorder/NX-EXP-001-alpha-trade-flow-imbalance.md): short-horizon taker-flow imbalance, one frozen primary configuration, an exploratory parameter grid with multiple-testing correction, chronological walk-forward validation, execution costs and a two-week stop rule. First report target: 2026-11-28; if valid data is unavailable, report the blocker rather than extending silently.

## Evidence boundary

- The live command records raw public WebSocket frames only. It does not yet call REST snapshots or expose a reconstructed live book as valid.
- The snapshot/delta state machine is unit-tested separately. A replay equality assertion is valid only when the expected snapshot and replayed book share the same u and seq; a moving live book cannot be compared byte-for-byte with a later REST snapshot.
- received_monotonic_ns is only comparable within one host boot. NTP/chrony synchronization is an operational prerequisite for wall-clock correlation; elapsed latency must use monotonic clocks.
- Every frame is tagged with a connection generation. Raw frames are journaled before any JSON parsing.
- RPI orders are absent from the full-depth orderbook; downstream analytics must retain this limitation.
- SHA-256 stored beside each frame detects accidental corruption relative to that digest but is not tamper-proof.
- Live transport dependency is pinned to websockets==17.4 (BSD-3-Clause, Python >=3.11), isolated in the optional extra. No pybit SDK or private/account client is included.

## Official contracts (checked 2026-11-14)

- Full-depth WebSocket: https://bybit-exchange.github.io/docs/v5/websocket/public/full-ob
- Full-depth REST snapshot: https://bybit-exchange.github.io/docs/v5/market/full-ob
- Public trades: https://bybit-exchange.github.io/docs/v5/websocket/public/trade
- Restricted jurisdictions: https://www.bybit.com/en/help-center/article/Service-Restricted-Countries/trade/spot
