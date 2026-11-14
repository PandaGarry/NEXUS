# NEXUS — project status and evidence register

**Last reviewed:** 2026-11-15  
**Status vocabulary:** Proposed / In Progress / Verified / Blocked / Deferred

This is a dated evidence snapshot. Every status is scoped to the cited commit, CI run or source. A passing test or public connection is not production certification.

## Repository / integration status

| Item | Status | Evidence / limitation (checked 2026-11-15) |
|---|---|---|
| Public repository and review access | Verified | [Repository](https://github.com/PandaGarry/NEXUS); default branch `main` |
| Main branch project overview | In Progress | [PR #20](https://github.com/PandaGarry/NEXUS/pull/20), head `8e0b5391c1340bdc49492fd651e8e005d3aa8e54`; documentation proposal is not on `main` |
| Legacy architecture/documentation chain | In Progress | [Open PR list](https://github.com/PandaGarry/NEXUS/pulls); each PR must be checked for current base/head before relying on it |
| Independent recorder spike | In Progress | [PR #19](https://github.com/PandaGarry/NEXUS/pull/19), head `1051aec3b9776227c091fe9bc7c41ab7ee82d510`, based directly on `main`, Draft/open |
| Recorder unit CI | Verified for code revision | [Run 43641738962](https://github.com/PandaGarry/NEXUS/actions/runs/43641738962) passed Python 3.11/3.12/3.13 on code revision `223e299fd87c1f19ca990129eb7da6d3149f90b6`; later PR #19 commits in this review changed documentation only |
| Live public exchange capture | Verified — first 10-minute smoke only | [Run #10](https://github.com/PandaGarry/NEXUS/actions/runs/43637091666); artifact [14131465205](https://github.com/PandaGarry/NEXUS/actions/runs/43637091666/artifacts/14131465205), expires 2026-11-28. It is not M1 or production certification |
| Published frame accounting | Open discrepancy | 8,149 trade-topic + 2,998 orderbook-topic = 11,147, versus 11,177 total records. The remaining 30 are not yet classified in the published evidence. See [M2 checklist](https://github.com/PandaGarry/NEXUS/blob/prototype/bybit-public-data-recorder-python-v0/experiments/bybit-public-recorder/M2-ACCEPTANCE.md) |
| Live order-book reconstruction | Not implemented in live CLI | [PR #19 source](https://github.com/PandaGarry/NEXUS/pull/19); pure bridge state machine has tests, but live REST snapshot + buffered-delta integration remains M2 |
| M2 acceptance | Not started / not accepted | [M2 acceptance checklist](https://github.com/PandaGarry/NEXUS/blob/prototype/bybit-public-data-recorder-python-v0/experiments/bybit-public-recorder/M2-ACCEPTANCE.md); target 2026-11-28 |
| Historical L2 coverage | Unknown | No historical L2 archive has been verified; HYP-001 data inventory remains open |
| Alpha profitability | Unknown / not claimed | [HYP-001 preregistration](https://github.com/PandaGarry/NEXUS/blob/prototype/bybit-public-data-recorder-python-v0/experiments/bybit-public-recorder/NX-EXP-001-alpha-trade-flow-imbalance.md); no alpha result exists |
| Production exchange selection | Blocked | Exact owner/account/product eligibility and venue selection remain unresolved; public endpoint reachability is not eligibility |
| Live order execution | Not implemented / not authorized | PR #19 contains no private API, credentials, order dispatch or live trading |

## Current engineering evidence

### PR #19 — public-data recorder spike

- Code and tests are in [PR #19](https://github.com/PandaGarry/NEXUS/pull/19), current head `1051aec3b9776227c091fe9bc7c41ab7ee82d510`.
- [Unit CI run 43641738962](https://github.com/PandaGarry/NEXUS/actions/runs/43641738962) passed the three supported Python versions on code revision `223e299fd87c1f19ca990129eb7da6d3149f90b6`; the subsequent commits in the current PR head are documentation-only.
- [Live smoke run 43637091666](https://github.com/PandaGarry/NEXUS/actions/runs/43637091666) captured 11,177 journal records over approximately 10 minutes. Published topic counts are 8,149 trades and 2,998 orderbook deltas. These sum to 11,147, so 30 records remain to be classified. Do not label them as pong/control frames without inspecting the raw artifact.
- The prior artifact inspection reported 11,177 valid JSONL lines, no malformed lines, no missing SHA-256 values and no digest mismatches. Integrity and frame classification are separate checks.
- Artifact [14131465205](https://github.com/PandaGarry/NEXUS/actions/runs/43637091666/artifacts/14131465205) expires 2026-11-28. Preserve a private copy before expiry; do not publish raw exchange frames until terms and redistribution rights are reviewed.
- The first full-depth orderbook messages were `type=delta`. The live CLI still does not fetch REST snapshots or expose a synchronized book.
- GitHub-hosted runner region is suitable for public protocol reachability/capture checks only. Its timing is not a production latency benchmark.
- SHA-256 stored beside a frame detects accidental corruption relative to the stored digest; it is not tamper-proof evidence.

### M2 — next engineering gate

- The exact checklist is [M2-ACCEPTANCE.md](https://github.com/PandaGarry/NEXUS/blob/prototype/bybit-public-data-recorder-python-v0/experiments/bybit-public-recorder/M2-ACCEPTANCE.md).
- Official Bybit contract: [full-depth WebSocket](https://bybit-exchange.github.io/docs/v5/websocket/public/full-ob) is delta-only and requires [full-depth REST snapshot](https://bybit-exchange.github.io/docs/v5/market/full-ob); the bridge must align exact `seq` and `u`.
- Required fail-closed cases include update-ID gap, `u=1`, disconnect/reconnect, malformed event, wrong symbol, crossed book and buffer overflow.
- No downstream consumer may see a valid book until the REST snapshot and buffered deltas are synchronized.

### Research

- HYP-001 primary configuration is fixed: 5-second notional imbalance, absolute threshold 0.20, 3-second horizon. The remaining 17 combinations are exploratory and require Holm–Bonferroni correction for grid-wide inference.
- The instrument/venue universe must be documented separately from the confirmatory primary test. Do not change the primary configuration after inspecting OOS results.
- No positive alpha is claimed. Historical trade archives and any historical L2 coverage must be inspected before deciding what can be concluded.

## Immediate priorities

1. Reconcile the 30 unclassified records from the original artifact and preserve the artifact privately before 2026-11-28 expiry.
2. Implement and test Bybit live REST full-depth snapshot + buffered-delta synchronization, replay and fail-closed recovery per the M2 checklist.
3. Continue bounded Kraken Spot protocol/terms research, including exact CRC32 string construction and the top-10-only validation boundary; defer a second recorder until Bybit M2 is accepted.
4. Define the HYP-001 instrument/venue research universe without changing its frozen primary configuration.
5. Only after two materially different adapters are actually examined, define the smallest shared market-data contracts.
6. Keep venue/account selection blocked until exact product and eligibility are verified.

## Evidence discipline

A check mark requires an artifact, test result, official source, review or explicit owner decision. Every status must include a checked date and a link to its proof. A document draft is not an accepted architecture decision. A passing unit test is not a live protocol test. A public feed connection is not proof of account eligibility.
