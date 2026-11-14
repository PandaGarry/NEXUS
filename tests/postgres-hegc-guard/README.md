# PostgreSQL HEGC Guard Qualification Harness

**Status:** disposable test fixture; not production schema, migration or service code.

This harness exercises the proposed common guard protocol against a real PostgreSQL 18.7 server using independent psql connections. It is isolated under tests/ and creates only nexus_* test roles and schemas in a disposable CI database.

## Run

Requirements: Python 3.13, psql, and PostgreSQL 18.7 (server_version_num = 180007).

    PGHOST=127.0.0.1 PGPORT=5432 PGDATABASE=nexus_test PGUSER=postgres PGPASSWORD=postgres python tests/postgres-hegc-guard/test_harness.py

GitHub Actions runs the same harness with the postgres:18.7 service image in the PostgreSQL HEGC guard qualification workflow.

## What the fixture exercises

- Separate NOLOGIN / NOINHERIT / NOSUPERUSER / NOBYPASSRLS guard, HEGC-definer and writer-definer roles; distinct HEGC and source-writer login principals.
- An internal SECURITY DEFINER guard helper. It is not executable by application logins.
- The root/account guard is the first protected database operation. Caller authentication is part of that same root-guard UPDATE; scope membership is read only after the root guard is acquired.
- Complete scope-set validation against authoritative fixture membership, mandatory root-first locking and deterministic child UUID-byte ordering.
- One reviewed HEGC grant entrypoint and one reviewed source-writer entrypoint. Runtime logins have EXECUTE-only access and no direct source/control-table DML.
- Fixed search paths with pg_temp last, fully qualified relation references, exact-attempt retry identity and changed-binding conflict.
- Adversarial checks for direct SELECT/UPDATE/INSERT, helper invocation, SET ROLE, temp-object/search_path spoofing and caller-asserted custom-GUC identity.

## Concurrency contract tested

Each race uses two independent PostgreSQL sessions and observes the contender waiting on a row lock through pg_stat_activity.

1. **Writer first:** the source writer advances the guard and changes source state while holding the transaction open. HEGC waits, then PostgreSQL returns SQLSTATE 40001. The whole HEGC transaction is retried; the persisted grant snapshot includes the committed source change.
2. **HEGC first:** HEGC advances the same guard and commits its grant while holding the transaction open. The source writer waits, receives 40001, and retries the whole transaction. Its source change commits after the grant snapshot.

These are real PostgreSQL 18.7 multi-connection results, not a sequential Python simulation. The retry in the tests is explicit; the fixture does not add an application retry framework.

## Verified result

Exact code/test HEAD 972ae546e432448ae995dee868b21194756b14e1 passed workflow #43621246827: **5 tests passed** on PostgreSQL 18.7, including both commit-order races. The Python reference-model workflow #43621246829 also passed on the same HEAD. Job logs were inspected; no ResourceWarnings remained after subprocess stream cleanup.

## Explicit limitations

This fixture proves only the behavior of these test-only SQL functions and role grants. It does not establish production schema correctness, production caller identity, complete NEXUS source-writer participation, RLS policy correctness, concurrent duplicate-attempt serialization, scope-membership mutation races, crash/ambiguous-commit recovery, halt-epoch semantics, Egress process identity, socket initiation, host/network fencing, venue reconciliation, backup/PITR or production readiness.

The test binding_digest is an opaque fixture string, not a cryptographic canonicalization or signature. The image is selected by the postgres:18.7 tag; image digest/provenance pinning remains open. No production role, credential, database, schema or service is created by this work.
