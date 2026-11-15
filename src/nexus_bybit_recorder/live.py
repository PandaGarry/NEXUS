from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import random
import threading
import time
from collections import deque
from pathlib import Path

from .journal import RawFrameJournal
from .jsonutil import strict_json_loads
from .snapshot import SnapshotFetchError, fetch_full_depth_snapshot, parse_full_depth_snapshot
from .synchronizer import BookSynchronizer

LOG = logging.getLogger("nexus_bybit_recorder")
_SNAPSHOT_FETCH_SLOT = threading.BoundedSemaphore(1)
BACKOFF_RESET_AFTER_SECONDS = 30.0
MAX_RECONNECT_BACKOFF_SECONDS = 30.0
MAX_RECONNECT_JITTER_SECONDS = 0.25
RECONNECT_RATE_WINDOW_SECONDS = 60.0
MAX_RECONNECT_ATTEMPTS_PER_WINDOW = 8


class ReconnectRateLimiter:
    """Bound reconnect attempts in a rolling monotonic-time window."""

    def __init__(
        self,
        *,
        max_attempts: int = MAX_RECONNECT_ATTEMPTS_PER_WINDOW,
        window_seconds: float = RECONNECT_RATE_WINDOW_SECONDS,
    ) -> None:
        if max_attempts < 1 or window_seconds <= 0:
            raise ValueError("reconnect rate limit must be positive")
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts = deque()

    def _prune(self, now: float) -> None:
        while self._attempts and now - self._attempts[0] >= self.window_seconds:
            self._attempts.popleft()

    def delay(self, now: float | None = None) -> float:
        current = time.monotonic() if now is None else now
        self._prune(current)
        if len(self._attempts) < self.max_attempts:
            return 0.0
        return max(0.0, self._attempts[0] + self.window_seconds - current)

    def record(self, now: float | None = None) -> None:
        current = time.monotonic() if now is None else now
        self._prune(current)
        self._attempts.append(current)


def _reconnect_sleep_seconds(backoff: float, jitter_fraction: float) -> float:
    """Return capped exponential backoff plus bounded positive jitter."""
    base = min(max(backoff, 1.0), MAX_RECONNECT_BACKOFF_SECONDS)
    fraction = min(max(jitter_fraction, 0.0), 1.0)
    jitter_cap = min(MAX_RECONNECT_JITTER_SECONDS, base / 4.0)
    return min(MAX_RECONNECT_BACKOFF_SECONDS, base + jitter_cap * fraction)


def _backoff_after_connection(current: float, connected_seconds: float) -> float:
    """Reset reconnect backoff only after a connection has remained stable."""
    return 1.0 if connected_seconds >= BACKOFF_RESET_AFTER_SECONDS else current


def _fetch_snapshot_singleflight(symbol: str, testnet: bool):
    # asyncio cancellation cannot stop a running to_thread HTTP call. Hold a
    # process-wide slot until the actual blocking request returns; overlapping
    # generations fail fast instead of accumulating orphaned HTTP workers.
    if not _SNAPSHOT_FETCH_SLOT.acquire(blocking=False):
        raise SnapshotFetchError("a prior REST snapshot request is still in flight")
    try:
        return fetch_full_depth_snapshot(
            symbol, category="linear", testnet=testnet
        )
    finally:
        _SNAPSHOT_FETCH_SLOT.release()


def public_linear_url(testnet: bool = False) -> str:
    host = "stream-testnet.bybit.com" if testnet else "stream.bybit.com"
    return f"wss://{host}/v5/public/linear"


def subscription(symbol: str) -> str:
    symbol = symbol.upper()
    if not symbol.isascii() or not symbol.isalnum():
        raise ValueError("symbol must contain ASCII letters and digits only")
    return json.dumps({
        "op": "subscribe",
        "args": [f"publicTrade.{symbol}", f"orderbook.full.{symbol}"],
    }, separators=(",", ":"))


