import json
import unittest
from nexus_bybit_recorder.snapshot import (
    SnapshotHttpResponse,
    SnapshotValidationError,
    full_depth_snapshot_url,
    parse_full_depth_snapshot,
)


class SnapshotClientTests(unittest.TestCase):
    def setUp(self):
        self.result = {
            "s": "BTCUSDT",
            "u": 10,
            "seq": 100,
            "b": [["100", "2"], ["99", "3"]],
            "a": [["101", "4"], ["102", "5"]],
        }
        self.response = SnapshotHttpResponse(
            request_url="https://api.bybit.com/v5/market/full_orderbook?category=linear&symbol=BTCUSDT",
            http_status=200,
            body=json.dumps({"retCode": 0, "result": self.result}),
            received_wall_ns=1,
            received_monotonic_ns=2,
        )

    def test_url_uses_full_depth_endpoint_and_expected_product(self):
        url = full_depth_snapshot_url("btcusdt")
        self.assertIn("/v5/market/full_orderbook?", url)
        self.assertIn("category=linear", url)
        self.assertIn("symbol=BTCUSDT", url)

    def test_rejects_invalid_category_and_symbol(self):
        with self.assertRaises(ValueError):
            full_depth_snapshot_url("BTC/USDT")
        with self.assertRaises(ValueError):
            full_depth_snapshot_url("BTCUSDT", category="option")

    def test_parses_valid_full_depth_snapshot(self):
        result = parse_full_depth_snapshot(self.response, expected_symbol="BTCUSDT")
        self.assertEqual(result["u"], 10)
        self.assertEqual(result["seq"], 100)

    def test_rejects_non_200_status(self):
        response = SnapshotHttpResponse(**{**self.response.__dict__, "http_status": 503})
        with self.assertRaises(SnapshotValidationError):
            parse_full_depth_snapshot(response, expected_symbol="BTCUSDT")

    def test_rejects_nonzero_retcode(self):
        response = SnapshotHttpResponse(**{**self.response.__dict__, "body": json.dumps({"retCode": 10001})})
        with self.assertRaises(SnapshotValidationError):
            parse_full_depth_snapshot(response, expected_symbol="BTCUSDT")

    def test_rejects_wrong_symbol(self):
        response = SnapshotHttpResponse(**{**self.response.__dict__, "body": json.dumps({"retCode": 0, "result": {**self.result, "s": "ETHUSDT"}})})
        with self.assertRaises(SnapshotValidationError):
            parse_full_depth_snapshot(response, expected_symbol="BTCUSDT")

    def test_rejects_crossed_snapshot(self):
        crossed = {**self.result, "a": [["100", "1"]]}
        response = SnapshotHttpResponse(**{**self.response.__dict__, "body": json.dumps({"retCode": 0, "result": crossed})})
        with self.assertRaises(SnapshotValidationError):
            parse_full_depth_snapshot(response, expected_symbol="BTCUSDT")


if __name__ == "__main__":
    unittest.main()
