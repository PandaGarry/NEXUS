# NEXUS

**NEXUS** is a personal-first trading and financial workstation under active research and early engineering. The intended product direction includes venue-neutral domain logic, provider-specific market-data/execution adapters, order-flow analytics, quantitative research, independent risk controls, reconciliation and controlled execution.

> **Current state:** early prototype and architecture research. Not production. No exchange is selected for personal live trading. No live order execution is implemented or authorized by this work.

## Start here

- [Project overview](docs/PROJECT_OVERVIEW.md)
- [Current status and evidence register](docs/PROJECT_STATUS.md)
- [Architecture decision index](docs/ADR_INDEX.md)
- [Risk register](docs/RISK_REGISTER.md)
- [Security baseline](SECURITY.md)
- [AI agent operating rules](AGENTS.md)
- [Venue qualification matrix](docs/VENUE_QUALIFICATION_MATRIX.md)
- [Product stages and commercial activation triggers](docs/PRODUCT_EVOLUTION.md)
- [External engineering / AI review guide](docs/EXTERNAL_REVIEW_GUIDE.md)
- [All open pull requests](https://github.com/PandaGarry/NEXUS/pulls)
- [Current recorder prototype — PR #19](https://github.com/PandaGarry/NEXUS/pull/19)
- [Project review hub — PR #20](https://github.com/PandaGarry/NEXUS/pull/20)
- [Recorder milestones — Issue #18](https://github.com/PandaGarry/NEXUS/issues/18)

## Non-negotiable principles

1. The domain core is venue-neutral; exchange-specific behavior stays in adapters.
2. Do not freeze a generic adapter abstraction before comparing two materially different adapters.
3. Risk approval is independent from strategy/AI and execution dispatch.
4. Invalid/stale data and uncertain order/account state fail closed for risk-increasing actions.
5. Unknown capabilities remain UNKNOWN until source-backed and, where relevant, runtime-tested.
6. Personal-first and future commercial operation are separate product stages.
7. AI agents work in isolated branches/PRs, receive no secrets and never merge or alter `main` without explicit owner authorization.
8. A Draft PR or passing unit test is not proof of production readiness.

See [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) for the review map and limitations.
