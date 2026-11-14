# NX-ARCH-009 — Capability Catalog & Authorization Contract Model

**Status:** PROPOSED — canonical design contract only; no executable schema, policy engine, authorization service or module grants are approved  
**Date:** 2026-11-14  
**Related:** NX-ARCH-001, NX-ARCH-006, NX-ARCH-007, NX-ARCH-008, NX-ARCH-REVIEW-002, NX-SEC-001, NX-OWNER-DECISIONS-001  
**Purpose:** Turn the broad module permission matrix into a platform-owned, versioned capability catalog whose entries can be mapped to a contract owner, data scope, enforcement point, audit record and negative test without granting modules ambient or self-declared authority.

## 1. Executive decisions proposed

1. Capability IDs are stable, namespaced platform identifiers; display labels never participate in authorization.
2. Every capability has exactly one accountable owning domain and one authoritative enforcement owner. Multiple services may implement replicas/projections, but cannot independently redefine the capability's semantics.
3. Capability definition, module declaration, workload grant, user entitlement and request authorization are distinct records and decision stages.
4. A module grant is always bound to an exact workload identity, immutable artifact digest, environment, capability version, action, resource scope, purpose, validity interval and revocation generation.
5. No wildcard resource scope, implicit inheritance, ambient credential or privilege inferred from a module class, trust tier, subscription or successful artifact signature.
6. Optional modules receive no capability that directly mutates Risk state, reservations, command/outbox, Ledger, halt/recovery authority, venue credentials or Trusted Egress.
7. A user-facing API or workflow may submit a request to a protected domain's public contract, but that does not create a module capability to bypass the protected domain's own user authorization, Risk checks, durable reservation and command acceptance.
8. Unknown, deprecated, unsupported, ambiguous or unrecognized capability versions fail closed.

These are proposed architecture baselines within the owner's bounded delegation. They do not close OD-08/09/10/12, select a technology or authorize runtime implementation.

## 2. Terminology and decision order

| Object | Owner | Meaning | Does not mean |
|---|---|---|---|
| Capability definition | Platform/domain owner | A versioned description of one operation and its enforcement semantics | A grant to any caller |
| Module declaration | Module release owner | Requested capability, purpose and proposed resource scope | Permission |
| Workload grant | Independent policy authority | A bounded authorization for one admitted workload | User authorization or domain approval |
| Product entitlement | Commercial control plane | Product eligibility, plan allowance or quota | Workload identity, security role or trading authority |
| User authorization | Identity/resource owner | User's permission over an action/resource | Permission for arbitrary module workload |
| Request authorization | Resource-owning service | Current allow/deny decision for this exact request | A reusable bearer permission |
| Domain invariant | Protected owning service | Mandatory state/risk/safety constraints | Something that can be waived by a module or plan |

Required request decision order:

1. Strictly parse and validate request and contract version.
2. Authenticate caller and workload identity independently.
3. Verify module admission, exact artifact binding, environment and current revocation state.
4. Resolve the capability definition and check grant binding, action, scope, purpose and validity.
5. Bind the end-user principal and resource ownership from authenticated context; ignore caller-supplied identity claims unless independently verified.
6. Evaluate user authorization and product entitlement/quota only where relevant.
7. Evaluate domain-specific invariants, freshness, halt/recovery state and current authoritative records.
8. Commit the operation using the owning domain's transaction and idempotency contract.
9. Emit a redacted, append-only audit outcome with a stable reason code.

Any failed or indeterminate mandatory check denies the operation. The order is a logical dependency sequence; implementations may combine steps only if they preserve equivalent evidence and fail-closed behavior.

## 3. Capability definition record — required fields

A future versioned schema must represent at least:

