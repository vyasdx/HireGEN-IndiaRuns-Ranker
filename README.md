# HireGEN IndiaRuns Ranker

Offline candidate discovery and ranking engine for the Hack2skill x Redrob India Runs AI & Datathon Arena.

HireGEN Ranker ranks 100,000 anonymized candidate profiles against a Senior AI Engineer job description and outputs the top 100 candidates with deterministic scores and grounded reasoning.

## What This Repo Contains

- CPU-only Python ranking pipeline
- No hosted LLM calls during ranking
- No network calls during ranking
- Streaming JSONL support for the full candidate pool
- JSON-array support for the official sample file
- Deterministic top-k ranking with stable tie-breakers
- Strict submission CSV validator
- Fact-grounded reasoning templates
- Optional Streamlit judge demo for visual inspection

## Repository Layout

```text
data/official/        Small official support files and sample data
demo/                 Optional Streamlit visual demo
docs/                 Phase notes, audit report, and submission Q&A
outputs/              Generated local outputs, ignored by Git
scripts/              CLI entry points
src/hiregen_ranker/   Ranking engine package
```

## Judge Quick Start

```bash
git clone https://github.com/vyasdx/HireGEN-IndiaRuns-Ranker.git
cd HireGEN-IndiaRuns-Ranker
python -m pip install -r requirements.txt
```

The official ranker uses only the Python standard library. `requirements.txt` is intentionally lightweight so setup is predictable in a CPU-only sandbox.

## Run On Official Full Dataset

Place the official challenge dataset at:

```text
data/raw/candidates.jsonl
```

Then run:

```bash
python scripts/run_ranker.py --input data/raw/candidates.jsonl --output outputs/submission.csv --limit 100
```

Expected console shape:

```text
Ranked 100 of 100000 candidates in <runtime>s
Wrote outputs/submission.csv
```

Validate the official output:

```bash
python scripts/validate_submission.py outputs/submission.csv
```

Expected result:

```text
VALID
```

## Run On Included Sample Data

The included sample has 50 candidates, so validate it with `--expected-rows 50`.

```bash
python scripts/run_ranker.py --input data/official/sample_candidates.json --output outputs/submission_sample.csv --limit 100
python scripts/validate_submission.py outputs/submission_sample.csv --expected-rows 50
```

Expected result:

```text
Ranked 50 of 50 candidates in <runtime>s
VALID
```

## Generate Audit Report

```bash
python scripts/generate_report.py --submission outputs/submission.csv --candidates data/raw/candidates.jsonl --runtime-seconds <runtime> --output-md outputs/report.md --output-json outputs/report.json
```

For sample data:

```bash
python scripts/generate_report.py --submission outputs/submission_sample.csv --candidates data/official/sample_candidates.json --runtime-seconds 0.02 --output-md outputs/report_sample.md --output-json outputs/report_sample.json
```

## Optional Visual Demo

The Streamlit demo is for judge/product inspection only. It is not required for the official ranking command.

It lets a reviewer:

- Use the included sample data or upload candidate JSON/JSONL
- Run the same deterministic ranker
- Inspect shortlist tiers
- Check evidence coverage
- Review risk controls
- Read top-10 grounded reasoning
- Download the generated CSV

Run:

```bash
python -m pip install -r requirements-demo.txt
streamlit run demo/streamlit_app.py
```

Then open:

```text
http://localhost:8501
```

The demo can run offline after dependencies are installed. It does not call hosted LLMs or external APIs.

## Submission CSV Contract

The official submission CSV must contain exactly:

```text
candidate_id,rank,score,reasoning
```

Rules enforced by `scripts/validate_submission.py`:

- exactly 100 rows for the full dataset
- ranks 1-100 exactly once
- unique `candidate_id`
- scores between 0 and 1
- scores sorted in non-increasing order
- non-empty reasoning

## Design Choices

- Ranking is deterministic and reproducible.
- Behavioral availability is a multiplier, not a cosmetic bonus.
- Honeypot / suspicious profiles are penalized.
- Reasoning is generated from candidate fields and score components only.
- Optional semantic artifacts, if added later, must be precomputed and excluded from rank-time execution.

## Product Positioning

HireGEN Ranker is a standalone offline ranker for this challenge. It is also the recruiter-intelligence module of the larger HireGEN proof-layer platform, where candidates build evidence-backed proof profiles and recruiters discover trusted talent.
