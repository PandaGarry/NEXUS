# NX-ADR-008 — G1 Technical Baseline: Canonical Commands, Persistence & Safe Operations

**Date:** 2026-11-14  
**Status:** TECHNICAL BASELINE SELECTED FOR G1 DESIGN / PROTOTYPE EVALUATION — NOT PRODUCTION APPROVAL  
**Decision authority:** Technical lead under the owner's explicit delegation to choose conservative technical solutions  
**Related:** NX-IF-001..005, NX-REF-EXEC-002, NX-ARCH-004/005, NX-ARCH-REVIEW-005, NX-OWNER-DECISIONS-001, NX-SEC-001, NX-RESEARCH-010/011

## 1. Context

NEXUS has published proposed command, Risk reservation, Ledger, recovery, emergency-control and egress contracts. The remaining architecture work needs a coherent technical baseline so implementation research does not keep reopening the same choices.

The baseline must preserve:
- exact, cross-language command identity and financial values;
- independent Risk approval and one-time consumption;
- durable reservation, command/outbox and Ledger transaction boundaries;
- a sole credential/socket-owning Trusted Egress boundary;
- fail-closed behavior when authority, evidence, freshness or recovery state is uncertain;
- a small first implementation footprint for the accepted single-venue / dedicated-account v1 scope.

This ADR selects bounded G1 evaluation defaults. It does not select a cloud, database host, vault product, venue, legal operating model, numeric Risk limits or production availability target. It does not authorize live credentials, orders or deployment.

## 2. Decision summary

| Area | G1 technical baseline | What remains gated |
|---|---|---|
| Canonical command bytes | RFC 8949 core deterministic CBOR with a strict NEXUS profile | Exact encoder/decoder libraries and versions; golden vectors; implementation |
| Command digest | SHA-256 over a NEXUS command-domain separator and deterministic command bytes | Exact versioned digest envelope and test vectors |
| Risk approval envelope | COSE_Sign1, fully specified COSE Ed25519 algorithm (-19, RFC 9864), protected algorithm and key identifier | Provider/HSM support, key custody, lifecycle, security review and jurisdictional qualification |
| Persistence candidate | PostgreSQL 18, one logical primary, service-owned schemas and roles | Exact patch version, deployment, backup/restore, isolation and failure proof |
| Transactions | Separate Risk, Command and Ledger local ACID transactions; no distributed transaction | Isolation/locking implementation and crash/concurrency evidence |
| Messaging | Transactional outbox/inbox in the owning database; no broker initially | Add a broker only after measured fan-out/replay need |
| Freshness/recovery | Source-specific EvidenceRequirementSet and FreshnessPolicy; no global TTL | Venue-specific thresholds, retention, clock uncertainty, RTO/RPO |
| Emergency operations | Halt is available; resume is owner-only after step-up and RecoveryBarrier; no automatic cancel-all/flatten or offline emergency order plan | Identity provider, step-up mechanism, operator assignment and venue certification |

## 3. Canonical command serialization and digest

### 3.1 Selected G1 encoding profile

Use **RFC 8949 core deterministic CBOR** for the bytes hashed and referenced by RiskApprovalCapability.

NEXUS's restricted command profile MUST:
- use RFC 8949 core deterministic encoding, including preferred shortest-form arguments and lengths;
- use definite-length strings, arrays and maps only; reject indefinite-length items;
- restrict command-map keys to schema-defined ASCII text field names only; reject non-ASCII, unknown keys and duplicate key values before constructing an application map;
- sort map keys by the bytewise lexicographic order of their deterministic encodings (RFC 8949 §4.2.1; do not use the legacy length-first ordering);
- on ingress, verify the received byte stream itself satisfies the deterministic profile before materializing application objects; reject non-preferred integer/length encodings, unsorted maps, duplicate keys and trailing bytes rather than silently decode-and-reencode them;
- reject invalid UTF-8, unknown tags, indefinite-length items and all floating-point values;
- use only signed 64-bit CBOR integers for explicitly declared control metadata;
- encode financial quantities, prices, coefficients, numerators, denominators and other exact values as canonical decimal/integer strings or schema-defined typed objects, never binary floats;
- reject unknown fields and unsupported schema/canonicalization versions;
- preserve Unicode strings byte-for-byte after strict UTF-8 decoding; do not silently normalize or alias identifiers;
- apply explicit maximum input bytes, nesting depth, collection length, string length and numeric digit/scale budgets before expensive processing.

