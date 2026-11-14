# NX-ARCH-008 — Module Registry, Admission & Capability Governance

**Status:** PROPOSED — architecture and control-plane design only; no executable registry, module runtime, plugin loader or permission-grant service is approved  
**Date:** 2026-11-14  
**Related:** NX-ARCH-006, NX-ARCH-007, NX-SEC-001, NX-IF-001..005, NX-OWNER-DECISIONS-001, NX-RESEARCH-010  
**Purpose:** Define a controlled, auditable and fail-closed way to describe, qualify, admit, activate, isolate, revoke and retire first-party or future third-party modules without granting modules self-authorized access or weakening protected core boundaries.

## 1. Decision summary

NEXUS needs a **registry-governed modular platform**, not an unrestricted plugin host.

The registry is the authoritative catalog of module identity, reviewed artifact provenance, contract compatibility, declared dependencies, data classifications, requested capabilities, resource budgets, operational constraints and lifecycle state. It is not itself a permission grant and does not make a module trusted merely because an entry exists.

Three independent controls must all succeed before a module can perform an operation:

1. **Admission:** this exact artifact and version are approved for this environment and lifecycle state.
2. **Workload authorization:** this running workload has an independently issued identity and narrowly scoped grants for the requested operation and resource.
3. **Domain authorization:** the owning service independently validates the user/principal, resource ownership, entitlement (if applicable), domain invariants and current safety state.

A module manifest is a declaration, not an authorization. A signature is provenance evidence, not proof of benign behavior. A subscription or feature entitlement is product eligibility, not a security credential.

**Protected core is not an ordinary module.** Risk, command acceptance, durable reservations, Ledger authority, halt/recovery controls and Trusted Egress remain protected domains with separately governed deployment and change controls. No optional module may load code into these domains or acquire their authority through registry metadata.

## 2. Scope and non-goals

In scope:
- canonical module identity and immutable version/artifact references;
- registry record and manifest requirements;
- module classes and trust-boundary classification;
- lifecycle and admission transitions;
- separation of declared capabilities, approved grants, entitlements and per-request authorization;
- data-access and permission matrix;
- contract/dependency compatibility;
- workload identity, resource budgets, network policy declarations and secret references;
- audit, revocation, rollback and retirement;
- adversarial qualification scenarios and G0D/G1 exit criteria.

Not in scope:
- an executable JSON Schema, database schema, API, scheduler, module loader or plugin SDK;
- a decision to use containers, Kubernetes, WASM, a service mesh, a broker or any named vendor;
- public marketplace, arbitrary user-supplied executable code or third-party module publication;
- approval of multi-tenancy, teams, paid subscriptions or commercial launch;
- changing NEXUS v1 scope, venue, account model or trading authority;
- granting any module access to live credentials, venue sockets or production trading actions.

## 3. Identity model and immutable artifact binding

### 3.1 Stable module identity

Every module has a permanent, namespaced identifier, for example `nexus.analytics.research`. The identifier:
- is globally unique within the NEXUS registry namespace;
- is not a display name, package name supplied by an artifact, plan name or user-controlled string;
- is never reassigned to a different product/domain owner;
- survives module version upgrades and display-name changes;
- has an explicit owner accountable for its contract, data handling, security posture and lifecycle.

A fork, independently operated integration or materially different trust boundary receives a distinct identity. Aliases are presentation metadata only.

### 3.2 Immutable release identity

A release is identified by the tuple:
- stable module ID;
- semantic module version;
- platform contract compatibility declaration;
- immutable artifact digest and digest algorithm;
- signing identity/key ID and signature verification result;
- build provenance/attestation reference, where available;
- source revision and reproducible-build status, where applicable;
- SBOM and vulnerability-review references;
- approval record and policy version.

A mutable tag, branch name, registry URL or package version alone is not an artifact identity. Replacing bytes under the same version is forbidden; publish a new immutable release and preserve the prior record.

### 3.3 Ownership and accountability

Each module record identifies:
- accountable domain owner;
- engineering maintainer(s);
- security reviewer and approval authority;
- data owner(s) for consumed and produced data;
- operational owner/on-call responsibility when activated;
- support and incident escalation path;
- lifecycle review date and deprecation/retirement plan.

One person may hold multiple roles in a personal development environment, but production-grade privileged changes must retain explicit separation/dual-control requirements defined by the applicable owner and security policy. A module cannot approve itself.

