# NX-ARCH-007 — Platform Extensibility, Product Capabilities & Entitlement Model

**Status:** PROPOSED — strategic architecture foundation; not an accepted commercial or implementation baseline  
**Date:** 2026-11-14  
**Related:** NX-ARCH-001..006, NX-SEC-001, NX-IF-001..005, NX-RESEARCH-010, NX-OWNER-DECISIONS-001  
**Purpose:** Make future product expansion, paid tiers, professional capabilities and optional modules possible without coupling commercial packaging to security authority or destabilizing the protected core.

## 1. Strategic principle

NEXUS is to be designed as an extensible platform, not as a fixed list of screens or a single-purpose trading application. New product domains, workflows, integrations and commercial offerings may be added over time through explicit module contracts and independently governed releases.

The architecture must support future optional capabilities without assuming that every proposed capability will be built, that the product will become a public multi-tenant SaaS, or that any regulatory/commercial model is approved. Extensibility is a design goal; scope, launch and monetization remain separately approved decisions.

**Non-negotiable rule:** commercial plan, subscription status, feature flag, module availability or payment-provider response must never grant or bypass identity, authorization, Risk, limits, Ledger, venue eligibility, halt state or trusted-egress controls.

## 2. Three independent decision planes

Keep these concerns distinct and compose them only at explicit policy boundaries:

1. **Product capability plane — what the platform offers.** Module catalog, feature identifiers, contract versions, availability by deployment/environment, supported workflows and product lifecycle.
2. **Commercial entitlement plane — what a plan or purchase includes.** Plan catalog, subscription state, add-ons, trial, expiry, grace period, quotas, usage metering and billing reconciliation.
3. **Security authorization plane — what this principal may do to this resource now.** Authenticated user/workload identity, resource ownership, role/relationship, scope, data classification, risk state, account type, venue eligibility, limits and operational controls.

A successful payment or a claim such as plan=professional is not an authorization token. Entitlements may make a feature available, but the owning service still authorizes each operation. Core-sensitive actions are always evaluated by the core against its own authoritative state.

## 3. Product module portfolio — candidate taxonomy

The following is a planning taxonomy, not a delivery commitment or complete specification.

| Domain | Candidate capabilities | Trust / authority disposition |
|---|---|---|
| Identity & Access | Sign-in, registration when approved, MFA/passkeys, sessions, recovery, profile | Security-critical identity provider; no Risk/Ledger/egress authority |
| Trading Core | Commands, Risk, reservations, execution, Ledger, reconciliation, halt/recovery | Protected authoritative domain; changes require strongest review |
| Demo & Simulation | Virtual accounts, simulated fills, paper workflows, strategy exercises | Separate account namespace, ledger and simulator; no live egress |
| Analytics & Research | Charts, indicators, market analytics, reports, research workspace | Read-scoped data access; never an alternate Risk authority |
| Strategy Lab | Strategy authoring, validation, backtesting, optimization, versioning | Sandboxed compute; untrusted strategy code; no production secrets or direct order route |
| Automation & Operations | User-defined workflows, alerts, conditional actions, scheduling | Declarative, bounded actions through core contracts; no arbitrary privileged scripts |
| Learning & Knowledge | Wiki, courses, tutorials, quizzes, progress | Low privilege; sanitized content; no financial write access |
| Portfolio & Reporting | Positions, statements, performance, export and tax/reporting support | Read models and controlled exports; data privacy/retention requirements |
| Notifications & Collaboration | Alerts, watchlists, shared views, team workflows | Explicit user consent, scopes and tenant isolation if collaboration is approved |
| API & Integrations | Personal API, partner integrations, webhooks, connectors | Separate client identity, scopes, quotas, signing, revocation and abuse controls |
| Billing & Entitlements | Plans, trials, invoices, subscriptions, add-ons, usage metering | Commercial metadata only; cannot mutate financial/trading authority |
| Administration & Support | Support tooling, moderation, audit review, controlled operator actions | Separate operator identity, step-up, approvals, dual control and immutable audit |

Each future domain must have an owner, data classification, public contract, dependency policy, threat model, permission matrix, operational SLO/failure behavior and retirement plan before implementation.

## 4. Entitlement model

### 4.1 Stable feature identifiers

Represent product access with stable, namespaced identifiers, not UI labels or scattered booleans. Examples:

- demo.simulation.basic
- analytics.advanced.indicators
- strategy.backtest.extended
- api.personal.access
- reports.export.extended
- learning.pro.content

