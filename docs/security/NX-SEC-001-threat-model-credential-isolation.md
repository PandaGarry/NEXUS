# NX-SEC-001 — Threat Model & Credential Isolation

**Status:** PROPOSED — requires owner review  
**Date:** 2026-11-14  
**Scope:** NEXUS Crypto, autonomous execution, shared Desktop + Web clients, server-side services, exchange credentials, AI Orchestrator, Risk Engine, financial ledger and deployment supply chain.  
**Method:** Asset inventory, trust-boundary analysis, STRIDE-style threat enumeration and abuse-case review. This is a design threat model, not a penetration test, security certification or proof that controls are implemented.

## 1. Security objectives

1. Prevent unauthorized creation, modification or cancellation of exchange orders.
2. Prevent theft or misuse of exchange API credentials and signing capability.
3. Ensure every risk-increasing order is independently authorized by deterministic Risk Engine policy.
4. Preserve integrity and recoverability of orders, fills, balances, positions and ledger events.
5. Prevent compromised Desktop/Web clients or AI prompts from bypassing server-side controls.
6. Detect, contain and investigate compromise without losing the evidence needed for reconciliation.
7. Keep the autonomous execution service safe when clients disconnect, AI services fail, market data degrades or dependencies are compromised.

Security is a capital-protection and correctness property. Availability must not be restored by bypassing authorization, risk limits or reconciliation.

## 2. Assets and security priorities

| Asset | Security property | Impact if compromised |
|---|---|---|
| Exchange API credentials / venue signing capability | Confidentiality, integrity, least privilege | Unauthorized venue requests and account exposure |
| RiskApprovalCapability private signing key | Confidentiality, integrity, non-exportability | Forged Risk authorization or approval replay |
| HEGC control identity, HaltState generation and EgressBoundaryAuthorization | Integrity, single-use/replay resistance, availability | Unauthorized final-send grants, stale socket initiation after halt or false HALTED acknowledgement |
| Risk evidence manifest / ValuationInputVector | Integrity, provenance, freshness | Approval against stale, substituted or incomplete valuation evidence |
| User identity, MFA factors, sessions | Authenticity, revocability | Account takeover and privileged action |
| Risk policies, limits, kill-switch state | Integrity, availability | Unbounded or unsafe trading |
| Order intents, outbox, exchange IDs | Integrity, durability | Duplicate or lost orders |
| Fills, balances, positions, ledger | Integrity, provenance | Incorrect exposure and financial reporting |
| Market data and instrument specs | Authenticity, freshness, correctness | Invalid strategy decisions and order parameters |
| AI instructions, tool permissions, context | Integrity, isolation | Prompt injection or unauthorized actions |
| Signing service / execution service | Integrity, availability, identity | Direct capital-impacting compromise |
| Database, backups, encryption keys | Confidentiality, integrity, recoverability | Broad compromise or unrecoverable state |
| Build pipeline, dependencies, release artifacts | Integrity, provenance | Supply-chain compromise |
| Audit logs and incident evidence | Integrity, confidentiality, availability | Undetected compromise and failed investigation |

Priority tiers:
- **Critical:** exchange credentials/signing, Risk Engine policy, execution authorization, single-use EgressBoundaryAuthorization, halt-state generation, order/fill/ledger integrity.
- **High:** user sessions, service identities, market data integrity, instrument metadata, backups, CI/CD.
- **Supporting:** analytics, dashboards, non-sensitive preferences and research outputs.

## 3. Trust boundaries

### TB-1 — User devices and clients
Desktop and Web clients are untrusted execution environments. They may be compromised, modified, automated or disconnected. No security-critical limit or authorization decision may exist only in client code.

### TB-2 — Public edge and identity
Internet-facing API gateway, authentication, session management, MFA and user authorization. Validate identity, device/session risk, request schema, origin/CSRF protections where applicable, quotas and authorization on every sensitive request.

### TB-3 — Internal service boundary
Market data, strategy, AI Orchestrator, Risk Engine, execution, portfolio/ledger and notification services communicate using authenticated service identities and narrowly scoped authorization. The Trusted Egress boundary alone owns venue credentials, signing capability and the actual venue socket; strategy, AI, API, adapters and ordinary dispatchers have no direct venue route or credentials. Network location alone grants no trust.

