# NX-ARCH-REVIEW-008 — HEGC Entrypoint and Database Privilege Boundary

**Status:** DESIGN REVIEW COMPLETE; ACCEPTANCE AND IMPLEMENTATION EVIDENCE OPEN  
**Date:** 2026-11-14  
**Scope:** NX-IF-001, NX-IF-005, NX-ADR-008, NX-SEC-001, NX-REF-EXEC-002, NX-ARCH-REVIEW-007 and NX-RESEARCH-012 §4.2–4.3.

## 1. Executive result

The HEGC trust boundary is materially stronger when the application runtime cannot read gate-critical source tables or write control records directly. The preferred G1 evaluation shape is:

- HEGC runtime receives EXECUTE-only access to a small set of reviewed database entrypoints.
- A dedicated NOLOGIN SECURITY DEFINER owner performs the bounded validation read set and writes only HEGC control state.
- A separate NOLOGIN guard-function owner writes only the common scope guard and reads only minimal scope-membership/config-version metadata.
- Trusted Egress has a distinct workload principal and can consume its own one-use grant, report socket initiation and read bounded attempt status, but cannot write control tables or call the privileged authorization entrypoint.
- Risk/Command/eligibility writers use guarded domain procedures; direct DML paths that bypass the common commit-order guard are revoked.

This is a preferred G1 candidate, not a selected production implementation. No database schema, role, function, connection or credential has been created.

## 2. Authority and role separation

| Principal / role | Allowed authority | Explicitly excluded |
|---|---|---|
| HEGC runtime login | EXECUTE on reviewed authorization, halt, consume and bounded status entrypoints | Direct source SELECT; direct guard/HaltState/EgressBoundaryAuthorization DML; venue credentials/socket; Risk signing key |
| nexus_hegc_owner (NOLOGIN definer owner) | SELECT on exact gate-critical source records; write HEGC-owned control records through fixed reviewed functions | Source mutation; venue credentials/socket; Risk signing key; superuser/BYPASSRLS; privileged role membership |
| nexus_control_owner (NOLOGIN guard owner) | Write the common guard table; SELECT only on minimal authoritative scope-membership/config-version projection if required | Risk/Command/Ledger financial data; HaltState or EgressBoundaryAuthorization writes |
| Trusted Egress instance principal | Read only canonical persisted payload/attempt references it needs; EXECUTE on its own ConsumeEgressGrant, ReportSocketInitiated and bounded status operations | Direct control-table DML; grant issuance; Risk approval signing; alternative venue route |
| Risk / Command / Eligibility writers | EXECUTE on reviewed guard and domain-write procedures; mutate only their own domain records through those procedures | Direct bypass of common guard; direct HaltState/EgressBoundaryAuthorization writes |
| Operator / control principal | EXECUTE on authenticated halt/resume entrypoints subject to approved operator policy and dual control | Direct DML to control tables; venue socket or Risk signing authority |

The definer roles are not application identities and must never be used as connection login roles. They are dedicated NOLOGIN, NOINHERIT, non-superuser roles with NOBYPASSRLS, no privileged role memberships, no CREATEROLE/CREATEDB/REPLICATION and no ability to mutate source-domain records. The HEGC definer owner is not an owner of Risk/Command source tables.

## 3. Reviewed database entrypoints

The G1 API surface should remain small and typed:

1. **AuthorizeEgressAttempt** — one outer transaction: acquire the common guard first; validate the caller; read the complete authoritative Risk/Command/eligibility/evidence/dispatcher validation set; validate exact command/reservation/evidence/epoch/eligibility/fence bindings; persist one grant; return only an opaque grant/attempt reference.
2. **CommitHaltEpoch** — acquire the same common guard and commit a monotonic halt epoch. A halt-first ordering denies a later grant; a grant-first ordering leaves the attempt in-flight.
3. **ConsumeEgressGrant** — Egress-specific one-use transition from GATE_COMMITTED to GRANT_CONSUMED. Only a positive consume result permits one socket-write attempt.
4. **ReportSocketInitiated** — Egress-specific, attempt-bound report after the socket-write syscall has actually been invoked/returned. A pre-send local flag is not proof.
5. **GetAttemptStatus** — bounded status lookup by the same stable attempt ID; returns only the minimum metadata required to resolve an ambiguous response, not financial source records.

The common guard helper is internal to the reviewed database entrypoints and guarded domain-write procedures. General application roles do not receive direct EXECUTE on the helper.

