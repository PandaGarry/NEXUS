# NX-IF-001 — Canonical Trade Command & Risk Approval Contract

**Date:** 2026-11-14  
**Status:** PROPOSED — normative interface draft; not accepted  
**Work package:** NX-ARCH-REVIEW-001 / WP-A  
**Applies to:** ТЗ-NX-003, ТЗ-NX-004, ТЗ-NX-005, NX-ADR-002, NX-ADR-005, NX-ARCH-001  
**Baseline branch:** `docs/project-foundation`  
**Baseline commit reviewed:** `0a6f0f5700bd24c31e260aba01d12abb6d8eafbf`

## 1. Purpose and scope

Define one interoperable, versioned contract from a strategy/user proposal to an independently authorized execution command.

This interface covers:
- proposal identity and lineage;
- canonical command fields and semantic validation;
- deterministic canonicalization and payload digest;
- Risk Engine decision and approval capability;
- independent Execution-side verification;
- expiry, one-time consumption, replay protection and invalidation;
- rejection behavior and contract conformance tests.

Out of scope:
- venue-specific REST/WebSocket wire payloads and signing;
- risk policy contents and numeric limits;
- reservation accounting internals (WP-B);
- distributed persistence/outbox protocol beyond required references (WP-B/WP-C);
- choice of cryptographic algorithms, serialization library, RPC protocol or database;
- live trading authorization.

## 2. Normative language and safety invariants

The terms MUST, MUST NOT, SHOULD and MAY are normative.

1. TradeIntent is a proposal, never an executable order.
2. Only a CanonicalTradeCommand can be evaluated for execution authorization.
3. RiskApprovalCapability MUST bind to the exact canonical command digest and all required scope/version fields.
4. Any change to an execution-affecting field MUST produce a different digest and invalidate the previous approval.
5. Execution MUST independently validate approval authenticity, scope, expiry, current halt epoch, spec/policy compatibility and one-time consumption.
6. An approval is not an exchange credential and grants no authority to sign arbitrary requests.
7. Unknown, unsupported, malformed, ambiguous or omitted-required fields MUST reject; they MUST NOT be silently defaulted.
8. Numeric financial values MUST use exact decimal strings or an equally exact schema representation; binary floating-point is forbidden in canonical command fields.
9. The canonical command MUST be immutable after creation. Amend/cancel are separate commands referencing the target order.
10. Idempotency prevents duplicate logical intake; it does not imply exactly-once delivery to an exchange.
11. No client, AI component or strategy can mint, modify, extend or replay an approval.
12. The command and approval protocol MUST fail closed when required trust, version or state evidence is unavailable.

## 3. Three-stage object model

### 3.1 TradeIntent — proposal

Owned by ТЗ-NX-003. It expresses desired trading action, not a venue instruction.

Required identity/lineage:
- `intent_id`: globally unique immutable identifier;
- `intent_schema_version`;
- `idempotency_key` and declared scope;
- `origin`: STRATEGY, AUTHORIZED_OPERATOR or SYSTEM_POLICY;
- `strategy_artifact_id` and immutable version when origin is STRATEGY;
- `decision_context_digest`;
- `created_at`, `not_after`;
- `target`: desired exposure/action semantics, not yet an executable order;
- `evidence_refs`: market/account snapshot references and quality metadata.

A TradeIntent MUST NOT contain a Risk Approval, exchange signature or private API credential. Confidence/score is advisory metadata and MUST NOT be interpreted as risk permission.

### 3.2 CanonicalTradeCommand — executable instruction candidate

Owned by ТЗ-NX-004 command intake and canonical command contract. It is created by an authorized command-construction path after validating the proposal and resolving it into a specific order instruction.

It is immutable and versioned. One command represents one logical operation. CREATE, AMEND, CANCEL and emergency/control operations are distinct command types; they MUST NOT be encoded as mutations of an existing command.

### 3.3 RiskApprovalCapability — constrained authorization

Owned and signed by ТЗ-NX-005. It authorizes only the exact command digest and scope declared in the capability. It is not a general account permission, not a risk policy, and not a venue request signature.

The capability MUST be independently verifiable by Execution without asking AI or Strategy to interpret it.

## 4. CanonicalTradeCommand v1

### 4.1 Envelope fields