The encoder and decoder must independently validate the profile. A generic CBOR decoder that silently collapses duplicate keys, tolerates non-deterministic encodings or discards trailing bytes is not sufficient. Command map keys are fixed schema-defined ASCII field names; free-form identifiers and user text belong in values, not keys. Unicode is permitted in values under strict UTF-8 handling, but no Unicode normalization or aliasing is performed.

The JSON fixture format in NX-ARCH-005 remains the human-reviewable, strict test-vector envelope. It is not the command's canonical byte encoding. Golden vectors must bind the typed command input to exact CBOR bytes and the resulting digest.

### 3.2 Why not canonical JSON for the command digest

RFC 8785 JCS constrains JSON number values to IEEE-754 binary64-compatible values and recommends strings for numbers requiring greater precision or longer integer ranges. NEXUS's proposed command contract permits signed 64-bit control integers, including values beyond the exact integer range of binary64. JCS could be used only after changing every such field to a string or narrowing its domain. The deterministic CBOR profile preserves the required integer domain without weakening exact financial strings.

Ordinary JSON serialization is rejected as a digest format because key ordering, numeric rendering, escaping and duplicate-key handling vary between implementations.

### 3.3 Digest

The command digest is:

`SHA-256("NEXUS:CANONICAL-TRADE-COMMAND:v1" || 0x00 || deterministic\_cbor\_bytes)`

The domain separator is fixed by protocol version and is not caller-controlled. The digest is recomputed by Risk and Execution from the canonical command bytes; caller-supplied digest values are never trusted.

A schema or canonicalization change that affects bytes requires a new version and new golden vectors. Historical command bytes and digests remain immutable.

## 4. RiskApprovalCapability signing

### 4.1 Selected G1 envelope

Use **COSE_Sign1** with the fully specified **COSE Ed25519 algorithm (COSE alg = -19, RFC 9864)** for the G1 capability-signing profile. Do not use the older polymorphic COSE EdDSA identifier (-8): RFC 9864 deprecates polymorphic algorithm identifiers and provides the fully specified Ed25519 replacement.

- The fully specified algorithm identifier (-19) is protected and MUST match the COSE key's algorithm policy; the COSE key MUST be OKP with the Ed25519 curve. Reject polymorphic EdDSA (-8), Ed448, algorithm substitution and key/algorithm mismatch.
- The protected key identifier (kid) is an untrusted lookup hint until signature verification succeeds; COSE does not define it as security-critical or guarantee uniqueness. Resolve only against a bounded local versioned key registry—never fetch keys from token-supplied URLs. Token-supplied issuer/audience values are also untrusted lookup hints, not authority: bind candidate selection to locally configured expected issuer/audience and key purpose, then after signature verification require the signed claims to match that expected context and the registry entry. Require exactly one eligible key or fail closed on ambiguity, stale registry generation, revocation or mismatch.
- Accept only a public COSE OKP/Ed25519 verification key with a 32-byte public x parameter; reject private d material in Execution or any non-Risk process. Require a 64-byte Ed25519 signature. Key encoding, algorithm and purpose are pinned by local registry policy, not negotiated from the token.
- The signed payload contains the command digest, command ID, reservation ID, exact account/scope, issuer and audience, issue/not-before/expiry times, policy/spec/exposure versions, halt epoch, capability schema version and a unique approval/nonce identity.

- The signed capability payload is exactly one NEXUS restricted deterministic-CBOR map, encoded into the COSE payload byte string. The verifier validates the original payload bytes against the NEXUS profile before typed claim use; it MUST NOT decode-and-reencode and then treat normalized bytes as the signed input.
- The wire object is the **untagged, embedded-payload COSE_Sign1 four-element array** `[protected : bstr, unprotected : map, payload : bstr, signature : bstr]`. Reject tag 18, detached/null payload, wrong array length and alternative message structures; the enclosing protocol context identifies COSE_Sign1.
- The protected-header byte string contains exactly a deterministic CBOR map with integer label 1 (`alg`) = -19 and integer label 4 (`kid`) = a byte string of 1–64 bytes. No other protected parameters are allowed. The unprotected map MUST be empty. Reject duplicate labels and protected/unprotected collisions.
- Preserve and verify against the exact received protected-header byte string. Do not reconstruct it from a decoded map. The `Sig_structure` is encoded with RFC 9052 §9 core deterministic encoding; the fixed NEXUS external AAD is an exact byte string and is not caller-controlled.
- COSE external AAD carries a fixed NEXUS protocol-domain context; it is not supplied by Strategy, AI or an untrusted client.
- Risk's signing key is distinct from every venue API/signing key.
- Execution receives public verification material only. It cannot mint capabilities.
- Private signing material is held behind a dedicated Risk signer boundary and must be non-exportable in a production deployment. Ordinary API, Strategy, AI, Dispatcher and adapter workers receive no signing authority.
- Key rotation, activation/retirement, emergency revocation, historical verification and issuer/audience rules are explicit stateful controls.

