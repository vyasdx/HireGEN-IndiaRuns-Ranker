from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hiregen_ranker.ranker import rank_candidates, write_submission  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run HireGEN IndiaRuns candidate ranker.")
    parser.add_argument("--input", required=True, help="Path to sample_candidates.json or candidates.jsonl.")
    parser.add_argument("--output", required=True, help="Path to output submission CSV.")
    parser.add_argument("--limit", type=int, default=100, help="Number of candidates to output.")
    args = parser.parse_args()

    ranked, seen, elapsed = rank_candidates(args.input, limit=args.limit)
    write_submission(ranked, args.output)

    print(f"Ranked {len(ranked)} of {seen} candidates in {elapsed:.2f}s")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
