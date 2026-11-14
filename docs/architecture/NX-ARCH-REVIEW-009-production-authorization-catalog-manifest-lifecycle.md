# NX-ARCH-REVIEW-009 — Production Authorization-Catalog Manifest Lifecycle

**Status:** DESIGN REVIEW DRAFT; OWNER / SECURITY ACCEPTANCE OPEN  
**Date:** 2026-11-14  
**Scope:** NX-ARCH-REVIEW-008, NX-ADR-008, NX-RESEARCH-011/012, NX-SEC-001 and the PostgreSQL catalog-drift fixture.

## 1. Executive decision

The disposable PostgreSQL fixture demonstrates that a bounded catalog snapshot changes when selected privilege-boundary objects are mutated and returns to baseline after exact restoration. That is useful regression evidence, but it is not a production trust anchor.

This review defines a candidate lifecycle for an independently approved, signed production authorization-catalog manifest. It does not select a production schema, signer implementation, key custodian, immutable-storage provider, deployment controller or DBA operating model.

The production control must be fail-closed and externally anchored:

1. A reviewed migration release produces an exact expected catalog manifest for a named deployment profile and migration-set digest.
2. Independent authorized reviewers approve the manifest; approval is recorded outside the database being measured.
3. A dedicated signing authority signs the canonical manifest using the approved trust root.
4. A deployment gate obtains a consistent live catalog observation, validates signature/trust/revocation/freshness/context and compares the complete observed scope with the approved manifest.
5. Any missing, extra, changed, unclassified or unobservable item blocks readiness. No automatic privilege repair is performed by the gate.
6. A separate continuous drift detector and emergency reconciliation process cover changes after startup and out-of-band DBA/superuser activity.

A hash stored in the same database, a CI artifact, or a manifest signed by the deployment identity is not an independent trust anchor.

## 2. Threat model and security invariants

Threats include compromised application/runtime credentials, compromised migration credentials, accidental or malicious DBA/superuser changes, PUBLIC/default privilege expansion, role-membership escalation, ownership transfer, SECURITY DEFINER replacement, RLS/policy weakening, trusted-schema object injection, stale/rolled-back manifests, signer compromise and audit-store deletion.

Mandatory invariants:

- **I-1 Independent authority:** manifest approval, signing and immutable evidence custody are separate from the database principals being measured.
- **I-2 Exact context binding:** a manifest is valid only for its environment, deployment profile, cluster identity, database identity, schema scope, PostgreSQL compatibility and exact migration-set digest.
- **I-3 Complete bounded inventory:** the schema declares the complete object classes and namespaces in scope, including expected absence/deny rules. Unknown object classes or unobservable catalog fields fail closed.
- **I-4 Semantic identity:** objects are identified by stable semantic keys (qualified names, object kind, function/procedure identity argument types and relevant signatures), not bare OIDs. OIDs may be recorded as observations but are not portable identity.
- **I-5 Effective privilege evaluation:** compare role attributes, transitive membership/effective SET ROLE paths, ownership, ACLs, PUBLIC grants, default privileges, function security properties and RLS behavior—not merely explicit GRANT statements.
- **I-6 Freshness and anti-rollback:** manifest sequence, issuance/expiry, predecessor digest and revocation state are checked against an independent monotonic trust service or equivalent protected state.
- **I-7 No silent repair:** deployment verification reports and blocks; it never automatically grants, revokes, transfers ownership, disables roles or rewrites policies.
- **I-8 Post-startup coverage:** startup verification alone is insufficient. DDL/role/ACL change monitoring and an independently enforced response path are required for the running system.
- **I-9 Fail-closed observability:** permission errors, unsupported catalog versions, partial snapshots, timeouts, missing trust roots and unavailable revocation state are failures, not partial success.
- **I-10 Evidence custody:** signed manifest, approval record, observed report, comparison result, migration digest and deployment decision are retained in an append-only/immutable audit domain independent of the target database.

## 3. Candidate manifest schema

The following is a logical schema, not a committed wire-format implementation. Exact canonical CBOR field labels and integer assignments remain subject to NX-ADR-008 and cross-language conformance review.

| Field | Required content | Validation |
|---|---|---|
| manifest_type | Fixed domain identifier, e.g. nexus.postgres.authorization-catalog | Exact allow-listed value |
| schema_version | Positive manifest schema version | Unknown versions reject |
| manifest_id | Random immutable identifier | Unique in approval ledger |
| sequence | Monotonic approval sequence | Must exceed last accepted sequence |
| predecessor_digest | Previous approved manifest digest, or explicit genesis marker | Chain continuity checked |
| issued_at, not_before, expires_at | UTC issuance and validity interval | Bounded clock skew; expired/not-yet-valid reject |
| environment | Environment and deployment profile | Exact match |
| cluster_id, database_id | Independently provisioned stable identifiers | Exact match; not inferred solely from mutable DB metadata |
| postgres_compatibility | Supported server version range and required extensions | Exact qualified compatibility |
| migration_set_digest | Digest of ordered, immutable migration artifacts | Exact deployment input |
| scope | Explicit schemas, object classes, roles and exclusions | No wildcard expansion at verification time |
| inventory | Canonical expected objects and security-relevant properties | Complete inventory; unknowns reject |
| deny_rules | Forbidden principals, memberships, grants, owners, functions and object patterns | Evaluated against effective state |
| snapshot_profile | Versioned catalog-query and normalization profile | Exact verifier compatibility |
| approval_record_ref | Immutable external approval evidence reference | Resolvable and independently authenticated |
| signing_policy_id | Approved signing/trust policy version | Active and not revoked |

