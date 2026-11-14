# NX-ARCH-REVIEW-007 — Risk Scope Serialization & PostgreSQL Concurrency

**Date:** 2026-11-14  
**Status:** DESIGN REVIEW COMPLETE — transaction protocol selected for G1 evaluation; no schema or runtime implemented  
**Scope:** NX-ADR-008 §5.3–5.4, NX-IF-002 §6.3–7, OD-09, NX-REF-EXEC-002  
**Related:** NX-ARCH-REVIEW-006, NX-IF-003, NX-IF-004, NX-IF-005

## 1. Executive decision

The Risk-owned scope-state serialization design is sound as a G1 evaluation baseline **provided that every operation changing the same exposure/capacity invariant participates in one Risk-owned local transaction and updates every affected scope row**.

The design is strengthened with seven explicit rules:

1. A projection event affecting a child scope and any parent/account aggregate must update all affected pre-provisioned scope-state rows in the same transaction, in canonical scope-ID byte order.
2. Scope membership/configuration changes must advance a version and serialize against both projection updates and reservations; stale scope-set calculations fail closed.
3. The account/root scope-state record is mandatory in every v1 reservation/projection transaction and acts as the scope-configuration guard. After the complete lock set is acquired, the root `scope_config_version` is rechecked; a changed version forces full scope-set recomputation.
4. A Risk scope-state row is a serialization/version record, not a second source of accounting truth. It points to the current Risk projection and reservation aggregate versions/watermarks.
5. SQLSTATE **23505** is not a generic retry signal. Only a known idempotency-key collision may be resolved by a new transaction reading the durable request identity and digest; unrelated uniqueness violations fail closed.
6. Market/index/FX/fee/collateral inputs remain immutable, versioned valuation snapshots bound to the reservation and capability. Market-data ticks MUST NOT rewrite every Risk scope-state row; stale or policy-invalid valuation inputs block dispatch.
7. The shared scope-state serialization point deliberately trades write concurrency for correctness. G1 must benchmark contention and tail latency at the actual v1 scope fan-out; do not weaken atomicity to improve throughput.

This review does not approve PostgreSQL for production, a schema, automatic failover, or any runtime. PostgreSQL 18 remains the exact-version evaluation target only.

## 2. Why the common serialization point is necessary

A reservation decision reads current exposure and active reservations, and binds to exact immutable valuation-input snapshots, checks all applicable limits, and commits a new reservation. A concurrent Ledger/venue/external-activity projection update can change the exposure against which that decision was made. Market/index/FX updates are separate source-owned versioned valuation inputs and MUST NOT rewrite every Risk scope-state row on every market-data tick. They are not assumed to share the Risk PostgreSQL transaction or database.

If those operations update different rows or rely on advisory locks that some writer can omit, both can commit based on stale competing views. The Risk-owned scope-state row is therefore the mandatory serialization point for each scope whose shared capacity invariant is affected.

For one scope, the desired serial order is:

- projection update commits first, then reservation reads the updated projection; or
- reservation commits first, then projection update observes and reconciles the reservation against the new exposure.

Neither operation may commit as though the other had not occurred.

For multiple scopes, all affected rows and all reservation/projection mutations commit atomically. A child-only update is insufficient if account/parent limits aggregate that child.

## 3. Minimum logical scope-state record

This is a logical contract for review, **not a selected SQL table schema**. The record should expose enough version state to serialize and prove the transaction:

| Logical field | Purpose |
|---|---|
| risk_scope_id | Stable canonical scope identity |
| scope_config_version | Detect stale parent/child membership, limits and scope configuration |
| scope_state_version | Monotonic serialization version; increments for every reservation or exposure-projection mutation affecting the scope |
| exposure_projection_version | Version/reference of Risk-owned exposure state visible to the scope |
| reservation_aggregate_version | Version/reference of active reservation totals |
| source_watermark_vector_ref/version | Identifies the source evidence/watermark set supporting the projection |
| fencing_generation | Rejects stale Risk writer generations inside the authoritative store; not an external socket fence |
| last_transition_id | Durable idempotent state transition lineage |

The account/root scope-state record is mandatory in every v1 reservation and projection transaction and is the scope-configuration guard. After acquiring the complete scope lock set, the transaction rechecks the root `scope_config_version`; if membership changed, it aborts and recomputes the complete scope set.
| updated_at | Operational timestamp only; not a substitute for monotonic version |

