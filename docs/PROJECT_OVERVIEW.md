# NEXUS — public project overview

**Last reviewed:** 2026-11-15  
**Project status:** early engineering / research prototype; not production  
**Repository:** https://github.com/PandaGarry/NEXUS  
**Current review hub:** this document and the linked active pull requests

## 1. What NEXUS is

NEXUS is being developed as a professional, personal-first trading and financial workstation. The long-term product direction includes market-data ingestion, order-flow analytics, quantitative research and simulation, portfolio/ledger state, independent risk controls, and controlled execution.

The first release is a closed single-owner product. A future multi-user/commercial product is a separate product and legal/security workstream, not an automatic extension of the personal deployment.

## 2. Current truth — read this before reviewing

- The default branch currently contains only a small initial README and two early research/reference documents. Most of the engineering and architecture work is still in open Draft PRs.
- No PR in the active chain should be treated as merged or owner-approved merely because it exists.
- The public-data recorder in PR #19 is an experimental Python spike. It is not a production market-data service and does not implement order execution.
- CI unit tests have passed, but this is not evidence of successful live exchange connectivity. The first live public-feed smoke run is tracked separately and must be checked for its final result and artifacts.
- No exchange has been selected for personal live trading. Public market-data research and trading eligibility are separate questions.
- No production Rust engine, live credentials, private account connection, order dispatch, deposits, withdrawals, or live trading are implemented or authorized by this work.
- Architecture and security proposals remain subject to explicit owner review and readiness gates.

For precise status, use [Project status and evidence](PROJECT_STATUS.md), [active PRs](https://github.com/PandaGarry/NEXUS/pulls), and the linked CI runs rather than inferring completion from document existence.

## 3. Core engineering principles

1. **Venue-neutral domain, venue-specific adapters.** The domain core must not depend on one exchange's field names, sequence counters, order IDs, product names or REST paths.
2. **Do not invent abstractions prematurely.** Implement the first adapter concretely; compare it with a materially different second adapter; only then freeze shared adapter interfaces (the "rule of two").
3. **A venue is not a product.** Spot, perpetual swaps, dated futures, options and broker-listed derivatives have distinct instrument, funding, expiry, settlement, margin and eligibility semantics.
4. **Unknown means unknown.** No unsupported capability is upgraded to "yes" without source evidence and, where relevant, a live protocol test.
5. **Independent risk and controlled execution.** Strategy/AI components do not bypass risk approval or directly own unrestricted exchange credentials.
6. **Fail closed on uncertain state.** Stale or invalid market data, sequence gaps, unknown order outcomes and unreconciled account state block risk-increasing actions.
7. **Evidence before claims.** Tests, CI, live smoke tests, benchmarks, legal/account eligibility and production readiness are separate evidence classes.
8. **Personal first, commercial later.** Third-party users, customer assets, shared tenancy or customer credentials trigger a new security, legal, data-rights and product review.

## 4. Workstreams

| Workstream | Purpose | Current status |
|---|---|---|
| Public market data | Capture, replay, normalize and validate public exchange feeds | Experimental Python spike in PR #19 |
| Venue qualification | Compare product, API, market-data, execution and eligibility capabilities | Preliminary Coinbase/Kraken research; Bybit recorder is one technical probe |
| Domain / financial correctness | Instrument semantics, exact arithmetic, fees, funding and ledger invariants | Reference models and tests in Draft PR chain |
| Risk / execution integrity | Independent risk approval, idempotency, reconciliation and emergency controls | Architecture/specification drafts; not production implementation |
| Strategy research | Falsifiable hypotheses, OOS validation and realistic costs | Initial HYP-001 preregistration in PR #19 |
| Product / governance | Personal-first scope, review process and readiness gates | Draft documentation in PR chain |

## 5. Venue strategy

Bybit is **not** the project target or a selected production venue. It is currently one public-data recorder experiment because a concrete protocol makes it possible to test capture/replay plumbing.

The initial comparison should include materially different APIs and market models. Coinbase and Kraken are already present in preliminary research; other venues can be added through the same qualification matrix. The actual shortlist must depend on the owner's real eligibility, desired instrument family, account type, API terms and operational needs. No location or account eligibility is inferred from the app or network.

See [Venue qualification matrix](VENUE_QUALIFICATION_MATRIX.md).

## 6. Review entry points

- [Project status and evidence](PROJECT_STATUS.md)
- [Venue qualification matrix](VENUE_QUALIFICATION_MATRIX.md)
- [Product evolution and activation triggers](PRODUCT_EVOLUTION.md)
- [Open pull requests](https://github.com/PandaGarry/NEXUS/pulls)
- [Draft architecture / interface documents](https://github.com/PandaGarry/NEXUS/tree/engineering/bybit-v5-market-data-qualification-v0/docs/architecture)
- [Recorder prototype PR #19](https://github.com/PandaGarry/NEXUS/pull/19)
- [Recorder milestones issue #18](https://github.com/PandaGarry/NEXUS/issues/18)

## 7. How external reviewers should review NEXUS

Please distinguish:
- **Implemented** code from proposed architecture;
- deterministic unit tests from live exchange tests;
- public market-data access from account/trading eligibility;
- one venue's adapter behavior from domain-core requirements;
- personal-use scope from a future commercial product.

Review questions are welcome on the relevant PR. High-value feedback should identify a concrete risk, reproducible counterexample, missing acceptance criterion, or source-backed alternative. Do not assume Draft PRs are accepted decisions.
