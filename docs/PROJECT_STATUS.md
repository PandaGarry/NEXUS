# NEXUS — project status and evidence register

**Last reviewed:** 2026-11-15  
**Status vocabulary:** Proposed / In Progress / Verified / Blocked / Deferred

This file is an evidence snapshot, not a claim that every linked proposal has been accepted.

## Repository / integration status

| Item | Status | Evidence / limitation |
|---|---|---|
| Public repository and review access | Verified | Repository is public; default branch is `main` |
| Main branch project overview | In Progress | This review-hub PR proposes the public entry point; it is not on main until merged |
| Legacy architecture/documentation chain | In Progress | PRs #1–#17 remain Draft/open as of this review; inspect each PR's current base/head before relying on it |
| Independent recorder spike | In Progress | PR #19, based directly on main; Draft/open |
| Recorder unit CI | Verified | Run #9 passed Python 3.11/3.12/3.13; a later run also reports 17 tests passing in its unit-test jobs |
| Live public exchange capture | Unknown / pending evidence | Hosted-runner smoke job was started; do not mark complete without final successful run, both expected topics and uploaded replay-verified artifact |
| Live order-book reconstruction | Deferred / not implemented in live CLI | Snapshot/delta bridge exists as a tested pure state-machine prototype; live REST + WS integration remains future work |
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
- A hosted live-feed smoke workflow was added. Its final outcome must be checked at [GitHub Actions](https://github.com/PandaGarry/NEXUS/actions) before claiming real-feed evidence.

### Research

- HYP-001: short-horizon BTCUSDT taker-notional imbalance. It has one frozen primary configuration (5-second window, 0.20 absolute threshold, 3-second horizon); remaining parameter combinations are exploratory and require multiple-testing correction.
- The hypothesis can be rejected. No positive alpha is claimed.
- Official Bybit historical trade archives are a candidate data source, but schema/completeness and any L2 availability require direct inspection.

## Immediate priorities

1. Close the hosted real-feed smoke evidence gate or record its exact blocker.
2. Make the public project overview and current status visible on `main) through a reviewed documentation PR.
3. Build a venue qualification matrix with explicit UNKNOWN values and dated official sources.
4. Implement and measure a second materially different public-data adapter before defining a generic adapter interface.
5. Only after comparing two adapters, define the minimal shared market-data contracts and conformance fixtures.
6. Keep live venue/account selection blocked until exact product and eligibility are verified.
7. Preserve the personal-first boundary and document commercial activation triggers.

## Evidence discipline

A check mark requires an artifact, test result, source, review or explicit owner decision. A document draft is not an accepted architecture decision. A passing unit test is not a live protocol test. A public feed connection is not proof of account eligibility.
