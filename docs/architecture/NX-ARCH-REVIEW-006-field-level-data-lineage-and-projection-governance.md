# NX-ARCH-REVIEW-006 — Field-Level Data Lineage & Projection Governance

**Date:** 2026-11-14  
**Status:** SOURCE-GROUNDED DESIGN REVIEW COMPLETE — field classifications are proposed; retention/legal basis and projection contracts remain OPEN  
**Scope:** NX-IF-001..005, NX-SEC-001, NX-ARCH-007..009 and NX-ARCH-REVIEW-004  
**Related:** NX-ARCH-REVIEW-003/004/005, NX-OWNER-DECISIONS-001, NX-ADR-008

## 1. Purpose and method

NX-ARCH-REVIEW-004 identified that the current interface set is a protected execution/accounting/recovery/control-plane contract set, not a general-purpose module data API. It also recorded a source-grounded data inventory but did not classify individual fields or define projection lineage.

This review reads the actual field tables and object definitions in NX-IF-001..005 and the asset/trust-boundary inventory in NX-SEC-001. It groups only fields explicitly present in those sources. It does not invent journal-leg, profile, billing, analytics or module API fields where no canonical contract exists.

The classifications below are **proposed engineering defaults**, not owner-approved data policy, legal classification or a statement that the field is currently persisted. The owning domain remains authoritative for the source field and any projection derived from it.

## 2. Classification policy

Use the NX-ARCH-009 classification vocabulary:

| Class | Meaning | Default access |
|---|---|---|
| PUBLIC | Public market data and public reference material | Read only through approved contract |
| INTERNAL | Platform health and non-sensitive operational metadata | Minimum necessary read |
| PERSONAL | Profile, preferences and learning progress | Self/consent-scoped only |
| FINANCIAL_RESTRICTED | Balances, positions, order/fill history, Ledger and Risk projections | Deny by default; only separately approved read models, never raw authority |
| SECRET | API keys, signing keys, payment credentials and identity-provider secrets | No optional-module access |

Classification applies to **fields and combinations**, not merely tables. An otherwise public `venue_id` or `instrument_id` becomes FINANCIAL_RESTRICTED when joined to an account, command, order, fill, position or activity timestamp. Opaque identifiers are not automatically non-sensitive: `account_ref`, `raw_evidence_ref` and `command_id` can be linkable.

Derived reports inherit the most restrictive source classification unless a documented minimization/declassification process is approved by the source owner. A digest or opaque pointer does not make the underlying record public.

## 3. Source-grounded field inventory

### 3.1 NX-IF-001 — intent, command, decision and approval