### TB-4 — Risk authorization boundary
Risk Engine is independent from strategy and AI. It receives canonical order proposals plus current account, market-data health, instrument rules and exposure state. It returns a short-lived, single-purpose approval bound to immutable command digest, account/instrument scope, reservation version, exact ValuationInputVector ID/version, StateEvidenceVector/FreshnessPolicy evidence, halt epoch, eligibility revision, expiry and policy version. Any payload or bound-evidence mutation invalidates approval.

### TB-5 — Credential and signing boundary
Risk approval signing and venue request signing are separate authority domains with separate keys, identities and policies. The private key that signs RiskApprovalCapability is held only by the Risk signing authority; Execution and Trusted Egress receive public verification material only and cannot mint or alter Risk approvals. Venue API credentials and venue request-signing capability are held only by Trusted Egress, which owns the actual venue socket. No key is reused across these domains. If a KMS/HSM or vault is later selected, it must enforce separate non-exportable key policies and narrowly scoped workload identities. AI, strategy, clients, analytics, adapters, general API services and logs cannot retrieve either private key or raw venue credentials. Prefer signing without exporting long-lived secret material into general application memory where venue protocols permit. EgressBoundaryAuthorization is a distinct one-use attempt-scoped control record, not a substitute for RiskApprovalCapability or a venue credential.

### TB-5A — Halt/Egress Gate Coordinator boundary

The Halt/Egress Gate Coordinator (HEGC) is the sole writer of authoritative HaltState and EgressBoundaryAuthorization records. It is a critical control-plane trust domain separate from Risk, Command Coordinator and the credential-owning Egress process. HEGC has no venue credentials, venue signing capability, Risk signing key or socket; it cannot transmit an order. It has a dedicated control-plane identity, write access only to its control-owned schema and narrowly scoped read-only access to Risk/Command/evidence/eligibility/dispatcher state required for final validation. HEGC final-gate transactions run at SERIALIZABLE on the authoritative primary in the same logical database; all invalidating writers must participate in that isolation protocol or a proven shared version/CAS guard. HEGC retries whole transactions on serialization/deadlock failures and resolves ambiguous commits by stable attempt ID. It receives no UPDATE privilege on source tables solely for row-locking. HEGC can authorize the halt/egress gate but cannot create or modify a RiskApprovalCapability; Trusted Egress must independently verify the Risk signature, exact command digest, active reservation, evidence bindings, audience, expiry and single-use consumption in addition to validating the HEGC grant.

Trusted Egress cannot write halt or gate records directly. It requests an opaque, persisted, one-use attempt-scoped grant from HEGC and may initiate exactly one socket-write attempt against that grant. HEGC grant issuance is idempotent on stable attempt ID: exact retries return the same grant; changed bindings conflict; ambiguous responses are resolved by reading the same attempt ID, never by creating a replacement attempt. Egress reports socket initiation only after the syscall has been invoked/returned; a local pre-send flag is not proof. If Egress pauses/crashes before reporting, HEGC retains the attempt as in-flight until the write is observed or the old sender is positively fenced. A sender fence prevents future writes but does not prove no prior socket side effect; absent a trusted initiation report the attempt remains OUTCOME_UNKNOWN with reservation held until venue reconciliation. HEGC outage denies new final gates and prevents a claim of fully enforced HALTED until durable epoch commit and boundary acknowledgement/isolation. HEGC is a critical control-plane trust domain and requires independent authentication, audit, least-privilege roles, workload identity, process/host fencing and recovery tests.

### TB-6 — Exchange boundary
External exchange REST/WebSocket APIs are untrusted networks and external state authorities. Responses may be delayed, duplicated, reordered, malformed, rate-limited or unavailable. Exchange state must be reconciled; transport success is not execution truth.

### TB-7 — Data and recovery boundary
Primary database, event store, object storage, backups and audit logs require separate identities, encryption, access policy, retention and restore controls. Backup credentials must not be available to ordinary runtime services.

### TB-8 — Build and operations boundary
Source control, CI runners, dependency registries, signing/release credentials, observability and operator consoles form a separate privileged plane. Production secrets must not be exposed to untrusted pull-request jobs or arbitrary build steps.

## 4. Threat actors and assumptions

Threat actors include:
- external attackers targeting public APIs, user accounts or exposed services;
- malware or a compromised user device/browser extension;
- malicious or compromised dependency, maintainer, CI action or build artifact;
- malicious insider or over-privileged operator;
- compromised exchange account/API key or venue-side outage;
- prompt-injection content embedded in market/news/web/user data;
- accidental operator error, misconfiguration or unsafe recovery action.

