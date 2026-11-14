# NEXUS Security baseline

**Scope:** personal, single-owner development/research prototype. This document does not certify production security.

## Level 1 — required now

- Protect `main`: prohibit direct pushes and force-pushes; require PR review and passing required CI checks where GitHub plan/settings support them.
- Enable GitHub secret scanning/push protection and dependency alerts where available. Verify actual repository settings; do not report them enabled without evidence.
- Keep API keys, tokens, local captures, logs containing private data and environment files out of Git. Maintain a reviewed `.gitignore`; rotate any credential ever committed.
- Pin or constrain dependencies, review automated dependency updates and keep CI permissions least-privilege.
- AI agents receive no secrets, no private account access and no production permissions.
- Keep raw exchange data private until provider terms, retention and redistribution rights are verified.

## Level 2 — mandatory before the first live order

- Use a dedicated exchange subaccount with isolated funds; API key has only required trading permissions and **no withdrawal permission**.
- Restrict key by IP allowlist where supported; store it in an OS credential manager/secret manager, never source control or agent context.
- Enforce hard limits independently of strategy/AI: max order size, position/notional, daily loss, order rate, instrument allowlist and stale-data cutoff. Missing/invalid risk state blocks risk-increasing orders.
- Provide exchange-side and application-side kill switches; test process death, network partition, duplicate command, uncertain outcome and leaked-key response.
- Reconcile orders, fills, positions and balances before resuming after restart or uncertainty.
- Keep auditable logs without exposing secrets; encrypt backups and test restore.

## Level 3 — triggered by public/commercial/multi-user operation

Before any third-party user, asset, key, tenant, paid service, data redistribution or externally authorized command: conduct a separate legal/data-rights review, tenant isolation design, credential vault/rotation, stronger audit and monitoring, incident-response plan, independent security review and penetration testing. Do not inherit personal-mode approval.

## Threat model — minimum scenarios

| Threat | Required containment |
|---|---|
| Secret committed or leaked | Secret scanning, rapid revocation/rotation, no withdrawal scope, IP restriction, isolated subaccount |
| Strategy or AI emits malicious/oversized order | Independent Risk Engine; allowlists and hard limits; AI/strategy cannot access unrestricted venue credentials |
| Execution bug / duplicate retry | Single Execution Gateway, idempotency, explicit unknown-outcome state, reconciliation; no blind retry |
| Stale/gapped order book | Sequence validation, fail-closed invalidation, freshness gate; block risk-increasing actions |
| Process crash / network partition | Durable state, kill switch, restart reconciliation, tested recovery |
| Prompt injection or compromised external agent | Treat repository/data/web content as untrusted; least privilege; no secrets; PR-only workflow |
| Malicious dependency / CI compromise | Dependency review, pinned actions/dependencies where practical, minimal CI permissions, protected main |

## Verification rule

Each control must be marked in `docs/PROJECT_STATUS.md` with evidence or remain unverified. This baseline is a plan until repository settings and runtime controls are actually checked. No claim of absolute protection is permitted.
