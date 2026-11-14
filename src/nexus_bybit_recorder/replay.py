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
    """Read journal in append order and verify each exact raw-frame digest."""
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
                raise JournalIntegrityError(f"raw frame checksum mismatch at line {line_number}")
            yield record


def summarize(path: str | Path) -> dict:
    generations: set[int] = set()
    topics: Counter[str] = Counter()
    frames = 0
    for record in iter_verified_frames(path):
        frames += 1
        generations.add(int(record["connection_generation"]))
        try:
            payload = json.loads(record["raw_frame"])
        except json.JSONDecodeError:
            continue
        topic = payload.get("topic")
        if isinstance(topic, str):
            topics[topic] += 1
    return {"frames": frames, "connection_generations": len(generations), "topics": dict(sorted(topics.items()))}


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify and summarize a NEXUS raw market-data journal")
    parser.add_argument("journal", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.journal), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