| Field | Requirement |
|---|---|
| `capability_id` | Stable namespaced identifier, e.g. `nexus.analytics.query` |
| `definition_version` | Immutable semantic version of authorization semantics |
| `lifecycle` | `DRAFT`, `ACTIVE`, `DEPRECATED`, `RETIRED`; controlled by capability owner |
| `owner_domain` | Exactly one accountable owning domain |
| `description` | Human-readable intent; not policy |
| `actions` | Finite enumerated operations; no arbitrary caller-provided action strings |
| `resource_types` | Explicit resource types and scope grammar |
| `data_classifications` | Maximum input/output classifications |
| `purpose_constraints` | Allowed purpose values and purpose-binding rules |
| `contract_refs` | Exact contract IDs and compatible versions |
| `enforcement_owner` | Service/domain that makes the authoritative request decision |
| `enforcement_points` | Named API/service boundary and any required storage/network enforcement |
| `principal_requirements` | User, workload or dual-principal requirements |
| `entitlement_dependency` | None or exact product eligibility/quota dependency; never security authority |
| `idempotency` | Required key scope, deduplication window and replay semantics |
| `rate_resource_limits` | Bounded request/payload/concurrency/compute constraints |
| `audit_events` | Stable event types, mandatory fields and redaction policy |
| `deny_reason_codes` | Non-sensitive, finite reason taxonomy |
| `compatibility` | Deprecation window and breaking-change rules |
| `negative_tests` | Test IDs that must prove denial at the enforcement boundary |
| `approval` | Owner, security review, policy version, timestamp and evidence references |

No schema may accept arbitrary executable policy expressions, user-supplied SQL, unbounded JSON paths, wildcards, runtime code or free-form network destinations as an authorization rule. New policy primitives require a separately reviewed schema/engine change.

## 4. Scope grammar and data classification

### 4.1 Resource scope

Scopes must be typed and canonical. A scope is not a free-form string and cannot contain a wildcard unless a separate owner-approved capability definition explicitly constrains a bounded set. The initial default supports:

- `SELF`: authenticated principal's own resource, derived by the owning service, not trusted from request body.
- `EXPLICIT_RESOURCE_SET`: finite resource identifiers validated against authoritative ownership and environment.
- `EXPLICIT_NAMESPACE`: one server-assigned namespace, e.g. demo or module-owned projection namespace.
- `READ_MODEL_FILTER`: an owner-defined, bounded query shape over an approved projection; no raw SQL or arbitrary filter expression.
- `CASE_BOUND`: one support case and the minimum linked resources needed for that case, time-limited and audited.
- `NO_RESOURCE`: operation does not address a user resource; only for narrowly defined control-plane operations.

The following are forbidden defaults: `*`, `ALL_USERS`, `ALL_ACCOUNTS`, cross-tenant scans, arbitrary account IDs from an untrusted body, unrestricted database/schema access and unbounded pagination.

### 4.2 Data classification

| Class | Examples | Optional-module default |
|---|---|---|
| `PUBLIC` | Public market data and public reference material | Read only through approved contract |
| `INTERNAL` | Platform health, non-sensitive operational metadata | Minimum necessary read |
| `PERSONAL` | Profile, preferences, learning progress | Self/consent-scoped only |
| `FINANCIAL_RESTRICTED` | Balances, positions, order/fill history, ledger and risk projections | Deny by default; only separately approved read models, never raw authority |
| `SECRET` | API keys, signing keys, payment credentials, identity-provider secrets | No optional module access |
| `UNTRUSTED_INPUT` | User code, documents, webhooks, imported files, third-party payloads | Treat as hostile; parse/sandbox, never confer authority |

Data owners must classify fields, not merely tables or whole APIs. Derived reports inherit the most restrictive source classification unless a documented minimization/declassification process is approved by the source owner.

## 5. Initial capability catalog — proposed, not granted

The table is a bounded starting catalog for first-party product domains. IDs are illustrative stable names to reserve only after owner approval. They are not implemented endpoints or active permissions.

