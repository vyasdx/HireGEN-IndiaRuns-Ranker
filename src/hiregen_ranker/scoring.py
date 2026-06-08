"""Deterministic baseline scoring for Senior AI Engineer candidate ranking."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


AI_TERMS = {
    "ai",
    "machine learning",
    "ml",
    "llm",
    "genai",
    "generative ai",
    "deep learning",
    "nlp",
    "computer vision",
    "fine-tuning",
    "embeddings",
    "rag",
    "retrieval",
    "ranking",
    "recommender",
    "recommendation",
    "search",
    "vector",
    "semantic",
    "model",
    "inference",
}

ENGINEERING_TERMS = {
    "python",
    "backend",
    "api",
    "microservices",
    "distributed",
    "production",
    "deployment",
    "docker",
    "kubernetes",
    "cloud",
    "aws",
    "azure",
    "gcp",
    "data pipeline",
    "spark",
    "airflow",
}

EVALUATION_TERMS = {
    "evaluation",
    "benchmark",
    "ab test",
    "a/b test",
    "ndcg",
    "mrr",
    "map",
    "metrics",
    "feedback loop",
}

TITLE_TERMS = {
    "ai engineer",
    "machine learning engineer",
    "ml engineer",
    "data scientist",
    "data engineer",
    "backend engineer",
    "software engineer",
    "full stack developer",
    "search engineer",
    "ranking engineer",
    "recommendation systems engineer",
    "platform engineer",
    "devops engineer",
    "cloud engineer",
}

WEAK_TITLE_TERMS = {
    "business analyst",
    "hr manager",
    "marketing manager",
    "project manager",
    "operations manager",
    "graphic designer",
    "content writer",
    "mechanical engineer",
    "sales",
    "recruiter",
}

STRONG_AI_TERMS = {
    "machine learning",
    "ml",
    "llm",
    "deep learning",
    "fine-tuning",
    "embeddings",
    "rag",
    "retrieval",
    "ranking",
    "recommender",
    "recommendation",
    "search",
    "vector",
    "semantic",
    "inference",
}


@dataclass(frozen=True)
class ScoreDetails:
    candidate_id: str
    score: float
    role_fit_score: float
    direct_evidence_score: float
    availability_multiplier: float
    penalty_score: float
    recency_score: float
    reasoning: str


@dataclass(frozen=True)
class EvidenceBundle:
    direct_ai_terms: tuple[str, ...]
    engineering_terms: tuple[str, ...]
    evaluation_terms: tuple[str, ...]
    evidence_titles: tuple[str, ...]
    concern_labels: tuple[str, ...]


def score_candidate(candidate: dict[str, Any]) -> ScoreDetails:
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    skills = candidate.get("skills", [])
    career_history = candidate.get("career_history", [])

    candidate_id = str(candidate.get("candidate_id", ""))
    title = str(profile.get("current_title", "Unknown role"))
    years = float(profile.get("years_of_experience") or 0)
    text = _candidate_text(candidate)
    technical_text = _technical_text(candidate)

    ai_hits = _count_hits(text, AI_TERMS)
    strong_ai_hits = _count_hits(text, STRONG_AI_TERMS)
    technical_ai_hits = _count_hits(technical_text, STRONG_AI_TERMS)
    engineering_hits = _count_hits(text, ENGINEERING_TERMS)
    evaluation_hits = _count_hits(text, EVALUATION_TERMS)
    title_hits = _count_hits(title.lower(), TITLE_TERMS)
    weak_title_hits = _count_hits(title.lower(), WEAK_TITLE_TERMS)
    title_multiplier = _title_multiplier(title)
    skill_strength = _skill_strength(skills)
    production_evidence = _career_evidence(career_history)
    experience_fit = _experience_fit(years)
    jd_intent_score = _jd_intent_score(
        strong_ai_hits=strong_ai_hits,
        technical_ai_hits=technical_ai_hits,
        engineering_hits=engineering_hits,
        evaluation_hits=evaluation_hits,
        title_hits=title_hits,
        production_evidence=production_evidence,
    )

    role_fit_score = (
        8.0
        + jd_intent_score
        + strong_ai_hits * 3.0
        + technical_ai_hits * 4.0
        + engineering_hits * 1.8
        + evaluation_hits * 3.0
        + title_hits * 9.0
        + skill_strength
        + production_evidence
        + experience_fit
    )

    direct_evidence_score = (
        technical_ai_hits * 10.0
        + strong_ai_hits * 4.0
        + engineering_hits * 2.5
        + evaluation_hits * 4.0
        + production_evidence
    )
    availability_multiplier = _availability_multiplier(signals)
    penalty_score = _penalty_score(
        candidate,
        ai_hits=ai_hits,
        strong_ai_hits=strong_ai_hits,
        technical_ai_hits=technical_ai_hits,
        engineering_hits=engineering_hits,
        weak_title_hits=weak_title_hits,
        role_fit_score=role_fit_score,
    )
    recency_score = _recency_score(signals)
    evidence = _evidence_bundle(
        candidate,
        strong_ai_hits=strong_ai_hits,
        technical_ai_hits=technical_ai_hits,
        engineering_hits=engineering_hits,
        evaluation_hits=evaluation_hits,
        title_multiplier=title_multiplier,
        penalty_score=penalty_score,
    )

    raw_final_score = max(
        0.0,
        role_fit_score * availability_multiplier * title_multiplier - penalty_score,
    )
    final_score = min(0.9999, 1.0 - math.exp(-raw_final_score / 75.0))

    reasoning = _reasoning(
        candidate_id=candidate_id,
        title=title,
        years=years,
        ai_hits=strong_ai_hits,
        technical_ai_hits=technical_ai_hits,
        engineering_hits=engineering_hits,
        evaluation_hits=evaluation_hits,
        availability_multiplier=availability_multiplier,
        title_multiplier=title_multiplier,
        penalty_score=penalty_score,
        signals=signals,
        evidence=evidence,
    )

    return ScoreDetails(
        candidate_id=candidate_id,
        score=round(final_score, 4),
        role_fit_score=round(role_fit_score, 4),
        direct_evidence_score=round(direct_evidence_score, 4),
        availability_multiplier=round(availability_multiplier, 4),
        penalty_score=round(penalty_score, 4),
        recency_score=round(recency_score, 4),
        reasoning=reasoning,
    )


def _candidate_text(candidate: dict[str, Any]) -> str:
    profile = candidate.get("profile", {})
    chunks: list[str] = [
        str(profile.get("headline", "")),
        str(profile.get("summary", "")),
        str(profile.get("current_title", "")),
        str(profile.get("current_industry", "")),
    ]

    for item in candidate.get("career_history", []):
        chunks.append(str(item.get("title", "")))
        chunks.append(str(item.get("description", "")))
        chunks.append(str(item.get("industry", "")))

    for skill in candidate.get("skills", []):
        chunks.append(str(skill.get("name", "")))

    for cert in candidate.get("certifications", []):
        chunks.append(str(cert))

    return " ".join(chunks).lower()


def _technical_text(candidate: dict[str, Any]) -> str:
    chunks: list[str] = []
    for item in candidate.get("career_history", []):
        chunks.append(str(item.get("title", "")))
        chunks.append(str(item.get("description", "")))
    for skill in candidate.get("skills", []):
        chunks.append(str(skill.get("name", "")))
    return " ".join(chunks).lower()


def _count_hits(text: str, terms: set[str]) -> int:
    return sum(1 for term in terms if term in text)


def _jd_intent_score(
    *,
    strong_ai_hits: int,
    technical_ai_hits: int,
    engineering_hits: int,
    evaluation_hits: int,
    title_hits: int,
    production_evidence: float,
) -> float:
    score = 0.0
    if title_hits:
        score += 10.0
    if technical_ai_hits >= 2:
        score += 15.0
    elif technical_ai_hits == 1:
        score += 7.0
    if engineering_hits >= 4:
        score += 12.0
    elif engineering_hits >= 2:
        score += 6.0
    if strong_ai_hits >= 4 and engineering_hits >= 3:
        score += 10.0
    if evaluation_hits:
        score += 6.0
    if production_evidence >= 8.0:
        score += 8.0
    return min(35.0, score)


def _skill_strength(skills: list[dict[str, Any]]) -> float:
    score = 0.0
    for skill in skills:
        name = str(skill.get("name", "")).lower()
        proficiency = _proficiency_value(skill.get("proficiency"))
        duration_months = float(skill.get("duration_months") or 0)
        if any(term in name for term in AI_TERMS | ENGINEERING_TERMS | EVALUATION_TERMS):
            score += min(6.0, proficiency * 0.05 + duration_months * 0.02)
    return min(18.0, score)


def _proficiency_value(value: Any) -> float:
    if isinstance(value, int | float):
        return float(value)

    label = str(value or "").strip().lower()
    mapping = {
        "beginner": 25.0,
        "novice": 25.0,
        "intermediate": 55.0,
        "advanced": 75.0,
        "expert": 90.0,
    }
    return mapping.get(label, 0.0)


def _career_evidence(career_history: list[dict[str, Any]]) -> float:
    score = 0.0
    for role in career_history:
        description = str(role.get("description", "")).lower()
        title = str(role.get("title", "")).lower()
        if any(term in title for term in TITLE_TERMS):
            score += 4.0
        if "production" in description or "deployed" in description or "built" in description:
            score += 3.0
        if "ranking" in description or "retrieval" in description or "search" in description:
            score += 4.0
        if "feedback" in description or "evaluation" in description or "benchmark" in description:
            score += 3.0
    return min(18.0, score)


def _experience_fit(years: float) -> float:
    if 5.0 <= years <= 9.0:
        return 10.0
    if 3.5 <= years < 5.0 or 9.0 < years <= 12.0:
        return 7.0
    if 2.0 <= years < 3.5 or 12.0 < years <= 16.0:
        return 4.0
    return 1.5


def _title_multiplier(title: str) -> float:
    title_text = title.lower()
    top_titles = {
        "ai engineer",
        "machine learning engineer",
        "ml engineer",
        "recommendation systems engineer",
        "search engineer",
        "ranking engineer",
        "data scientist",
    }
    strong_engineering_titles = {
        "backend engineer",
        "software engineer",
        "data engineer",
        "platform engineer",
        "cloud engineer",
        "devops engineer",
        "full stack developer",
    }
    adjacent_engineering_titles = {
        ".net developer",
        "java developer",
        "frontend engineer",
        "mobile developer",
    }

    if any(term in title_text for term in top_titles):
        return 1.0
    if any(term in title_text for term in strong_engineering_titles):
        return 0.94
    if any(term in title_text for term in adjacent_engineering_titles):
        return 0.80
    if any(term in title_text for term in WEAK_TITLE_TERMS):
        return 0.52
    if "engineer" in title_text or "developer" in title_text:
        return 0.74
    return 0.62


def _availability_multiplier(signals: dict[str, Any]) -> float:
    response_rate = float(signals.get("recruiter_response_rate") or 0)
    interview_rate = float(signals.get("interview_completion_rate") or 0)
    open_to_work = bool(signals.get("open_to_work_flag"))
    notice_days = float(signals.get("notice_period_days") or 90)
    last_active = str(signals.get("last_active_date", ""))
    willing_to_relocate = bool(signals.get("willing_to_relocate"))

    multiplier = 0.58
    multiplier += min(0.18, response_rate * 0.18)
    multiplier += min(0.10, interview_rate * 0.10)
    multiplier += 0.08 if open_to_work else 0.0
    multiplier += 0.05 if notice_days <= 30 else 0.02 if notice_days <= 60 else 0.0
    multiplier += 0.04 if willing_to_relocate else 0.0
    multiplier += 0.04 if last_active.startswith("2026") else 0.01 if last_active.startswith("2025") else 0.0
    return min(1.0, max(0.35, multiplier))


def _penalty_score(
    candidate: dict[str, Any],
    *,
    ai_hits: int,
    strong_ai_hits: int,
    technical_ai_hits: int,
    engineering_hits: int,
    weak_title_hits: int,
    role_fit_score: float,
) -> float:
    profile = candidate.get("profile", {})
    years = float(profile.get("years_of_experience") or 0)
    skills = candidate.get("skills", [])
    text = _candidate_text(candidate)

    penalty = 0.0
    if role_fit_score > 80 and years < 2:
        penalty += 12.0
    if ai_hits >= 10 and engineering_hits <= 1:
        penalty += 8.0
    if strong_ai_hits >= 4 and technical_ai_hits == 0:
        penalty += 14.0
    if weak_title_hits and technical_ai_hits <= 1:
        penalty += 20.0
    if weak_title_hits and engineering_hits <= 4:
        penalty += 10.0
    if role_fit_score > 70 and technical_ai_hits == 0:
        penalty += 10.0
    if role_fit_score > 65 and engineering_hits < 2:
        penalty += 8.0
    if len(skills) > 35:
        penalty += 4.0
    if text.count("expert") >= 8 and years < 5:
        penalty += 7.0
    if "research" in text and "production" not in text and "deployed" not in text:
        penalty += 5.0
    return min(25.0, penalty)


def _recency_score(signals: dict[str, Any]) -> float:
    last_active = str(signals.get("last_active_date", ""))
    if last_active.startswith("2026"):
        return 1.0
    if last_active.startswith("2025"):
        return 0.7
    return 0.3


def _evidence_bundle(
    candidate: dict[str, Any],
    *,
    strong_ai_hits: int,
    technical_ai_hits: int,
    engineering_hits: int,
    evaluation_hits: int,
    title_multiplier: float,
    penalty_score: float,
) -> EvidenceBundle:
    technical_text = _technical_text(candidate)
    full_text = _candidate_text(candidate)
    direct_ai_terms = _matched_terms(technical_text, STRONG_AI_TERMS, limit=3)
    engineering_terms = _matched_terms(full_text, ENGINEERING_TERMS, limit=3)
    evaluation_terms = _matched_terms(full_text, EVALUATION_TERMS, limit=2)
    evidence_titles = _evidence_titles(candidate.get("career_history", []), limit=2)

    concern_labels: list[str] = []
    if technical_ai_hits == 0 and strong_ai_hits:
        concern_labels.append("AI terms are not backed by technical role evidence")
    if title_multiplier < 0.7:
        concern_labels.append("current title is not a close AI engineering fit")
    elif title_multiplier < 0.9:
        concern_labels.append("title is adjacent but not core AI")
    if engineering_hits < 3:
        concern_labels.append("limited production engineering signal")
    if evaluation_hits == 0:
        concern_labels.append("evaluation/benchmark signal is missing")
    if penalty_score:
        concern_labels.append("penalty applied for unsupported or weak-fit signals")

    return EvidenceBundle(
        direct_ai_terms=direct_ai_terms,
        engineering_terms=engineering_terms,
        evaluation_terms=evaluation_terms,
        evidence_titles=evidence_titles,
        concern_labels=tuple(concern_labels[:2]),
    )


def _matched_terms(text: str, terms: set[str], *, limit: int) -> tuple[str, ...]:
    matches = sorted(term for term in terms if term in text)
    return tuple(matches[:limit])


def _evidence_titles(career_history: list[dict[str, Any]], *, limit: int) -> tuple[str, ...]:
    titles: list[str] = []
    for role in career_history:
        title = str(role.get("title", "")).strip()
        description = str(role.get("description", "")).lower()
        if title and (
            any(term in title.lower() for term in TITLE_TERMS)
            or any(term in description for term in STRONG_AI_TERMS | ENGINEERING_TERMS | EVALUATION_TERMS)
        ):
            titles.append(title)
    deduped: list[str] = []
    for title in titles:
        if title not in deduped:
            deduped.append(title)
    return tuple(deduped[:limit])


def _reasoning(
    *,
    candidate_id: str,
    title: str,
    years: float,
    ai_hits: int,
    technical_ai_hits: int,
    engineering_hits: int,
    evaluation_hits: int,
    availability_multiplier: float,
    title_multiplier: float,
    penalty_score: float,
    signals: dict[str, Any],
    evidence: EvidenceBundle,
) -> str:
    response_rate = float(signals.get("recruiter_response_rate") or 0)
    title_note = f"{title} with {years:.1f} yrs"
    ai_note = _terms_note(evidence.direct_ai_terms, fallback=f"{technical_ai_hits} direct AI/retrieval signals")
    eng_note = _terms_note(evidence.engineering_terms, fallback=f"{engineering_hits} engineering signals")
    eval_note = _terms_note(
        evidence.evaluation_terms,
        fallback="no evaluation evidence found" if evaluation_hits == 0 else f"{evaluation_hits} evaluation signals",
    )
    career_note = _career_note(evidence.evidence_titles)
    availability_note = f"availability {availability_multiplier:.2f}, response {response_rate:.2f}"
    concern_note = _concern_note(evidence.concern_labels, title_multiplier, penalty_score)

    variant = _candidate_number(candidate_id) % 4
    if variant == 0:
        return (
            f"{title_note}; matched {ai_note} with {eng_note}. "
            f"{career_note} {availability_note}. {concern_note}"
        ).strip()
    if variant == 1:
        return (
            f"Strong fit signal from {title_note}: {ai_note}; {eng_note}; {eval_note}. "
            f"{availability_note}. {concern_note}"
        ).strip()
    if variant == 2:
        return (
            f"Ranked for {ai_note} plus {eng_note}; profile shows {title_note}. "
            f"{career_note} {availability_note}. {concern_note}"
        ).strip()
    return (
        f"{title_note}; evidence includes {ai_note}. "
        f"Engineering/recruiter signals: {eng_note}; {availability_note}. {concern_note}"
    ).strip()


def _terms_note(terms: tuple[str, ...], *, fallback: str) -> str:
    if not terms:
        return fallback
    if len(terms) == 1:
        return terms[0]
    return ", ".join(terms[:-1]) + f", and {terms[-1]}"


def _career_note(titles: tuple[str, ...]) -> str:
    if not titles:
        return "Career history provides limited direct title evidence."
    return f"Relevant role evidence: {_terms_note(titles, fallback='career history')}."


def _concern_note(labels: tuple[str, ...], title_multiplier: float, penalty_score: float) -> str:
    concerns = list(labels)
    if title_multiplier < 0.9 and not any("title" in item for item in concerns):
        concerns.append(f"title fit {title_multiplier:.2f}")
    if penalty_score and not any("penalty" in item for item in concerns):
        concerns.append(f"penalty {penalty_score:.0f}")

    if not concerns:
        return "No major deterministic concern triggered."
    return "Concern: " + "; ".join(concerns[:2]) + "."


def _candidate_number(candidate_id: str) -> int:
    try:
        return int(candidate_id.rsplit("_", 1)[1])
    except (IndexError, ValueError):
        return 0
