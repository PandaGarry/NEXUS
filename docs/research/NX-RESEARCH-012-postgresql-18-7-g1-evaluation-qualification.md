# NX-RESEARCH-012 — PostgreSQL 18.7 G1 Evaluation Qualification

**Date:** 2026-11-14  
**Status:** RESEARCH / EVALUATION TARGET SELECTED — no database installed, deployed or approved for production  
**Scope:** OD-09, NX-ADR-008 §5, NX-ARCH-REVIEW-007, NX-IF-002  
**Related:** NX-RESEARCH-010, NX-OWNER-DECISIONS-001

## 1. Executive disposition

Select **PostgreSQL 18.7** as the exact patch-level target for the first G1 database qualification harness. PostgreSQL 18 remains the architectural candidate; 18.7 is the current supported minor release as of 2026-11-14 and was released on 2026-11-12.

This is a bounded test target, not a production deployment decision. Before any G1 harness is built, verify the actual vendor/package build, source provenance, checksums, supported platform, configuration, extensions (none are currently allowed), and current security advisories. Before any later deployment, re-check the newest supported PostgreSQL 18 minor release; do not freeze 18.7 as a permanent production pin.

The 18.7 release announcement states that it fixes 52 security vulnerabilities and more than 140 bugs. Its own migration notes include material caveats about index corruption and incremental backups. The G1 test environment must account for these caveats rather than treating a minor update as risk-free.

## 2. Patch-level selection

| Item | Decision |
|---|---|
| Major line | PostgreSQL 18 |
| G1 evaluation patch | **18.7** |
| Release date | 2026-11-12 |
| Support status on review date | Supported |
| Production approval | Not granted |
| Deployment provider / region | Not selected |
| Package/image digest and build provenance | Open qualification item |
| Extensions | None permitted in initial G1 harness |
| Replication/failover | No automatic failover or active-active writer |

The patch target is evidence-based and time-bounded. A later supported 18.x security release supersedes 18.7 for a new qualification run after its release notes and migration requirements are reviewed.

## 3. Release-note caveats that affect NEXUS

### 3.1 Index integrity and backup implications

The official 18.7 migration notes warn that several earlier bugs could cause index corruption. They instruct operators to inspect entries mentioning `REINDEX` and rebuild affected indexes where applicable. They also state that existing incremental backup files should not be trusted because of discovered corruption paths; users of incremental backups are advised to take a new full backup after updating and use it as the basis for subsequent incremental backups.

G1 requirements:

- Start the evaluation cluster from a fresh 18.7 initialization or a verified migration path with a documented index-integrity review.
- Do not carry forward incremental backup chains created before the relevant fix level. The initial G1 backup/restore exercise uses a new full base backup.
- The first G1 design remains single-primary with no automatic failover. PITR and restore must be exercised from a fresh, verified base backup plus WAL.
- Review the full 18.7 release notes for every `REINDEX` entry against the actual schema/index types before using migrated data.
- Avoid unconstrained `bpchar` columns (the release-note issue concerns the type without a length constraint); the PostgreSQL 18.7 notes explicitly say ordinary fixed-length `CHAR(n)` is not affected by this specific bug. Prefer TEXT/VARCHAR for new schema unless fixed-width semantics are required. Avoid GIN and `gist_trgm_ops` indexes in the initial schema unless a concrete need exists and the relevant reindex/recovery requirements are explicitly qualified. No index is presumed safe merely because the server has been patched.

### 3.2 C extensions and extension scripts

The release notes describe composite-type safety changes that require rebuilding C-language extensions for full protection; some extensions may require source changes. They also document extension-script privilege/schema issues fixed in this release.

G1 requirements:

- No C-language or third-party PostgreSQL extension in the initial evaluation harness.
- No `CREATE EXTENSION` from unreviewed or mutable sources.
- Any future extension requires exact-version/source/license/provenance review, source compatibility review against PostgreSQL 18.7 or its successor, least-privilege installation, and explicit security review.
- Do not disable `composite_type_mismatch` protections to work around compatibility failures.