| Source object / exact fields | Accountable source owner | Proposed classification | Projection disposition |
|---|---|---|---|
| TradeIntent: `intent_id`, `intent_schema_version`, `idempotency_key`, declared idempotency scope, `origin`, `strategy_artifact_id` and immutable version, `decision_context_digest`, `created_at`, `not_after` | Strategy / authorized command origin under ТЗ-NX-003 | INTERNAL for schema/origin and opaque lineage; PERSONAL/INTERNAL for strategy artifact reference; FINANCIAL_RESTRICTED for target/evidence references when tied to an account or trade | No direct module read. Strategy owner may expose only its own artifact metadata through a future Strategy contract |
| TradeIntent: `target`, `evidence_refs` | Strategy proposal; evidence remains owned by source domains | FINANCIAL_RESTRICTED where target/evidence describes account exposure, market/account snapshot or intended trade | Do not copy raw evidence into Analytics, Notifications or Learning; resolve references through source-owner APIs |
| CanonicalTradeCommand identity/scope: `schema_id`, `schema_version`, `nexus_command_id`, `command_type`, `environment`, `origin`, `intent_id`, `parent_command_id`, `idempotency_key`, `idempotency_scope`, `account_ref`, `venue_id`, `market_type`, `instrument_id`, `venue_instrument_id`, `instrument_spec_version` | ТЗ-NX-004 command intake / canonical command owner | INTERNAL for schema/version/type; FINANCIAL_RESTRICTED for account-linked identifiers, environment, command lineage and venue/instrument linkage | Never expose raw command envelope to optional modules. A minimized status view may expose non-reusable IDs only after user/resource authorization |
| CanonicalTradeCommand execution parameters: `side`, `position_side`, `order_type`, `quantity`, `price`, `trigger_price`, `trigger_reference`, `time_in_force`, `reduce_only`, `close_position`, `post_only`, `position_mode`, `margin_mode`, `price_protection / execution flags` | ТЗ-NX-004; venue semantics remain adapter-evidenced | FINANCIAL_RESTRICTED | No optional-module raw access. Portfolio may receive only approved report fields; Analytics only minimized source-owner projections |
| CanonicalTradeCommand target/time/control: `target_order_ref`, `target_venue_order_id`, `created_at`, `not_after`, `halt_epoch`, `correlation_id`, `causation_id`, `extensions` | ТЗ-NX-004; halt epoch from control plane | FINANCIAL_RESTRICTED for target/order/time linkage; INTERNAL for correlation/control metadata; `extensions` is empty in v1 and arbitrary keys are forbidden | No raw exposure to optional modules; do not leak correlation or control internals in user-facing reports |
| RiskDecision: `decision_id`, `command_id`, recomputed `command_digest`, decision enum, `reason_codes`, diagnostic references, `evaluated_at`, `decision_deadline`, `policy_bundle_id/version`, `instrument_spec_version`, `exposure_snapshot_id/version`, `state_evidence_ref/version`, `halt_epoch`, `reservation_id/version`, `evaluation_engine_version`, `audit_event_id` | Risk / ТЗ-NX-005 | INTERNAL for engine/version/reason metadata; FINANCIAL_RESTRICTED for command, exposure, reservation and account linkage | No optional-module access to full decision object. User-facing explanations require a separately approved reason-code projection |
| RiskApprovalCapability claims: `capability_schema_version`, `approval_id`, `issuer`, `audience`, `command_id`, `command_digest`, `command_type`, `environment`, `account_ref`, `venue_id`, `market_type`, `instrument_id`, `venue_instrument_id`, `instrument_spec_version`, `policy_bundle_id/version`, `exposure_snapshot_id/version`, `reservation_id/version`, `halt_epoch`, `issued_at`, `expires_at`, `nonce`, `evaluation_id`, `signature/key_id` | Risk signing authority / ТЗ-NX-005 | INTERNAL security metadata plus FINANCIAL_RESTRICTED command/account scope; nonce and approval evidence are replay-sensitive; signature is integrity evidence, not a secret | **Never expose the capability, signature, nonce or full claims to optional modules or clients.** It is a one-use execution authorization, not a report object. Private signing key remains SECRET and Risk-owned |

### 3.2 NX-IF-002 — Risk scope, exposure and reservation

| Source object / exact fields | Accountable source owner | Proposed classification | Projection disposition |
|---|---|---|---|
| RiskScope: `risk_scope_id`, `scope_type`, `account_id`, `subaccount_id`, `venue_id`, market/account mode, `parent_scope_id`, aggregation membership, `scope_config_version`, `policy_version` | Risk | FINANCIAL_RESTRICTED when scope identifies a real account/portfolio; INTERNAL for policy/config version metadata | No direct store access. Only a source-owner-approved scoped projection |
| ExposureItem identity/lineage: `exposure_item_id`, `root_lineage_id`, `source_type`, `source_identity`, `account_id`, `venue_id`, market type, canonical instrument identity, `instrument_spec_version`, `owner_bucket`, `bucket_version` | Risk owns bucket state; source identity facts originate in Execution/Ledger/venue reconciliation | FINANCIAL_RESTRICTED; bucket and source metadata additionally INTERNAL | No optional-module raw access |
| ExposureItem economics: exact remaining quantity/notional/margin/collateral dimensions, units/currency, side, position side/index, order semantics, reduce-only/close flags, valuation evidence/quality | Risk aggregates; Ledger/Execution/venue remain source owners for their facts | FINANCIAL_RESTRICTED | Only a separately approved minimized portfolio/report projection; Analytics must not query raw exposure items |
| ExposureItem provenance/state: source timestamps, receive/processing timestamps, source watermarks, correlation IDs, predecessor/successor item IDs, raw evidence references, status, reason codes, `last_transition_id` | Risk + originating source owner | FINANCIAL_RESTRICTED when linked to an account/trade; INTERNAL for non-sensitive transition metadata | Raw evidence references are not dereference permissions. No module access without source-owner authorization |
| ExposureSnapshot: schema version, snapshot ID, risk scope/parent-scope versions, `snapshot_version`, `fencing_token`, creation/as-of time, source event watermarks, projection offsets, account/venue/spec/policy versions, health/quality/completeness, bucket totals/item references, unknowns/discrepancies/quarantined identities/conservative bounds, valuation inputs/units/currency/calculation version, previous snapshot reference, transition/event range | Risk; source domains retain original facts | FINANCIAL_RESTRICTED for totals/items/valuation and account-linked metadata; INTERNAL for schema/calculation/control metadata | Only source-owner-approved report projections. Do not expose unknown exposure details, raw item references or fencing tokens to optional modules |
| RiskReservation: `reservation_id`, schema version, `reservation_request_id`, `risk_scope_id(s)`, scope config versions, command ID/digest, account/venue/market/instrument/spec, policy version, exposure snapshot ID/version, reserved dimensions (quantity/notional/margin/fee/cost buffer/collateral impact), units/currency, valuation assumptions/evidence/version, lifecycle state/version/fencing token, created/updated/expiry timestamps/policy, actor/service, reason codes, correlation lineage, audit evidence, consumed/remaining amounts, linked fill/order/exposure IDs, release evidence/reconciliation references | Risk | FINANCIAL_RESTRICTED; actor/audit metadata additionally PERSONAL/INTERNAL as applicable | No optional-module access to reservation records or release evidence. Reservation state is execution authority, not an analytics balance |