## 4. Registry record and manifest contract

The registry stores the reviewed desired state. The artifact's embedded manifest is untrusted input until validated and matched to the approved registry record.

### 4.1 Required registry fields

| Field | Requirement |
|---|---|
| `module_id` | Stable namespaced identity |
| `display_name`, `description` | Human-readable metadata; never used for authorization |
| `owner` | Accountable domain/team reference |
| `module_class` | Enumerated class from §5 |
| `trust_boundary` | Explicit trust tier; cannot be self-selected by artifact |
| `release_version` | Immutable semantic version |
| `artifact_digest` | Digest of exact executable/package bytes |
| `signature` | Signing key identity, algorithm, signature and verification evidence |
| `provenance` | Source revision, build identity, SBOM and build attestation references |
| `platform_contracts` | Required/provided contract IDs and supported version ranges |
| `dependencies` | Exact or bounded dependency identities and compatibility constraints |
| `capability_declarations` | Requested operations, resource scopes and purpose; declarations only |
| `data_inventory` | Data classes read/written, purpose, retention and export behavior |
| `secret_references` | Named references to separately provisioned secrets; never secret values |
| `network_policy` | Required destinations, protocols, ports and direction; default deny |
| `resource_budget` | CPU, memory, concurrency, queue, storage, payload and execution-time bounds |
| `lifecycle_state` | Registry-governed state from §6 |
| `approval` | Review identities, evidence links, policy version and decision timestamp |
| `compatibility` | Platform/API/runtime compatibility and migration constraints |
| `operations` | Health contract, SLO/degradation behavior, logs/metrics policy and runbook |
| `retirement` | Disable, data export/retention, schema cleanup and rollback/forward-fix plan |

All fields that affect execution, access, dependency resolution, network egress or data handling must be validated against a versioned registry contract. Unknown critical fields, unsupported versions, duplicate keys, invalid encodings, unbounded values and ambiguous defaults must fail closed.

### 4.2 Manifest declarations versus grants

The module may declare:
- capabilities it needs;
- data it expects to consume or produce;
- external destinations it proposes to contact;
- secret reference names it expects;
- resource ceilings it requires;
- contract versions and dependencies.

The module may not:
- grant itself any declared capability;
- widen its own scopes, resource budgets or destinations;
- choose or elevate its trust tier;
- add or remove its own registry approval;
- approve a dependency or signer;
- access a secret by guessing a name;
- activate, update, revoke or replace another module;
- alter platform authorization policy.

A separate policy/approval process converts an accepted subset of declarations into explicit grants. The actual runtime enforcement point checks those grants on every relevant boundary. Registry approval is necessary but never sufficient for a request.

### 4.3 Illustrative record (not an executable schema)

```yaml
module_id: nexus.analytics.research
release_version: 0.1.0
module_class: OPTIONAL_READ_MODEL
trust_boundary: ISOLATED_OPTIONAL_WORKLOAD
artifact:
  digest: sha256:<immutable-digest>
  signer_key_id: <approved-signing-key-reference>
  provenance_ref: <attestation-reference>
contracts:
  consumes:
    - id: nexus.market-data.read
      version_range: "1.x"
  provides:
    - id: nexus.analytics.query
      version: "1.0"
capability_declarations:
  - operation: market_data.read
    scope: explicitly-approved-instruments
data_inventory:
  reads: [MARKET_DATA]
  writes: [MODULE_OWNED_ANALYTICS]
network_policy:
  egress: [] # default deny; destinations require separate review
secret_references: []
resource_budget:
  cpu: bounded
  memory: bounded
  concurrency: bounded
lifecycle_state: PROPOSED
```

Placeholders above are intentionally non-operational. The example grants no permissions, chooses no deployment technology and is not valid input to a runtime.

## 5. Module classes and trust boundaries

Module class describes product responsibility. Trust tier describes the maximum execution boundary and review burden. Neither is a user role or a permission grant.

### 5.1 Module classes