async def _heartbeat(ws, stop: asyncio.Event) -> None:
    while not stop.is_set():
        try:
            await asyncio.wait_for(stop.wait(), timeout=20)
        except TimeoutError:
            await ws.send('{"op":"ping"}')


async def _frames_until_deadline(ws, deadline: float | None):
    """Yield frames until close or the recorder's monotonic deadline."""
    iterator = ws.__aiter__()
    while True:
        try:
            if deadline is None:
                frame = await anext(iterator)
            else:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return
                frame = await asyncio.wait_for(anext(iterator), timeout=remaining)
        except StopAsyncIteration:
            return
        except TimeoutError:
            return
        yield frame


def _snapshot_fetch_task(symbol: str, testnet: bool, delay_seconds: float = 0.0):
    async def run():
        if delay_seconds:
            await asyncio.sleep(delay_seconds)
        return await asyncio.to_thread(
            _fetch_snapshot_singleflight, symbol, testnet
        )
    return asyncio.create_task(run())


def _journal_book_state(journal, generation: int, state: str, *, reason=None, sync=None, applied=0):
    fingerprint = None
    if sync is not None and sync.valid and sync.book is not None:
        fingerprint = hashlib.sha256(
            json.dumps(sync.book.fingerprint_view(), separators=(",", ":")).encode("utf-8")
        ).hexdigest()
    payload = {
        "symbol": sync.symbol if sync is not None else None,
        "state": state,
        "reason": reason,
        "valid": bool(sync.valid) if sync is not None else False,
        "no_book": bool(sync.no_book) if sync is not None else False,
        "buffered_deltas": sync.buffered_count if sync is not None else 0,
        "update_id": sync.book.update_id if sync is not None and sync.valid else None,
        "cross_seq": sync.book.cross_seq if sync is not None and sync.valid else None,
        "fingerprint_sha256": fingerprint,
        "applied_buffered_deltas": applied,
    }
    journal.append(json.dumps(payload, separators=(",", ":")), generation, record_type="derived_book_state")


