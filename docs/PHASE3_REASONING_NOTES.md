# Phase 3 Reasoning Notes

last_updated: 2026-06-08

## Goal

Improve candidate reasoning quality without adding any LLM dependency at rank time.

The ranking step must remain:

- deterministic
- CPU-only
- no network
- no hosted LLM/API calls
- reproducible in the evaluator sandbox

## What Changed

- Added an `EvidenceBundle` built from actual candidate fields.
- Reasoning now quotes matched terms such as `embeddings`, `fine-tuning`, `production`, `python`, `evaluation`, and relevant role titles.
- Added deterministic template variation using candidate ID modulo logic.
- Added concern notes when weak evidence patterns fire:
  - missing evaluation/benchmark signal
  - adjacent/non-core title fit
  - weak or unsupported AI evidence
  - limited production engineering signal
- Kept all reasoning generation rule-based and grounded in parsed candidate data.

## Validation

Sample run:

```text
python scripts/run_ranker.py --input data/official/sample_candidates.json --output outputs/submission_sample_phase3.csv --limit 50
python scripts/validate_submission.py outputs/submission_sample_phase3.csv --expected-rows 50
```

Result:

```text
VALID
```

Full 100k run:

```text
python scripts/run_ranker.py --input <official candidates.jsonl> --output outputs/submission_full_phase3.csv --limit 100
python scripts/validate_submission.py outputs/submission_full_phase3.csv
```

Result:

```text
Ranked 100 of 100000 candidates in 48.25s
VALID
```

## Example Reasoning

```text
Ranked for deep learning, embeddings, and llm plus cloud, production, and python; profile shows Lead AI Engineer with 6.7 yrs. Relevant role evidence: Lead AI Engineer, and Senior Machine Learning Engineer. availability 1.00, response 0.73. No major deterministic concern triggered.
```

## Why This Matters

This approach avoids hallucination risk because every phrase comes from:

- matched candidate terms
- title/career history
- Redrob behavioral signals
- deterministic penalty/concern rules

It should be easier to defend in Stage 4 manual review because the reasoning is readable but still reproducible.
