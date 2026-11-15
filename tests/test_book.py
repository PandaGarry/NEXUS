import unittest
from nexus_bybit_recorder.book import Delta, OrderBook, ResyncRequired, SnapshotNotCaughtUp, bridge_snapshot


def delta(u, seq, bids=None, asks=None):
    return Delta(u, seq, tuple(bids or []), tuple(asks or []), {})


class OrderBookTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {"u": 10, "seq": 100, "b": [["100", "2"], ["99", "3"]], "a": [["101", "4"], ["102", "5"]]}

    def test_bridge_discards_pre_snapshot_and_applies_following_delta(self):
        buffered = [delta(9, 99, [["98", "1"]]), delta(10, 100), delta(11, 102, [["100", "7"]], [["101", "0"]])]
        book, consumed = bridge_snapshot(self.snapshot, buffered)
        self.assertEqual(consumed, 2)
        self.assertTrue(book.valid)
        self.assertEqual(book.update_id, 11)
        self.assertEqual(book.bids["100"], "7")
        self.assertNotIn("101", book.asks)


    def test_same_snapshot_seq_with_later_u_after_match_requires_new_snapshot(self):
        buffered = [delta(10, 100), delta(11, 100, [["100", "8"]])]
        with self.assertRaises(SnapshotNotCaughtUp):
            bridge_snapshot(self.snapshot, buffered)

    def test_post_snapshot_sequence_regression_forces_resync(self):
        buffered = [
            delta(10, 100),
            delta(11, 102, [["100", "8"]]),
            delta(12, 101, [["99", "9"]]),
        ]
        with self.assertRaises(ResyncRequired):
            bridge_snapshot(self.snapshot, buffered)

    def test_snapshot_behind_buffer_requires_new_snapshot(self):
        with self.assertRaises(SnapshotNotCaughtUp):
            bridge_snapshot(self.snapshot, [delta(11, 101)])

    def test_same_seq_different_u_requires_new_snapshot(self):
        with self.assertRaises(SnapshotNotCaughtUp):
            bridge_snapshot(self.snapshot, [delta(9, 100)])

    def test_buffer_gap_requires_restart(self):
        with self.assertRaises(ResyncRequired):
            bridge_snapshot(self.snapshot, [delta(10, 100), delta(12, 102)])

    def test_duplicate_and_stale_deltas_are_ignored(self):
        book = OrderBook.from_snapshot(self.snapshot)
        book.apply(delta(10, 100, [["98", "3"]]))
        book.apply(delta(9, 99, [["98", "3"]]))
        self.assertNotIn("98", book.bids)
        self.assertEqual(book.update_id, 10)

    def test_u_gap_invalidates_book(self):
        book = OrderBook.from_snapshot(self.snapshot)
        with self.assertRaises(ResyncRequired):
            book.apply(delta(12, 102))
        self.assertFalse(book.valid)
        self.assertEqual(book.bids, {})

    def test_u_one_invalidates_book(self):
        book = OrderBook.from_snapshot(self.snapshot)
        with self.assertRaises(ResyncRequired):
            book.apply(delta(1, 200))
        self.assertFalse(book.valid)

    def test_zero_quantity_deletes_level(self):
        book = OrderBook.from_snapshot(self.snapshot)
        book.apply(delta(11, 101, [["99", "0"]]))
        self.assertNotIn("99", book.bids)

    def test_nonconsecutive_seq_is_not_a_gap(self):
        book = OrderBook.from_snapshot(self.snapshot)
        book.apply(delta(11, 103))
        self.assertTrue(book.valid)
        self.assertEqual(book.cross_seq, 103)

    def test_replay_equals_fresh_snapshot_at_same_watermark(self):
        book = OrderBook.from_snapshot(self.snapshot)
        book.apply(delta(11, 101, [["100", "8"]], [["102", "0"]]))
        fresh = {"u": 11, "seq": 101, "b": [["100", "8"], ["99", "3"]], "a": [["101", "4"]]}
        self.assertEqual(book.fingerprint_view(), OrderBook.from_snapshot(fresh).fingerprint_view())

    def test_identical_buffer_duplicate_is_ignored(self):
        repeated = delta(10, 100)
        book, consumed = bridge_snapshot(self.snapshot, [repeated, repeated])
        self.assertTrue(book.valid)
        self.assertEqual(consumed, 1)

    def test_conflicting_buffer_duplicate_requires_resync(self):
        buffered = [
            delta(10, 100),
            delta(10, 100, [["100", "9"]]),
        ]
        with self.assertRaisesRegex(ResyncRequired, "conflicting duplicate"):
            bridge_snapshot(self.snapshot, buffered)


if __name__ == "__main__":
    unittest.main()
