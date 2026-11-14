"""Test-only single-process model of eligibility fencing at the egress boundary.

The lock serializes eligibility epoch changes with the adapter side-effect call.
This is a reference model only; it does not prove distributed/process/network fencing.
"""
from dataclasses import dataclass
from enum import Enum
from threading import Lock
from typing import Callable, Dict, Optional


class EgressMode(str, Enum):
    LIVE_ELIGIBLE = "LIVE_ELIGIBLE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"


class DispatchStatus(str, Enum):
    DENIED = "DENIED"
    SENT = "SENT"
    VENUE_REJECTED = "VENUE_REJECTED"
    OUTCOME_UNKNOWN = "OUTCOME_UNKNOWN"


class EgressDenial(str, Enum):
    NONE = "NONE"
    DUPLICATE_COMMAND = "DUPLICATE_COMMAND"
    NOT_LIVE_ELIGIBLE = "NOT_LIVE_ELIGIBLE"
    SCOPE_MISMATCH = "SCOPE_MISMATCH"
    RECORD_MISMATCH = "RECORD_MISMATCH"
    REVISION_MISMATCH = "REVISION_MISMATCH"
    EPOCH_MISMATCH = "EPOCH_MISMATCH"
    SNAPSHOT_EXPIRED = "SNAPSHOT_EXPIRED"
    COMMAND_EXPIRED = "COMMAND_EXPIRED"
    COMMAND_OUTLIVES_SNAPSHOT = "COMMAND_OUTLIVES_SNAPSHOT"


@dataclass(frozen=True)
class EligibilitySnapshot:
    record_id: str
    revision: int
    scope_digest: str
    epoch: int
    mode: EgressMode
    expires_at_ms: Optional[int] = None

    def __post_init__(self):
        if not isinstance(self.record_id, str) or not self.record_id:
            raise ValueError("record_id is required")
        if not isinstance(self.scope_digest, str) or not self.scope_digest:
            raise ValueError("scope_digest is required")
        if not isinstance(self.mode, EgressMode):
            raise TypeError("mode must be an EgressMode")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 1
               for value in (self.revision, self.epoch)):
            raise ValueError("revision and epoch must be positive integers")
        if self.expires_at_ms is not None and (
            isinstance(self.expires_at_ms, bool)
            or not isinstance(self.expires_at_ms, int)
            or self.expires_at_ms < 0
        ):
            raise ValueError("expires_at_ms must be a non-negative integer")


@dataclass(frozen=True)
class EgressCommand:
    command_id: str
    record_id: str
    revision: int
    scope_digest: str
    epoch: int
    expires_at_ms: int
    payload_digest: str

    def __post_init__(self):
        if not all(isinstance(value, str) and value for value in (
            self.command_id, self.record_id, self.scope_digest, self.payload_digest
        )):
            raise ValueError("command identity, scope and payload digest are required")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 1
               for value in (self.revision, self.epoch)):
            raise ValueError("revision and epoch must be positive integers")
        if isinstance(self.expires_at_ms, bool) or not isinstance(self.expires_at_ms, int) or self.expires_at_ms < 0:
            raise ValueError("command expiry must be a non-negative integer")


@dataclass(frozen=True)
class DispatchResult:
    status: DispatchStatus
    denial: EgressDenial
    command_id: str


class EligibilityEgressAuthority:
    """Single-process reference boundary; adapter send executes under one lock."""

    def __init__(self, initial: EligibilitySnapshot):
        self._snapshot = initial
        self._lock = Lock()
        self._outcomes: Dict[str, DispatchResult] = {}

    @property
    def snapshot(self) -> EligibilitySnapshot:
        with self._lock:
            return self._snapshot

    def advance(self, new_snapshot: EligibilitySnapshot) -> EligibilitySnapshot:
        if not isinstance(new_snapshot, EligibilitySnapshot):
            raise TypeError("new_snapshot must be an EligibilitySnapshot")
        with self._lock:
            if new_snapshot.scope_digest != self._snapshot.scope_digest:
                raise ValueError("scope identity cannot change within an authority")
            if new_snapshot.epoch <= self._snapshot.epoch:
                raise ValueError("eligibility epoch must increase monotonically")
            self._snapshot = new_snapshot
            return self._snapshot

    def suspend(self) -> EligibilitySnapshot:
        with self._lock:
            current = self._snapshot
            self._snapshot = EligibilitySnapshot(
                current.record_id, current.revision, current.scope_digest,
                current.epoch + 1, EgressMode.SUSPENDED, current.expires_at_ms
            )
            return self._snapshot

    def dispatch(
        self,
        command: EgressCommand,
        *,
        now_ms: int,
        send: Callable[[EgressCommand], bool],
    ) -> DispatchResult:
        if isinstance(now_ms, bool) or not isinstance(now_ms, int) or now_ms < 0:
            raise ValueError("now_ms must be a non-negative integer")
        if not isinstance(command, EgressCommand):
            raise TypeError("command must be an EgressCommand")
        if not callable(send):
            raise TypeError("send must be callable")
        with self._lock:
            previous = self._outcomes.get(command.command_id)
            if previous is not None:
                return DispatchResult(DispatchStatus.DENIED,
                                      EgressDenial.DUPLICATE_COMMAND,
                                      command.command_id)

            snapshot = self._snapshot
            denial = EgressDenial.NONE
            if snapshot.mode != EgressMode.LIVE_ELIGIBLE:
                denial = EgressDenial.NOT_LIVE_ELIGIBLE
            elif command.scope_digest != snapshot.scope_digest:
                denial = EgressDenial.SCOPE_MISMATCH
            elif command.record_id != snapshot.record_id:
                denial = EgressDenial.RECORD_MISMATCH
            elif command.revision != snapshot.revision:
                denial = EgressDenial.REVISION_MISMATCH
            elif command.epoch != snapshot.epoch:
                denial = EgressDenial.EPOCH_MISMATCH
            elif snapshot.expires_at_ms is not None and snapshot.expires_at_ms <= now_ms:
                denial = EgressDenial.SNAPSHOT_EXPIRED
            elif command.expires_at_ms <= now_ms:
                denial = EgressDenial.COMMAND_EXPIRED
            elif snapshot.expires_at_ms is not None and command.expires_at_ms > snapshot.expires_at_ms:
                denial = EgressDenial.COMMAND_OUTLIVES_SNAPSHOT

            if denial != EgressDenial.NONE:
                result = DispatchResult(DispatchStatus.DENIED, denial, command.command_id)
                self._outcomes[command.command_id] = result
                return result

            # Linearization point: epoch changes cannot complete until this call returns.
            try:
                accepted = send(command)
            except Exception:
                result = DispatchResult(DispatchStatus.OUTCOME_UNKNOWN,
                                        EgressDenial.NONE, command.command_id)
            else:
                if not isinstance(accepted, bool):
                    result = DispatchResult(DispatchStatus.OUTCOME_UNKNOWN,
                                            EgressDenial.NONE, command.command_id)
                elif accepted:
                    result = DispatchResult(DispatchStatus.SENT,
                                            EgressDenial.NONE, command.command_id)
                else:
                    result = DispatchResult(DispatchStatus.VENUE_REJECTED,
                                            EgressDenial.NONE, command.command_id)
            self._outcomes[command.command_id] = result
            return result