Identifiers are illustrative only. They must be registered in a controlled catalog with owner, description, module, contract/API version, data classification, default state, dependencies, deprecation policy and whether the capability consumes a quota.

Do not encode prices, currencies, plan names or marketing copy into domain contracts. Commercial catalog mappings can change without changing module APIs.

### 4.2 Entitlement grants

An entitlement record should be attributable and auditable and should carry at minimum:
- subject/account reference and subject type;
- feature identifier and optional bounded scope;
- source (plan, add-on, trial, administrator grant, promotion);
- status and effective interval;
- quota/limit reference, where applicable;
- issuer, policy/catalog version and reason/reference;
- creation/update/revocation metadata and idempotency key.

Entitlements must be computed or issued by a controlled service, not trusted from client-side storage, query parameters or arbitrary module claims. A signed, short-lived entitlement snapshot may reduce lookup load, but the receiving service must validate issuer, audience, signature, expiry, revocation/version strategy and subject binding. High-risk operations must not depend solely on a cached subscription snapshot.

### 4.3 Plan and subscription lifecycle

Model transitions explicitly: pending, trial, active, grace, past-due/suspended, canceled, expired and refunded/disputed where relevant. Exact states and semantics require commercial/legal review.

- Payment-provider webhooks are untrusted, replayable external input: verify signatures, timestamps and event identity; deduplicate; persist before processing; reconcile against provider state.
- Subscription state changes are idempotent and auditable; out-of-order events cannot silently restore revoked access.
- Grace periods and downgrade behavior are explicit policy, not ad hoc UI logic.
- Downgrade must not silently delete user data, strategy definitions, reports or history. Define read-only/export/retention behavior and notify users before irreversible retention actions.
- Billing outage must not corrupt core state or create unauthorized trading privileges. Define safe entitlement caching and reconciliation behavior.
- Refund, chargeback, fraud and account compromise require separate policies; payment state is not proof of identity.
- No payment provider or payment method is selected by this document.

### 4.4 Quotas and usage

Quotas are distinct from security limits and trading Risk limits.

- Product quotas may bound API calls, report exports, backtest compute, storage, alert count or concurrent jobs.
- Security rate limits protect service availability and abuse surfaces.
- Trading Risk limits protect financial exposure and remain exclusively core-owned.
- A paid plan can increase a product quota only within independently enforced hard safety ceilings.
- Metering events must be attributable, idempotent, tamper-evident and privacy-minimized; avoid collecting payloads that are unnecessary for billing.
- Usage accounting must define aggregation windows, corrections, late events and dispute evidence.

## 5. Feature availability is not authorization

A feature flag controls rollout/visibility, not permission. A plan entitlement controls product eligibility, not identity or authority. A module allowlist controls which artifact may run, not what every user may do.

For every request the owning service must independently check:
- authenticated principal and workload identity;
- resource ownership and tenant boundary (if multi-tenancy is later approved);
- action-specific authorization and current revocation state;
- required entitlement, if the feature is paid/limited;
- service/domain invariants and data classification;
- quotas, abuse limits and operational state;
- core Risk/eligibility/halt checks for any core-sensitive command.

The order of checks must avoid leaking whether a protected resource or premium feature exists to unauthorized callers. Failure defaults to denial for privileged operations. UI hiding is never a security control.

## 6. Plans and product packaging

Future packaging may include a free/basic tier, advanced/professional tier, team/organization tier, API/developer add-ons, research/analytics packages, education bundles and usage-based compute. These are examples, not approved names, prices, promises or commercial commitments.

Design requirements:
- plans are data-driven catalog entries; do not fork the application or core for each tier;
- modules expose capability descriptors; plans map to feature identifiers and quotas;
- add-ons compose with plans through explicit conflict/precedence rules;
- trials and promotions have explicit start/end and abuse controls;
- plan changes do not change a module's security role or grant core privileges;
- user-visible plan descriptions and actual entitlement policy must derive from the same versioned catalog;
- keep price, tax, currency, billing cadence, refunds and consumer disclosures outside domain-core logic;
- preserve a migration path if commercial packaging changes or subscriptions are discontinued.

## 7. Extension and compatibility architecture

Every module publishes a versioned contract and capability descriptor. Platform composition uses an explicit registry, not runtime discovery of arbitrary code.

