# NX-ARCH-006 — Modular Product Boundaries, Extension Contracts & Trust Isolation

**Status:** PROPOSED — architecture direction for review; not an accepted implementation baseline  
**Date:** 2026-11-14  
**Scope:** Product modularity, independent evolution, module admission, trust boundaries, identity/access, demo and learning domains  
**Related:** NX-ARCH-001..005, NX-SEC-001, NX-IF-001..005, NX-REF-EXEC-002, NX-RESEARCH-010  
**Non-goals:** Selecting a framework, service mesh, database, identity provider, plugin runtime, cloud, or deployment topology; authorizing public registration, real users, live trading, or third-party extensions.

## 1. Executive decision proposal

NEXUS should be designed as a modular platform with a protected domain core and independently governed product modules. Modularity is a source-code and deployment boundary, not a collection of Git branches and not permission to load arbitrary extensions into the core process.

The preferred evolution path is:

1. Begin with explicit bounded contexts and ports/contracts; avoid premature microservice sprawl.
2. Keep the authoritative trading domain in a small, separately protected core.
3. Keep product capabilities (Identity & Access, Demo, Learning/Knowledge, Analytics, Notifications, integrations) behind versioned contracts.
4. Give each module a distinct workload identity, minimum permissions, owned data boundary and independently testable release.
5. Admit only explicitly allowlisted, signed, policy-compliant module builds and contract versions.
6. Keep demo money, demo positions, demo orders, learning progress and content technically incapable of becoming live balances, live orders, or core trading authority.
7. Permit the core to accept only narrowly defined, authenticated and validated commands/events—not arbitrary module code, SQL, scripts, callbacks or direct database writes.

This is a proposal, not an implementation or a security certification.

## 2. Architectural shape

### 2.1 Logical boundaries

- **Protected Domain Core:** canonical command model, independent Risk authority, durable reservation and command/outbox semantics, Execution state, Ledger posting/reconciliation, recovery barriers, halt state and trusted egress. The core owns all financial and trading invariants.
- **Contract Gateway / Module Admission:** authenticates workload identity; checks module ID, approved build digest, contract/API version, capability grants, schema, request size/rate and current policy; rejects unknown, stale, revoked or over-privileged modules.
- **Identity & Access module:** registration (only when product scope allows it), authentication, MFA/passkeys, session lifecycle, account recovery and user-facing profile. It does not decide financial risk, grant trading authority, or hold venue credentials.
- **Demo module/domain:** virtual accounts, synthetic balances, simulated orders/fills, demo positions, reset/replay and educational exercises. It uses a separate ledger namespace/store and simulated execution path.
- **Learning & Knowledge module:** wiki, lessons, documentation, tutorials, quizzes and learning progress. It is not a source of market/trading commands and has no access to account secrets.
- **Other optional modules:** analytics, notifications, reporting, connectors and future capabilities, each with a named owner, contract, data classification and capability profile.

### 2.2 Initial topology recommendation

Use a modular monolith or a small number of separately deployed trust domains, not a microservice per feature from day one. Enforce module boundaries in code and tests now; split a module into a separate process/service when its threat profile, scaling, release independence or operational ownership justifies the added distributed-systems cost.

A module must not import core internals merely because it shares a repository. Cross-boundary calls go through public interfaces. No module may write another module's tables or reach into another module's private storage.

## 3. Module contract and admission protocol

Every module must have a reviewed manifest containing at least:

- stable module ID and owner;
- artifact/build digest and provenance reference;
- publisher identity and signature;
- module version, supported contract versions and compatibility range;
- requested capabilities and declared data classifications;
- owned routes, event types and schemas;
- resource ceilings (CPU/memory/concurrency/request size/rate);
- outbound network destinations and required secret references (normally none);
- health/readiness behavior, failure mode, disable/rollback procedure;
- dependency inventory, licenses, SBOM and vulnerability disposition.

Admission is deny-by-default. The platform compares the manifest with a repository-controlled allowlist/policy and verifies the exact artifact digest and signature before enabling it. A valid signature proves provenance/integrity under a trust key; it does not prove the module is safe or correct.

The gateway validates every request independently. A module-supplied user_id, role, account_id, risk_status, balance, approval, or venue_eligibility is untrusted input unless independently bound to authenticated context and authoritative core state. Never accept a module's assertion that a trade is safe or approved.

### 3.1 Contract rules