| Field | Type / rule | Required |
|---|---|---|
| schema_id | Fixed identifier `nexus.canonical_trade_command` | Yes |
| schema_version | Integer major/minor; v1 semantics immutable | Yes |
| nexus_command_id | Globally unique immutable ID | Yes |
| command_type | CREATE, AMEND, CANCEL, CLOSE, REDUCE_ONLY, CANCEL_ALL; unsupported type rejects | Yes |
| environment | PAPER, SANDBOX, LIVE | Yes |
| origin | STRATEGY, AUTHORIZED_OPERATOR, SYSTEM_POLICY | Yes |
| intent_id | Original TradeIntent ID; null only for explicitly permitted non-strategy operations | Conditional |
| parent_command_id | Prior command for causal link, e.g. amend/cancel chain | Conditional |
| idempotency_key | Caller-generated immutable key | Yes |
| idempotency_scope | Tenant + account + operation namespace | Yes |
| account_ref | Internal immutable account/subaccount reference | Yes |
| venue_id | Canonical venue identifier | Yes |
| market_type | SPOT, LINEAR_PERPETUAL, INVERSE_PERPETUAL, dated/futures as supported | Yes |
| instrument_id | Stable NEXUS instrument identity | Yes |
| venue_instrument_id | Exact native instrument identifier | Yes |
| instrument_spec_version | Immutable ADR-005 specification version | Yes |
| side | BUY or SELL where applicable | Conditional |
| position_side | Explicit LONG, SHORT, NET or venue-specific supported value | Conditional |
| order_type | Explicit supported order type | Conditional |
| quantity | Exact positive decimal string in native order quantity units | Conditional |
| price | Exact decimal string or explicit null where order type permits | Conditional |
| trigger_price | Exact decimal string or explicit null | Conditional |
| trigger_reference | MARK, INDEX, LAST or supported venue reference | Conditional |
| time_in_force | Explicit supported enum; no implicit venue default | Conditional |
| reduce_only | Explicit boolean; absence rejects for applicable commands | Conditional |
| close_position | Explicit boolean only where venue semantics are certified | Conditional |
| post_only | Explicit boolean | Conditional |
| position_mode | Immutable expected account mode/version or reference | Yes for derivatives |
| margin_mode | ISOLATED, CROSS, PORTFOLIO or venue-defined supported value | Yes for derivatives |
| price_protection / execution flags | Explicit typed map with schema-defined allowlist | Yes; empty allowed |
| target_order_ref | Immutable NEXUS order identity for amend/cancel | Conditional |
| target_venue_order_id | Native order identity when known; otherwise explicit absence reason | Conditional |
| created_at | UTC RFC 3339 timestamp with defined precision | Yes |
| not_after | UTC RFC 3339 timestamp; bounded maximum lifetime | Yes |
| halt_epoch | Current monotonic halt generation observed at command creation | Yes |
| correlation_id | End-to-end trace ID | Yes |
| causation_id | Parent event/decision ID | Yes |
| extensions | No arbitrary executable extensions in v1; unknown keys reject | Yes, empty object allowed |

Conditional fields are required according to the command-type and order-type validation matrix. The matrix MUST be explicit and versioned; a missing field is not equivalent to a venue default.

### 4.2 Command-type rules

- CREATE: requires account, instrument, side, order type and all required sizing/pricing/TIF fields.
- AMEND: is a new command with its own ID and digest; references one existing order; includes the complete resulting effective order parameters, not a partial patch whose meaning depends on mutable defaults.
- CANCEL: is a new command referencing one target order. It does not imply the order is canceled; venue outcome must be reconciled.
- CLOSE / REDUCE_ONLY: are not inherently safe. They require explicit position mode, quantity/close semantics and fresh position evidence; venue-specific capability must be certified.
- CANCEL_ALL: is a separately scoped control command with explicit account/instrument scope and bounded target set semantics. It cannot be represented as a generic unbounded request.
- Unsupported command type or venue capability MUST reject before risk approval.

A cancel or reduce command can remove protection, race with a fill, or reverse exposure. Risk policy defines whether it is risk-increasing, risk-reducing or indeterminate. There is no universal bypass.

## 5. Canonicalization and digest

### 5.1 Canonicalization requirements