COSE_Sign1 / fully specified COSE Ed25519 is selected as the protocol baseline, not as proof that a particular HSM/KMS supports Ed25519. The production key-custody provider is not selected. If a required custody provider cannot safely support the selected profile, that incompatibility must return to security review; do not silently substitute HMAC or custom cryptography.

### 4.2 Signature is not authorization

A valid signature proves integrity and issuer possession only. Before dispatch, NEXUS still MUST verify:
- capability scope, audience, issuer, expiry and key status, all checked against locally expected context after signature verification;
- command digest and immutable payload equality;
- durable active reservation;
- durable single-use consumption;
- current policy/spec/evidence versions;
- current halt and eligibility epochs;
- dispatcher fence and final Trusted Egress authorization.

Approval consumption is atomic with the Command-owned command/outbox commit. The final egress check remains independent. No signature can bypass Risk, reservation, Ledger, halt, reconciliation or external fencing.

## 5. Persistence and transaction baseline

### 5.1 Database candidate

Select **PostgreSQL 18 as the leading G1 persistence evaluation target**, not as an installed or production-selected dependency.

Initial G1 topology:
- one logical primary;
- service-owned schemas and separate least-privilege roles for Risk, Command, Ledger and Egress;
- no shared application superuser;
- no direct database access from Strategy/AI or optional modules;
- no multi-primary writes and no distributed ACID transaction;
- immutable IDs, unique idempotency constraints, state-version/CAS guards and append-only audit/event lineage where required.

A single PostgreSQL cluster with separated schemas/roles is preferred over multiple databases for the first controlled prototype because it permits bounded local transactions without introducing a distributed commit protocol. Schema separation is not a substitute for role, process and network isolation.

### 5.2 Transaction ownership

1. **Risk transaction:** evaluate the current complete exposure scope, reserve all applicable v1 account/child constraints, write idempotency and reservation state atomically, then commit. Only after confirmed commit may Risk issue a capability.
2. **Command transaction:** atomically consume the single-use approval and persist the immutable canonical command, reservation reference and outbox record. A duplicate request returns the original durable result or an explicit idempotency conflict.
3. **Dispatcher attempt transaction:** durably claim an outbox item and commit the conservative pre-egress attempt marker before any external side effect.
4. **Ledger transaction:** atomically deduplicate the execution event/inbox identity, post the balanced journal entry and advance the corresponding local posting/projection watermark.
5. **Trusted Egress:** re-read authoritative state and validate the current approval/reservation/halt/eligibility/fence immediately before transmission. It alone owns venue credentials and the actual venue socket.

These are ordered local ACID transactions, not one cross-service transaction. The design retains ambiguity and reconciliation across the gaps.

### 5.3 Risk reservation serialization point, isolation and retry rules

The G1 design uses a **Risk-owned scope-state record as the common serialization point** for both capacity reservations and changes to Risk's derived exposure projection. This is a design contract, not a selected SQL schema.

