import json
import unittest
from nexus_bybit_recorder.live import public_linear_url, subscription


class LiveConfigTests(unittest.TestCase):
    def test_endpoints(self):
        self.assertEqual(public_linear_url(), "wss://stream.bybit.com/v5/public/linear")
        self.assertEqual(public_linear_url(True), "wss://stream-testnet.bybit.com/v5/public/linear")

    def test_subscription_contains_trade_and_full_depth_topics(self):
        payload = json.loads(subscription("btcusdt"))
        self.assertEqual(payload["args"], ["publicTrade.BTCUSDT", "orderbook.full.BTCUSDT"])

    def test_rejects_malformed_symbol(self):
        with self.assertRaises(ValueError):
            subscription("BTC/USDT")


if __name__ == "__main__":
    unittest.main()
