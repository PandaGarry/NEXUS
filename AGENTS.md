# NEXUS — AI agent operating rules

These rules apply to every AI coding/research agent (ChatGPT, Arena, Claude, Copilot or other tools) working on this repository. They are repository instructions, not permission to access accounts, secrets or deploy.

## Mission and authority

- Work as a careful senior engineering team: verify before changing, prefer small reviewable diffs, test, document and report honestly.
- Product direction is personal-first, venue-neutral and evidence-driven. Bybit is a technical probe, not the chosen production venue.
- The owner is the final authority for merges, live trading, credentials, risk limits, legal decisions and irreversible actions.
- Never merge a PR, push to `main`, change branch protection, delete branches, force-push, deploy, connect a private account, submit orders or alter risk limits unless the owner explicitly authorizes that exact action.
- No agent may claim a feature is complete merely because code was written or mocked tests pass.

## Required workflow for every task

1. Read `README.md`, `docs/PROJECT_STATUS.md`, this file and the task-specific acceptance checklist.
2. Inspect the current branch, base/head commits, working tree and relevant PR diff before editing. Do not assume previous summaries are current.
3. State the concrete objective, scope, acceptance criteria, risks and files expected to change.
4. Implement the smallest coherent vertical slice. Avoid speculative abstractions and unrelated refactors.
5. Add/update tests. Prefer independent fixtures and protocol-derived cases over mocks that duplicate the implementation's assumptions.
6. Run relevant tests, lint/type checks and CI where available. Record exact commands, results, runtime versions, commit SHA and workflow URL.
7. Update documentation in the same PR: `PROJECT_STATUS.md`, relevant acceptance checklist, `ADR_INDEX.md` for durable decisions, and `RISK_REGISTER.md` when risks change.
8. Review the final diff for secrets, raw exchange data, unrelated changes, stale claims, broken links and accidental scope expansion.
9. Report changed files, commit SHA, tests run/passed/failed/skipped, evidence links, limitations, remaining blockers and recommended next task.

## Status semantics

Use only four statuses:
- `IN_PROGRESS`: work is underway or evidence is incomplete.
- `TESTED`: specified tests/evidence passed, but acceptance is not complete.
- `ACCEPTED`: all written acceptance criteria passed and evidence is linked.
- `BLOCKED`: a named external, technical, legal or owner decision prevents progress.

A unit test, mocked exchange, public endpoint response or design document is never by itself production acceptance.

## Git and PR discipline

- Never work directly on `main`. Use a task-specific branch and one focused PR.
- Default target is no more than two active PRs: primary implementation/integration plus one independent docs/research PR. Avoid stacked PRs unless dependency is real and documented.
- Do not open a new PR if the work belongs in an existing active PR.
- Do not retarget a stacked PR until its dependency graph and unique diff are reviewed.
- Never overwrite another agent's work. Check branch head before updates; use non-force fast-forward commits.
- Keep PRs small enough for independent review. Split only when components can genuinely merge and be tested independently.
- A PR is not complete until tests and docs are synchronized.

## NEXUS technical and safety principles

- Public data and private account APIs are separate trust domains. No credentials, private streams or order endpoints in the recorder prototype.
- Keep raw exchange frames private unless provider terms explicitly permit publication. Never send raw exchange data to external AI agents by default.
- Preserve exact decimal values, exchange timestamps, receive timestamps, sequence IDs and provenance. Do not silently coerce, sort or repair event streams.
- Unknown means unknown. Keep venue, instrument, account, jurisdiction, data rights and capability claims evidence-backed.
- Fail closed on stale/invalid books, sequence gaps, uncertain account/order state and failed reconciliation.
- Strategies, AI agents and UI must not bypass an independent Risk boundary and a single controlled Execution Gateway.
- No withdrawal permission for trading API keys. Before any live order, require a dedicated account/subaccount, least-privilege key, IP allowlist where supported, hard risk limits, emergency stop and tested recovery.
- Do not use hosted CI latency as a production latency benchmark.
- Do not claim alpha/profitability without preregistered out-of-sample evidence and realistic executable costs.
- Respect provider terms, retention, redistribution and commercial-use restrictions. Seek qualified legal advice for legal conclusions.

## Collaboration between agents

- Each agent works in a separate branch/PR with a clearly bounded task and no secrets.
- Before coding, read current status and report overlap with active PRs.
- For review-only tasks, do not edit code. Return file/line references, failure scenario, severity, fix and a reproducible test.
- One agent is designated integrator for a task. Other agents provide independent review; conflicting changes are not merged automatically.
- The integrator evaluates feedback, records accepted/rejected recommendations and rationale in the PR/ADR, then updates status.
- External AI reviewers receive only public repository links, source code and synthetic/redacted fixtures. Do not upload credentials, account identifiers, private records or raw exchange captures unless rights and necessity are verified.

## Definition of done

A task is done only when acceptance criteria are explicit and satisfied; tests have been run and evidence linked; docs and checklist match the code; no secret/raw-data leakage or unexplained diff remains; known limitations and follow-up work are recorded; and the PR is ready for human review (not silently merged).
