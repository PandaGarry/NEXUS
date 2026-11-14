from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Iterator


class JournalIntegrityError(ValueError):
    pass


def iter_verified_frames(path: str | Path) -> Iterator[dict]:
    """Read journal in append order and verify each exact raw-payload digest."""
    with Path(path).open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise JournalIntegrityError(f"invalid JSON at line {line_number}") from exc
            raw = record.get("raw_frame")
            if not isinstance(raw, str):
                raise JournalIntegrityError(f"missing raw frame at line {line_number}")
            actual = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            if actual != record.get("raw_sha256"):
                raise JournalIntegrityError(f"raw payload checksum mismatch at line {line_number}")
            yield record


def summarize(path: str | Path) -> dict:
    generations: set[int] = set()
    topics: Counter[str] = Counter()
    record_types: Counter[str] = Counter()
    control_ops: Counter[str] = Counter()
    control_frames = 0
    non_json_frames = 0
    other_json_frames = 0
    non_ws_records = 0
    snapshot_responses = 0
    snapshot_errors = 0
    book_states: Counter[str] = Counter()
    valid_book_events = 0
    frames = 0
    for record in iter_verified_frames(path):
        frames += 1
        generations.add(int(record["connection_generation"]))
        record_type = str(record.get("record_type", "unknown"))
        record_types[record_type] += 1
        if record_type != "raw_ws_frame":
            non_ws_records += 1
            if record_type == "raw_rest_snapshot":
                snapshot_responses += 1
            if record_type.endswith("_error"):
                snapshot_errors += 1
            if record_type == "derived_book_state":
                try:
                    state_payload = json.loads(record["raw_frame"])
                except json.JSONDecodeError:
                    other_json_frames += 1
                else:
                    state = state_payload.get("state")
                    if isinstance(state, str):
                        book_states[state] += 1
                    if state_payload.get("valid") is True:
                        valid_book_events += 1
            continue
        try:
            payload = json.loads(record["raw_frame"])
        except json.JSONDecodeError:
            non_json_frames += 1
            continue
        if not isinstance(payload, dict):
            other_json_frames += 1
            continue
        topic = payload.get("topic")
        if isinstance(topic, str):
            topics[topic] += 1
            continue
        op = payload.get("op")
        if isinstance(op, str):
            control_ops[op] += 1
            control_frames += 1
        elif any(key in payload for key in ("success", "retCode", "ret_msg", "conn_id", "req_id")):
            control_ops["control_without_op"] += 1
            control_frames += 1
        else:
            other_json_frames += 1
    classified = sum(topics.values()) + control_frames + non_json_frames + other_json_frames + non_ws_records
    return {
        "frames": frames,
        "connection_generations": len(generations),
        "record_types": dict(sorted(record_types.items())),
        "topics": dict(sorted(topics.items())),
        "control_frames": control_frames,
        "control_ops": dict(sorted(control_ops.items())),
        "non_json_frames": non_json_frames,
        "other_json_frames": other_json_frames,
        "non_ws_records": non_ws_records,
        "snapshot_responses": snapshot_responses,
        "snapshot_errors": snapshot_errors,
        "book_states": dict(sorted(book_states.items())),
        "valid_book_events": valid_book_events,
        "classification_total": classified,
        "classification_reconciles": classified == frames,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify and summarize a NEXUS raw market-data journal")
    parser.add_argument("journal", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.journal), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
