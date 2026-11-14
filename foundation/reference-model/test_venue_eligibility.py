import unittest

from venue_eligibility import (
    ActivationMode, DenialReason, EligibilityPolicy, EvidenceItem,
    EvidenceStatus, VenueEligibilityRecord, evaluate_eligibility,
)

NOW = 10_000
SCOPE = "sha256:venue-account-product-scope"
POLICY = EligibilityPolicy(
    required_evidence=("jurisdiction", "product", "venue_terms", "api_rights"),
    reviewer_required_evidence=("jurisdiction", "product"),
    max_age_ms=(("jurisdiction", 5_000), ("venue_terms", 8_000)),
    require_owner_approval=True,
)


def evidence(key, *, status=EvidenceStatus.CONFIRMED, scope=SCOPE,
             observed=NOW - 100, expires=None, reviewer="review-ref"):
    return EvidenceItem(key, status, scope, observed, expires,
                        source_ref="source-ref", reviewer_ref=reviewer)


def record(*, mode=ActivationMode.LIVE_ELIGIBLE, revision=3, scope=SCOPE,
           created=NOW - 500, expires=NOW + 5_000, items=None, owner_revision=3):
    if items is None:
        items = (
            evidence("jurisdiction"),
            evidence("product"),
            evidence("venue_terms"),
            evidence("api_rights"),
        )
    return VenueEligibilityRecord("eligibility-001", revision, scope, mode,
                                  created, expires, tuple(items), owner_revision)


def decision(value, *, requested=ActivationMode.LIVE_ELIGIBLE,
             scope=SCOPE, policy=POLICY, now=NOW):
    return evaluate_eligibility(value, requested_mode=requested,
                                expected_scope_digest=scope, now_ms=now,
                                policy=policy)


class VenueEligibilityReferenceTests(unittest.TestCase):
    def test_complete_current_evidence_allows_exact_scope(self):
        result = decision(record())
        self.assertTrue(result.allowed)
        self.assertEqual(result.reason, DenialReason.ALLOWED)
        self.assertEqual(result.revision, 3)

    def test_missing_record_fails_closed(self):
        self.assertEqual(decision(None).reason, DenialReason.NO_RECORD)

    def test_record_scope_mismatch_denied(self):
        self.assertEqual(decision(record(scope="other")).reason,
                         DenialReason.RECORD_SCOPE_MISMATCH)

    def test_evidence_scope_mismatch_denied(self):
        items = list(record().evidence)
        items[1] = evidence("product", scope="other")
        self.assertEqual(decision(record(items=items)).reason,
                         DenialReason.EVIDENCE_SCOPE_MISMATCH)

    def test_unknown_evidence_denied(self):
        items = list(record().evidence)
        items[0] = evidence("jurisdiction", status=EvidenceStatus.UNKNOWN)
        self.assertEqual(decision(record(items=items)).reason,
                         DenialReason.EVIDENCE_UNKNOWN)

    def test_rejected_evidence_denied(self):
        items = list(record().evidence)
        items[1] = evidence("product", status=EvidenceStatus.REJECTED)
        self.assertEqual(decision(record(items=items)).reason,
                         DenialReason.EVIDENCE_REJECTED)

    def test_missing_evidence_denied(self):
        self.assertEqual(decision(record(items=record().evidence[:-1])).reason,
                         DenialReason.EVIDENCE_MISSING)

    def test_expired_record_denied_at_exact_boundary(self):
        self.assertEqual(decision(record(expires=NOW)).reason,
                         DenialReason.RECORD_EXPIRED)

    def test_expired_evidence_denied_at_exact_boundary(self):
        items = list(record().evidence)
        items[2] = evidence("venue_terms", expires=NOW)
        self.assertEqual(decision(record(items=items)).reason,
                         DenialReason.EVIDENCE_EXPIRED)

    def test_stale_evidence_denied(self):
        items = list(record().evidence)
        items[0] = evidence("jurisdiction", observed=NOW - 5_001)
        self.assertEqual(decision(record(items=items)).reason,
                         DenialReason.EVIDENCE_STALE)

    def test_future_record_creation_denied(self):
        self.assertEqual(decision(record(created=NOW + 1)).reason,
                         DenialReason.RECORD_NOT_YET_VALID)

    def test_future_evidence_denied(self):
        items = list(record().evidence)
        items[3] = evidence("api_rights", observed=NOW + 1)
        self.assertEqual(decision(record(items=items)).reason,
                         DenialReason.EVIDENCE_NOT_YET_VALID)

    def test_missing_reviewer_reference_denied(self):
        items = list(record().evidence)
        items[0] = evidence("jurisdiction", reviewer=None)
        self.assertEqual(decision(record(items=items)).reason,
                         DenialReason.REVIEWER_REFERENCE_MISSING)

    def test_owner_approval_must_bind_exact_revision(self):
        self.assertEqual(decision(record(owner_revision=2)).reason,
                         DenialReason.OWNER_APPROVAL_MISMATCH)

    def test_suspended_record_denied_even_with_complete_evidence(self):
        self.assertEqual(decision(record(mode=ActivationMode.SUSPENDED)).reason,
                         DenialReason.RECORD_SUSPENDED)

    def test_revoked_record_denied_even_with_complete_evidence(self):
        self.assertEqual(decision(record(mode=ActivationMode.REVOKED)).reason,
                         DenialReason.RECORD_REVOKED)

    def test_lower_mode_does_not_authorize_live(self):
        self.assertEqual(decision(record(mode=ActivationMode.DATA_ONLY)).reason,
                         DenialReason.RECORD_NOT_APPROVED)

    def test_live_record_does_not_implicitly_authorize_data_only_scope(self):
        self.assertEqual(decision(record(), requested=ActivationMode.DATA_ONLY).reason,
                         DenialReason.RECORD_NOT_APPROVED)

    def test_research_only_is_not_an_execution_mode(self):
        self.assertEqual(decision(record(mode=ActivationMode.RESEARCH_ONLY)).reason,
                         DenialReason.RECORD_NOT_APPROVED)

    def test_duplicate_evidence_keys_are_rejected_at_construction(self):
        item = evidence("jurisdiction")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            record(items=(item, item))

    def test_policy_has_no_implicit_defaults(self):
        with self.assertRaises(TypeError):
            EligibilityPolicy()

    def test_expiry_and_max_age_are_independent(self):
        items = list(record().evidence)
        items[0] = evidence("jurisdiction", observed=NOW - 4_000,
                            expires=NOW + 1)
        self.assertTrue(decision(record(items=items)).allowed)
        self.assertEqual(decision(record(items=items), now=NOW + 2).reason,
                         DenialReason.EVIDENCE_EXPIRED)

    def test_max_age_boundary_is_inclusive(self):
        items = list(record().evidence)
        items[0] = evidence("jurisdiction", observed=NOW - 5_000)
        self.assertTrue(decision(record(items=items)).allowed)

    def test_invalid_time_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            decision(record(), now=-1)


if __name__ == "__main__":
    unittest.main()
