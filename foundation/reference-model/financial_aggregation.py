"""Exact, venue-neutral aggregation of supplied partial fills.

Test-only reference operation. It performs dimensional weighted-average
arithmetic only; it does not define fill validity, fees, funding, P&L,
accounting, venue normalization, or rounding policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from domain_types import AssetAmount, Notional, Price
from nexus_decimal import ExactRational


@dataclass(frozen=True, slots=True)
class PartialFillAggregate:
    """Exact aggregate for one supplied set of fills."""

    total_quantity: AssetAmount
    total_quote_notional: Notional
    weighted_average_price: ExactRational


def aggregate_partial_fills(
    fills: Iterable[tuple[AssetAmount, Price]],
) -> PartialFillAggregate:
    """Aggregate (base-asset quantity, quote-per-base price) pairs exactly.

    An empty iterable is invalid. Asset and quote dimensions are enforced by
    the domain value types. The weighted average is returned as an exact
    rational, so non-terminating decimal results are preserved without
    selecting a rounding mode. Signed quantities are not prohibited here:
    this function defines arithmetic over supplied inputs, not venue fill
    admissibility.
    """
    total_quantity: AssetAmount | None = None
    total_quote: Notional | None = None

    for quantity, price in fills:
        if not isinstance(quantity, AssetAmount):
            raise TypeError("fill quantity must be AssetAmount")
        if not isinstance(price, Price):
            raise TypeError("fill price must be Price")
        quote_notional = price.notional_for(quantity)
        total_quantity = (
            quantity if total_quantity is None else total_quantity + quantity
        )
        total_quote = (
            quote_notional if total_quote is None else total_quote + quote_notional
        )

    if total_quantity is None or total_quote is None:
        raise ValueError("at least one partial fill is required")

    weighted_average = total_quote.amount.divide_exact(total_quantity.amount)
    return PartialFillAggregate(total_quantity, total_quote, weighted_average)
