# NEXUS — project status and evidence register

**Last reviewed:** 2026-11-15  
**Status vocabulary:** Proposed / In Progress / Verified / Blocked / Deferred

This is a dated evidence snapshot. Every status is scoped to the cited commit, CI run or source. A passing test or public connection is not production certification.

## Repository / integration status

| Item | Status | Evidence / limitation (checked 2026-11-15) |
|---|---|---|
| Public repository and review access | Verified | [Repository](https://github.com/PandaGarry/NEXUS); default branch `main` |
| Main branch project overview | In Progress | [PR #20](https://github.com/PandaGarry/NEXUS/pull/20) remains open and unmerged; review-hub proposal is not on `main` (checked 2026-11-15) |
| Legacy architecture/documentation chain | In Progress | [Open PR list](https://github.com/PandaGarry/NEXUS/pulls); each PR must be checked for current base/head before relying on it |
| Independent recorder spike | In Progress | [PR #19](https://github.com/PandaGarry/NEXUS/pull/19), head `7ec12122937c84f281f7a913b4d607ae6bbc68a6`, based directly on `main`, Draft/open |
| Recorder unit CI | Verified | [Run 43643265811](https://github.com/PandaGarry/NEXUS/actions/runs/43643265811) passed Python 3.11/3.12/3.13 on code revision `12ef58ad7c4b50210d9fa0e9f310628a61068504`; later PR #19 commits in this review changed documentation only |
| Live public exchange capture | Verified — first 10-minute smoke only | [Run #10](https://github.com/PandaGarry/NEXUS/actions/runs/43637091666); artifact [14131465205](https://github.com/PandaGarry/NEXUS/actions/runs/43637091666/artifacts/14131465205), expires 2026-11-28. It is not M1 or production certification |
| Published frame accounting | Verified / reconciled | Original artifact #10 independently classified 2026-11-15: 8,149 trades + 2,998 book deltas + 29 pong replies + 1 subscription acknowledgement = 11,177; zero malformed/non-JSON/other records, zero SHA-256 mismatches |
| Live order-book reconstruction | Implemented in prototype; live proof pending | [PR #19](https://github.com/PandaGarry/NEXUS/pull/19) now fetches and journals the public REST full-depth snapshot, bridges buffered WS deltas at exact `u` + `seq`, invalidates on reset/gap/disconnect and supports journal replay. [Run 43642980172](https://github.com/PandaGarry/NEXUS/actions/runs/43642980172) was cancelled before capture completed; future live smoke is gated pending Bybit API terms review; M2 remains NOT ACCEPTED |
| M2 acceptance | In progress / not accepted | [M2 acceptance checklist](https://github.com/PandaGarry/NEXUS/blob/prototype/bybit-public-data-recorder-python-v0/experiments/bybit-public-recorder/M2-ACCEPTANCE.md); implementation exists, but live synchronized-book proof, reconnect/fault injection and acceptance evidence remain open; target 2026-11-28 |
| Historical L2 coverage | Partially documented; archive validation open | OKX official portal advertises high-resolution L2 from 2023-03; no sample archive has yet been downloaded/validated. Bybit historical L2 coverage remains unverified by NEXUS |
| Alpha profitability | Unknown / not claimed | [HYP-001 preregistration](https://github.com/PandaGarry/NEXUS/blob/prototype/bybit-public-data-recorder-python-v0/experiments/bybit-public-recorder/NX-EXP-001-alpha-trade-flow-imbalance.md); no alpha result exists |
| Production exchange selection | Blocked | Exact owner/account/product eligibility and venue selection remain unresolved; public endpoint reachability is not eligibility |
| Live order execution | Not implemented / not authorized | PR #19 contains no private API, credentials, order dispatch or live trading |

## Current engineering evidence

### PR #19 — public-data recorder spike

- Code and tests are in [PR #19](https://github.com/PandaGarry/NEXUS/pull/19), current head `0f2de4fa8a57b3296d3701e3a0f0ff2d7a79d66b`.
- [Unit CI run 43643265811](https://github.com/PandaGarry/NEXUS/actions/runs/43643265811) passed Python 3.11, 3.12 and 3.13 on code revision `12ef58ad7c4b50210d9fa0e9f310628a61068504`; the subsequent PR #19 commits in the current head changed documentation only.
- [Live smoke run 43637091666](https://github.com/PandaGarry/NEXUS/actions/runs/43637091666) captured 11,177 journal records over approximately 10 minutes. Exact classification: 8,149 trade-topic + 2,998 orderbook-topic + 29 pong replies (`op=ping`, `ret_msg=pong`) + 1 subscription acknowledgement = 11,177. The count discrepancy is closed.
- The prior artifact inspection reported 11,177 valid JSONL lines, no malformed lines, no missing SHA-256 values and no digest mismatches. Integrity and frame classification are separate checks.
- Artifact [14131465205](https://github.com/PandaGarry/NEXUS/actions/runs/43637091666/artifacts/14131465205) expires 2026-11-28. The ZIP was downloaded into the current working session for inspection, but a user-controlled durable private copy is still required. Do not publish raw exchange frames until terms and redistribution rights are reviewed.
- The first full-depth orderbook messages were `type=delta`. The live CLI still does not fetch REST snapshots or expose a synchronized book.
- GitHub-hosted runner region is suitable for public protocol reachability/capture checks only. Its timing is not a production latency benchmark.
- SHA-256 stored beside a frame detects accidental corruption relative to the stored digest; it is not tamper-proof evidence.

### M2 — next engineering gate

- The exact checklist is [M2-ACCEPTANCE.md](https://github.com/PandaGarry/NEXUS/blob/prototype/bybit-public-data-recorder-python-v0/experiments/bybit-public-recorder/M2-ACCEPTANCE.md). REST snapshot fetch, validation, journal, live synchronizer and deterministic replay are implemented; unit CI passed all three Python versions. Live proof, fault injection and reconnect acceptance remain open.
- Official Bybit contract: [full-depth WebSocket](https://bybit-exchange.github.io/docs/v5/websocket/public/full-ob) is delta-only and requires [full-depth REST snapshot](https://bybit-exchange.github.io/docs/v5/market/full-ob); the bridge must align exact `seq` and `u`.
- Required fail-closed cases include update-ID gap, `u=1`, disconnect/reconnect, malformed event, wrong symbol, crossed book and buffer overflow.
- No downstream consumer may see a valid book until the REST snapshot and buffered deltas are synchronized.
- Bybit API Terms (updated 2026-10-20) restrict benchmarking, repackaging/resale and commercial exploitation; Section 2.3 API-key applicability to unauthenticated public endpoints needs clarification. Raw data remain private and future live smoke is gated by `NEXUS_BYBIT_PUBLIC_DATA_TERMS_APPROVED=true`.

### Research

- HYP-001 primary configuration is fixed: 5-second notional imbalance, absolute threshold 0.20, 3-second horizon. The remaining 17 combinations are exploratory and require Holm–Bonferroni correction for grid-wide inference.
- The candidate instrument/venue universe is registered in [RESEARCH-UNIVERSE.md](https://github.com/PandaGarry/NEXUS/blob/prototype/bybit-public-data-recorder-python-v0/experiments/bybit-public-recorder/RESEARCH-UNIVERSE.md), separately from the frozen confirmatory primary. Kraken Spot has historical Time & Sales through 2026-09-30 but no L2 evidence; OKX advertises tick trades since 2021-09 and high-resolution L2 since 2023-03; Binance publishes raw trades/aggTrades but only coarse percentage-band `bookDepth`, and its dataset terms prohibit live proprietary execution. OKX archive samples, historical side semantics, account eligibility and restrictive personal-use terms still require validation.
- No positive alpha is claimed. Historical trade archives and any historical L2 coverage must be inspected before deciding what can be concluded.

## Immediate priorities

1. Preserve a user-controlled private copy of artifact #10 before its 2026-11-28 expiry; the count discrepancy is already resolved.
2. Resolve the Bybit API terms gate, then run an approved integrated M2 smoke and demonstrate disconnect/reconnect, injected `u=1` and update-ID gap recovery.
3. Continue bounded Kraken Spot protocol/terms research, including exact CRC32 string construction, the top-10-only validation boundary and the historical Time & Sales terms; defer a second recorder until Bybit M2 is accepted.
4. Define the HYP-001 instrument/venue research universe without changing its frozen primary configuration.
5. Only after two materially different adapters are actually examined, define the smallest shared market-data contracts.
6. Keep venue/account selection blocked until exact product and eligibility are verified.

## Evidence discipline

A check mark requires an artifact, test result, official source, review or explicit owner decision. Every status must include a checked date and a link to its proof. A document draft is not an accepted architecture decision. A passing unit test is not a live protocol test. A public feed connection is not proof of account eligibility.
