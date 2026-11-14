import unittest

from egress_authority import EgressAuthority, Phase, TransitionDenied


class EgressAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.authority = EgressAuthority(
            account_ref="acct-1", epoch=7, active_identity="egress-a"
        )

    def takeover_to_b(self):
        self.assertEqual(
            self.authority.request_takeover(expected_epoch=7, target_identity="egress-b"),
            8,
        )
        self.authority.acknowledge_halt()

    def test_initial_authority_can_dispatch_only_for_matching_identity_and_epoch(self):
        self.assertTrue(self.authority.can_dispatch("egress-a", 7))
        self.assertFalse(self.authority.can_dispatch("egress-b", 7))
        self.assertFalse(self.authority.can_dispatch("egress-a", 6))
        self.assertFalse(self.authority.can_dispatch("egress-a", 8))

    def test_takeover_immediately_revokes_old_epoch_at_control_plane(self):
        self.authority.request_takeover(expected_epoch=7, target_identity="egress-b")
        self.assertFalse(self.authority.can_dispatch("egress-a", 7))
        self.assertFalse(self.authority.can_dispatch("egress-b", 8))
        self.assertEqual(self.authority.phase, Phase.HALTING)

    def test_new_authority_cannot_be_granted_before_fence(self):
        self.takeover_to_b()
        with self.assertRaises(TransitionDenied):
            self.authority.grant_new_authority()

    def test_reconciliation_cannot_start_before_positive_fence_receipt(self):
        self.takeover_to_b()
        with self.assertRaises(TransitionDenied):
            self.authority.begin_reconciliation()

    def test_wrong_identity_cannot_satisfy_fence(self):
        self.takeover_to_b()
        with self.assertRaises(TransitionDenied):
            self.authority.attest_old_egress_fenced(
                identity="egress-b", receipt="fence-receipt-1"
            )
        self.assertEqual(self.authority.phase, Phase.FENCING)

    def test_empty_fence_receipt_is_rejected(self):
        self.takeover_to_b()
        with self.assertRaises(TransitionDenied):
            self.authority.attest_old_egress_fenced(identity="egress-a", receipt=" ")

    def test_new_authority_cannot_be_granted_before_reconciliation(self):
        self.takeover_to_b()
        self.authority.attest_old_egress_fenced(
            identity="egress-a", receipt="fence-receipt-1"
        )
        self.authority.begin_reconciliation()
        with self.assertRaises(TransitionDenied):
            self.authority.grant_new_authority()

    def test_empty_reconciliation_watermark_is_rejected(self):
        self.takeover_to_b()
        self.authority.attest_old_egress_fenced(
            identity="egress-a", receipt="fence-receipt-1"
        )
        self.authority.begin_reconciliation()
        with self.assertRaises(TransitionDenied):
            self.authority.complete_reconciliation(watermark=" ")

    def test_successful_takeover_requires_fence_and_reconciliation(self):
        self.takeover_to_b()
        self.authority.attest_old_egress_fenced(
            identity="egress-a", receipt="fence-receipt-1"
        )
        self.authority.begin_reconciliation()
        self.authority.complete_reconciliation(watermark="venue-cursor-900")
        self.authority.grant_new_authority()
        self.assertEqual(self.authority.phase, Phase.ACTIVE)
        self.assertEqual(self.authority.epoch, 8)
        self.assertEqual(self.authority.active_identity, "egress-b")
        self.assertTrue(self.authority.can_dispatch("egress-b", 8))
        self.assertFalse(self.authority.can_dispatch("egress-a", 7))

    def test_unknown_fence_fails_closed_and_cannot_be_regranted(self):
        self.takeover_to_b()
        self.authority.fail_closed("old host fencing outcome unknown")
        self.assertEqual(self.authority.phase, Phase.HALTED)
        self.assertFalse(self.authority.can_dispatch("egress-a", 7))
        self.assertFalse(self.authority.can_dispatch("egress-b", 8))
        with self.assertRaises(TransitionDenied):
            self.authority.grant_new_authority()

    def test_stale_takeover_epoch_is_rejected(self):
        with self.assertRaises(TransitionDenied):
            self.authority.request_takeover(expected_epoch=6, target_identity="egress-b")
        self.assertEqual(self.authority.phase, Phase.ACTIVE)

    def test_takeover_target_must_be_distinct(self):
        with self.assertRaises(TransitionDenied):
            self.authority.request_takeover(expected_epoch=7, target_identity="egress-a")

    def test_halted_authority_cannot_resume_through_takeover_api(self):
        self.authority.fail_closed("operator halt")
        with self.assertRaises(TransitionDenied):
            self.authority.request_takeover(expected_epoch=7, target_identity="egress-b")


if __name__ == "__main__":
    unittest.main()