Assumptions:
- Exchange APIs and their matching engines are external dependencies; NEXUS cannot guarantee venue availability or correctness.
- The host OS, cloud control plane, identity provider and vault are high-value dependencies and must be included in deployment-specific threat review.
- No component is trusted merely because it runs on an internal network.
- AI output is untrusted input. It is not an authorization token.
- A compromised client can issue arbitrary API requests as its current user; server-side authorization and Risk Engine enforcement remain mandatory.

## 5. Threat register

| ID | Threat / abuse case | Primary impact | Required controls | Residual concern |
|---|---|---|---|---|
| SEC-01 | Stolen API key used outside NEXUS | Unauthorized trading | Trade/read-only key, no withdrawal, IP allowlist where supported, per-key scope, monitoring, revoke/rotate runbook | Venue-specific key scope and IP controls vary |
| SEC-02 | Execution service or host compromised | Arbitrary signing/orders | Isolated signer, workload identity, narrow signing policy, egress allowlist, host hardening, short-lived access, independent Risk approval | A fully compromised authorized signer remains high severity |
| SEC-03 | AI prompt injection or tool misuse | Unauthorized order proposal | AI has no secrets/signing API; typed proposal-only interface; server-side schema validation; Risk Engine veto; tool allowlist; provenance labels | Model may still generate harmful proposals |
| SEC-04 | Client tampering / forged request | Bypass UI limits | Treat clients as untrusted; server-side authz, validation, rate limits and Risk Engine; signed approval bound to payload | Stolen user session remains exploitable within its permissions |
| SEC-05 | Session theft / CSRF / token replay | Account takeover | Secure HttpOnly cookies or platform secure storage, rotation, short idle/absolute expiry, revocation, CSRF protections, MFA/step-up for sensitive actions, device/session inventory | Client malware can act as the user |
| SEC-06 | Cross-service privilege escalation | Lateral movement to execution | Per-service identities, deny-by-default policy, mTLS or equivalent authenticated transport, scoped authorization, segmentation, no shared superuser credentials | Identity/control-plane compromise |
| SEC-07 | Risk policy altered or bypassed | Excessive exposure | Policy as versioned protected artifact, dual control for changes, immutable audit, independent approval validation at dispatch, deny on unavailable/stale policy | Privileged policy administrators remain critical |
| SEC-08 | Duplicate order after timeout/retry | Duplicate exposure | Durable outbox, immutable command IDs, OUTCOME_UNKNOWN, query/reconcile before retry, venue-specific idempotency contract | Venue retention/consistency semantics vary |
| SEC-09 | Fake, stale or poisoned market data/spec | Incorrect order or risk calculation | Feed health state, provenance, sequence/checksum, freshness thresholds, versioned instrument specs, independent sanity checks, halt on invalid critical inputs | Exchange/source itself can be wrong |
| SEC-10 | DB tampering, ransomware or rollback | Corrupt order/ledger state | Least privilege, encryption, immutable/WORM audit export, point-in-time recovery, tested backups, reconciliation against exchange | Restore may reintroduce stale state |
| SEC-11 | Secret leakage through logs/crash dumps/telemetry | Credential theft | Structured redaction, denylist tests, no raw request auth headers, memory/core-dump policy, restricted telemetry, secret scanning | Runtime memory compromise |
| SEC-12 | CI/CD or dependency compromise | Malicious production artifact | Pin dependencies/actions, review provenance, protected branches, signed artifacts, isolated runners, least-privilege CI, SBOM, vulnerability/license review | Upstream zero-days |
| SEC-13 | Operator abuse or accidental unsafe action | Capital loss | RBAC, MFA/step-up, dual approval for key/policy/live enablement, just-in-time access, immutable audit, break-glass procedure | Collusion or identity-provider compromise |
| SEC-14 | Kill switch unavailable or false success | Continued unsafe orders | Independent Control Plane, authoritative halt-state generation, final Trusted Egress gate, boundary drain/fencing acknowledgement, alerts and periodic drills; venue cancel only when separately authorized and certified | Venue/network outage may prevent cancellation; an already gate-authorized/in-flight request cannot be retroactively recalled |
| SEC-15 | Backup/vault recovery compromise | Broad credential exposure | Separate backup identity, encrypted backups, dual-control restore, recovery testing, key hierarchy and rotation | Recovery process is a privileged attack path |
| SEC-16 | Resource exhaustion / API abuse | Loss of control plane or market visibility | Per-user/service quotas, bounded queues, backpressure, circuit breakers, rate-limit-aware retries, DDoS protection | Large upstream or cloud outage |

