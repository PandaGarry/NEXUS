from __future__ import annotations

import argparse
import asyncio
import json
import logging
import random
import time
from pathlib import Path

from .journal import RawFrameJournal
from .snapshot import fetch_full_depth_snapshot, parse_full_depth_snapshot
from .synchronizer import BookSynchronizer

LOG = logging.getLogger("nexus_bybit_recorder")


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


def _snapshot_fetch_task(symbol: str, testnet: bool, delay_seconds: float = 0.0):
    async def run():
        if delay_seconds:
            await asyncio.sleep(delay_seconds)
        return await asyncio.to_thread(
            fetch_full_depth_snapshot, symbol, category="linear", testnet=testnet
        )
    return asyncio.create_task(run())


def _journal_book_state(journal, generation: int, state: str, *, reason=None, sync=None, applied=0):
    payload = {
        "state": state,
        "reason": reason,
        "valid": bool(sync.valid) if sync is not None else False,
        "buffered_deltas": sync.buffered_count if sync is not None else 0,
        "update_id": sync.book.update_id if sync is not None and sync.valid else None,
        "cross_seq": sync.book.cross_seq if sync is not None and sync.valid else None,
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
    with RawFrameJournal(output, flush_each_frame=True) as journal:
        while deadline is None or time.monotonic() < deadline:
            generation += 1
            stop = asyncio.Event()
            heartbeat_task = None
            snapshot_task = None
            snapshot_retry_delay = 0.0
            last_snapshot_request_at = 0.0
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
                    await ws.send(subscription(normalized_symbol))
                    heartbeat_task = asyncio.create_task(_heartbeat(ws, stop))
                    backoff = 1.0
                    async for raw_frame in ws:
                        raw_text = raw_frame if isinstance(raw_frame, str) else "hex:" + raw_frame.hex()
                        journal.append(raw_text, generation)

                        try:
                            payload = json.loads(raw_text)
                        except (json.JSONDecodeError, TypeError):
                            payload = None

                        if isinstance(payload, dict) and payload.get("topic") == f"orderbook.full.{normalized_symbol}":
                            outcome = synchronizer.on_delta(payload)
                            if outcome.reason:
                                LOG.warning("book state generation=%d state=%s reason=%s", generation, outcome.state, outcome.reason)
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
                                snapshot_retry_delay = min(max(snapshot_retry_delay * 2, 0.5), 5.0)
                                response = None
                            if response is not None:
                                journal.append(
                                    response.body, generation, record_type="raw_rest_snapshot",
                                    metadata={"request_url": response.request_url, "http_status": response.http_status},
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
            if deadline is not None and time.monotonic() >= deadline:
                break
            await asyncio.sleep(min(backoff, 30.0) + random.uniform(0.0, min(0.25, backoff / 4)))
            backoff = min(backoff * 2, 30.0)


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
