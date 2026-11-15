# NEXUS — project status and evidence register

**Last reviewed:** 2026-11-15  
**Default branch:** `main`  
**Project stage:** early engineering / research prototype; not production  
**Status vocabulary:** `IN_PROGRESS`, `TESTED`, `ACCEPTED`, `BLOCKED`

A status is valid only for the exact commit, test, artifact or dated source linked in its evidence. `TESTED` is not `ACCEPTED`; unit CI is not live-exchange proof; a public endpoint is not account eligibility.

## Current decision summary

| Workstream | Status | Current truth / evidence |
|---|---|---|
| Main branch protection | BLOCKED | Last repository audit (2026-11-15) found `main` unprotected and no repository rulesets. A docs-link workflow is proposed in #20; configure PR-only main, block force-push/deletion and require available checks after workflow integration. GitHub settings still need owner-side verification |
| Documentation CI | TESTED | Latest relative-link validation [run 43680185586](https://github.com/PandaGarry/NEXUS/actions/runs/43680185586) passed after replacing broken cross-PR relative references with explicit source-branch URLs. Workflow remains in PR #20 and is not yet a required main-branch check |
| Public project landing page | IN_PROGRESS | PR [#20](https://github.com/PandaGarry/NEXUS/pull/20) contains the review hub and README replacement; not merged |
| Bybit public recorder | IN_PROGRESS | PR [#19](https://github.com/PandaGarry/NEXUS/pull/19), Python research prototype only; no private API, credentials or orders |
| Recorder unit/integration tests | TESTED | Latest branch-head [CI 43680127082](https://github.com/PandaGarry/NEXUS/actions/runs/43680127082) passed all 41 tests on Python 3.11/3.12/3.13, including live `seq`-regression invalidation, malformed-root rejection and snapshot watermark edge cases. Live smoke was skipped under the terms gate; mocked integration is not exchange-live proof |
| First public-feed capture | TESTED | [Run 43637091666](https://github.com/PandaGarry/NEXUS/actions/runs/43637091666): 11,177 records in ~10 minutes; 8,149 trades + 2,998 book deltas + 29 pong + 1 subscription ACK. All records classified; no malformed lines or SHA-256 mismatches |
| Live synchronized order book / M2 | IN_PROGRESS | Snapshot bridge, journaling, synchronizer and replay implemented in #19. No successful live synchronized-book evidence yet; M2 is NOT ACCEPTED |
| Bybit data-use gate | BLOCKED | Written clarification request due 2026-11-18; record response or no-response decision by 2026-11-24. Automated live smoke remains gated by `NEXUS_BYBIT_PUBLIC_DATA_TERMS_APPROVED=true`. Raw frames stay private |
| HYP-001 research | IN_PROGRESS | Confirmatory primary is frozen in [NX-EXP-001](https://github.com/PandaGarry/NEXUS/blob/prototype/bybit-public-data-recorder-python-v0/experiments/bybit-public-recorder/NX-EXP-001-alpha-trade-flow-imbalance.md); no profitability result is claimed |
| Second venue adapter | BLOCKED | Protocol/terms research may continue; implementation waits until Bybit M2 is accepted |
| Venue/account selection | BLOCKED | No exchange/product/account eligibility is selected or inferred |
| Risk / execution runtime | BLOCKED | Design/reference models are not production Risk Engine, Execution Gateway or order dispatch |
| Live trading | BLOCKED | Not implemented and not authorized |

## Active work and next sequence

1. **Keep #19 and #20 as the only primary active PRs.** Review #20 first as the public documentation landing page. The current changed-file inventory shows #19 does not modify the root `README.md`; after #20 is integrated, verify #19 against the new base and preserve its recorder-specific README. No automatic merge.
2. **Continue M2 in parallel with bounded documentation cleanup.** Do not create a new audit phase that blocks engineering.
3. **Close the Bybit terms question** before another live capture or raw-data publication. Do not treat technical reachability as permission.
4. **Strengthen M2 evidence:** exact-head CI for latest runtime hardening; independent protocol review; controlled disconnect/reconnect; injected `u=1` and update-ID gap; replay of a real permitted session; reconcile REST snapshot by buffering WS, advancing through its exact `seq/u` watermark, then comparing both books at a later common watermark. Do not use arbitrary tolerances.
5. **Keep research venue-neutral.** Kraken Spot is a protocol contrast; OKX is a historical-L2 research candidate but its personal/non-commercial restrictions make it unsuitable to assume as a future commercial data source. Evaluate commercial data licensing as a separate matrix dimension.
6. **After M2 acceptance**, implement one materially different second adapter (candidate selected from evidence and eligibility), then define only the shared contracts justified by both.

## Governance documents

- [AI agent rules](../AGENTS.md) — required workflow, permissions and collaboration boundaries.
- [Security baseline](../SECURITY.md) — controls by readiness level and minimum threat model.
- [ADR index](ADR_INDEX.md) — durable engineering decisions.
- [Risk register](RISK_REGISTER.md) — active risks and evidence needed to close them.

## Evidence snapshot

- First capture artifact [14131465205](https://github.com/PandaGarry/NEXUS/actions/runs/43637091666/artifacts/14131465205) expires **2026-11-28**. The original artifact has been inspected in this workstream, but a durable private copy under the owner's control is still required. Do not assume a temporary inspection copy is preserved.
- Recorder CI [43646661506](https://github.com/PandaGarry/NEXUS/actions/runs/43646661506) passed all 37 tests on Python 3.11/3.12/3.13, including parser-hardening regressions at code commit [`54b0a51`](https://github.com/PandaGarry/NEXUS/commit/54b0a510b254f91f1e06346a3b6ce61e13f41999). Later PR #19 commits update acceptance documentation and CI path filters only; no subsequent runtime-code change is present. Live smoke remains skipped under the terms gate.
- Cancelled live run [43642980172](https://github.com/PandaGarry/NEXUS/actions/runs/43642980172) is not live proof.
- Hosted GitHub runner timing is not a production latency benchmark.
- SHA-256 stored beside a frame detects accidental corruption relative to that digest; it is not tamper-proof evidence.

## Legacy PR disposition — provisional

The open PR inventory currently contains #1–#17 plus active #19 and #20. Only #19 and #20 are active delivery lanes. The older PRs are parked for review; their branches and review history are preserved, and none is approved for merge.

| PR group | Contents | Current disposition |
|---|---|---|
| #1–#9 | Early project charter, architecture/requirements, owner decisions, product profile and banking/venue research | Historical source material. Review for unique owner decisions and research not already represented in #20; do not merge the chain wholesale |
| #10–#13 | Exact numeric kernel, instrument/domain reference models, financial rounding and venue-neutral golden fixtures | Potentially reusable code/tests. Keep isolated until a concrete product slice needs them; independently review before cherry-pick/integration |
| #14 | Venue eligibility and egress-fencing reference models plus jurisdiction research | Preserve as a separate eligibility/security workstream; not a dependency of the public recorder |
| #16 | Large execution/trust/G1 architecture and reference-model suite | Future pre-live design evidence, not production implementation. Do not merge wholesale into the current prototype |
| #17 | Bybit V5 market-data qualification research | Compare against #19 M2 and #20 venue matrix; extract only unique, source-backed findings |

The consolidation decision for each old PR is one of: integrate selected commits/files, superseded/close while preserving its branch, or defer with a named trigger. Closing old PRs is a separate owner-visible action; no PR has been closed or merged in this pass.

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
