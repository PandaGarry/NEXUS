# NX-PRODUCT-COMMS-001 — Public release communication standard

**Status:** approved working standard for future publication; no public channels are launched by this document.
**Date:** 2026-11-14

## 1. Purpose

NEXUS engineering records are the internal source of truth. Public product updates must translate verified product changes into concise, accurate information that helps users understand what changed and whether they need to act.

The product platform's release notes are the canonical public record. Community channels may distribute or summarize those notes later; they must not become competing sources of truth.

## 2. Public release-note structure

Each public update should contain only the sections that materially apply:

1. **What changed** — one short, factual summary.
2. **What this means for users** — practical benefit or changed behavior.
3. **Fixes and improvements** — only user-visible, verified changes.
4. **What users need to do** — compatibility, migration or action required; explicitly say when no action is needed.
5. **Availability and limitations** — release status, supported scope and important constraints.

Use plain language. Prefer concrete outcomes over implementation details. Do not publish a section merely to fill the template.

## 3. Publication gates

A change is eligible for a public release note only when:

- The relevant change is merged into the designated release branch.
- Required CI and release checks pass on the exact released commit.
- User-facing documentation is current.
- Security-sensitive changes receive the required review.
- Known limitations, compatibility impact and rollback/support path are understood.
- The release owner approves the final text and the actual availability/status claim.

A passing test fixture, draft PR, prototype or design document is not a production release and must never be described as one.

## 4. Information boundaries

Never include in public posts:

- Credentials, tokens, private endpoints, customer/account data or personal information.
- Raw internal checklists, unredacted CI logs, private incident details or security-sensitive exploit instructions.
- Unmerged plans, hypotheses or speculative dates presented as commitments.
- Performance, reliability, security, profitability or automation claims without appropriate measured evidence and review.
- Internal architecture details that do not help users make a decision.

Security advisories and material incidents require a separate reviewed disclosure process.

## 5. Channel strategy and activation gates

Planned future distribution channels:

- In-product/platform release notes — canonical public source.
- Telegram and/or MAX — concise announcements and service notices.
- VK community — announcements, educational material and user support routing.
- Additional channels only where a clear audience and support owner exist.

Do not activate channels until all of the following are in place:

- Stable, genuinely user-available product scope.
- Named owners for publishing, moderation and support escalation.
- Privacy, moderation and community rules.
- Incident/status communication and account-recovery procedures where applicable.
- A repeatable release cadence and a single canonical link back to platform documentation.

Channel creation is a launch project with its own checklist; it is not evidence of product readiness.

## 6. Internal release preparation checklist

- [ ] Exact released commit and version recorded.
- [ ] User-visible impact verified.
- [ ] Documentation and compatibility notes updated.
- [ ] Security/privacy review completed where applicable.
- [ ] Known limitations and required user actions stated.
- [ ] Rollback/support readiness confirmed.
- [ ] Public text reviewed for accuracy, clarity and unnecessary internal detail.
- [ ] Release owner approval recorded.
- [ ] Canonical platform note published; community posts link back to it.

## 7. Current disposition

This standard is preparatory. NEXUS is still in engineering qualification; no production availability or community-channel launch is claimed. Internal technical status remains in the repository. Public communication begins only for changes that pass the publication gates above.