## 6. Mandatory security invariants

1. No exchange API secret, passphrase, private key or signing token is available to AI Orchestrator, strategy workers, browser/Desktop clients, general analytics or logs.
2. AI may produce a typed proposal only. It cannot mint Risk approvals, alter policy, call arbitrary URLs, or sign exchange requests.
3. Every risk-increasing command requires a valid, unexpired Risk approval bound to the exact persisted command payload and current account/instrument state.
4. Missing, stale, invalid or unavailable risk inputs fail closed for risk-increasing commands.
5. A compromised or disconnected client cannot bypass server-side limits.
6. Unknown order outcomes block blind retry and require reconciliation.
7. A private-stream gap or stale account snapshot degrades account execution health and blocks risk-increasing orders until reconciled.
8. Kill switch is enforced at the final dispatch boundary, not only in UI or AI logic.
9. Key rotation/revocation and account disablement have documented, tested procedures.
10. Security events and order decisions are auditable without recording secrets or unnecessary personal data.
11. Production and development identities, credentials, data and infrastructure are separated.
12. No live enablement until owner-approved security controls have passed evidence-based acceptance tests.

## 7. Credential lifecycle requirements

- Create venue keys with read/trade permissions only; disable withdrawal and transfer permissions. Use separate keys per environment and account where supported.
- Restrict by IP where venue supports it; do not treat IP allowlisting as a substitute for least privilege.
- Store credentials in a dedicated secrets manager or KMS-backed vault with envelope encryption, access policies and audit trails.
- Runtime access uses workload identity and least privilege; avoid static bootstrap credentials.
- Prefer short-lived/dynamic credentials where supported; otherwise define rotation, revocation and emergency replacement procedures.
- Record secret metadata (owner, purpose, consumer, creation, rotation, expiry/revocation and incident contact), never secret values.
- Redact API keys, signatures, passphrases, authorization headers, session tokens and sensitive account identifiers from logs, traces, crash reports and support bundles.
- Never store exchange secrets in Git, client bundles, browser storage, local project files, CI artifacts, issue trackers or AI context.
- Secret exposure triggers immediate containment: halt affected account, revoke key at venue, rotate dependent credentials, inspect orders/fills/ledger, preserve evidence and notify owner.
- Backup and restore of vault material requires separate access, dual control and periodic recovery testing.

## 8. Identity, authorization and operations

- Separate human identities, service identities and exchange identities.
- Use phishing-resistant MFA (e.g. passkeys/WebAuthn) for privileged human access where feasible.
- Require step-up authentication for adding/replacing exchange keys, changing risk policies, enabling live trading, changing withdrawal/transfer settings, disabling kill switch or granting privileged roles.
- Use RBAC plus resource-level authorization; default deny.
- Privileged access is just-in-time, time-limited and audited.
- Critical changes (live enablement, risk-limit increase, key permission change, vault policy change) require owner approval and preferably a second independent approver.
- Break-glass access is separate, tightly controlled, alerted, time-limited and reviewed after use.
- Alerts cover anomalous key access, signing volume, order rate, policy changes, session anomalies, secret retrieval, disabled controls and reconciliation drift.

## 9. Incident response

Minimum playbooks:
1. Exchange key suspected leaked: halt affected account; revoke key at venue; verify no withdrawal rights; inspect open orders, recent orders, fills, balances and positions; rotate; reconcile; preserve evidence.
2. Execution/signing service compromised: stop dispatch at independent gate; revoke workload identity and affected keys; isolate host; preserve forensic evidence; reconcile all accounts before restart.
3. AI prompt injection / malicious proposal: disable AI proposal path; retain prompt/source provenance; verify no order bypass; rotate affected service tokens if exposed.
4. Risk Engine or policy integrity failure: global or scoped halt; restore approved policy artifact; verify hash/version and approvals; reconcile state.
5. Database or ledger compromise: freeze risk-increasing actions; restore from verified backup into isolated environment; replay immutable events; reconcile against exchanges before resuming.
6. CI/CD or dependency compromise: block deployment; revoke exposed CI credentials; identify artifact/build provenance; rebuild from known-good source; rotate affected runtime secrets.

No automated recovery may resume live risk-increasing execution solely because a service is healthy again. Recovery requires state reconciliation and explicit policy checks.

## 10. Security verification plan

