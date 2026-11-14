# NEXUS — risk register

**Last reviewed:** 2026-11-15  
**Statuses:** `IN_PROGRESS`, `TESTED`, `ACCEPTED`, `BLOCKED`  
**Scoring:** qualitative until likelihood/impact can be supported by evidence. No risk is closed by documentation alone.

| ID | Risk / failure scenario | Impact | Mitigation / evidence required | Status |
|---|---|---|---|---|
| R-01 | `main` is not protected; accidental or compromised direct change | High | Configure PR-only main, block force-push, require CI; verify actual GitHub settings and test behavior | IN_PROGRESS |
| R-02 | API key or token leaks through Git, logs or AI agent | Critical | No secrets in repo/agent context; secret scanning; revoke/rotate; no-withdrawal key and IP allowlist before live | IN_PROGRESS |
| R-03 | Bybit public-data terms do not permit intended local capture/retention | High | Resolve exact terms and scope; keep raw data private; no new live capture until gate cleared | BLOCKED |
| R-04 | Snapshot/delta bridge accepts a misaligned order book | Critical | Protocol-derived tests, independent review, live snapshot comparison, fault injection and deterministic replay | IN_PROGRESS |
| R-05 | Reconnect or sequence reset leaves stale book marked valid | Critical | Invalidate on generation change, gap and reset; prove disconnect/reconnect and `u=1` recovery | IN_PROGRESS |
| R-06 | Strategy/AI can bypass Risk or directly access venue credentials | Critical | Separate Risk and Execution boundaries; no order execution exists today; enforce before first live order | IN_PROGRESS |
| R-07 | Duplicate/ambiguous order submission after timeout | Critical | Idempotency, explicit unknown outcome, no blind retry, reconciliation; required before live orders | IN_PROGRESS |
| R-08 | Old stacked PRs carry conflicting or obsolete architecture into product | Medium/High | Inventory branch dependencies and unique diffs; extract validated assets; close/defer obsolete proposals | IN_PROGRESS |
| R-09 | Research leakage, multiple testing or unrealistic costs creates false alpha | High | Frozen HYP-001, separate exploratory strata, OOS validation, multiplicity correction, executable costs | IN_PROGRESS |
| R-10 | External AI agent receives raw exchange data or private material | High | Public code/synthetic fixtures only; bounded tasks, separate branch, PR review, no secrets | IN_PROGRESS |
| R-11 | Venue/API/data rights or account eligibility assumed from public endpoint reachability | High | Separate technical, legal, account and product qualification; keep unknowns explicit | IN_PROGRESS |
| R-12 | CI/dependency compromise modifies trusted code | High | Protected main, least-privilege CI, dependency alerts/review, pinned actions where practical | IN_PROGRESS |

## Review triggers

Review this register when a new trust boundary is added; credentials/private APIs are introduced; live orders are proposed; a new venue/data source is added; a PR changes security, execution or recovery behavior; or the product moves beyond one owner.