- `PROTECTED_CORE_DOMAIN`: Risk, command, reservations, execution authority, Ledger, halt and recovery. Governed outside the optional module admission path.
- `PLATFORM_SECURITY_SERVICE`: identity, workload identity, authorization policy and security audit. Privileged; dedicated threat model and independent approval.
- `OPTIONAL_READ_MODEL`: analytics, reporting and research projections; no authoritative financial writes.
- `OPTIONAL_WORKFLOW`: notifications, learning, collaboration and bounded declarative automation.
- `SANDBOXED_COMPUTE`: strategy evaluation, backtests and user-authored logic; untrusted input/code and strict resource/network isolation.
- `COMMERCIAL_CONTROL_PLANE`: billing, plans, entitlement catalog and usage metering; cannot mutate core financial or security authority.
- `EXTERNAL_ADAPTER`: protocol translation or external integration; untrusted boundary, no direct privileged domain writes.

### 5.2 Trust tiers

| Tier | Boundary | Default posture |
|---|---|---|
| T0 — Untrusted content/input | Documents, strategy source, uploaded data, webhooks and user-controlled payloads | Parse/sanitize/validate; never execute with ambient authority |
| T1 — Sandboxed workload | User logic, research jobs and optional compute | Isolated, resource-bounded, no secrets, no direct core/venue network |
| T2 — Isolated optional service | Reviewed first-party optional modules | Workload identity, explicit grants, separate data ownership, default-deny network |
| T3 — Privileged platform service | Identity, policy, security control plane | Dedicated review, hardened deployment, narrowly scoped administrative authority and audit |
| T4 — Protected financial core / Trusted Egress | Risk, command, Ledger, halt/recovery and the sole authorized venue egress boundary | Separate change control and runtime boundary; not assignable by module manifest or commercial entitlement |

T0–T4 are architecture labels, not a claim that a system is invulnerable. Raising a module's tier requires a separate architecture/security decision and cannot be inferred from a successful signature, owner field or plan.

## 6. Lifecycle state machine

Registry lifecycle states:

1. `PROPOSED` — record submitted; no executable admission.
2. `UNDER_REVIEW` — contract, ownership, data, threat model, dependency and license review in progress.
3. `APPROVED` — exact artifact/version approved for a named environment and bounded policy set; not yet active.
4. `STAGED` — artifact verified and deployed in an isolated non-serving state; health and compatibility checks run.
5. `ACTIVE` — explicitly enabled for the approved environment, scopes and rollout cohort.
6. `QUARANTINED` — isolated due to suspicious behavior, failed integrity/health checks, policy violation or incident; new requests denied.
7. `REVOKED` — admission/signing/grants invalidated; activation prohibited; revocation propagated and acknowledged.
8. `RETIRED` — no longer executable; records, audit and required user data retained or disposed under policy.

Rules:
- Only a controlled registry authority can change lifecycle state.
- State transitions are authenticated, authorized, versioned and append-only audited.
- `APPROVED` is bound to exact artifact digest, environment, contract set and policy version.
- Any artifact digest, signer, critical dependency, contract major version or privilege change requires re-review.
- `ACTIVE` never implies a permanent grant; runtime authorization and revocation are checked independently.
- `QUARANTINED` and `REVOKED` deny new work immediately; in-flight behavior follows an explicit bounded cancellation/containment policy.
- Failure to retrieve current admission/revocation state follows a per-operation fail-closed policy; no indefinite stale approval cache.
- A rollback is a new audited transition to a previously reviewed immutable artifact, not a mutable downgrade or erased history.
- Re-activation after quarantine/revocation requires documented root cause, evidence and fresh approval.

## 7. Capability catalog, grants and authorization

### 7.1 Four separate objects

1. **Capability definition:** a platform-owned, versioned operation such as `market_data.read` or `analytics.query`. It defines owner, semantics, allowed resource types, data class and enforcement point.
2. **Module declaration:** a release asks to use a capability for a stated purpose and bounded scope.
3. **Workload grant:** an independent policy authority approves a subset for an exact workload identity, artifact, environment, resource scope and validity interval.
4. **Request authorization:** the owning service checks the actual caller, resource, action, grant, user authorization, entitlement (if applicable), quota and domain state at request time.

No object substitutes for another. A module cannot mint grants; a user entitlement cannot mint workload grants; a workload grant cannot override domain invariants.

### 7.2 Grant binding

A grant should be bound to:
- workload identity and stable module ID;
- exact artifact digest and release version;
- environment and deployment identity;
- capability ID and contract version;
- explicit resource scope and data classification;
- allowed action(s), purpose and optional conditions;
- not-before/expiry and revocation generation;
- issuer, policy version, approval evidence and audit reference.