- Contract versioning follows additive evolution where possible; breaking changes require a new major contract, migration plan, compatibility window and rollback path.
- A module declares minimum/maximum supported platform API versions and required dependencies.
- The platform checks dependency graph for cycles, incompatible versions, revoked modules and unsupported combinations before activation.
- Optional module absence must not prevent core safety controls, recovery, account export or emergency halt.
- A module can be independently disabled and rolled back; schema migration must not make rollback impossible without a documented forward-fix.
- Events are versioned, replay-tolerant and non-authoritative unless explicitly designated; consumers handle duplicates, delays and reordering.
- No module may dynamically install another module, change its own grants or bypass the reviewed registry.
- Do not create a public plugin marketplace or third-party executable extension system without a separate high-risk architecture and threat review.

## 8. Multi-tenancy and organization readiness without premature implementation

The architecture should avoid hard-coding a single global user namespace into every future contract, but NEXUS v1 remains bounded to its currently approved scope. Do not introduce tenant isolation complexity or public multi-user registration merely to appear future-proof.

Before teams, organizations, managed accounts or public SaaS:
- define tenant/account hierarchy and ownership semantics;
- prove tenant isolation at database, cache, queue, object storage, search, analytics, logs and export boundaries;
- model invitations, roles, delegated administration, offboarding and ownership transfer;
- define data residency, retention, deletion, legal basis and breach notification;
- prevent cross-tenant identifiers and confused-deputy access;
- conduct independent security/privacy/legal review and penetration tests.

A future schema may include explicit ownership/tenant context only where it is supported by current domain requirements and tested invariants; do not scatter speculative tenant IDs through all models without a coherent design.

## 9. Security, privacy and abuse controls for a growing platform

Expansion increases attack surface. Every added module, plan and integration creates new routes, data flows, dependencies and abuse opportunities. Require:
- threat modeling and data-flow diagrams before implementation;
- data minimization, classification, retention/deletion and export controls;
- secure defaults, least privilege and deny-by-default contracts;
- rate limits, resource budgets, queue backpressure and cost/abuse controls;
- dependency pinning, SBOM, provenance, artifact signatures and vulnerability response;
- secret isolation, rotation and no secrets in client applications or telemetry;
- audit trails for privileged changes, entitlement grants, operator access and billing reconciliation;
- privacy-safe telemetry, bounded cardinality and redaction;
- backup/restore, incident response, revocation and rollback tests;
- independent security review for high-risk modules and external integrations.

## 10. Performance and reliability principles

Extensibility must not make the critical trading path depend on non-critical product services.

- No synchronous call to Billing, Learning, Analytics, Notifications or a payment provider from the order dispatch path.
- Cache only data with explicit freshness/revocation semantics; core Risk and egress use authoritative safety state.
- Optional modules use bounded queues, timeouts, concurrency and payload sizes.
- Backpressure and load shedding protect the core; non-critical features degrade first.
- Separate read models and analytical workloads from transactional write paths.
- Avoid unbounded fan-out, unbounded event retention and N+1 inter-module calls.
- Measure latency, availability, error budgets and resource use before splitting services.
- Do not add distributed systems without a demonstrated isolation, scale or ownership need.

## 11. Acceptance gates

**G0D — Product platform design**
- module portfolio and bounded contexts reviewed;
- feature catalog schema and ownership rules defined;
- entitlement/security authorization separation reviewed;
- compatibility, quota and lifecycle policies drafted;
- no contradiction with NX-ARCH-001..006 and NX-SEC-001.

**G1 — Safe non-production prototype**
- one representative optional module consumes a versioned contract;
- entitlement checks are independently enforced by the owning service;
- forged plan/feature claims, stale snapshots, replayed billing events, downgrade and revocation cases are tested;
- module failure/load cannot block Risk, halt, recovery or trusted egress;
- no cross-domain data writes or secret access;
- evidence includes contract, authorization, load, fault-injection and rollback tests.

**Before commercial/public launch**
- explicit owner and legal approval of product, pricing, terms, consumer disclosures, payment flow and refund/chargeback handling;
- privacy and data-retention review;
- production billing and entitlement reconciliation controls;
- independent penetration test and incident response readiness;
- support, abuse, availability and financial operations staffed and rehearsed.

Publication of this proposal passes none of these gates.

## 12. Current disposition

**PROPOSED / STRATEGIC DESIGN ONLY.** This document creates no subscription, plan, price, payment integration, user account, tenant, module runtime, feature flag, entitlement service or commercial promise. No third-party provider or deployment topology is selected. NEXUS v1 scope and all existing safety/owner gates remain in force.