### 3.3 Privilege and SQL execution boundaries

18.7 fixes several security issues directly relevant to database isolation and privileged operations: CVE-2026-16237 (`INSERT ... ON CONFLICT` could bypass an auto-updatable view's WHERE visibility), CVE-2026-120154 (ON CONFLICT row visibility against RLS), CVE-2026-14661 (`dblink`/replication subscriptions could append arbitrary files), CVE-2026-6460 (concurrent composite-type changes could trigger type confusion/code execution), CVE-2026-6467 (extension script schema handling could execute arbitrary SQL), and CVE-2026-116314 (corrupt `pg_restore` archives could trigger out-of-bounds access/path traversal).

G1 requirements:

- Authoritative Risk/Command/Ledger writes target base tables through narrowly scoped service roles; auto-updatable views are not write APIs.
- Row-level security, if later used, is defense-in-depth and is not the only tenant/service isolation boundary. Prove base-table grants and cross-role access independently, including ON CONFLICT paths.
- Database role grants, schema ownership and SECURITY DEFINER functions require explicit review; no shared application superuser. Runtime roles receive no SUPERUSER, CREATEDB, CREATEROLE, REPLICATION, BYPASSRLS, pg_read_all_data, pg_write_all_data, pg_read_server_files, pg_write_server_files or pg_execute_server_program privileges; they cannot SET ROLE to schema owners and have no schema/extension DDL privileges.
- Do not install or enable `dblink`, replication subscriptions, untrusted extensions or dynamic extension/script execution in the initial G1 environment.
- C-language extensions are excluded; any later C extension must be rebuilt and requalified for PostgreSQL 18.7 and the current server patch.
- Do not restore untrusted `pg_restore` archives or treat backup manifests as trusted input. All imports are bounded, validated and performed by a narrowly scoped process.

## 4. Implications for the selected transaction model

The PostgreSQL 18.7 release does not change the NX-ADR-008 transaction model:

- Risk-owned scope-state remains the serialization point for reservations and discrete economic exposure-projection changes.
- PostgreSQL SERIALIZABLE remains the default G1 evaluation isolation level, with whole-transaction bounded retry for 40001 and cautious whole-transaction retry for 40P01.
- Expected idempotency 23505 is resolved by a fresh authoritative-primary read of the same request identity and digest; unrelated unique/exclusion failures fail closed.
- No advisory lock or database fencing token is treated as an external venue socket fence.
- No automatic failover is allowed before old-primary fencing, ambiguous commit recovery, backup/restore and egress reconciliation are proven.

The 18.7 release contains a fix to `INSERT ... ON CONFLICT` behavior, but NEXUS must still prove its own transaction protocol, row ownership, idempotency constraints and crash semantics. A database release fix does not establish application-level correctness.

### 4.1 HEGC cross-schema read/write consistency

The HEGC final-gate transaction writes only its control-owned schema but reads the gate-critical Risk/Command/eligibility/evidence/dispatcher state. The transaction must run at SERIALIZABLE on the **same logical PostgreSQL database and authoritative primary** as those records. This guarantee is not obtained by running only HEGC at SERIALIZABLE: every transaction that mutates a row/version in HEGC's validation read set must participate in the same SERIALIZABLE protocol or a separately proven shared version/CAS guard. A weaker writer or stale replica is a bypass and blocks grant issuance.

- PostgreSQL's SERIALIZABLE guarantee applies to the set of participating serializable transactions; HEGC and each relevant source writer need a bounded whole-transaction retry path for SQLSTATE 40001. Deadlock 40P01 also requires a bounded retry policy with the whole transaction restarted.
- HEGC has SELECT-only privileges on source schemas and write privileges only in its control schema. PostgreSQL requires UPDATE privilege on at least one column for `SELECT ... FOR SHARE/UPDATE`; do not quietly grant HEGC source-table UPDATE solely to obtain row locks. If serializable predicate/conflict tracking plus source-writer participation cannot be proven, use a separately reviewed least-privilege lock/version API or fail closed.
- Advisory locks are application-defined; PostgreSQL does not force every writer to acquire them. They are not an acceptable sole guard unless direct DML is revoked and every relevant write is forced through a reviewed procedure that acquires the same lock.
- Gate-critical reads must not come from asynchronous replicas. A different database, cross-cluster source or independently lagging replica needs a new consistency/fencing design; do not treat a matching version string as proof of a common atomic snapshot.
- HEGC grant issuance is idempotent on stable attempt ID. On serialization retry or ambiguous commit, resolve the same attempt ID and digest; never issue a second grant or a replacement attempt while the first may still send.

These requirements are design/qualification constraints, not evidence that the HEGC transaction, role grants or database schema exists.

### 4.2 SERIALIZABLE is not a commit-order barrier

PostgreSQL SERIALIZABLE guarantees that successfully committed participating transactions are equivalent to some serial execution order. It does not promise that this serial order is identical to wall-clock commit order for overlapping transactions. PostgreSQL takes a transaction snapshot at its first non-transaction-control statement and uses Serializable Snapshot Isolation (SSI) to detect dangerous read/write dependency structures; SSI is not a strict-serializability or linearizability primitive. Consequently, participation by HEGC and every source writer is necessary but may still be insufficient for the stronger contract that every source mutation committed before the HEGC grant commit must be visible to that grant.

For the required real-time ordering, G1 MUST additionally prove an enforced common per-scope serialization barrier. Candidate design for evaluation:

- A gate-critical scope-generation/guard record is shared by HEGC and every writer capable of invalidating the validation read set.
- Every source writer and HEGC must acquire the relevant guard as the **first data statement after BEGIN and transaction-isolation/session settings**, before any read or write in the protected validation set. Acquiring it after a snapshot or protected read is established is invalid; the transaction must abort and restart with the guard first.
- Each source writer atomically advances/locks the relevant guard in the same transaction as its source mutation. HEGC atomically advances/locks the same guard before its validation reads and commits the grant in that transaction. A writer holding the guard first must commit before HEGC can validate; HEGC holding it first prevents the source mutation from committing until after the grant.
- The guard protocol must guarantee a fresh post-wait view or force a whole-transaction retry when the transaction snapshot predates a concurrent guard update. The lock remains held through commit. Multi-scope operations acquire guards in deterministic sorted order, with the root/account guard first.
- **Least-privilege implementation candidate:** a dedicated coordination schema with guard rows owned by a non-login role and a narrowly scoped `SECURITY DEFINER` function (fixed `search_path`, fully qualified object names, no dynamic SQL, PUBLIC execution revoked) that advances/locks sorted guard rows. HEGC and each participating writer receive EXECUTE only; direct guard/source DML bypasses are revoked. This is a candidate for G1 qualification, not a selected implementation. The guard function by itself does not prevent a caller from performing protected reads before invoking it. G1 must therefore either expose one reviewed HEGC transaction entrypoint that acquires the guard before performing any validation read and writing the grant, or enforce a transaction API in which the guard call is the first SQL statement and every invalidating writer can mutate source state only through guarded procedures. A caller convention without a DB-enforced no-bypass path is insufficient.
- Enforce participation at the database boundary: revoke direct source DML paths that bypass the guard and route writes through reviewed procedures/roles. An application convention or advisory lock that any writer can omit is not proof. Preserve least privilege; HEGC must not receive broad UPDATE access to Risk/Command source tables just to acquire locks.
- Keep SERIALIZABLE as defense in depth and retain bounded whole-transaction retry for 40001/40P01. A generation string read without an atomic shared guard is not proof of a common commit order.

### Recommended G1 guard-function implementation shape

The preferred G1 mechanism to evaluate is a narrowly scoped database-owned function, not direct cross-service DML:

- Internal guard helper candidate: `nexus_control.acquire_scope_guards(scope_ids uuid[])`. It is not directly exposed to application service roles. It rejects null, duplicate, unknown and over-limit scope IDs; requires the mandatory account/root scope; verifies the requested scope set against authoritative scope-membership/configuration data; and advances/locks guard rows in deterministic order (root/account first, then canonical UUID-byte order). Caller-supplied scope lists alone are not proof of completeness. The root guard serializes scope-membership changes while the complete affected set is derived/validated; every operation must acquire every guard relevant to its read/write set before touching protected business rows.
- The internal helper is `SECURITY DEFINER`, owned by a dedicated `NOLOGIN`, non-superuser `nexus_guard_owner` role. That owner may SELECT the minimal service-authorization/scope-membership metadata and SELECT/UPDATE only the guard table; it has no privileges on Risk/Command/Ledger source or HEGC grant tables and does not own the source or coordination schemas.
- **HEGC entrypoint candidate:** expose only a reviewed `nexus_control.issue_egress_grant(...)` transaction entrypoint to the HEGC service role. Its separate `NOLOGIN`/non-superuser owner has SELECT-only access to the exact gate-critical source records, write access only to HEGC control/grant records, and EXECUTE on the internal guard helper. The entrypoint itself must acquire the root and complete affected-scope guards as its first transaction operation, then read/validate the source set and write the grant in that same outer SERIALIZABLE transaction. HEGC's application role receives no direct SELECT on protected source tables and no direct DML on guard/grant tables. Each source domain similarly exposes only reviewed guarded write procedures; direct source DML is revoked from service roles. This is a candidate boundary design, not an implemented schema or approved SQL API.
- **Caller identity must be database-authenticated, not caller-asserted.** Inside SECURITY DEFINER, `current_user` is the function owner; use `session_user` only with a dedicated non-shared login per service/workload, explicit mapping to allowed operations/scopes, and no shared pool login or `SET ROLE` impersonation path. If the deployment cannot preserve a distinct authenticated principal at the database connection, this SECURITY DEFINER candidate is not qualified; do not substitute an untrusted custom GUC or a caller-supplied role name. PostgreSQL documents the distinction between session_user and current_user and the SECURITY DEFINER context change [here](https://www.postgresql.org/docs/18/functions-info.html).
- Fix `search_path` to trusted schemas with `pg_temp` last; schema-qualify every object; prohibit dynamic SQL, caller-supplied object names and untrusted languages/extensions. The control schema is not writable by service roles.
- Revoke function EXECUTE from PUBLIC and grant it only to explicit, reviewed domain-writer and HEGC roles in the same DDL transaction. Callers receive no direct DML rights on the guard table. No direct source-table DML path may bypass reviewed domain-write procedures.
- Every domain write and HEGC final-gate transaction is entered only through its reviewed database procedure/entrypoint. The caller invokes that entrypoint as the first data statement after BEGIN and transaction-isolation/session settings; the procedure's first internal operation is guard acquisition, followed by protected reads/writes, all in the same outer SERIALIZABLE transaction. Source mutation or grant write commits while locks remain held. The helper MUST NOT commit independently or swallow/retry internally. Revoke application-role access that would permit an earlier protected SELECT or direct DML; a standalone helper call followed by arbitrary application SQL is not an enforceable protocol.
- If a SERIALIZABLE snapshot predates a concurrent guard update while waiting, the operation must surface 40001 and restart the whole transaction from a fresh snapshot; the retry begins with guard acquisition, before any protected read/write.
- Security-definer ownership, session identity, fixed search_path, PUBLIC revocation, role inheritance, function overloading, temporary-object spoofing, SQL injection, scope-set completeness, max fan-out, deterministic lock order, guard bypass, deadlock and crash recovery all require adversarial tests.

This pattern preserves service ownership of source tables while giving the common guard one narrow, audited write authority. It is a G1 evaluation candidate, not an implementation or production approval.

This guard remains a design candidate, not a selected production mechanism. A disposable PostgreSQL 18.7 fixture now proves the initial writer-first and HEGC-first multi-connection ordering cases: the blocked stale transaction receives SQLSTATE 40001 and succeeds only after a whole-transaction retry. The same fixture checks root-first/complete scope locking, basic role/ACL closure, direct-DML denial, SET ROLE, search_path/temp-object and custom-GUC spoofing, and exact grant retry binding; see tests/postgres-hegc-guard/README.md and workflow #43621246827. This is fixture-level evidence only. Before G1, extend qualification to pause/crash points, RLS, concurrent duplicate attempts, ambiguous commit recovery, scope-membership mutation, role/ACL closure under the actual connection topology, full migration/restore behavior and independent security review. Until the production commit-order property is demonstrated, HEGC MUST deny a final grant whenever it cannot prove the bound validation state is current under the common guard.

**Why this matters:** the existing contract says updates committed before the final gate are visible and updates committed after it are causally later. That is a real-time ordering requirement; ordinary SSI serializability alone must not be represented as proof.






### 4.3 SECURITY DEFINER entrypoint and caller identity

The preferred G1 HEGC shape is an EXECUTE-only runtime principal invoking a small set of reviewed SECURITY DEFINER entrypoints. The definer owner performs the bounded source read set and writes only HEGC control state; the application runtime has no direct SELECT on Risk/Command/evidence/eligibility/dispatcher source tables and no direct DML on guard, HaltState or EgressBoundaryAuthorization. A separate guard-function owner writes only the common guard and reads only minimal scope-membership/config-version metadata.

Mandatory constraints:

- Definer owners are NOLOGIN, NOINHERIT, non-superuser, NOBYPASSRLS, have no privileged role memberships, and are not owners of source-domain tables. They have no CREATEROLE, CREATEDB or REPLICATION privilege.
- Every SECURITY DEFINER function fixes search_path to pg_catalog first, trusted schemas next and pg_temp last; all security-sensitive objects are schema-qualified. No dynamic SQL, caller-supplied object names or untrusted language is allowed.
- PostgreSQL grants EXECUTE on new functions to PUBLIC by default. Revoke PUBLIC EXECUTE and issue only explicit per-workload grants in the same DDL transaction that creates/replaces the function. Test function overloads and accidental grants.
- Inside SECURITY DEFINER, current_user is the definer owner; session_user is the authenticated database login. Caller authorization must use the authenticated session principal, not current_user, caller-supplied GUCs or JSON identity fields. Runtime roles have no membership path to a definer/privileged role and cannot SET ROLE into one.
- HEGC and Egress must not share a database login. In v1, each Egress process generation has a distinct database principal/credential mapped to its immutable workload generation, artifact digest and environment in a trusted registry. The grant binds to that generation. A shared connection-pooler server login collapses session_user and invalidates the identity guarantee unless the pooler preserves distinct authenticated server principals.
- Disabling a role, setting NOLOGIN or rotating its credential does not terminate an already established backend session and is not proof that the old process/socket is fenced. Terminate/revoke the database session and independently prove process/host/network fencing; a database principal is identity evidence, not a transport fence.
- Definer owners must not have BYPASSRLS and must not own source tables. PostgreSQL superusers and BYPASSRLS roles bypass RLS; table owners normally bypass it unless FORCE ROW LEVEL SECURITY is enabled. Test the actual RLS policies under the definer owner and verify only intended source rows are visible.
- The entrypoint returns only an opaque grant reference and bounded attempt status. It must not return unrestricted source records or canonical financial payloads to the HEGC runtime.

This is a G1 qualification requirement. The fixture contains test-only analogues of these functions and roles; no production database functions, roles, schemas or credentials exist.

## 5. G1 qualification checklist

- [ ] Pin the exact PostgreSQL 18.7 distribution, package checksum/image digest and build provenance.
- [ ] Verify the host OS/architecture and supported deployment platform.
- [ ] Record complete configuration and server build metadata; prohibit unreviewed extensions.
- [ ] Review all PostgreSQL 18.7 release-note `REINDEX` entries against actual schema/index definitions.
- [ ] Use a new full backup as the base for G1 backup/PITR exercises; do not trust old incremental backup chains.
- [ ] Test crash recovery, full restore, PITR, WAL continuity and corruption detection.
- [ ] Verify base-table-only authoritative writes, separate schema ownership and least-privilege service roles.
- [ ] Test SERIALIZABLE concurrency, 40001/40P01 whole-transaction retry, expected/unexpected 23505, ambiguous commit and scope-state serialization.
- [ ] Benchmark reservation/projection p50/p95/p99 latency and lock contention under realistic v1 single-account fan-out.
- [ ] Recheck current supported minor version and security advisories immediately before any future deployment decision.

## 6. Official sources

- PostgreSQL Global Development Group, PostgreSQL 18.7 release announcement (2026-11-12): https://www.postgresql.org/about/news/postgresql-187-1712-1616-1520-1425-and-19-rc-2-released-3442/
- PostgreSQL 18.7 release notes and migration caveats: https://www.postgresql.org/docs/18/release-18-7.html
- PostgreSQL versioning policy / supported minor releases: https://www.postgresql.org/support/versioning/
- PostgreSQL 18.7 transaction serialization failure handling: https://www.postgresql.org/docs/18/mvcc-serialization-failure-handling.html
- PostgreSQL 18.7 transaction isolation: https://www.postgresql.org/docs/18/transaction-iso.html
- PostgreSQL source-level SSI design notes (including serialization dependencies and WAL replay considerations): https://github.com/postgres/postgres/blob/master/src/backend/storage/lmgr/README-SSI
- O'Neil & O'Neil, “Determining serialization order for serializable snapshot isolation,” Information Systems 58 (2016), DOI: https://doi.org/10.1016/j.is.2016.02.001 — documents that SSI serialization order need not equal commit order.
- PostgreSQL Wiki, Serializable — explanation of apparent serial order under SSI and its distinction from commit order: https://wiki.postgresql.org/wiki/Serializable
- PostgreSQL 18 privileges: `SELECT FOR SHARE/UPDATE` requires UPDATE privilege on at least one column: https://www.postgresql.org/docs/18/ddl-priv.html
- PostgreSQL 18 SECURITY DEFINER function safety: fixed trusted search_path, `pg_temp` last and explicit PUBLIC EXECUTE revocation: https://www.postgresql.org/docs/18/sql-createfunction.html
- PostgreSQL 18 function security / trusted object ownership: https://www.postgresql.org/docs/18/perm-functions.html
- PostgreSQL 18 explicit/advisory locking: advisory locks are application-defined and not enforced for all writers: https://www.postgresql.org/docs/18/explicit-locking.html
- PostgreSQL 18 application-level consistency / SERIALIZABLE caveats: https://www.postgresql.org/docs/18/applevel-consistency.html

**Final disposition:** PostgreSQL 18.7 is the current G1 evaluation patch target only. Production database selection, hosting, replication, backup retention, RPO/RTO, failover and financial correctness remain unapproved and evidence-gated.
- PostgreSQL 18 CREATE FUNCTION and SECURITY DEFINER guidance (search_path, default PUBLIC EXECUTE): https://www.postgresql.org/docs/18/sql-createfunction.html
- PostgreSQL 18 session_user/current_user semantics: https://www.postgresql.org/docs/18/functions-info.html
- PostgreSQL 18 role attributes (NOLOGIN, NOINHERIT, BYPASSRLS): https://www.postgresql.org/docs/18/role-attributes.html
- PostgreSQL 18 role membership and SET ROLE: https://www.postgresql.org/docs/18/role-membership.html
- PostgreSQL 18 function security and untrusted languages: https://www.postgresql.org/docs/18/perm-functions.html
- PostgreSQL 18 row security policies and table-owner bypass: https://www.postgresql.org/docs/18/ddl-rowsecurity.html
