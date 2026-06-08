from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hiregen_ranker.reporting import build_report, write_json_report, write_markdown_report  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a HireGEN Ranker audit report.")
    parser.add_argument("--submission", required=True, help="Path to generated top-100 submission CSV.")
    parser.add_argument("--candidates", help="Optional candidate JSON/JSONL source for title/location enrichment.")
    parser.add_argument("--runtime-seconds", type=float, help="Runtime from the ranking command, if available.")
    parser.add_argument("--output-md", required=True, help="Path to markdown report output.")
    parser.add_argument("--output-json", help="Optional path to JSON report output.")
    args = parser.parse_args()

    report = build_report(
        submission_path=args.submission,
        candidates_path=args.candidates,
        runtime_seconds=args.runtime_seconds,
    )
    write_markdown_report(report, args.output_md)
    if args.output_json:
        write_json_report(report, args.output_json)

    print(f"Wrote markdown report: {args.output_md}")
    if args.output_json:
        print(f"Wrote JSON report: {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
