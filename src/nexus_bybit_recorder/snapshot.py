from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .book import OrderBook


class SnapshotFetchError(RuntimeError):
    """A public REST snapshot could not be fetched safely."""


class SnapshotValidationError(ValueError):
    """A REST response is not a valid full-depth snapshot for this instrument."""


@dataclass(frozen=True)
class SnapshotHttpResponse:
    request_url: str
    http_status: int
    body: str
    received_wall_ns: int
    received_monotonic_ns: int

    @property
    def received_at_utc(self) -> str:
        return datetime.fromtimestamp(
            self.received_wall_ns / 1_000_000_000, tz=timezone.utc
        ).isoformat(timespec="microseconds")


def full_depth_snapshot_url(
    symbol: str, *, category: str = "linear", testnet: bool = False
) -> str:
    normalized = symbol.upper()
    if not normalized.isascii() or not normalized.isalnum():
        raise ValueError("symbol must contain ASCII letters and digits only")
    if category not in {"spot", "linear", "inverse"}:
        raise ValueError("unsupported Bybit category")
    host = "api-testnet.bybit.com" if testnet else "api.bybit.com"
    query = urlencode({"category": category, "symbol": normalized})
    return f"https://{host}/v5/market/full_orderbook?{query}"


def fetch_full_depth_snapshot(
    symbol: str, *, category: str = "linear", testnet: bool = False,
    timeout_seconds: float = 10.0, max_response_bytes: int = 8 * 1024 * 1024,
) -> SnapshotHttpResponse:
    """Fetch the unauthenticated Bybit full-depth snapshot; never parses the body.

    The caller must journal the exact response body before calling the parser.
    HTTP error bodies are returned too, so they can be journaled and diagnosed.
    """
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if max_response_bytes <= 0:
        raise ValueError("max_response_bytes must be positive")
    url = full_depth_snapshot_url(symbol, category=category, testnet=testnet)
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "NEXUS-public-recorder/0.1"})
    status = 0
    try:
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                status = int(response.status)
                raw = response.read(max_response_bytes + 1)
        except HTTPError as error:
            status = int(error.code)
            raw = error.read(max_response_bytes + 1)
    except (URLError, TimeoutError, OSError) as exc:
        raise SnapshotFetchError(f"Bybit full-depth snapshot request failed: {exc}") from exc
    if len(raw) > max_response_bytes:
        raise SnapshotFetchError(
            f"Bybit full-depth snapshot exceeded {max_response_bytes} bytes; response rejected"
        )
    try:
        body = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SnapshotFetchError("Bybit full-depth snapshot response was not UTF-8") from exc
    return SnapshotHttpResponse(
        request_url=url,
        http_status=status,
        body=body,
        received_wall_ns=time.time_ns(),
        received_monotonic_ns=time.monotonic_ns(),
    )


def parse_full_depth_snapshot(
    response: SnapshotHttpResponse, *, expected_symbol: str
) -> dict:
    """Validate a journaled Bybit REST response and return its snapshot result."""
    if response.http_status != 200:
        raise SnapshotValidationError(f"unexpected HTTP status: {response.http_status}")
    try:
        payload = json.loads(response.body)
    except json.JSONDecodeError as exc:
        raise SnapshotValidationError("REST response is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise SnapshotValidationError("REST response root must be an object")
    if payload.get("retCode") != 0:
        raise SnapshotValidationError(f"Bybit retCode is not zero: {payload.get('retCode')!r}")
    result = payload.get("result")
    if not isinstance(result, dict):
        raise SnapshotValidationError("REST response result must be an object")
    if result.get("s") != expected_symbol.upper():
        raise SnapshotValidationError("snapshot symbol does not match requested symbol")
    for field in ("u", "seq"):
        value = result.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise SnapshotValidationError(f"snapshot {field} must be a non-negative integer")
    try:
        book = OrderBook.from_snapshot(result)
    except (KeyError, TypeError, ValueError) as exc:
        raise SnapshotValidationError(f"invalid snapshot price levels: {exc}") from exc
    if book.bids and book.asks:
        from decimal import Decimal
        if max(Decimal(price) for price in book.bids) >= min(Decimal(price) for price in book.asks):
            raise SnapshotValidationError("snapshot is crossed or locked")
    return result
