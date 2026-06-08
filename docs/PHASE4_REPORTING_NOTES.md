# Phase 4 Reporting Notes

last_updated: 2026-06-08

## Goal

Add a lightweight report generator that turns a ranked submission CSV into interview/deck evidence.

The report is separate from the official rank-time path. It does not affect ranking and can be run after the CSV is generated.

## What The Report Produces

- Submission SHA-256 hash for determinism proof.
- Runtime field for documenting full-run performance.
- Top-10 score separation to prove score saturation was fixed.
- Score bands for the top 100.
- Top current-title distribution.
- Experience-band distribution.
- Evidence coverage across the top 100:
  - embeddings
  - fine-tuning
  - production
  - evaluation
  - Python
  - LLM
  - search/ranking/retrieval
- Control checks:
  - non-engineering titles in top 10
  - AI-title candidates in top 100
  - engineering-title candidates in top 100
  - honeypot/weak-fit concern count
- Top-10 reasoning preview.

## Validation Run

Command:

```text
python scripts/generate_report.py --submission outputs/submission_full_phase3.csv --candidates <official candidates.jsonl> --runtime-seconds 48.25 --output-md outputs/report_full_phase4.md --output-json outputs/report_full_phase4.json
```

Result:

```text
Wrote markdown report: outputs/report_full_phase4.md
Wrote JSON report: outputs/report_full_phase4.json
```

A copy of the latest markdown audit report is committed at:

```text
docs/REPORT_FULL_PHASE4.md
```

## Current Full-Run Evidence

```text
Candidates ranked: 100
Score range: 0.8692 - 0.9318
Average score: 0.8866
Median score: 0.8838
Top-10 spread: 0.0264
Non-engineering titles in top 10: 0
AI-title candidates in top 100: 98
Engineering-title candidates in top 100: 100
Honeypot/weak-fit concern count in top 100: 1
```

## Determinism Proof

The report prints a SHA-256 of the generated CSV:

```text
14eae0a12ad1192c633527e1cfb2c2e9a109e75cd10f5ff8d4c772f37ea1b989
```

Defense line:

```text
Same input and same code path should reproduce the same CSV hash.
```
