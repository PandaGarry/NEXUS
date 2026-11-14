import unittest

from halt_egress_gate import AttemptPhase, GateDenied, HaltEgressGate, HaltPhase


class HaltEgressGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = HaltEgressGate(epoch=7)

    def test_halt_commits_before_gate_and_denies_socket_initiation(self):
        self.assertEqual(self.gate.request_halt(reason="operator halt"), 8)
        with self.assertRaises(GateDenied):
            self.gate.authorize_attempt(attempt_id="attempt-1", observed_epoch=7)
        self.gate.acknowledge_halt()
        self.assertEqual(self.gate.phase, HaltPhase.HALTED)
        self.assertEqual(self.gate.attempts, {})

    def test_gate_commits_before_halt_and_becomes_in_flight(self):
        self.gate.authorize_attempt(attempt_id="attempt-1", observed_epoch=7)
        self.assertEqual(self.gate.request_halt(reason="operator halt"), 8)
        with self.assertRaises(GateDenied):
            self.gate.acknowledge_halt()
        self.gate.initiate_socket_write(attempt_id="attempt-1")
        self.gate.acknowledge_halt()
        self.assertEqual(self.gate.phase, HaltPhase.HALTED)
        self.assertEqual(self.gate.reconciliation_required(), ("attempt-1",))

    def test_paused_process_after_gate_commit_blocks_halt_ack(self):
        self.gate.authorize_attempt(attempt_id="paused", observed_epoch=7)
        self.gate.request_halt(reason="operator halt")
        with self.assertRaisesRegex(GateDenied, "may still initiate"):
            self.gate.acknowledge_halt()
        self.assertEqual(self.gate.attempts["paused"].phase, AttemptPhase.GATE_COMMITTED)

    def test_positive_sender_fence_allows_ack_without_socket_write(self):
        self.gate.authorize_attempt(attempt_id="paused", observed_epoch=7)
        self.gate.request_halt(reason="operator halt")
        self.gate.fence_unstarted_sender(attempt_id="paused", receipt="test-fence-receipt")
        self.gate.acknowledge_halt()
        with self.assertRaises(GateDenied):
            self.gate.initiate_socket_write(attempt_id="paused")
        self.assertEqual(self.gate.reconciliation_required(), ())

    def test_halt_blocks_new_gate_commits_while_existing_gate_commit_remains_in_flight(self):
        self.gate.authorize_attempt(attempt_id="old", observed_epoch=7)
        self.gate.request_halt(reason="operator halt")
        with self.assertRaises(GateDenied):
            self.gate.authorize_attempt(attempt_id="new", observed_epoch=8)
        self.gate.initiate_socket_write(attempt_id="old")
        self.gate.acknowledge_halt()
        self.assertEqual(set(self.gate.attempts), {"old"})

    def test_attempt_authorization_is_single_use(self):
        self.gate.authorize_attempt(attempt_id="attempt-1", observed_epoch=7)
        with self.assertRaisesRegex(GateDenied, "single-use"):
            self.gate.authorize_attempt(attempt_id="attempt-1", observed_epoch=7)

    def test_unavailable_halt_store_blocks_gate_and_does_not_claim_halted(self):
        self.gate.store_available = False
        self.assertIsNone(self.gate.request_halt(reason="store unavailable"))
        self.assertEqual(self.gate.phase, HaltPhase.HALT_PENDING)
        with self.assertRaisesRegex(GateDenied, "store is unavailable"):
            self.gate.authorize_attempt(attempt_id="attempt-1", observed_epoch=7)
        with self.assertRaises(GateDenied):
            self.gate.acknowledge_halt()
        self.assertEqual(self.gate.phase, HaltPhase.HALT_PENDING)

    def test_pending_halt_commits_only_after_store_recovers(self):
        self.gate.store_available = False
        self.gate.request_halt(reason="store unavailable")
        with self.assertRaises(GateDenied):
            self.gate.commit_pending_halt()
        self.gate.store_available = True
        self.assertEqual(self.gate.commit_pending_halt(), 8)
        self.gate.acknowledge_halt()
        self.assertEqual(self.gate.phase, HaltPhase.HALTED)

    def test_gate_committed_attempt_is_still_reconciled_after_halt_ack(self):
        self.gate.authorize_attempt(attempt_id="attempt-1", observed_epoch=7)
        self.gate.request_halt(reason="operator halt")
        self.gate.initiate_socket_write(attempt_id="attempt-1")
        self.gate.acknowledge_halt()
        self.assertEqual(self.gate.reconciliation_required(), ("attempt-1",))

    def test_stale_epoch_and_boolean_epoch_are_rejected(self):
        with self.assertRaises(GateDenied):
            self.gate.authorize_attempt(attempt_id="stale", observed_epoch=6)
        with self.assertRaises(GateDenied):
            self.gate.authorize_attempt(attempt_id="bool", observed_epoch=True)
        self.assertEqual(self.gate.attempts, {})

    def test_invalid_halt_reason_is_rejected(self):
        with self.assertRaises(ValueError):
            self.gate.request_halt(reason=" ")


if __name__ == "__main__":
    unittest.main()