### 3.3 NX-IF-003 — execution facts, raw evidence and Ledger

| Source object / exact fields | Accountable source owner | Proposed classification | Projection disposition |
|---|---|---|---|
| Raw venue order/fill/fee payload, retrieval metadata, raw bytes/reference, digest, endpoint/channel, adapter version and retrieval context | Adapter evidence store / Execution; source evidence provenance remains with venue adapter | FINANCIAL_RESTRICTED; any credential/token accidentally present is SECRET and must be redacted/isolated | No optional-module access to raw payloads or raw evidence stores. Raw evidence reference is not a grant |
| ExecutionEvent envelope: `schema_name`, `schema_version`, `event_id`, `event_type`, `execution_id`, `venue`, `environment`, `account_id`, `subaccount_id`, `market_type`, `native_instrument_id`, `internal_instrument_id`, `instrument_spec_version` | Execution | INTERNAL for schema/version/type; FINANCIAL_RESTRICTED for venue/account/instrument/execution linkage | No raw event stream to optional modules |
| ExecutionEvent order/fill economics: `venue_order_id`, `client_order_id`, `venue_execution_id`, `venue_trade_id`, `side`, `position_side`, `price`, `quantity`, `contract_count`, `multiplier`, `price_currency`, `quantity_unit`, `settlement_currency`, `fee_amount`, `fee_currency`, `fee_sign_convention`, `liquidity_role` | Execution; Ledger owns resulting accounting facts | FINANCIAL_RESTRICTED | Only approved financial read models may expose minimized fields to an authenticated user |
| ExecutionEvent timing/provenance: `exchange_event_time`, `received_at`, `processed_at`, `source_channel`, `source_sequence`, `source_cursor`, `connection_generation`, `source_payload_digest`, `raw_evidence_ref`, `adapter_version`, `correction_of`, `correction_version`, `effective_time`, `strategy_lineage`, `command_id`, `risk_approval_id`, `reservation_id`, `normalization_version`, `deduplication_scope`, `quality` | Execution and source adapter; Risk/Ledger consume but do not rewrite | FINANCIAL_RESTRICTED when tied to account/fill; INTERNAL for transport/normalization metadata | No direct Analytics/Notifications exposure. Minimized projections may include approved event time and lineage aggregates only |
| Ledger: journal transaction, debit/credit postings, posting-rule version, balances, positions, cost basis and realized accounting projections | Ledger | FINANCIAL_RESTRICTED | The reviewed IF-003 contract does **not** enumerate a complete journal-leg field schema. Do not invent posting fields or expose raw journal tables. Portfolio projections require a separate Ledger-owned schema/contract |

### 3.4 NX-IF-004 — evidence, freshness and recovery

