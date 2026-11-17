# NEXUS — external engineering / AI review guide

**Last reviewed:** 2026-11-15  
**Purpose:** make independent review practical without requiring reviewers to reconstruct the project from every historical Draft PR.

## 1. Public review entry points

Start with these in order:

1. [AI agent operating rules](../AGENTS.md) — permissions, task workflow, testing and documentation requirements.
2. [Security baseline](../SECURITY.md) — security controls and threat scenarios.
3. [Architecture decision index](ADR_INDEX.md) and [risk register](RISK_REGISTER.md) — decisions and active risks.
4. [Project overview](PROJECT_OVERVIEW.md) — product direction, boundaries and workstreams.
5. [Project status and evidence register](PROJECT_STATUS.md) — what is implemented, tested, live-tested, proposed or unknown.
6. [Venue qualification matrix](VENUE_QUALIFICATION_MATRIX.md) — candidate venues and explicit UNKNOWN values.
7. [Product evolution](PRODUCT_EVOLUTION.md) — personal-first stages and triggers for commercial/multi-user review.
8. [PR #20 — public review hub](https://github.com/PandaGarry/NEXUS/pull/20) — proposed default-branch documentation landing page.
9. [PR #19 — public recorder implementation](https://github.com/PandaGarry/NEXUS/pull/19) — concrete Python Bybit public-data prototype, code and tests.
10. [Live-feed smoke run #10](https://github.com/PandaGarry/NEXUS/actions/runs/43637091666) — actual public-feed capture and replay evidence.
11. [Issue #18 — recorder milestones](https://github.com/PandaGarry/NEXUS/issues/18) and [Issue #21 — second adapter qualification](https://github.com/PandaGarry/NEXUS/issues/21).

The repository is public. Reviewers can inspect the default branch, open PR diffs, source branches and GitHub Actions logs/artifacts without needing private project access.

## 2. Important interpretation rules

- PRs are proposals until merged; Draft PRs are not accepted architecture.
- Code in PR #19 is a prototype, not a production recorder or trading system.
- The live smoke proves public endpoint reachability and raw capture/replay for one 10-minute run. It does not prove a valid synchronized order book, reconnect recovery, endurance, account eligibility or alpha.
- Bybit is one concrete adapter experiment, not the selected live venue.
- Coinbase and Kraken are research candidates. OKX and Binance are discovery candidates; no qualification is implied.
- The generic adapter interface is intentionally not frozen until a materially different second adapter has been examined.
- Personal-first scope does not remove legal, provider-terms, KYC, data-rights or security requirements.
- Unknown or unverified claims should remain UNKNOWN.

## 3. Suggested review prompt

You are an independent senior engineering, quantitative trading systems, exchange-integration and security reviewer. Review the public NEXUS repository and the linked pull requests as an external auditor, not as a collaborator trying to defend prior decisions.

Please:
1. Read the project overview and evidence register first.
2. Inspect PR #19 source code, tests, workflow and the live smoke logs/artifact. Verify claims independently where possible.
3. Inspect PR #20 and the proposed venue-neutral/product-stage documentation.
4. Inspect relevant architecture and research Draft PRs only where they materially affect the current design. Do not assume a Draft PR is accepted.
5. Challenge the product direction, engineering sequence, security boundaries, market-data correctness, exchange adapter assumptions, data rights, and research methodology.
6. Compare Bybit with at least one materially different venue API (Coinbase Advanced Trade or Kraken Spot are candidates). Keep product/API families distinct; do not mix Coinbase Advanced Trade with Coinbase Exchange or Kraken Spot with Kraken Futures.
7. Identify which shared adapter contracts are genuinely justified by two implementations and which should remain venue-specific.
8. Evaluate whether the current data capture can support any valid market microstructure research; distinguish trade-only, L2 and L3 claims.
9. Review the HYP-001 preregistration for leakage, multiple testing, sample-size, cost-model and robustness problems.
10. Propose a prioritized sequence of concrete changes with acceptance criteria and tests.

Return findings in this structure:
- **Critical blockers** (must fix before next milestone)
- **High-risk design/code issues**
- **Medium/low priority improvements**
- **Unsupported or overstated claims**
- **Alternative architecture / implementation recommendations**
- **Second adapter recommendation and why**
- **Next 2-week plan with measurable exit criteria**

For every finding, provide file path / PR / line or section reference, failure scenario, impact, recommended fix, and a test or evidence that would prove the fix. Separate confirmed defects from hypotheses and preferences. Do not invent user residence, account eligibility, API behavior or production readiness. Do not recommend live trading or handling credentials as a shortcut to testing.
