"""Test-only reference model for halt / final-egress authorization ordering.

This models a logical commit order only. It does NOT implement database locks,
a durable halt store, a socket, a network fence, or a production kill switch.
A GATE_COMMITTED attempt is in-flight even before socket initiation. Positive
sender fencing prevents a future write but does not prove that no earlier
socket side effect occurred; the outcome therefore remains unknown.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class GateDenied(RuntimeError):
    """Raised when a final egress authorization is not admissible."""


class HaltPhase(str, Enum):
    ACTIVE = "ACTIVE"
    HALT_PENDING = "HALT_PENDING"
    HALTING = "HALTING"
    HALTED = "HALTED"


class AttemptPhase(str, Enum):
    GATE_COMMITTED = "GATE_COMMITTED"
    SOCKET_INITIATED = "SOCKET_INITIATED"
    SENDER_FENCED_UNKNOWN = "SENDER_FENCED_UNKNOWN"


@dataclass
class Attempt:
    attempt_id: str
    authorized_epoch: int
    phase: AttemptPhase = AttemptPhase.GATE_COMMITTED


@dataclass
class HaltEgressGate:
    """Single-process oracle for the two legal halt/gate commit orders."""

    epoch: int = 1
    phase: HaltPhase = HaltPhase.ACTIVE
    store_available: bool = True
    halt_reason: str | None = None
    attempts: dict[str, Attempt] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.epoch, int) or isinstance(self.epoch, bool) or self.epoch < 1:
            raise ValueError("epoch must be a positive integer")

    def request_halt(self, *, reason: str) -> int | None:
        """Commit halt epoch, or leave a pending request if the store is unavailable."""
        self._require_text(reason, "halt reason")
        self.halt_reason = reason
        if not self.store_available:
            self.phase = HaltPhase.HALT_PENDING
            return None
        if self.phase is HaltPhase.ACTIVE:
            self.epoch += 1
            self.phase = HaltPhase.HALTING
        return self.epoch

    def commit_pending_halt(self) -> int:
        if self.phase is not HaltPhase.HALT_PENDING:
            raise GateDenied("there is no pending halt request")
        if not self.store_available:
            raise GateDenied("authoritative halt store is unavailable")
        self.epoch += 1
        self.phase = HaltPhase.HALTING
        return self.epoch

    def authorize_attempt(self, *, attempt_id: str, observed_epoch: int) -> None:
        """Model the final gate commit; successful IDs are single-use."""
        self._require_text(attempt_id, "attempt_id")
        if not isinstance(observed_epoch, int) or isinstance(observed_epoch, bool):
            raise GateDenied("observed_epoch must be an integer")
        if not self.store_available:
            raise GateDenied("authoritative halt store is unavailable")
        if self.phase is not HaltPhase.ACTIVE:
            raise GateDenied("halt is pending, propagating or enforced")
        if observed_epoch != self.epoch:
            raise GateDenied("stale halt epoch")
        if attempt_id in self.attempts:
            raise GateDenied("attempt authorization is single-use")
        self.attempts[attempt_id] = Attempt(attempt_id, self.epoch)

    def initiate_socket_write(self, *, attempt_id: str) -> None:
        """An earlier gate-committed attempt may start while halt is propagating.

        It cannot start after HALTED acknowledgement. The halt acknowledgement
        is blocked until this attempt is initiated or its sender is positively
        fenced. Fencing does not establish that no earlier side effect occurred.
        """
        attempt = self._attempt(attempt_id)
        if attempt.phase is not AttemptPhase.GATE_COMMITTED:
            raise GateDenied("attempt is not awaiting socket initiation")
        if self.phase is HaltPhase.HALTED:
            raise GateDenied("halt was acknowledged; stale socket initiation denied")
        attempt.phase = AttemptPhase.SOCKET_INITIATED

    def fence_sender(self, *, attempt_id: str, receipt: str) -> None:
        """Record test-fixture evidence that the sender can no longer initiate.

        The absence of an initiation report is not proof that the socket call
        never happened. The attempt therefore remains OUTCOME_UNKNOWN and
        reconciliation-required after the halt is acknowledged.
        """
        attempt = self._attempt(attempt_id)
        self._require_text(receipt, "fence receipt")
        if attempt.phase is not AttemptPhase.GATE_COMMITTED:
            raise GateDenied("only a gate-committed attempt without an initiation report can be fenced here")
        if self.phase not in (HaltPhase.HALT_PENDING, HaltPhase.HALTING):
            raise GateDenied("sender fencing is only part of halt containment")
        # Opaque test fixture only; this is not a verified production attestation.
        attempt.phase = AttemptPhase.SENDER_FENCED_UNKNOWN

    def acknowledge_halt(self) -> None:
        if self.phase is not HaltPhase.HALTING:
            raise GateDenied("a durable halt epoch must be committed before acknowledgement")
        if not self.store_available:
            raise GateDenied("authoritative halt store is unavailable")
        pending = [
            item.attempt_id
            for item in self.attempts.values()
            if item.phase is AttemptPhase.GATE_COMMITTED
        ]
        if pending:
            raise GateDenied(
                "pre-halt gate-committed attempts may still initiate: "
                + ",".join(sorted(pending))
            )
        self.phase = HaltPhase.HALTED

    def reconciliation_required(self) -> tuple[str, ...]:
        """Initiated or fenced-without-report attempts remain externally uncertain."""
        return tuple(
            sorted(
                item.attempt_id
                for item in self.attempts.values()
                if item.phase in (
                    AttemptPhase.SOCKET_INITIATED,
                    AttemptPhase.SENDER_FENCED_UNKNOWN,
                )
            )
        )

    def _attempt(self, attempt_id: str) -> Attempt:
        try:
            return self.attempts[attempt_id]
        except KeyError as exc:
            raise GateDenied("unknown attempt") from exc

    @staticmethod
    def _require_text(value: str, label: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} must be non-empty text")
