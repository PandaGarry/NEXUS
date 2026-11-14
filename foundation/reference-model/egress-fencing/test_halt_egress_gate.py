import unittest

from halt_egress_gate import AttemptPhase, GateDenied, HaltEgressGate, HaltPhase


class HaltEgressGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = HaltEgressGate(epoch=7)

    def test_halt_commits_before_gate_and_denies_socket_initiation(self):
        self.assertEqual(self.gate.request_halt(reason="operator halt"), 8)
        with self.assertRaises(GateDenied):
            self.gate.authorize_attempt(attempt_id="attempt-1", observed_epoch=7, binding_digest="digest-attempt-1")
        self.gate.acknowledge_halt()
        self.assertEqual(self.gate.phase, HaltPhase.HALTED)
        self.assertEqual(self.gate.attempts, {})

    def test_gate_commits_before_halt_and_becomes_in_flight(self):
        self.gate.authorize_attempt(attempt_id="attempt-1", observed_epoch=7, binding_digest="digest-attempt-1")
        self.assertEqual(self.gate.request_halt(reason="operator halt"), 8)
        with self.assertRaises(GateDenied):
            self.gate.acknowledge_halt()
        self.gate.consume_grant(attempt_id="attempt-1")
        self.gate.initiate_socket_write(attempt_id="attempt-1")
        self.gate.acknowledge_halt()
        self.assertEqual(self.gate.phase, HaltPhase.HALTED)
        self.assertEqual(self.gate.reconciliation_required(), ("attempt-1",))

    def test_paused_process_after_gate_commit_blocks_halt_ack(self):
        self.gate.authorize_attempt(attempt_id="paused", observed_epoch=7, binding_digest="digest-paused")
        self.gate.request_halt(reason="operator halt")
        with self.assertRaisesRegex(GateDenied, "may still initiate"):
            self.gate.acknowledge_halt()
        self.assertEqual(self.gate.attempts["paused"].phase, AttemptPhase.GATE_COMMITTED)

    def test_positive_sender_fence_allows_ack_but_retains_unknown_outcome(self):
        self.gate.authorize_attempt(attempt_id="paused", observed_epoch=7, binding_digest="digest-paused")
        self.gate.request_halt(reason="operator halt")
        self.gate.fence_sender(attempt_id="paused", receipt="test-fence-receipt")
        self.gate.acknowledge_halt()
        self.assertEqual(self.gate.phase, HaltPhase.HALTED)
        with self.assertRaises(GateDenied):
            self.gate.consume_grant(attempt_id="paused")
        with self.assertRaises(GateDenied):
            self.gate.initiate_socket_write(attempt_id="paused")
        self.assertEqual(self.gate.attempts["paused"].phase, AttemptPhase.SENDER_FENCED_UNKNOWN)
        self.assertTrue(self.gate.attempts["paused"].reservation_held)
        self.assertEqual(self.gate.reconciliation_required(), ("paused",))

    def test_sender_fence_does_not_prove_no_prior_socket_side_effect(self):
        self.gate.authorize_attempt(attempt_id="possibly-sent", observed_epoch=7, binding_digest="digest-possibly-sent")
        self.gate.request_halt(reason="operator halt")
        self.gate.fence_sender(attempt_id="possibly-sent", receipt="host-fence-receipt")
        self.gate.acknowledge_halt()
        # No initiation report was received, so the conservative outcome remains unknown.
        self.assertIn("possibly-sent", self.gate.reconciliation_required())
        self.assertTrue(self.gate.attempts["possibly-sent"].reservation_held)

    def test_halt_blocks_new_gate_commits_while_existing_gate_commit_remains_in_flight(self):
        self.gate.authorize_attempt(attempt_id="old", observed_epoch=7, binding_digest="digest-old")
        self.gate.request_halt(reason="operator halt")
        with self.assertRaises(GateDenied):
            self.gate.authorize_attempt(attempt_id="new", observed_epoch=8, binding_digest="digest-new")
        self.gate.consume_grant(attempt_id="old")
        self.gate.initiate_socket_write(attempt_id="old")
        self.gate.acknowledge_halt()
        self.assertEqual(set(self.gate.attempts), {"old"})

    def test_exact_attempt_authorization_retry_returns_original_grant(self):
        first = self.gate.authorize_attempt(
            attempt_id="attempt-1", observed_epoch=7, binding_digest="digest-attempt-1"
        )
        self.gate.request_halt(reason="operator halt")
        retry = self.gate.authorize_attempt(
            attempt_id="attempt-1", observed_epoch=7, binding_digest="digest-attempt-1"
        )
        self.assertIs(retry, first)
        self.assertEqual(len(self.gate.attempts), 1)
        self.assertEqual(retry.authorized_epoch, 7)
        self.assertEqual(self.gate.epoch, 8)

    def test_attempt_id_conflicts_when_authorization_binding_changes(self):
        self.gate.authorize_attempt(
            attempt_id="attempt-1", observed_epoch=7, binding_digest="digest-attempt-1"
        )
        with self.assertRaisesRegex(GateDenied, "changed authorization binding"):
            self.gate.authorize_attempt(
                attempt_id="attempt-1", observed_epoch=7, binding_digest="different-digest"
            )
        with self.assertRaisesRegex(GateDenied, "changed authorization binding"):
            self.gate.authorize_attempt(
                attempt_id="attempt-1", observed_epoch=8, binding_digest="digest-attempt-1"
            )
        self.assertEqual(len(self.gate.attempts), 1)

    def test_unavailable_halt_store_blocks_gate_and_does_not_claim_halted(self):
        self.gate.store_available = False
        self.assertIsNone(self.gate.request_halt(reason="store unavailable"))
        self.assertEqual(self.gate.phase, HaltPhase.HALT_PENDING)
        with self.assertRaisesRegex(GateDenied, "store is unavailable"):
            self.gate.authorize_attempt(attempt_id="attempt-1", observed_epoch=7, binding_digest="digest-attempt-1")
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
        self.gate.authorize_attempt(attempt_id="attempt-1", observed_epoch=7, binding_digest="digest-attempt-1")
        self.gate.request_halt(reason="operator halt")
        self.gate.consume_grant(attempt_id="attempt-1")
        self.gate.initiate_socket_write(attempt_id="attempt-1")
        self.gate.acknowledge_halt()
        self.assertEqual(self.gate.reconciliation_required(), ("attempt-1",))

    def test_stale_epoch_and_boolean_epoch_are_rejected(self):
        with self.assertRaises(GateDenied):
            self.gate.authorize_attempt(attempt_id="stale", observed_epoch=6, binding_digest="digest-stale")
        with self.assertRaises(GateDenied):
            self.gate.authorize_attempt(attempt_id="bool", observed_epoch=True, binding_digest="digest-bool")
        self.assertEqual(self.gate.attempts, {})

    def test_invalid_halt_reason_is_rejected(self):
        with self.assertRaises(ValueError):
            self.gate.request_halt(reason=" ")

    def test_grant_consumption_is_single_use_and_precedes_socket_write(self):
        self.gate.authorize_attempt(attempt_id="one-use", observed_epoch=7, binding_digest="digest-one-use")
        self.gate.consume_grant(attempt_id="one-use")
        with self.assertRaisesRegex(GateDenied, "single-use"):
            self.gate.consume_grant(attempt_id="one-use")
        self.gate.request_halt(reason="operator halt")
        with self.assertRaises(GateDenied):
            self.gate.acknowledge_halt()
        self.gate.initiate_socket_write(attempt_id="one-use")
        self.gate.acknowledge_halt()
        self.assertEqual(self.gate.reconciliation_required(), ("one-use",))

    def test_lost_grant_consumption_response_never_allows_second_send(self):
        self.gate.authorize_attempt(attempt_id="lost-consume", observed_epoch=7, binding_digest="digest-lost-consume")
        self.gate.consume_grant(attempt_id="lost-consume")
        # Simulate a lost response: the durable grant is consumed, so retry cannot mint a new send.
        with self.assertRaisesRegex(GateDenied, "single-use"):
            self.gate.consume_grant(attempt_id="lost-consume")
        self.gate.request_halt(reason="operator halt")
        with self.assertRaises(GateDenied):
            self.gate.acknowledge_halt()
        self.gate.fence_sender(attempt_id="lost-consume", receipt="independent-fence")
        self.gate.acknowledge_halt()
        self.assertEqual(self.gate.reconciliation_required(), ("lost-consume",))

    def test_store_outage_prevents_grant_consumption(self):
        self.gate.authorize_attempt(attempt_id="store-outage", observed_epoch=7, binding_digest="digest-store-outage")
        self.gate.store_available = False
        with self.assertRaisesRegex(GateDenied, "store is unavailable"):
            self.gate.consume_grant(attempt_id="store-outage")
        self.assertEqual(self.gate.attempts["store-outage"].phase, AttemptPhase.GATE_COMMITTED)
        self.assertIsNone(self.gate.request_halt(reason="store outage"))
        with self.assertRaises(GateDenied):
            self.gate.initiate_socket_write(attempt_id="store-outage")

    def test_gate_committed_attempt_survives_pending_halt_store_outage(self):
        self.gate.authorize_attempt(attempt_id="paused", observed_epoch=7, binding_digest="digest-paused")
        self.gate.consume_grant(attempt_id="paused")
        self.gate.store_available = False
        self.assertIsNone(self.gate.request_halt(reason="store outage"))
        self.assertEqual(self.gate.phase, HaltPhase.HALT_PENDING)
        with self.assertRaises(GateDenied):
            self.gate.acknowledge_halt()
        # A grant consumed before the outage remains in-flight and may initiate.
        self.gate.store_available = True
        self.assertEqual(self.gate.commit_pending_halt(), 8)
        # The already-consumed grant is still in-flight; observe its one socket attempt before HALTED.
        self.gate.initiate_socket_write(attempt_id="paused")
        self.gate.acknowledge_halt()
        self.assertEqual(self.gate.phase, HaltPhase.HALTED)
        self.assertEqual(self.gate.reconciliation_required(), ("paused",))

    def test_pending_halt_can_fence_gate_committed_attempt_before_store_recovers(self):
        self.gate.authorize_attempt(attempt_id="paused", observed_epoch=7, binding_digest="digest-paused")
        self.gate.store_available = False
        self.assertIsNone(self.gate.request_halt(reason="store outage"))
        self.gate.fence_sender(attempt_id="paused", receipt="independent-fence-receipt")
        with self.assertRaises(GateDenied):
            self.gate.acknowledge_halt()
        self.gate.store_available = True
        self.assertEqual(self.gate.commit_pending_halt(), 8)
        self.gate.acknowledge_halt()
        self.assertEqual(self.gate.phase, HaltPhase.HALTED)
        self.assertEqual(self.gate.reconciliation_required(), ("paused",))
        self.assertTrue(self.gate.attempts["paused"].reservation_held)

    def test_repeated_halt_request_does_not_advance_epoch_twice(self):
        self.assertEqual(self.gate.request_halt(reason="operator halt"), 8)
        self.assertEqual(self.gate.request_halt(reason="repeated request"), 8)
        self.assertEqual(self.gate.epoch, 8)
        self.assertEqual(self.gate.phase, HaltPhase.HALTING)

    def test_duplicate_halt_request_does_not_overwrite_original_reason(self):
        self.assertEqual(self.gate.request_halt(reason="first cause"), 8)
        self.assertEqual(self.gate.request_halt(reason="later duplicate cause"), 8)
        self.assertEqual(self.gate.halt_reason, "first cause")

    def test_duplicate_pending_halt_request_does_not_overwrite_original_reason(self):
        self.gate.store_available = False
        self.assertIsNone(self.gate.request_halt(reason="first pending cause"))
        self.assertIsNone(self.gate.request_halt(reason="later pending cause"))
        self.assertEqual(self.gate.halt_reason, "first pending cause")
        self.gate.store_available = True
        self.assertEqual(self.gate.commit_pending_halt(), 8)


    def test_duplicate_halt_request_during_store_outage_does_not_downgrade_committed_epoch(self):
        self.assertEqual(self.gate.request_halt(reason="operator halt"), 8)
        self.assertEqual(self.gate.phase, HaltPhase.HALTING)
        self.gate.store_available = False
        self.assertEqual(self.gate.request_halt(reason="duplicate while store down"), 8)
        self.assertEqual(self.gate.phase, HaltPhase.HALTING)
        with self.assertRaises(GateDenied):
            self.gate.acknowledge_halt()
        self.gate.store_available = True
        self.gate.acknowledge_halt()
        self.assertEqual(self.gate.phase, HaltPhase.HALTED)

    def test_duplicate_halt_request_after_halted_store_outage_preserves_halted_epoch(self):
        self.gate.request_halt(reason="operator halt")
        self.gate.acknowledge_halt()
        self.gate.store_available = False
        self.assertEqual(self.gate.request_halt(reason="duplicate while store down"), 8)
        self.assertEqual(self.gate.phase, HaltPhase.HALTED)

    def test_halt_epoch_exhaustion_fails_closed(self):
        from halt_egress_gate import MAX_HALT_EPOCH

        gate = HaltEgressGate(epoch=MAX_HALT_EPOCH)
        with self.assertRaisesRegex(GateDenied, "epoch exhausted"):
            gate.authorize_attempt(attempt_id="before-halt", observed_epoch=MAX_HALT_EPOCH, binding_digest="digest-before-halt")
        self.assertIsNone(gate.request_halt(reason="epoch exhausted"))
        self.assertEqual(gate.phase, HaltPhase.HALT_PENDING)
        with self.assertRaisesRegex(GateDenied, "epoch exhausted"):
            gate.commit_pending_halt()
        with self.assertRaises(GateDenied):
            gate.authorize_attempt(attempt_id="blocked", observed_epoch=MAX_HALT_EPOCH, binding_digest="digest-blocked")


if __name__ == "__main__":
    unittest.main()
