# NX-ARCH-REVIEW-004 — Capability-to-Interface Contract Traceability

**Date:** 2026-11-14  
**Status:** DESIGN TRACEABILITY REVIEW COMPLETE — owner acceptance, field-level classification and implementation evidence remain OPEN  
**Scope:** NX-ARCH-009 candidate capability catalog mapped against NX-IF-001..005, NX-SEC-001 and NX-OWNER-DECISIONS-001  
**Related:** NX-ARCH-006, NX-ARCH-007, NX-ARCH-008, NX-ARCH-009, NX-ARCH-REVIEW-002, NX-ARCH-REVIEW-003

## 1. Purpose and review method

This review closes the document-discovery and traceability step for the proposed capability catalog. It identifies which existing contracts actually govern protected execution/accounting/recovery operations, which candidate product capabilities have no corresponding interface contract yet, and which data/authorization details cannot safely be inferred.

The canonical files were located on branch `engineering/rust-execution-domain-conformance-v0`:

- [NX-IF-001 — Canonical Trade Command & Risk Approval](NX-IF-001-canonical-trade-command-risk-approval-contract.md)
- [NX-IF-002 — Exposure Snapshot & Risk Reservation](NX-IF-002-exposure-snapshot-risk-reservation-contract.md)
- [NX-IF-003 — Execution Event & Ledger Posting](NX-IF-003-execution-event-ledger-posting-contract.md)
- [NX-IF-004 — State Evidence, Freshness & Recovery Barrier](NX-IF-004-state-evidence-freshness-recovery-barrier-contract.md)
- [NX-IF-005 — Emergency Operations, Halt & Risk-Reduction Authorization](NX-IF-005-emergency-operations-halt-risk-reduction-contract.md)
- [NX-SEC-001 — Threat Model & Credential Isolation](../security/NX-SEC-001-threat-model-credential-isolation.md)
- [NX-OWNER-DECISIONS-001 — Critical Owner Decision Register](NX-OWNER-DECISIONS-001-critical-owner-decision-register.md)

The review distinguishes (a) an existing domain contract, (b) a candidate product capability, and (c) an approved API/grant. The first does not automatically establish the second or third. No endpoint, database table, event schema, permission or runtime is invented by this mapping.

## 2. Cross-contract authority baseline

| Contract | Authoritative responsibility evidenced by the contract | Authorization / enforcement implication | Capability-catalog disposition |
|---|---|---|---|
| NX-IF-001 | Risk owns the RiskDecision and RiskApprovalCapability; Execution independently validates exact command binding, scope, expiry, halt epoch, compatibility and single-use consumption | Approval is command-specific, not a general module permission or venue credential; AI/Strategy cannot issue or consume it | Protected core contract; no optional-module capability |
| NX-IF-002 | Risk is sole publisher of authoritative ExposureSnapshot and owns reservation state; Execution owns dispatch/order facts; Ledger owns posted financial facts | Durable reservation precedes approval; scope/capacity serialization and conservative exposure retention are mandatory | Protected Risk contract; no optional-module capability or direct projection-store access |
| NX-IF-003 | Execution owns normalized venue order/fill facts and source evidence; Ledger owns posted journals, balances and accounting projections | Execution-to-Ledger handoff is at-least-once with durable outbox/inbox and atomic Ledger posting; neither domain may assume the other's authority | Protected financial-data contract; only separately approved minimized read models may be exposed |
| NX-IF-004 | Owns state-evidence quality/freshness and RecoveryBarrier composition across source evidence, checkpoints, projections and reconciliation | Risk-increasing authorization depends on current READY evidence for exact scope/operation; stale or incomplete evidence fails closed | Protected recovery/freshness contract; no optional module may publish/override barrier state |
| NX-IF-005 | Defines halt scope/epoch, emergency plan/command classification, authorization and final-dispatch enforcement | Halt activation is independently available; risk-reduction remains authenticated/scoped and routed through Execution; no generic emergency bypass | Protected control-plane contract; no optional-module halt/resume/dispatch grant |
| NX-SEC-001 | Establishes credential, signing, identity, service, client, recovery and build/operations trust boundaries | Exchange secrets/signing authority are isolated from clients, AI, Strategy, Analytics and logs; production requires owner-approved evidence | Security constraint across every row; not itself an application API contract |

### 2.1 Non-negotiable owner constraints