| Capability ID | Owner / enforcement authority | Action and scope | Data class | Module consumers considered | Explicit denial |
|---|---|---|---|---|---|
| `nexus.market-data.read` | Market Data | Read approved instruments/venues and bounded time range | PUBLIC / INTERNAL | Analytics, Strategy Lab, Demo, Portfolio | No private account or venue credential access |
| `nexus.profile.self.read` | Identity & Access | Read authenticated principal's own minimal profile | PERSONAL | Optional modules where essential | No arbitrary subject lookup |
| `nexus.demo.simulation.run` | Demo & Simulation | Run bounded simulation in server-assigned demo namespace | UNTRUSTED_INPUT / INTERNAL | Demo UI, Strategy Lab | No live account routing or venue egress |
| `nexus.strategy.artifact.read` | Strategy Lab | Read authorized strategy metadata/artifact | PERSONAL / UNTRUSTED_INPUT | Strategy Lab, Analytics | No execution privilege |
| `nexus.strategy.artifact.write` | Strategy Lab | Write own/authorized strategy artifact namespace | PERSONAL / UNTRUSTED_INPUT | Strategy Lab | No writes to core state |
| `nexus.analytics.query` | Analytics & Research | Bounded query over approved projections | INTERNAL / PERSONAL / FINANCIAL_RESTRICTED projection | Analytics, Portfolio | No raw Ledger/Risk DB or arbitrary SQL |
| `nexus.portfolio.report.generate` | Portfolio & Reporting | Generate a report from approved read models | FINANCIAL_RESTRICTED projection | Portfolio, Notifications (summary only) | No financial posting or order mutation |
| `nexus.learning.progress.read` | Learning & Knowledge | Read own learning progress | PERSONAL | Learning | No trading profile/financial access |
| `nexus.learning.progress.write` | Learning & Knowledge | Update own progress within learning domain | PERSONAL | Learning | No entitlements or account permissions |
| `nexus.notification.publish` | Notifications & Collaboration | Publish an approved template/event to consented destinations | PERSONAL / INTERNAL | Notifications, bounded workflows | No secret-bearing arbitrary payloads |
| `nexus.billing.usage.read` | Billing & Entitlements | Read minimum subject-scoped usage aggregate | PERSONAL / INTERNAL | Billing UI, Administration case scope | No payment credentials or financial account data |
| `nexus.billing.subscription.manage` | Billing & Entitlements | Submit subscription lifecycle request through billing owner | PERSONAL | Billing UI/API only | No trading authority or entitlement self-issuance |

### 5.1 Protected capabilities are not module-grantable

The following are deliberately absent from the optional-module catalog and must remain protected service contracts:

- Risk evaluation, limit mutation, reservation create/consume/release and halt control.
- Command acceptance, outbox mutation, dispatcher claim and trusted egress transmission.
- Ledger posting, journal correction, reconciliation override and accounting policy mutation.
- Venue credential retrieval, signing authority, direct venue sockets and production key management.
- Operator break-glass, dual-control override and production deployment authority.

A client or approved API integration may submit a user-originated command to the NEXUS public command contract, but the command coordinator and Risk domain must independently validate user identity, account scope, current state, risk approval, idempotency, durable reservation and all existing execution gates. Such a request path is not a reusable module capability and never permits bypass.

## 6. Mapping matrix — module, capability, owner and negative test