Wildcard scopes, ambient credentials, unrestricted filesystem/database access and unrestricted egress are prohibited by default. Any exceptional broad scope requires a separately documented risk acceptance and cannot include direct venue egress or bypass of protected core contracts.

### 7.3 Authorization evaluation

The resource-owning service evaluates:
- authenticated end-user or workload principal;
- current workload admission and revocation;
- action-specific grant and resource scope;
- user authorization and ownership;
- product entitlement and quota where relevant;
- data classification and purpose constraints;
- domain-specific invariants and current operational state.

Denial is the default. The caller receives a non-sensitive error that does not disclose protected resource existence or internal policy detail. High-risk operations use authoritative current state, not only a cached entitlement or stale registry snapshot.

## 8. Data ownership and inter-module access matrix

Legend: **R** = bounded read through owned contract; **W** = write only to own domain; **C** = controlled command through owning service; **—** = denied by default. This is an architecture policy proposal, not an implemented ACL.

| Module/domain | Market data | User/profile | Demo data | Strategy artifacts | Analytics/report projections | Billing/entitlements | Risk/reservations | Ledger | Venue credentials/socket |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Identity & Access | — | W | — | — | — | — | — | — | — |
| Trading Core | R | R | — | — | W (owned projections only) | — | W | W | C (Trusted Egress only) |
| Demo & Simulation | R | R | W | R | W (demo namespace) | — | — | W (demo ledger only) | — |
| Analytics & Research | R | R (minimal) | R (authorized demo scope) | R | W (own projections) | — | — | R (approved projections only) | — |
| Strategy Lab | R | R (minimal) | R (sandbox scope) | W | W (own results) | — | — | — | — |
| Automation & Operations | R (bounded) | R (minimal) | R (if authorized) | R (metadata) | R | — | C (approved core command only; no direct mutation) | — | — |
| Learning & Knowledge | — | R (minimal progress) | — | — | — | — | — | — | — |
| Portfolio & Reporting | R (approved) | R | R (demo scope) | — | W (own reports) | — | R (approved projections) | R (read model only) | — |
| Notifications & Collaboration | R (event summaries) | R (consent-scoped) | R (authorized summaries) | — | R (authorized summaries) | — | — | — | — |
| API & Integrations | R (scoped) | R (own principal) | R (explicitly granted) | R (explicitly granted) | R (scoped) | — | C (through public core contract only) | R (approved projections) | — |
| Billing & Entitlements | — | R (billing subject minimum) | — | — | R (usage aggregates) | W | — | — | — |
| Administration & Support | — | R (case-scoped) | — | — | R (case-scoped) | R (case-scoped) | — | — | — |

Additional invariants:
- `W` never means direct writes into another domain's database/schema. Cross-domain state changes use the owning service's authenticated contract.
- No optional module gets raw Risk state mutation, reservation creation/release, Ledger posting, halt override or direct command/outbox write.
- Any `C` path is a request to the owning domain; the owning domain re-evaluates user and domain policy and may deny it.
- Demo accounts, identifiers, event streams, storage and ledger are isolated from live trading by an independently enforced account-mode boundary. Identifier tampering must not cross that boundary.
- Support access is case-scoped, time-limited, audited and read-only by default; privileged operator actions require separate step-up and dual-control policy.
- The matrix is a deny-by-default starting point. It does not authorize an operation merely because a cell is marked R/W/C.

## 9. Inter-module contract and dependency governance

Each contract has:
- stable contract ID and semantic version;
- owning domain and authoritative data owner;
- request/response or event schema with strict parsing limits;
- authentication and workload identity requirements;
- authorization and resource-scope semantics;
- idempotency and replay behavior;
- timeout, retry, backpressure and cancellation behavior;
- error taxonomy and compatibility guarantees;
- data classification, retention and privacy requirements;
- observability/redaction requirements;
- conformance fixtures and consumer/provider compatibility tests.

Dependency policy:
- dependencies are declared, version-pinned or bounded by a reviewed range, and resolved before activation;
- cycles are rejected unless a specific reviewed contract proves safe composition (default: no cycles);
- dependency closure must not elevate trust tier or inherit permissions;
- optional dependency absence degrades the dependent module, not the protected core;
- transitive dependency changes trigger SBOM and vulnerability re-evaluation;
- no module may download or execute arbitrary code at runtime;
- no automatic update can change artifact bytes or grants without admission review;
- breaking contract changes require a new major version, compatibility window, migration evidence and rollback/forward-fix plan.