The owner decision register accepts for v1 one venue plus one dedicated account/subaccount (OD-01), account/subaccount as the initial hard-limit and reservation scope (OD-04), and a server-authoritative autonomous runtime with Web/Desktop as clients (OD-15, partially accepted). It does not accept a venue, product/account mode, numeric risk limits, signing/key custody, storage transaction model, freshness/recovery objectives, accounting policy, emergency operator roles or live authorization.

Consequently:
- do not infer multi-venue or cross-portfolio scope;
- do not interpret an unconfigured parent scope or unknown external activity as unlimited/zero exposure;
- do not define financial limits, freshness thresholds, revocation SLOs or recovery objectives by guess;
- do not treat a proposed capability ID as an approved grant;
- do not couple Billing/entitlement services synchronously to Risk, command acceptance, dispatch or Trusted Egress.

## 3. Candidate capability traceability

The table below covers every initial candidate in NX-ARCH-009. “No contract” means the current reviewed NX-IF-001..005 set does not define that product API; it does not mean the feature is impossible or approved.

| Candidate capability | Existing contract evidence | Accountable owner / enforcement boundary | Resource and data scope established today | Missing contract / decision |
|---|---|---|---|---|
| `nexus.market-data.read` | No dedicated market-data interface among NX-IF-001..005; IF-001/004 consume market/spec evidence but do not define a module read API | Market Data owner named in ARCH-009; exact service contract absent | Proposed approved instruments/time range; public/internal only; private account data and credentials excluded | Market-data read contract, source provenance/freshness, instrument allowlist, pagination/retention, audit and negative tests |
| `nexus.profile.self.read` | No Identity & Access interface in reviewed IF set | Identity & Access | Authenticated subject's own minimal profile (PERSONAL) | Principal/session contract, canonical subject binding, field allowlist, consent/retention, cross-subject denial tests |
| `nexus.demo.simulation.run` | IF-001 defines PAPER/SANDBOX/LIVE scope fields but is not a Demo API; IF-005 prohibits generic bypass | Demo & Simulation; server-side namespace enforcement | Server-assigned demo namespace; untrusted input and internal data | Demo lifecycle/API contract, deterministic isolation, routing proof that demo cannot reach live account/outbox/egress |
| `nexus.strategy.artifact.read` | No Strategy artifact contract in IF-001..005 | Strategy Lab | Own/authorized artifact namespace; PERSONAL / UNTRUSTED_INPUT | Artifact identity/version/ACL contract, immutable artifact binding, content limits, malware/parser boundary and audit |
| `nexus.strategy.artifact.write` | No Strategy artifact write contract in IF-001..005 | Strategy Lab | Own/authorized artifact namespace only; no core-state writes | Write transaction/idempotency/version-conflict contract, retention/deletion policy, path/namespace negative tests |
| `nexus.analytics.query` | IF-003 defines Ledger-owned accounting projections; IF-002 defines Risk-owned exposure snapshots. Neither grants raw store/query access | Analytics owns query API; source domains retain field-level authority | Approved minimized projections only; INTERNAL/PERSONAL/FINANCIAL_RESTRICTED as applicable | Projection catalog, field-level lineage/classification, subject/resource filter, query budget, timeout/cancellation, retention and row/field leakage tests |
| `nexus.portfolio.report.generate` | IF-003 establishes Ledger accounting facts and projections; IF-002 establishes Risk exposure view. Neither defines report generation | Portfolio & Reporting; source owners approve projection contracts | User-authorized account/report scope, FINANCIAL_RESTRICTED projection only | Report input/output schema, source watermark/freshness, field minimization, export/download authorization, retention and cross-account tests |
| `nexus.learning.progress.read` | No Learning contract in IF-001..005 | Learning & Knowledge | Authenticated user's own learning progress (PERSONAL) | Learning progress read contract, subject binding, field list, retention and cross-subject denial |
| `nexus.learning.progress.write` | No Learning write contract in IF-001..005 | Learning & Knowledge | Own learning namespace only; cannot alter entitlements or account permissions | Write/idempotency/version contract, allowed state transitions, audit and tamper/replay tests |
| `nexus.notification.publish` | No Notifications contract in IF-001..005; IF-005 audit/incident requirements are not a general publish API | Notifications & Collaboration | Approved template + consented destination; PERSONAL/INTERNAL; no secret-bearing arbitrary payload | Template/event schema, consent and destination binding, retry/dedupe, rate/size limits, secret-redaction and URL-abuse tests |
| `nexus.billing.usage.read` | No Billing contract in IF-001..005; ARCH-007/009 define separation only | Billing & Entitlements | Minimum subject-scoped usage aggregate; PERSONAL/INTERNAL | Usage definition/source-of-truth, aggregation granularity, privacy/retention, subject binding and cross-subject tests |
| `nexus.billing.subscription.manage` | No Billing provider/API contract in IF-001..005; ARCH-009 constrains it to user-authorized intent submission | Billing & Entitlements alone validates provider events/reconciliation and writes entitlement lifecycle | Authenticated billing subject; subscription-change intent only | Billing intent/provider reconciliation contract, webhook signature/replay/order semantics, dedupe, lifecycle transition table, dispute/refund handling and audit |