| Source object / exact fields | Accountable source owner | Proposed classification | Projection disposition |
|---|---|---|---|
| EvidenceScope: scope type, stable scope ID, parent scope IDs, venue/account/subaccount/market/instrument/channel identifiers, account/position mode, scope configuration and policy versions | Source owner for each evidence domain; WP-D composes | INTERNAL for generic scope metadata; FINANCIAL_RESTRICTED when account/order/position scoped | No direct source-vector or raw evidence access to optional modules |
| StateEvidenceVector: `schema_version`, `vector_id`, `vector_version`, `scope_id`, `scope_type`, parent-scope versions, `evaluated_at`, monotonic evaluation sequence, `consumer`, `operation_class`, requirement-policy version, source evidence entries, aggregate completeness/quality, missing/stale/contradictory/quarantined requirements, instrument-spec/risk-policy/projection/adapter/schema versions, previous vector reference, transition reason and correlation lineage | WP-D composition; each source owner remains authoritative for its evidence | INTERNAL / FINANCIAL_RESTRICTED depending on source scope and included lineage | No raw vector exposure. A minimized status projection may expose only approved health state and non-sensitive reason families |
| StateEvidenceVector source entry: source owner/component, venue/channel/endpoint, source event/receive/process/evaluation times, monotonic age, clock-quality/uncertainty, sequence range/cursor/journal offset/projection watermark/snapshot ID, connection generation, quality/transport/recovery/reconciliation state, completeness/coverage/pagination boundaries, raw evidence ref/digest, adapter/schema/normalization/calculation versions, instrument/policy versions, deduplication/correction lineage, last reconciliation ref, limitations/reason codes | Individual source owner | INTERNAL or FINANCIAL_RESTRICTED according to source; raw evidence pointers remain restricted | Never use the vector as a generic data lake or a substitute for source authorization |
| FreshnessPolicy: source type, scope, operation class, market/timeframe, maximum event/receive age, clock uncertainty, sequence/cursor continuity, snapshot/reconciliation age and completeness, accepted quality/recovery states, degraded modes/exclusions, unconfigured-threshold behavior, policy version/effective time/owner/approval/audit ref | Source owner and policy owner; Risk enforces for authorization | INTERNAL security/policy metadata | No optional-module policy mutation or direct access to operational thresholds |
| RecoveryCase: case ID/schema, affected scopes/parents, trigger source/event, reason codes/severity/detected time, last-known-good vectors/watermarks, invalidated versions, affected projections/approvals/reservations, stage/attempts/retry-policy version, evidence refs/discrepancies/operator actions, owner/assigned service/operator/correlation IDs, resolution criteria/proof/closure actor/time/final vector | Source owner opens/resolves; WP-D coordinates; Risk gates | INTERNAL / FINANCIAL_RESTRICTED; operator identity/incident evidence is also PERSONAL where applicable | No optional-module case mutation; any support view must be separately case-scoped and redacted |
| RecoveryBarrier: `barrier_id`, schema version, scope/parent versions, operation class, EvidenceRequirementSet/FreshnessPolicy versions, barrier generation/epoch/fencing token, required source domains and accepted watermarks/versions, recovery cases/reconciliation refs, stage/result/reason/last transition, created/evaluated times, evaluator identity/audit lineage | WP-D / Risk enforcement boundary; source owners provide evidence | INTERNAL security/control metadata plus FINANCIAL_RESTRICTED scope linkage | No optional module may publish, override or use a barrier as a reusable grant |

### 3.5 NX-IF-005 — halt and emergency-control data

| Source object / exact fields | Accountable source owner | Proposed classification | Projection disposition |
|---|---|---|---|
| HaltScope: scope type (GLOBAL_SYSTEM/PORTFOLIO/VENUE_ACCOUNT/ACCOUNT/SUBACCOUNT/VENUE/INSTRUMENT/STRATEGY), stable internal ID, parent IDs, configuration and policy versions | Control-plane / Risk owner; actual operator governance remains owner-controlled | INTERNAL; FINANCIAL_RESTRICTED when it identifies a real account or strategy incident | Optional modules may read only a minimized authorized status, never mutate scope |
| HaltState: schema version, halt event ID, monotonic `halt_epoch`, scope/parent epochs, state/transition version, trigger type/reason/severity/source evidence, actor identity/role/authentication/step-up evidence/request channel, effective time, acknowledgement/propagation watermarks, expiry/review metadata, invalidated approvals/queued commands/recovery cases, incident/EmergencyActionPlan/audit IDs | Control-plane / Risk; human actor identity from Identity & Access | INTERNAL security metadata; PERSONAL actor metadata; FINANCIAL_RESTRICTED affected-account linkage | No module may mutate or clear HaltState. Status views require redaction and subject/scope authorization |
| EmergencyActionPlan: triggers/scopes, allowed operations/target rules, required evidence/RecoveryBarrier/FreshnessPolicy versions, Risk-online/offline condition, instrument/account/position-mode/venue prerequisites, protective-order rules, quantity/notional/price/slippage/time bounds, rate-limit/retry, operator/dual-control, stop conditions/attempts/reconciliation, policy version/approval/effective time/digest/review date | Owner-approved control-plane policy; Risk/Execution enforce | INTERNAL security policy plus FINANCIAL_RESTRICTED operational parameters | No optional module access or mutation; no arbitrary emergency plan creation |
| EmergencyCommand: `incident_id`, `halt_epoch`, emergency plan ID/version, `target_set_id/version`, `operator_action_id`, actor identity, state-evidence vector ID/version, recovery barrier ID/generation, risk classification, RiskDecision, scoped authorization, reason code/deadline/correlation lineage | Execution command owner; Risk approves; control-plane supplies incident/plan | FINANCIAL_RESTRICTED and INTERNAL security metadata; actor identity is PERSONAL | No direct optional-module access; no client/AI dispatch or approval rights |

