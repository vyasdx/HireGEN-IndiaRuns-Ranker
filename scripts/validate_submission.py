from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

REQUIRED_COLUMNS = ["candidate_id", "rank", "score", "reasoning"]
ID_PATTERN = re.compile(r"^CAND_[0-9]{7}$")


def validate(path: str | Path, expected_rows: int = 100) -> list[str]:
    errors: list[str] = []
    csv_path = Path(path)

    if not csv_path.exists():
        return [f"Missing file: {csv_path}"]

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != REQUIRED_COLUMNS:
            errors.append(f"Header must be exactly {REQUIRED_COLUMNS}, got {reader.fieldnames}")
            return errors

        rows = list(reader)

    if len(rows) != expected_rows:
        errors.append(f"Expected exactly {expected_rows} rows, got {len(rows)}")

    seen_ids: set[str] = set()
    seen_ranks: set[int] = set()
    previous_score: float | None = None

    for index, row in enumerate(rows, start=1):
        candidate_id = row["candidate_id"]
        if not ID_PATTERN.match(candidate_id):
            errors.append(f"Row {index}: invalid candidate_id {candidate_id!r}")
        if candidate_id in seen_ids:
            errors.append(f"Row {index}: duplicate candidate_id {candidate_id}")
        seen_ids.add(candidate_id)

        try:
            rank = int(row["rank"])
        except ValueError:
            errors.append(f"Row {index}: rank is not an integer")
            continue

        if rank != index:
            errors.append(f"Row {index}: rank should be {index}, got {rank}")
        seen_ranks.add(rank)

        try:
            score = float(row["score"])
        except ValueError:
            errors.append(f"Row {index}: score is not numeric")
            continue

        if not 0 <= score <= 1:
            errors.append(f"Row {index}: score must be between 0 and 1, got {score}")
        if previous_score is not None and score > previous_score:
            errors.append(f"Row {index}: score {score} is greater than previous score {previous_score}")
        previous_score = score

        if not row["reasoning"].strip():
            errors.append(f"Row {index}: reasoning is empty")

    expected_ranks = set(range(1, expected_rows + 1))
    if seen_ranks != expected_ranks:
        errors.append("Ranks must be exactly 1 through 100")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate IndiaRuns submission CSV.")
    parser.add_argument("csv_path")
    parser.add_argument("--expected-rows", type=int, default=100)
    args = parser.parse_args()

    errors = validate(args.csv_path, expected_rows=args.expected_rows)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
