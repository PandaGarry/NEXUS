import json
import tempfile
import unittest
from pathlib import Path
from nexus_bybit_recorder.journal import RawFrameJournal
from nexus_bybit_recorder.replay import JournalIntegrityError, iter_verified_frames, summarize


class ReplayTests(unittest.TestCase):
    def test_verified_replay_preserves_order_and_classifies_every_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw.jsonl"
            with RawFrameJournal(path) as journal:
                journal.append('{"topic":"publicTrade.BTCUSDT"}', 1)
                journal.append('{"topic":"orderbook.full.BTCUSDT"}', 1)
                journal.append('{"op":"subscribe","success":true}', 1)
                journal.append('{"op":"pong"}', 1)
                journal.append('{"success":true,"ret_msg":"OK"}', 1)
                journal.append('not-json', 1)
                journal.append('{"other":"value"}', 1)
                journal.append('{"retCode":0,"result":{"s":"BTCUSDT"}}', 1, record_type="raw_rest_snapshot", metadata={"http_status": 200})
                journal.append('{"state":"LIVE_VALID","valid":true,"update_id":10,"cross_seq":100}', 1, record_type="derived_book_state")
            rows = list(iter_verified_frames(path))
            self.assertEqual([r["connection_generation"] for r in rows], [1] * 8)
            summary = summarize(path)
            self.assertEqual(summary["frames"], 9)
            self.assertEqual(summary["connection_generations"], 1)
            self.assertEqual(summary["topics"], {"orderbook.full.BTCUSDT": 1, "publicTrade.BTCUSDT": 1})
            self.assertEqual(summary["control_ops"], {"control_without_op": 1, "pong": 1, "subscribe": 1})
            self.assertEqual(summary["control_frames"], 3)
            self.assertEqual(summary["non_json_frames"], 1)
            self.assertEqual(summary["other_json_frames"], 1)
            self.assertEqual(summary["non_ws_records"], 2)
            self.assertEqual(summary["record_types"], {"derived_book_state": 1, "raw_rest_snapshot": 1, "raw_ws_frame": 7})
            self.assertEqual(summary["snapshot_responses"], 1)
            self.assertEqual(summary["snapshot_errors"], 0)
            self.assertEqual(summary["book_states"], {"LIVE_VALID": 1})
            self.assertEqual(summary["valid_book_events"], 1)
            self.assertEqual(summary["classification_total"], 9)
            self.assertTrue(summary["classification_reconciles"])

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
