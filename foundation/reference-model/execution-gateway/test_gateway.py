import os
import tempfile
import threading
import unittest

from gateway import (Approval, CanonicalCommand, CommandGateway, Denied,
                     FakeVenueAdapter, InjectedCrash, SQLiteOutbox,
                     issue_test_approval)

KEY = b"test-only-not-production-key"
NOW = 1_800_000_000


def command(**changes):
    fields = dict(command_id="cmd-001", command_type="CREATE", environment="PAPER",
                  account_ref="acct-1", venue_id="venue-x", instrument_id="BTC-USD-PERP",
                  instrument_spec_version="spec-7", policy_version="policy-3",
                  reservation_id="res-1", halt_epoch=4, quantity="0.01", price="65000",
                  created_at="2026-11-14T00:00:00Z", expires_at="2026-11-14T00:01:00Z")
    fields.update(changes)
    return CanonicalCommand(**fields)


class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "nexus.sqlite")
        self.store = SQLiteOutbox(self.path)
        self.adapter = FakeVenueAdapter()
        self.epoch = 4
        self.now = NOW
        self.gateway = CommandGateway(self.store, self.adapter, verification_key=KEY,
                                      clock=lambda: self.now,
                                      current_halt_epoch=lambda _account: self.epoch)
        self.cmd = command()
        self.store.add_reservation("res-1", "cmd-001")
        self.approval = issue_test_approval(self.cmd, key=KEY, now=NOW)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_valid_approval_persists_then_dispatches_once(self):
        self.gateway.persist_approved(self.cmd, self.approval)
        self.assertEqual(self.gateway.state("cmd-001"), "PERSISTED")
        self.assertEqual(self.adapter.calls, [])
        self.assertEqual(self.gateway.dispatch("cmd-001"), "ACKNOWLEDGED")
        self.assertEqual(len(self.adapter.calls), 1)
        self.assertEqual(self.gateway.state("cmd-001"), "ACKNOWLEDGED")
        self.assertEqual(self.store.db.execute("SELECT outcome FROM commands WHERE command_id='cmd-001'").fetchone()[0], "ACCEPTED_NOT_FILLED")

    def test_missing_or_tampered_approval_never_calls_adapter(self):
        bad = Approval(**{**self.approval.__dict__, "signature": "00" * 32})
        with self.assertRaises(Denied):
            self.gateway.persist_approved(self.cmd, bad)
        self.assertEqual(self.adapter.calls, [])

    def test_command_mutation_breaks_digest_binding(self):
        mutated = command(price="65001")
        with self.assertRaises(Denied):
            self.gateway.persist_approved(mutated, self.approval)
        self.assertEqual(self.adapter.calls, [])

    def test_wrong_scope_is_denied(self):
        other = command(account_ref="acct-2")
        approval = issue_test_approval(other, key=KEY, now=NOW)
        with self.assertRaises(Denied):
            self.gateway.persist_approved(self.cmd, approval)

    def test_expired_approval_is_denied(self):
        expired = issue_test_approval(self.cmd, key=KEY, now=NOW-100, ttl=10)
        with self.assertRaises(Denied):
            self.gateway.persist_approved(self.cmd, expired)

    def test_stale_halt_epoch_is_denied(self):
        self.epoch = 5
        with self.assertRaises(Denied):
            self.gateway.persist_approved(self.cmd, self.approval)

    def test_reservation_must_be_active_and_bound(self):
        self.store.db.execute("UPDATE reservations SET state='RELEASED'")
        with self.assertRaises(Denied):
            self.gateway.persist_approved(self.cmd, self.approval)

    def test_transaction_failure_prevents_persistence_and_dispatch(self):
        with self.assertRaises(InjectedCrash):
            self.gateway.persist_approved(self.cmd, self.approval, fail_before_commit=True)
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM commands").fetchone()[0], 0)
        self.assertEqual(self.adapter.calls, [])

    def test_crash_after_commit_is_recoverable_before_any_dispatch(self):
        with self.assertRaises(InjectedCrash):
            self.gateway.persist_approved(self.cmd, self.approval, crash_after_commit=True)
        self.assertEqual(self.gateway.state("cmd-001"), "PERSISTED")
        self.assertEqual(self.adapter.calls, [])
        self.assertEqual(self.gateway.dispatch("cmd-001"), "ACKNOWLEDGED")

    def test_crash_after_dispatch_marker_becomes_unknown_and_is_not_resent(self):
        self.gateway.persist_approved(self.cmd, self.approval)
        with self.assertRaises(InjectedCrash):
            self.gateway.dispatch("cmd-001", crash_after_dispatch_marker=True)
        self.assertEqual(self.gateway.state("cmd-001"), "DISPATCHING")
        self.assertEqual(self.gateway.recover_after_restart(), ["cmd-001"])
        self.assertEqual(self.gateway.state("cmd-001"), "OUTCOME_UNKNOWN")
        with self.assertRaises(Denied):
            self.gateway.dispatch("cmd-001")
        self.assertEqual(self.adapter.calls, [])

    def test_restart_uses_persisted_state_not_process_memory(self):
        self.gateway.persist_approved(self.cmd, self.approval)
        with self.assertRaises(InjectedCrash):
            self.gateway.dispatch("cmd-001", crash_after_dispatch_marker=True)
        self.store.close()
        self.store = SQLiteOutbox(self.path)
        self.gateway = CommandGateway(self.store, self.adapter, verification_key=KEY,
                                      clock=lambda: self.now,
                                      current_halt_epoch=lambda _account: self.epoch)
        self.assertEqual(self.gateway.recover_after_restart(), ["cmd-001"])
        self.assertEqual(self.gateway.state("cmd-001"), "OUTCOME_UNKNOWN")
        self.assertEqual(self.adapter.calls, [])

    def test_halt_epoch_change_after_persistence_blocks_dispatch(self):
        self.gateway.persist_approved(self.cmd, self.approval)
        self.epoch = 5
        with self.assertRaises(Denied):
            self.gateway.dispatch("cmd-001")
        self.assertEqual(self.gateway.state("cmd-001"), "REJECTED")
        self.assertEqual(self.adapter.calls, [])

    def test_approval_expiry_after_persistence_blocks_dispatch(self):
        self.gateway.persist_approved(self.cmd, self.approval)
        self.now = NOW + 30
        with self.assertRaises(Denied):
            self.gateway.dispatch("cmd-001")
        self.assertEqual(self.gateway.state("cmd-001"), "REJECTED")
        self.assertEqual(self.adapter.calls, [])

    def test_non_create_command_is_not_silently_treated_as_create(self):
        unsupported = command(command_type="CANCEL")
        with self.assertRaises(Denied):
            unsupported.canonical_bytes()

    def test_crash_after_venue_accept_before_ack_persistence_is_unknown(self):
        self.gateway.persist_approved(self.cmd, self.approval)
        with self.assertRaises(InjectedCrash):
            self.gateway.dispatch("cmd-001", crash_after_venue_accept=True)
        self.assertEqual(len(self.adapter.calls), 1)
        self.assertEqual(self.gateway.state("cmd-001"), "DISPATCHING")
        self.assertEqual(self.gateway.recover_after_restart(), ["cmd-001"])
        self.assertEqual(self.gateway.state("cmd-001"), "OUTCOME_UNKNOWN")
        with self.assertRaises(Denied):
            self.gateway.dispatch("cmd-001")
        self.assertEqual(len(self.adapter.calls), 1)

    def test_timeout_after_possible_send_is_unknown_and_not_resent(self):
        self.gateway.persist_approved(self.cmd, self.approval)
        self.adapter.result = "timeout"
        self.assertEqual(self.gateway.dispatch("cmd-001"), "OUTCOME_UNKNOWN")
        with self.assertRaises(Denied):
            self.gateway.dispatch("cmd-001")
        self.assertEqual(len(self.adapter.calls), 1)

    def test_two_gateway_instances_race_for_same_approval_only_one_commits(self):
        barrier = threading.Barrier(3)
        outcomes = []
        lock = threading.Lock()

        def submit():
            store = SQLiteOutbox(self.path)
            gateway = CommandGateway(store, FakeVenueAdapter(), verification_key=KEY,
                                     clock=lambda: self.now,
                                     current_halt_epoch=lambda _account: self.epoch)
            barrier.wait()
            try:
                gateway.persist_approved(self.cmd, self.approval)
                result = "COMMITTED"
            except Denied:
                result = "DENIED"
            finally:
                store.close()
            with lock:
                outcomes.append(result)

        threads = [threading.Thread(target=submit) for _ in range(2)]
        for thread in threads:
            thread.start()
        barrier.wait()
        for thread in threads:
            thread.join(timeout=5)
        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertCountEqual(outcomes, ["COMMITTED", "DENIED"])
        self.assertEqual(self.store.db.execute(
            "SELECT COUNT(*) FROM commands WHERE command_id='cmd-001'").fetchone()[0], 1)
        self.assertEqual(self.store.db.execute(
            "SELECT state FROM reservations WHERE reservation_id='res-1'").fetchone()[0], "CONSUMED")

    def test_two_dispatcher_instances_cannot_claim_same_command(self):
        entered = threading.Event()
        release = threading.Event()

        class BlockingAdapter(FakeVenueAdapter):
            def send(inner_self, payload):
                inner_self.calls.append(payload)
                entered.set()
                if not release.wait(timeout=5):
                    raise TimeoutError("test release timed out")
                return "venue-order-1"

        blocking = BlockingAdapter()
        adapter2 = FakeVenueAdapter()
        store2 = SQLiteOutbox(self.path)
        gateway2 = CommandGateway(store2, adapter2, verification_key=KEY,
                                  clock=lambda: self.now,
                                  current_halt_epoch=lambda _account: self.epoch)
        self.gateway.persist_approved(self.cmd, self.approval)
        outcomes = []

        def first_dispatch():
            store1 = SQLiteOutbox(self.path)
            gateway1 = CommandGateway(store1, blocking, verification_key=KEY,
                                      clock=lambda: self.now,
                                      current_halt_epoch=lambda _account: self.epoch)
            try:
                outcomes.append(gateway1.dispatch("cmd-001"))
            finally:
                store1.close()

        thread = threading.Thread(target=first_dispatch)
        thread.start()
        try:
            self.assertTrue(entered.wait(timeout=3), "first dispatcher never reached adapter")
            with self.assertRaises(Denied):
                gateway2.dispatch("cmd-001")
            self.assertEqual(adapter2.calls, [])
        finally:
            release.set()
            thread.join(timeout=5)
            store2.close()
        self.assertFalse(thread.is_alive())
        self.assertEqual(outcomes, ["ACKNOWLEDGED"])
        self.assertEqual(len(blocking.calls), 1)

    def test_duplicate_approval_and_command_replay_rejected(self):
        self.gateway.persist_approved(self.cmd, self.approval)
        with self.assertRaises(Denied):
            self.gateway.persist_approved(self.cmd, self.approval)
        self.assertEqual(self.adapter.calls, [])

    def test_noncanonical_decimal_rejected(self):
        bad = command(quantity="01.0")
        with self.assertRaises(Denied):
            bad.canonical_bytes()


if __name__ == "__main__":
    unittest.main(verbosity=2)