## 4. SECURITY DEFINER hardening

PostgreSQL executes a SECURITY DEFINER function with the privileges of its owner. The following are mandatory qualification constraints:

- Definer owner is NOLOGIN, NOINHERIT, non-superuser, NOBYPASSRLS, has no privileged role memberships and is not the owner of source-domain tables.
- HEGC runtime and Egress login roles are distinct from definer owners and have no membership path that permits SET ROLE to a definer or privileged role.
- Every function fixes a trusted search_path with pg_catalog first, only trusted schemas next and pg_temp last; all security-sensitive objects are schema-qualified.
- No dynamic SQL, caller-supplied object names, untrusted function language or unsafe extension entrypoint is permitted in the privileged path.
- Revoke default PUBLIC EXECUTE and grant only explicit per-workload function signatures in the same DDL transaction that creates/replaces the function. Function overloads and accidental default grants are adversarial test cases.
- The HEGC runtime identity is authenticated through a distinct database principal. Inside SECURITY DEFINER, current_user is the definer; caller authentication uses session_user. Shared database logins, shared pooler server identities, caller-supplied identity/GUC values and runtime SET ROLE impersonation are disallowed.
- In v1, the single active Egress process generation must have a distinct database principal/credential mapped to its immutable workload generation and artifact digest. Reusing the same login across old/new Egress processes destroys this identity boundary. Role disable/revocation does not terminate an already-established backend session and is not a substitute for positive process/host/network fencing.
- The function owner returns only an opaque grant reference and bounded status. It must not return unrestricted source records or canonical financial payloads to the HEGC runtime.
- RLS behavior is tested explicitly. The definer owner must not have BYPASSRLS and must not own source tables; policies must permit only the intended source rows. Do not assume SECURITY DEFINER automatically bypasses or safely satisfies RLS.

Official PostgreSQL 18 guidance:
- CREATE FUNCTION / safe SECURITY DEFINER usage, search_path and PUBLIC EXECUTE: https://www.postgresql.org/docs/18/sql-createfunction.html
- session_user versus current_user and SECURITY DEFINER execution context: https://www.postgresql.org/docs/18/functions-info.html
- Role attributes including NOLOGIN, NOINHERIT and BYPASSRLS: https://www.postgresql.org/docs/18/role-attributes.html
- Role membership and SET ROLE behavior: https://www.postgresql.org/docs/18/role-membership.html
- Function security and untrusted languages: https://www.postgresql.org/docs/18/perm-functions.html

## 5. Transaction and commit-order contract

- All gate-critical source records and HEGC control records reside in the same logical PostgreSQL database on the authoritative primary for the G1 candidate.
- The outer transaction uses SERIALIZABLE; every writer that can invalidate the validation read set participates in the same protocol or the common guard protocol. SERIALIZABLE/SSI alone is not the required real-time commit-order barrier for overlapping transactions.
- The first data statement after BEGIN and transaction/session settings invokes the common guard. No protected read/write may occur first.
- The common guard is distinct from the Risk-owned exposure/scope-state guard. Acquire the HEGC account/root guard first, then child scope guards in canonical UUID-byte order; acquire Risk-owned root/child scope-state locks only afterward in the documented deterministic order.
- Every invalidating writer acquires/advances the same guard atomically with its source mutation and holds it through commit. The HEGC entrypoint holds it through grant commit.
- The guard function validates the complete bounded scope set against authoritative scope configuration after acquiring the root guard; it rejects duplicate/null/unknown/retired/incomplete scopes and unbounded fan-out. Guard rows are pre-provisioned; no hot-path row creation.
- A lock wait that leaves the transaction snapshot stale must force a full transaction retry (SQLSTATE 40001). 40P01 also retries the whole bounded transaction. Unknown commit outcome is resolved by the same attempt ID; never mint a replacement grant.
- Direct DML and advisory-lock-only bypasses are prohibited. The database must enforce that all relevant writers use guarded procedures.

The nexus_control.acquire_scope_guards(scope_ids uuid[]) SECURITY DEFINER helper is a candidate only. Its owner has guard-table write permission and, if needed, SELECT-only access to a minimal scope-membership/config-version projection. The exact helper, ownership, privileges, isolation and post-wait snapshot behavior remain unselected until PostgreSQL 18.7 multi-connection tests pass.

## 6. Attempt and halt semantics

The durable attempt lifecycle is:

GATE_COMMITTED → GRANT_CONSUMED → SOCKET_INITIATED

