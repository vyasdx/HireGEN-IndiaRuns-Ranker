"""Submission report helpers for audit and demo materials."""

from __future__ import annotations

import csv
import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

from hiregen_ranker.io import iter_candidates


def build_report(
    *,
    submission_path: str | Path,
    candidates_path: str | Path | None = None,
    runtime_seconds: float | None = None,
) -> dict[str, Any]:
    rows = _read_submission(submission_path)
    candidate_lookup = _candidate_lookup(candidates_path, {row["candidate_id"] for row in rows})

    scores = [float(row["score"]) for row in rows]
    top_10_scores = scores[:10]
    titles = Counter()
    locations = Counter()
    experience_bands = Counter()
    concern_counts = Counter()
    evidence_terms = Counter()
    top_10_non_engineering: list[str] = []
    top_100_ai_title_count = 0
    top_100_engineering_title_count = 0

    for row in rows:
        candidate = candidate_lookup.get(row["candidate_id"], {})
        profile = candidate.get("profile", {})
        title = str(profile.get("current_title") or _title_from_reasoning(row["reasoning"]) or "Unknown")
        location = str(profile.get("location") or "Unknown")
        years = float(profile.get("years_of_experience") or 0)

        titles[title] += 1
        locations[location] += 1
        experience_bands[_experience_band(years)] += 1
        if _is_ai_title(title):
            top_100_ai_title_count += 1
        if _is_engineering_title(title):
            top_100_engineering_title_count += 1
        if int(row["rank"]) <= 10 and not _is_engineering_title(title):
            top_10_non_engineering.append(f"{row['candidate_id']} - {title}")
        for concern in _concerns(row["reasoning"]):
            concern_counts[concern] += 1
        for term in _evidence_terms(row["reasoning"]):
            evidence_terms[term] += 1

    signal_coverage = _signal_coverage(rows)
    honeypot_or_weak_fit_count = sum(
        count
        for concern, count in concern_counts.items()
        if "unsupported" in concern
        or "weak-fit" in concern
        or "not backed" in concern
        or "not a close" in concern
    )

    return {
        "summary": {
            "candidate_count": len(rows),
            "score_max": round(max(scores), 4) if scores else 0,
            "score_min": round(min(scores), 4) if scores else 0,
            "score_avg": round(statistics.mean(scores), 4) if scores else 0,
            "score_median": round(statistics.median(scores), 4) if scores else 0,
            "submission_sha256": _sha256_file(submission_path),
            "runtime_seconds": runtime_seconds,
            "determinism_note": "Same input and same code path should reproduce the same CSV hash.",
        },
        "score_bands": dict(_score_bands(scores)),
        "top_10_score_separation": {
            "rank_1_score": round(top_10_scores[0], 4) if len(top_10_scores) >= 1 else 0,
            "rank_10_score": round(top_10_scores[9], 4) if len(top_10_scores) >= 10 else 0,
            "spread": round(top_10_scores[0] - top_10_scores[9], 4) if len(top_10_scores) >= 10 else 0,
            "average_gap": round((top_10_scores[0] - top_10_scores[9]) / 9, 4)
            if len(top_10_scores) >= 10
            else 0,
        },
        "evidence_coverage": signal_coverage,
        "control_checks": {
            "top_10_non_engineering_count": len(top_10_non_engineering),
            "top_10_non_engineering": top_10_non_engineering,
            "top_100_ai_title_count": top_100_ai_title_count,
            "top_100_engineering_title_count": top_100_engineering_title_count,
            "honeypot_or_weak_fit_concern_count": honeypot_or_weak_fit_count,
        },
        "top_titles": titles.most_common(15),
        "top_locations": locations.most_common(10),
        "experience_bands": dict(experience_bands),
        "concerns": concern_counts.most_common(10),
        "evidence_terms": evidence_terms.most_common(15),
        "top_10": [
            {
                "rank": int(row["rank"]),
                "candidate_id": row["candidate_id"],
                "score": float(row["score"]),
                "title": str(candidate_lookup.get(row["candidate_id"], {}).get("profile", {}).get("current_title", "")),
                "reasoning": row["reasoning"],
            }
            for row in rows[:10]
        ],
    }


