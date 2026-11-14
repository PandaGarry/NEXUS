# NX-ARCH-REVIEW-003 — Capability Catalog & Authorization Cross-Review

**Status:** DESIGN CROSS-REVIEW COMPLETE — corrections applied; acceptance and implementation evidence remain OPEN  
**Date:** 2026-11-14  
**Scope:** NX-ARCH-009 capability definitions, scope grammar, data classification, workload grants, entitlement separation and request-time authorization  
**Reviewed against:** NX-ARCH-001, NX-ARCH-006, NX-ARCH-007, NX-ARCH-008, NX-ARCH-REVIEW-002, NX-SEC-001, NX-OWNER-DECISIONS-001 and the current interface/owner-decision baseline  
**Purpose:** Identify ambiguous authority transfer, privilege escalation, data exposure and failure coupling before any executable capability schema or policy service is proposed.

## 1. Executive result

NX-ARCH-009 is compatible with the existing architecture at the design level after one important narrowing correction to the billing capability. The catalog now distinguishes a user-authorized subscription-change **intent** from entitlement-state mutation: only the Billing owner may validate provider state/reconciliation and write entitlement lifecycle records.

The review confirms:
- a capability definition is not a grant;
- a module declaration is not permission;
- a workload grant is not user authorization;
- a commercial entitlement is not a security credential or financial authority;
- request authorization remains with the resource-owning service;
- optional modules cannot receive protected Risk, Command, Ledger, halt/recovery or Trusted Egress authority;
- billing/payment systems are outside the synchronous order dispatch and execution path.

This is a design cross-review only. It does not approve candidate capability names, create an executable policy schema, close owner decisions, or establish security certification. G0D/G1 remain open.

## 2. Cross-document consistency matrix

| Concern | Source baseline | NX-ARCH-009 treatment | Result |
|---|---|---|---|
| Capability and grant separation | NX-ARCH-006/008 | Platform-owned definitions; module declarations; independent grants; request-time owner authorization | ALIGNED |
| Entitlement versus authorization | NX-ARCH-007 | Entitlement is product eligibility/quota only; cannot issue workload grant or protected authority | ALIGNED |
| Billing event authority | NX-ARCH-007 | Billing owner alone validates provider events/reconciliation and writes entitlement state | ALIGNED after clarification |
| Protected financial path | NX-ARCH-001, NX-REF-EXEC-002 | No optional-module capability for Risk mutation, reservation, command/outbox, Ledger posting or egress | ALIGNED |
| User/workload principal binding | NX-ARCH-006, NX-SEC-001 | Both principals authenticated; resource owner resolves canonical resource and checks ownership | ALIGNED |
| Data minimization/classification | NX-SEC-001, NX-ARCH-006 | Field-level classification; financial read models remain restricted; secret access denied | ALIGNED; detailed inventory OPEN |
| Demo/live isolation | NX-ARCH-006/008 | Demo namespace and core account-mode enforcement; no live outbox/egress | ALIGNED |
| Revocation and stale cache | NX-ARCH-008 | Monotonic generation, bounded cache, fail-closed outage; numeric objectives remain open | ALIGNED; G1 blocker |
| Audit integrity | NX-SEC-001, NX-ARCH-008 | Redacted audit outcomes; independent custody/retention still required | ALIGNED; OD-09/10/legal review OPEN |
| Contract and API ownership | NX-ARCH-001, NX-IF-001..005 | Each catalog entry maps to a single owner/enforcement authority; exact endpoint references remain unapproved | ALIGNED; mapping incomplete |

## 3. Findings and dispositions

### CAP-R-01 — Billing subscription capability could be misread as entitlement write authority

**Severity:** HIGH — semantic ambiguity corrected  
**Risk:** A UI or optional module might interpret the subscription-management capability as permission to write plan/entitlement state, or treat a payment redirect/client claim as proof of payment.

**Correction applied:** The capability now means only “submit a user-authorized subscription-change intent to the Billing owner.” The Billing owner alone validates signed provider events and reconciliation and writes entitlement lifecycle. The capability cannot create, sign, activate, extend or revoke entitlement records. Billing remains absent from Risk, command acceptance, dispatch and Trusted Egress synchronous dependencies.

**Required evidence:** Future tests must forge client plan claims, replay/out-of-order provider events, submit duplicate intents, simulate provider outage and prove entitlement state changes only after authoritative provider verification/reconciliation.

### CAP-R-02 — Capability ID stability must not be confused with current approval

**Severity:** MEDIUM — governance requirement  
**Risk:** A reserved or published identifier may be mistaken as an active operation.

**Disposition:** IDs remain proposed until owner approval. Lifecycle state and definition version are authoritative. Unknown, draft, deprecated or retired IDs deny by default. An identifier is never permission.

### CAP-R-03 — Typed scope grammar still needs canonical resource binding

**Severity:** HIGH — G1 blocker  
**Risk:** SELF, explicit resource sets or namespace references can be unsafe if derived from caller-controlled IDs or ambiguous normalization.

**Disposition:** Owning service must derive subject and namespace from authenticated context, canonicalize identifiers before policy evaluation, validate ownership in authoritative state and reject duplicate/ambiguous encodings. No caller-provided account ID or tenant ID may widen scope. Add Unicode/normalization, alias and identifier-substitution tests.

### CAP-R-04 — Financial read-model projections require field-level lineage and minimization

**Severity:** HIGH — G1 blocker  
**Risk:** An approved projection may accidentally include raw credentials, private order payloads, excessive account metadata or data from another subject.

