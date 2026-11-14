"""Adversarial tests for the test-only authorization-catalog manifest model."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import unittest

from manifest import (
    CONTEXT_FIELDS, ManifestValidationError, admission_decision, validate_manifest,
)

NOW = datetime(2026, 11, 14, 12, 0, tzinfo=timezone.utc)
DIGEST = "a" * 64
PREVIOUS = "b" * 64


def valid_manifest():
    return {
        "manifest_type": "nexus.postgres.authorization-catalog",
        "schema_version": 1,
        "manifest_id": "manifest-test-001",
        "sequence": 8,
        "predecessor_digest": PREVIOUS,
        "issued_at": "2026-11-14T11:00:00Z",
        "not_before": "2026-11-14T11:30:00Z",
        "expires_at": "2026-11-14T13:00:00Z",
        "environment": "test",
        "deployment_profile": "single-primary",
        "cluster_id": "cluster-test-01",
        "database_id": "database-test-01",
        "postgres_compatibility": "18.7",
        "migration_set_digest": DIGEST,
        "scope": {
            "schemas": ["nexus_app", "nexus_control"],
            "roles": ["nexus_runtime", "nexus_owner"],
            "object_kinds": ["role", "function", "policy"],
        },
        "inventory": [
            {"object_kind": "role", "semantic_id": "nexus_runtime", "properties": {"login": True}},
            {"object_kind": "function", "semantic_id": "nexus_control.authorize(text)", "properties": {"security": "definer"}},
        ],
        "deny_rules": [
            {"rule_id": "deny-public-execute", "target": "PUBLIC EXECUTE on privileged functions", "reason": "least privilege"}
        ],
        "snapshot_profile": "postgres18-auth-catalog-v1",
        "approval_record_ref": "audit://approvals/test-001",
        "signing_policy_id": "nexus-test-policy-v1",
    }


def expected_context():
    m = valid_manifest()
    return {key: m[key] for key in CONTEXT_FIELDS}


def admitted(manifest=None, **overrides):
    args = {
        "expected_context": expected_context(),
        "last_accepted_sequence": 7,
        "last_accepted_digest": PREVIOUS,
        "candidate_digest": "c" * 64,
        "now": NOW,
        "signature_verified": True,
        "approval_verified": True,
        "revocation_state_available": True,
    }
    args.update(overrides)
    return admission_decision(valid_manifest() if manifest is None else manifest, **args)


class ManifestValidationTests(unittest.TestCase):
    def test_valid_manifest_passes_logical_schema(self):
        validate_manifest(valid_manifest())

    def test_unknown_top_level_field_rejected(self):
        m = valid_manifest()
        m["unreviewed"] = True
        with self.assertRaises(ManifestValidationError) as ctx:
            validate_manifest(m)
        self.assertEqual(ctx.exception.code, "MANIFEST.UNKNOWN_FIELD")

    def test_missing_field_rejected(self):
        m = valid_manifest()
        del m["approval_record_ref"]
        with self.assertRaises(ManifestValidationError) as ctx:
            validate_manifest(m)
        self.assertEqual(ctx.exception.code, "MANIFEST.MISSING_FIELD")

    def test_bool_is_not_accepted_as_schema_version(self):
        m = valid_manifest()
        m["schema_version"] = True
        with self.assertRaises(ManifestValidationError) as ctx:
            validate_manifest(m)
        self.assertEqual(ctx.exception.code, "MANIFEST.UNSUPPORTED_VERSION")

    def test_wildcard_scope_rejected(self):
        m = valid_manifest()
        m["scope"]["schemas"] = ["nexus_*"]
        with self.assertRaises(ManifestValidationError) as ctx:
            validate_manifest(m)
        self.assertEqual(ctx.exception.code, "MANIFEST.WILDCARD_SCOPE")

    def test_duplicate_scope_entry_rejected(self):
        m = valid_manifest()
        m["scope"]["roles"].append("nexus_runtime")
        with self.assertRaises(ManifestValidationError) as ctx:
            validate_manifest(m)
        self.assertEqual(ctx.exception.code, "MANIFEST.DUPLICATE_SCOPE_ENTRY")

    def test_unknown_object_kind_rejected(self):
        m = valid_manifest()
        m["scope"]["object_kinds"].append("unclassified_object")
        with self.assertRaises(ManifestValidationError) as ctx:
            validate_manifest(m)
        self.assertEqual(ctx.exception.code, "MANIFEST.UNKNOWN_OBJECT_KIND")

    def test_duplicate_semantic_identity_rejected(self):
        m = valid_manifest()
        m["inventory"].append(deepcopy(m["inventory"][0]))
        with self.assertRaises(ManifestValidationError) as ctx:
            validate_manifest(m)
        self.assertEqual(ctx.exception.code, "MANIFEST.DUPLICATE_SEMANTIC_ID")

    def test_inventory_object_outside_declared_scope_rejected(self):
        m = valid_manifest()
        m["inventory"].append({"object_kind": "extension", "semantic_id": "postgis", "properties": {}})
        with self.assertRaises(ManifestValidationError) as ctx:
            validate_manifest(m)
        self.assertEqual(ctx.exception.code, "MANIFEST.OUT_OF_SCOPE_OBJECT")

    def test_invalid_migration_digest_rejected(self):
        m = valid_manifest()
        m["migration_set_digest"] = "NOT-A-DIGEST"
        with self.assertRaises(ManifestValidationError) as ctx:
            validate_manifest(m)
        self.assertEqual(ctx.exception.code, "MANIFEST.INVALID_MIGRATION_DIGEST")

    def test_invalid_validity_interval_rejected(self):
        m = valid_manifest()
        m["expires_at"] = m["issued_at"]
        with self.assertRaises(ManifestValidationError) as ctx:
            validate_manifest(m)
        self.assertEqual(ctx.exception.code, "MANIFEST.INVALID_VALIDITY_INTERVAL")

    def test_duplicate_deny_rule_id_rejected(self):
        m = valid_manifest()
        m["deny_rules"].append(deepcopy(m["deny_rules"][0]))
        with self.assertRaises(ManifestValidationError) as ctx:
            validate_manifest(m)
        self.assertEqual(ctx.exception.code, "MANIFEST.DUPLICATE_DENY_RULE")


class ManifestAdmissionTests(unittest.TestCase):
    def test_valid_candidate_meets_admission_preconditions(self):
        result = admitted()
        self.assertTrue(result.accepted)
        self.assertEqual(result.code, "MANIFEST.ADMISSION_PRECONDITIONS_MET")

    def test_signature_failure_is_fail_closed(self):
        result = admitted(signature_verified=False)
        self.assertFalse(result.accepted)
        self.assertEqual(result.code, "MANIFEST.SIGNATURE_NOT_VERIFIED")

    def test_approval_failure_is_fail_closed(self):
        result = admitted(approval_verified=False)
        self.assertFalse(result.accepted)
        self.assertEqual(result.code, "MANIFEST.APPROVAL_NOT_VERIFIED")

    def test_unavailable_revocation_state_is_fail_closed(self):
        result = admitted(revocation_state_available=False)
        self.assertFalse(result.accepted)
        self.assertEqual(result.code, "MANIFEST.REVOCATION_UNAVAILABLE")

    def test_context_mismatch_is_fail_closed(self):
        context = expected_context()
        context["database_id"] = "different-database"
        result = admitted(expected_context=context)
        self.assertFalse(result.accepted)
        self.assertEqual(result.code, "MANIFEST.CONTEXT_MISMATCH")

    def test_sequence_rollback_or_gap_is_fail_closed(self):
        result = admitted(last_accepted_sequence=8)
        self.assertFalse(result.accepted)
        self.assertEqual(result.code, "MANIFEST.SEQUENCE_ROLLBACK_OR_GAP")

    def test_predecessor_mismatch_is_fail_closed(self):
        result = admitted(last_accepted_digest="d" * 64)
        self.assertFalse(result.accepted)
        self.assertEqual(result.code, "MANIFEST.PREDECESSOR_MISMATCH")

    def test_expired_manifest_is_fail_closed(self):
        result = admitted(now=datetime(2026, 11, 14, 14, 0, tzinfo=timezone.utc))
        self.assertFalse(result.accepted)
        self.assertEqual(result.code, "MANIFEST.EXPIRED")

    def test_not_yet_valid_manifest_is_fail_closed(self):
        result = admitted(now=datetime(2026, 11, 14, 11, 0, tzinfo=timezone.utc))
        self.assertFalse(result.accepted)
        self.assertEqual(result.code, "MANIFEST.NOT_YET_VALID")


if __name__ == "__main__":
    unittest.main()
