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

**Final disposition:** PostgreSQL 18.7 is the current G1 evaluation patch target only. Production database selection, hosting, replication, backup retention, RPO/RTO, failover and financial correctness remain unapproved and evidence-gated.