### 3.6 NX-SEC-001 — security assets

NX-SEC-001 names security assets but does not define their complete field schemas. The following classifications are grounded at asset level only:

- Exchange API keys, signing capability, identity-provider secrets, MFA factors, session tokens, private signing material and payment credentials: **SECRET**. No optional module, client, analytics service, log, support bundle or ordinary runtime may retrieve them.
- User identity, MFA/session metadata and operator identity: **PERSONAL**; authentication secrets/tokens are SECRET. Only minimal identity attributes may be exposed through an Identity-owned self-scope contract.
- Risk policies, limits, kill-switch state, approval authority and signer metadata: **INTERNAL security-sensitive**; when bound to an account/order, linked data is FINANCIAL_RESTRICTED.
- Order intents, outbox records, venue IDs, fills, balances, positions and Ledger: **FINANCIAL_RESTRICTED**.
- Public market data and public instrument reference data: PUBLIC at source; private stream/session health and account-linked observations are INTERNAL or FINANCIAL_RESTRICTED.
- Audit and incident evidence: INTERNAL / FINANCIAL_RESTRICTED / PERSONAL according to content; secrets and unnecessary raw payloads are prohibited.

No detailed credential schema, identity-provider field list or audit-record schema is invented here.

## 4. Projection and consumer policy

Existing NX-IF-001..005 do not authorize optional modules to read their stores. Future consumers must use domain-owned, minimized projections with a separate versioned interface contract.

| Consumer / capability | Allowed data class and scope | Explicitly prohibited |
|---|---|---|
| Analytics — `nexus.analytics.query` | INTERNAL/PERSONAL/FINANCIAL_RESTRICTED **approved projections only**; authenticated subject/resource scope; bounded query budget, timeout and cancellation | Raw Risk/ExposureSnapshot/Reservation stores, raw Ledger journal, raw ExecutionEvent stream, raw venue payloads, approval capabilities, arbitrary SQL, cross-account joins |
| Portfolio — `nexus.portfolio.report.generate` | FINANCIAL_RESTRICTED Ledger-owned report projection for the exact user-authorized v1 account/subaccount; source watermarks and freshness must accompany report output | Raw journal tables, direct Risk store access, other subjects/accounts, hidden unknowns, fabricated completeness, order mutation or approval authority |
| Notifications — `nexus.notification.publish` | Approved template/event summary to consented destination; minimal PERSONAL/INTERNAL fields | Arbitrary payloads, raw order/fill/ledger records, secret values, approval tokens, unbounded URLs or consent bypass |
| Strategy Lab | Own/authorized strategy artifact metadata and version only under a future Strategy contract | Raw credentials, Risk approvals, direct exposure store, raw account/ledger data or execution authority |
| Demo & Simulation | Server-assigned demo namespace and public/replay market data | Live account namespace, live orders, live ledger, private credentials or route to Trusted Egress |
| Learning | Authenticated user's own learning progress only | Trading history, financial data, entitlement mutation or other users' progress |
| Billing | Minimum subject-scoped usage aggregate and subscription-change intent only | Payment credentials, raw order/fill/account data, direct entitlement writes or trading permissions |
| Administration & Support | No initial generic capability; any future access must be time-limited, case-bound, approved and redacted | Standing support access to financial stores, secrets, signer, unrestricted export or production dispatch |

The v1 owner-approved account boundary remains one venue plus one dedicated account/subaccount. No multi-tenant, cross-venue or portfolio aggregation scope is assumed.

## 5. Mandatory projection lineage envelope

