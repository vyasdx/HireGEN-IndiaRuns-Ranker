"""Top-k ranking engine."""

from __future__ import annotations

import csv
import heapq
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from hiregen_ranker.io import iter_candidates
from hiregen_ranker.scoring import ScoreDetails, score_candidate


@dataclass(frozen=True)
class RankedCandidate:
    details: ScoreDetails

    @property
    def heap_key(self) -> tuple[float, float, float, float, float, float, int]:
        return (
            self.details.score,
            self.details.role_fit_score,
            self.details.direct_evidence_score,
            self.details.availability_multiplier,
            -self.details.penalty_score,
            self.details.recency_score,
            -_candidate_number(self.details.candidate_id),
        )

    @property
    def sort_key(self) -> tuple[float, float, float, float, float, float, int]:
        return (
            -self.details.score,
            -self.details.role_fit_score,
            -self.details.direct_evidence_score,
            -self.details.availability_multiplier,
            self.details.penalty_score,
            -self.details.recency_score,
            _candidate_number(self.details.candidate_id),
        )


def rank_candidates(input_path: str | Path, limit: int = 100) -> tuple[list[RankedCandidate], int, float]:
    started = time.perf_counter()
    heap: list[tuple[tuple[float, float, float, float, float, float, int], RankedCandidate]] = []
    seen = 0

    for candidate in iter_candidates(input_path):
        seen += 1
        ranked = RankedCandidate(score_candidate(candidate))
        item = (ranked.heap_key, ranked)
        if len(heap) < limit:
            heapq.heappush(heap, item)
        elif item[0] > heap[0][0]:
            heapq.heapreplace(heap, item)

    ranked_candidates = [item[1] for item in heap]
    ranked_candidates.sort(key=lambda item: item.sort_key)
    elapsed = time.perf_counter() - started
    return ranked_candidates, seen, elapsed


def write_submission(ranked_candidates: Iterable[RankedCandidate], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["candidate_id", "rank", "score", "reasoning"])
        writer.writeheader()
        for rank, candidate in enumerate(ranked_candidates, start=1):
            writer.writerow(
                {
                    "candidate_id": candidate.details.candidate_id,
                    "rank": rank,
                    "score": f"{candidate.details.score:.4f}",
                    "reasoning": candidate.details.reasoning,
                }
            )


def _candidate_number(candidate_id: str) -> int:
    try:
        return int(candidate_id.rsplit("_", 1)[1])
    except (IndexError, ValueError):
        return 0