or, if the sender is positively isolated without a trusted initiation report:

GATE_COMMITTED / GRANT_CONSUMED → SENDER_FENCED_UNKNOWN

- GATE_COMMITTED and GRANT_CONSUMED block halt acknowledgement while the sender could still initiate.
- SOCKET_INITIATED permits halt acknowledgement only because the boundary has observed the one allowed socket attempt; the external effect remains potentially live and must be reconciled.
- SENDER_FENCED_UNKNOWN permits halt acknowledgement only because the old sender can no longer initiate a future write. It does not prove that no earlier side effect occurred. OUTCOME_UNKNOWN and the full reservation remain until authoritative venue reconciliation.
- Lost/ambiguous grant or consume responses are resolved using the same attempt ID. No second consume, replacement attempt, blind resend or reservation release.
- HALTED means no stale/queued sender can newly initiate after boundary acknowledgement. It does not mean all prior venue outcomes have been reconciled.

## 7. Adversarial qualification matrix

The following tests are required before implementation acceptance:

1. Default PUBLIC EXECUTE is absent immediately after function creation/replacement.
2. Temporary table, malicious schema object, operator/function overload and search_path spoof cannot redirect privileged SQL.
3. Runtime roles cannot create objects in trusted schemas or assume definer/owner roles.
4. Shared login, connection-pooler identity collapse, SET ROLE and caller-supplied GUC cannot impersonate another workload.
5. session_user remains the authenticated workload identity inside SECURITY DEFINER while current_user is the definer.
6. Egress generation N cannot consume a grant bound to generation N+1; old generation cannot use a new login after rotation.
7. Role disable/revoke while a backend session exists does not get misreported as process fencing; stale session and network path are independently isolated.
8. Definer owner cannot mutate Risk/Command/Ledger source records or read unrelated source fields.
9. RLS policies, table ownership and NOBYPASSRLS behave as intended for every source read.
10. Direct DML to guard/HaltState/EgressBoundaryAuthorization is denied to runtime roles.
11. A caller cannot bypass the common guard by reading protected state before invoking the helper.
12. Scope set omission, duplicate, NULL, unknown, retired, cross-account and fan-out-limit violations fail closed.
13. Root-first / canonical child order is deterministic under concurrent multi-scope operations.
14. Source-writer-first ordering forces HEGC to observe the committed update.
15. HEGC-first ordering forces the invalidating writer to serialize after grant commit.
16. Stale post-wait snapshot produces 40001 and a full transaction retry.
17. Guard transaction rollback/crash releases no partial grant and does not leak lock ownership.
18. Same attempt ID + same binding digest is idempotent; changed digest/scope/epoch/workload identity conflicts.
19. Lost grant response and lost consume response cannot create a second grant or send.
20. Socket initiation cannot precede GRANT_CONSUMED.
21. Process pause after GATE_COMMITTED or GRANT_CONSUMED blocks HALTED acknowledgement until observed initiation or positive sender fencing.
22. Sender fence without trusted initiation report remains SENDER_FENCED_UNKNOWN, OUTCOME_UNKNOWN and reservation-held.
23. HEGC outage, store outage, serialization retry exhaustion and ambiguous commit all fail closed.
24. Migration/rollback/restore preserves function ownership, ACLs, role memberships, guard rows and grant/halt state.
25. Lock contention, guard fan-out and p95/p99 latency are measured without weakening atomicity or guard ordering.

## 8. Open gates and disposition

- [ ] Select the concrete PostgreSQL guard/entrypoint implementation only after comparative least-privilege review.
- [ ] Build an isolated PostgreSQL 18.7 multi-connection harness and execute the full matrix above.
- [ ] Prove the exact database role graph, RLS policy behavior, function ownership, function ACLs and caller identity under the real connection/pooler topology.
- [ ] Prove positive Egress process/host/network fencing independently of database leases and role revocation.
- [ ] Prove crash, backup/restore, PITR, ambiguous commit and failover/recovery semantics.
- [ ] Measure throughput, lock wait, fan-out and tail latency.
- [ ] Obtain independent security review of SECURITY DEFINER code before any production deployment.

**Disposition:** architecture boundary and candidate controls are specified. No schema, function, role, connection or runtime is implemented. G0D/G1 remain open; production/live execution is not authorized. Owner decisions OD-08, OD-09, OD-10 and OD-12 remain open where they concern key custody, storage/isolation, recovery objectives and break-glass operations.
