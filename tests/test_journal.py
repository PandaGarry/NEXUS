import json
import tempfile
import unittest
from pathlib import Path
from nexus_bybit_recorder.journal import RawFrameJournal


class JournalTests(unittest.TestCase):
    def test_raw_frame_is_journaled_with_generation_and_clocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw.jsonl"
            with RawFrameJournal(path) as journal:
                journal.append('{"topic":"publicTrade.BTCUSDT"}', 4)
            record = json.loads(path.read_text().splitlines()[0])
            self.assertEqual(record["raw_frame"], '{"topic":"publicTrade.BTCUSDT"}')
            self.assertEqual(record["connection_generation"], 4)
            self.assertIn("received_monotonic_ns", record)
            self.assertIn("raw_sha256", record)


if __name__ == "__main__":
    unittest.main()