**Disposition:** Each projection needs a field-level data inventory, source lineage, minimization purpose, retention, subject/resource filter and export policy. Derived data inherits the most restrictive source class unless an approved declassification decision exists. A projection is not automatically safe because it is read-only.

### CAP-R-05 — Capability-to-contract mapping is not yet complete or executable

**Severity:** HIGH — G0D blocker  
**Risk:** Candidate capability rows can be implemented as broad APIs without explicit owner, scope, transaction, idempotency and denial behavior.

**Disposition:** Every accepted capability must map to a versioned interface contract, owning service, canonical resource type, request/response schema, idempotency/replay behavior, timeout/retry policy, audit event and negative test. Do not invent endpoint names or infer that an API already exists.

### CAP-R-06 — Revocation/cache/outage semantics lack numeric service objectives

**Severity:** HIGH — G1 blocker  
**Risk:** A stale policy or grant cache may allow actions after revocation or during loss of the policy control plane.

**Disposition:** Set maximum propagation time, cache age, in-flight cancellation behavior and acknowledgement requirements per action class. Read-only low-risk behavior may have a distinct policy, but no privileged or financial action may fail open. Registry state change alone is not proof of credential/network containment.

### CAP-R-07 — Audit record integrity and privacy are not yet operationally proven

**Severity:** HIGH — G1/G3 blocker  
**Risk:** Audit data may be mutable by the same principal it records, leak personal/financial data, or be unavailable during incident recovery.

**Disposition:** Define independent custody, signer/key separation, retention/legal basis, access review, clock-quality metadata, backup/restore and tamper-evidence verification. Hash chaining alone is insufficient if the same principal controls records and verification keys.

### CAP-R-08 — Initial catalog is intentionally incomplete

**Severity:** LOW — scope discipline  
**Risk:** Missing Automation, API/Integrations, Administration, Identity or Strategy Lab operations could tempt implementers to add generic admin, execute, trade or wildcard capabilities.

**Disposition:** Keep omitted domains unsupported until each has a dedicated owner, bounded operation, scope, data class and threat review. No generic admin, execute, write:any, trade:any, database.read or network.egress capability is permitted.

### CAP-R-09 — Billing and optional modules must remain outside protected execution latency/failure domain

**Severity:** CRITICAL — non-negotiable architecture invariant  
**Risk:** Synchronous entitlement/payment checks in Risk or dispatch can couple trading safety to provider latency, outages or event replay.

**Disposition:** Billing may affect product eligibility before a product action is admitted, but the protected execution path must not call payment/Billing services synchronously. Trading Risk, command, reservations, dispatcher and Trusted Egress enforce their own security and safety state. Entitlement caches cannot replace hard risk limits or safety checks.

## 4. Required adversarial evidence additions

NX-ARCH-009 CAP-01..18 remains the base qualification matrix. Add:

| ID | Additional scenario | Required result |
|---|---|---|
| CAP-19 | Duplicate keys, Unicode normalization or alias collision in resource scope | Strict parse/canonicalization rejects ambiguity; no widened scope |
| CAP-20 | Projection contains a forbidden field or cross-subject row | Data-lineage/field filter rejects or strips under approved policy; safe audit reason |
| CAP-21 | Billing client claims payment success without provider evidence | No entitlement mutation |
| CAP-22 | Billing webhook is replayed, delayed, reordered or conflicts with provider reconciliation | Idempotent reconciliation; authoritative provider state wins |
| CAP-23 | Capability owner attempts generic wildcard or admin/execute/trade capability | Catalog governance rejects |
| CAP-24 | Audit writer and verifier share compromised credentials | Independent custody detects/contains; no false tamper-proof claim |
| CAP-25 | Billing provider outage while order dispatch is active | Protected execution remains independent; no synchronous billing dependency |
| CAP-26 | Retired capability version is replayed after upgrade | Owning service rejects unsupported version; no compatibility fallback |

## 5. Open decisions and gate disposition

| Work item | Gate | Current disposition |
|---|---|---|
| Accept capability naming/versioning and lifecycle | G0D | OPEN — proposal only |
| Approve domain owner and enforcement authority for every row | G0D | OPEN |
| Map each capability to exact contract and test | G0D | OPEN |
| Approve field-level data classification/lineage/retention | G0D/G1 | OPEN |
| Decide signing and key custody (OD-08) | G1/G3 | OPEN |
| Decide durable registry/audit persistence (OD-09) | G1 | OPEN |
| Set freshness/recovery/revocation objectives (OD-10) | G1/G2 | OPEN |
| Define support/operator step-up and dual control (OD-12) | G1/G3 | OPEN |
| Prove actual process/DB/secret/network boundaries | G1 | NOT IMPLEMENTED |
| Run CAP-01..26 with observed boundary evidence | G1 | NOT IMPLEMENTED |

## 6. Final disposition

**DESIGN CROSS-REVIEW COMPLETE; ACCEPTANCE NOT GRANTED.** One high-severity semantic ambiguity was corrected (Billing subscription intent versus entitlement-state write). Eight additional findings remain as implementation/approval requirements (CAP-R-02..09). The review does not select vendors, schema formats, APIs, storage, cryptographic algorithms or runtime isolation technology.

No code, executable schema, policy engine, grant issuer, active permission, module runtime, dependency, payment integration, credential, account connection, order or production deployment was added. PR #16 remains subject to explicit owner approval before merge. G0D/G1 remain open.
