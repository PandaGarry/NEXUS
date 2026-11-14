"""NEXUS command-gateway reference model.

TEST-ONLY conformance model. SQLite is used to make transaction boundaries
executable; this is not a production database, signer, venue adapter or
security boundary. A real deployment needs a separately reviewed service,
cryptographic key custody, durable database configuration and adapter proofs.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
import hmac
import json
import re
import sqlite3
from typing import Callable, Optional


class GatewayError(Exception):
    pass


class Denied(GatewayError):
    pass


class InjectedCrash(GatewayError):
    """Test-only crash at a named durability boundary."""


class CommandState(str, Enum):
    PERSISTED = "PERSISTED"
    DISPATCHING = "DISPATCHING"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    OUTCOME_UNKNOWN = "OUTCOME_UNKNOWN"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class CanonicalCommand:
    command_id: str
    command_type: str
    environment: str
    account_ref: str
    venue_id: str
    instrument_id: str
    instrument_spec_version: str
    policy_version: str
    reservation_id: str
    halt_epoch: int
    quantity: str
    price: Optional[str]
    created_at: str
    expires_at: str

    def canonical_bytes(self) -> bytes:
        _validate_decimal(self.quantity, positive=True)
        if self.price is not None:
            _validate_decimal(self.price, positive=True)
        if self.command_type != "CREATE":
            raise Denied("SCHEMA_UNSUPPORTED_IN_REFERENCE_SLICE")
        if self.environment not in {"PAPER", "SANDBOX", "LIVE"}:
            raise Denied("SCHEMA_INVALID_ENVIRONMENT")
        if self.halt_epoch < 0:
            raise Denied("SCHEMA_INVALID_HALT_EPOCH")
        for name, value in asdict(self).items():
            if name not in {"price"} and (value is None or value == ""):
                raise Denied(f"SCHEMA_MISSING_{name.upper()}")
        payload = {"schema_id": "nexus.canonical_trade_command", "schema_version": 1, **asdict(self)}
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")

    @property
    def digest(self) -> str:
        return hashlib.sha256(b"NEXUS-CANONICAL-TRADE-COMMAND-V1\0" + self.canonical_bytes()).hexdigest()


def _validate_decimal(value: str, positive: bool) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.[0-9]*[1-9])?", value):
        raise Denied("CANONICALIZATION_INVALID_DECIMAL")
    if positive and value == "0":
        raise Denied("CANONICALIZATION_NON_POSITIVE_DECIMAL")


@dataclass(frozen=True)
class Approval:
    approval_id: str
    audience: str
    command_id: str
    command_digest: str
    account_ref: str
    venue_id: str
    instrument_id: str
    instrument_spec_version: str
    policy_version: str
    reservation_id: str
    halt_epoch: int
    issued_at: int
    expires_at: int
    nonce: str
    signature: str

    def claims(self) -> dict:
        d = asdict(self)
        d.pop("signature")
        return d


def _mac(claims: dict, key: bytes) -> str:
    raw = json.dumps(claims, sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(key, b"NEXUS-TEST-APPROVAL-V1\0" + raw, hashlib.sha256).hexdigest()


def issue_test_approval(command: CanonicalCommand, *, key: bytes, now: int,
                         approval_id: str = "approval-1", nonce: str = "nonce-1",
                         audience: str = "nexus-execution-gateway", ttl: int = 30) -> Approval:
    """Test fixture only; production Risk Engine signing is deliberately absent."""
    claims = dict(approval_id=approval_id, audience=audience,
                  command_id=command.command_id, command_digest=command.digest,
                  account_ref=command.account_ref, venue_id=command.venue_id,
                  instrument_id=command.instrument_id,
                  instrument_spec_version=command.instrument_spec_version,
                  policy_version=command.policy_version,
                  reservation_id=command.reservation_id, halt_epoch=command.halt_epoch,
                  issued_at=now, expires_at=now + ttl, nonce=nonce)
    return Approval(**claims, signature=_mac(claims, key))


class SQLiteOutbox:
    """Small transactional reference store; one connection per instance."""
    def __init__(self, path: str):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS reservations (
            reservation_id TEXT PRIMARY KEY, command_id TEXT NOT NULL UNIQUE,
            state TEXT NOT NULL CHECK(state IN ('ACTIVE','CONSUMED','RELEASED'))
        );
        CREATE TABLE IF NOT EXISTS consumed_approvals (
            approval_id TEXT PRIMARY KEY, nonce TEXT NOT NULL UNIQUE,
            command_id TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS commands (
            command_id TEXT PRIMARY KEY, digest TEXT NOT NULL, payload BLOB NOT NULL,
            approval_id TEXT NOT NULL UNIQUE, reservation_id TEXT NOT NULL,
            halt_epoch INTEGER NOT NULL, approval_expires_at INTEGER NOT NULL,
            state TEXT NOT NULL, attempt INTEGER NOT NULL DEFAULT 0,
            venue_reference TEXT, outcome TEXT
        );
        CREATE TABLE IF NOT EXISTS venue_observations (
            observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            command_id TEXT NOT NULL,
            observation_type TEXT NOT NULL,
            venue_reference TEXT NOT NULL,
            authority_epoch INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS dispatch_observations (
            observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            command_id TEXT NOT NULL,
            observation_type TEXT NOT NULL,
            detail TEXT NOT NULL,
            authority_epoch INTEGER NOT NULL
        );
        """)

    def add_reservation(self, reservation_id: str, command_id: str) -> None:
        self.db.execute("INSERT INTO reservations VALUES(?,?, 'ACTIVE')", (reservation_id, command_id))

    def close(self) -> None:
        self.db.close()