Before hashing:
1. Validate against the exact schema version and command-type matrix.
2. Reject duplicate object keys, unknown fields, invalid enum values, malformed timestamps and invalid decimal strings.
3. Normalize timestamps to UTC with the contract-defined precision.
4. Normalize decimal strings to a unique representation: no exponent notation, no leading plus, no unnecessary leading zeros, no trailing fractional zeros, and zero represented as `0`. Negative zero is forbidden.
5. Distinguish null from absent. Required nullable fields are present with explicit null; optional omission is permitted only where the schema explicitly says so.
6. Apply deterministic object-key ordering and UTF-8 encoding. Arrays preserve semantic order; set-like arrays require schema-defined sorting.
7. Include schema ID and version in the canonical bytes.
8. Exclude transport headers, signatures, mutable delivery attempts and non-semantic tracing metadata only if the schema explicitly identifies them as outside the command payload. All execution-affecting fields remain included.

G1 canonical-byte baseline is selected in NX-ADR-008: RFC 8949 core deterministic CBOR under the strict NEXUS profile. The exact encoder/decoder library and version remain an implementation qualification item and MUST be pinned and backed by cross-language golden vectors. Ordinary JSON serialization is not canonical.

### 5.2 Digest

`command_digest = HASH(domain_separator || canonical_command_bytes)`

The domain separator MUST be unique to NEXUS canonical trade commands and include the major schema version. G1 digest baseline is SHA-256 with a fixed NEXUS command-domain separator. The exact versioned digest envelope and cross-language vectors remain mandatory before implementation; production security review remains open.

The digest is calculated over the complete immutable CanonicalTradeCommand payload. Approval metadata is not embedded into the command digest, avoiding a circular dependency.

## 6. RiskEvaluationRequest v1

Risk Engine receives:
- complete canonical command and computed digest;
- authenticated caller/service identity and authorization scope;
- current account/venue/instrument references;
- immutable instrument specification version;
- current policy bundle/version and policy evaluation mode;
- exposure snapshot ID/version and reservation state reference;
- immutable valuation_input_vector_id/version for mark/index/FX/fee/collateral inputs and its source-specific freshness evidence;
- StateEvidence/FreshnessVector reference (WP-D);
- current halt epoch and scoped halt state;
- requested evaluation deadline;
- provenance references for positions, open orders, pending commands, balances, market state and reconciliation.

The Risk Engine MUST recompute the digest from canonical bytes. It MUST NOT trust a caller-supplied digest without recomputation.

A request with mismatched account, unknown instrument, unsupported command semantics, stale evidence, unresolved exposure or incompatible policy/spec version returns DENY or REQUIRE_REVIEW, never APPROVE.

## 7. RiskDecision v1

Decision enum:
- APPROVE — executable only when accompanied by a valid RiskApprovalCapability and durable reservation reference where required;
- DENY — explicit hard failure with stable reason code;
- REQUIRE_REVIEW — non-executable; requires authorized human/process resolution and a new evaluation.

Required fields:
- decision_id;
- command_id and recomputed command_digest;
- decision enum;
- stable reason_codes and bounded diagnostic references;
- evaluated_at and decision_deadline;
- policy_bundle_id/version;
- instrument_spec_version;
- exposure_snapshot_id/version;
- valuation_input_vector_id/version;
- state_evidence_ref/version;
- halt_epoch;
- reservation_id/version when applicable;
- evaluation_engine_version;
- audit_event_id.

Warnings or confidence scores MUST NOT override DENY or REQUIRE_REVIEW. No default APPROVE on timeout, exception, partial response or unknown enum.

## 8. RiskApprovalCapability v1

### 8.1 Required claims

| Claim | Meaning |
|---|---|
| capability_schema_version | Approval capability schema version |
| approval_id | Unique immutable approval identifier |
| issuer | Trusted Risk Engine identity/key ID |
| audience | Exact Execution/Command Coordinator service audience |
| command_id | Exact NEXUS command ID |
| command_digest | Digest recomputed from canonical command |
| command_type | Authorized operation type |
| environment | PAPER/SANDBOX/LIVE exact scope |
| account_ref | Exact account/subaccount |
| venue_id / market_type | Exact venue and market scope |
| instrument_id / venue_instrument_id | Exact instrument scope |
| instrument_spec_version | Approved immutable spec version |
| policy_bundle_id/version | Exact risk policy version |
| exposure_snapshot_id/version | Exposure state used for approval |
| valuation_input_vector_id/version | Exact immutable mark/index/FX/fee/collateral input vector used by the decision |
| reservation_id/version | Durable reservation binding and persisted valuation-vector reference when required |
| halt_epoch | Halt generation observed at approval |
| issued_at / expires_at | Short-lived authorization interval |
| nonce | Cryptographically strong unique value |
| evaluation_id | Risk evaluation lineage |
| signature/key_id | Verifiable signature and key identifier |