### 3.1 Protected operations — existing contracts, not module capabilities

The following operations are governed by existing protected contracts and must not be added to the optional-module catalog:

- Risk evaluation, policy/limit mutation, reservation create/consume/release and authoritative exposure publication — NX-IF-001/002.
- Command acceptance, outbox/dispatcher authority, final egress and ambiguous-outcome handling — NX-IF-001 plus the execution/egress architecture and NX-SEC-001.
- Execution facts, fill identity/corrections and Ledger journal posting — NX-IF-003.
- Freshness/evidence publication and recovery readiness — NX-IF-004.
- Halt activation/propagation, emergency command authorization and resume — NX-IF-005.
- Exchange credentials, signing keys and production secret operations — NX-SEC-001.

A public API or workflow may submit a user-originated request to a protected domain. That request remains subject to authenticated principal binding, domain authorization, Risk, reservation, command/outbox, recovery, halt, audit and final egress checks. It does not receive reusable permission to perform the protected operation.

## 4. Cross-cutting contract requirements for any future capability

Every future capability contract must specify, before implementation:

1. **Identity:** authenticated user principal and/or workload identity; exact issuer/audience and artifact binding where a module is involved.
2. **Resource binding:** source-owner resolution of canonical resource identity; no caller-supplied identifier widening, wildcard, alias ambiguity or implicit parent scope.
3. **Data contract:** request/response fields, data classification per field, source lineage, minimization/declassification, retention and deletion/legal basis.
4. **Transaction semantics:** owning transaction boundary, atomicity, idempotency key and scope, duplicate/replay behavior, version/CAS behavior and durable audit outcome.
5. **Operational bounds:** timeout, cancellation, retry/backoff, rate/concurrency/payload/pagination limits, backpressure and behavior during dependency outage.
6. **Authorization:** owner and enforcement point, purpose, resource scope, grant generation/revocation check and finite deny reason codes.
7. **Audit:** actor/workload, capability and contract version, canonical resource, policy/grant generation, result, reason, correlation and timestamp quality; no secrets or unnecessary personal/financial payload.
8. **Negative tests:** unauthorized subject/resource, stale/revoked grant, malformed/ambiguous identity, duplicate request, outage/timeout, forbidden field, excessive query and attempted cross-domain mutation.
9. **Evidence:** tests must observe authoritative persisted state and the actual API/process/DB/secret/network boundary. Mock-only policy tests do not prove isolation.

These are requirements for future contract authorship, not claims that the fields or mechanisms already exist.

## 5. Findings and required actions

| ID | Severity | Finding | Required action / gate |
|---|---|---|---|
| IF-CAP-01 | HIGH | The existing IF set is execution/accounting/recovery/control-plane focused; most ARCH-009 product capabilities have no canonical interface contract | Keep those capabilities proposal-only; create a domain-owned contract before schema/API/grant work (G0D) |
| IF-CAP-02 | CRITICAL | IF-001/002/003/004/005 are protected authority boundaries, not general-purpose module data APIs | Do not grant modules direct access to their stores or state transitions; expose only owner-approved minimized read models |
| IF-CAP-03 | HIGH | ARCH-009 classifications are broad projection classes, not field-level inventory or lineage | Source owners must produce field-level data inventory, retention and minimization decisions (G0D/G1) |
| IF-CAP-04 | HIGH | User/workload/resource binding, idempotency, timeout/retry and audit semantics are incomplete for product-domain capabilities | Define these in each new domain contract; do not invent endpoint names or default retry semantics |
| IF-CAP-05 | HIGH | Revocation/cache freshness and outage objectives remain unspecified; OD-10 is open | Propose measurable options and failure matrix, then obtain owner/security acceptance before G1 |
| IF-CAP-06 | HIGH | Billing provider/webhook semantics are not defined by current IF contracts | Keep Billing isolated; no synchronous dependency in protected execution path; require separate Billing contract and CAP-21/22/25 evidence |
| IF-CAP-07 | HIGH | The owner-approved v1 account boundary narrows data access; no multi-venue/shared portfolio scope is accepted | Bind future portfolio/analytics capabilities to the single dedicated account/subaccount until a new decision |
| IF-CAP-08 | MEDIUM | Administration & Support case-scoped access appears in ARCH-009's mapping but has no initial candidate capability ID | Do not silently create a generic support capability; define a separate case-bound proposal and approval if needed |

