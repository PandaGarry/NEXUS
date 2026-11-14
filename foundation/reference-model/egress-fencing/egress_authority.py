"""Test-only control-plane model for fenced egress authority handover.

This model checks transition ordering and fail-closed behavior. It does NOT
revoke network access, terminate a process, validate fence attestations, or
provide a production security boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TransitionDenied(RuntimeError):
    """Raised when an authority transition violates the handover protocol."""


class Phase(str, Enum):
    ACTIVE = "ACTIVE"
    HALTING = "HALTING"
    FENCING = "FENCING"
    FENCED = "FENCED"
    RECONCILING = "RECONCILING"
    READY_TO_GRANT = "READY_TO_GRANT"
    HALTED = "HALTED"


@dataclass
class EgressAuthority:
    account_ref: str
    epoch: int
    active_identity: str
    phase: Phase = Phase.ACTIVE
    old_identity: str | None = None
    old_epoch: int | None = None
    target_identity: str | None = None
    target_epoch: int | None = None
    fence_receipt: str | None = None
    reconciliation_watermark: str | None = None
    halt_reason: str | None = None

    def __post_init__(self) -> None:
        if not self.account_ref or not self.active_identity:
            raise ValueError("account_ref and active_identity are required")
        if not isinstance(self.epoch, int) or isinstance(self.epoch, bool) or self.epoch < 1:
            raise ValueError("epoch must be a positive integer")

    def can_dispatch(self, identity: str, epoch: int) -> bool:
        """Control-plane eligibility only; not a network egress enforcement."""
        return (
            self.phase is Phase.ACTIVE
            and identity == self.active_identity
            and epoch == self.epoch
        )

    def request_takeover(self, *, expected_epoch: int, target_identity: str) -> int:
        self._require(Phase.ACTIVE)
        if expected_epoch != self.epoch:
            raise TransitionDenied("stale expected authority epoch")
        if not target_identity or target_identity == self.active_identity:
            raise TransitionDenied("target identity must be non-empty and distinct")
        self.old_identity = self.active_identity
        self.old_epoch = self.epoch
        self.target_identity = target_identity
        self.target_epoch = self.epoch + 1
        self.phase = Phase.HALTING
        return self.target_epoch

    def acknowledge_halt(self) -> None:
        self._require(Phase.HALTING)
        self.phase = Phase.FENCING

    def attest_old_egress_fenced(self, *, identity: str, receipt: str) -> None:
        self._require(Phase.FENCING)
        if identity != self.old_identity:
            raise TransitionDenied("fence evidence does not identify the old egress authority")
        if not receipt or not receipt.strip():
            raise TransitionDenied("positive fence receipt is required")
        # A caller-supplied receipt is only a test fixture; production must
        # verify a trusted, independently controlled fencing attestation.
        self.fence_receipt = receipt
        self.phase = Phase.FENCED

    def begin_reconciliation(self) -> None:
        self._require(Phase.FENCED)
        self.phase = Phase.RECONCILING

    def complete_reconciliation(self, *, watermark: str) -> None:
        self._require(Phase.RECONCILING)
        if not watermark or not watermark.strip():
            raise TransitionDenied("complete reconciliation watermark is required")
        self.reconciliation_watermark = watermark
        self.phase = Phase.READY_TO_GRANT

    def grant_new_authority(self) -> None:
        self._require(Phase.READY_TO_GRANT)
        if not self.fence_receipt or not self.reconciliation_watermark:
            raise TransitionDenied("fence and reconciliation evidence are both required")
        if self.target_epoch is None or self.target_identity is None:
            raise TransitionDenied("target authority was not established")
        self.epoch = self.target_epoch
        self.active_identity = self.target_identity
        self._clear_handover()
        self.phase = Phase.ACTIVE

    def fail_closed(self, reason: str) -> None:
        if not reason or not reason.strip():
            raise ValueError("halt reason is required")
        self.halt_reason = reason
        self.phase = Phase.HALTED

    def _clear_handover(self) -> None:
        self.old_identity = None
        self.old_epoch = None
        self.target_identity = None
        self.target_epoch = None
        self.fence_receipt = None
        self.reconciliation_watermark = None

    def _require(self, expected: Phase) -> None:
        if self.phase is not expected:
            raise TransitionDenied(
                f"transition requires {expected.value}; current phase is {self.phase.value}"
            )
