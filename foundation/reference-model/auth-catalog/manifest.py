"""Test-only authorization-catalog manifest admission model.

This module validates the logical manifest contract and admission preconditions.
It does NOT parse CBOR, verify COSE signatures, establish trust roots, read PostgreSQL,
or authorize production deployment.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any, Mapping

MANIFEST_TYPE = "nexus.postgres.authorization-catalog"
SCHEMA_VERSION = 1
HEX_DIGEST = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_OBJECT_KINDS = frozenset({
    "role", "membership", "schema", "relation", "sequence", "function",
    "procedure", "policy", "default_privilege", "extension", "language",
    "event_trigger", "database_setting",
})
REQUIRED_FIELDS = frozenset({
    "manifest_type", "schema_version", "manifest_id", "sequence",
    "predecessor_digest", "issued_at", "not_before", "expires_at",
    "environment", "deployment_profile", "cluster_id", "database_id",
    "postgres_compatibility", "migration_set_digest", "scope", "inventory",
    "deny_rules", "snapshot_profile", "approval_record_ref", "signing_policy_id",
})
SCOPE_FIELDS = frozenset({"schemas", "roles", "object_kinds"})
CONTEXT_FIELDS = frozenset({
    "environment", "deployment_profile", "cluster_id", "database_id",
    "postgres_compatibility", "migration_set_digest",
})


class ManifestValidationError(ValueError):
    """Stable, machine-readable manifest validation failure."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class AdmissionDecision:
    accepted: bool
    code: str
    detail: str


def _fail(code: str, detail: str) -> None:
    raise ManifestValidationError(code, detail)


def _is_nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value) and value == value.strip()


