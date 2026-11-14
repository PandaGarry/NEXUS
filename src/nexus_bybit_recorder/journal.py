from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class RawFrameJournal:
    """Append-only JSONL journal. Raw frame is stored before any parsing."""

    def __init__(self, path: str | Path, *, flush_each_frame: bool = True) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("a", encoding="utf-8", newline="\n")
        self.flush_each_frame = flush_each_frame
        self.count = 0

    def append(self, raw_frame: str, connection_generation: int) -> dict[str, Any]:
        received_wall_ns = time.time_ns()
        received_monotonic_ns = time.monotonic_ns()
        record = {
            "record_type": "raw_ws_frame",
            "connection_generation": connection_generation,
            "received_at_utc": datetime.fromtimestamp(
                received_wall_ns / 1_000_000_000, tz=timezone.utc
            ).isoformat(timespec="microseconds"),
            "received_wall_ns": received_wall_ns,
            "received_monotonic_ns": received_monotonic_ns,
            "raw_frame": raw_frame,
            "raw_sha256": hashlib.sha256(raw_frame.encode("utf-8")).hexdigest(),
        }
        self._file.write(json.dumps(record, separators=(",", ":"), ensure_ascii=False) + "\n")
        if self.flush_each_frame:
            self._file.flush()
        self.count += 1
        return record

    def close(self) -> None:
        if not self._file.closed:
            self._file.flush()
            self._file.close()

    def __enter__(self) -> "RawFrameJournal":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