| Consumer | Proposed capability | Owning enforcement service | Scope rule | Minimum negative test |
|---|---|---|---|---|
| Analytics & Research | market-data.read | Market Data | approved instrument set + time bound | deny unapproved instrument and private endpoint |
| Analytics & Research | analytics.query | Analytics | approved projection + bounded filter | deny raw SQL, raw Ledger table and other subject |
| Strategy Lab | strategy.artifact.read/write | Strategy Lab | owner/ACL-bound namespace | deny cross-subject artifact and path traversal |
| Strategy Lab | market-data.read | Market Data | approved instruments/time window | deny private feed and unapproved symbol |
| Demo & Simulation | demo.simulation.run | Demo | server-assigned demo namespace | deny live account ID, live outbox and venue egress |
| Demo & Simulation | market-data.read | Market Data | public/replay feed only | deny private credential or order channel |
| Portfolio & Reporting | portfolio.report.generate | Portfolio | user-owned account/read-model projection | deny other account and raw ledger mutation |
| Learning & Knowledge | learning.progress.read/write | Learning | authenticated user's own progress | deny arbitrary user and financial profile |
| Notifications & Collaboration | notification.publish | Notifications | consented destination + approved template | deny arbitrary URL, secret payload and consent bypass |
| Billing & Entitlements | billing.usage.read | Billing | subject-scoped aggregate | deny other subject and payment secret |
| Billing UI/API | billing.subscription.manage | Billing | authenticated billing subject | deny plan claim from client and self-issued entitlement |
| Administration & Support | case-scoped reads | Owning source service | active case + minimum fields + time limit | deny access without case, expired case or unrelated subject |

This mapping is intentionally incomplete where a canonical service/API does not yet exist. No route name, endpoint, table or permission is asserted to exist until the owning interface contract defines it.

## 7. Authorization contract and decision result

Every enforcement boundary should produce a structured internal decision with:

- `decision_id`: unique, non-secret correlation identifier;
- `outcome`: `ALLOW` or `DENY`; no third "soft allow";
- `principal_binding`: authenticated user and workload references, where required;
- `capability_ref`: exact ID and definition version;
- `resource_binding`: canonical type/ID/namespace after ownership resolution;
- `policy_version` and `grant_generation`;
- `reason_code`: finite, non-sensitive code;
- `evaluated_at` and bounded freshness metadata;
- `audit_ref`: durable audit correlation.

An ALLOW is request-scoped and must not become an indefinitely reusable bearer token. If an implementation uses a signed short-lived authorization envelope, it must bind the exact operation, canonical payload digest, resource, principal, grant/policy generation, audience, expiry and nonce/idempotency context; protected financial commands continue to use their separately specified RiskApprovalCapability and command-consumption contracts.

Decision reasons should distinguish at least: unauthenticated, workload-not-admitted, artifact-mismatch, grant-missing, grant-expired, grant-revoked, capability-unknown, version-unsupported, scope-mismatch, subject-mismatch, entitlement-ineligible, quota-exceeded, resource-not-found-or-not-visible, stale-state, policy-denied and internal-control-plane-unavailable. External responses must not reveal whether a protected resource exists.

## 8. Revocation, cache and control-plane outage

No numeric revocation objective is invented in this design. Before G1, the owner/security review must set a measurable maximum revocation propagation objective for each class of action and define:
- authoritative revocation generation and monotonicity;
- cache maximum age and invalidation/refresh behavior;
- control-plane outage behavior for read-only versus state-changing actions;
- cancellation of queued and in-flight work;
- independent termination, secret revocation and network isolation;
- acknowledgement proving all enforcement points observed revocation;
- behavior when acknowledgement is missing or stale.

Mandatory policy:
- A stale grant or unknown revocation generation is not valid.
- No control-plane outage may cause a privileged action to fail open.
- An application cache invalidation message is not proof that a process lost credentials or network access.
- High-risk and financial operations must use authoritative current domain state and their own transaction/fencing model.
- If revocation cannot be positively confirmed at the required boundary, affected capability remains disabled and incident state is retained.

## 9. Audit, privacy and telemetry

Every grant issuance/change/revocation and every privileged allow/deny outcome must be auditable. Audit records must include actor/workload, capability version, scope reference, policy/grant generation, reason code, timestamp/clock quality, correlation ID and result. They must not include secret values, raw credentials, full payment data, raw private order payloads or unnecessary personal data.

Audit integrity, retention, access, export, deletion and legal basis remain policy decisions. A hash chain or append-only table alone does not prove tamper resistance if the same principal can rewrite both data and verification material. Independent audit custody and recovery are required before production claims.

