import threading
import unittest

from venue_egress_fencing import (
    DispatchStatus, EgressCommand, EgressDenial, EgressMode,
    EligibilityEgressAuthority, EligibilitySnapshot,
)

NOW = 50_000
SCOPE = "scope-digest-v1"


def snapshot(*, epoch=7, mode=EgressMode.LIVE_ELIGIBLE,
             expires=NOW + 10_000, revision=4, record_id="elig-4"):
    return EligibilitySnapshot(record_id, revision, SCOPE, epoch, mode, expires)


def command(*, command_id="cmd-1", epoch=7, scope=SCOPE, revision=4,
            record_id="elig-4", expires=NOW + 1_000):
    return EgressCommand(command_id, record_id, revision, scope, epoch,
                         expires, "payload-digest")


class VenueEligibilityEgressTests(unittest.TestCase):
    def setUp(self):
        self.authority = EligibilityEgressAuthority(snapshot())

    def test_exact_current_scope_revision_epoch_dispatches(self):
        calls = []
        result = self.authority.dispatch(command(), now_ms=NOW,
                                         send=lambda value: calls.append(value) or True)
        self.assertEqual(result.status, DispatchStatus.SENT)
        self.assertEqual(len(calls), 1)

    def test_suspended_state_blocks_dispatch(self):
        self.authority.suspend()
        calls = []
        result = self.authority.dispatch(command(), now_ms=NOW,
                                         send=lambda value: calls.append(value) or True)
        self.assertEqual(result.denial, EgressDenial.NOT_LIVE_ELIGIBLE)
        self.assertEqual(calls, [])

    def test_stale_epoch_is_rejected_after_suspension(self):
        self.authority.suspend()
        result = self.authority.dispatch(command(), now_ms=NOW,
                                         send=lambda value: True)
        self.assertEqual(result.denial, EgressDenial.NOT_LIVE_ELIGIBLE)

    def test_scope_mismatch_denied_before_adapter_call(self):
        result = self.authority.dispatch(command(scope="other"), now_ms=NOW,
                                         send=lambda value: self.fail("must not send"))
        self.assertEqual(result.denial, EgressDenial.SCOPE_MISMATCH)

    def test_record_identity_mismatch_denied(self):
        result = self.authority.dispatch(command(record_id="other"), now_ms=NOW,
                                         send=lambda value: self.fail("must not send"))
        self.assertEqual(result.denial, EgressDenial.RECORD_MISMATCH)

    def test_revision_mismatch_denied(self):
        result = self.authority.dispatch(command(revision=3), now_ms=NOW,
                                         send=lambda value: self.fail("must not send"))
        self.assertEqual(result.denial, EgressDenial.REVISION_MISMATCH)

    def test_epoch_mismatch_denied(self):
        result = self.authority.dispatch(command(epoch=6), now_ms=NOW,
                                         send=lambda value: self.fail("must not send"))
        self.assertEqual(result.denial, EgressDenial.EPOCH_MISMATCH)

    def test_expired_snapshot_and_command_are_denied(self):
        authority = EligibilityEgressAuthority(snapshot(expires=NOW))
        result = authority.dispatch(command(), now_ms=NOW, send=lambda value: True)
        self.assertEqual(result.denial, EgressDenial.SNAPSHOT_EXPIRED)
        result2 = self.authority.dispatch(command(expires=NOW), now_ms=NOW,
                                          send=lambda value: True)
        self.assertEqual(result2.denial, EgressDenial.COMMAND_EXPIRED)

    def test_command_cannot_outlive_eligibility_snapshot(self):
        result = self.authority.dispatch(command(expires=NOW + 20_000), now_ms=NOW,
                                         send=lambda value: True)
        self.assertEqual(result.denial, EgressDenial.COMMAND_OUTLIVES_SNAPSHOT)

    def test_command_id_is_one_time_even_after_denial(self):
        denied = self.authority.dispatch(command(epoch=6), now_ms=NOW,
                                         send=lambda value: True)
        duplicate = self.authority.dispatch(command(), now_ms=NOW,
                                            send=lambda value: self.fail("duplicate send"))
        self.assertEqual(denied.denial, EgressDenial.EPOCH_MISMATCH)
        self.assertEqual(duplicate.denial, EgressDenial.DUPLICATE_COMMAND)

    def test_ambiguous_send_is_outcome_unknown_and_never_retried(self):
        calls = []
        def uncertain(value):
            calls.append(value)
            raise TimeoutError("simulated lost acknowledgement")
        first = self.authority.dispatch(command(), now_ms=NOW, send=uncertain)
        second = self.authority.dispatch(command(), now_ms=NOW,
                                         send=lambda value: calls.append(value) or True)
        self.assertEqual(first.status, DispatchStatus.OUTCOME_UNKNOWN)
        self.assertEqual(second.denial, EgressDenial.DUPLICATE_COMMAND)
        self.assertEqual(len(calls), 1)

    def test_venue_rejection_is_distinct_from_unknown(self):
        result = self.authority.dispatch(command(), now_ms=NOW, send=lambda value: False)
        self.assertEqual(result.status, DispatchStatus.VENUE_REJECTED)

    def test_suspension_serializes_after_in_progress_send(self):
        entered = threading.Event()
        release = threading.Event()
        suspend_started = threading.Event()
        suspended = threading.Event()
        results = []

        def send(value):
            entered.set()
            if not release.wait(2):
                raise TimeoutError("test release timed out")
            return True

        dispatch_thread = threading.Thread(
            target=lambda: results.append(
                self.authority.dispatch(command(), now_ms=NOW, send=send)
            )
        )
        dispatch_thread.start()
        self.assertTrue(entered.wait(1))

        def suspend():
            suspend_started.set()
            self.authority.suspend()
            suspended.set()

        suspend_thread = threading.Thread(target=suspend)
        suspend_thread.start()
        self.assertTrue(suspend_started.wait(1))
        self.assertFalse(suspended.wait(0.05))
        release.set()
        dispatch_thread.join(2)
        suspend_thread.join(2)

        self.assertFalse(dispatch_thread.is_alive())
        self.assertFalse(suspend_thread.is_alive())
        self.assertEqual(results[0].status, DispatchStatus.SENT)
        self.assertTrue(suspended.is_set())
        self.assertEqual(self.authority.snapshot.mode, EgressMode.SUSPENDED)
        self.assertEqual(self.authority.snapshot.epoch, 8)

    def test_dispatch_after_suspension_epoch_advance_cannot_send(self):
        self.authority.suspend()
        calls = []
        result = self.authority.dispatch(command(command_id="cmd-after-halt"),
                                         now_ms=NOW,
                                         send=lambda value: calls.append(value) or True)
        self.assertEqual(result.status, DispatchStatus.DENIED)
        self.assertEqual(calls, [])

    def test_epoch_must_increase_and_scope_identity_is_immutable(self):
        with self.assertRaisesRegex(ValueError, "increase"):
            self.authority.advance(snapshot(epoch=7))
        with self.assertRaisesRegex(ValueError, "scope"):
            self.authority.advance(EligibilitySnapshot(
                "elig-4", 4, "other", 8, EgressMode.LIVE_ELIGIBLE, NOW + 10_000
            ))

    def test_invalid_clock_is_rejected(self):
        with self.assertRaises(ValueError):
            self.authority.dispatch(command(), now_ms=True, send=lambda value: True)

    def test_boolean_revision_is_not_accepted(self):
        with self.assertRaises(ValueError):
            snapshot(revision=True)

    def test_string_mode_is_not_accepted(self):
        with self.assertRaises(TypeError):
            snapshot(mode="LIVE_ELIGIBLE")

    def test_non_command_and_non_callable_adapter_are_rejected(self):
        with self.assertRaises(TypeError):
            self.authority.dispatch("not-a-command", now_ms=NOW, send=lambda value: True)
        with self.assertRaises(TypeError):
            self.authority.dispatch(command(), now_ms=NOW, send=None)


if __name__ == "__main__":
    unittest.main()
