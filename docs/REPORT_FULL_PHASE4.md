# HireGEN Ranker Submission Report

## Summary

- Candidates ranked: 100
- Score range: 0.8692 - 0.9318
- Average score: 0.8866
- Median score: 0.8838
- Submission SHA-256: `14eae0a12ad1192c633527e1cfb2c2e9a109e75cd10f5ff8d4c772f37ea1b989`
- Runtime seconds: 48.25
- Determinism note: Same input and same code path should reproduce the same CSV hash.

## Top-10 Score Separation

- Rank 1 score: 0.9318
- Rank 10 score: 0.9054
- Top-10 spread: 0.0264
- Average rank-to-rank gap: 0.0029

## Evidence Coverage In Top 100

| Signal | Count | Coverage |
| --- | --- | --- |
| embeddings | 75 | 75.0% |
| fine_tuning | 42 | 42.0% |
| production | 87 | 87.0% |
| evaluation | 24 | 24.0% |
| python | 23 | 23.0% |
| llm | 40 | 40.0% |
| search_or_ranking | 22 | 22.0% |

## Control Checks

- Non-engineering titles in top 10: 0
- AI-title candidates in top 100: 98
- Engineering-title candidates in top 100: 100
- Honeypot/weak-fit concern count in top 100: 1

## Score Bands
| Band | Count |
| --- | --- |
| 0.90-1.00 | 16 |
| 0.80-0.89 | 84 |
| 0.70-0.79 | 0 |
| 0.60-0.69 | 0 |
| <0.60 | 0 |

## Top Current Titles

| Title | Count |
| --- | --- |
| Recommendation Systems Engineer | 13 |
| AI Engineer | 12 |
| Search Engineer | 11 |
| Senior Data Scientist | 11 |
| Machine Learning Engineer | 11 |
| Applied ML Engineer | 9 |
| ML Engineer | 7 |
| Data Scientist | 5 |
| AI Research Engineer | 5 |
| Junior ML Engineer | 4 |
| Senior Machine Learning Engineer | 3 |
| Staff Machine Learning Engineer | 3 |
| Senior AI Engineer | 3 |
| Senior Software Engineer (ML) | 2 |
| Lead AI Engineer | 1 |

## Experience Bands

| Experience | Count |
| --- | --- |
| 5-9 yrs | 75 |
| 12+ yrs | 2 |
| 3-5 yrs | 23 |

## Deterministic Concerns

| Concern | Count |
| --- | --- |
| limited production engineering signal | 28 |
| evaluation/benchmark signal is missing | 9 |
| penalty applied for unsupported or weak-fit signals | 1 |

## Evidence Terms Seen In Reasoning

| Evidence Term | Count |
| --- | --- |
| deployment | 90 |
| production | 87 |
| embeddings | 75 |
| machine learning | 47 |
| fine-tuning | 42 |
| llm | 40 |
| evaluation | 24 |
| python | 23 |
| search | 19 |
| inference | 18 |
| rag | 11 |
| kubernetes | 8 |
| ranking | 5 |
| feedback loop | 1 |

## Top 10 Reasoning Preview

### #1 CAND_0081846 - Lead AI Engineer (0.9318)

Ranked for deep learning, embeddings, and llm plus cloud, production, and python; profile shows Lead AI Engineer with 6.7 yrs. Relevant role evidence: Lead AI Engineer, and Senior Machine Learning Engineer. availability 1.00, response 0.73. No major deterministic concern triggered.

### #2 CAND_0018499 - Senior Machine Learning Engineer (0.9280)

Senior Machine Learning Engineer with 7.2 yrs; evidence includes deep learning, embeddings, and inference. Engineering/recruiter signals: cloud, kubernetes, and production; availability 0.98, response 0.61. No major deterministic concern triggered.

### #3 CAND_0055905 - Senior Machine Learning Engineer (0.9277)

Strong fit signal from Senior Machine Learning Engineer with 8.1 yrs: embeddings, fine-tuning, and inference; kubernetes, production, and python; evaluation, and feedback loop. availability 0.97, response 0.87. No major deterministic concern triggered.

### #4 CAND_0077337 - Staff Machine Learning Engineer (0.9233)

Strong fit signal from Staff Machine Learning Engineer with 7.0 yrs: embeddings, llm, and machine learning; production, and python; a/b test, and evaluation. availability 1.00, response 0.95. Concern: limited production engineering signal.

### #5 CAND_0055992 - AI Engineer (0.9156)

AI Engineer with 16.9 yrs; matched deep learning, embeddings, and fine-tuning with deployment, and production. Relevant role evidence: AI Engineer, and Senior Data Scientist. availability 0.98, response 0.72. Concern: limited production engineering signal.

### #6 CAND_0042506 - Search Engineer (0.9140)

Ranked for deep learning, embeddings, and fine-tuning plus airflow, deployment, and production; profile shows Search Engineer with 4.2 yrs. Relevant role evidence: Search Engineer, and Machine Learning Engineer. availability 0.92, response 0.48. No major deterministic concern triggered.

### #7 CAND_0043860 - Junior ML Engineer (0.9086)

Junior ML Engineer with 6.1 yrs; matched deep learning, inference, and llm with deployment, production, and python. Relevant role evidence: Junior ML Engineer, and Senior Software Engineer (ML). availability 1.00, response 0.81. No major deterministic concern triggered.

### #8 CAND_0037160 - Data Scientist (0.9085)

Data Scientist with 6.0 yrs; matched deep learning, embeddings, and inference with deployment, production, and python. Relevant role evidence: Data Scientist, and AI Specialist. availability 0.98, response 0.74. No major deterministic concern triggered.

### #9 CAND_0005649 - Senior Data Scientist (0.9081)

Strong fit signal from Senior Data Scientist with 7.4 yrs: deep learning, embeddings, and fine-tuning; deployment, microservices, and production; a/b test, and evaluation. availability 0.93, response 0.57. No major deterministic concern triggered.

### #10 CAND_0002025 - Senior AI Engineer (0.9054)

Strong fit signal from Senior AI Engineer with 5.9 yrs: deep learning, embeddings, and fine-tuning; kubernetes, production, and python; a/b test, and evaluation. availability 0.97, response 0.80. No major deterministic concern triggered.