- Explicit, versioned request/response and event schemas; compatibility tests and deprecation windows.
- No arbitrary SQL, dynamic code execution, shell access, unrestricted filesystem access or generic execute endpoint.
- No direct mutation of core-owned tables.
- Idempotency keys, bounded payloads, timeouts, replay protection and correlation IDs for commands.
- Event consumers tolerate duplicate, delayed and reordered delivery; events are not a substitute for authoritative reads.
- Unknown fields/versions and authorization ambiguity fail closed for privileged operations.
- A module cannot expand its own capabilities or install/enable another module.
- Contract changes are reviewed as security-relevant changes; breaking changes require explicit migration and rollback plans.

## 4. Trust zones and capability model

Use distinct identities and authorization policies for:
1. end user;
2. module workload;
3. core service;
4. Risk authority;
5. trusted egress workload;
6. operator/break-glass identity;
7. build/release automation.

Capabilities must be explicit, scoped, time-bounded where practical, revocable and auditable. Prefer narrow actions (for example, demo.account.read and learning.progress.write) over broad roles (for example, admin or trading). No module receives risk.approve, ledger.post, venue.credentials.read, egress.send, halt.override or equivalent privileged capabilities.

The core independently authenticates workload identity (for example, via mutually authenticated transport and/or signed workload credentials), verifies audience, issuer, expiry, key ID, revocation/rotation state and required scope, and then evaluates user authorization against authoritative policy. A module's own authorization check is not sufficient for a core-sensitive operation.

A signed module manifest is an admission control, not a runtime substitute for isolation. Separate process/container/host/network boundaries, OS identity, syscall/resource restrictions and independent secret mounts are needed according to threat level. Never rely on an in-process plugin sandbox as the sole security boundary for untrusted code.

## 5. Identity & Access boundary

Identity is security-critical and must not become a privileged plugin that the rest of the platform blindly trusts.

- Authentication establishes identity; authorization is evaluated by the service owning the protected resource.
- Use established, maintained identity standards and libraries after a separate security qualification; do not invent password hashing, token formats, cryptography or MFA protocols.
- Passwords (if supported) require a reviewed modern password-hashing scheme with per-user salts and explicit cost parameters; secrets are never logged or returned.
- Prefer phishing-resistant passkeys/WebAuthn for strong authentication where feasible; MFA, step-up authentication and recovery need separate threat analysis.
- Session cookies/tokens require secure transport, appropriate HttpOnly/Secure/SameSite settings where browser cookies are used, short-lived access, controlled refresh rotation, revocation and device/session inventory.
- Protect against credential stuffing, brute force, enumeration, CSRF, XSS, SSRF, session fixation, replay and account-recovery takeover; apply rate limits and abuse detection without leaking account existence.
- Core services verify token signature and claims themselves and do not trust UI-supplied identity or role fields.
- Recovery and privileged account changes require risk-based step-up and auditable flows; operator recovery is separate from user recovery.
- Identity service compromise must not directly expose exchange credentials, bypass Risk, post Ledger entries or send venue traffic.

## 6. Demo domain — hard separation from live trading

Demo is a separate financial simulation domain, not a flag that changes the meaning of a live account.

Mandatory invariants:
- Distinct account type, namespace, identifiers, storage ownership and ledger/journal.
- Virtual assets are non-withdrawable, non-transferable to live accounts and never represented as real deposits or collateral.
- Demo execution uses a simulator or explicitly isolated sandbox adapter; no route from demo requests to production venue credentials or live egress.
- The core rejects any attempt to use a demo identity/account against a live command path and vice versa.
- No shared mutable balance/position tables; no cross-domain SQL joins that can mutate financial state.
- UI labels are not the control: server-side account type, service identity, database permissions and egress policy enforce the boundary.
- Demo resets and synthetic fills are auditable and idempotent; simulation assumptions and market-data delays are disclosed.
- Tests prove no demo request can reach the live egress boundary, including forged IDs, replay, stale tokens, routing mistakes and module compromise.

If a future paper/shadow environment uses real venue market data or venue sandbox APIs, it remains a separate environment with its own credentials, policy and egress allowlist. It must not be conflated with the user-facing virtual-balance Demo.

## 7. Learning & Wiki domain

Learning content and progress are a separate low-privilege product domain:
- content publishing is role-controlled, reviewed and versioned;
- rendered Markdown/HTML is sanitized; uploads are type/size scanned and stored outside executable paths;
- quizzes/progress are user-scoped and cannot write trading state;
- learning module has no access to authentication secrets, venue keys, risk reservations, balances or ledger write paths;
- content can explain trading concepts but cannot issue privileged actions through embedded scripts or arbitrary links;
- progress events are informational and cannot alter account permissions or risk limits.