Before any prototype with credentials:
- threat-model review and owner approval;
- secret scanning on repository history and current tree;
- dependency/license/SBOM review;
- authentication/session/authorization tests;
- negative tests proving AI and client cannot reach signing interfaces;
- tests proving Risk approval is payload-bound, expires and cannot be replayed;
- fault injection for vault outage, signer outage, stale policy, revoked key and network partition;
- log/trace/crash-dump secret redaction tests;
- backup restore and key rotation/revocation drills;
- CI artifact provenance and branch protection review.

Before any live trading:
- independent security review of deployed architecture and cloud IAM;
- penetration test of public and privileged surfaces;
- exchange key scope and IP restriction evidence;
- signing boundary and kill-switch drills;
- reconciliation tests across restart, partial fills, duplicate events and venue outage;
- owner-approved residual risk register and explicit live authorization.

## 11. Standards and reference basis

- NIST SP 800-207 — Zero Trust Architecture: no implicit trust based on network location; resource-focused access decisions.
- NIST SP 800-207A — application/service identity and granular access policies for cloud-native services.
- OWASP Secrets Management Cheat Sheet — centralized secret lifecycle, least privilege, rotation/revocation, audit, CI/CD exposure and secret redaction.
- OWASP ASVS 5.0.0 — application security verification requirements baseline.
- NIST SP 800-57 key-management guidance — key lifecycle, protection and management planning.

References:
- https://csrc.nist.gov/pubs/sp/800/207/final
- https://csrc.nist.gov/pubs/sp/800/207/A/final
- https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- https://asvs.owasp.org/
- https://csrc.nist.gov/Projects/Key-Management/Key-Management-Guidelines

## 12. Open owner decisions

1. Deployment trust model: single-user self-hosted node, managed cloud, or both; define operator access and physical/tenant isolation assumptions.
2. Preferred vault/KMS options and whether a dedicated signing service/HSM is justified for initial scope.
3. Human authentication provider and required phishing-resistant MFA baseline.
4. Approval policy for live enablement, risk-limit changes, key rotation and break-glass.
5. Log/audit retention, backup geography and recovery objectives.
6. Whether local Desktop client may run any local trading connector; default recommendation is no private key material on the client.

## Status note

PROPOSED. No security control described here should be interpreted as implemented. No penetration test, secret scan, vault integration, MFA integration, signer isolation, cloud IAM review or incident drill has been performed by this document.


## WP-E — Emergency operations security boundary

### Halt/Egress Gate Coordinator authority

HEGC owns the only write path for HaltState and EgressBoundaryAuthorization; Egress has no direct write grant to those records. The Coordinator cannot sign Risk approvals or send venue requests. It validates the exact approval/reservation/evidence/eligibility/fence references and commits one-use attempt authorization against the same halt-state generation used by the halt API. Egress owns credentials/socket and reports the actual socket initiation; an absent report leaves the attempt in-flight until positive fencing. HEGC failure blocks new sends and leaves halt pending, not falsely HALTED. See NX-IF-005 §5.2.2 and NX-ADR-008 §5.5. No implementation or independent security review has been completed.


Emergency halt activation and resume MUST use authenticated, resource-scoped Control Plane permissions with step-up authentication for privileged actions and dual control only if a separately approved second independent operator exists. Halt activation must remain possible when the Risk Engine process is unavailable while the authoritative halt-state store is available. If that store is unavailable or authority is uncertain, Trusted Egress denies new sends and the system MUST NOT claim HALTED as fully enforced until durable epoch commit and all boundaries acknowledge or are positively isolated. Halt-epoch transition and final EgressBoundaryAuthorization commit serialize on the same authoritative generation: halt-first denies; gate-first is an in-flight attempt that retains reservation and must be reconciled. Egress cannot acknowledge a newer halt epoch while a paused pre-halt authorized attempt could still initiate a socket write. The guarantee is no stale/queued initiation after boundary acknowledgement, not no bytes after the wall-clock request. V1 has no offline emergency order plan and no automatic cancel-all/flatten; emergency order workflows remain disabled until exact venue/account-mode semantics are certified. Break-glass is time-limited, alerted, audited and limited to halt/isolation/credential-route containment; it cannot grant withdrawal rights, direct venue access or unrestricted signer access. AI/Strategy may submit a halt request with evidence but cannot mutate HaltState, mint EgressBoundaryAuthorization, activate arbitrary emergency plans, sign commands or resume. See [NX-IF-005](../architecture/NX-IF-005-emergency-operations-halt-risk-reduction-contract.md). No such controls are implemented or verified.
