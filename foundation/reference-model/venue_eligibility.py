"""Test-only reference evaluator for NEXUS venue eligibility evidence.

This module validates evidence completeness and freshness. It does not interpret
law, determine legal eligibility, authenticate reviewers, verify signatures,
persist records, or authorize production network access.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class ActivationMode(str, Enum):
    RESEARCH_ONLY = "RESEARCH_ONLY"
    DATA_ONLY = "DATA_ONLY"
    PAPER_ONLY = "PAPER_ONLY"
    LIVE_ELIGIBLE = "LIVE_ELIGIBLE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"


class EvidenceStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    UNKNOWN = "UNKNOWN"
    REJECTED = "REJECTED"


class DenialReason(str, Enum):
    ALLOWED = "ALLOWED"
    NO_RECORD = "NO_RECORD"
    RECORD_SCOPE_MISMATCH = "RECORD_SCOPE_MISMATCH"
    RECORD_NOT_APPROVED = "RECORD_NOT_APPROVED"
    RECORD_SUSPENDED = "RECORD_SUSPENDED"
    RECORD_REVOKED = "RECORD_REVOKED"
    RECORD_NOT_YET_VALID = "RECORD_NOT_YET_VALID"
    RECORD_EXPIRED = "RECORD_EXPIRED"
    EVIDENCE_MISSING = "EVIDENCE_MISSING"
    EVIDENCE_UNKNOWN = "EVIDENCE_UNKNOWN"
    EVIDENCE_REJECTED = "EVIDENCE_REJECTED"
    EVIDENCE_SCOPE_MISMATCH = "EVIDENCE_SCOPE_MISMATCH"
    EVIDENCE_NOT_YET_VALID = "EVIDENCE_NOT_YET_VALID"
    EVIDENCE_EXPIRED = "EVIDENCE_EXPIRED"
    EVIDENCE_STALE = "EVIDENCE_STALE"
    REVIEWER_REFERENCE_MISSING = "REVIEWER_REFERENCE_MISSING"
    OWNER_APPROVAL_MISMATCH = "OWNER_APPROVAL_MISMATCH"


@dataclass(frozen=True)
class EvidenceItem:
    key: str
    status: EvidenceStatus
    scope_digest: str
    observed_at_ms: int
    expires_at_ms: Optional[int] = None
    source_ref: Optional[str] = None
    reviewer_ref: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("evidence key is required")
        if not isinstance(self.status, EvidenceStatus):
            raise TypeError("status must be an EvidenceStatus")
        if not isinstance(self.scope_digest, str) or not self.scope_digest:
            raise ValueError("scope_digest is required")
        if isinstance(self.observed_at_ms, bool) or not isinstance(self.observed_at_ms, int) or self.observed_at_ms < 0:
            raise ValueError("observed_at_ms must be a non-negative integer")
        if self.expires_at_ms is not None and (
            isinstance(self.expires_at_ms, bool) or not isinstance(self.expires_at_ms, int)
            or self.expires_at_ms < 0
        ):
            raise ValueError("expires_at_ms must be a non-negative integer")
        if self.expires_at_ms is not None and self.expires_at_ms <= self.observed_at_ms:
            raise ValueError("evidence expiry must follow observation time")
        if self.source_ref is not None and not isinstance(self.source_ref, str):
            raise TypeError("source_ref must be a string or None")
        if self.reviewer_ref is not None and not isinstance(self.reviewer_ref, str):
            raise TypeError("reviewer_ref must be a string or None")


@dataclass(frozen=True)
class VenueEligibilityRecord:
    record_id: str
    revision: int
    scope_digest: str
    mode: ActivationMode
    created_at_ms: int
    expires_at_ms: Optional[int]
    evidence: Tuple[EvidenceItem, ...]
    owner_approved_revision: Optional[int] = None

    def __post_init__(self):
        if not isinstance(self.record_id, str) or not self.record_id:
            raise ValueError("record_id is required")
        if not isinstance(self.scope_digest, str) or not self.scope_digest:
            raise ValueError("scope_digest is required")
        if not isinstance(self.mode, ActivationMode):
            raise TypeError("mode must be an ActivationMode")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 1:
            raise ValueError("revision must be a positive integer")
        if isinstance(self.created_at_ms, bool) or not isinstance(self.created_at_ms, int) or self.created_at_ms < 0:
            raise ValueError("created_at_ms must be a non-negative integer")
        if self.expires_at_ms is not None and (
            isinstance(self.expires_at_ms, bool) or not isinstance(self.expires_at_ms, int)
            or self.expires_at_ms <= self.created_at_ms
        ):
            raise ValueError("record expiry must be an integer after creation")
        if not isinstance(self.evidence, tuple) or any(
            not isinstance(item, EvidenceItem) for item in self.evidence
        ):
            raise TypeError("evidence must be a tuple of EvidenceItem")
        if self.owner_approved_revision is not None and (
            isinstance(self.owner_approved_revision, bool)
            or not isinstance(self.owner_approved_revision, int)
            or self.owner_approved_revision < 1
        ):
            raise ValueError("owner_approved_revision must be a positive integer or None")
        keys = [item.key for item in self.evidence]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate evidence keys are forbidden")


@dataclass(frozen=True)
class EligibilityPolicy:
    """Explicit policy supplied by the caller; intentionally has no defaults."""

    required_evidence: Tuple[str, ...]
    reviewer_required_evidence: Tuple[str, ...]
    max_age_ms: Tuple[Tuple[str, int], ...]
    require_owner_approval: bool

    def __post_init__(self):
        if not isinstance(self.required_evidence, tuple) or any(
            not isinstance(key, str) or not key for key in self.required_evidence
        ):
            raise TypeError("required_evidence must be a tuple of non-empty strings")
        if not isinstance(self.reviewer_required_evidence, tuple) or any(
            not isinstance(key, str) or not key for key in self.reviewer_required_evidence
        ):
            raise TypeError("reviewer_required_evidence must be a tuple of non-empty strings")
        if len(self.required_evidence) != len(set(self.required_evidence)):
            raise ValueError("duplicate required evidence keys")
        if len(self.reviewer_required_evidence) != len(set(self.reviewer_required_evidence)):
            raise ValueError("duplicate reviewer-required evidence keys")
        if not set(self.reviewer_required_evidence).issubset(self.required_evidence):
            raise ValueError("reviewer-required keys must also be required")
        if not isinstance(self.max_age_ms, tuple) or any(
            not isinstance(pair, tuple) or len(pair) != 2
            or not isinstance(pair[0], str) or not pair[0]
            or isinstance(pair[1], bool) or not isinstance(pair[1], int)
            for pair in self.max_age_ms
        ):
            raise TypeError("max_age_ms must be a tuple of (key, integer) pairs")
        if len(dict(self.max_age_ms)) != len(self.max_age_ms):
            raise ValueError("duplicate max-age keys")
        if any(age < 0 for _, age in self.max_age_ms):
            raise ValueError("max-age values must be non-negative")
        if not set(dict(self.max_age_ms)).issubset(self.required_evidence):
            raise ValueError("max-age keys must be required evidence")
        if not isinstance(self.require_owner_approval, bool):
            raise TypeError("require_owner_approval must be boolean")


@dataclass(frozen=True)
class EligibilityDecision:
    allowed: bool
    reason: DenialReason
    record_id: Optional[str]
    revision: Optional[int]
    mode: ActivationMode


def _deny(reason: DenialReason, record: Optional[VenueEligibilityRecord],
          requested_mode: ActivationMode) -> EligibilityDecision:
    return EligibilityDecision(False, reason,
                               record.record_id if record else None,
                               record.revision if record else None,
                               requested_mode)


def evaluate_eligibility(
    record: Optional[VenueEligibilityRecord],
    *,
    requested_mode: ActivationMode,
    expected_scope_digest: str,
    now_ms: int,
    policy: EligibilityPolicy,
) -> EligibilityDecision:
    """Evaluate one exact scope against explicit evidence requirements.

    This is a deterministic test oracle, not a production authorization boundary.
    Callers must supply the complete policy and a trusted clock.
    """
    if isinstance(now_ms, bool) or not isinstance(now_ms, int) or now_ms < 0:
        raise ValueError("now_ms must be a non-negative integer")
    if not isinstance(expected_scope_digest, str) or not expected_scope_digest:
        raise ValueError("expected_scope_digest is required")
    if not isinstance(requested_mode, ActivationMode):
        raise TypeError("requested_mode must be an ActivationMode")
    if not isinstance(policy, EligibilityPolicy):
        raise TypeError("policy must be an EligibilityPolicy")
    if record is None:
        return _deny(DenialReason.NO_RECORD, None, requested_mode)
    if record.mode == ActivationMode.REVOKED:
        return _deny(DenialReason.RECORD_REVOKED, record, requested_mode)
    if record.mode == ActivationMode.SUSPENDED:
        return _deny(DenialReason.RECORD_SUSPENDED, record, requested_mode)
    if record.mode != requested_mode or requested_mode in (
        ActivationMode.RESEARCH_ONLY, ActivationMode.SUSPENDED, ActivationMode.REVOKED
    ):
        return _deny(DenialReason.RECORD_NOT_APPROVED, record, requested_mode)
    if record.scope_digest != expected_scope_digest:
        return _deny(DenialReason.RECORD_SCOPE_MISMATCH, record, requested_mode)
    if record.created_at_ms > now_ms:
        return _deny(DenialReason.RECORD_NOT_YET_VALID, record, requested_mode)
    if record.expires_at_ms is not None and record.expires_at_ms <= now_ms:
        return _deny(DenialReason.RECORD_EXPIRED, record, requested_mode)

    evidence = {item.key: item for item in record.evidence}
    max_ages = dict(policy.max_age_ms)
    for key in policy.required_evidence:
        item = evidence.get(key)
        if item is None:
            return _deny(DenialReason.EVIDENCE_MISSING, record, requested_mode)
        if item.status == EvidenceStatus.UNKNOWN:
            return _deny(DenialReason.EVIDENCE_UNKNOWN, record, requested_mode)
        if item.status == EvidenceStatus.REJECTED:
            return _deny(DenialReason.EVIDENCE_REJECTED, record, requested_mode)
        if item.scope_digest != expected_scope_digest:
            return _deny(DenialReason.EVIDENCE_SCOPE_MISMATCH, record, requested_mode)
        if item.observed_at_ms > now_ms:
            return _deny(DenialReason.EVIDENCE_NOT_YET_VALID, record, requested_mode)
        if item.expires_at_ms is not None and item.expires_at_ms <= now_ms:
            return _deny(DenialReason.EVIDENCE_EXPIRED, record, requested_mode)
        if key in max_ages and now_ms - item.observed_at_ms > max_ages[key]:
            return _deny(DenialReason.EVIDENCE_STALE, record, requested_mode)
        if key in policy.reviewer_required_evidence and not item.reviewer_ref:
            return _deny(DenialReason.REVIEWER_REFERENCE_MISSING, record, requested_mode)

    if policy.require_owner_approval and record.owner_approved_revision != record.revision:
        return _deny(DenialReason.OWNER_APPROVAL_MISMATCH, record, requested_mode)

    return EligibilityDecision(True, DenialReason.ALLOWED, record.record_id,
                               record.revision, requested_mode)
