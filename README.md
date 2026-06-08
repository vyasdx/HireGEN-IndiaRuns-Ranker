# HireGEN IndiaRuns Ranker

Offline candidate discovery and ranking engine for the Hack2skill x Redrob India Runs AI & Datathon Arena.

The challenge goal is to rank 100,000 anonymized candidate profiles against a Senior AI Engineer job description and output the top 100 candidates with grounded reasoning.

## Current Phase

Phase 1 baseline:

- CPU-only Python ranker
- No hosted LLM calls
- No network calls during ranking
- Streaming JSONL support for full candidate pool
- JSON-array support for the official sample file
- Deterministic top-100 output
- Strict CSV validator

## Repository Layout

```text
data/official/        Small official support files and sample data
docs/                 Planning notes and submission Q&A
outputs/              Generated local outputs, ignored by Git
scripts/              CLI entry points
src/hiregen_ranker/   Ranking engine package
```

## Run Baseline On Sample Candidates

```powershell
python scripts/run_ranker.py `
  --input data/official/sample_candidates.json `
  --output outputs/submission_sample.csv `
  --limit 100
```

Validate:

```powershell
python scripts/validate_submission.py outputs/submission_sample.csv
```

## Full Dataset

Keep the official full `candidates.jsonl` outside Git. A recommended local path is:

```text
data/raw/candidates.jsonl
```

Official submission mode should produce exactly:

```text
candidate_id,rank,score,reasoning
```

with ranks 1-100 exactly once, unique candidate IDs, and non-increasing scores.

## Product Positioning

HireGEN Ranker is the offline ranking brain for HireGEN recruiter workflows. It is intentionally separate from the HireGEN web proof-profile product during the challenge, then can later become the recruiter shortlist module.