async def record_public(
    *, symbol: str, output: Path, testnet: bool = False,
    duration_seconds: float | None = None, max_buffered_deltas: int = 50_000,
) -> None:
    """Record public frames and maintain a fail-closed synchronized full-depth book."""
    try:
        from websockets.asyncio.client import connect
    except ImportError as exc:
        raise RuntimeError("install the live extra: pip install -e '.[live]'") from exc

    normalized_symbol = symbol.upper()
    deadline = None if duration_seconds is None else time.monotonic() + duration_seconds
    generation = 0
    backoff = 1.0
    reconnect_limiter = ReconnectRateLimiter()
    with RawFrameJournal(output, flush_each_frame=True) as journal:
        while deadline is None or time.monotonic() < deadline:
            rate_limit_delay = reconnect_limiter.delay()
            if rate_limit_delay > 0:
                LOG.warning(
                    "reconnect attempt budget exhausted; waiting %.3fs",
                    rate_limit_delay,
                )
                await asyncio.sleep(rate_limit_delay)
            if deadline is not None and time.monotonic() >= deadline:
                break
            reconnect_limiter.record()
            generation += 1
            stop = asyncio.Event()
            heartbeat_task = None
            snapshot_task = None
            snapshot_retry_delay = 0.0
            last_snapshot_request_at = 0.0
            connected_at = None
            synchronizer = BookSynchronizer(normalized_symbol, max_buffered_deltas=max_buffered_deltas)

            def schedule_snapshot_fetch(requested_delay: float = 0.0):
                nonlocal last_snapshot_request_at
                now = time.monotonic()
                rate_limit_delay = max(0.0, 0.5 - (now - last_snapshot_request_at))
                last_snapshot_request_at = now
                return _snapshot_fetch_task(
                    normalized_symbol, testnet,
                    delay_seconds=max(requested_delay, rate_limit_delay),
                )
            try:
                LOG.info("connecting generation=%d endpoint=%s", generation, public_linear_url(testnet))
                async with connect(
                    public_linear_url(testnet),
                    ping_interval=None,
                    open_timeout=10,
                    close_timeout=5,
                    max_size=16 * 1024 * 1024,
                    max_queue=64,
                ) as ws:
                    connected_at = time.monotonic()
                    await ws.send(subscription(normalized_symbol))
                    heartbeat_task = asyncio.create_task(_heartbeat(ws, stop))
                    async for raw_frame in _frames_until_deadline(ws, deadline):
                        raw_text = raw_frame if isinstance(raw_frame, str) else "hex:" + raw_frame.hex()
                        journal.append(
                            raw_text, generation,
                            metadata={"expected_symbol": normalized_symbol},
                        )

                        try:
                            payload = strict_json_loads(raw_text)
                        except (json.JSONDecodeError, TypeError, ValueError):
                            payload = None

                        # An unparseable frame or non-object JSON may conceal a lost
                        # order-book update. Do not leave a previously valid book
                        # readable while continuing on an uncertain stream.
                        if payload is None or not isinstance(payload, dict):
                            synchronizer.invalidate("malformed_ws_frame")
                            _journal_book_state(
                                journal, generation, "INVALID",
                                reason="malformed_ws_frame", sync=synchronizer,
                            )
                            break

                        topic = payload.get("topic")
                        is_orderbook_frame = (
                            isinstance(topic, str) and topic.startswith("orderbook.full.")
                        ) or (
                            payload.get("type") == "delta"
                            and isinstance(payload.get("data"), dict)
                            and ("u" in payload["data"] or "seq" in payload["data"])
                        )
                        if is_orderbook_frame:
                            outcome = synchronizer.on_delta(payload)
                            if outcome.reason:
                                LOG.warning("book state generation=%d state=%s reason=%s", generation, outcome.state, outcome.reason)
                            # Record every order-book transition, including each
                            # post-snapshot LIVE_VALID watermark and fingerprint.
                            _journal_book_state(
                                journal, generation, outcome.state,
                                reason=outcome.reason, sync=synchronizer,
                            )
                            if outcome.state == "INVALID":
                                # A wrong symbol/topic or malformed delta cannot
                                # be repaired by a REST snapshot on this stream.
                                # End the generation and reconnect fail-closed.
                                break
                            if outcome.request_snapshot:
                                force_refresh = bool(outcome.reason) and any(
                                    marker in outcome.reason for marker in (
                                        "u=1_reinitialization", "live_delta_requires_resync",
                                        "buffer_update_id_gap", "snapshot_buffer_overflow",
                                    )
                                )
                                if snapshot_task is None or force_refresh:
                                    if snapshot_task is not None:
                                        snapshot_task.cancel()
                                        try:
                                            await snapshot_task
                                        except (asyncio.CancelledError, Exception):
                                            pass
                                    snapshot_task = schedule_snapshot_fetch(snapshot_retry_delay)

                        if snapshot_task is not None and snapshot_task.done():
                            completed_task = snapshot_task
                            snapshot_task = None
                            try:
                                response = completed_task.result()
                            except asyncio.CancelledError:
                                response = None
                            except Exception as exc:
                                LOG.warning("REST snapshot fetch failed generation=%d: %s", generation, exc)
                                journal.append(
                                    json.dumps({"error": str(exc)}, separators=(",", ":")),
                                    generation, record_type="rest_snapshot_error",
                                )
                                synchronizer.invalidate("rest_snapshot_fetch_failed")
                                _journal_book_state(
                                    journal, generation, "INVALID",
                                    reason="rest_snapshot_fetch_failed", sync=synchronizer,
                                )
                                snapshot_retry_delay = min(max(snapshot_retry_delay * 2, 0.5), 5.0)
                                response = None
                            if response is not None:
                                journal.append(
                                    response.body, generation, record_type="raw_rest_snapshot",
                                    metadata={
                                        "request_url": response.request_url,
                                        "http_status": response.http_status,
                                        "expected_symbol": normalized_symbol,
                                    },
                                    received_wall_ns=response.received_wall_ns,
                                    received_monotonic_ns=response.received_monotonic_ns,
                                )
                                try:
                                    snapshot = parse_full_depth_snapshot(response, expected_symbol=normalized_symbol)
                                except Exception as exc:
                                    LOG.warning("REST snapshot validation failed generation=%d: %s", generation, exc)
                                    journal.append(
                                        json.dumps({"error": str(exc)}, separators=(",", ":")),
                                        generation, record_type="snapshot_validation_error",
                                    )
                                    synchronizer.invalidate("rest_snapshot_validation_failed")
                                    _journal_book_state(
                                        journal, generation, "INVALID",
                                        reason="rest_snapshot_validation_failed", sync=synchronizer,
                                    )
                                    snapshot_retry_delay = min(snapshot_retry_delay * 2, 5.0)
                                else:
                                    snapshot_retry_delay = 0.5
                                    sync_outcome = synchronizer.on_snapshot(snapshot)
                                    _journal_book_state(
                                        journal, generation, sync_outcome.state,
                                        reason=sync_outcome.reason, sync=synchronizer,
                                        applied=sync_outcome.applied_buffered_deltas,
                                    )
                                    if sync_outcome.state == "LIVE_VALID":
                                        LOG.info(
                                            "book LIVE_VALID generation=%d u=%d seq=%d applied_buffered=%d",
                                            generation, synchronizer.book.update_id,
                                            synchronizer.book.cross_seq, sync_outcome.applied_buffered_deltas,
                                        )
                                    if sync_outcome.request_snapshot:
                                        snapshot_task = schedule_snapshot_fetch(snapshot_retry_delay)

                        if deadline is not None and time.monotonic() >= deadline:
                            break
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                LOG.warning("connection generation=%d ended: %s", generation, exc)
            finally:
                stop.set()
                synchronizer.on_disconnect()
                _journal_book_state(
                    journal, generation, "INVALID",
                    reason="websocket_disconnect_or_generation_end", sync=synchronizer,
                )
                if heartbeat_task is not None:
                    heartbeat_task.cancel()
                    try:
                        await heartbeat_task
                    except asyncio.CancelledError:
                        pass
                if snapshot_task is not None:
                    snapshot_task.cancel()
                    try:
                        await snapshot_task
                    except (asyncio.CancelledError, Exception):
                        pass
                if connected_at is not None:
                    backoff = _backoff_after_connection(
                        backoff, time.monotonic() - connected_at
                    )
            if deadline is not None and time.monotonic() >= deadline:
                break
            reconnect_delay = _reconnect_sleep_seconds(backoff, random.random())
            if deadline is not None:
                remaining = max(0.0, deadline - time.monotonic())
                reconnect_delay = min(reconnect_delay, remaining)
            if reconnect_delay > 0:
                await asyncio.sleep(reconnect_delay)
            backoff = min(backoff * 2, MAX_RECONNECT_BACKOFF_SECONDS)


def main() -> None:
    parser = argparse.ArgumentParser(description="Record public Bybit V5 trades and synchronized full-depth book")
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--output", type=Path, default=Path("data/bybit-public-raw.jsonl"))
    parser.add_argument("--testnet", action="store_true")
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument("--max-buffered-deltas", type=int, default=50_000)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    if args.duration is not None and args.duration <= 0:
        parser.error("--duration must be positive")
    if args.max_buffered_deltas < 2:
        parser.error("--max-buffered-deltas must be at least 2")
    asyncio.run(record_public(
        symbol=args.symbol, output=args.output, testnet=args.testnet,
        duration_seconds=args.duration, max_buffered_deltas=args.max_buffered_deltas,
    ))


if __name__ == "__main__":
    main()