The manifest must include explicit expected-absence assertions for security-critical surfaces (for example, no unexpected LOGIN-capable definer owner, no PUBLIC EXECUTE on privileged entrypoints, no unreviewed trusted-schema functions, no unapproved membership path). Absence is a first-class assertion, not an omission from the file.

The observed report is a separate artifact. It records the manifest digest, verifier build digest, database identity, server version, observation interval, catalog-query profile, per-surface comparison results and any inability to observe. It must not contain secrets or credential material.

## 4. Canonicalization, digest and signature envelope

Candidate encoding is restricted deterministic CBOR as described by NX-ADR-008/NX-RESEARCH-011. The profile must define:

- definite-length items only; shortest integer/length encodings;
- deterministic map-key ordering and duplicate-key rejection;
- strict UTF-8 and a documented text normalization policy (prefer ASCII identifiers for protocol keys);
- no floats, tags, indefinite-length values or unknown critical fields;
- duplicate semantic object identities rejected before serialization;
- explicit null/absence semantics; no implicit defaults;
- canonical re-encoding equality on verification.

The manifest payload is domain-separated before hashing/signing. The exact domain string and byte construction must be frozen in a versioned profile; a candidate is NEXUS-AUTH-CATALOG-MANIFEST-v1 followed by a zero byte and canonical manifest bytes. Digest algorithm and signature suite must match the accepted ADR profile; the current candidate is SHA-256 and COSE_Sign1 Ed25519 (COSE alg=-19), with protected headers binding key ID, content type and critical profile identifiers.

The verifier must reject unprotected security-critical headers, algorithm substitution, unknown critical parameters, key-ID ambiguity, non-canonical payload bytes, wrong domain, wrong environment/context, revoked keys and signatures that do not verify under the active trust policy.

A digest detects change; it does not establish approval. A valid signature establishes only that a trusted key signed bytes; it does not prove that the manifest was correctly reviewed or that the measured catalog is safe. Both approval governance and technical comparison are mandatory.

## 5. Approval, signing and trust-root separation

Candidate roles are logically separate:

- **Manifest author:** generates the proposed expected inventory from reviewed migration artifacts; cannot approve or sign.
- **Architecture/security approvers:** review scope completeness, effective privilege semantics, deny rules and diffs; approval requires recorded independent identities and rationale.
- **Release authority:** binds the approved manifest to the exact migration-set digest and deployment context.
- **Signing service/key custodian:** signs only an immutable approved payload after verifying approval evidence; has no database login or migration capability.
- **Deployment verifier:** verifies but cannot create or approve manifests and has no database write privilege.
- **Audit custodian:** retains approvals, signatures, verifier reports and incident records; cannot alter the target database.

Threshold/multi-party approval, hardware-backed key custody, rotation, revocation, recovery and emergency signing policy remain open decisions. No single application runtime identity may author, approve, sign and deploy the same manifest.

## 6. Deployment-time gate protocol

The gate is a mandatory pre-readiness dependency, not an advisory health check:

1. Load the candidate manifest and approval evidence from independent protected storage.
2. Verify canonical bytes, schema version, signature, trust chain, key status, monotonic sequence, predecessor digest, validity interval and deployment-context binding.
3. Verify the exact migration artifact set and expected database/cluster identity.
4. Acquire a consistent catalog observation under a documented transaction/isolation and DDL-coordination strategy. If a coherent snapshot cannot be guaranteed, fail closed.
5. Query every declared catalog surface using a versioned verifier profile; detect missing, extra, changed and unobservable objects.
6. Evaluate effective role graph, ACL/default-ACL inheritance, ownership, SECURITY DEFINER properties, function configuration/search_path, RLS flags/policies and required object absence.
7. Compare canonical semantic records; produce a tamper-evident observation report.
8. Permit service readiness only on an exact approved match and a valid independent trust/revocation state.
9. Persist the decision and evidence outside the target database.

A startup snapshot has a time-of-check/time-of-use gap if a privileged actor can mutate the catalog immediately afterward. Therefore the production design must also define DDL authorization/fencing during the deployment window and continuous out-of-band drift detection after readiness. A database advisory lock alone does not constrain superusers or external control planes.

## 7. Drift response and emergency reconciliation

Unexpected drift is a security incident until classified:

