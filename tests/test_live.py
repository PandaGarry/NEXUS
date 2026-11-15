import json
import unittest
from unittest.mock import patch

from nexus_bybit_recorder.live import (
    _SNAPSHOT_FETCH_SLOT,
    _backoff_after_connection,
    _fetch_snapshot_singleflight,
    _reconnect_sleep_seconds,
    ReconnectRateLimiter,
    public_linear_url,
    subscription,
)
from nexus_bybit_recorder.snapshot import SnapshotFetchError


class LiveConfigTests(unittest.TestCase):
    def test_short_lived_successful_socket_open_does_not_reset_backoff(self):
        self.assertEqual(_backoff_after_connection(8.0, 0.2), 8.0)
        self.assertEqual(_backoff_after_connection(8.0, 29.999), 8.0)

    def test_stable_connection_resets_backoff(self):
        self.assertEqual(_backoff_after_connection(8.0, 30.0), 1.0)
        self.assertEqual(_backoff_after_connection(30.0, 120.0), 1.0)


    def test_reconnect_rate_limiter_bounds_attempts_in_rolling_window(self):
        limiter = ReconnectRateLimiter(max_attempts=3, window_seconds=10.0)
        limiter.record(now=0.0)
        limiter.record(now=1.0)
        limiter.record(now=2.0)
        self.assertEqual(limiter.delay(now=5.0), 5.0)
        self.assertAlmostEqual(limiter.delay(now=9.999), 0.001)
        self.assertEqual(limiter.delay(now=10.0), 0.0)

    def test_reconnect_rate_limiter_rejects_invalid_configuration(self):
        with self.assertRaises(ValueError):
            ReconnectRateLimiter(max_attempts=0)
        with self.assertRaises(ValueError):
            ReconnectRateLimiter(window_seconds=0)

    def test_reconnect_backoff_caps_base_and_bounds_jitter(self):
        self.assertEqual(_reconnect_sleep_seconds(1.0, 0.0), 1.0)
        self.assertEqual(_reconnect_sleep_seconds(1.0, 1.0), 1.25)
        self.assertEqual(_reconnect_sleep_seconds(100.0, 0.0), 30.0)
        self.assertEqual(_reconnect_sleep_seconds(100.0, 1.0), 30.25)
        self.assertEqual(_reconnect_sleep_seconds(4.0, 2.0), 4.25)
        self.assertEqual(_reconnect_sleep_seconds(4.0, -1.0), 4.0)

    def test_endpoints(self):
        self.assertEqual(public_linear_url(), "wss://stream.bybit.com/v5/public/linear")
        self.assertEqual(public_linear_url(True), "wss://stream-testnet.bybit.com/v5/public/linear")

    def test_subscription_contains_trade_and_full_depth_topics(self):
        payload = json.loads(subscription("btcusdt"))
        self.assertEqual(payload["args"], ["publicTrade.BTCUSDT", "orderbook.full.BTCUSDT"])

    def test_rejects_malformed_symbol(self):
        with self.assertRaises(ValueError):
            subscription("BTC/USDT")

    def test_overlapping_snapshot_fetch_fails_fast_without_spawning_http_call(self):
        with _SNAPSHOT_FETCH_SLOT:
            with patch("nexus_bybit_recorder.live.fetch_full_depth_snapshot") as fetch:
                with self.assertRaises(SnapshotFetchError):
                    _fetch_snapshot_singleflight("BTCUSDT", False)
                fetch.assert_not_called()

    def test_snapshot_fetch_slot_is_released_after_request_finishes(self):
        sentinel = object()
        with patch(
            "nexus_bybit_recorder.live.fetch_full_depth_snapshot",
            return_value=sentinel,
        ) as fetch:
            self.assertIs(_fetch_snapshot_singleflight("BTCUSDT", False), sentinel)
            fetch.assert_called_once_with("BTCUSDT", category="linear", testnet=False)
        with _SNAPSHOT_FETCH_SLOT:
            pass


if __name__ == "__main__":
    unittest.main()