Every future derived projection or report must carry, at minimum, a separately defined lineage envelope. These are **requirements for a future contract**, not fields claimed to exist in the current IF schemas:

1. projection schema/version and accountable source owner;
2. exact source contract/object versions and source IDs/watermarks;
3. source scope and authorized subject/account scope;
4. transformation/calculation version and immutable configuration/policy references;
5. source freshness, completeness, reconciliation and quality result;
6. field allowlist, classification, minimization/declassification rule and approval reference;
7. creation/evaluation time with clock-quality semantics;
8. retention class, deletion/legal basis and audit reference;
9. correlation IDs and reproducible source lineage without copying raw source payloads.

A projection is invalidated when a material source watermark, schema, policy, instrument spec, calculation or authorization generation changes. A report must not present a precise total while hiding incomplete or unknown source coverage.

## 6. Retention, minimization and audit disposition

The reviewed source contracts do not establish numeric retention periods, deletion schedules or legal bases. These remain open; do not invent TTLs.

- Immutable command bytes/digests, approvals, execution facts, journal postings, corrections and audit references must preserve original lineage under a separately approved retention schedule. Never overwrite historical facts or recompute a historical digest with a newer canonicalizer.
- Raw venue evidence retention must be source/venue/legal-policy-specific. Store a digest/reference and access-controlled evidence object; do not duplicate raw payloads into analytics or notification stores.
- Derived projections must have explicit retention, deletion and rebuild policy. Deleting a projection must not delete source journal/audit evidence required for accounting or reconciliation.
- Personal identity/session metadata requires purpose limitation and minimization. Actual authentication factors/tokens remain SECRET and are never logged.
- Logs/traces may contain only allowlisted IDs, digests, versions and bounded reason codes. Never log credentials, private keys, session tokens, authorization headers, full RiskApprovalCapability objects or unrestricted raw financial payloads.
- A field-level declassification requires source-owner approval, documented purpose, input/output allowlist, transformation, residual re-identification analysis, retention and adversarial leakage tests. A role or module trust tier alone cannot declassify data.

## 7. Findings and required actions

| ID | Severity | Finding | Required action / gate |
|---|---|---|---|
| DATA-01 | CRITICAL | Existing IF contracts define protected objects, not reusable module read APIs | Keep optional modules off raw stores; require source-owned projection contracts |
| DATA-02 | HIGH | Exact Ledger journal-leg schema is not enumerated in NX-IF-003 | Ledger owner must author a separate journal schema before any projection/API work; do not infer debit/credit fields |
| DATA-03 | HIGH | Field classifications in this review are proposed, not accepted | Source owners and security must approve every field/combination before G0D acceptance |
| DATA-04 | HIGH | Account/order IDs and evidence references are linkable despite being opaque | Treat linkable references as restricted; authorization must cover dereference, not just identifier visibility |
| DATA-05 | HIGH | Derived Analytics/Portfolio outputs can leak raw source detail or hide unknown coverage | Define projection allowlists, lineage/watermark and explicit PARTIAL/UNKNOWN output semantics |
| DATA-06 | HIGH | Retention/legal basis and deletion/rebuild policy are not defined | Obtain jurisdictional/privacy/accounting review and approve retention schedule before G1/G2 |
| DATA-07 | HIGH | Audit/incident/operator records combine personal, security and financial metadata | Define field-level redaction, access, retention and independent audit custody |
| DATA-08 | MEDIUM | Support access is mentioned in governance but has no initial capability ID/contract | No generic support permission; if needed, propose a separate case-bound, dual-controlled contract |

## 8. Gate disposition

- **Design traceability:** complete for the source fields explicitly present in NX-IF-001..005 and NX-SEC-001.
- **Field-level classification:** proposed only; owner/security approval remains open.
- **Analytics/Portfolio projection APIs:** not defined or implemented; require source-owned schemas and negative tests.
- **Retention/legal basis:** open; no numeric TTL selected.
- **G0D/G1:** remain blocked on data owner approvals, exact projection schemas, field-level tests and actual storage/process/secret/network enforcement evidence.
- **G2/G3:** unchanged. No venue, live credential, production deployment or live-trading authority is implied.

No API, schema, database table, projection service, access policy, grant, runtime, dependency, credential or production integration was created by this review.

**Final disposition: FIELD INVENTORY AND PROJECTION GOVERNANCE DESIGN COMPLETE; ACCEPTANCE NOT GRANTED.**