- Ledger remains the owner of journal posting and its durable event/inbox identity. It MUST NOT write Risk-owned state directly. Risk consumes Ledger/venue/external-activity facts through an idempotent inbox and updates its own exposure projection, source watermarks and scope-state version in a Risk-owned local transaction.
- Every reservation and every Risk projection update affecting the same account/child scope MUST update the same Risk-owned scope-state record. This prevents a reservation check from racing a concurrent projection update that would otherwise change the exposure being checked. If the projection consumer is delayed, incomplete or contradictory, the relevant source watermark/freshness gate fails and risk-increasing approval is denied.
- For a command spanning the account scope and one or more child constraints, the Risk transaction MUST resolve the complete required scope set, lock/update all corresponding pre-provisioned scope-state records in one local transaction, and process them in a single deterministic order by canonical scope-ID bytes. Missing, disabled or ambiguous scope-state records fail closed; the hot reservation path MUST NOT create missing scope rows opportunistically.
- Within that transaction, Risk reads the versioned exposure projection and active reservation totals, evaluates every applicable limit, and—only if all scopes pass—persists the request identity/result, all reservation rows and all updated reserved-capacity totals atomically. A partial reservation across scopes is forbidden.
- The common scope-state update is the serialization point; a version/CAS guard and database constraints remain mandatory. PostgreSQL SERIALIZABLE is the G1 default evaluation level as a second line of defense against predicate/write-skew anomalies. The exact query plan, lock strategy and whether every table needs SERIALIZABLE remain subject to measured concurrency/fault tests.
- Projection-event application is idempotent: persist the inbox/event identity, apply the projection delta, advance the corresponding source watermark and update scope state in one Risk-owned transaction. Redelivery cannot apply the same exposure delta twice. The projection must retain lineage to its source event/snapshot and policy version. The transaction MUST resolve and update every affected pre-provisioned scope row, including parent/account aggregates and any child scopes whose projection changes; a child-only update that leaves a parent aggregate stale is forbidden.
- Scope hierarchy/configuration changes use a separate privileged transaction. It MUST lock the complete old/new affected scope set in canonical order, advance scope_config_version atomically and invalidate stale scope-set calculations. Reservations/projection updates using an old configuration version abort and recompute; missing or unbounded scope membership fails closed.
- The logical scope-state record MUST carry at least stable risk_scope_id, scope_config_version, monotonic scope_state_version, exposure_projection_version, reservation_aggregate_version, source-watermark-vector reference/version, fencing_generation and last_transition_id. This is a logical concurrency contract, not an approved physical schema; exposure facts and reservation rows remain separate Risk-owned records.
- The Risk idempotency identity is stable across retries and bound to the canonical command/request digest. A repeated identity with the same digest returns the original durable result; the same identity with a different digest is an explicit conflict. A database uniqueness constraint is the final duplicate guard, not an application-only pre-check.
- Issue RiskApprovalCapability only after the Risk reservation transaction's commit is positively confirmed. A lost response or unknown commit result is resolved by querying the same idempotency identity and digest on the positively identified authoritative primary. If no committed row is visible, absence alone MUST NOT be interpreted as rollback while the original transaction may still be in flight. Any retry may use only the same identity and digest so the unique constraint arbitrates against the original transaction; never mint a second reservation under a new request identity to "recover" a timeout. If primary authority or the final outcome cannot be established within bounded recovery, keep the scope HALTED.
- A serialization failure (`40001`) or deadlock (`40P01`) aborts the complete transaction. Retry the **whole transaction** from a fresh snapshot under a finite retry budget and bounded backoff; recompute every exposure/limit decision. Never retry only the failed statement or reuse data from the aborted snapshot. Other constraint/business failures are not generic retry signals.
- A unique violation (`23505`) is not a generic retry. Only the expected idempotency unique constraint may enter the duplicate-resolution path: abort, start a new transaction on the authoritative primary, read the stable request identity, return the original result only if the digest matches, and return conflict if it differs. An unrelated unique violation or exclusion violation fails closed; never loop-retry it blindly.
- If the commit outcome cannot be resolved from the authoritative store, or primary authority is uncertain, keep the affected scope HALTED for risk-increasing operations. Do not infer rollback from a lost connection.

Command approval consumption and outbox insertion use one separate Command-owned transaction with a conditional single-use state transition and unique constraints. Ledger inbox deduplication, journal posting and its local projection update likewise commit atomically. Neither transaction is folded into the Risk reservation transaction or a distributed commit.

Advisory locks alone are not correctness controls because PostgreSQL does not enforce that every writer participates. A database lease or fencing token does not fence an external socket. Explicit row locks are not a substitute for updating the common Risk-owned state record: every writer that changes the Risk projection/reservation invariant must participate in the same transaction protocol.
### 5.4 Durability, backup and failover

For the first G1 prototype, use one primary and prove backup, restore and point-in-time recovery. Do not enable automatic failover or active-active writers.

PostgreSQL streaming replication is asynchronous by default and may lose acknowledged transactions on failover. Synchronous replication can wait for a standby WAL acknowledgement, but adds availability/latency trade-offs and does not remove the need to fence an old primary. Any future failover design MUST prove:
- replication mode and exact commit acknowledgement semantics;
- old-primary isolation/STONITH before successor writes are enabled;
- no split-brain or stale writer can mutate authoritative state;
- recovery and reconciliation of uncertain commits and external attempts;
- tested backup/restore/PITR and declared RPO/RTO.

If the old primary cannot be positively fenced or the authoritative state is uncertain, the affected execution scope remains HALTED.

## 6. Messaging and observability

