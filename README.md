# NEXUS Bybit public-data recorder spike (Python)

**Status:** experimental public-data prototype; not production and not venue approval.

This short-lived implementation branch starts directly from main, independent of the stacked architecture PR chain. It has no credentials, private endpoints, account access, order entry, or trading functionality.

## Included

- Raw append-only JSONL journal for exact public WebSocket frames and REST snapshot responses, with connection generation, UTC wall time, monotonic receive time and SHA-256.
- Public Bybit V5 linear recorder for `publicTrade.{symbol}` and `orderbook.full.{symbol}`, with a 20-second application heartbeat and bounded reconnect backoff.
- Public full-depth REST snapshot client using `/v5/market/full_orderbook`, with response-size/timeout bounds and validation before use.
- Bounded snapshot/delta synchronizer: exact `seq` + `u` bridge, `u=1` reset, update-ID gap, malformed event, buffer overflow and disconnect invalidation.
- Replay checksum verification, exact record classification and optional order-book reconstruction from journaled REST/WS events.
- Exact-decimal trade parser and deduplication by trade ID `i`; repeated `seq` values remain valid.
- Pre-registered HYP-001 falsification experiment and a separate [research universe](experiments/bybit-public-recorder/RESEARCH-UNIVERSE.md) that keeps the confirmatory primary test fixed.

## Run locally

```bash
python -m pip install -e ".[live]"
python -m unittest discover -s tests -v
nexus-bybit-record --symbol BTCUSDT --output data/bybit-public-raw.jsonl --duration 600
nexus-bybit-replay data/bybit-public-raw.jsonl --replay-book
```

## Live smoke and evidence

A push to the prototype branch runs unit tests and a public-only 10-minute smoke. The smoke requires both public topics, exact journal classification, a journaled REST snapshot, at least one `LIVE_VALID` book event, and replay agreement with recorded valid-book watermarks. A failed or blocked run is evidence of a blocker, not a passing capture. No credentials or account access are used.

GitHub-hosted runner timing is not a production latency benchmark. The original 10-minute artifact is retained only until 2026-11-28; preserve it privately before expiry and do not publish raw exchange frames until applicable terms and redistribution rights have been reviewed.

## Milestones

See [MILESTONES.md](experiments/bybit-public-recorder/MILESTONES.md) and the detailed [M2 acceptance checklist](experiments/bybit-public-recorder/M2-ACCEPTANCE.md). M2 remains NOT ACCEPTED until replay, fault injection, reconnect and live evidence gates all pass.

## Alpha research lane

The falsifiable experiment is pre-registered in [NX-EXP-001](experiments/bybit-public-recorder/NX-EXP-001-alpha-trade-flow-imbalance.md). Its primary configuration is frozen; other venue/instrument combinations are separately labelled exploratory. No positive alpha is claimed.

## Evidence boundary

- A `LIVE_VALID` state is only asserted after the REST snapshot and buffered deltas match exactly on `u` and `seq`.
- The full-depth book excludes RPI orders and has finite initial snapshot depth; unknown depth outside the snapshot must not be represented as complete.
- The replay command verifies raw digests and can reconstruct the order-book state from journaled REST snapshots and WS deltas. This remains a prototype pending live-run evidence.
- `received_monotonic_ns` is only comparable within one host boot. NTP/chrony synchronization is an operational prerequisite for wall-clock correlation.
- SHA-256 stored beside a frame detects accidental corruption relative to that digest but is not tamper-proof.
- Live transport dependency is pinned to `websockets==17.4` in the optional extra. No pybit SDK or private/account client is included.

## Official contracts (checked 2026-11-15)

- Full-depth WebSocket: https://bybit-exchange.github.io/docs/v5/websocket/public/full-ob
- Full-depth REST snapshot: https://bybit-exchange.github.io/docs/v5/market/full-ob
- Public trades: https://bybit-exchange.github.io/docs/v5/websocket/public/trade
- Restricted jurisdictions: https://www.bybit.com/en/help-center/article/Service-Restricted-Countries/trade/spot