A capability MUST NOT contain exchange API keys, reusable venue signatures or broad permissions such as “trade any instrument on this account”.

### 8.2 Execution-side preflight validation (non-authorizing)

Before handing a persisted command/attempt reference to Trusted Egress, Execution MUST independently verify:
1. signature and trusted issuer/key status using public verification material only;
2. audience matches the configured Execution service;
3. command ID and recomputed digest match byte-for-byte;
4. command type, environment, account, venue, market and instrument match;
5. instrument spec and policy versions remain permitted;
6. approval is not expired and clock uncertainty is within the configured bound;
7. nonce/approval has not already been consumed;
8. reservation is active and bound to this command;
9. valuation_input_vector_id/version matches the signed capability and durable reservation;
10. the exact StateEvidenceVector/FreshnessPolicy and RecoveryBarrier references are present and compatible with the requested operation class;
11. the observed halt epoch is current at preflight time and the scope is not reported halted;
12. command/outbox payload being handed to Egress is exactly the approved canonical payload.

Any failed check rejects the attempt and records a stable reason code. A valid signature alone is insufficient.

These checks are preflight and defense in depth. They do not authorize a venue-side effect and cannot guarantee that state remains unchanged after the check. Execution MUST NOT hold venue credentials or a direct venue network route. It submits an immutable command/attempt reference to Trusted Egress; it does not open the venue socket.

### 8.2.1 Trusted Egress final send-authorization gate

Immediately before socket initiation, Trusted Egress MUST independently reload and validate the persisted command, consumed Risk approval, active reservation, bound StateEvidenceVector and ValuationInputVector, source-watermark/correction manifest, venue eligibility revision, current halt generation, dispatcher/egress fence generation and exact attempt identity. It MUST NOT trust Execution's earlier preflight result as the final authorization.

The final validation and one-use EgressBoundaryAuthorization commit occur in a short attempt-scoped transaction. This commit is the sole send-authorization linearization point and MUST serialize against the same authoritative halt-state generation as a halt transition. Only Trusted Egress may initiate the venue socket write; no queue hop, remote source fetch or unbounded asynchronous preparation may occur between the final gate and socket initiation.

If the halt transition commits first, Egress denies the attempt. If the final gate commits first, the attempt is in-flight and remains potentially sent; the reservation is retained and the attempt is reconciled. The Egress boundary MUST NOT acknowledge the newer HALTED epoch while that pre-halt authorized attempt could still resume and initiate a socket write, unless its sender is positively fenced. See NX-IF-005 and NX-REF-EXEC-002.

The logical owner and sole writer of `EgressBoundaryAuthorization` is the Halt/Egress Gate Coordinator (HEGC) defined by NX-IF-005 §5.2.2. Trusted Egress requests a one-use attempt-scoped grant from HEGC and MUST NOT write or mutate halt-state / gate-authorization records directly. Before socket initiation it must durably consume the grant through HEGC's `ConsumeEgressGrant` transition; only a positive consume response permits one socket-write attempt. An indeterminate consume response is not retried as a new attempt and cannot authorize a send. HEGC serializes the final gate with the authoritative halt epoch. If HEGC or its authoritative store is unavailable, Egress denies the send. The grant binds command digest, reservation, attempt, halt epoch, eligibility revision, StateEvidenceVector, ValuationInputVector, dispatcher generation and Egress workload identity; that identity includes a distinct authenticated database principal for the active process generation, immutable artifact digest and environment; a shared server-side pooler identity is disallowed. It is not a replacement RiskApprovalCapability.

