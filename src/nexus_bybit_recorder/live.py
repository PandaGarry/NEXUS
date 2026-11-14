from __future__ import annotations

import argparse
import asyncio
import json
import logging
import random
import time
from pathlib import Path

from .journal import RawFrameJournal

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


async def record_public(
    *, symbol: str, output: Path, testnet: bool = False,
    duration_seconds: float | None = None,
) -> None:
    """Record exact public WS text frames; never parse before journaling."""
    try:
        from websockets.asyncio.client import connect
    except ImportError as exc:
        raise RuntimeError("install the live extra: pip install -e '.[live]'") from exc

    deadline = None if duration_seconds is None else time.monotonic() + duration_seconds
    generation = 0
    backoff = 1.0
    with RawFrameJournal(output, flush_each_frame=True) as journal:
        while deadline is None or time.monotonic() < deadline:
            generation += 1
            stop = asyncio.Event()
            heartbeat_task = None
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
                    await ws.send(subscription(symbol))
                    heartbeat_task = asyncio.create_task(_heartbeat(ws, stop))
                    backoff = 1.0
                    async for raw_frame in ws:
                        raw_text = raw_frame if isinstance(raw_frame, str) else "hex:" + raw_frame.hex()
                        journal.append(raw_text, generation)
                        if deadline is not None and time.monotonic() >= deadline:
                            break
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                LOG.warning("connection generation=%d ended: %s", generation, exc)
            finally:
                stop.set()
                if heartbeat_task is not None:
                    heartbeat_task.cancel()
                    try:
                        await heartbeat_task
                    except asyncio.CancelledError:
                        pass
            if deadline is not None and time.monotonic() >= deadline:
                break
            await asyncio.sleep(min(backoff, 30.0) + random.uniform(0.0, min(0.25, backoff / 4)))
            backoff = min(backoff * 2, 30.0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Record public Bybit V5 trades and full-depth deltas")
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--output", type=Path, default=Path("data/bybit-public-raw.jsonl"))
    parser.add_argument("--testnet", action="store_true")
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    if args.duration is not None and args.duration <= 0:
        parser.error("--duration must be positive")
    asyncio.run(record_public(
        symbol=args.symbol, output=args.output, testnet=args.testnet,
        duration_seconds=args.duration,
    ))


if __name__ == "__main__":
    main()
