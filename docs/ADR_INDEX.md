# NEXUS — architecture decision index

**Last reviewed:** 2026-11-15

This index is the concise navigation point for durable decisions. Detailed specifications and historical decision records remain in their owning documents/PRs; this file does not duplicate them.

## Current working decisions

| ID | Decision | Rationale / boundary | Status |
|---|---|---|---|
| ADR-001 | Personal-first, single-owner v1 | Keeps initial product, security and legal scope bounded; commercial/multi-user use requires a separate review | IN_PROGRESS — proposed direction, not production authorization |
| ADR-002 | Product-first vertical slices; no audit phase that blocks delivery | Build measurable capabilities and validate assumptions incrementally | ACCEPTED as engineering process |
| ADR-003 | Venue-neutral domain, concrete venue-specific adapters | Avoid coupling domain semantics to one exchange; apply rule-of-two before freezing shared adapter abstractions | IN_PROGRESS |
| ADR-004 | Bybit is a technical recorder probe, not a production venue selection | A concrete first protocol enables capture/replay testing; eligibility and terms remain separate | ACCEPTED as scope boundary |
| ADR-005 | No second recorder before Bybit M2 acceptance | Avoid parallelizing adapters before first synchronization/replay evidence is sound | ACCEPTED as sequencing rule |
| ADR-006 | Independent Risk boundary and one controlled Execution Gateway before live orders | Strategy/AI/UI must not gain direct unrestricted venue authority | IN_PROGRESS — design only |
| ADR-007 | AI agents work PR-only, no secrets, no direct main changes | Limits blast radius and keeps owner approval over merges/live actions | ACCEPTED as collaboration rule |
| ADR-008 | Normally two active PRs; no automatic merge | Keep review surface manageable without losing necessary dependency history | ACCEPTED as workflow rule |

## Existing detailed decision sources

- NX-ADR-001..008 and security baseline proposals: see architecture documents linked from [PR #16](https://github.com/PandaGarry/NEXUS/pull/16).
- Owner decisions OD-01..OD-15: see [PR #6](https://github.com/PandaGarry/NEXUS/pull/6) and downstream architecture chain.
- Product/deployment profile proposal: [PR #9](https://github.com/PandaGarry/NEXUS/pull/9).
- Venue-neutral research and qualification: [PR #20](https://github.com/PandaGarry/NEXUS/pull/20) and [venue qualification matrix](VENUE_QUALIFICATION_MATRIX.md).

## Change rule

A durable decision change must include context, options considered, decision, consequences, status, date, evidence and required owner approval. Do not silently turn a proposal in a Draft PR into an accepted product decision.
