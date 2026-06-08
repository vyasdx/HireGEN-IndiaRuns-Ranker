"""Input helpers for candidate files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator


def iter_candidates(path: str | Path) -> Iterator[dict[str, Any]]:
    """Yield candidates from either a JSON array file or JSONL file."""

    candidate_path = Path(path)
    with candidate_path.open("r", encoding="utf-8") as handle:
        first = handle.read(1)
        handle.seek(0)

        if first == "[":
            data = json.load(handle)
            for candidate in data:
                yield candidate
            return

        for line in handle:
            stripped = line.strip()
            if stripped:
                yield json.loads(stripped)