HEGC grant issuance is idempotent on the stable `attempt_id`: retrying the exact same request returns the same persisted grant/reference, never a second authorization. Reusing the attempt ID with a different command digest, reservation, evidence version, halt epoch, eligibility revision or Egress identity MUST conflict. If the HEGC response is ambiguous after commit, Egress resolves the result by the same attempt ID against the authoritative store; it MUST NOT create a new attempt or release/reacquire the reservation to work around uncertainty. A gate-committed attempt remains in-flight until socket initiation is observed or its sender is positively fenced. HEGC performs grant issuance on the authoritative primary in the same logical PostgreSQL database as gate-critical source records at SERIALIZABLE isolation. The HEGC runtime principal is EXECUTE-only and has no direct source SELECT or control-table DML. One reviewed SECURITY DEFINER AuthorizeEgressAttempt entrypoint performs the complete validation read set and grant write after acquiring the common guard first. Its NOLOGIN definer owner has SELECT only on the exact source records and write only to HEGC control state; caller authorization uses a distinct authenticated session_user per workload. All writers that can invalidate those records must participate in the same SERIALIZABLE protocol or a proven shared version/CAS guard; stale replicas and weaker bypass writers are prohibited. HEGC retries the entire transaction on 40001/40P01 within a finite budget and resolves unknown commit by the same attempt ID. Egress consumes the grant through a one-use HEGC operation and never writes the grant record directly. The persisted attempt moves GATE_COMMITTED → GRANT_CONSUMED → SOCKET_INITIATED, or to SENDER_FENCED_UNKNOWN when isolated without a trusted initiation report. Egress MUST NOT invoke the socket before positive grant-consumption acknowledgement. An ambiguous consume result is read by the same attempt ID; it cannot be retried as a second permit or replacement send. PostgreSQL SERIALIZABLE alone does not establish wall-clock commit ordering for overlapping source writers; the final gate also requires an enforced common per-scope generation/guard updated atomically by HEGC and every invalidating source writer before their respective reads/mutations. If that guard or its bypass prevention cannot be proven, HEGC denies the grant (NX-RESEARCH-012 §4.2). The HEGC gate-validation guard is distinct from the Risk-owned scope-state guard used for exposure/reservation aggregation; sharing rows is permitted only if the full HEGC validation read set and every invalidating writer are proven to participate atomically, with database-boundary bypass prevention. The G1 SECURITY DEFINER candidate must authorize a dedicated authenticated service principal (session_user), not current_user inside the definer context or a caller-supplied identity; shared database logins, SET ROLE impersonation and untrusted custom-GUC identity are disqualifying unless a separately reviewed identity-preserving design is proven. The guard API must prove complete affected-scope membership under the root/account guard, not trust a caller-supplied scope list. The guard is acquired as the first data statement after BEGIN and transaction-isolation/session settings, before any protected read/write; the account/root guard is first and child scope guards follow canonical UUID-byte order. If a lock wait leaves the transaction snapshot stale, abort and restart the whole transaction. Scope membership completeness is checked against the authoritative scope-config version after the root guard is held. Direct DML/advisory-lock bypass is prohibited.

### 8.3 Single-use consumption and crash handling

Approval consumption MUST be durable and atomic with the transition that makes the command eligible for dispatch. The same approval cannot authorize two commands or two independent dispatch records.

The protocol MUST distinguish:
- NOT_CONSUMED;
- CONSUMED_FOR_DISPATCH;
- DISPATCH_OUTCOME_KNOWN;
- DISPATCH_OUTCOME_UNKNOWN;
- INVALIDATED;
- EXPIRED.

If the process crashes after durable consumption but before it is known whether the venue received the request, the command enters the ADR-002 ambiguous-outcome path. It MUST NOT mint or reuse a new approval to blindly resend. Recovery requires authoritative evidence or a new command/evaluation after the previous outcome is resolved.

## 9. Invalidation rules

Approval is invalid if any of the following occurs before dispatch:
- canonical command digest changes;
- command schema major version changes;
- account, environment, venue, market type or instrument changes;
- instrument spec version changes incompatibly;
- policy version changes in a material way;
- exposure snapshot/reservation becomes stale, released, consumed by another command or invalidated;
- the bound valuation input vector is corrected/revoked, falls outside source-specific freshness/uncertainty/drift bounds or fails a policy that requires a newer/latest snapshot; a newer monotonic tick alone does not invalidate a still-valid bound vector;
- halt epoch advances or scope is halted;
- approval expires or issuer key is revoked/disabled;
- required account/market/reconciliation evidence falls outside policy freshness bounds;
- command is canceled, superseded or quarantined.

