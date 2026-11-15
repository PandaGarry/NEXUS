import unittest
from nexus_bybit_recorder.trades import TradeDeduplicator


class TradeTests(unittest.TestCase):
    def test_deduplicates_by_trade_id_not_seq_and_keeps_rpi(self):
        dedupe = TradeDeduplicator()
        message = {"ts": 1000, "data": [
            {"i": "t1", "s": "BTCUSDT", "S": "Buy", "p": "100.00", "v": "0.1", "T": 999, "seq": 7, "RPI": True},
            {"i": "t2", "s": "BTCUSDT", "S": "Sell", "p": "100.01", "v": "0.2", "T": 999, "seq": 7, "RPI": False},
        ]}
        accepted = dedupe.accept_message(message)
        self.assertEqual([x.trade_id for x in accepted], ["t1", "t2"])
        self.assertTrue(accepted[0].is_rpi)
        self.assertEqual(dedupe.accept_message(message), [])


if __name__ == "__main__":
    unittest.main()
