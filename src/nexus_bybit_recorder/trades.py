from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class Trade:
    trade_id: str
    symbol: str
    side: str
    price: str
    size: str
    exchange_trade_time_ms: int
    message_time_ms: int
    cross_seq: int
    is_block_trade: bool | None
    is_rpi: bool | None

    @classmethod
    def from_item(cls, item: dict[str, Any], message_ts: int) -> "Trade":
        price, size = str(item["p"]), str(item["v"])
        if not Decimal(price).is_finite() or not Decimal(size).is_finite():
            raise ValueError("non-finite trade decimal")
        if Decimal(price) <= 0 or Decimal(size) <= 0:
            raise ValueError("trade price and size must be positive")
        if item["S"] not in ("Buy", "Sell"):
            raise ValueError("unknown taker side")
        return cls(
            trade_id=str(item["i"]), symbol=str(item["s"]), side=str(item["S"]),
            price=price, size=size, exchange_trade_time_ms=int(item["T"]),
            message_time_ms=int(message_ts), cross_seq=int(item["seq"]),
            is_block_trade=item.get("BT"), is_rpi=item.get("RPI"),
        )


class TradeDeduplicator:
    def __init__(self) -> None:
        self._seen: set[str] = set()

    def accept_message(self, message: dict[str, Any]) -> list[Trade]:
        accepted = []
        message_ts = int(message["ts"])
        for item in message.get("data", []):
            trade = Trade.from_item(item, message_ts)
            if trade.trade_id in self._seen:
                continue
            self._seen.add(trade.trade_id)
            accepted.append(trade)
        return accepted
