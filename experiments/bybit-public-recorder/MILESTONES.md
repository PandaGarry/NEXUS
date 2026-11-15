# NEXUS product-first milestones — public market-data prototype

**Plan date:** 2026-11-15  
**Scope owner:** NEXUS engineering / research workstream  
**Status:** `IN_PROGRESS` — first raw-capture gate passed; M1/M2/M3 acceptance remains open. Further automated live captures are gated pending Bybit API terms review. See [M2-ACCEPTANCE.md](M2-ACCEPTANCE.md).

## Interim gate — first real bytes

**PASS — 2026-11-14; record accounting independently reconciled 2026-11-15**

- Hosted GitHub Actions run #10 connected to the public Bybit linear WebSocket and captured approximately 10 minutes.
- 11,177 raw journal records total, exactly reconciled from the raw artifact: 8,149 `publicTrade.BTCUSDT`, 2,998 `orderbook.full.BTCUSDT`, 29 pong replies (`op=ping`, `ret_msg=pong`), and 1 subscription acknowledgement. Sum = 11,177; no unclassified records remain.
- One connection generation; both expected topics present; replay and the workflow acceptance check passed.
- Independent reinspection on 2026-11-15 verified all 11,177 JSONL lines, zero malformed records, zero missing SHA-256 values, zero digest mismatches, and exact category reconciliation. The artifact ZIP was downloaded into the current working session for inspection; it has not been committed to the public repository.
- [Raw artifact](https://github.com/PandaGarry/NEXUS/actions/runs/43637091666/artifacts/14131465205), expires 2026-11-28. Preserve a user-controlled private copy before expiry. Do not publish raw exchange frames in the repository until data terms and redistribution rights have been reviewed.
- The first order-book messages were deltas. This is expected for the full-depth stream contract and reinforces that REST snapshot + buffered delta bridge is required before a book can be considered synchronized.
- This gate proves public-feed reachability and raw capture/replay plumbing only. It does not prove snapshot synchronization, reconnect recovery, feed completeness, long-run reliability or trading eligibility.
- Hosted runner region is not a latency benchmark; do not derive production latency claims from this capture.

## M1 — working raw recorder and replay (target 2026-11-21)

- Public-only connection to Bybit V5 linear WebSocket; no credentials or private endpoint.
- Capture publicTrade.BTCUSDT and orderbook.full.BTCUSDT raw frames before parsing.
- Every frame has UTC wall time, monotonic receive time, connection generation and SHA-256.
- Application heartbeat every 20 seconds; bounded reconnect backoff.
- Replay verifies every raw checksum and reproduces the same ordered frame stream.
- Acceptance: at least a 60-minute live smoke session, one observed reconnect or controlled disconnect/reconnect, zero corrupt journal lines, all deterministic tests green, and the 10-minute real-data interim gate already passed.
- This gate proves capture plumbing only; it does not prove book correctness or feed completeness.

## M2 — live book reconstruction (target 2026-11-28)

**Implementation status (2026-11-15):** REST snapshot client, response validator, bounded synchronizer, live CLI integration, REST journal records, book-state markers and deterministic book replay are implemented in PR #19. Parser-hardening CI [43646661506](https://github.com/PandaGarry/NEXUS/actions/runs/43646661506) passed all 37 tests on Python 3.11/3.12/3.13, including the malformed-delta regression cases. The recorder workflow now also triggers on M2 checklist/milestone changes, so documentation acceptance changes are re-tested against the current branch code. This is not exchange-live evidence. M2 remains NOT ACCEPTED.

- Follow the detailed [M2 acceptance checklist](M2-ACCEPTANCE.md); do not mark M2 accepted by passing only pure state-machine fixtures.
- Fetch documented REST full-depth snapshot from `/v5/market/full_orderbook`, journal exact response before parsing, buffer WS deltas, and bridge only at exact matching `seq` + `u`.
- Invalidate and resynchronize on update-ID gap, `u=1`, stale connection, malformed event, wrong symbol, crossed book or bounded-buffer overflow.
- Expose a book as valid only after snapshot bridge; preserve RPI exclusion metadata; never let consumers read invalid/synchronizing state.
- Demonstrate replay equivalence, a real synchronized session, disconnect/reconnect, and injected `u=1` and gap recovery.
- Obtain an independent protocol review of `u`/`seq` handling. `u` is consecutive; `seq` is monotonic but not consecutive. Exact snapshot/delta matching of both fields is required at the bridge watermark.
- Reconcile a REST snapshot against WS state by buffering continuously, advancing/replaying through its exact matching `seq/u` watermark, then applying subsequent deltas to both books and comparing again at a later common watermark. The REST response can be newer than the local book at response time; never compare different watermarks or hide unexplained differences behind timing tolerance.
- Verify official archive inventory: trade-level vs candle-only, categories, symbols, date range, timestamps, IDs, and whether any L2 history is actually present.
- Publish HYP-001 result or an explicit archive/data-coverage blocker. Primary config is fixed; secondary grid is exploratory with Holm–Bonferroni correction. The registered venue/instrument candidate set is in [RESEARCH-UNIVERSE.md](RESEARCH-UNIVERSE.md).

## M3 — seven-day endurance (target start 2026-11-28; report target 2026-12-05)

- Run continuous capture only after M1/M2 acceptance.
- Pair endurance with fault injection; seven days alone is not a reliability proof.
- Report reconnects, sequence gaps, resets, resync duration, raw archive integrity, duplicate trades, write latency, disk growth and replay divergence.
- Any silent drop, checksum failure or unbounded queue invalidates the run.
- Venue/account/jurisdiction eligibility must be verified against actual owner circumstances and current official terms before any venue selection or account-connected work. Public-data capture does not imply trading eligibility.

## Scope controls

- Python is a disposable evidence-gathering spike. No Rust port until measured throughput, correctness and maintenance requirements justify it.
- No UI, AI orchestration, multi-venue layer, database server, ClickHouse, private API, order entry or live trading.
- Kraken Spot and OKX protocol/data-terms research may continue, but no second recorder implementation until Bybit M2 is accepted. OKX currently has the stronger documented historical L2 dataset; Kraken remains a useful Spot checksum contrast.
- Bybit API terms gate: no further automated live capture unless public market-data-only use, API-key applicability, retention and non-redistribution conditions are reviewed and the repository variable `NEXUS_BYBIT_PUBLIC_DATA_TERMS_APPROVED=true` is deliberately set.
- OKX historical data is documented as personal-use-only; its API Agreement restricts redistribution, competing data/analytics products and commercialized AI model training. No OKX raw data may be committed or redistributed without written permission.
- Dates are reviewed explicitly if an external blocker occurs; they are not silently moved.

## Evidence references checked 2026-11-15

- Bybit WS synchronization contract: https://bybit-exchange.github.io/docs/v5/websocket/public/full-ob
- Bybit REST full-depth snapshot: https://bybit-exchange.github.io/docs/v5/market/full-ob
- Successful live capture run #10: https://github.com/PandaGarry/NEXUS/actions/runs/43637091666
- Current recorder PR: https://github.com/PandaGarry/NEXUS/pull/19
