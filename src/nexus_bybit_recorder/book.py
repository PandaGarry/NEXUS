from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal, DecimalException, InvalidOperation
from typing import Any, Iterable


class ResyncRequired(RuntimeError):
    """The local book cannot be trusted until a new REST snapshot is bridged."""


class SnapshotNotCaughtUp(RuntimeError):
    """The REST snapshot is not aligned with the buffered WebSocket stream yet."""


MAX_DECIMAL_INPUT_LENGTH = 64
MAX_DECIMAL_DIGITS = 32
MAX_DECIMAL_EXPONENT = 32


def _validated_level(price: str, quantity: str) -> tuple[Decimal, Decimal]:
    if (
        not isinstance(price, str)
        or not isinstance(quantity, str)
        or len(price) > MAX_DECIMAL_INPUT_LENGTH
        or len(quantity) > MAX_DECIMAL_INPUT_LENGTH
    ):
        raise ValueError("invalid order-book decimal length")
    try:
        p, q = Decimal(price), Decimal(quantity)
    except (DecimalException, TypeError, ValueError) as exc:
        raise ValueError("invalid order-book decimal") from exc
    if not p.is_finite() or not q.is_finite() or p <= 0 or q < 0:
        raise ValueError("invalid order-book decimal")
    for value in (p, q):
        parts = value.as_tuple()
        if (
            len(parts.digits) > MAX_DECIMAL_DIGITS
            or not isinstance(parts.exponent, int)
            or abs(parts.exponent) > MAX_DECIMAL_EXPONENT
        ):
            raise ValueError("order-book decimal exceeds precision or exponent limits")
    return p, q


def _price_key(price: str) -> str:
    value, _ = _validated_level(price, "0")
    # Avoid Decimal.normalize(): it is context-sensitive and can overflow.
    # The validated exponent bound also keeps fixed-point expansion bounded.
    canonical = format(value, "f")
    if "." in canonical:
        canonical = canonical.rstrip("0").rstrip(".")
    return canonical


def _levels(raw: Iterable[Iterable[str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    seen_prices: set[str] = set()
    for row in raw:
        if not isinstance(row, (list, tuple)) or len(row) != 2:
            raise ValueError("order-book level must contain price and quantity")
        if not isinstance(row[0], str) or not isinstance(row[1], str):
            raise ValueError("order-book price and quantity must be strings")
        price, quantity = row
        _, q = _validated_level(price, quantity)
        key = _price_key(price)
        if key in seen_prices:
            raise ValueError(f"duplicate numeric price level: {key}")
        seen_prices.add(key)
        if q != 0:
            result[key] = quantity
    return result


@dataclass(frozen=True)
class Delta:
    update_id: int
    cross_seq: int
    bids: tuple[tuple[str, str], ...]
    asks: tuple[tuple[str, str], ...]
    raw: dict[str, Any] = field(compare=False, repr=False)

    @property
    def digest(self) -> str:
        canonical = json.dumps(
            {
                "raw": self.raw,
                "u": self.update_id,
                "seq": self.cross_seq,
                "b": self.bids,
                "a": self.asks,
            },
            sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

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
            if name not in data:
                raise ValueError(f"delta is missing required {name} side")
            raw_levels = data[name]
            if not isinstance(raw_levels, list):
                raise ValueError(f"delta {name} must be an array")
            parsed: list[tuple[str, str]] = []
            seen_prices: set[str] = set()
            for row in raw_levels:
                if not isinstance(row, (list, tuple)) or len(row) != 2:
                    raise ValueError("order-book level must contain price and quantity")
                price, quantity = row
                if not isinstance(price, str) or not isinstance(quantity, str):
                    raise ValueError("order-book price and quantity must be strings")
                _validated_level(price, quantity)
                key = _price_key(price)
                if key in seen_prices:
                    raise ValueError(f"duplicate numeric price level in delta: {key}")
                seen_prices.add(key)
                parsed.append((key, quantity))
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
    last_delta_digest: str | None = None

    @classmethod
    def from_snapshot(cls, snapshot: dict[str, Any]) -> "OrderBook":
        if not isinstance(snapshot, dict):
            raise ValueError("snapshot must be an object")
        for side in ("b", "a"):
            if side not in snapshot:
                raise ValueError(f"snapshot is missing required {side} side")
            if not isinstance(snapshot[side], list):
                raise ValueError(f"snapshot {side} side must be an array")
        return cls(
            update_id=int(snapshot["u"]),
            cross_seq=int(snapshot["seq"]),
            bids=_levels(snapshot["b"]),
            asks=_levels(snapshot["a"]),
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
            if self.last_delta_digest is None or delta.digest == self.last_delta_digest:
                return
            self.invalidate()
            raise ResyncRequired(
                f"conflicting duplicate update id {delta.update_id}"
            )
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
        self.last_delta_digest = delta.digest
        if self.bids and self.asks:
            if max(Decimal(p) for p in self.bids) >= min(Decimal(p) for p in self.asks):
                self.invalidate()
                raise ResyncRequired("crossed or locked book after delta")

    @staticmethod
    def _apply_side(side: dict[str, str], changes: Iterable[tuple[str, str]]) -> None:
        for price, quantity in changes:
            _, q = _validated_level(price, quantity)
            key = _price_key(price)
            if q == 0:
                side.pop(key, None)
            else:
                side[key] = quantity

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
    seq_regressions: list[Delta] = []
    for delta in buffered:
        if filtered and delta.cross_seq < filtered[-1].cross_seq:
            seq_regressions.append(delta)
            continue
        if filtered:
            previous = filtered[-1]
            if delta.update_id <= previous.update_id:
                if delta.update_id == previous.update_id:
                    if delta.digest != previous.digest:
                        raise ResyncRequired(
                            f"conflicting duplicate update id {delta.update_id} in buffer"
                        )
                    continue
                continue
            if delta.update_id != previous.update_id + 1:
                raise ResyncRequired("buffer discontinuity; restart buffering")
        filtered.append(delta)
    if not filtered:
        raise SnapshotNotCaughtUp("buffer contains no usable deltas")

    snap_seq, snap_u = int(snapshot["seq"]), int(snapshot["u"])
    # A decreasing-seq event newer than the snapshot's update ID cannot be
    # silently dropped: the snapshot does not prove that its state is included.
    if any(delta.update_id > snap_u for delta in seq_regressions):
        raise ResyncRequired("post-snapshot buffered delta has decreasing cross sequence")
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
    # The exact bridge delta is already represented by the REST snapshot.
    # Remember its canonical payload so a conflicting replay of the same u
    # cannot be silently accepted after the transition to LIVE_VALID.
    book.last_delta_digest = filtered[match_index].digest
    for delta in filtered[match_index + 1 :]:
        if delta.cross_seq == snap_seq and delta.update_id != snap_u:
            raise SnapshotNotCaughtUp("same snapshot seq but a different update id after the match")
        book.apply(delta)
    return book, match_index + 1