- Do not add NATS, Kafka or another broker to G1. Use transactional outbox/inbox with bounded polling until measured fan-out, replay or throughput requirements justify a broker.
- If JetStream is adopted later, treat its normal delivery as at-least-once; broker-level deduplication/double-ack does not make venue side effects exactly-once.
- Use allowlisted telemetry attributes and bounded-cardinality dimensions. Redaction processors are defense-in-depth; sensitive values must be excluded at instrumentation source.
- Telemetry loss must not block Risk, halt, durable command acceptance or trusted egress. Telemetry is not the accounting/audit source of truth.

## 7. Freshness and recovery baseline

Select source-specific EvidenceRequirementSet/FreshnessPolicy as the only acceptable model. Every requirement is bound to source, venue/account/instrument scope, operation class, sequence/cursor/watermark, completeness, clock quality and policy version.

- No universal market/account/order/fill/Ledger TTL is selected.
- Elapsed-time decisions use monotonic time; wall-clock uncertainty is explicit where timestamps or signatures require it.
- Missing, stale, contradictory, incomplete or unconfigured mandatory evidence is UNKNOWN and blocks the affected risk-increasing operation.
- RecoveryBarrier is scoped and dependency-aware; restart or socket reconnect does not restore readiness.
- Numeric thresholds, retention windows, clock uncertainty, retry budgets and RTO/RPO remain owner/domain decisions. They are not inferred from a test profile or from infrastructure defaults.

## 8. Emergency operations baseline

For the v1 single-owner product:
- the authenticated Owner and pre-approved hard system triggers may request a scoped halt; halting must not require trading approval;
- AI, Strategy and ordinary clients may report a halt condition but cannot mutate HaltState or resume;
- resume is Owner-only, requires step-up authentication, a reason/evidence record and a READY RecoveryBarrier for the exact scope;
- no automatic cancel-all, flatten or protective-order removal occurs on halt;
- no offline emergency order plan is enabled;
- emergency order workflows remain disabled until exact venue/account-mode semantics and required authority are certified;
- ordinary cancel/reduce commands still pass through canonical command, Risk, reservation, outbox, venue capability and reconciliation gates;
- break-glass is limited to containment actions such as halting, isolating workloads and revoking credentials/routes; it cannot mint approvals, relax Risk limits, place orders or transfer assets;
- dual control is not simulated in a single-owner deployment. If a second independent operator is introduced, high-impact resume/emergency scopes require an explicit two-person policy before activation.

The identity provider and step-up mechanism are not selected. This baseline deliberately prefers unavailable emergency trading over an unbounded or ambiguous emergency side effect.

## 9. Rejected alternatives

| Alternative | Decision |
|---|---|
| Ordinary JSON serialization for command hashing | Reject: non-canonical behavior across runtimes |
| RFC 8785 JCS without changing numeric schema | Reject for command digest: JSON numbers are constrained to IEEE-754 binary64; NEXUS permits signed 64-bit metadata |
| Shared HMAC approval secret held by Risk and Execution | Reject: any verifier holding the shared secret can also mint approvals |
| Custom signature/canonicalization scheme | Reject: use reviewed standards and vetted implementations |
| Distributed transaction across Risk, Command and Ledger | Reject for G1: unnecessary operational coupling; preserve ordered local commits and explicit ambiguity |
| Message broker as reservation/outbox source of truth | Reject: durable domain state remains in owning database transactions |
| PostgreSQL advisory lock or lease as sole fencing | Reject: application participation and external-send authority are not enforced |
| Automatic asynchronous database failover | Reject until old-primary fencing and possible commit-loss semantics are proven |
| Active-active Egress for one account | Reject until single-writer and independent external fencing are proven |
| Global freshness TTL | Reject: source completeness and risk differ by operation and venue |
| Automatic cancel-all/flatten or offline emergency trading | Reject for v1 until explicit owner policy and venue evidence exist |

## 10. Consequences and remaining gates

### Positive
- Establishes one coherent cross-language serialization/signing direction.
- Keeps signing authority asymmetric and isolated from verification and venue credentials.
- Keeps the first persistence design relational and locally transactional.
- Avoids premature broker, multi-database and active-active complexity.
- Makes the safe degraded behavior explicit.

