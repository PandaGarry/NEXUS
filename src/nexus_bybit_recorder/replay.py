from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Iterator

from .snapshot import SnapshotHttpResponse, parse_full_depth_snapshot
from .jsonutil import strict_json_loads
from .synchronizer import BookSynchronizer


class JournalIntegrityError(ValueError):
    pass


def iter_verified_frames(path: str | Path) -> Iterator[dict]:
    """Read journal in append order and verify each exact raw-payload digest."""
    with Path(path).open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            try:
                record = strict_json_loads(line)
            except (json.JSONDecodeError, ValueError) as exc:
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
                except (json.JSONDecodeError, ValueError):
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
            control_label = "pong_reply" if op == "ping" and payload.get("ret_msg") == "pong" else op
            control_ops[control_label] += 1
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


def replay_book(path: str | Path) -> dict:
    """Rebuild book state from raw WS deltas and journaled REST snapshots."""
    synchronizers: dict[tuple[int, str], BookSynchronizer] = {}
    marker_matches = 0
    marker_mismatches: list[str] = []
    delta_events = 0
    snapshot_events = 0
    def get_sync(generation: int, symbol: str) -> BookSynchronizer:
        key = (generation, symbol)
        if key not in synchronizers:
            synchronizers[key] = BookSynchronizer(symbol)
        return synchronizers[key]

    for index, record in enumerate(iter_verified_frames(path), start=1):
        generation = int(record["connection_generation"])
        record_type = record.get("record_type", "raw_ws_frame")
        raw = record["raw_frame"]
        if record_type == "raw_ws_frame":
            metadata = record.get("metadata") or {}
            expected_symbol = metadata.get("expected_symbol")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                if isinstance(expected_symbol, str):
                    get_sync(generation, expected_symbol).invalidate("malformed_ws_frame")
                else:
                    for (gen, _), sync in synchronizers.items():
                        if gen == generation:
                            sync.invalidate("malformed_ws_frame")
                continue
            if not isinstance(payload, dict):
                if isinstance(expected_symbol, str):
                    get_sync(generation, expected_symbol).invalidate("malformed_ws_frame")
                else:
                    for (gen, _), sync in synchronizers.items():
                        if gen == generation:
                            sync.invalidate("malformed_ws_frame")
                continue
            topic = payload.get("topic")
            is_orderbook_frame = (
                isinstance(topic, str) and topic.startswith("orderbook.full.")
            ) or (
                payload.get("type") == "delta"
                and isinstance(payload.get("data"), dict)
                and ("u" in payload["data"] or "seq" in payload["data"])
            )
            if is_orderbook_frame:
                topic_symbol = (
                    topic.removeprefix("orderbook.full.")
                    if isinstance(topic, str) and topic.startswith("orderbook.full.")
                    else None
                )
                if isinstance(expected_symbol, str) and topic_symbol != expected_symbol:
                    get_sync(generation, expected_symbol).invalidate("unexpected_topic")
                elif topic_symbol is not None:
                    sync = get_sync(generation, topic_symbol)
                    sync.on_delta(payload)
                elif isinstance(expected_symbol, str):
                    get_sync(generation, expected_symbol).on_delta(payload)
                delta_events += 1
        elif record_type == "raw_rest_snapshot":
            metadata = record.get("metadata") or {}
            sync = None
            try:
                payload = json.loads(raw)
                result = payload.get("result", {}) if isinstance(payload, dict) else {}
                symbol = result.get("s") if isinstance(result, dict) else None
                if not isinstance(symbol, str):
                    raise ValueError("snapshot has no symbol")
                sync = get_sync(generation, symbol)
                response = SnapshotHttpResponse(
                    request_url=str(metadata.get("request_url", "")),
                    http_status=int(metadata.get("http_status", 0)),
                    body=raw,
                    received_wall_ns=int(record.get("received_wall_ns", 0)),
                    received_monotonic_ns=int(record.get("received_monotonic_ns", 0)),
                )
                snapshot = parse_full_depth_snapshot(response, expected_symbol=symbol)
                sync.on_snapshot(snapshot)
                snapshot_events += 1
            except (ValueError, TypeError, KeyError, json.JSONDecodeError):
                if sync is not None:
                    sync.invalidate("replay_snapshot_invalid")
        elif record_type in {"rest_snapshot_error", "snapshot_validation_error"}:
            # Error events invalidate the current generation's in-flight book state.
            candidates = [sync for (gen, _), sync in synchronizers.items() if gen == generation]
            for sync in candidates:
                sync.invalidate(record_type)
        elif record_type == "derived_book_state":
            try:
                marker = json.loads(raw)
            except json.JSONDecodeError:
                marker_mismatches.append(f"line {index}: malformed derived state marker")
                continue
            if not isinstance(marker, dict):
                marker_mismatches.append(f"line {index}: derived state marker is not an object")
                continue
            symbol = marker.get("symbol")
            if marker.get("state") == "INVALID" and marker.get("reason") == "websocket_disconnect_or_generation_end":
                if isinstance(symbol, str):
                    get_sync(generation, symbol).on_disconnect()
                else:
                    for (gen, _), sync in synchronizers.items():
                        if gen == generation:
                            sync.on_disconnect()
            if isinstance(symbol, str):
                sync = get_sync(generation, symbol)
                if "valid" in marker and bool(marker.get("valid")) != sync.valid:
                    marker_mismatches.append(
                        f"line {index}: recorded validity does not match replay for {symbol}"
                    )
                if marker.get("state") == "LIVE_VALID":
                    matched = (
                        sync.valid
                        and sync.book is not None
                        and sync.book.update_id == marker.get("update_id")
                        and sync.book.cross_seq == marker.get("cross_seq")
                    )
                    expected_fingerprint = marker.get("fingerprint_sha256")
                    if matched and isinstance(expected_fingerprint, str):
                        actual_fingerprint = hashlib.sha256(
                            json.dumps(
                                sync.book.fingerprint_view(), separators=(",", ":")
                            ).encode("utf-8")
                        ).hexdigest()
                        matched = actual_fingerprint == expected_fingerprint
                    if matched:
                        marker_matches += 1
                    else:
                        marker_mismatches.append(
                            f"line {index}: LIVE_VALID marker watermark/fingerprint mismatch for {symbol}"
                        )
                elif marker.get("state") == "NO_BOOK" and not sync.no_book:
                    marker_mismatches.append(
                        f"line {index}: NO_BOOK marker does not match replay for {symbol}"
                    )
            elif marker.get("state") == "LIVE_VALID":
                # Backward compatibility for older journals without symbol/fingerprint fields.
                symbol_candidates = [
                    sync for (gen, _), sync in synchronizers.items()
                    if gen == generation and sync.valid
                ]
                matched = any(
                    sync.book is not None
                    and sync.book.update_id == marker.get("update_id")
                    and sync.book.cross_seq == marker.get("cross_seq")
                    for sync in symbol_candidates
                )
                if matched:
                    marker_matches += 1
                else:
                    marker_mismatches.append(
                        f"line {index}: LIVE_VALID marker did not match replayed watermark"
                    )

    final_books = {}
    for (generation, symbol), sync in sorted(synchronizers.items()):
        fingerprint = None
        if sync.valid and sync.book is not None:
            fingerprint = hashlib.sha256(
                json.dumps(sync.book.fingerprint_view(), separators=(",", ":")).encode("utf-8")
            ).hexdigest()
        final_books[f"{generation}:{symbol}"] = {
            "valid": sync.valid,
            "update_id": sync.book.update_id if sync.valid and sync.book else None,
            "cross_seq": sync.book.cross_seq if sync.valid and sync.book else None,
            "fingerprint_sha256": fingerprint,
            "no_book": sync.no_book,
            "last_invalidation_reason": sync.last_invalidation_reason,
        }
    return {
        "delta_events": delta_events,
        "snapshot_events": snapshot_events,
        "valid_book_markers_matched": marker_matches,
        "marker_mismatches": marker_mismatches,
        "final_books": final_books,
        "replay_matches_recorded_valid_markers": not marker_mismatches,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify and summarize a NEXUS raw market-data journal")
    parser.add_argument("journal", type=Path)
    parser.add_argument("--replay-book", action="store_true", help="rebuild book state from WS deltas and REST snapshots")
    args = parser.parse_args()
    summary = summarize(args.journal)
    if args.replay_book:
        summary["book_replay"] = replay_book(args.journal)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
