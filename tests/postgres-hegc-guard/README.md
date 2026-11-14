# PostgreSQL HEGC Guard Qualification Harness

**Status:** disposable test fixture; not production schema, migration or service code.

This harness exercises the proposed common guard protocol against a real PostgreSQL 18.7 server using independent psql connections. It is isolated under tests/ and creates only nexus_* test roles and schemas in a disposable CI database.

## Run

Requirements: Python 3.13, psql, and PostgreSQL 18.7 (server_version_num = 180007).

    PGHOST=127.0.0.1 PGPORT=5432 PGDATABASE=nexus_test PGUSER=postgres PGPASSWORD=postgres python tests/postgres-hegc-guard/test_harness.py

GitHub Actions runs the same harness with the Docker Official Image pinned by multi-platform index digest `sha256:9f4fd4aa918f52ae3d6f3b687f1de90d8f867cd4d520021545a9a50c120eae3b`. The `linux/amd64` child manifest is `sha256:c7fedce47eff6a78cb35dad6b627f0d684107f75ab15c0870e40c093766ba452`; both were checked on [Docker Hub's official postgres:18.7 image page](https://hub.docker.com/layers/library/postgres/18.7/images/sha256-c7fedce47eff6a78cb35dad6b627f0d684107f75ab15c0870e40c093766ba452).

## What the fixture exercises

- Separate NOLOGIN / NOINHERIT / NOSUPERUSER / NOBYPASSRLS guard, HEGC-definer and writer-definer roles; distinct HEGC and source-writer login principals.
- An internal SECURITY DEFINER guard helper. It is not executable by application logins.
- Dedicated membership and service-principal administration entrypoints: scope additions/deactivations and service-principal activation/revocation take the same root-first guard and validate the complete pre-change scope set. Self-revocation is rejected.
- Forced RLS on the fixture source table; policies bind HEGC and writer access to session_user and account authorization metadata.
- The root/account guard is the first protected database operation. Caller authentication is part of that same root-guard UPDATE; scope membership is read only after the root guard is acquired.
- Complete scope-set validation against authoritative fixture membership, mandatory root-first locking and deterministic child UUID-byte ordering; an explicitly permuted child array is rejected.
- One reviewed HEGC grant entrypoint and one reviewed source-writer entrypoint. Runtime logins have EXECUTE-only access and no direct source/control-table DML.
- Fixed search paths with pg_temp last, fully qualified relation references, exact-attempt retry identity and changed-binding conflict.
- Adversarial checks for direct SELECT/UPDATE/INSERT, helper invocation, SET ROLE, temp-object/search_path spoofing and caller-asserted custom-GUC identity.
- Negative runtime-role tests for role creation/escalation, definer-role membership grants, PUBLIC EXECUTE grants, SECURITY INVOKER alteration, default-privilege changes against the definer owner and trusted-schema function creation.
- Restrictive RLS composition: a restrictive HEGC SELECT policy excludes a negative source row from the SECURITY DEFINER snapshot despite the permissive policy.
- Concurrent duplicate attempt: the blocked duplicate receives 40001, retries the whole transaction and receives the original grant.
- Lost post-commit client response: the caller connection is terminated after grant commit but before the client consumes the response; retry by the same attempt ID returns the committed grant.

## Concurrency contract tested

Each race uses independent PostgreSQL sessions and observes the contender waiting on a row lock through pg_stat_activity.

1. **Writer first:** the source writer advances the guard and changes source state while holding the transaction open. HEGC waits, then PostgreSQL returns SQLSTATE 40001. The whole HEGC transaction is retried; the persisted grant snapshot includes the committed source change.
2. **HEGC first:** HEGC advances the same guard and commits its grant while holding the transaction open. The source writer waits, receives 40001, and retries the whole transaction. Its source change commits after the grant snapshot.
3. **Concurrent duplicate:** two HEGC sessions use the same attempt ID and binding. The second session is forced to retry after 40001 and then resolves to the first committed grant.
4. **Lost response:** the grant commits, the client process is terminated before consuming the response, and an exact retry returns the same durable grant ID.
5. **Membership mutation:** an authorized administrator adds a scope while a gate transaction is blocked on the root guard. The stale gate receives 40001; a full retry with the expanded authoritative scope set succeeds. Deactivation then makes the former complete set fail closed.
6. **Authorization revocation:** a membership administrator revokes a HEGC service-principal mapping while a gate is blocked. The stale gate receives 40001; a full retry is denied with 42501. The mapping can be restored through the same guarded entrypoint.

These are real PostgreSQL 18.7 multi-connection results, not a sequential Python simulation. The retry in the tests is explicit; the fixture does not add an application retry framework.

## Verified result

Exact code/test HEAD b1b39dee3eddea3503d785fe54d9306013529eb9 passed [PostgreSQL workflow #43628823064](https://github.com/PandaGarry/NEXUS/actions/runs/43628823064): **9 tests passed** on PostgreSQL 18.7, including scope-membership addition/deactivation, service-principal revocation races and forced RLS. The Python reference-model workflow [#43628823097](https://github.com/PandaGarry/NEXUS/actions/runs/43628823097) passed 13 suites / 264 tests on each of Python 3.11, 3.12 and 3.13 (792 executions). Job logs were inspected; no ResourceWarnings, test failures or deprecation warnings remained.

The earlier PostgreSQL run #43621620302 correctly exposed a harness orchestration error: the simulated response-loss process slept before COMMIT, so the grant was not visible to the independent observer. The test was corrected to sleep after COMMIT, and the exact corrected head passed.

## Explicit limitations

This fixture proves only the behavior of these test-only SQL functions and role grants. Its RLS tests are limited to the fixture source table and fixture policies; they do not establish production policy correctness. It does not establish production schema correctness, production caller identity, complete NEXUS source-writer participation, DBA/superuser role or ACL mutation safety, catalog-manifest drift detection, migration governance, crash/restore, halt-epoch semantics, Egress process identity, socket initiation, host/network fencing, venue reconciliation, backup/PITR or production readiness. The lost-response case tests a committed grant whose client response is lost; it is not a complete crash/failover or uncertain-COMMIT recovery qualification.

The test binding_digest is an opaque fixture string, not a cryptographic canonicalization or signature. The CI image index is digest-pinned; signed build provenance, SBOM retention, vulnerability disposition and independent image review remain open. No production role, credential, database, schema or service is created by this work.


The documentation-only synchronization HEAD 806832a2a15ea25376408c7d27cde409438451ce also triggered CI: PostgreSQL workflow #43628569042 passed all 8 tests, and Python workflow #43628569028 passed 264 tests on each of Python 3.11, 3.12 and 3.13. No source/test changes were made after the verified code/test HEAD.

## Additional privilege and RLS regression scope

The new runtime tests deliberately attempt PostgreSQL role/ACL operations from each fixture login. Expected denial is limited to those runtime identities and exact statements. PostgreSQL superuser/DBA changes remain outside the application row-guard protocol and require a separate reviewed migration/control-plane process, catalog-manifest drift detection, audit and session termination/reconciliation. The restrictive-policy test checks one composition case only; owner bypass, role inheritance combinations, policy subqueries and covert channels remain open.

## Latest exact code/test verification

Code/test HEAD `07373e88109bd492d3b0f7c0ab1491e0bb1ab7bf` passed [PostgreSQL workflow #43629845855](https://github.com/PandaGarry/NEXUS/actions/runs/43629845855): **11/11 tests** on PostgreSQL 18.7. New coverage includes runtime-role privilege-escalation denial and restrictive RLS composition. Python reference-model workflow [#43629845861](https://github.com/PandaGarry/NEXUS/actions/runs/43629845861) passed 13 suites / **264 tests per runtime** on Python 3.11, 3.12 and 3.13 (792 executions). All four job logs were inspected; no failures or ResourceWarning/DeprecationWarning matches were found.

The initial test iteration exposed a harness assertion issue, not a database privilege escalation: PostgreSQL can treat a non-owner GRANT attempt as a warning/no-op when the role can resolve the schema, while a role without schema USAGE receives 42501. The corrected regression checks both the role's schema visibility and the effective function ACL after the attempt; the PUBLIC grant must not appear in effective privileges.

## PostgreSQL container image pin

The workflow pins the Docker Official Image multi-platform index digest `sha256:9f4fd4aa918f52ae3d6f3b687f1de90d8f867cd4d520021545a9a50c120eae3b`; Docker Hub identifies the linux/amd64 child manifest as `sha256:c7fedce47eff6a78cb35dad6b627f0d684107f75ab15c0870e40c093766ba452`. The exact workflow commit `1844a9964fee667b7d29299a5b75f0f07df5076d` passed PostgreSQL workflow [#43630438579](https://github.com/PandaGarry/NEXUS/actions/runs/43630438579) (11/11) and Python workflow [#43630438570](https://github.com/PandaGarry/NEXUS/actions/runs/43630438570) (264 tests per runtime). This pins the referenced image content but does not itself prove publisher build provenance, signatures, SBOM completeness or vulnerability acceptability.


## Catalog-manifest drift regression — 2026-11-14

The fixture harness now computes a deterministic SHA-256-independent test fingerprint (MD5 over canonical JSONB text) of the relevant disposable `nexus_*` PostgreSQL catalog surface: role attributes, role memberships, schema owners/ACLs, relation owners/RLS flags/ACLs, function identity/owner/SECURITY mode/configuration/ACLs, RLS policy definitions/roles and default privileges. The fingerprint is a regression oracle only; it is not a signed production manifest, cryptographic attestation or continuous production drift monitor.

The new test deliberately changes and restores four catalog dimensions: a runtime role's CREATEROLE attribute, PUBLIC EXECUTE on the HEGC entrypoint, SECURITY DEFINER/INVOKER mode and an unexpected trusted-schema function. Each mutation must change the fingerprint; each exact restoration must return to the approved baseline. Exact code/test HEAD `f815c351a709ff169996e3f0e451da73651a142c` passed PostgreSQL workflow [#43631662692](https://github.com/PandaGarry/NEXUS/actions/runs/43631662692): **12/12 tests** on PostgreSQL 18.7. Python workflow [#43631662864](https://github.com/PandaGarry/NEXUS/actions/runs/43631662864) passed 264 tests on each of Python 3.11, 3.12 and 3.13 (792 executions). All four jobs completed successfully.

This remains disposable-fixture evidence. The production approved-manifest signing/storage/review lifecycle, deployment-time fail-closed comparison, catalog coverage qualification against the eventual production schema, independent DBA control plane, audit custody, emergency-change reconciliation and active-session/network fencing remain OPEN.