### Costs and unresolved evidence
- CBOR decoder strictness, duplicate-key detection and resource limits need cross-language tests.
- Exact Python/Rust libraries, versions, build provenance and licenses are not selected.
- Ed25519 support, RFC 9864 alg=-19 interoperability, non-exportable key custody, issuer-scoped key lookup and ambiguous-kid rejection must be proven for the eventual provider.
- PostgreSQL 18 exact patch, host, replication, backup and restore topology remain unselected.
- Transaction isolation, concurrency, ambiguous commit, crash/restart and actual egress-boundary fault tests remain mandatory.
- Source-specific freshness thresholds, data retention, RTO/RPO and operator identity details remain open.
- Venue/legal eligibility, accounting policy, numeric Risk limits and production/live authorization remain outside this ADR.

## 11. Acceptance and verification

This ADR is selected as the **G1 technical design baseline** under the owner's delegated technical authority. It is not an accepted production architecture or a security certification.

Before implementation:
- [ ] review the exact CBOR/COSE libraries and versions for Python and Rust;
- [ ] publish cross-language canonical byte, digest and COSE signature vectors using RFC 9864 COSE Ed25519 alg=-19; include rejection vectors for deprecated alg=-8, wrong curve, algorithm/key mismatch and ambiguous kid;
- [ ] run duplicate-key, invalid UTF-8, float/tag/indefinite-length, integer-range and resource-exhaustion tests;
- [ ] prove the Risk-owned scope-state serialization point is shared by reservation and exposure-projection updates; test that a concurrent Ledger/venue projection update cannot race a capacity check;
- [ ] prove all-scope atomicity for account + child constraints, deterministic scope lock order, missing-scope fail-closed behavior and no partial reservation;
- [ ] prove same-idempotency/same-digest replay returns the original result and same-idempotency/different-digest is rejected under concurrent duplicate requests;
- [ ] inject SQLSTATE 40001 / 40P01 and prove whole-transaction retry from a fresh snapshot with bounded attempts; verify no stale precomputed exposure is reused;
- [ ] inject lost commit responses and prove reconciliation by the same durable request identity/digest; unresolved primary/commit authority must keep the scope HALTED;
- [ ] prove duplicate projection-event delivery cannot double-apply exposure and that stale/incomplete source watermarks block risk-increasing reservations;
- [ ] run the full reservation/projection concurrency, all-scope atomicity, serialization retry and unknown-commit suite on the exact PostgreSQL patch version;
- [ ] prove Command single-use consumption/outbox atomicity and Ledger inbox/journal idempotency;
- [ ] test backup/restore/PITR and fail-closed recovery;
- [ ] prove stale process/host/network path cannot reach venue egress after fencing;
- [ ] obtain security review of key custody and jurisdictional compatibility;
- [ ] retain owner approval for numeric Risk limits, accounting policy, venue selection, production deployment and any live authorization.

No runtime dependency, database, key, credential, venue, order or production deployment is introduced by this ADR.

## 12. Sources

- RFC 8949 — CBOR, core deterministic encoding: https://www.rfc-editor.org/rfc/rfc8949.html
- RFC 8785 — JSON Canonicalization Scheme: https://www.rfc-editor.org/rfc/rfc8785.html
- RFC 9052 — COSE structures and signing process: https://www.rfc-editor.org/rfc/rfc9052.html
- RFC 9053 — COSE initial algorithms (updated by RFC 9864): https://www.rfc-editor.org/rfc/rfc9053.html
- RFC 9864 — fully specified COSE Ed25519 algorithm (-19); deprecates polymorphic EdDSA (-8): https://www.rfc-editor.org/rfc/rfc9864.html
- RFC 8032 — EdDSA / Ed25519: https://www.rfc-editor.org/rfc/rfc8032.html
- NIST FIPS 186-5 — Digital Signature Standard: https://csrc.nist.gov/pubs/fips/186-5/final
- PostgreSQL 18 transaction isolation: https://www.postgresql.org/docs/18/sql-set-transaction.html
- PostgreSQL serialization failure handling: https://www.postgresql.org/docs/18/mvcc-serialization-failure-handling.html
- PostgreSQL 18 application-level consistency and explicit locking: https://www.postgresql.org/docs/18/applevel-consistency.html
- PostgreSQL 18 INSERT / ON CONFLICT uniqueness and concurrency: https://www.postgresql.org/docs/18/sql-insert.html
- PostgreSQL high availability and synchronous replication: https://www.postgresql.org/docs/18/high-availability.html
- PostgreSQL failover and old-primary fencing: https://www.postgresql.org/docs/18/warm-standby-failover.html

**Final disposition:** G1 technical baseline selected for design and qualification. Production technology selection, security/operational acceptance and all live capabilities remain gated.