No automatic extension of expiry is allowed. Re-evaluation creates a new decision and, if approved, a new capability.

## 10. Stable reason-code families

Initial reason-code namespaces (exact catalogue to be versioned):
- SCHEMA_* — malformed/unknown schema or field;
- CANONICALIZATION_* — digest/canonical representation mismatch;
- IDENTITY_* — caller, account or scope mismatch;
- INSTRUMENT_* — unsupported instrument or spec mismatch;
- VENUE_CAPABILITY_* — unsupported order/position semantics;
- POLICY_* — hard limit, unconfigured policy or policy version mismatch;
- EXPOSURE_* — limit breach, unknown exposure or stale snapshot;
- RESERVATION_* — missing, expired, duplicated or conflicting reservation;
- DATA_QUALITY_* — stale, invalid, unsynchronized or incomplete evidence;
- RECONCILIATION_* — unresolved account/order/ledger discrepancy;
- HALT_* — active halt or stale halt epoch;
- APPROVAL_* — invalid signature, expired, consumed, revoked or audience mismatch;
- INTERNAL_* — Risk/Execution integrity failure; fail closed.

Reason codes are machine-stable; human-readable explanations may evolve independently.

## 11. Security and trust requirements

- Risk approval signing keys are separate from exchange signing keys.
- Approval signing key material is isolated; ordinary services cannot export it.
- Execution holds only public verification material or a constrained verification interface.
- Key rotation includes key ID, activation/retirement windows and revocation handling.
- Signature verification MUST be constant-time where applicable and use vetted libraries.
- Approval claims are integrity-protected; sensitive account identifiers are opaque references.
- Logs record IDs, digests, versions and reason codes, never secrets or raw signatures unless secure evidence policy explicitly requires protected retention.
- AI and Strategy have no permission to issue or consume approval capabilities.
- Operator-originated commands require authenticated actor identity, role and audit context; privileged scopes may require dual control per owner policy.

G1 capability-signature baseline is COSE_Sign1 with the fully specified COSE Ed25519 algorithm identifier -19 (RFC 9864), selected in NX-ADR-008. The deprecated polymorphic EdDSA identifier -8 is rejected. Exact vetted library/version, non-exportable key custody provider, key ceremony, rotation/revocation operations and jurisdictional/security approval remain open. No custom cryptography.

## 12. Contract state transitions

`PROPOSED → NORMALIZED → VALIDATED → RISK_EVALUATED`

Risk evaluation branches:
- `RISK_EVALUATED → DENIED`
- `RISK_EVALUATED → REVIEW_REQUIRED`
- `RISK_EVALUATED → APPROVED_WITH_RESERVATION`

Execution intake:
- `APPROVED_WITH_RESERVATION → PERSISTED`
- `PERSISTED → APPROVAL_CONSUMED`
- `APPROVAL_CONSUMED → DISPATCH_ELIGIBLE`
- `DISPATCH_ELIGIBLE → DISPATCHED`
- `DISPATCHED → ACKNOWLEDGED / REJECTED / OUTCOME_UNKNOWN`

This is a logical contract, not a substitute for the detailed command/order state machines in ТЗ-NX-004 and reservation state machine in WP-B. No transition may be inferred from a missing response.

## 13. Version compatibility and migration

- Major schema version changes are incompatible unless a formally reviewed adapter proves equivalence.
- Minor versions may add only explicitly optional, non-ambiguous fields; unknown fields remain rejected by v1 consumers unless negotiated by capability.
- Canonicalization version is independently identified and pinned.
- Strategy proposal schema, command schema and approval schema are separately versioned.
- Adapter upgrades MUST pass the same canonicalization and signature test vectors.
- Historical command bytes/digests and approval evidence are retained under audit retention policy; never recompute historical digest using a newer canonicalizer and overwrite the original.

## 14. Conformance and negative test matrix

