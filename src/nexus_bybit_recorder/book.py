from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable


class ResyncRequired(RuntimeError):
    """The local book cannot be trusted until a new REST snapshot is bridged."""


class SnapshotNotCaughtUp(RuntimeError):
    """The REST snapshot is not aligned with the buffered WebSocket stream yet."""


def _validated_level(price: str, quantity: str) -> tuple[Decimal, Decimal]:
    try:
        p, q = Decimal(price), Decimal(quantity)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("invalid order-book decimal") from exc
    if not p.is_finite() or not q.is_finite() or p <= 0 or q < 0:
        raise ValueError("invalid order-book decimal")
    return p, q


def _levels(raw: Iterable[Iterable[str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for row in raw:
        if not isinstance(row, (list, tuple)) or len(row) != 2:
            raise ValueError("order-book level must contain price and quantity")
        if not isinstance(row[0], str) or not isinstance(row[1], str):
            raise ValueError("order-book price and quantity must be strings")
        price, quantity = row
        _, q = _validated_level(price, quantity)
        if q != 0:
            result[price] = quantity
    return result


@dataclass(frozen=True)
class Delta:
    update_id: int
    cross_seq: int
    bids: tuple[tuple[str, str], ...]
    asks: tuple[tuple[str, str], ...]
    raw: dict[str, Any] = field(compare=False, repr=False)

    @classmethod
    def from_message(cls, message: dict[str, Any]) -> "Delta":
        if not isinstance(message, dict) or message.get("type") != "delta":
            raise ValueError("full orderbook stream must contain delta messages")
        data = message.get("data")
        if not isinstance(data, dict):
            raise ValueError("delta data must be an object")

        def sequence(name: str, minimum: int) -> int:
            value = data.get(name)
            if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
                raise ValueError(f"delta {name} must be an integer >= {minimum}")
            return value

        def side_levels(name: str) -> tuple[tuple[str, str], ...]:
            raw_levels = data.get(name, [])
            if not isinstance(raw_levels, list):
                raise ValueError(f"delta {name} must be an array")
            parsed: list[tuple[str, str]] = []
            for row in raw_levels:
                if not isinstance(row, (list, tuple)) or len(row) != 2:
                    raise ValueError("order-book level must contain price and quantity")
                price, quantity = row
                if not isinstance(price, str) or not isinstance(quantity, str):
                    raise ValueError("order-book price and quantity must be strings")
                _validated_level(price, quantity)
                parsed.append((price, quantity))
            return tuple(parsed)

        return cls(
            update_id=sequence("u", 1),
            cross_seq=sequence("seq", 0),
            bids=side_levels("b"),
            asks=side_levels("a"),
            raw=message,
        )


@dataclass
class OrderBook:
    update_id: int
    cross_seq: int
    bids: dict[str, str]
    asks: dict[str, str]
    valid: bool = True

    @classmethod
    def from_snapshot(cls, snapshot: dict[str, Any]) -> "OrderBook":
        return cls(
            update_id=int(snapshot["u"]),
            cross_seq=int(snapshot["seq"]),
            bids=_levels(snapshot.get("b", [])),
            asks=_levels(snapshot.get("a", [])),
        )

    def apply(self, delta: Delta) -> None:
        if not self.valid:
            raise ResyncRequired("book already invalid")
        if delta.update_id == 1:
            self.invalidate()
            raise ResyncRequired("u=1 reset signal")
        if delta.update_id < self.update_id:
            return
        if delta.update_id == self.update_id:
            return
        if delta.update_id != self.update_id + 1:
            self.invalidate()
            raise ResyncRequired(
                f"update-id gap: expected {self.update_id + 1}, got {delta.update_id}"
            )
        if delta.cross_seq < self.cross_seq:
            self.invalidate()
            raise ResyncRequired(
                f"cross-sequence regression: previous {self.cross_seq}, got {delta.cross_seq}"
            )
        self._apply_side(self.bids, delta.bids)
        self._apply_side(self.asks, delta.asks)
        self.update_id = delta.update_id
        self.cross_seq = delta.cross_seq
        if self.bids and self.asks:
            if max(Decimal(p) for p in self.bids) >= min(Decimal(p) for p in self.asks):
                self.invalidate()
                raise ResyncRequired("crossed or locked book after delta")

    @staticmethod
    def _apply_side(side: dict[str, str], changes: Iterable[tuple[str, str]]) -> None:
        for price, quantity in changes:
            _, q = _validated_level(price, quantity)
            if q == 0:
                side.pop(price, None)
            else:
                side[price] = quantity

    def invalidate(self) -> None:
        self.valid = False
        self.bids.clear()
        self.asks.clear()

    def fingerprint_view(self) -> tuple[int, int, tuple[tuple[str, str], ...], tuple[tuple[str, str], ...]]:
        return (
            self.update_id,
            self.cross_seq,
            tuple(sorted(self.bids.items(), key=lambda x: Decimal(x[0]), reverse=True)),
            tuple(sorted(self.asks.items(), key=lambda x: Decimal(x[0]))),
        )


def bridge_snapshot(snapshot: dict[str, Any], buffered: list[Delta]) -> tuple[OrderBook, int]:
    """Apply Bybit's full-depth snapshot/delta bridge; return book and consumed count."""
    if not buffered:
        raise SnapshotNotCaughtUp("no buffered deltas")
    # Bybit instructs clients to discard packets whose cross-sequence decreases.
    filtered: list[Delta] = []
    for delta in buffered:
        if filtered and delta.cross_seq < filtered[-1].cross_seq:
            continue
        if filtered:
            previous = filtered[-1]
            if delta.update_id <= previous.update_id:
                if delta.update_id == previous.update_id:
                    continue
                continue
            if delta.update_id != previous.update_id + 1:
                raise ResyncRequired("buffer discontinuity; restart buffering")
        filtered.append(delta)
    if not filtered:
        raise SnapshotNotCaughtUp("buffer contains no usable deltas")

    snap_seq, snap_u = int(snapshot["seq"]), int(snapshot["u"])
    if snap_seq < filtered[0].cross_seq:
        raise SnapshotNotCaughtUp("snapshot predates first buffered delta")

    match_index = None
    for index, delta in enumerate(filtered):
        if delta.cross_seq < snap_seq:
            continue
        if delta.cross_seq == snap_seq:
            if delta.update_id != snap_u:
                raise SnapshotNotCaughtUp("same seq but different update id")
            match_index = index
            break
        raise SnapshotNotCaughtUp("snapshot bridge point not present in buffer")
    if match_index is None:
        raise SnapshotNotCaughtUp("snapshot bridge point not present in buffer")

    book = OrderBook.from_snapshot(snapshot)
    for delta in filtered[match_index + 1 :]:
        book.apply(delta)
    return book, match_index + 1
