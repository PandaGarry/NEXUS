# NEXUS — project status and evidence register

**Last reviewed:** 2026-11-15  
**Default branch:** `main`  
**Project stage:** early engineering / research prototype; not production  
**Status vocabulary:** `IN_PROGRESS`, `TESTED`, `ACCEPTED`, `BLOCKED`

A status is valid only for the exact commit, test, artifact or dated source linked in its evidence. `TESTED` is not `ACCEPTED`; unit CI is not live-exchange proof; a public endpoint is not account eligibility.

## Current decision summary

| Workstream | Status | Current truth / evidence |
|---|---|---|
| Main branch protection | BLOCKED | Last repository audit (2026-11-15) found `main` unprotected and no repository rulesets; re-check GitHub settings and configure PR-only main, force-push block and required CI before relying on this control |
| Public project landing page | IN_PROGRESS | PR [#20](https://github.com/PandaGarry/NEXUS/pull/20) contains the review hub and README replacement; not merged |
| Bybit public recorder | IN_PROGRESS | PR [#19](https://github.com/PandaGarry/NEXUS/pull/19), Python research prototype only; no private API, credentials or orders |
| Recorder unit/integration tests | IN_PROGRESS | Last passing [CI 43644001404](https://github.com/PandaGarry/NEXUS/actions/runs/43644001404) passed Python 3.11/3.12/3.13 at code head `1afaa21953aa369d634dd2c224f2495709bbdfd6`, including mocked WS → REST snapshot → LIVE_VALID → replay. Subsequent parser-hardening code/tests are committed in #19 (`ce773e1`, `54b0a51`) and require fresh CI verification; mocked integration is not exchange-live proof |
| First public-feed capture | TESTED | [Run 43637091666](https://github.com/PandaGarry/NEXUS/actions/runs/43637091666): 11,177 records in ~10 minutes; 8,149 trades + 2,998 book deltas + 29 pong + 1 subscription ACK. All records classified; no malformed lines or SHA-256 mismatches |
| Live synchronized order book / M2 | IN_PROGRESS | Snapshot bridge, journaling, synchronizer and replay implemented in #19. No successful live synchronized-book evidence yet; M2 is NOT ACCEPTED |
| Bybit data-use gate | BLOCKED | Terms interpretation for unauthenticated public-feed capture and retention is unresolved. Automated live smoke remains gated by `NEXUS_BYBIT_PUBLIC_DATA_TERMS_APPROVED=true`. Raw frames stay private |
| HYP-001 research | IN_PROGRESS | Confirmatory primary is frozen in [NX-EXP-001](https://github.com/PandaGarry/NEXUS/blob/prototype/bybit-public-data-recorder-python-v0/experiments/bybit-public-recorder/NX-EXP-001-alpha-trade-flow-imbalance.md); no profitability result is claimed |
| Second venue adapter | BLOCKED | Protocol/terms research may continue; implementation waits until Bybit M2 is accepted |
| Venue/account selection | BLOCKED | No exchange/product/account eligibility is selected or inferred |
| Risk / execution runtime | BLOCKED | Design/reference models are not production Risk Engine, Execution Gateway or order dispatch |
| Live trading | BLOCKED | Not implemented and not authorized |

## Active work and next sequence

1. **Keep #19 and #20 as the only primary active PRs.** Review #20 first as the public documentation landing page; reconcile its README with #19 before integration. No automatic merge.
2. **Continue M2 in parallel with bounded documentation cleanup.** Do not create a new audit phase that blocks engineering.
3. **Close the Bybit terms question** before another live capture or raw-data publication. Do not treat technical reachability as permission.
4. **Strengthen M2 evidence:** independent protocol review; controlled disconnect/reconnect; injected `u=1` and update-ID gap; replay of a real permitted session; compare a fresh REST snapshot with the local book over a defined observation window and documented tolerance.
5. **Keep research venue-neutral.** Kraken Spot is a protocol contrast; OKX is a historical-L2 research candidate but its personal/non-commercial restrictions make it unsuitable to assume as a future commercial data source. Evaluate commercial data licensing as a separate matrix dimension.
6. **After M2 acceptance**, implement one materially different second adapter (candidate selected from evidence and eligibility), then define only the shared contracts justified by both.

## Governance documents

- [AI agent rules](../AGENTS.md) — required workflow, permissions and collaboration boundaries.
- [Security baseline](../SECURITY.md) — controls by readiness level and minimum threat model.
- [ADR index](ADR_INDEX.md) — durable engineering decisions.
- [Risk register](RISK_REGISTER.md) — active risks and evidence needed to close them.

## Evidence snapshot

- First capture artifact [14131465205](https://github.com/PandaGarry/NEXUS/actions/runs/43637091666/artifacts/14131465205) expires **2026-11-28**. The original artifact has been inspected in this workstream, but a durable private copy under the owner's control is still required. Do not assume a temporary inspection copy is preserved.
- Recorder CI [43644001404](https://github.com/PandaGarry/NEXUS/actions/runs/43644001404) is the last cited passing test evidence for #19 at `1afaa21953aa369d634dd2c224f2495709bbdfd6`. Parser hardening in commits [`ce773e1`](https://github.com/PandaGarry/NEXUS/commit/ce773e190404ec33b2b6d2b09195fd7e8faf697c) and [`54b0a51`](https://github.com/PandaGarry/NEXUS/commit/54b0a510b254f91f1e06346a3b6ce61e13f41999) is awaiting a verified fresh CI result; do not call the current code head tested until that run passes.
- Cancelled live run [43642980172](https://github.com/PandaGarry/NEXUS/actions/runs/43642980172) is not live proof.
- Hosted GitHub runner timing is not a production latency benchmark.
- SHA-256 stored beside a frame detects accidental corruption relative to that digest; it is not tamper-proof evidence.

## PR consolidation policy

- Target: normally two active PRs — one integration/implementation PR and one independent docs/research PR. A third is allowed only for a genuinely independent urgent change.
- Stacked PRs are not merged or retargeted out of order. First map each branch's base, head, unique diff and dependencies.
- For every old PR, choose exactly one disposition: `integrate`, `cherry-pick specific assets`, `superseded/close`, or `defer with reason`.
- Preserve valuable tests/specifications before closing a branch. Do not merge a large architecture chain merely to reduce the PR count.
- No merge, branch deletion, force-push or default-branch change without explicit owner approval.

## Documentation and evidence rules

- Update this file in the same PR as any material change to code, tests, architecture, scope, status, risk or milestone.
- Every status row has a date and evidence link. If proof is missing, keep `IN_PROGRESS` or `BLOCKED`.
- Keep detailed acceptance checklists next to the relevant work package; do not duplicate them here.
- Record durable architecture decisions in [ADR index](ADR_INDEX.md); record threats and mitigations in [risk register](RISK_REGISTER.md).
- Every PR description states purpose, scope, tests/evidence, limitations, docs updated, remaining work and whether it changes behavior.
- Review this register at each PR update and before any merge/release. Never silently move a target date or promote a status.