Synchronous calls from optional modules into Billing, Learning, Analytics or Notifications must never be introduced into the protected order dispatch path. Event delivery is at-least-once unless a contract explicitly proves otherwise; consumers must be idempotent and tolerate duplicates, delay and reordering.

## 10. Runtime isolation and resource governance

The exact deployment technology remains open. Regardless of technology, the enforcement design must provide:
- distinct workload identity per module release/environment, not shared ambient service credentials;
- separate process/security boundary for untrusted or optional executable code;
- least-privilege filesystem, OS, database and secret access;
- default-deny network ingress/egress with reviewed destination allowlists;
- no route from optional workloads to venue endpoints and no venue credentials mounted into them;
- explicit CPU, memory, file, process, thread, concurrency, queue, payload, storage and execution-time limits;
- bounded retries, circuit breaking, load shedding and backpressure;
- independent health, disable and rollback controls;
- tamper-evident audit of admission, grant, activation, revocation and privileged access;
- telemetry redaction, bounded cardinality and no secrets or raw sensitive payloads in logs.

A container, namespace, WASM sandbox, service mesh or network policy is only one control layer. The security case must test actual enforcement at the host, process, identity, storage and egress boundaries; a configuration declaration is not proof.

## 11. Secret and external-network policy

- Secrets are provisioned outside module manifests and referenced by opaque identifiers.
- Secret values are never included in registry records, build artifacts, client bundles, logs, telemetry or module metadata.
- Optional modules receive no venue credentials, signing keys, payment-provider secrets or broad identity-provider secrets by default.
- A module-specific secret, if ever approved, is scoped to one workload, purpose, audience and rotation/revocation lifecycle.
- External destinations are enumerated by hostname/service identity, protocol, port and purpose; wildcard egress is denied.
- DNS rebinding, redirects, proxy bypass, alternate IPs, IPv6, metadata endpoints and compromised dependencies are included in egress tests.
- Trusted Egress remains the only path authorized to transmit canonical live venue commands. No module tier, capability declaration, API entitlement or operator convenience can create an alternate route.

## 12. Revocation, incident containment and rollback

Revocation triggers include artifact/signature mismatch, compromised signer, vulnerability severity threshold, unexpected network behavior, data exfiltration suspicion, authorization violation, owner request, contract incompatibility or lifecycle expiry.

Minimum response:
1. record an incident and freeze further admission/rollout;
2. deny new workload grants and invalidate current revocation generation;
3. isolate workload network and secret access through independent enforcement points;
4. terminate or quarantine the workload and verify containment;
5. preserve forensic/audit evidence without exposing secrets;
6. assess data access, downstream effects and dependent modules;
7. rotate/revoke affected credentials and signer material where needed;
8. restore service only from an independently verified immutable artifact and reviewed policy;
9. document root cause, blast radius, customer/user impact and corrective tests.

A registry flag alone is not containment if a compromised process retains credentials or network access. Revocation must be enforced outside the workload and verified. For protected egress authority, the stronger external fencing and reconciliation rules in NX-REF-EXEC-002 remain mandatory.

## 13. Adversarial qualification matrix

Before G1, tests must demonstrate denial and containment for at least:

