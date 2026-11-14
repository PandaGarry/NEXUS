# NEXUS — project status and evidence register

**Last reviewed:** 2026-11-15  
**Status vocabulary:** Proposed / In Progress / Verified / Blocked / Deferred

This file is an evidence snapshot, not a claim that every linked proposal has been accepted.

## Repository / integration status

| Item | Status | Evidence / limitation |
|---|---|---|
| Public repository and review access | Verified | Repository is public; default branch is `main` |
| Main branch project overview | In Progress | PR #20 proposes the public entry point; it is not on main until reviewed and merged |
| Legacy architecture/documentation chain | In Progress | PRs #1–#17 remain Draft/open as of this review; inspect each PR's current base/head before relying on it |
| Independent recorder spike | In Progress | PR #19, based directly on main; Draft/open |
| Recorder unit CI | Verified | Run #9 passed Python 3.11/3.12/3.13; current run #10 also passed 17 unit tests on all three versions |
| Live public exchange capture | **Verified — first 10-minute smoke only** | Hosted runner captured both required topics, replayed 11,177 frames and uploaded the raw journal artifact; this is not M1 or production certification |
| Live order-book reconstruction | Deferred / not implemented in live CLI | Captured full-depth WS messages are deltas; a REST snapshot bridge is still required before a valid synchronized book can be exposed |
| Historical L2 coverage | Unknown | No historical L2 archive has been verified |
| Alpha profitability | Unknown / not claimed | HYP-001 is a preregistered falsification experiment, not evidence of alpha |
| Production exchange selection | Blocked | No exact owner/account/product eligibility decision and no venue selection |
| Live order execution | Not implemented / not authorized | No private API, credentials, order dispatch or live trading in the recorder spike |

## Current engineering evidence

### PR #19 — public-data recorder spike

- Starts from `main`, independently of the old stacked PR chain.
- Raw public WebSocket frames are journaled before parsing, with wall-clock time, host monotonic receive time, connection generation and a per-frame SHA-256 digest.
- SHA-256 stored beside the frame detects accidental corruption relative to the stored digest; it is not tamper-proof evidence.
- Public trade parsing uses exact decimal values and trade ID deduplication.
- A pure snapshot/delta bridge state machine has deterministic tests; it is not yet integrated into the live capture CLI.
- Local test suite previously reported 14 passing tests. CI subsequently reported 17 tests passing on Python 3.11/3.12/3.13.
- **Live smoke run #10 succeeded:** 11,177 raw records over approximately 10 minutes; 8,149 `publicTrade.BTCUSDT` messages and 2,998 `orderbook.full.BTCUSDT` messages; one connection generation; both topics passed the workflow's acceptance check.
- The downloaded artifact was independently inspected: 11,177 valid JSONL records, 0 malformed lines, 0 missing per-frame SHA-256 values, 0 digest mismatches. The raw archive contains the original exchange messages and journal metadata.
- The first observed full-depth order-book messages are `type=delta`; this confirms why a REST snapshot and buffered-delta bridge are required. The capture alone does not establish a synchronized book.
- [Successful live capture run and artifact](https://github.com/PandaGarry/NEXUS/actions/runs/43637091666). Artifact retention expires 2026-11-28; preserve it before expiry if it is needed as long-term evidence.

### Research

- HYP-001: short-horizon BTCUSDT taker-notional imbalance. It has one frozen primary configuration (5-second window, 0.20 absolute threshold, 3-second horizon); remaining parameter combinations are exploratory and require multiple-testing correction.
- The hypothesis can be rejected. No positive alpha is claimed.
- Official Bybit historical trade archives are a candidate data source, but schema/completeness and any L2 availability require direct inspection.

## Immediate priorities

1. Preserve and document the first real-feed artifact; add a small sanitized representative fixture only after reviewing terms, size and data policy.
2. Complete live REST snapshot + buffered-delta integration and fail-closed resynchronization.
3. Build a second materially different public-data adapter (Coinbase Advanced Trade or Kraken Spot are current candidates) before defining a generic adapter interface.
4. Only after comparing two adapters, define the minimal shared market-data contracts and conformance fixtures.
5. Keep live venue/account selection blocked until exact product and eligibility are verified.
6. Preserve the personal-first boundary and document commercial activation triggers.

## Evidence discipline

A check mark requires an artifact, test result, source, review or explicit owner decision. A document draft is not an accepted architecture decision. A passing unit test is not a live protocol test. A public feed connection is not proof of account eligibility.
