from __future__ import annotations

import json
from typing import Any


class DuplicateJSONKeyError(ValueError):
    """Raised when a JSON object contains the same key more than once."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKeyError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def strict_json_loads(payload: str | bytes | bytearray) -> Any:
    """Decode JSON while rejecting duplicate keys at every object depth."""
    return json.loads(payload, object_pairs_hook=_unique_object)