Required test vectors before implementation approval:
1. Same semantic command from two supported language runtimes produces identical canonical bytes and digest.
2. Different quantity, price, side, account, instrument, TIF, trigger, reduce-only or position mode produces a different digest.
3. Null vs omitted required field rejects or produces explicitly distinct canonical representation.
4. Unknown field, duplicate key, exponent notation, NaN, Infinity, negative zero and malformed decimal reject.
5. Unicode, timestamp precision and key ordering vectors are deterministic.
6. Expired approval rejects at boundary and under configured clock-skew conditions.
7. Wrong audience, account, environment, venue, market or instrument rejects.
8. Modified payload with original approval rejects.
9. Wrong spec/policy/exposure version rejects.
10. Replayed nonce/approval and duplicate consumption reject.
11. Concurrent attempts to consume one approval allow at most one durable winner.
12. Crash before/after consumption follows explicit recovery path without blind resend.
13. Halt epoch change between approval and dispatch rejects.
14. Revoked signing key rejects according to revocation policy.
15. Unsupported venue capability and ambiguous reduce/close semantics reject.
16. AI/Strategy caller cannot mint, mutate or consume approval.
17. Risk timeout, signer outage, partial response or unknown decision enum never becomes APPROVE.
18. COSE_Sign1 accepts only the untagged embedded-payload four-element profile with protected alg=-19 and bounded kid; tag 18, detached payload, extra headers, non-empty unprotected map and duplicate/colliding labels reject.
19. Token-supplied kid/alg/issuer/audience cannot authorize or trigger remote key discovery before signature verification; ambiguous local key resolution fails closed.
20. Execution never receives private Ed25519 key material; wrong COSE key type/curve, key/signature length or algorithm mismatch rejects.
21. Missing/stale/incomplete Risk valuation evidence manifest, source watermark gap, correction/revocation or unconfigured freshness/drift policy denies dispatch; Egress makes no remote source-service call and never rebinds the signed vector.
22. A newer market-data tick alone does not invalidate an admissible immutable valuation vector unless the configured policy explicitly requires latest; the signed valuation_input_vector_id/version remains unchanged.

Golden vectors MUST include canonical input, expected canonical bytes, digest algorithm/version and expected digest. Vectors are not considered verified until executed in the selected implementation runtimes.

## 15. Acceptance criteria

- [ ] One versioned canonical command schema is accepted by Strategy/Command Coordinator/Risk/Execution owners.
- [ ] Field-level CREATE/AMEND/CANCEL/CLOSE/REDUCE_ONLY/CANCEL_ALL matrix is complete.
- [ ] Canonicalization and digest standard are selected, pinned and backed by cross-language golden vectors.
- [ ] Approval capability schema, issuer/audience, signature and key lifecycle are approved by Security.
- [ ] Execution validation checklist is normative and independently testable.
- [ ] One-time consumption and crash behavior are integrated with WP-B reservation and WP-C outbox design.
- [ ] Spec/policy/state/halt epoch invalidation semantics are accepted.
- [ ] Stable reason-code catalogue and audit lineage are approved.
- [ ] Negative conformance tests cover all critical rejection paths.
- [ ] Owner approves exact initial environment and operating scope before implementation.

## 16. Open owner decisions

1. Initial venue/account mode and supported command types for v1.
2. Exact COSE/Ed25519 implementation library, non-exportable key custody provider, key ceremony and rotation/revocation operations.
3. Exact deterministic-CBOR implementation/library version and cross-language golden vectors for the selected SHA-256 domain-separated digest.
4. Maximum approval lifetime and clock-skew tolerance.
5. Internal account-reference and operator identity model.
6. Whether v1 supports only one venue/account per command (recommended) or multi-leg atomic intents (defer unless required).
7. Initial order types and explicit venue defaults to prohibit.
8. Required operator dual-control actions and audit retention.

No risk limits, approval lifetimes, cryptographic algorithm or venue capabilities are invented as accepted project decisions. Until these are decided and implemented, live risk-increasing activity remains unconfigured and blocked.

## 17. Dependencies and next work

- WP-B must define durable reservation binding, concurrent exposure versioning, fencing and recovery.
- WP-C must define atomic persistence of command, approval consumption and outbox plus event handoff.
- WP-D must define StateEvidenceVector and freshness semantics referenced by RiskEvaluationRequest.
- WP-E must define halt epoch authority and emergency command classes.
- ТЗ-NX-003, ТЗ-NX-004 and ТЗ-NX-005 must reference this contract rather than maintaining competing field definitions.