def _utc_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        _fail("MANIFEST.INVALID_TIMESTAMP", f"{field} must be an RFC3339 UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        _fail("MANIFEST.INVALID_TIMESTAMP", f"{field} is not a valid timestamp")
    if parsed.tzinfo != timezone.utc:
        _fail("MANIFEST.INVALID_TIMESTAMP", f"{field} must be UTC")
    return parsed


def _string_list(value: Any, field: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        _fail("MANIFEST.INVALID_SCOPE", f"{field} must be a non-empty array")
    if any(not _is_nonempty_text(item) for item in value):
        _fail("MANIFEST.INVALID_SCOPE", f"{field} entries must be non-empty trimmed strings")
    if len(value) != len(set(value)):
        _fail("MANIFEST.DUPLICATE_SCOPE_ENTRY", f"{field} contains duplicate entries")
    if any("*" in item for item in value):
        _fail("MANIFEST.WILDCARD_SCOPE", f"{field} must enumerate explicit values; wildcards are forbidden")
    return value


def validate_manifest(manifest: Any) -> None:
    """Validate the v1 logical object before any canonical wire encoding."""
    if not isinstance(manifest, dict):
        _fail("MANIFEST.INVALID_ROOT", "manifest root must be an object")
    keys = frozenset(manifest)
    missing = REQUIRED_FIELDS - keys
    unknown = keys - REQUIRED_FIELDS
    if missing:
        _fail("MANIFEST.MISSING_FIELD", f"missing required fields: {', '.join(sorted(missing))}")
    if unknown:
        _fail("MANIFEST.UNKNOWN_FIELD", f"unknown fields: {', '.join(sorted(unknown))}")

    if manifest["manifest_type"] != MANIFEST_TYPE:
        _fail("MANIFEST.WRONG_TYPE", "manifest_type is not the NEXUS authorization-catalog type")
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != SCHEMA_VERSION:
        _fail("MANIFEST.UNSUPPORTED_VERSION", "unsupported manifest schema version")
    for field in ("manifest_id", "environment", "deployment_profile", "cluster_id",
                  "database_id", "postgres_compatibility", "snapshot_profile",
                  "approval_record_ref", "signing_policy_id"):
        if not _is_nonempty_text(manifest[field]):
            _fail("MANIFEST.INVALID_FIELD", f"{field} must be non-empty trimmed text")

    if type(manifest["sequence"]) is not int or manifest["sequence"] < 1:
        _fail("MANIFEST.INVALID_SEQUENCE", "sequence must be a positive integer")
    predecessor = manifest["predecessor_digest"]
    if predecessor is not None and (not isinstance(predecessor, str) or not HEX_DIGEST.fullmatch(predecessor)):
        _fail("MANIFEST.INVALID_PREDECESSOR", "predecessor_digest must be null or a lowercase SHA-256 hex digest")
    if not isinstance(manifest["migration_set_digest"], str) or not HEX_DIGEST.fullmatch(manifest["migration_set_digest"]):
        _fail("MANIFEST.INVALID_MIGRATION_DIGEST", "migration_set_digest must be a lowercase SHA-256 hex digest")

    issued = _utc_timestamp(manifest["issued_at"], "issued_at")
    not_before = _utc_timestamp(manifest["not_before"], "not_before")
    expires = _utc_timestamp(manifest["expires_at"], "expires_at")
    if not (issued <= not_before < expires):
        _fail("MANIFEST.INVALID_VALIDITY_INTERVAL", "expected issued_at <= not_before < expires_at")

    scope = manifest["scope"]
    if not isinstance(scope, dict) or frozenset(scope) != SCOPE_FIELDS:
        _fail("MANIFEST.INVALID_SCOPE", "scope must contain exactly schemas, roles and object_kinds")
    _string_list(scope["schemas"], "scope.schemas")
    _string_list(scope["roles"], "scope.roles")
    kinds = _string_list(scope["object_kinds"], "scope.object_kinds")
    if any(kind not in ALLOWED_OBJECT_KINDS for kind in kinds):
        _fail("MANIFEST.UNKNOWN_OBJECT_KIND", "scope contains an unsupported object kind")

    inventory = manifest["inventory"]
    if not isinstance(inventory, list):
        _fail("MANIFEST.INVALID_INVENTORY", "inventory must be an array")
    seen: set[tuple[str, str]] = set()
    for index, item in enumerate(inventory):
        if not isinstance(item, dict) or frozenset(item) != {"object_kind", "semantic_id", "properties"}:
            _fail("MANIFEST.INVALID_INVENTORY_ITEM", f"inventory[{index}] has an invalid shape")
        kind, semantic_id, properties = item["object_kind"], item["semantic_id"], item["properties"]
        if not isinstance(kind, str) or kind not in ALLOWED_OBJECT_KINDS or kind not in kinds:
            _fail("MANIFEST.OUT_OF_SCOPE_OBJECT", f"inventory[{index}] object kind is outside declared scope")
        if not _is_nonempty_text(semantic_id):
            _fail("MANIFEST.INVALID_SEMANTIC_ID", f"inventory[{index}] semantic_id must be non-empty text")
        if not isinstance(properties, dict):
            _fail("MANIFEST.INVALID_PROPERTIES", f"inventory[{index}] properties must be an object")
        identity = (kind, semantic_id)
        if identity in seen:
            _fail("MANIFEST.DUPLICATE_SEMANTIC_ID", f"duplicate semantic identity: {kind}:{semantic_id}")
        seen.add(identity)

    deny_rules = manifest["deny_rules"]
    if not isinstance(deny_rules, list):
        _fail("MANIFEST.INVALID_DENY_RULES", "deny_rules must be an array")
    for index, rule in enumerate(deny_rules):
        if not isinstance(rule, dict) or frozenset(rule) != {"rule_id", "target", "reason"}:
            _fail("MANIFEST.INVALID_DENY_RULE", f"deny_rules[{index}] has an invalid shape")
        if any(not _is_nonempty_text(rule[field]) for field in ("rule_id", "target", "reason")):
            _fail("MANIFEST.INVALID_DENY_RULE", f"deny_rules[{index}] fields must be non-empty trimmed strings")
    rule_ids = [rule["rule_id"] for rule in deny_rules]
    if len(rule_ids) != len(set(rule_ids)):
        _fail("MANIFEST.DUPLICATE_DENY_RULE", "deny rule identifiers must be unique")


def admission_decision(
    manifest: Any,
    *,
    expected_context: Mapping[str, str],
    last_accepted_sequence: int,
    last_accepted_digest: str | None,
    candidate_digest: str,
    now: datetime,
    signature_verified: bool,
    approval_verified: bool,
    revocation_state_available: bool,
) -> AdmissionDecision:
    """Evaluate admission preconditions against externally supplied trusted state.

    Signature/approval booleans are attestations from external verifiers, not
    cryptographic operations performed by this reference model.
    """
    try:
        validate_manifest(manifest)
        if not signature_verified:
            _fail("MANIFEST.SIGNATURE_NOT_VERIFIED", "signature verification is required")
        if not approval_verified:
            _fail("MANIFEST.APPROVAL_NOT_VERIFIED", "independent approval verification is required")
        if not revocation_state_available:
            _fail("MANIFEST.REVOCATION_UNAVAILABLE", "revocation state must be available")
        if not HEX_DIGEST.fullmatch(candidate_digest):
            _fail("MANIFEST.INVALID_CANDIDATE_DIGEST", "candidate digest must be lowercase SHA-256 hex")
        if set(expected_context) != CONTEXT_FIELDS:
            _fail("MANIFEST.INVALID_EXPECTED_CONTEXT", "expected_context must contain the exact context field set")

        for field in CONTEXT_FIELDS:
            if manifest[field] != expected_context[field]:
                _fail("MANIFEST.CONTEXT_MISMATCH", f"manifest context mismatch: {field}")

        if type(last_accepted_sequence) is not int or last_accepted_sequence < 0:
            _fail("MANIFEST.INVALID_TRUST_STATE", "last accepted sequence must be a non-negative integer")
        if last_accepted_sequence == 0:
            if last_accepted_digest is not None:
                _fail("MANIFEST.INVALID_TRUST_STATE", "genesis trust state must not have a predecessor digest")
        elif not isinstance(last_accepted_digest, str) or not HEX_DIGEST.fullmatch(last_accepted_digest):
            _fail("MANIFEST.INVALID_TRUST_STATE", "non-genesis trust state requires a lowercase SHA-256 digest")
        if manifest["sequence"] != last_accepted_sequence + 1:
            _fail("MANIFEST.SEQUENCE_ROLLBACK_OR_GAP", "manifest sequence must be exactly the next approved sequence")
        if manifest["predecessor_digest"] != last_accepted_digest:
            _fail("MANIFEST.PREDECESSOR_MISMATCH", "manifest predecessor does not match external trusted state")
        if now.tzinfo is None or now.utcoffset() is None:
            _fail("MANIFEST.INVALID_CLOCK", "now must be timezone-aware")
        current = now.astimezone(timezone.utc)
        if current < _utc_timestamp(manifest["not_before"], "not_before"):
            _fail("MANIFEST.NOT_YET_VALID", "manifest is not yet valid")
        if current >= _utc_timestamp(manifest["expires_at"], "expires_at"):
            _fail("MANIFEST.EXPIRED", "manifest has expired")
    except ManifestValidationError as exc:
        return AdmissionDecision(False, exc.code, exc.detail)
    return AdmissionDecision(True, "MANIFEST.ADMISSION_PRECONDITIONS_MET",
                             "logical schema, context, freshness and external trust preconditions passed; no production authorization implied")
