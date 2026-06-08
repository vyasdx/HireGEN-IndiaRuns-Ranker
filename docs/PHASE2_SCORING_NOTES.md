# Phase 2 Scoring Notes

last_updated: 2026-06-08

## Goal

Improve the Phase 1 deterministic baseline so it reflects the Senior AI Engineer JD more directly and reduces generic keyword inflation.

## What Changed

- Added stronger JD-intent scoring around AI/ML/retrieval, production engineering, and evaluation signals.
- Separated broad AI terms from direct technical AI/retrieval evidence.
- Added current-title suitability weighting so AI/ML/search/backend/data engineering roles outrank weak-transition profiles.
- Added penalties for weak title fit, unsupported AI claims, and high AI keyword density without technical evidence.
- Replaced hard score saturation with smooth normalization so top candidates do not flatten into identical `0.9999` scores.

## Validation

Sample run:

```text
python scripts/run_ranker.py --input data/official/sample_candidates.json --output outputs/submission_sample_phase2.csv --limit 50
python scripts/validate_submission.py outputs/submission_sample_phase2.csv --expected-rows 50
```

Result:

```text
VALID
```

Full 100k run:

```text
python scripts/run_ranker.py --input <official candidates.jsonl> --output outputs/submission_full_phase2.csv --limit 100
python scripts/validate_submission.py outputs/submission_full_phase2.csv
```

Result:

```text
Ranked 100 of 100000 candidates in 37.22s
VALID
```

## Current Full-Run Top Signals

The top output now starts with strong Senior AI Engineer aligned roles, including:

- Lead AI Engineer
- Senior Machine Learning Engineer
- Staff Machine Learning Engineer
- AI Engineer
- Search Engineer
- Data Scientist

This is a significant improvement over Phase 1, where generic non-engineering profiles could rank too high because of broad AI keywords.

## Remaining Phase 3 Work

- Make explanations more varied and less repetitive.
- Add richer disqualifier categories from the JD.
- Add a small report generator for top-100 title distribution and score bands.
- Consider a lightweight BM25/TF-IDF retrieval layer if deterministic scoring alone is not enough.