## 8. Data ownership and storage isolation

Each bounded context owns its schema/storage and migrations. Access is granted by service identity and least privilege, not by shared application credentials. Separate databases or clusters may be justified for the highest-risk domains; the exact storage split remains subject to OD-09 and threat/deployment review.

Minimum rules:
- no shared superuser credentials;
- separate DB roles and ownership, no cross-module write grants;
- encrypted transport and storage with reviewed key lifecycle;
- secrets obtained only by authorized workloads through a controlled secret boundary;
- tenant/user isolation enforced server-side and tested at every query boundary;
- retention, deletion, backup, restore and audit policy per data class;
- migrations are forward/backward compatible where rolling releases require it;
- no secrets, session tokens, personal data or full financial payloads in logs/telemetry.

## 9. Failure containment and lifecycle

A module must be independently disableable, restartable and rollbackable. Its outage must not corrupt core state or prevent emergency controls. Optional modules fail closed for their own privileged actions and fail independently; the core remains authoritative.

Lifecycle:
1. build in isolated CI with pinned dependencies and no production secrets;
2. generate SBOM and provenance; scan dependencies and artifacts;
3. review manifest, contract diff, permissions and data classification;
4. sign immutable artifact and verify signature/digest at deployment;
5. deploy disabled or in shadow/read-only mode;
6. run health, contract, isolation and adversarial tests;
7. explicitly enable only the approved module/version/capability set;
8. monitor bounded metrics and security events;
9. revoke/disable on policy breach; preserve audit evidence;
10. rollback to a known-good signed artifact and compatible schema.

Hot-loading arbitrary code into the core process is not an approved extension mechanism. No self-updating production module.

## 10. Threats and adversarial verification

Required threat scenarios include:
- compromised module attempts lateral movement, core table access, secret discovery or direct venue egress;
- forged user/account/role/approval claims; confused-deputy and IDOR;
- compromised identity module or stolen refresh token;
- malicious or compromised dependency/build pipeline/publisher key;
- unsigned, substituted, downgraded or revoked module artifact;
- contract downgrade, schema confusion, duplicate/replayed command and oversized payload;
- demo-to-live routing confusion and forged account identifiers;
- stored/reflected XSS, unsafe uploads and malicious wiki content;
- telemetry/log exfiltration and high-cardinality denial of service;
- module crash, timeout, queue flood, retry storm or corrupted migration;
- operator credential theft, break-glass misuse and rollback to vulnerable artifact.

Verification must combine static analysis, dependency/SBOM/provenance checks, contract tests, authorization tests, fuzzing, fault injection, network-policy tests, secret-scanning, independent penetration testing and incident/restore exercises. A passing unit suite alone is not a security claim.

## 11. Explicit non-goals and open decisions

This document does not select:
- microservices vs modular monolith as a final deployment topology;
- identity provider, authentication framework or token format;
- container/orchestration/service-mesh technology;
- database-per-module vs schema/role isolation;
- signing/KMS/HSM/key custody implementation;
- public registration or multi-tenant SaaS scope;
- any third-party plugin ecosystem or user-installed extensions.

Owner/security/operations review is required before these decisions become accepted. Existing OD-08/09/10/12 remain open where applicable. NEXUS v1 bounded single-owner scope remains unchanged; public user registration, multi-tenancy and commercial deployment are not implicitly authorized by this modular design.

## 12. Acceptance gates

**G0D design acceptance**
- bounded contexts, data owners, trust zones and contract principles reviewed;
- module inventory and capability matrix drafted;
- threat model cross-linked to NX-SEC-001;
- no contradiction with NX-ARCH-001..005 and NX-IF-001..005.

**G1 safe prototype readiness**
- selected module boundary and contract implemented in a non-production test environment;
- contract compatibility, identity binding, authorization, deny-by-default and negative tests pass;
- module cannot access core storage, secrets or egress;
- demo/live isolation test harness demonstrates zero live-egress reachability from demo;
- build pinning, SBOM, provenance, signature verification and rollback evidence exist.

**Before any public account or live capability**
- separate owner/legal/security approval, privacy/data-retention review, incident response and penetration-test evidence;
- production identity, key custody, operations, monitoring, backup/restore and abuse controls approved;
- independent review of all privileged flows and actual deployed network boundaries.
No gate is passed by this proposal alone.

## 13. Current disposition

**PROPOSED / DESIGN ONLY.** No service, package, identity provider, plugin framework, database, deployment topology or runtime module is selected or installed. No public registration, production account, live trading, credentials or real egress is enabled.
