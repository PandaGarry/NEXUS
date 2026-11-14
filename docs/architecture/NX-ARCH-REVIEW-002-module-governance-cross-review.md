# NX-ARCH-REVIEW-002 — Module Governance Cross-Architecture Review

**Status:** REVIEW COMPLETE AT DESIGN LEVEL — no blocking contradiction found after recorded clarifications; owner/security acceptance and implementation evidence remain OPEN  
**Date:** 2026-11-14  
**Scope:** Cross-review of module admission, registry, capabilities, entitlements, trust boundaries, data ownership and revocation semantics  
**Reviewed artifacts:** NX-ARCH-001, NX-ARCH-006, NX-ARCH-007, NX-ARCH-008, NX-SEC-001, NX-IF-001..005, NX-OWNER-DECISIONS-001  
**Purpose:** Check that the new module-registry proposal strengthens rather than contradicts the protected financial core, existing security model, commercial entitlement separation and current owner-approved scope.

## 1. Executive result

The reviewed documents are **compatible at the architecture/design level**. NX-ARCH-008 refines the module admission and lifecycle concepts in NX-ARCH-006 and adds the formal separation between:
- module/artifact admission;
- capability definitions and module declarations;
- independently issued workload grants;
- commercial entitlements;
- request-time authorization by the service owning the resource.

Two wording ambiguities were found and corrected during this review:
1. NX-ARCH-006's phrase that the gateway “validates every request” could be read as granting the gateway sole domain-authorization responsibility. It now distinguishes admission-level checks at the gateway from authoritative action/resource authorization by the owning service.
2. NX-ARCH-008's T4 label grouped protected financial core and Trusted Egress. It now explicitly states that Risk, Command, Ledger and Egress remain separate authorities/workloads/identities; the tier is a protection classification, not a shared permission set.

No design-level contradiction remains in the reviewed path. This is not owner acceptance, a security certification, a runtime implementation or proof of isolation. G0D/G1 remain blocked/open as recorded by the source documents.

## 2. Cross-document consistency matrix

| Concern | Existing source | NX-ARCH-008 treatment | Review result |
|---|---|---|---|
| Core owns financial invariants | NX-ARCH-001, NX-ARCH-006 | Optional modules cannot mutate Risk, reservations, command/outbox, Ledger, halt or trusted egress | ALIGNED |
| Gateway versus domain authorization | NX-ARCH-006, NX-SEC-001 | Gateway performs admission checks; owning service re-authorizes exact principal/action/resource and domain state | CLARIFIED |
| Workload and human identities | NX-ARCH-006, NX-SEC-001 | Separate workload identity, end-user authorization and resource owner enforcement | ALIGNED |
| Manifest and artifact provenance | NX-ARCH-006, NX-SEC-001, NX-RESEARCH-010 | Immutable digest, signer, provenance, SBOM and independent registry approval | ALIGNED; trust roots OPEN |
| Capability and authority | NX-ARCH-006, NX-IF-001..005 | Declaration is not grant; grant is not domain authorization; protected authority cannot be self-assigned | ALIGNED |
| Commercial entitlement | NX-ARCH-007 | Entitlement affects product eligibility/quota only; it cannot mint workload grants or financial authority | ALIGNED |
| Demo/live separation | NX-ARCH-006, NX-ARCH-007 | Distinct account namespace/ledger/simulator; core rejects account-mode mismatch; no live egress | ALIGNED |
| Secret and network isolation | NX-SEC-001, NX-ARCH-006 | No secrets/venue route for optional modules; independent egress/secret enforcement required | ALIGNED; implementation OPEN |
| Data ownership and persistence | NX-ARCH-001, NX-ARCH-006, OD-09 | Domain-owned writes and explicit contracts; no cross-domain direct DB writes | ALIGNED; storage topology OPEN |
| Recovery and revocation | NX-SEC-001, NX-REF-EXEC-002, NX-ARCH-008 | Revocation must be enforced outside workload; stale process containment requires actual fencing | ALIGNED; objective/mechanism OPEN |
| Scope and governance | NX-OWNER-DECISIONS-001 | Personal-first v1 preserved; no public marketplace, SaaS or third-party code execution implied | ALIGNED |
| Optional-module failure | NX-ARCH-001, NX-ARCH-007 | Bounded resources, backpressure and independent disable; core safety controls remain independent | ALIGNED; quantitative SLOs OPEN |

## 3. Findings and dispositions

### F-01 — Gateway admission versus resource-owner authorization

**Severity:** MEDIUM — wording ambiguity, design-level correction applied  
**Evidence:** NX-ARCH-006 §2.1 and §3 previously described the gateway as validating every request without sufficiently distinguishing admission checks from final domain authorization.

**Risk:** An implementation could centralize authorization in the gateway and allow a downstream service to trust a gateway/module assertion without rechecking resource ownership, current domain state or operation-specific policy.

**Correction:** NX-ARCH-006 now states that the gateway authenticates/admit-checks the workload and validates transport/schema/rate/admission state, while the resource-owning service independently authenticates/binds the caller and authorizes the exact user/workload/action/resource and domain invariants.

**Required future evidence:** negative tests at each owning service for forged subject/resource identifiers, stale grants, revoked workload identity and confused-deputy paths. Gateway-only tests are insufficient.

### F-02 — Protected T4 grouping could imply shared authority

**Severity:** LOW — terminology ambiguity, design-level correction applied  
**Evidence:** NX-ARCH-008 §5.2 grouped Protected Financial Core and Trusted Egress under T4.

**Risk:** Readers could infer that Risk, Command, Ledger and Egress share a workload identity, process boundary or permission set.