## 6. Field-level data inventory — grounded status

This review does not claim that a complete field inventory exists. The source contracts establish the following categories only:

| Source contract | Explicitly evidenced data groups | Classification / lineage status |
|---|---|---|
| NX-IF-001 | TradeIntent, canonical command envelope, exact financial values, account/venue/instrument/environment scope, Risk decision/approval claims, command digest and audit event ID | Financially sensitive execution data; field-level classification/retention not yet approved |
| NX-IF-002 | RiskScope, exposure items/buckets, immutable ExposureSnapshot, reservation identity/amount/scope/version, source identity and audit lineage | FINANCIAL_RESTRICTED candidate; exact field-level labels and projection minimization unresolved |
| NX-IF-003 | Venue/account/instrument/execution identity, normalized order/fill facts, raw source evidence, journal transaction, debit/credit postings, balances/positions and accounting projections | FINANCIAL_RESTRICTED; raw evidence vs derived projection lineage must be preserved; field retention unresolved |
| NX-IF-004 | Source evidence vectors, freshness/completeness/quality, checkpoints, cursors/watermarks, recovery stages and READY barrier | INTERNAL / FINANCIAL_RESTRICTED depending on referenced source; exact fields and retention unresolved |
| NX-IF-005 | Halt scope/state/epoch, incident, EmergencyActionPlan, target sets, command classification, authorization/evidence references and audit events | INTERNAL / FINANCIAL_RESTRICTED; operator identity and incident data require minimization |
| NX-SEC-001 | Credential metadata, workload/service identity, security events, audit evidence, incident and recovery records | SECRET values are prohibited from optional-module access and ordinary logs; metadata still requires field-level classification |

Do not copy whole contract payloads into Analytics, Portfolio, Notifications or support views. A derived dataset inherits the most restrictive source classification unless the source owner approves a documented minimization/declassification rule. Raw Ledger/Risk stores are not query APIs.

## 7. Revocation and outage objectives — proposal only

No numeric objective is selected in this review. Before G1, owners should decide and measure at least:

- maximum grant/policy cache age for low-risk reads;
- maximum revocation propagation time and how in-flight requests are cancelled or fenced;
- whether each operation requires online authoritative grant-generation checks;
- behavior when identity, registry, authorization, source owner or audit store is unavailable;
- behavior during partial partition where one process has stale state;
- recovery criteria after a revocation or control-plane outage.

Conservative interim behavior: unknown/stale generation denies privileged action; no privileged fail-open; if revocation or authority cannot be confirmed, affected capability remains disabled. Cache invalidation alone is not proof that credentials, processes or network routes have been revoked.

## 8. Gate disposition

- **G0D:** this traceability pass is complete as a design artifact. Capability naming/lifecycle, owners, scopes, field classification, contract mapping and negative tests still require explicit acceptance.
- **G1:** blocked until the relevant OD-08/09/10/12 decisions, canonical schemas, a low-risk first-party read-model contract, workload/grant binding, measured revocation objectives and actual DB/process/secret/network deny evidence exist.
- **G2/G3:** unchanged. No venue qualification, live credentials, numeric risk limits or live execution authority is implied.

No executable schema, endpoint, database table, policy engine, grant issuer, runtime, dependency, payment integration, credential, account connection, order or production deployment was created by this review.

**Final disposition: DESIGN TRACEABILITY REVIEW COMPLETE; ACCEPTANCE NOT GRANTED.** NX-ARCH-009 candidate capabilities remain proposals. NX-IF-001..005 remain protected domain contracts. PR #16 remains Draft and unmerged pending explicit owner approval.
