import unittest
from unittest.mock import patch
from nexus_bybit_recorder.book import ResyncRequired
from nexus_bybit_recorder.synchronizer import BookSynchronizer


def delta(u, seq, bids=None, asks=None):
    return {
        "topic": "orderbook.full.BTCUSDT",
        "type": "delta",
        "data": {"s": "BTCUSDT", "u": u, "seq": seq, "b": bids or [], "a": asks or []},
    }


def snapshot(u=10, seq=100):
    return {"u": u, "seq": seq, "b": [["100", "2"], ["99", "3"]], "a": [["101", "4"], ["102", "5"]]}


class BookSynchronizerTests(unittest.TestCase):
    def test_snapshot_bridge_exposes_only_valid_book_after_exact_watermark(self):
        sync = BookSynchronizer("BTCUSDT")
        self.assertFalse(sync.valid)
        self.assertTrue(sync.on_delta(delta(10, 100)).request_snapshot)
        self.assertFalse(sync.valid)
        self.assertFalse(sync.on_delta(delta(11, 102, [["100", "7"]])).request_snapshot)
        outcome = sync.on_snapshot(snapshot())
        self.assertEqual(outcome.state, "LIVE_VALID")
        self.assertEqual(outcome.applied_buffered_deltas, 1)
        self.assertTrue(sync.valid)
        self.assertEqual(sync.book.update_id, 11)
        self.assertEqual(sync.book.bids["100"], "7")

    def test_snapshot_not_caught_up_keeps_book_unavailable(self):
        sync = BookSynchronizer("BTCUSDT")
        sync.on_delta(delta(10, 100))
        outcome = sync.on_snapshot(snapshot(u=9, seq=99))
        self.assertEqual(outcome.state, "SYNCING")
        self.assertTrue(outcome.request_snapshot)
        self.assertFalse(sync.valid)

    def test_update_id_gap_invalidates_and_restarts_from_new_delta(self):
        sync = BookSynchronizer("BTCUSDT")
        sync.on_delta(delta(10, 100))
        sync.on_snapshot(snapshot())
        outcome = sync.on_delta(delta(12, 102))
        self.assertTrue(outcome.request_snapshot)
        self.assertFalse(sync.valid)
        self.assertEqual(sync.buffered_count, 1)
        self.assertEqual(sync.on_snapshot(snapshot(u=12, seq=102)).state, "LIVE_VALID")

    def test_u_one_forces_resynchronization(self):
        sync = BookSynchronizer("BTCUSDT")
        sync.on_delta(delta(10, 100))
        sync.on_snapshot(snapshot())
        outcome = sync.on_delta(delta(1, 200))
        self.assertTrue(outcome.request_snapshot)
        self.assertFalse(sync.valid)
        self.assertEqual(sync.last_invalidation_reason, "u=1_reinitialization")
        self.assertEqual(sync.on_snapshot(snapshot(u=1, seq=200)).state, "LIVE_VALID")

    def test_decreasing_seq_delta_is_discarded_without_sorting(self):
        sync = BookSynchronizer("BTCUSDT")
        sync.on_delta(delta(10, 100))
        discarded = sync.on_delta(delta(11, 99))
        self.assertEqual(discarded.reason, "decreasing_seq_delta_discarded")
        self.assertEqual(sync.buffered_count, 1)
        sync.on_delta(delta(11, 101))
        self.assertEqual(sync.on_snapshot(snapshot()).state, "LIVE_VALID")

    def test_buffer_overflow_invalidates_and_retains_only_latest_delta(self):
        sync = BookSynchronizer("BTCUSDT", max_buffered_deltas=2)
        sync.on_delta(delta(10, 100))
        sync.on_delta(delta(11, 101))
        outcome = sync.on_delta(delta(12, 102))
        self.assertTrue(outcome.request_snapshot)
        self.assertEqual(sync.buffered_count, 1)
        self.assertFalse(sync.valid)

    def test_disconnect_invalidates_book(self):
        sync = BookSynchronizer("BTCUSDT")
        sync.on_delta(delta(10, 100))
        sync.on_snapshot(snapshot())
        sync.on_disconnect()
        self.assertFalse(sync.valid)
        self.assertEqual(sync.last_invalidation_reason, "websocket_disconnect")



    def test_non_object_message_root_invalidates_without_raising(self):
        sync = BookSynchronizer("BTCUSDT")
        outcome = sync.on_delta(["not", "an", "object"])
        self.assertEqual(outcome.state, "INVALID")
        self.assertFalse(sync.valid)
        self.assertIn("root_must_be_object", outcome.reason)

    def test_live_cross_sequence_regression_invalidates_immediately(self):
        sync = BookSynchronizer("BTCUSDT")
        sync.on_delta(delta(10, 100))
        self.assertEqual(sync.on_snapshot(snapshot()).state, "LIVE_VALID")
        outcome = sync.on_delta(delta(11, 99, [["100", "8"]]))
        self.assertEqual(outcome.state, "SYNCING")
        self.assertTrue(outcome.request_snapshot)
        self.assertFalse(sync.valid)
        self.assertEqual(sync.buffered_count, 1)

    def test_malformed_level_shape_invalidates_without_raising(self):
        sync = BookSynchronizer("BTCUSDT")
        outcome = sync.on_delta(delta(10, 100, [["100"]]))
        self.assertEqual(outcome.state, "INVALID")
        self.assertFalse(outcome.request_snapshot)
        self.assertFalse(sync.valid)

    def test_non_integer_sequence_values_are_rejected(self):
        sync = BookSynchronizer("BTCUSDT")
        malformed = delta(10, 100)
        malformed["data"]["u"] = 10.5
        outcome = sync.on_delta(malformed)
        self.assertEqual(outcome.state, "INVALID")
        self.assertFalse(sync.valid)

    def test_boolean_sequence_values_are_rejected(self):
        sync = BookSynchronizer("BTCUSDT")
        malformed = delta(10, 100)
        malformed["data"]["seq"] = True
        outcome = sync.on_delta(malformed)
        self.assertEqual(outcome.state, "INVALID")
        self.assertFalse(sync.valid)

    def test_malformed_event_does_not_trigger_snapshot_without_buffer(self):
        sync = BookSynchronizer("BTCUSDT")
        outcome = sync.on_delta({"topic": "orderbook.full.BTCUSDT", "type": "delta", "data": None})
        self.assertEqual(outcome.state, "INVALID")
        self.assertFalse(outcome.request_snapshot)
        self.assertFalse(sync.valid)

    def test_delta_requires_both_side_arrays(self):
        for missing_side in ("b", "a"):
            with self.subTest(missing_side=missing_side):
                sync = BookSynchronizer("BTCUSDT")
                malformed = delta(10, 100)
                del malformed["data"][missing_side]
                outcome = sync.on_delta(malformed)
                self.assertEqual(outcome.state, "INVALID")
                self.assertFalse(sync.valid)
                self.assertEqual(sync.buffered_count, 0)

    def test_each_missing_side_after_live_invalidates_book(self):
        for missing_side in ("b", "a"):
            with self.subTest(missing_side=missing_side):
                sync = BookSynchronizer("BTCUSDT")
                sync.on_delta(delta(10, 100))
                self.assertEqual(sync.on_snapshot(snapshot()).state, "LIVE_VALID")
                malformed = delta(11, 101)
                del malformed["data"][missing_side]
                outcome = sync.on_delta(malformed)
                self.assertEqual(outcome.state, "INVALID")
                self.assertFalse(sync.valid)

    def test_u_one_empty_rest_snapshot_is_no_book_not_live_valid(self):
        sync = BookSynchronizer("BTCUSDT")
        sync.on_delta(delta(1, 200))
        outcome = sync.on_snapshot({"u": 1, "seq": 200, "b": [], "a": []})
        self.assertEqual(outcome.state, "NO_BOOK")
        self.assertFalse(sync.valid)
        self.assertTrue(sync.no_book)
        self.assertEqual(sync.last_invalidation_reason, "u=1_empty_snapshot_no_book")

    def test_bridge_resync_failure_immediately_requests_fresh_snapshot(self):
        sync = BookSynchronizer("BTCUSDT")
        sync.on_delta(delta(10, 100))
        with patch(
            "nexus_bybit_recorder.synchronizer.bridge_snapshot",
            side_effect=ResyncRequired("synthetic bridge discontinuity"),
        ):
            outcome = sync.on_snapshot(snapshot())
        self.assertEqual(outcome.state, "SYNCING")
        self.assertTrue(outcome.request_snapshot)
        self.assertEqual(sync.buffered_count, 1)
        self.assertEqual(sync._buffer[0].update_id, 10)

    def test_identical_duplicate_update_id_is_ignored(self):
        sync = BookSynchronizer("BTCUSDT")
        first = delta(10, 100)
        sync.on_delta(first)
        self.assertEqual(sync.on_snapshot(snapshot()).state, "LIVE_VALID")
        update = delta(11, 101, [["100", "7"]])
        self.assertEqual(sync.on_delta(update).state, "LIVE_VALID")
        duplicate = delta(11, 101, [["100", "7"]])
        outcome = sync.on_delta(duplicate)
        self.assertEqual(outcome.state, "LIVE_VALID")
        self.assertTrue(sync.valid)
        self.assertEqual(sync.book.bids["100"], "7")

    def test_conflicting_duplicate_update_id_invalidates_live_book(self):
        sync = BookSynchronizer("BTCUSDT")
        sync.on_delta(delta(10, 100))
        self.assertEqual(sync.on_snapshot(snapshot()).state, "LIVE_VALID")
        self.assertEqual(sync.on_delta(delta(11, 101, [["100", "7"]])).state, "LIVE_VALID")
        outcome = sync.on_delta(delta(11, 101, [["100", "8"]]))
        self.assertEqual(outcome.state, "SYNCING")
        self.assertTrue(outcome.request_snapshot)
        self.assertFalse(sync.valid)
        self.assertIn("conflicting duplicate update id", outcome.reason)

    def test_unexpected_orderbook_topic_invalidates_live_book(self):
        sync = BookSynchronizer("BTCUSDT")
        sync.on_delta(delta(10, 100))
        self.assertEqual(sync.on_snapshot(snapshot()).state, "LIVE_VALID")
        wrong_topic = delta(11, 101)
        wrong_topic["topic"] = "orderbook.full.ETHUSDT"
        outcome = sync.on_delta(wrong_topic)
        self.assertEqual(outcome.state, "INVALID")
        self.assertFalse(sync.valid)


if __name__ == "__main__":
    unittest.main()