The actual exposure items, valuation evidence, source events and reservation rows remain in their Risk-owned domain records. The scope-state row is not a duplicate Ledger or venue source of truth.

## 4. Required transaction protocols

### 4.1 Reservation transaction

1. Begin one local Risk transaction at the G1 evaluation isolation level (PostgreSQL SERIALIZABLE).
2. Resolve the immutable scope configuration and the complete account/child/ancestor scope set for the command. The account/root scope-state row is always included as the v1 scope-configuration guard.
3. Require every corresponding scope-state row to be pre-provisioned and active. Missing, disabled, duplicate or ambiguous rows fail closed; the hot path never creates them.
4. Lock all rows in one deterministic order using canonical scope-ID bytes. Do not use locale-sensitive text collation for lock order.
5. Recheck the root and descendant scope configuration versions and the required source watermark/freshness vector after acquiring locks. A changed root version invalidates the resolved scope set and requires a full retry.
6. Read the current exposure projection and active reservation aggregates inside the Risk transaction. Bind the evaluation to the exact immutable market/index/FX/fee/collateral version vector supplied by source-owner contracts; do not assume those source snapshots share the Risk database transaction. Require stable snapshot identity, value/digest, completeness/watermark and freshness evidence. Do not reuse exposure or reservation values calculated before lock acquisition. Bind the reservation and capability to the exact valuation-input version vector and source freshness evidence.
7. Recompute every affected limit with exact arithmetic, including parent/account aggregate limits and child constraints.
8. If all scopes pass, persist the idempotency identity/result, all reservation rows, updated reservation totals and scope-state versions atomically. If any scope fails, persist no partial reservation.
9. Commit. Issue the RiskApprovalCapability only after commit is positively confirmed and the result is bound to the canonical command digest, exact reservation state and valuation-input version vector.
10. If the result is unknown, resolve only through the same stable request identity and digest on a positively identified authoritative primary. Never mint a new identity to recover a timeout.

### 4.2 Projection-event transaction

1. Receive discrete economic exposure facts through a durable Risk-owned inbox; Ledger remains authoritative for journal posting and cannot write Risk state directly. Market-data ticks remain separate immutable valuation inputs and do not create per-tick scope-state writes.
2. Deduplicate by the source-defined event identity and namespace, with payload digest binding. Same identity/same digest is idempotent; same identity/different digest is an integrity conflict and quarantines the affected scope.
3. Determine the complete affected scope set, including all parent/account aggregates and any child scopes whose exposure projection changes.
4. Lock every affected pre-provisioned scope-state row in canonical scope-ID byte order in one Risk transaction.
5. Validate current scope-config versions, source sequence/cursor/watermark continuity, correction lineage and freshness. Out-of-order or incomplete evidence is held/reconciled; it is not silently skipped.
6. Apply the projection delta, persist inbox result, advance source watermark(s), update exposure-projection version and increment every affected scope-state version atomically.
7. If any scope row or required source evidence is missing/ambiguous/stale, commit no partial projection transition; mark the affected scope set stale/blocked through the defined durable control path and deny risk-increasing authorization.
8. Rebuilds/replays use the same idempotent event identities and publish a new complete projection/watermark vector only after validation.

### 4.3 Scope hierarchy/configuration changes

Parent/child membership, account aggregation membership, scope activation, policy linkage or limit configuration changes can alter which rows a reservation must serialize against.

- Scope changes use a separate privileged configuration transaction, never an order hot-path side effect.
- The transaction includes the account/root configuration guard and locks all old and new affected scope rows in canonical order, advances the root and relevant descendant `scope_config_version` values, and publishes the new membership/configuration only atomically.
- A reservation or projection transaction using a stale scope-config version aborts/recomputes from the new configuration.
- Missing/ambiguous parent membership or an unbounded affected-scope set fails closed.
- The maximum supported scope fan-out must be bounded by configuration and measured. The v1 single-account/subaccount scope keeps this small; no multi-tenant or arbitrary portfolio fan-out is assumed.

## 5. Retry, uniqueness and ambiguous-commit semantics

PostgreSQL 18 documentation distinguishes serialization failures, deadlocks and uniqueness errors:

- **40001 (serialization_failure):** abort and retry the whole transaction from a fresh snapshot, with bounded attempts/backoff and full recomputation.
- **40P01 (deadlock_detected):** abort and retry the whole transaction from a fresh snapshot under the same finite budget. Canonical lock order is the primary deadlock prevention mechanism, not a reason to omit deadlock handling.
- **23505 (unique_violation):** not a generic retry. If and only if it is the expected idempotency unique constraint, abort and start a new transaction on the authoritative primary; read the existing request identity. Same digest returns the original durable result; different digest is an idempotency conflict. If no matching row is visible or the violated constraint is unrelated, fail closed and investigate.
- **23P01 (exclusion_violation)** and all other constraints are not automatically retried unless a separately specified, tested case proves a transient serialization cause.
- A lost commit response is not proof of rollback. Resolve through the stable request identity/digest on the positively identified primary. If primary authority or outcome remains uncertain, keep the affected scope HALTED for risk-increasing operations.

No statement-only retry, stale snapshot reuse, unbounded retry loop, or retry under a new request identity is permitted.

## 6. Enforcement and operational boundaries

- Only the Risk workload may write Risk-owned scope-state, exposure-projection, reservation aggregate and Risk inbox records. Database roles must prevent Ledger, Execution, adapters, Analytics and optional modules from bypassing Risk.
- All code paths that can change a scope's exposure/capacity invariant must use the same protocol. A row lock or version field is ineffective if a writer can update the projection without updating scope state.
- Advisory locks are not the sole correctness mechanism: PostgreSQL does not enforce that all writers participate.
- PostgreSQL SERIALIZABLE is defense-in-depth, not a substitute for the common state row, exact transaction protocol, idempotency constraints or source freshness.
- A database fencing generation does not fence an external venue socket. Trusted Egress and old-process/host/network fencing remain separate proofs under NX-REF-EXEC-002.
- No automatic failover or active-active primary in G1. Backup/restore/PITR, primary authority and positive old-primary fencing must be proven before failover is considered.

## 7. Concurrency and fault-injection matrix

| Test | Required invariant |
|---|---|
| Two simultaneous reservations compete for final capacity | At most one reservation commits if combined worst-case exposure exceeds limit |
| Reservation races a Ledger/venue projection event | One serial order; no stale-view over-approval |
| Child projection event affects account parent aggregate | Child and all affected parent scope rows update atomically |
| Parent/child multi-scope reservations overlap in opposite input order | Canonical lock order prevents avoidable deadlock; all-scope commit or no commit |
| Duplicate projection event, same digest | Exactly one projection delta |
| Duplicate event identity, different digest | Integrity conflict; no silent overwrite |
| Out-of-order event / watermark regression / missing page | Scope stale/blocked; never infer zero exposure |
| Scope membership changes during reservation | Stale config aborts/recomputes; no mixed hierarchy |
| Missing or disabled pre-provisioned scope row | Fail closed; no opportunistic hot-path creation |
| Same idempotency ID + same digest | Return original durable result; no extra capacity |
| Same idempotency ID + different digest | Explicit conflict; no second reservation |
| Expected idempotency 23505 race | New transaction resolves existing row/digest; no generic retry |
| Unrelated 23505 / 23P01 | Fail closed; no retry loop |
| Inject 40001 and 40P01 | Whole transaction retries from fresh snapshot, bounded |
| Lost commit response / primary change | Same identity resolution; unknown authority keeps scope halted |
| Risk writer stale generation | Cannot mutate authoritative scope state |
| Ledger attempts direct Risk-state write | Database permission denial |
| High contention / lock timeout / fan-out limit | Bounded latency/retries; fail closed without partial state |
| Market-data mark/index/FX tick | No scope-state write per tick; reservation binds exact immutable valuation-input versions and stale/invalid inputs block dispatch |
| New monotonic market watermark after approval | The exact bound valuation vector remains eligible only if source-specific age, clock uncertainty, quality, correction and drift policy still pass; policy may explicitly require latest |
| Valuation vector corrected/revoked or freshness/drift policy fails | Egress rejects; no silent vector substitution or approval rebinding; Risk must re-evaluate and establish a safe replacement path |
| Newer market-data tick arrives after reservation | Existing bound immutable valuation vector remains usable only while its source-specific freshness/uncertainty/drift policy passes; a policy may require latest; Egress never silently substitutes the new vector |
| Bound valuation vector becomes stale, corrected or policy-invalid before dispatch | Egress rejects the send; reservation remains held/reconciliation-gated until Risk re-evaluates and proves a safe replacement path |
| Projection and reservation crash at every commit boundary | Durable inbox, projection, reservation and scope version remain mutually consistent |
| PostgreSQL primary failover with old writer alive | No second authoritative writer; external egress remains separately fenced |