- Immediately prevent new privileged authorization and new venue egress through an independently enforced control path.
- Preserve existing ambiguous attempts/reservations; do not blindly retry or erase in-flight state.
- Capture a fresh catalog observation, database/server identity, role graph, active sessions, DDL/audit events and deployment/migration evidence.
- Determine whether the change was approved, accidental, malicious or caused by a failed migration.
- Do not auto-revert. A blind REVOKE/ALTER may destroy legitimate recovery paths or conceal evidence.
- Prepare a reviewed corrective migration and a new manifest; require independent approval and signature.
- Reconcile active sessions separately. Role disable/revocation does not terminate established PostgreSQL sessions; connection-pool invalidation, backend termination and process/host/network fencing need distinct evidence.
- Resume only after catalog match, session/process fencing evidence, attempt reconciliation and explicit operator authorization.

Emergency bypass is not an informal override. It requires a pre-approved break-glass policy, strong operator authentication, dual control, time-bounded authority, immutable event capture and mandatory post-incident manifest reconciliation. Exact authority and response objectives are owner/security decisions.

## 8. Coverage and verifier conformance matrix

| Surface | Required semantic coverage | Negative cases |
|---|---|---|
| Roles | LOGIN/NOLOGIN, SUPERUSER, CREATEDB, CREATEROLE, REPLICATION, BYPASSRLS, connection limits and validity | Unexpected privileged attribute; login-capable definer owner |
| Membership | Full transitive graph, ADMIN/INHERIT/SET semantics and grantor | Indirect path to definer/superuser; unexpected SET ROLE |
| Schemas | Owner, CREATE/USAGE ACL, trusted namespace classification | PUBLIC CREATE/USAGE; unapproved owner |
| Relations/sequences | Owner, ACL, RLS/FORCE RLS, partition/sequence coverage | Direct DML bypass; unexpected owner/grant |
| RLS | Complete policy set, command, roles, USING/WITH CHECK, permissive/restrictive composition | Missing restrictive policy; role widening; policy subquery leakage |
| Functions/procedures | Schema/name/identity args, language, owner, SECURITY mode, volatility, leakproof/strict flags, config/search_path, ACL | SECURITY INVOKER substitution; overload; PUBLIC EXECUTE; unsafe language |
| Default privileges | Per grantor/schema/object type, owner and effective inherited result | Future function/table receives unintended grant |
| Extensions/languages | Installed extension/version/schema/owner and trusted status; procedural languages | Unapproved extension, version drift or untrusted language |
| Event triggers / DDL hooks | Inventory, owner, enabled state and function binding | Disabled/missing audit hook; unexpected trigger |
| Database/cluster settings | Security-relevant settings and authentication/TLS policy where observable | Weakened setting; unavailable source |
| External control plane | Role provisioning, cloud IAM, secret rotation, pooler and network policy | DB catalog matches but external principal/route remains stale |

The current fixture covers only a subset of roles, memberships, schemas/relations, functions, RLS/policies and default privileges. It does not yet cover all rows above. The production verifier must declare its exact PostgreSQL major-version support and fail closed on unsupported catalog semantics.

## 9. Required verification before implementation acceptance

- Schema validation and canonical-byte golden vectors, including duplicate keys, non-shortest encodings, unknown critical fields and semantic duplicate identities.
- Cross-language Rust/Python encode/decode/sign/verify vectors with byte-for-byte equality.
- Signature negative tests: wrong key, revoked key, wrong context/domain, algorithm substitution, modified payload, malformed protected headers and stale sequence/rollback.
- Manifest approval tests: author cannot approve/sign; signer rejects unapproved or changed payload; reviewer identity and evidence are independently auditable.
- Catalog mutation matrix for every supported object class, including mutate/restore and unexpected-object insertion.
- Effective role-graph and default-privilege tests, not only direct ACL text comparison.
- Concurrent DDL/change during observation; prove snapshot consistency or deterministic fail-closed behavior.
- Deployment TOCTOU test: mutation after successful comparison must be blocked/detected before privileged service readiness or egress.
- Post-startup drift detection and emergency halt/reconciliation tests.
- Restore/PITR test proving manifest sequence, revocation state and audit custody cannot roll back with the application database.
- Independent security review of trust roots, signer, verifier, audit storage, DBA control plane and operational runbooks.

## 10. Explicit non-authorizations and exit criteria

This document does not implement or authorize a production manifest, signer, key custody, approval service, verifier, migration runner, database schema, DDL proxy, drift monitor, emergency operator control or venue egress fence.

Acceptance requires all of the following: approved schema/profile; exact supported PostgreSQL catalog coverage; independent approval/signing/trust custody; immutable audit; deterministic cross-language conformance; adversarial mutation and concurrency tests; deployment TOCTOU control; post-startup drift detection; DBA/migration and emergency runbooks; independent security review; owner approval.

Until then, the disposable SHA-256 fingerprint remains a fixture regression oracle only. G0D/G1 remain open, Prototype Readiness remains BLOCKED, and live trading remains NOT AUTHORIZED.