class FakeVenueAdapter:
    """A test spy; production code must not expose this surface to strategies/AI."""
    def __init__(self, result: str = "accepted"):
        self.calls: list[bytes] = []
        self.result = result

    def send(self, payload: bytes) -> str:
        self.calls.append(payload)
        if self.result == "timeout":
            raise TimeoutError("simulated timeout after possible venue receipt")
        return self.result


class CommandGateway:
    def __init__(self, store: SQLiteOutbox, adapter: FakeVenueAdapter, *,
                 verification_key: bytes, clock: Callable[[], int],
                 current_halt_epoch: Callable[[str], int]):
        self.store, self._adapter = store, adapter
        self._key, self._clock = verification_key, clock
        self._halt_epoch = current_halt_epoch

    def persist_approved(self, command: CanonicalCommand, approval: Approval,
                         *, crash_after_commit: bool = False,
                         fail_before_commit: bool = False) -> None:
        payload = command.canonical_bytes()
        self._verify(command, approval)
        db = self.store.db
        db.execute("BEGIN IMMEDIATE")
        try:
            row = db.execute("SELECT command_id,state FROM reservations WHERE reservation_id=?",
                             (approval.reservation_id,)).fetchone()
            if row != (command.command_id, "ACTIVE"):
                raise Denied("RESERVATION_NOT_ACTIVE_OR_WRONG_SCOPE")
            if db.execute("SELECT 1 FROM commands WHERE command_id=?", (command.command_id,)).fetchone():
                raise Denied("COMMAND_DUPLICATE")
            db.execute("INSERT INTO consumed_approvals VALUES(?,?,?)",
                       (approval.approval_id, approval.nonce, command.command_id))
            db.execute("UPDATE reservations SET state='CONSUMED' WHERE reservation_id=?",
                       (approval.reservation_id,))
            db.execute("INSERT INTO commands(command_id,digest,payload,approval_id,reservation_id,halt_epoch,approval_expires_at,state) VALUES(?,?,?,?,?,?,?,?)",
                       (command.command_id, command.digest, payload, approval.approval_id,
                        approval.reservation_id, command.halt_epoch, approval.expires_at,
                        CommandState.PERSISTED.value))
            if fail_before_commit:
                raise InjectedCrash("simulated transaction failure before commit")
            db.execute("COMMIT")
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        if crash_after_commit:
            raise InjectedCrash("crash after durable commit, before dispatch")

    def dispatch(self, command_id: str, *, crash_after_dispatch_marker: bool = False,
                 crash_after_venue_accept: bool = False) -> str:
        db = self.store.db
        db.execute("BEGIN IMMEDIATE")
        try:
            row = db.execute("SELECT payload,state,halt_epoch,approval_expires_at FROM commands WHERE command_id=?", (command_id,)).fetchone()
            if row is None:
                raise Denied("COMMAND_NOT_PERSISTED")
            payload, state, halt_epoch, approval_expires_at = row
            if state != CommandState.PERSISTED.value:
                raise Denied("COMMAND_NOT_DISPATCHABLE")
            if self._clock() >= approval_expires_at or self._halt_epoch_for_command(command_id) != halt_epoch:
                db.execute("UPDATE commands SET state=?,outcome=? WHERE command_id=?",
                           (CommandState.REJECTED.value, "APPROVAL_EXPIRED_OR_HALT_EPOCH_CHANGED", command_id))
                db.execute("COMMIT")
                raise Denied("APPROVAL_EXPIRED_OR_HALT_EPOCH_CHANGED")
            db.execute("UPDATE commands SET state=?,attempt=attempt+1 WHERE command_id=?",
                       (CommandState.DISPATCHING.value, command_id))
            db.execute("COMMIT")
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        if crash_after_dispatch_marker:
            raise InjectedCrash("crash after durable DISPATCHING marker")
        # This second check narrows, but cannot eliminate, the external-send race.
        if self._clock() >= approval_expires_at or self._halt_epoch_for_command(command_id) != halt_epoch:
            cursor = db.execute(
                "UPDATE commands SET state=?,outcome=? "
                "WHERE command_id=? AND state=? AND halt_epoch=?",
                (CommandState.REJECTED.value, "APPROVAL_EXPIRED_OR_HALT_EPOCH_CHANGED",
                 command_id, CommandState.DISPATCHING.value, halt_epoch))
            if cursor.rowcount != 1:
                self._record_stale_dispatch_observation(
                    command_id, "STALE_PRE_SEND_GUARD",
                    "approval expired or halt epoch changed after authority was superseded",
                    halt_epoch)
                return "STALE_STATE_PRESERVED"
            raise Denied("APPROVAL_EXPIRED_OR_HALT_EPOCH_CHANGED")
        try:
            result = self._adapter.send(payload)
        except Exception as exc:
            cursor = db.execute(
                "UPDATE commands SET state=?,outcome=? "
                "WHERE command_id=? AND state=? AND halt_epoch=?",
                (CommandState.OUTCOME_UNKNOWN.value, type(exc).__name__,
                 command_id, CommandState.DISPATCHING.value, halt_epoch))
            if cursor.rowcount != 1:
                self._record_stale_dispatch_observation(
                    command_id, "STALE_SEND_ERROR",
                    type(exc).__name__, halt_epoch)
                return "STALE_RESPONSE_RECORDED"
            return CommandState.OUTCOME_UNKNOWN.value
        if crash_after_venue_accept:
            # The venue may have accepted the command, but the ACK is not durable.
            raise InjectedCrash("crash after venue acceptance, before ACK persistence")
        cursor = db.execute(
            "UPDATE commands SET state=?,venue_reference=?,outcome=? "
            "WHERE command_id=? AND state=? AND halt_epoch=?",
            (CommandState.ACKNOWLEDGED.value, result, "ACCEPTED_NOT_FILLED",
             command_id, CommandState.DISPATCHING.value, halt_epoch))
        if cursor.rowcount != 1:
            # A recovered or superseded command cannot be overwritten by a late worker response.
            db.execute(
                "INSERT INTO venue_observations(command_id,observation_type,venue_reference,authority_epoch) "
                "VALUES(?,?,?,?)",
                (command_id, "LATE_ACK_STALE_STATE", result, halt_epoch))
            return "STALE_RESPONSE_RECORDED"
        return CommandState.ACKNOWLEDGED.value

    def recover_after_restart(self) -> list[str]:
        db = self.store.db
        rows = db.execute("SELECT command_id FROM commands WHERE state=?",
                          (CommandState.DISPATCHING.value,)).fetchall()
        for (command_id,) in rows:
            db.execute("UPDATE commands SET state=?,outcome=? WHERE command_id=?",
                       (CommandState.OUTCOME_UNKNOWN.value, "PROCESS_RESTART_DURING_DISPATCH", command_id))
        return [r[0] for r in rows]

    def _record_stale_dispatch_observation(
        self, command_id: str, observation_type: str, detail: str, authority_epoch: int
    ) -> None:
        self.store.db.execute(
            "INSERT INTO dispatch_observations(command_id,observation_type,detail,authority_epoch) "
            "VALUES(?,?,?,?)",
            (command_id, observation_type, detail, authority_epoch))

    def _halt_epoch_for_command(self, command_id: str) -> int:
        row = self.store.db.execute("SELECT payload FROM commands WHERE command_id=?", (command_id,)).fetchone()
        if row is None:
            raise Denied("COMMAND_NOT_PERSISTED")
        payload = json.loads(row[0])
        return self._halt_epoch(payload["account_ref"])

    def state(self, command_id: str) -> str:
        row = self.store.db.execute("SELECT state FROM commands WHERE command_id=?", (command_id,)).fetchone()
        if row is None:
            raise KeyError(command_id)
        return row[0]

    def _verify(self, command: CanonicalCommand, approval: Approval) -> None:
        if not hmac.compare_digest(approval.signature, _mac(approval.claims(), self._key)):
            raise Denied("APPROVAL_INVALID_SIGNATURE")
        if approval.audience != "nexus-execution-gateway":
            raise Denied("APPROVAL_WRONG_AUDIENCE")
        if approval.command_id != command.command_id or approval.command_digest != command.digest:
            raise Denied("APPROVAL_COMMAND_BINDING_MISMATCH")
        scope = (approval.account_ref, approval.venue_id, approval.instrument_id,
                 approval.instrument_spec_version, approval.policy_version,
                 approval.reservation_id, approval.halt_epoch)
        expected = (command.account_ref, command.venue_id, command.instrument_id,
                    command.instrument_spec_version, command.policy_version,
                    command.reservation_id, command.halt_epoch)
        if scope != expected:
            raise Denied("APPROVAL_SCOPE_MISMATCH")
        now = self._clock()
        if now < approval.issued_at or now >= approval.expires_at:
            raise Denied("APPROVAL_EXPIRED_OR_NOT_YET_VALID")
        if self._halt_epoch(command.account_ref) != command.halt_epoch:
            raise Denied("HALT_EPOCH_MISMATCH")