The actual test harness must inspect committed rows, source watermarks, inbox identities, scope-state versions and the instrumented authorization/egress boundary. Mock-only lock tests are insufficient.

## 8. Performance and availability trade-offs

A common scope-state row intentionally serializes writes to a shared economic exposure/capacity invariant. This may create contention; it is not free. G1 keeps market-data ticks out of this write path by reading immutable versioned valuation snapshots and binding their version vector to the decision.

G1 must measure, on the exact PostgreSQL 18 patch and realistic data volume:

- reservation/projection throughput and p50/p95/p99 transaction latency;
- lock wait duration, serialization/deadlock rates and bounded retry exhaustion;
- hot-scope skew and parent/child fan-out;
- WAL/replication/commit latency and recovery behavior;
- impact of discrete exposure-projection bursts and reconnect/replay backlogs;
- valuation snapshot lookup latency and behavior when market-data/FX inputs change between reservation and dispatch;
- behavior under lock timeout, pool exhaustion and primary uncertainty.

If performance is insufficient, first examine query plans, scope partitioning consistent with the invariant, bounded projection batching and connection-pool policy. Do not remove the shared serialization point, split all-scope atomicity or weaken source freshness merely to increase throughput. Any alternative must re-prove the same no-overcommit invariant.

## 9. Official PostgreSQL 18 evidence

- Transaction isolation and SERIALIZABLE anomalies: https://www.postgresql.org/docs/18/transaction-iso.html
- Application-level consistency checks and retry guidance: https://www.postgresql.org/docs/18/applevel-consistency.html
- Explicit row locks, deterministic lock ordering, deadlocks and advisory-lock limitations: https://www.postgresql.org/docs/18/explicit-locking.html
- Serialization failure handling; complete-transaction retry and cautious handling of 23505/23P01: https://www.postgresql.org/docs/18/mvcc-serialization-failure-handling.html
- INSERT / ON CONFLICT semantics: https://www.postgresql.org/docs/18/sql-insert.html

PostgreSQL documentation supports the transaction/error semantics above; it does not prove NEXUS's implementation or deployment safety.

### Valuation-input consistency and dispatch revalidation

- Market/index/FX/fee/collateral values are source-owned immutable snapshots, not mutable fields read opportunistically during a reservation transaction.
- The Risk transaction binds to an exact version vector and validates source identity, value/digest, completeness/watermark and freshness evidence. Cross-domain snapshots are not presumed to share a database or distributed transaction.
- Trusted Egress validates the same bound `valuation_input_vector_id/version` against the authoritative persisted Risk evidence manifest, source-specific freshness and any configured drift/admissibility policy immediately before send. It MUST NOT fetch replacement market/FX/fee/collateral values or call source services on the dispatch path. A newer snapshot does not automatically replace the signed approval's inputs.
- If the exact bound vector is stale, incomplete, contradictory, outside a configured drift bound or the policy is unconfigured, Egress denies send. Risk must perform a new evaluation and reservation; it must not mutate an existing approval in place.
- The interface schema and exact version-vector representation remain future source-owner contract work; this review does not invent an executable schema or numeric thresholds.

## 10. Gate disposition

- Risk-owned scope-state serialization is the selected G1 evaluation design.
- PostgreSQL 18 SERIALIZABLE is the default evaluation isolation level, not a production deployment decision.
- Logical scope-state fields and transaction protocols are design requirements, not an approved physical schema.
- Scope fan-out, lock plan, role grants, exact PostgreSQL patch, retry budgets, replication, backup/RPO/RTO and old-primary fencing remain to be tested/approved.
- No database, schema, migration, Risk service, reservation runtime or venue integration was created.

**Final disposition: CONCURRENCY DESIGN REFINED; IMPLEMENTATION AND PROOF REMAIN OPEN.**
