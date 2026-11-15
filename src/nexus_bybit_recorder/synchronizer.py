from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .book import Delta, OrderBook, ResyncRequired, SnapshotNotCaughtUp, bridge_snapshot


@dataclass(frozen=True)
class SyncOutcome:
    state: str
    request_snapshot: bool = False
    reason: str | None = None
    applied_buffered_deltas: int = 0


class BookSynchronizer:
    """Fail-closed Bybit full-depth snapshot/delta synchronizer for one WS generation."""

    def __init__(self, symbol: str, *, max_buffered_deltas: int = 50_000) -> None:
        if max_buffered_deltas < 2:
            raise ValueError("max_buffered_deltas must be at least 2")
        self.symbol = symbol.upper()
        self.max_buffered_deltas = max_buffered_deltas
        self.book: OrderBook | None = None
        self._buffer: list[Delta] = []
        self.last_invalidation_reason: str | None = "awaiting_initial_snapshot"

    @property
    def valid(self) -> bool:
        return self.book is not None and self.book.valid

    @property
    def buffered_count(self) -> int:
        return len(self._buffer)

    def invalidate(self, reason: str, *, retain_delta: Delta | None = None) -> None:
        if self.book is not None:
            self.book.invalidate()
        self.book = None
        self._buffer = [] if retain_delta is None else [retain_delta]
        self.last_invalidation_reason = reason

    def on_delta(self, message: dict[str, Any]) -> SyncOutcome:
        if not isinstance(message, dict):
            self.invalidate("malformed_delta:root_must_be_object")
            return SyncOutcome("INVALID", False, self.last_invalidation_reason)
        if message.get("topic") != f"orderbook.full.{self.symbol}":
            self.invalidate("unexpected_topic")
            return SyncOutcome("INVALID", False, "unexpected_topic")
        try:
            delta = Delta.from_message(message)
            data = message.get("data")
            if not isinstance(data, dict) or data.get("s") != self.symbol:
                raise ValueError("unexpected or missing symbol")
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            self.invalidate(f"malformed_delta:{exc}")
            return SyncOutcome("INVALID", False, self.last_invalidation_reason)

        if delta.update_id == 1:
            self.invalidate("u=1_reinitialization", retain_delta=delta)
            return SyncOutcome("SYNCING", True, self.last_invalidation_reason)

        if self.valid:
            try:
                assert self.book is not None
                self.book.apply(delta)
            except (ResyncRequired, ValueError) as exc:
                self.invalidate(f"live_delta_requires_resync:{exc}", retain_delta=delta)
                return SyncOutcome("SYNCING", True, self.last_invalidation_reason)
            return SyncOutcome("LIVE_VALID")

        if self._buffer and delta.cross_seq < self._buffer[-1].cross_seq:
            return SyncOutcome("SYNCING", False, "decreasing_seq_delta_discarded")

        if self._buffer and delta.update_id != self._buffer[-1].update_id + 1:
            expected = self._buffer[-1].update_id + 1
            self.invalidate(f"buffer_update_id_gap:expected_{expected}_got_{delta.update_id}", retain_delta=delta)
            return SyncOutcome("SYNCING", True, self.last_invalidation_reason)

        self._buffer.append(delta)
        if len(self._buffer) > self.max_buffered_deltas:
            self.invalidate("snapshot_buffer_overflow", retain_delta=delta)
            return SyncOutcome("SYNCING", True, self.last_invalidation_reason)
        return SyncOutcome("SYNCING", request_snapshot=len(self._buffer) == 1)

    def on_snapshot(self, snapshot: dict[str, Any]) -> SyncOutcome:
        if not self._buffer:
            self.invalidate("snapshot_arrived_without_buffer")
            return SyncOutcome("SYNCING", False, self.last_invalidation_reason)
        try:
            book, consumed = bridge_snapshot(snapshot, self._buffer)
        except SnapshotNotCaughtUp as exc:
            self.last_invalidation_reason = f"snapshot_not_caught_up:{exc}"
            return SyncOutcome("SYNCING", True, self.last_invalidation_reason)
        except (ResyncRequired, ValueError, KeyError, TypeError) as exc:
            self.invalidate(f"snapshot_bridge_failed:{exc}")
            return SyncOutcome("SYNCING", False, self.last_invalidation_reason)
        self.book = book
        self._buffer.clear()
        self.last_invalidation_reason = None
        return SyncOutcome("LIVE_VALID", False, None, consumed)

    def on_disconnect(self) -> None:
        self.invalidate("websocket_disconnect")
