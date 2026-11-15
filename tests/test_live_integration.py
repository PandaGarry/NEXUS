import asyncio
import json
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from nexus_bybit_recorder.live import record_public
from nexus_bybit_recorder.replay import replay_book, summarize
from nexus_bybit_recorder.snapshot import SnapshotHttpResponse


class FakeWebSocket:
    def __init__(self, frames):
        self.frames = list(frames)
        self.sent = []
        self.index = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def send(self, message):
        self.sent.append(message)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.frames):
            raise StopAsyncIteration
        await asyncio.sleep(0.05)
        frame = self.frames[self.index]
        self.index += 1
        return frame


class LiveIntegrationTests(unittest.TestCase):
    def test_live_loop_journals_snapshot_and_replay_matches_valid_book(self):
        frames = [
            json.dumps({"topic": "orderbook.full.BTCUSDT", "type": "delta", "data": {"s": "BTCUSDT", "u": 10, "seq": 100, "b": [], "a": []}}),
            json.dumps({"topic": "orderbook.full.BTCUSDT", "type": "delta", "data": {"s": "BTCUSDT", "u": 11, "seq": 102, "b": [["100", "4"]], "a": []}}),
            json.dumps({"topic": "orderbook.full.BTCUSDT", "type": "delta", "data": {"s": "BTCUSDT", "u": 12, "seq": 103, "b": [["100", "5"]], "a": []}}),
        ]
        ws = FakeWebSocket(frames)
        client_module = types.ModuleType("websockets.asyncio.client")
        client_module.connect = lambda *args, **kwargs: ws
        asyncio_module = types.ModuleType("websockets.asyncio")
        asyncio_module.__path__ = []
        websockets_module = types.ModuleType("websockets")
        websockets_module.__path__ = []
        fake_modules = {
            "websockets": websockets_module,
            "websockets.asyncio": asyncio_module,
            "websockets.asyncio.client": client_module,
        }
        snapshot_body = json.dumps({"retCode": 0, "result": {
            "s": "BTCUSDT", "u": 10, "seq": 100,
            "b": [["100", "2"], ["99", "3"]],
            "a": [["101", "4"], ["102", "5"]],
        }})
        response = SnapshotHttpResponse(
            request_url="https://api.bybit.com/v5/market/full_orderbook?category=linear&symbol=BTCUSDT",
            http_status=200,
            body=snapshot_body,
            received_wall_ns=1_700_000_000_000_000_000,
            received_monotonic_ns=123_456_789,
        )
        with tempfile.TemporaryDirectory() as tmp:
            journal_path = Path(tmp) / "live.jsonl"
            with patch.dict(sys.modules, fake_modules):
                with patch("nexus_bybit_recorder.live.fetch_full_depth_snapshot", return_value=response):
                    asyncio.run(record_public(symbol="BTCUSDT", output=journal_path, duration_seconds=0.25))
            self.assertTrue(any('"op":"subscribe"' in message for message in ws.sent))
            summary = summarize(journal_path)
            self.assertEqual(summary["snapshot_responses"], 1)
            self.assertGreaterEqual(summary["valid_book_events"], 1)
            self.assertTrue(summary["classification_reconciles"])
            replay = replay_book(journal_path)
            self.assertGreaterEqual(replay["valid_book_markers_matched"], 1)
            self.assertEqual(replay["marker_mismatches"], [])
            self.assertFalse(replay["final_books"]["1:BTCUSDT"]["valid"])


    def test_short_lived_handshakes_keep_growing_backoff_and_rate_limit_pauses(self):
        class EmptyWebSocket(FakeWebSocket):
            def __init__(self):
                super().__init__([])

        connections = []
        sleeps = []
        backoffs = []
        real_sleep = asyncio.sleep

        def connect(*args, **kwargs):
            ws = EmptyWebSocket()
            connections.append(ws)
            return ws

        def short_delay(backoff, jitter):
            backoffs.append(backoff)
            return 0.001

        async def recording_sleep(seconds):
            sleeps.append(seconds)
            await real_sleep(seconds)

        client_module = types.ModuleType("websockets.asyncio.client")
        client_module.connect = connect
        asyncio_module = types.ModuleType("websockets.asyncio")
        asyncio_module.__path__ = []
        websockets_module = types.ModuleType("websockets")
        websockets_module.__path__ = []
        fake_modules = {
            "websockets": websockets_module,
            "websockets.asyncio": asyncio_module,
            "websockets.asyncio.client": client_module,
        }

        from nexus_bybit_recorder.live import ReconnectRateLimiter
        with tempfile.TemporaryDirectory() as tmp:
            journal_path = Path(tmp) / "reconnect.jsonl"
            with patch.dict(sys.modules, fake_modules):
                with patch(
                    "nexus_bybit_recorder.live.ReconnectRateLimiter",
                    side_effect=lambda: ReconnectRateLimiter(
                        max_attempts=2, window_seconds=0.04
                    ),
                ):
                    with patch(
                        "nexus_bybit_recorder.live._reconnect_sleep_seconds",
                        side_effect=short_delay,
                    ):
                        with patch(
                            "nexus_bybit_recorder.live.asyncio.sleep",
                            side_effect=recording_sleep,
                        ):
                            asyncio.run(record_public(
                                symbol="BTCUSDT",
                                output=journal_path,
                                duration_seconds=0.14,
                            ))

        self.assertGreaterEqual(len(connections), 3)
        self.assertEqual(backoffs[:3], [1.0, 2.0, 4.0])
        self.assertTrue(any(seconds >= 0.025 for seconds in sleeps))


    def test_duration_bounds_rate_limit_wait_and_connection_handshake(self):
        connections = []
        open_timeouts = []

        def connect(*args, **kwargs):
            open_timeouts.append(kwargs["open_timeout"])
            ws = FakeWebSocket([])
            connections.append(ws)
            return ws

        client_module = types.ModuleType("websockets.asyncio.client")
        client_module.connect = connect
        asyncio_module = types.ModuleType("websockets.asyncio")
        asyncio_module.__path__ = []
        websockets_module = types.ModuleType("websockets")
        websockets_module.__path__ = []
        fake_modules = {
            "websockets": websockets_module,
            "websockets.asyncio": asyncio_module,
            "websockets.asyncio.client": client_module,
        }

        from nexus_bybit_recorder.live import ReconnectRateLimiter
        with tempfile.TemporaryDirectory() as tmp:
            journal_path = Path(tmp) / "duration-rate-limit.jsonl"
            started = time.monotonic()
            with patch.dict(sys.modules, fake_modules):
                with patch(
                    "nexus_bybit_recorder.live.ReconnectRateLimiter",
                    side_effect=lambda: ReconnectRateLimiter(
                        max_attempts=1, window_seconds=1.0
                    ),
                ):
                    with patch(
                        "nexus_bybit_recorder.live._reconnect_sleep_seconds",
                        return_value=0.001,
                    ):
                        asyncio.run(record_public(
                            symbol="BTCUSDT",
                            output=journal_path,
                            duration_seconds=0.05,
                        ))
            elapsed = __import__("time").monotonic() - started

        self.assertEqual(len(connections), 1)
        self.assertEqual(len(open_timeouts), 1)
        self.assertLessEqual(open_timeouts[0], 0.05)
        self.assertLess(elapsed, 0.2)

    def test_malformed_json_frame_is_journaled_and_forces_invalidation(self):
        ws = FakeWebSocket(["not-json"])
        client_module = types.ModuleType("websockets.asyncio.client")
        client_module.connect = lambda *args, **kwargs: ws
        asyncio_module = types.ModuleType("websockets.asyncio")
        asyncio_module.__path__ = []
        websockets_module = types.ModuleType("websockets")
        websockets_module.__path__ = []
        fake_modules = {
            "websockets": websockets_module,
            "websockets.asyncio": asyncio_module,
            "websockets.asyncio.client": client_module,
        }
        with tempfile.TemporaryDirectory() as tmp:
            journal_path = Path(tmp) / "malformed.jsonl"
            with patch.dict(sys.modules, fake_modules):
                asyncio.run(record_public(symbol="BTCUSDT", output=journal_path, duration_seconds=0.25))
            records = [json.loads(line) for line in journal_path.read_text().splitlines()]
            states = [
                json.loads(record["raw_frame"])
                for record in records
                if record.get("record_type") == "derived_book_state"
            ]
            self.assertTrue(any(
                state.get("reason") == "malformed_ws_frame" and state.get("state") == "INVALID"
                for state in states
            ))

    def test_wrong_orderbook_symbol_is_not_silently_ignored(self):
        wrong = json.dumps({
            "topic": "orderbook.full.ETHUSDT",
            "type": "delta",
            "data": {"s": "ETHUSDT", "u": 10, "seq": 100, "b": [], "a": []},
        })
        ws = FakeWebSocket([wrong])
        client_module = types.ModuleType("websockets.asyncio.client")
        client_module.connect = lambda *args, **kwargs: ws
        asyncio_module = types.ModuleType("websockets.asyncio")
        asyncio_module.__path__ = []
        websockets_module = types.ModuleType("websockets")
        websockets_module.__path__ = []
        fake_modules = {
            "websockets": websockets_module,
            "websockets.asyncio": asyncio_module,
            "websockets.asyncio.client": client_module,
        }
        with tempfile.TemporaryDirectory() as tmp:
            journal_path = Path(tmp) / "wrong-topic.jsonl"
            with patch.dict(sys.modules, fake_modules):
                asyncio.run(record_public(symbol="BTCUSDT", output=journal_path, duration_seconds=0.25))
            records = [json.loads(line) for line in journal_path.read_text().splitlines()]
            states = [
                json.loads(record["raw_frame"])
                for record in records
                if record.get("record_type") == "derived_book_state"
            ]
            self.assertTrue(any(
                state.get("reason") == "unexpected_topic" and state.get("state") == "INVALID"
                for state in states
            ))


if __name__ == "__main__":
    unittest.main()