| ID | Adversarial scenario | Required result / evidence |
|---|---|---|
| MOD-01 | Forged module ID, owner or trust tier in artifact manifest | Registry identity wins; mismatch rejected and audited |
| MOD-02 | Artifact bytes changed under an approved version | Digest/signature mismatch; activation denied |
| MOD-03 | Revoked/expired signing key or compromised signer | Admission denied; affected releases quarantined/revoked |
| MOD-04 | Module requests undeclared or ungranted capability | Owning service denies; no ambient fallback |
| MOD-05 | Stale, expired or revoked workload grant | Request denied at enforcement boundary |
| MOD-06 | Module forges a Professional plan or entitlement snapshot | No security authority gained; issuer/audience/signature/subject/version checked |
| MOD-07 | Optional module attempts direct DB write to another domain | Network/role boundary denies; audit evidence |
| MOD-08 | Optional module attempts direct venue connection or credential discovery | Egress and secret boundaries deny; instrumented network evidence |
| MOD-09 | Demo identifier/account-mode tampering routes to live | Core account-mode check denies; no live outbox/egress side effect |
| MOD-10 | Cross-module or cross-subject identifier substitution | Owning service enforces ownership/scope; no data disclosure |
| MOD-11 | Replayed, duplicated, delayed or reordered events | Idempotent processing; no duplicate privileged effect |
| MOD-12 | Malicious dependency update or dependency confusion | Pinned provenance/allowlist rejects; SBOM and review required |
| MOD-13 | SSRF, DNS rebinding, redirect or metadata-service access | Default-deny egress blocks; packet/flow evidence retained |
| MOD-14 | Resource exhaustion or queue flood by optional module | Bounded resources and load shedding; Risk/halt/recovery remain responsive |
| MOD-15 | Registry/control-plane outage or stale cache | No new privileged activation; per-operation fail-closed behavior |
| MOD-16 | Quarantine/revocation while work is in flight | Defined cancellation/containment behavior; no post-revocation new side effect |
| MOD-17 | Rollback to vulnerable or incompatible artifact | Rejected unless exact artifact is re-approved under current policy |
| MOD-18 | Support/admin role abuse or approval self-review | Step-up, scoped approval, separation/dual control and immutable audit enforced |
| MOD-19 | Optional module outage or slow dependency | Core command, Risk, halt, recovery and trusted egress unaffected |
| MOD-20 | Sensitive values leak through logs, metrics, traces or error messages | Redaction and bounded-cardinality tests pass; no secret/raw sensitive payload leakage |

Evidence must inspect both authoritative persisted state and the actual enforcement boundary (process identity, database role, filesystem, network/egress, secret broker or instrumented socket). A mocked policy decision without boundary observation is insufficient.

## 14. Acceptance gates

### G0D — Module governance design
- NX-ARCH-006/007/008 cross-reviewed for consistent trust, capability, entitlement and authorization semantics;
- module record, release identity, lifecycle and approval authority agreed;
- capability catalog ownership and grant issuance boundaries defined;
- domain data ownership and permission matrix reviewed;
- contract compatibility, dependency and revocation policies reviewed;
- no contradiction with NX-SEC-001, NX-IF-001..005 or owner decisions;
- unresolved decisions explicitly registered; no executable runtime implied.

### G1 — Non-production controlled module prototype
- exactly one low-risk first-party optional read-model module selected;
- signed immutable artifact and registry admission verified end-to-end;
- separate workload identity and independently issued least-privilege grant;
- owning service enforces user authorization and resource scope;
- module cannot read secrets or reach venue/privileged core endpoints;
- direct cross-domain database writes are denied;
- module failure, overload, quarantine and revocation do not affect core safety operations;
- MOD-01..20 applicable tests pass with observed boundary evidence;
- rollback, audit and incident containment rehearsed;
- no real accounts, credentials, orders, payments or production data used.

G1 does not authorize a public plugin marketplace, arbitrary third-party executable code, live trading or commercial launch.

### Before external/third-party modules
- independent security architecture and threat review;
- signed publisher identity, key lifecycle, artifact transparency/provenance and SBOM policy;
- legal/license review and vulnerability response SLA;
- sandbox escape and host/network boundary penetration testing;
- privacy, data-processing, user-consent and support model;
- revocation/incident response and publisher abuse process;
- explicit owner approval.

## 15. Open decisions and implementation blockers

The following remain OPEN and must not be guessed:
- registry source of truth, storage consistency and recovery model;
- signing algorithm, key custody, rotation, revocation and build-attestation trust roots;
- workload identity issuance and short-lived credential mechanism;
- exact process/host/network isolation and egress enforcement technology;
- policy decision/enforcement topology and revocation propagation objective;
- audit immutability, retention and privacy policy;
- resource-budget values and service SLOs;
- first module for G1 and its contract/data scope;
- support/admin dual-control policy;
- any multi-tenant or third-party publisher model.

These decisions must be linked to NX-OWNER-DECISIONS-001 or a successor decision register before implementation. NX-RESEARCH-010 candidates remain research only; this document selects no dependency or vendor.

## 16. Current disposition

**PROPOSED / DESIGN ONLY.** No module registry, manifest validator, signing service, grant issuer, module runtime, sandbox, deployment platform, plugin marketplace, commercial plan or external integration is implemented or approved. The permission matrix is a proposed policy baseline, not an executable ACL. Existing G0D/G1 blockers and the explicit owner-approval requirement for PR merge remain unchanged.
