#!/usr/bin/env python3
"""Disposable PostgreSQL 18.7 HEGC guard qualification tests; never production code."""
from __future__ import annotations

import os
import subprocess
import time
import unittest
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ADMIN = os.environ.get("PGUSER", "postgres")
PASSWORD = os.environ.get("PGPASSWORD", "postgres")
HOST = os.environ.get("PGHOST", "127.0.0.1")
PORT = os.environ.get("PGPORT", "5432")
DATABASE = os.environ.get("PGDATABASE", "nexus_test")


def command(user: str, password: str, app: str) -> list[str]:
    return [
        "psql", "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1",
        "-h", HOST, "-p", PORT, "-U", user, "-d", DATABASE, "-f", "-"
    ]


def env_for(user: str, password: str, app: str) -> dict[str, str]:
    env = os.environ.copy()
    env.update({
        "PGUSER": user,
        "PGPASSWORD": password,
        "PGAPPNAME": app,
        "PGCONNECT_TIMEOUT": "3",
    })
    return env


def run_sql(sql: str, user: str = ADMIN, password: str = PASSWORD, app: str = "nexus-harness-admin") -> subprocess.CompletedProcess[str]:
    script = "\\set VERBOSITY verbose\n" + sql
    return subprocess.run(
        command(user, password, app),
        input=script,
        text=True,
        capture_output=True,
        env=env_for(user, password, app),
        timeout=15,
    )


def start_sql(sql: str, user: str, password: str, app: str) -> subprocess.Popen[str]:
    proc = subprocess.Popen(
        command(user, password, app),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env_for(user, password, app),
    )
    assert proc.stdin is not None
    proc.stdin.write("\\set VERBOSITY verbose\n" + sql)
    proc.stdin.close()
    return proc


def finish(proc: subprocess.Popen[str], timeout: int = 12) -> tuple[int, str, str]:
    proc.wait(timeout=timeout)
    stdout = proc.stdout.read() if proc.stdout else ""
    stderr = proc.stderr.read() if proc.stderr else ""
    if proc.stdout:
        proc.stdout.close()
    if proc.stderr:
        proc.stderr.close()
    return proc.returncode or 0, stdout, stderr


