# Phase 5 Demo UI Notes

last_updated: 2026-06-09

## Goal

Add a rich judge-facing UI that demonstrates the ranker live without changing the official deterministic ranking path.

## Demo Surface

File:

```text
demo/streamlit_app.py
```

Run:

```text
pip install -r requirements-demo.txt
streamlit run demo/streamlit_app.py
```

## What Judges Can Do

- Use the official sample candidate data.
- Upload a mock JSON/JSONL candidate file.
- Run the deterministic ranker from the UI.
- View executive proof checks:
  - runtime
  - top-10 score spread
  - non-engineering titles in top 10
  - AI-title candidates in top 100
  - SHA-256 determinism hash
- Inspect shortlist tiers:
  - Tier 1: interview now
  - Tier 2: recruiter review
  - Tier 3: bench
- Review evidence coverage, score bands, concern counts, and top-10 reasoning.
- Download the generated demo CSV.

## Product Boundary

This is intentionally a Streamlit demo for the challenge module. It is not part of the official rank-time command.

Future HireGEN web integration can link to or embed the same workflow under a recruiter dashboard, but for Track 1 this Streamlit app is faster, cleaner, and safer.