## 18. Verification status

This document is a proposed interface design artifact only.

Verified in this documentation task:
- relevant source specifications and ADRs were fetched from `docs/project-foundation`;
- this contract is linked to the existing 12-finding cross-specification review.

Not verified:
- implementation, schemas, serialization, signatures or cryptographic configuration;
- conformance/golden tests, CI, builds, runtime, latency or failure behavior;
- venue capability support for any command class;
- owner acceptance or authorization for live operation.

No code, exchange connection, credentials, order placement, risk-limit change, PR merge or default-branch change was performed.


## WP-D evidence binding

RiskApprovalCapability MUST reference the immutable StateEvidenceVector ID/version and canonical digest defined by [NX-IF-004](NX-IF-004-state-evidence-freshness-recovery-barrier-contract.md), together with the EvidenceRequirementSet/FreshnessPolicy version used for evaluation. It MUST also bind the exact immutable `valuation_input_vector_id/version` defined by NX-IF-002. Trusted Egress performs the final compatibility check at its attempt-scoped send-authorization gate immediately before initiating the venue socket write. A source-generation change, sequence gap/regression, correction/revocation, completeness or quality deterioration, incompatible spec/policy change, exposure/reservation change, halt-epoch advance or source-freshness/drift-policy failure invalidates the capability. A monotonic newer market-data watermark or tick alone does NOT automatically invalidate it when the exact bound immutable valuation-input vector remains within its approved source-specific freshness/uncertainty/drift window; a source policy may explicitly require the latest version. The signed valuation_input_vector_id/version is never silently rebound. Trusted Egress validates the exact bound vector against the authoritative persisted Risk evidence manifest and latest consumed source-watermark/correction status; it MUST NOT call market/FX/fee/collateral source services or fetch replacement values on the dispatch path. Missing, stale, incomplete or unverifiable manifest denies send. Approval MUST NOT be rebound in place; Risk must re-evaluate and issue a new capability. This is a proposed cross-contract requirement, not an implemented behavior.


## WP-E emergency command authorization

The command types already enumerated by this contract MUST use the operation-class policy and emergency authorization rules in [NX-IF-005](NX-IF-005-emergency-operations-halt-risk-reduction-contract.md). CANCEL, CLOSE, REDUCE_ONLY and CANCEL_ALL are not implicit bypasses and are not presumed risk-reducing. Every emergency command remains a separate immutable CanonicalTradeCommand bound to its exact payload digest, account/scope, current halt epoch, target-set digest where applicable, instrument-spec version, StateEvidenceVector, RecoveryBarrier and policy. A halt activation is a control-plane action and does not mint an order approval. Resume requires privileged authorization and cannot be represented as a trade command.


## G1 technical baseline alignment — NX-ADR-008

The delegated G1 baseline is RFC 8949 restricted deterministic CBOR for canonical command bytes, SHA-256 with a fixed NEXUS command-domain separator for the digest, and COSE_Sign1 with fully specified COSE Ed25519 algorithm identifier -19 (RFC 9864) for RiskApprovalCapability. This is a technical design selection only. It does not select a key custody provider, authorize a signer/runtime, or close production Security/jurisdictional review. See [NX-ADR-008](NX-ADR-008-g1-technical-baseline-storage-and-capability-signing.md).

The exact COSE application wire profile is the untagged, embedded-payload four-element COSE_Sign1 array; protected header contains only alg=-19 and a 1–64-byte kid; unprotected map is empty; payload is one NEXUS restricted deterministic-CBOR capability map. Preserve the exact received protected-header and payload bytes and use RFC 9052 §9 deterministic Sig_structure encoding. Token-supplied kid/alg/issuer/audience are untrusted until signature verification; candidate key lookup is bounded to the local versioned registry and MUST NOT dereference token-supplied URLs. Execution receives public OKP/Ed25519 verification material only; private signing material remains inside the Risk signer boundary.



COSE verification MUST reject the deprecated polymorphic algorithm identifier -8, Ed448, non-OKP keys, non-Ed25519 curves, algorithm/key mismatch and algorithm substitution. A protected kid is only a lookup hint; resolve the signing key against signed issuer, algorithm, purpose, validity/revocation state and registry generation, requiring exactly one eligible key. See NX-ADR-008 and RFC 9864.
