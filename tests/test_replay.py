import json
import tempfile
import unittest
from pathlib import Path
from nexus_bybit_recorder.journal import RawFrameJournal
from nexus_bybit_recorder.replay import JournalIntegrityError, iter_verified_frames, summarize


class ReplayTests(unittest.TestCase):
    def test_verified_replay_preserves_order_and_counts_topics(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw.jsonl"
            with RawFrameJournal(path) as journal:
                journal.append('{"topic":"publicTrade.BTCUSDT"}', 1)
                journal.append('{"topic":"orderbook.full.BTCUSDT"}', 1)
                journal.append('{"topic":"publicTrade.BTCUSDT"}', 2)
            rows = list(iter_verified_frames(path))
            self.assertEqual([r["connection_generation"] for r in rows], [1, 1, 2])
            self.assertEqual(summarize(path), {
                "frames": 3,
                "connection_generations": 2,
                "topics": {"orderbook.full.BTCUSDT": 1, "publicTrade.BTCUSDT": 2},
            })

    def test_corrupt_frame_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw.jsonl"
            with RawFrameJournal(path) as journal:
                journal.append('{"topic":"publicTrade.BTCUSDT"}', 1)
            row = json.loads(path.read_text())
            row["raw_frame"] = "tampered"
            path.write_text(json.dumps(row) + "\n")
            with self.assertRaises(JournalIntegrityError):
                list(iter_verified_frames(path))


if __name__ == "__main__":
    unittest.main()
