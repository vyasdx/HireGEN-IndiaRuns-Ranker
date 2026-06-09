from __future__ import annotations

import csv
import sys
import tempfile
from pathlib import Path
from typing import Any

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hiregen_ranker.io import iter_candidates  # noqa: E402
from hiregen_ranker.ranker import rank_candidates, write_submission  # noqa: E402
from hiregen_ranker.reporting import build_report  # noqa: E402


SAMPLE_PATH = ROOT / "data" / "official" / "sample_candidates.json"
OUTPUT_DIR = ROOT / "outputs"


st.set_page_config(
    page_title="HireGEN Ranker Demo",
    page_icon="H",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    _css()
    _hero()

    with st.sidebar:
        st.markdown("### Run settings")
        source_mode = st.radio(
            "Candidate data",
            ["Official sample", "Upload JSON/JSONL"],
            index=0,
            key="source_mode",
            on_change=_clear_demo_result,
        )
        limit = st.slider(
            "Candidates to rank",
            min_value=10,
            max_value=100,
            value=50,
            step=10,
            key="candidate_limit",
            on_change=_clear_demo_result,
        )
        uploaded = None
        if source_mode == "Upload JSON/JSONL":
            uploaded = st.file_uploader(
                "Upload candidate JSON or JSONL",
                type=["json", "jsonl"],
                key="candidate_upload",
                on_change=_clear_demo_result,
            )

        st.markdown("---")
        st.caption("Official rank-time path stays CPU-only, deterministic, and network-free.")
        run = st.button("Run HireGEN Ranker", type="primary", use_container_width=True)

    input_path = _input_path(source_mode, uploaded)
    if input_path is None:
        _empty_state()
        return

    run_key = _run_key(source_mode, uploaded, limit)
    previous_key = st.session_state.get("demo_result", {}).get("run_key")
    if previous_key and previous_key != run_key:
        st.session_state.pop("demo_result", None)

    if run:
        with st.spinner("Ranking candidates with deterministic proof signals..."):
            result = _run_demo(input_path, limit)
            result["run_key"] = run_key
            st.session_state["demo_result"] = result

    if "demo_result" not in st.session_state:
        _ready_state(source_mode, uploaded, limit)
        return

    _render_result(st.session_state["demo_result"])


def _clear_demo_result() -> None:
    st.session_state.pop("demo_result", None)


def _hero() -> None:
    st.markdown(
        """
        <section class="hero">
          <div>
            <div class="eyebrow">HireGEN IndiaRuns Ranker · Judge Demo</div>
            <h1>Candidate discovery that shows its work.</h1>
            <p>
              Upload candidate data, run the offline ranker, and inspect a shortlist by score tiers,
              evidence coverage, deterministic controls, and grounded candidate reasoning.
            </p>
          </div>
          <div class="hero-card">
            <span>CPU-only</span>
            <span>No LLM at rank time</span>
            <span>Explainable top 100</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _empty_state() -> None:
    st.info("Upload a candidate JSON/JSONL file to run the demo.")


def _ready_state(source_mode: str, uploaded: Any, limit: int) -> None:
    file_name = uploaded.name if uploaded is not None else "official sample"
    st.markdown(
        f"""
        <div class="ready-card">
          <strong>Ready to rank</strong>
          <p>Source: {source_mode} · File: {file_name} · Output limit: {limit}</p>
          <span>Click <b>Run HireGEN Ranker</b> to generate the executive proof checks and shortlist.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _run_key(source_mode: str, uploaded: Any, limit: int) -> tuple[str, str, int, int]:
    if uploaded is None:
        return (source_mode, "official-sample", 0, limit)
    return (source_mode, uploaded.name, len(uploaded.getvalue()), limit)


def _input_path(source_mode: str, uploaded: Any) -> Path | None:
    if source_mode == "Official sample":
        return SAMPLE_PATH
    if uploaded is None:
        return None

    suffix = ".jsonl" if uploaded.name.endswith(".jsonl") else ".json"
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp.write(uploaded.getvalue())
    temp.flush()
    temp.close()
    return Path(temp.name)


def _run_demo(input_path: Path, limit: int) -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "demo_submission.csv"
    ranked, seen, elapsed = rank_candidates(input_path, limit=limit)
    write_submission(ranked, output_path)
    report = build_report(submission_path=output_path, candidates_path=input_path, runtime_seconds=elapsed)
    rows = _enriched_rows(output_path, input_path)
    return {
        "input_path": str(input_path),
        "output_path": str(output_path),
        "seen": seen,
        "elapsed": elapsed,
        "report": report,
        "rows": rows,
    }


def _render_result(result: dict[str, Any]) -> None:
    report = result["report"]
    summary = report["summary"]
    controls = report["control_checks"]
    separation = report["top_10_score_separation"]

    st.markdown("### Executive proof checks")
    cols = st.columns(5)
    cols[0].metric("Ranked", summary["candidate_count"])
    cols[1].metric("Runtime", f"{result['elapsed']:.2f}s")
    cols[2].metric("Non-eng top 10", controls["top_10_non_engineering_count"])
    cols[3].metric("AI-title count", controls["top_100_ai_title_count"])
    cols[4].metric("Top-10 spread", separation["spread"])
    st.caption(
        "Runtime scans the full uploaded file to find the best candidates. Top-10 spread stays the same across 10/20/30 outputs if the top 10 candidates are unchanged."
    )

    st.markdown(
        f"""
        <div class="hash-card">
          <strong>CSV fingerprint</strong>
          <code>{summary["submission_sha256"]}</code>
          <span>
            This is a SHA-256 fingerprint of the generated CSV. If the same data and code are run again,
            this number should remain identical.
          </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["Shortlist tiers", "Evidence coverage", "Risk controls", "Top 10 reasoning", "Raw output"])

    with tabs[0]:
        _tier_view(result["rows"])

    with tabs[1]:
        _coverage_view(report)

    with tabs[2]:
        _controls_view(report)

    with tabs[3]:
        _reasoning_view(report)

    with tabs[4]:
        st.dataframe(result["rows"], use_container_width=True, hide_index=True)
        st.markdown('<div class="download-wrap">', unsafe_allow_html=True)
        st.download_button(
            "Download demo CSV",
            data=Path(result["output_path"]).read_text(encoding="utf-8"),
            file_name="hiregen_ranker_demo_submission.csv",
            mime="text/csv",
            use_container_width=False,
        )
        st.markdown("</div>", unsafe_allow_html=True)


def _tier_view(rows: list[dict[str, Any]]) -> None:
    tiers = [
        ("Tier 1", "Interview now", rows[:10], "Best direct fit and strongest evidence."),
        ("Tier 2", "Recruiter review", rows[10:30], "Good fit; compare compensation, location, or evidence gaps."),
        ("Tier 3", "Bench", rows[30:], "Worth keeping warm for backup outreach or future roles."),
    ]
    columns = st.columns(3)
    for column, (tier, label, tier_rows, note) in zip(columns, tiers):
        with column:
            st.markdown(f"#### {tier}: {label}")
            st.caption(note)
            for row in tier_rows[:12]:
                st.markdown(
                    f"""
                    <div class="candidate-card">
                      <div class="rank">#{row["rank"]} · {row["score"]:.4f}</div>
                      <h4>{row["title"] or "Unknown title"}</h4>
                      <p>{row["candidate_id"]} · {row["experience"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def _coverage_view(report: dict[str, Any]) -> None:
    coverage_rows = [
        {"signal": signal, "count": values["count"], "coverage": f"{values['coverage_pct']}%"}
        for signal, values in report["evidence_coverage"].items()
    ]
    left, right = st.columns([1, 1])
    with left:
        st.markdown("#### Evidence coverage")
        st.dataframe(coverage_rows, use_container_width=True, hide_index=True)
    with right:
        st.markdown("#### Score bands")
        st.dataframe(
            [{"band": band, "count": count} for band, count in report["score_bands"].items()],
            use_container_width=True,
            hide_index=True,
        )


def _controls_view(report: dict[str, Any]) -> None:
    controls = report["control_checks"]
    cols = st.columns(4)
    cols[0].metric("Non-eng top 10", controls["top_10_non_engineering_count"])
    cols[1].metric("Engineering top 100", controls["top_100_engineering_title_count"])
    cols[2].metric("AI-title top 100", controls["top_100_ai_title_count"])
    cols[3].metric("Weak-fit concerns", controls["honeypot_or_weak_fit_concern_count"])

    st.markdown("#### Deterministic concern counts")
    st.dataframe(
        [{"concern": concern, "count": count} for concern, count in report["concerns"]],
        use_container_width=True,
        hide_index=True,
    )


def _reasoning_view(report: dict[str, Any]) -> None:
    for item in report["top_10"]:
        title = item["title"] or "Unknown title"
        st.markdown(
            f"""
            <div class="reason-card">
              <div class="rank">#{item["rank"]} · {item["candidate_id"]} · {item["score"]:.4f}</div>
              <h4>{title}</h4>
              <p>{item["reasoning"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _enriched_rows(submission_path: Path, candidates_path: Path) -> list[dict[str, Any]]:
    candidate_ids: set[str] = set()
    with submission_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
        candidate_ids = {row["candidate_id"] for row in rows}

    lookup = {}
    for candidate in iter_candidates(candidates_path):
        candidate_id = str(candidate.get("candidate_id", ""))
        if candidate_id in candidate_ids:
            lookup[candidate_id] = candidate
        if len(lookup) == len(candidate_ids):
            break

    enriched = []
    for row in rows:
        profile = lookup.get(row["candidate_id"], {}).get("profile", {})
        years = profile.get("years_of_experience")
        enriched.append(
            {
                "rank": int(row["rank"]),
                "candidate_id": row["candidate_id"],
                "score": float(row["score"]),
                "title": str(profile.get("current_title", "")),
                "location": str(profile.get("location", "")),
                "experience": f"{years} yrs" if years is not None else "unknown exp",
                "reasoning": row["reasoning"],
            }
        )
    return enriched


def _css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
          background:
            radial-gradient(circle at 18% 12%, rgba(64, 158, 255, .28), transparent 32%),
            radial-gradient(circle at 86% 22%, rgba(126, 87, 255, .18), transparent 28%),
            linear-gradient(135deg, #f7fbff 0%, #eaf4ff 44%, #f9fbff 100%);
          color: #111827;
        }
        [data-testid="stMetric"] {
          padding: 16px 18px;
          border-radius: 18px;
          background: rgba(255,255,255,.78);
          border: 1px solid rgba(255,255,255,.9);
          box-shadow: 0 14px 34px rgba(32, 84, 142, .10);
        }
        [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] p {
          color: #475569 !important;
          font-weight: 800 !important;
        }
        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] div {
          color: #111827 !important;
          font-weight: 900 !important;
        }
        [data-testid="stMetricDelta"] {
          color: #4338ca !important;
        }
        .stTabs [data-baseweb="tab-list"] {
          gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
          color: #334155 !important;
          font-weight: 800;
        }
        .stTabs [aria-selected="true"] {
          color: #4338ca !important;
          background: rgba(255,255,255,.72);
          border-radius: 999px;
        }
        .hero {
          display: flex;
          justify-content: space-between;
          gap: 24px;
          padding: 28px 30px;
          border: 1px solid rgba(255,255,255,.85);
          border-radius: 28px;
          background: rgba(255,255,255,.62);
          box-shadow: 0 24px 70px rgba(32, 84, 142, .16);
          backdrop-filter: blur(18px);
          margin-bottom: 20px;
        }
        .eyebrow {
          color: #4438ca;
          font-size: 13px;
          font-weight: 800;
          letter-spacing: .04em;
          text-transform: uppercase;
          margin-bottom: 8px;
        }
        .hero h1 {
          font-size: clamp(34px, 5vw, 66px);
          line-height: .96;
          margin: 0 0 14px;
          letter-spacing: 0;
        }
        .hero p {
          max-width: 780px;
          color: #40516d;
          font-size: 19px;
          line-height: 1.55;
        }
        .hero-card {
          min-width: 230px;
          align-self: center;
          display: grid;
          gap: 10px;
        }
        .hero-card span, .hash-card, .ready-card {
          border: 1px solid rgba(255,255,255,.88);
          border-radius: 18px;
          background: rgba(255,255,255,.72);
          box-shadow: 0 16px 42px rgba(32, 84, 142, .12);
        }
        .hero-card span {
          padding: 12px 14px;
          font-weight: 800;
          color: #172033;
        }
        .hash-card, .ready-card {
          padding: 16px 18px;
          margin: 12px 0 22px;
        }
        .ready-card strong {
          color: #111827;
          font-size: 18px;
        }
        .ready-card p {
          color: #334155;
          margin: 8px 0;
          font-weight: 700;
        }
        .ready-card span {
          color: #52657f;
        }
        .hash-card code {
          display: block;
          color: #4438ca;
          white-space: normal;
          overflow-wrap: anywhere;
          margin: 5px 0;
        }
        .hash-card span {
          color: #5b6b83;
          font-size: 14px;
        }
        .candidate-card, .reason-card {
          padding: 14px 16px;
          border-radius: 18px;
          background: rgba(255,255,255,.72);
          border: 1px solid rgba(255,255,255,.9);
          box-shadow: 0 16px 42px rgba(32, 84, 142, .10);
          margin-bottom: 12px;
        }
        .candidate-card h4, .reason-card h4 {
          margin: 4px 0 6px;
          font-size: 17px;
        }
        .candidate-card p, .reason-card p {
          margin: 0;
          color: #55657f;
          font-size: 14px;
          line-height: 1.45;
        }
        .rank {
          color: #4338ca;
          font-weight: 900;
          font-size: 13px;
        }
        .download-wrap div[data-testid="stDownloadButton"] button,
        div[data-testid="stDownloadButton"] button {
          background: #111827 !important;
          color: #ffffff !important;
          border: 1px solid rgba(255,255,255,.25) !important;
          border-radius: 12px !important;
          font-weight: 900 !important;
          box-shadow: 0 16px 34px rgba(17,24,39,.22);
        }
        div[data-testid="stDownloadButton"] button p,
        div[data-testid="stDownloadButton"] button span {
          color: #ffffff !important;
        }
        @media (max-width: 900px) {
          .hero { display: block; }
          .hero-card { margin-top: 18px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