## 10. Adversarial qualification plan

| ID | Attack | Required proof |
|---|---|---|
| CAP-01 | Caller invents an unknown capability ID or future version | Denied at owning boundary; no fallback |
| CAP-02 | Module changes manifest declaration after approval | Exact digest mismatch; no grant reuse |
| CAP-03 | Workload replays a grant from another environment | Audience/environment binding rejects |
| CAP-04 | Workload uses a grant for another artifact version | Artifact binding rejects |
| CAP-05 | Caller changes subject/account/resource ID | Owning service rebinds identity and denies cross-scope |
| CAP-06 | Wildcard, empty or malformed scope is supplied | Strict parser rejects; no broad default |
| CAP-07 | Entitlement or plan claim is forged/stale/revoked | No security authority; entitlement issuer/current state checked |
| CAP-08 | Module invokes capability after expiry/revocation | Denied at enforcement boundary; stale cache test |
| CAP-09 | Billing/control plane unavailable | Trading core remains independent; billing-gated action fails closed |
| CAP-10 | Analytics submits raw SQL or accesses raw Ledger/Risk store | Contract/query boundary rejects; DB role/network evidence |
| CAP-11 | Demo module substitutes live account ID | Core mode check rejects; no live side effect |
| CAP-12 | Notification module injects arbitrary destination or secret payload | Destination/template/data policy rejects |
| CAP-13 | Support user accesses data without active case | Source owner denies; audit evidence |
| CAP-14 | Capability owner attempts unilateral grant to own privileged workload | Separation/approval policy rejects |
| CAP-15 | Duplicate/reordered request or event causes repeated effect | Idempotency and owner transaction prevent duplicate effect |
| CAP-16 | Authorization service returns timeout/indeterminate result | No soft allow; operation fails closed |
| CAP-17 | Old policy snapshot is replayed after policy version change | Version/generation check rejects |
| CAP-18 | Audit fields leak secret or high-cardinality personal data | Redaction and cardinality tests pass |

Tests must observe authoritative persisted state and the actual API, DB, process, secret or network boundary. Mock-only policy tests are necessary but insufficient.

## 11. G0D/G1 exit criteria and open decisions

### G0D design exit
- capability naming/versioning and lifecycle agreed;
- each catalog entry has exactly one owner and enforcement authority;
- resource scope grammar and data classification approved;
- every allowed module-to-capability edge maps to a contract, audit event and deny test;
- protected capabilities remain outside optional module grants;
- cross-review with NX-ARCH-006/007/008, NX-SEC-001 and interface contracts complete;
- unresolved OD items remain explicit.

### G1 non-production prototype exit
- canonical schema and strict validator implemented only after G0D approval;
- one low-risk first-party read-model module selected;
- exact workload identity/artifact/grant binding verified;
- owner service performs request-time authorization;
- actual DB, secret, process and network boundaries prove deny cases;
- revocation objective measured and stale-cache/outage behavior tested;
- CAP-01..18 applicable tests pass;
- no real credentials, real account, live orders, payment data or production deployment.

### Open decisions
- OD-08 signing/canonicalization and key custody;
- OD-09 durable registry/audit storage and transaction semantics;
- OD-10 clock/freshness/recovery objectives;
- OD-12 operator/support step-up and dual control;
- exact registry/policy/workload-identity topology;
- numeric revocation and cache objectives;
- field-level data classification and retention/legal basis.

## 12. Disposition

**PROPOSED / DESIGN ONLY.** This document provides a canonical design contract and a proposed initial catalog. It does not define an executable JSON Schema, API route, database schema, authorization engine or active permission. It selects no vendor, dependency, cryptographic algorithm or deployment technology. No grant is issued, no module is activated and no protected core authority is delegated.

NX-ARCH-009 does not close G0D/G1 or any owner decision. It is a companion to NX-ARCH-008; its catalog entries remain proposals until domain owners and security review accept them.