def lit(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def uuid_array(values: list[str]) -> str:
    return "ARRAY[" + ",".join(lit(v) + "::uuid" for v in values) + "]::uuid[]"


def wait_for_activity(app: str, *, waiting_on_lock: bool, timeout: float = 8.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = run_sql(
            "SELECT COALESCE(wait_event_type, '') || '|' || COALESCE(query, '') "
            "FROM pg_stat_activity WHERE application_name = " + lit(app) + " AND state = 'active';"
        )
        value = result.stdout.strip()
        if result.returncode == 0 and value:
            if waiting_on_lock and value.startswith("Lock|"):
                return
            if not waiting_on_lock and "pg_sleep" in value:
                return
        time.sleep(0.05)
    raise AssertionError(f"backend {app!r} did not reach expected state (waiting_on_lock={waiting_on_lock})")


class PostgreSQLGuardHarness(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        result = run_sql("SHOW server_version_num;")
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        version_num = result.stdout.strip()
        if version_num != "180007":
            raise RuntimeError(f"expected PostgreSQL 18.7 (server_version_num=180007), got {version_num!r}")
        bootstrap = run_sql((ROOT / "bootstrap.sql").read_text())
        if bootstrap.returncode != 0:
            raise RuntimeError(bootstrap.stderr)

    def seed(self) -> tuple[str, list[str]]:
        account = str(uuid.uuid4())
        children = sorted([str(uuid.uuid4()), str(uuid.uuid4())])
        scopes = [account, *children]
        rows = ", ".join(f"({lit(account)}::uuid, {lit(scope)}::uuid, true)" for scope in scopes)
        guards = ", ".join(f"({lit(account)}::uuid, {lit(scope)}::uuid, 0)" for scope in scopes)
        exposures = ", ".join(f"({lit(account)}::uuid, {lit(scope)}::uuid, 100)" for scope in scopes)
        principals = (
            f"({lit('nexus_hegc')}::name, 'hegc', {lit(account)}::uuid),"
            f"({lit('nexus_writer')}::name, 'writer', {lit(account)}::uuid),"
            f"({lit('nexus_membership_admin')}::name, 'membership_admin', {lit(account)}::uuid)"
        )
        result = run_sql(
            f"INSERT INTO nexus_control.scope_membership VALUES {rows};"
            f"INSERT INTO nexus_control.scope_guard(account_id,scope_id,generation) VALUES {guards};"
            f"INSERT INTO nexus_source.exposure VALUES {exposures};"
            f"INSERT INTO nexus_control.service_principal VALUES {principals};"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return account, scopes

    def gate_sql(self, account: str, scopes: list[str], attempt: str, digest: str, *, sleep: int = 0) -> str:
        sql = (
            "BEGIN ISOLATION LEVEL SERIALIZABLE;"
            f"SELECT nexus_hegc.issue_egress_grant({lit(account)}::uuid,{uuid_array(scopes)},"
            f"{lit(attempt)}::uuid,{lit(digest)});"
        )
        if sleep:
            sql += f"SELECT pg_sleep({sleep});"
        return sql + "COMMIT;"

    def writer_sql(self, account: str, scopes: list[str], delta: int = 10, *, sleep: int = 0) -> str:
        sql = (
            "BEGIN ISOLATION LEVEL SERIALIZABLE;"
            f"SELECT nexus_source.apply_exposure({lit(account)}::uuid,{uuid_array(scopes)},{delta});"
        )
        if sleep:
            sql += f"SELECT pg_sleep({sleep});"
        return sql + "COMMIT;"

    def test_privilege_boundary_and_search_path_spoof(self) -> None:
        account, scopes = self.seed()
        checks = run_sql(
            "SELECT has_table_privilege('nexus_hegc','nexus_source.exposure','SELECT'),"
            "has_table_privilege('nexus_hegc','nexus_hegc.egress_grant','INSERT'),"
            "has_table_privilege('nexus_hegc','nexus_hegc.egress_grant','SELECT'),"
            "has_table_privilege('nexus_hegc','nexus_control.scope_guard','UPDATE'),"
            "has_table_privilege('nexus_writer','nexus_source.exposure','UPDATE'),"
            "has_function_privilege('nexus_hegc','nexus_control.acquire_scope_guards(uuid,uuid[])','EXECUTE'),"
            "pg_has_role('nexus_hegc','nexus_hegc_owner','MEMBER'),"
            "(SELECT rolsuper OR rolbypassrls OR rolcanlogin OR rolinherit FROM pg_roles WHERE rolname='nexus_hegc_owner');"
        )
        self.assertEqual(checks.returncode, 0, checks.stderr)
        self.assertEqual(checks.stdout.strip(), "f|f|f|f|f|f|f|f")
        rls = run_sql(
            "SELECT relrowsecurity, relforcerowsecurity FROM pg_class WHERE oid='nexus_source.exposure'::regclass;"
        )
        self.assertEqual(rls.stdout.strip(), "t|t")
        admin_direct = run_sql(
            "SELECT * FROM nexus_control.scope_membership;",
            user="nexus_membership_admin", password="membership-test-only",
        )
        self.assertNotEqual(admin_direct.returncode, 0)
        admin_principals = run_sql(
            "SELECT * FROM nexus_control.service_principal;",
            user="nexus_membership_admin", password="membership-test-only",
        )
        self.assertNotEqual(admin_principals.returncode, 0)
        admin_helper = run_sql(
            "SELECT nexus_control.acquire_scope_guards(NULL, NULL);",
            user="nexus_membership_admin", password="membership-test-only",
        )
        self.assertNotEqual(admin_helper.returncode, 0)
        denied = run_sql("SELECT * FROM nexus_source.exposure;", user="nexus_hegc", password="hegc-test-only")
        self.assertNotEqual(denied.returncode, 0)
        role_denied = run_sql("SET ROLE nexus_hegc_owner;", user="nexus_hegc", password="hegc-test-only")
        self.assertNotEqual(role_denied.returncode, 0)
        direct_writer_dml = run_sql(
            f"UPDATE nexus_source.exposure SET exposure_units=0 WHERE account_id={lit(account)}::uuid;",
            user="nexus_writer", password="writer-test-only",
        )
        self.assertNotEqual(direct_writer_dml.returncode, 0)

        attempt = str(uuid.uuid4())
        spoof = run_sql(
            "CREATE TEMP TABLE egress_grant(attempt_id uuid, grant_id uuid);"
            "SET search_path = pg_temp, public;"
            f"SELECT nexus_hegc.issue_egress_grant({lit(account)}::uuid,{uuid_array(scopes)},"
            f"{lit(attempt)}::uuid,'spoof-test');",
            user="nexus_hegc", password="hegc-test-only",
        )
        self.assertEqual(spoof.returncode, 0, spoof.stderr)

        run_sql(
            f"DELETE FROM nexus_control.service_principal WHERE principal='nexus_hegc' AND account_id={lit(account)}::uuid;"
        )
        guc_spoof = run_sql(
            "SET nexus.claimed_principal = 'nexus_hegc';"
            f"SELECT nexus_hegc.issue_egress_grant({lit(account)}::uuid,{uuid_array(scopes)},"
            f"{lit(str(uuid.uuid4()))}::uuid,'guc-spoof');",
            user="nexus_hegc", password="hegc-test-only",
        )
        self.assertNotEqual(guc_spoof.returncode, 0)
        self.assertIn("42501", guc_spoof.stderr)

    def test_scope_set_must_be_complete_and_canonical(self) -> None:
        account, scopes = self.seed()
        attempt = str(uuid.uuid4())
        incomplete = run_sql(
            "BEGIN ISOLATION LEVEL SERIALIZABLE;"
            f"SELECT nexus_hegc.issue_egress_grant({lit(account)}::uuid,{uuid_array(scopes[:2])},"
            f"{lit(attempt)}::uuid,'scope-test'); COMMIT;",
            user="nexus_hegc", password="hegc-test-only",
        )
        self.assertNotEqual(incomplete.returncode, 0)
        self.assertIn("22023", incomplete.stderr)

        noncanonical_scopes = [scopes[0], scopes[2], scopes[1]]
        noncanonical = run_sql(
            "BEGIN ISOLATION LEVEL SERIALIZABLE;"
            f"SELECT nexus_hegc.issue_egress_grant({lit(account)}::uuid,{uuid_array(noncanonical_scopes)},"
            f"{lit(str(uuid.uuid4()))}::uuid,'noncanonical-scope-test'); COMMIT;",
            user="nexus_hegc", password="hegc-test-only",
        )
        self.assertNotEqual(noncanonical.returncode, 0)
        self.assertIn("22023", noncanonical.stderr)

    def test_scope_membership_change_serializes_with_gate(self) -> None:
        account, scopes = self.seed()
        added_scope = str(uuid.uuid4())
        # Prepare source data while the scope is inactive; guarded membership
        # mutation is the only operation that makes it part of the active set.
        prepared = run_sql(
            f"INSERT INTO nexus_source.exposure VALUES ({lit(account)}::uuid,{lit(added_scope)}::uuid,50);"
        )
        self.assertEqual(prepared.returncode, 0, prepared.stderr)

        membership_change = start_sql(
            "BEGIN ISOLATION LEVEL SERIALIZABLE;"
            f"SELECT nexus_control.set_scope_active({lit(account)}::uuid,{uuid_array(scopes)},"
            f"{lit(added_scope)}::uuid,true);"
            "SELECT pg_sleep(3); COMMIT;",
            "nexus_membership_admin", "membership-test-only", "membership-add-holder",
        )
        wait_for_activity("membership-add-holder", waiting_on_lock=False)
        attempt = str(uuid.uuid4())
        stale_gate = start_sql(
            self.gate_sql(account, scopes, attempt, "membership-race"),
            "nexus_hegc", "hegc-test-only", "membership-stale-gate",
        )
        try:
            wait_for_activity("membership-stale-gate", waiting_on_lock=True)
            holder_code, _, holder_err = finish(membership_change)
            self.assertEqual(holder_code, 0, holder_err)
            stale_code, _, stale_err = finish(stale_gate)
        finally:
            if membership_change.poll() is None:
                membership_change.terminate()
                finish(membership_change)
            if stale_gate.poll() is None:
                stale_gate.terminate()
                finish(stale_gate)
        self.assertNotEqual(stale_code, 0, stale_err)
        self.assertIn("40001", stale_err)

        expanded_scopes = [scopes[0], *sorted([*scopes[1:], added_scope])]
        retry = run_sql(
            self.gate_sql(account, expanded_scopes, attempt, "membership-race"),
            user="nexus_hegc", password="hegc-test-only",
        )
        self.assertEqual(retry.returncode, 0, retry.stderr)
        snapshot = run_sql(
            f"SELECT snapshot_total FROM nexus_hegc.egress_grant WHERE attempt_id={lit(attempt)}::uuid;"
        )
        self.assertEqual(snapshot.stdout.strip(), "350")

        # Deactivation is also guarded; the formerly complete set is now stale.
        deactivate = run_sql(
            "BEGIN ISOLATION LEVEL SERIALIZABLE;"
            f"SELECT nexus_control.set_scope_active({lit(account)}::uuid,{uuid_array(expanded_scopes)},"
            f"{lit(added_scope)}::uuid,false); COMMIT;",
            user="nexus_membership_admin", password="membership-test-only",
        )
        self.assertEqual(deactivate.returncode, 0, deactivate.stderr)
        stale_set = run_sql(
            "BEGIN ISOLATION LEVEL SERIALIZABLE;"
            f"SELECT nexus_hegc.issue_egress_grant({lit(account)}::uuid,{uuid_array(expanded_scopes)},"
            f"{lit(str(uuid.uuid4()))}::uuid,'stale-membership'); COMMIT;",
            user="nexus_hegc", password="hegc-test-only",
        )
        self.assertNotEqual(stale_set.returncode, 0)
        self.assertIn("22023", stale_set.stderr)

    def test_service_principal_revocation_serializes_with_gate(self) -> None:
        account, scopes = self.seed()
        revoke = start_sql(
            "BEGIN ISOLATION LEVEL SERIALIZABLE;"
            f"SELECT nexus_control.set_service_principal({lit(account)}::uuid,{uuid_array(scopes)},"
            "'nexus_hegc'::name,'hegc',false);"
            "SELECT pg_sleep(3); COMMIT;",
            "nexus_membership_admin", "membership-test-only", "principal-revoke-holder",
        )
        wait_for_activity("principal-revoke-holder", waiting_on_lock=False)
        stale_attempt = str(uuid.uuid4())
        stale_gate = start_sql(
            self.gate_sql(account, scopes, stale_attempt, "principal-revoke-race"),
            "nexus_hegc", "hegc-test-only", "principal-revoke-stale-gate",
        )
        try:
            wait_for_activity("principal-revoke-stale-gate", waiting_on_lock=True)
            holder_code, _, holder_err = finish(revoke)
            self.assertEqual(holder_code, 0, holder_err)
            stale_code, _, stale_err = finish(stale_gate)
        finally:
            if revoke.poll() is None:
                revoke.terminate()
                finish(revoke)
            if stale_gate.poll() is None:
                stale_gate.terminate()
                finish(stale_gate)
        self.assertNotEqual(stale_code, 0, stale_err)
        self.assertIn("40001", stale_err)

        denied_retry = run_sql(
            self.gate_sql(account, scopes, stale_attempt, "principal-revoke-race"),
            user="nexus_hegc", password="hegc-test-only",
        )
        self.assertNotEqual(denied_retry.returncode, 0)
        self.assertIn("42501", denied_retry.stderr)

        self_revoke = run_sql(
            "SELECT nexus_control.set_service_principal("
            + lit(account) + "::uuid," + uuid_array(scopes)
            + ",'nexus_membership_admin'::name,'membership_admin',false);",
            user="nexus_membership_admin", password="membership-test-only",
        )
        self.assertNotEqual(self_revoke.returncode, 0)
        self.assertIn("22023", self_revoke.stderr)

        restore = run_sql(
            "SELECT nexus_control.set_service_principal("
            + lit(account) + "::uuid," + uuid_array(scopes)
            + ",'nexus_hegc'::name,'hegc',true);",
            user="nexus_membership_admin", password="membership-test-only",
        )
        self.assertEqual(restore.returncode, 0, restore.stderr)
        recovered = run_sql(
            self.gate_sql(account, scopes, str(uuid.uuid4()), "principal-restored"),
            user="nexus_hegc", password="hegc-test-only",
        )
        self.assertEqual(recovered.returncode, 0, recovered.stderr)

    def test_exact_retry_returns_same_grant_and_changed_binding_conflicts(self) -> None:
        account, scopes = self.seed()
        attempt = str(uuid.uuid4())
        first = run_sql(
            f"SELECT nexus_hegc.issue_egress_grant({lit(account)}::uuid,{uuid_array(scopes)},"
            f"{lit(attempt)}::uuid,'digest-A');",
            user="nexus_hegc", password="hegc-test-only",
        )
        retry = run_sql(
            f"SELECT nexus_hegc.issue_egress_grant({lit(account)}::uuid,{uuid_array(scopes)},"
            f"{lit(attempt)}::uuid,'digest-A');",
            user="nexus_hegc", password="hegc-test-only",
        )
        conflict = run_sql(
            f"SELECT nexus_hegc.issue_egress_grant({lit(account)}::uuid,{uuid_array(scopes)},"
            f"{lit(attempt)}::uuid,'digest-B');",
            user="nexus_hegc", password="hegc-test-only",
        )
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(retry.returncode, 0, retry.stderr)
        self.assertEqual(first.stdout.strip(), retry.stdout.strip())
        self.assertNotEqual(conflict.returncode, 0)
        self.assertIn("23505", conflict.stderr)

    def test_concurrent_duplicate_attempt_retries_to_same_grant(self) -> None:
        account, scopes = self.seed()
        attempt = str(uuid.uuid4())
        holder = start_sql(
            self.gate_sql(account, scopes, attempt, "concurrent-duplicate", sleep=3),
            "nexus_hegc", "hegc-test-only", "duplicate-holder",
        )
        wait_for_activity("duplicate-holder", waiting_on_lock=False)
        contender = start_sql(
            self.gate_sql(account, scopes, attempt, "concurrent-duplicate"),
            "nexus_hegc", "hegc-test-only", "duplicate-contender",
        )
        try:
            wait_for_activity("duplicate-contender", waiting_on_lock=True)
            holder_code, holder_out, holder_err = finish(holder)
            self.assertEqual(holder_code, 0, holder_err)
            code, _, stderr = finish(contender)
        finally:
            if holder.poll() is None:
                holder.terminate()
                finish(holder)
            if contender.poll() is None:
                contender.terminate()
                finish(contender)
        self.assertNotEqual(code, 0, stderr)
        self.assertIn("40001", stderr)
        retry = run_sql(
            self.gate_sql(account, scopes, attempt, "concurrent-duplicate"),
            user="nexus_hegc", password="hegc-test-only",
        )
        self.assertEqual(retry.returncode, 0, retry.stderr)
        self.assertEqual(holder_out.strip(), retry.stdout.strip())

    def test_lost_post_commit_response_recovers_same_grant(self) -> None:
        account, scopes = self.seed()
        attempt = str(uuid.uuid4())
        holder = start_sql(
            self.gate_sql(account, scopes, attempt, "lost-response") + "SELECT pg_sleep(10);",
            "nexus_hegc", "hegc-test-only", "lost-response-holder",
        )
        try:
            deadline = time.monotonic() + 8.0
            grant_id = ""
            while time.monotonic() < deadline:
                found = run_sql(
                    f"SELECT grant_id FROM nexus_hegc.egress_grant WHERE attempt_id={lit(attempt)}::uuid;"
                )
                if found.returncode == 0 and found.stdout.strip():
                    grant_id = found.stdout.strip()
                    break
                time.sleep(0.05)
            self.assertTrue(grant_id, "grant did not commit before timeout")
            wait_for_activity("lost-response-holder", waiting_on_lock=False)
        finally:
            if holder.poll() is None:
                holder.terminate()
                finish(holder)
        retry = run_sql(
            self.gate_sql(account, scopes, attempt, "lost-response"),
            user="nexus_hegc", password="hegc-test-only",
        )
        self.assertEqual(retry.returncode, 0, retry.stderr)
        self.assertEqual(grant_id, retry.stdout.strip())

    def test_writer_first_forces_gate_whole_transaction_retry(self) -> None:
        account, scopes = self.seed()
        attempt = str(uuid.uuid4())
        holder = start_sql(self.writer_sql(account, scopes, sleep=3), "nexus_writer", "writer-test-only", "writer-first-holder")
        wait_for_activity("writer-first-holder", waiting_on_lock=False)
        contender = start_sql(
            self.gate_sql(account, scopes, attempt, "writer-first-digest"),
            "nexus_hegc", "hegc-test-only", "writer-first-gate",
        )
        try:
            wait_for_activity("writer-first-gate", waiting_on_lock=True)
            self.assertEqual(finish(holder)[0], 0)
            code, _, stderr = finish(contender)
        finally:
            if holder.poll() is None:
                holder.terminate()
            if contender.poll() is None:
                contender.terminate()
        self.assertNotEqual(code, 0, stderr)
        self.assertIn("40001", stderr)
        retry = run_sql(
            self.gate_sql(account, scopes, attempt, "writer-first-digest"),
            user="nexus_hegc", password="hegc-test-only",
        )
        self.assertEqual(retry.returncode, 0, retry.stderr)
        total = run_sql(
            f"SELECT snapshot_total FROM nexus_hegc.egress_grant WHERE attempt_id={lit(attempt)}::uuid;"
        )
        self.assertEqual(total.stdout.strip(), "330")

    def test_gate_first_forces_writer_whole_transaction_retry(self) -> None:
        account, scopes = self.seed()
        attempt = str(uuid.uuid4())
        holder = start_sql(
            self.gate_sql(account, scopes, attempt, "gate-first-digest", sleep=3),
            "nexus_hegc", "hegc-test-only", "gate-first-holder",
        )
        wait_for_activity("gate-first-holder", waiting_on_lock=False)
        contender = start_sql(
            self.writer_sql(account, scopes),
            "nexus_writer", "writer-test-only", "gate-first-writer",
        )
        try:
            wait_for_activity("gate-first-writer", waiting_on_lock=True)
            self.assertEqual(finish(holder)[0], 0)
            code, _, stderr = finish(contender)
        finally:
            if holder.poll() is None:
                holder.terminate()
            if contender.poll() is None:
                contender.terminate()
        self.assertNotEqual(code, 0, stderr)
        self.assertIn("40001", stderr)
        retry = run_sql(
            self.writer_sql(account, scopes),
            user="nexus_writer", password="writer-test-only",
        )
        self.assertEqual(retry.returncode, 0, retry.stderr)
        snapshot = run_sql(
            f"SELECT snapshot_total FROM nexus_hegc.egress_grant WHERE attempt_id={lit(attempt)}::uuid;"
        )
        self.assertEqual(snapshot.stdout.strip(), "300")
        current = run_sql(
            f"SELECT sum(exposure_units) FROM nexus_source.exposure WHERE account_id={lit(account)}::uuid;"
        )
        self.assertEqual(current.stdout.strip(), "330")


if __name__ == "__main__":
    unittest.main(verbosity=2)
