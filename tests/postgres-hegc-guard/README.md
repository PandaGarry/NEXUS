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
- A dedicated membership-administration entrypoint: additions and deactivations take the same root-first guard and validate the complete pre-change scope set.
- Forced RLS on the fixture source table; policies bind HEGC and writer access to session_user and account authorization metadata.
- The root/account guard is the first protected database operation. Caller authentication is part of that same root-guard UPDATE; scope membership is read only after the root guard is acquired.
- Complete scope-set validation against authoritative fixture membership, mandatory root-first locking and deterministic child UUID-byte ordering; an explicitly permuted child array is rejected.
- One reviewed HEGC grant entrypoint and one reviewed source-writer entrypoint. Runtime logins have EXECUTE-only access and no direct source/control-table DML.
- Fixed search paths with pg_temp last, fully qualified relation references, exact-attempt retry identity and changed-binding conflict.
- Adversarial checks for direct SELECT/UPDATE/INSERT, helper invocation, SET ROLE, temp-object/search_path spoofing and caller-asserted custom-GUC identity.
- Concurrent duplicate attempt: the blocked duplicate receives 40001, retries the whole transaction and receives the original grant.
- Lost post-commit client response: the caller connection is terminated after grant commit but before the client consumes the response; retry by the same attempt ID returns the committed grant.

## Concurrency contract tested

Each race uses independent PostgreSQL sessions and observes the contender waiting on a row lock through pg_stat_activity.

1. **Writer first:** the source writer advances the guard and changes source state while holding the transaction open. HEGC waits, then PostgreSQL returns SQLSTATE 40001. The whole HEGC transaction is retried; the persisted grant snapshot includes the committed source change.
2. **HEGC first:** HEGC advances the same guard and commits its grant while holding the transaction open. The source writer waits, receives 40001, and retries the whole transaction. Its source change commits after the grant snapshot.
3. **Concurrent duplicate:** two HEGC sessions use the same attempt ID and binding. The second session is forced to retry after 40001 and then resolves to the first committed grant.
4. **Lost response:** the grant commits, the client process is terminated before consuming the response, and an exact retry returns the same durable grant ID.
5. **Membership mutation:** an authorized administrator adds a scope while a gate transaction is blocked on the root guard. The stale gate receives 40001; a full retry with the expanded authoritative scope set succeeds. Deactivation then makes the former complete set fail closed.

These are real PostgreSQL 18.7 multi-connection results, not a sequential Python simulation. The retry in the tests is explicit; the fixture does not add an application retry framework.

## Verified result

Exact code/test HEAD 614f22f3bbff879d91c040eb73511a90fe7d32ef passed [PostgreSQL workflow #43628329933](https://github.com/PandaGarry/NEXUS/actions/runs/43628329933): **8 tests passed** on PostgreSQL 18.7, including scope-membership addition/deactivation races and forced RLS. The Python reference-model workflow [#43628329956](https://github.com/PandaGarry/NEXUS/actions/runs/43628329956) passed 13 suites / 264 tests on each of Python 3.11, 3.12 and 3.13 (792 executions). Job logs were inspected; no ResourceWarnings, test failures or deprecation warnings remained.

The earlier PostgreSQL run #43621620302 correctly exposed a harness orchestration error: the simulated response-loss process slept before COMMIT, so the grant was not visible to the independent observer. The test was corrected to sleep after COMMIT, and the exact corrected head passed.

## Explicit limitations

This fixture proves only the behavior of these test-only SQL functions and role grants. Its RLS test is limited to the fixture source table and two fixture policies; it does not establish production policy correctness. It does not establish production schema correctness, production caller identity, complete NEXUS source-writer participation, service-principal/authorization-map mutation races, crash/restore, halt-epoch semantics, Egress process identity, socket initiation, host/network fencing, venue reconciliation, backup/PITR or production readiness. The lost-response case tests a committed grant whose client response is lost; it is not a complete crash/failover or uncertain-COMMIT recovery qualification.

The test binding_digest is an opaque fixture string, not a cryptographic canonicalization or signature. The image is selected by the postgres:18.7 tag; image digest/provenance pinning remains open. No production role, credential, database, schema or service is created by this work.


The documentation-only synchronization HEAD 806832a2a15ea25376408c7d27cde409438451ce also triggered CI: PostgreSQL workflow #43628569042 passed all 8 tests, and Python workflow #43628569028 passed 264 tests on each of Python 3.11, 3.12 and 3.13. No source/test changes were made after the verified code/test HEAD.