**Correction:** NX-ARCH-008 now explicitly states that T4 is a protection classification only. Risk, Command, Ledger and Egress remain separately owned and independently controlled authorities/workloads/identities. Optional modules cannot be assigned T4 or inherit protected-domain identity.

**Required future evidence:** deployment and IAM design must show separate identities, credential access and network boundaries for each authority.

### F-03 — Permission matrix is not yet an executable authorization policy

**Severity:** HIGH — implementation blocker, not a contradiction  
**Evidence:** NX-ARCH-008 §8 intentionally provides R/W/C/deny semantics at product-domain level.

**Risk:** A coarse matrix can be mistaken for permission to expose broad APIs or direct data access.

**Disposition:** Matrix remains a proposed deny-by-default policy baseline. Before implementation, every cell must map to a versioned contract, owning service, resource/data scope, enforcement point, audit event and negative test. W means writes to the module's own domain only; C means a request to the owning service, never delegated authority.

### F-04 — Revocation propagation and stale authorization cache are not quantified

**Severity:** HIGH — G1 blocker  
**Evidence:** NX-ARCH-008 §6/§7/§12 requires current revocation state and fail-closed behavior but deliberately leaves propagation objectives open.

**Risk:** A revoked module or grant may continue acting if a process retains credentials or relies on a stale local cache.

**Disposition:** No numeric revocation objective is invented. Before G1, define maximum revocation propagation time, cache freshness, behavior during control-plane outage, in-flight cancellation and independent network/secret fencing. A registry state flip alone is not containment.

### F-05 — Registry, signing and workload-identity trust roots remain unselected

**Severity:** HIGH — G0D/G1 blocker  
**Evidence:** NX-ARCH-008 §15 and OD-08/OD-09; NX-SEC-001.

**Risk:** Without approved registry source of truth, key custody, signer revocation and workload identity issuance, artifact approval cannot be operationally trusted.

**Disposition:** Keep vendor/technology choice open. Require explicit trust-root ownership, key lifecycle, immutable approval history, recovery and independent verification before implementation. No package or provider is selected by this review.

### F-06 — Storage, network and host isolation are policy requirements, not proven controls

**Severity:** CRITICAL — no prototype/production security claim permitted  
**Evidence:** NX-ARCH-001, NX-ARCH-006, NX-SEC-001 and NX-REF-EXEC-002.

**Risk:** A module may bypass an application-level ACL through shared credentials, database grants, host access, proxy bypass or direct network routes.

**Disposition:** G1 evidence must inspect actual DB roles, filesystem/process identity, secret broker and instrumented network boundary. A mocked policy decision or container declaration is insufficient. Trusted Egress fencing remains independently governed by NX-REF-EXEC-002.

### F-07 — First G1 module and resource budgets remain undefined

**Severity:** MEDIUM — sequencing blocker  
**Evidence:** NX-ARCH-008 §14–15.

**Risk:** Attempting to prototype a privileged or cross-domain module first would increase scope and make isolation difficult to prove.

**Disposition:** Candidate first module should be a low-risk first-party read-model module with no secrets and no external egress, but the actual choice remains open until G0D approval. Quantitative CPU/memory/queue/payload/time budgets must be workload-derived, not invented.

### F-08 — Operator/support authority remains governed by OD-12

**Severity:** HIGH — privileged workflow blocker  
**Evidence:** NX-SEC-001 §8 and NX-OWNER-DECISIONS-001 OD-12; NX-ARCH-008 §8.

**Risk:** Support or administration features can become a confused-deputy path into private account, billing or financial data.

**Disposition:** Support is read-only and case-scoped by default. Any privileged operator action requires separate identity, step-up, time limit, dual-control policy and immutable audit. Role assignments and break-glass policy remain unapproved.

## 4. Explicit non-findings

The review did not identify a basis to:
- move Risk or Ledger into optional module execution;
- grant a paid plan or entitlement any security authority;
- permit Demo-to-live routing;
- allow modules direct access to core-owned databases;
- grant optional modules venue credentials or direct venue egress;
- adopt public plugin marketplace, third-party code execution or multi-tenancy;
- select PostgreSQL, OpenBao, Cilium, a container runtime, service mesh or any other dependency.

These remain prohibited, deferred or unselected as described by the source documents.

## 5. Required follow-up and gate mapping

| Work item | Required evidence | Gate |
|---|---|---|
| Map each capability to owner/API/scope/enforcement point | Versioned capability catalog + deny tests | G0D |
| Decide registry/signing/workload identity trust roots | OD-08 and security-reviewed key/identity lifecycle | G0D/G1 |
| Decide registry persistence and audit durability | OD-09 transaction/recovery evaluation | G1 |
| Define revocation and isolation objectives | Threat model, control-plane outage and stale-workload tests | G1 |
| Build permission and data-classification tests | Adversarial cross-domain matrix with boundary observation | G1 |
| Select first read-model module | Bounded scope, no secrets/egress, explicit owner | G1 |
| Verify operator/support boundary | OD-12 and step-up/dual-control tests | G1/G3 |
| Prove external egress fencing | Independent old-generation fence and reconciliation evidence | G1/G2/G3 as applicable |

## 6. Final disposition

**DESIGN CROSS-REVIEW COMPLETE; ACCEPTANCE NOT GRANTED.** NX-ARCH-006/007/008, NX-SEC-001 and NX-ARCH-001 are aligned after the two documented wording clarifications. Eight findings are retained: two terminology clarifications applied and six substantive implementation/approval gaps remain open (F-03..F-08).

This review changes no owner decision, readiness gate, product scope or runtime authority. No code, tests, dependencies, module runtime, registry service, identity provider, database, credentials, venue connection, payment integration, production deployment or live capability was added. PR #16 remains Draft/open/unmerged and requires explicit owner approval before merge.
