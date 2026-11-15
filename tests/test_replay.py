import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from nexus_bybit_recorder.journal import RawFrameJournal
from nexus_bybit_recorder.replay import JournalIntegrityError, iter_verified_frames, replay_book, summarize


class ReplayTests(unittest.TestCase):
    def test_verified_replay_preserves_order_and_classifies_every_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw.jsonl"
            with RawFrameJournal(path) as journal:
                journal.append('{"topic":"publicTrade.BTCUSDT"}', 1)
                journal.append('{"topic":"orderbook.full.BTCUSDT"}', 1)
                journal.append('{"op":"subscribe","success":true}', 1)
                journal.append('{"op":"ping","ret_msg":"pong"}', 1)
                journal.append('{"success":true,"ret_msg":"OK"}', 1)
                journal.append('not-json', 1)
                journal.append('{"other":"value"}', 1)
                journal.append('{"retCode":0,"result":{"s":"BTCUSDT"}}', 1, record_type="raw_rest_snapshot", metadata={"http_status": 200})
                journal.append('{"state":"LIVE_VALID","valid":true,"update_id":10,"cross_seq":100}', 1, record_type="derived_book_state")
            rows = list(iter_verified_frames(path))
            self.assertEqual([r["connection_generation"] for r in rows], [1] * 9)
            summary = summarize(path)
            self.assertEqual(summary["frames"], 9)
            self.assertEqual(summary["connection_generations"], 1)
            self.assertEqual(summary["topics"], {"orderbook.full.BTCUSDT": 1, "publicTrade.BTCUSDT": 1})
            self.assertEqual(summary["control_ops"], {"control_without_op": 1, "pong_reply": 1, "subscribe": 1})
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

    def test_replay_reconstructs_snapshot_bridge_and_disconnect(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw.jsonl"
            snapshot = {"retCode": 0, "result": {"s": "BTCUSDT", "u": 10, "seq": 100, "b": [["100", "2"]], "a": [["101", "3"]]}}
            with RawFrameJournal(path) as journal:
                journal.append(json.dumps({"topic": "orderbook.full.BTCUSDT", "type": "delta", "data": {"s": "BTCUSDT", "u": 10, "seq": 100, "b": [], "a": []}}), 1)
                journal.append(json.dumps({"topic": "orderbook.full.BTCUSDT", "type": "delta", "data": {"s": "BTCUSDT", "u": 11, "seq": 102, "b": [["100", "4"]], "a": []}}), 1)
                journal.append(json.dumps(snapshot), 1, record_type="raw_rest_snapshot", metadata={"request_url": "https://api.bybit.com/v5/market/full_orderbook?category=linear&symbol=BTCUSDT", "http_status": 200})
                journal.append(json.dumps({"state": "LIVE_VALID", "valid": True, "update_id": 11, "cross_seq": 102}), 1, record_type="derived_book_state")
                journal.append(json.dumps({"topic": "orderbook.full.BTCUSDT", "type": "delta", "data": {"s": "BTCUSDT", "u": 12, "seq": 103, "b": [["100", "5"]], "a": []}}), 1)
                journal.append(json.dumps({"state": "INVALID", "valid": False, "reason": "websocket_disconnect_or_generation_end"}), 1, record_type="derived_book_state")
            replay = replay_book(path)
            self.assertEqual(replay["delta_events"], 3)
            self.assertEqual(replay["snapshot_events"], 1)
            self.assertEqual(replay["valid_book_markers_matched"], 1)
            self.assertEqual(replay["marker_mismatches"], [])
            self.assertTrue(replay["replay_matches_recorded_valid_markers"])
            self.assertFalse(replay["final_books"]["1:BTCUSDT"]["valid"])

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

    def test_replay_detects_tampered_delta_by_live_fingerprint(self):
        from nexus_bybit_recorder.synchronizer import BookSynchronizer

        first = {
            "topic": "orderbook.full.BTCUSDT", "type": "delta",
            "data": {"s": "BTCUSDT", "u": 10, "seq": 100, "b": [], "a": []},
        }
        second = {
            "topic": "orderbook.full.BTCUSDT", "type": "delta",
            "data": {"s": "BTCUSDT", "u": 11, "seq": 102, "b": [["100", "4"]], "a": []},
        }
        snapshot = {
            "retCode": 0,
            "result": {
                "s": "BTCUSDT", "u": 10, "seq": 100,
                "b": [["100", "2"]], "a": [["101", "3"]],
            },
        }
        sync = BookSynchronizer("BTCUSDT")
        sync.on_delta(first)
        sync.on_delta(second)
        sync.on_snapshot(snapshot["result"])
        fingerprint = hashlib.sha256(
            json.dumps(sync.book.fingerprint_view(), separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        marker = {
            "symbol": "BTCUSDT", "state": "LIVE_VALID", "valid": True,
            "no_book": False, "update_id": 11, "cross_seq": 102,
            "fingerprint_sha256": fingerprint,
        }

        def build(path, quantity):
            changed = json.loads(json.dumps(second))
            changed["data"]["b"][0][1] = quantity
            with RawFrameJournal(path) as journal:
                journal.append(json.dumps(first), 1, metadata={"expected_symbol": "BTCUSDT"})
                journal.append(json.dumps(second), 1, metadata={"expected_symbol": "BTCUSDT"})
                journal.append(
                    json.dumps(snapshot), 1, record_type="raw_rest_snapshot",
                    metadata={"request_url": "https://api.bybit.com/v5/market/full_orderbook", "http_status": 200, "expected_symbol": "BTCUSDT"},
                )
                journal.append(json.dumps(marker), 1, record_type="derived_book_state")

        with tempfile.TemporaryDirectory() as tmp:
            good_path = Path(tmp) / "good.jsonl"
            bad_path = Path(tmp) / "tampered.jsonl"
            build(good_path, "4")
            build(bad_path, "5")
            good = replay_book(good_path)
            bad = replay_book(bad_path)
            self.assertTrue(good["replay_matches_recorded_valid_markers"])
            self.assertFalse(bad["replay_matches_recorded_valid_markers"])
            self.assertTrue(any("fingerprint mismatch" in item for item in bad["marker_mismatches"]))


if __name__ == "__main__":
    unittest.main()