def write_markdown_report(report: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# HireGEN Ranker Submission Report",
        "",
        "## Summary",
        "",
        f"- Candidates ranked: {report['summary']['candidate_count']}",
        f"- Score range: {report['summary']['score_min']} - {report['summary']['score_max']}",
        f"- Average score: {report['summary']['score_avg']}",
        f"- Median score: {report['summary']['score_median']}",
        f"- Submission SHA-256: `{report['summary']['submission_sha256']}`",
        f"- Runtime seconds: {report['summary']['runtime_seconds']}",
        f"- Determinism note: {report['summary']['determinism_note']}",
        "",
        "## Top-10 Score Separation",
        "",
        f"- Rank 1 score: {report['top_10_score_separation']['rank_1_score']}",
        f"- Rank 10 score: {report['top_10_score_separation']['rank_10_score']}",
        f"- Top-10 spread: {report['top_10_score_separation']['spread']}",
        f"- Average rank-to-rank gap: {report['top_10_score_separation']['average_gap']}",
        "",
        "## Evidence Coverage In Top 100",
        "",
    ]
    lines.extend(_table(["Signal", "Count", "Coverage"], _coverage_rows(report["evidence_coverage"])))
    lines.extend(
        [
            "",
            "## Control Checks",
            "",
            f"- Non-engineering titles in top 10: {report['control_checks']['top_10_non_engineering_count']}",
            f"- AI-title candidates in top 100: {report['control_checks']['top_100_ai_title_count']}",
            f"- Engineering-title candidates in top 100: {report['control_checks']['top_100_engineering_title_count']}",
            f"- Honeypot/weak-fit concern count in top 100: {report['control_checks']['honeypot_or_weak_fit_concern_count']}",
            "",
            "## Score Bands",
        ]
    )
    lines.extend(_table(["Band", "Count"], report["score_bands"].items()))
    lines.extend(["", "## Top Current Titles", ""])
    lines.extend(_table(["Title", "Count"], report["top_titles"]))
    lines.extend(["", "## Experience Bands", ""])
    lines.extend(_table(["Experience", "Count"], report["experience_bands"].items()))
    lines.extend(["", "## Deterministic Concerns", ""])
    lines.extend(_table(["Concern", "Count"], report["concerns"] or [("None", 0)]))
    lines.extend(["", "## Evidence Terms Seen In Reasoning", ""])
    lines.extend(_table(["Evidence Term", "Count"], report["evidence_terms"]))
    lines.extend(["", "## Top 10 Reasoning Preview", ""])

    for item in report["top_10"]:
        title = item["title"] or "Unknown title"
        lines.extend(
            [
                f"### #{item['rank']} {item['candidate_id']} - {title} ({item['score']:.4f})",
                "",
                item["reasoning"],
                "",
            ]
        )

    path.write_text("\n".join(lines), encoding="utf-8")


def write_json_report(report: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def _read_submission(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _candidate_lookup(path: str | Path | None, candidate_ids: set[str]) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}

    lookup: dict[str, dict[str, Any]] = {}
    for candidate in iter_candidates(path):
        candidate_id = str(candidate.get("candidate_id", ""))
        if candidate_id in candidate_ids:
            lookup[candidate_id] = candidate
            if len(lookup) == len(candidate_ids):
                break
    return lookup


def _experience_band(years: float) -> str:
    if years < 3:
        return "0-3 yrs"
    if years < 5:
        return "3-5 yrs"
    if years <= 9:
        return "5-9 yrs"
    if years <= 12:
        return "9-12 yrs"
    return "12+ yrs"


def _score_bands(scores: list[float]) -> Counter[str]:
    bands = Counter({"0.90-1.00": 0, "0.80-0.89": 0, "0.70-0.79": 0, "0.60-0.69": 0, "<0.60": 0})
    for score in scores:
        if score >= 0.9:
            bands["0.90-1.00"] += 1
        elif score >= 0.8:
            bands["0.80-0.89"] += 1
        elif score >= 0.7:
            bands["0.70-0.79"] += 1
        elif score >= 0.6:
            bands["0.60-0.69"] += 1
        else:
            bands["<0.60"] += 1
    return bands


def _concerns(reasoning: str) -> list[str]:
    if "No major deterministic concern triggered" in reasoning:
        return []
    marker = "Concern:"
    if marker not in reasoning:
        return []
    concern_text = reasoning.split(marker, 1)[1].strip().rstrip(".")
    return [item.strip() for item in concern_text.split(";") if item.strip()]


def _evidence_terms(reasoning: str) -> list[str]:
    known_terms = [
        "embeddings",
        "fine-tuning",
        "inference",
        "llm",
        "machine learning",
        "retrieval",
        "ranking",
        "rag",
        "search",
        "python",
        "production",
        "deployment",
        "kubernetes",
        "evaluation",
        "feedback loop",
    ]
    text = reasoning.lower()
    return [term for term in known_terms if term in text]


def _signal_coverage(rows: list[dict[str, str]]) -> dict[str, dict[str, float | int]]:
    signals = {
        "embeddings": "embeddings",
        "fine_tuning": "fine-tuning",
        "production": "production",
        "evaluation": "evaluation",
        "python": "python",
        "llm": "llm",
        "search_or_ranking": ("search", "ranking", "retrieval"),
    }
    coverage: dict[str, dict[str, float | int]] = {}
    total = max(1, len(rows))
    for label, marker in signals.items():
        count = 0
        for row in rows:
            reasoning = row["reasoning"].lower()
            if isinstance(marker, tuple):
                matched = any(item in reasoning for item in marker)
            else:
                matched = marker in reasoning
            if matched:
                count += 1
        coverage[label] = {"count": count, "coverage_pct": round((count / total) * 100, 2)}
    return coverage


def _coverage_rows(coverage: dict[str, dict[str, float | int]]) -> list[tuple[str, int, str]]:
    rows = []
    for signal, values in coverage.items():
        rows.append((signal, int(values["count"]), f"{values['coverage_pct']}%"))
    return rows


def _is_ai_title(title: str) -> bool:
    title_text = title.lower()
    return any(
        term in title_text
        for term in (
            "ai",
            "machine learning",
            "ml engineer",
            "data scientist",
            "search engineer",
            "ranking engineer",
            "recommendation systems engineer",
        )
    )


def _is_engineering_title(title: str) -> bool:
    title_text = title.lower()
    return _is_ai_title(title) or any(
        term in title_text
        for term in (
            "engineer",
            "developer",
            "architect",
            "data scientist",
            "platform",
            "devops",
        )
    )


def _title_from_reasoning(reasoning: str) -> str | None:
    if " with " in reasoning:
        return reasoning.split(" with ", 1)[0].strip('"')
    if "profile shows " in reasoning:
        segment = reasoning.split("profile shows ", 1)[1]
        return segment.split(" with ", 1)[0].strip()
    return None


def _table(headers: list[str], rows: Any) -> list[str]:
    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        output.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return output
