import streamlit as st
from collections import Counter
from pathlib import Path

from risk_engine import (
    default_engine,
    EvaluationContext,
    log_results,
)


# --- Page config --- #
st.set_page_config(
    page_title="AI Risk Navigator – Rule-Based LLM Risk Triage",
    layout="wide",
)

# --- Sidebar: screenshot + export --- #
screenshot_mode = st.sidebar.checkbox("🖼️ Screenshot Mode", value=False)

# Helper to read logs safely
logs_path = Path("logs/risks.jsonl")
if logs_path.exists():
    log_text = logs_path.read_text(encoding="utf-8")
    st.sidebar.download_button(
        label="⬇️ Download Logs (JSONL)",
        data=log_text,
        file_name="ai_risk_navigator_logs.jsonl",
        mime="application/json",
    )
else:
    st.sidebar.caption("No logs yet. Run an evaluation to generate logs.")

if screenshot_mode:
    st.markdown(
        """
        <style>
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        .stSidebar {background-color: #f8f9fa;}
        </style>
        """,
        unsafe_allow_html=True,
    )

st.title("🧭 AI Risk Navigator")
st.caption(
    "Deterministic, rule-based risk detection for LLM outputs "
    "(hallucination, bias, latency, safety)."
)

engine = default_engine()

# --- Input form --- #
with st.form("risk_form"):
    col1, col2 = st.columns(2)

    with col1:
        prompt = st.text_area(
            "LLM Prompt",
            height=180,
            placeholder="Enter the user prompt sent to the LLM...",
        )
        model_name = st.text_input("Model name (optional)", value="demo-model")

    with col2:
        response = st.text_area(
            "LLM Response",
            height=180,
            placeholder="Paste the LLM's response here...",
        )
        latency_ms = st.number_input(
            "Latency (ms, optional)",
            min_value=0.0,
            step=10.0,
            value=0.0,
        )

    source = st.text_input("Source (e.g., chat, api, batch)", value="dashboard")
    user_id = st.text_input("User ID (optional)", value="demo-user")

    submitted = st.form_submit_button("Run Risk Evaluation 🚦")

if submitted:
    if not response.strip():
        st.error("Please provide at least a response to evaluate.")
    else:
        ctx = EvaluationContext(
            prompt=prompt or "",
            response=response,
            latency_ms=latency_ms if latency_ms > 0 else None,
            model_name=model_name or None,
            user_id=user_id or None,
            source=source or None,
        )

        findings = engine.evaluate(ctx)
        log_results(ctx, findings)

        if not screenshot_mode:
            st.success("Evaluation complete. Logged to `logs/risks.jsonl`.")

        # --- Summary panel --- #
        if findings:
            st.markdown("### 📊 Risk Summary")
            severity_counts = Counter(f.severity.value for f in findings)
            type_counts = Counter(f.risk_type.value for f in findings)

            sev_labels = ["critical", "high", "medium", "low"]
            cols = st.columns(4)
            for col, label in zip(cols, sev_labels):
                col.metric(label.capitalize(), severity_counts.get(label, 0))

            if not screenshot_mode:
                st.caption("Counts are per evaluation; full logs are in `logs/risks.jsonl`.")

            st.markdown("#### By risk type")
            tcols = st.columns(len(type_counts) or 1)
            for (rtype, count), col in zip(type_counts.items(), tcols):
                col.metric(rtype.capitalize(), count)

        # --- Detailed results --- #
        if not findings:
            st.markdown("### ✅ No risks detected")
        else:
            st.markdown("### ⚠️ Detailed Risks")
            for f in findings:
                with st.container(border=True):
                    st.markdown(
                        f"**[{f.risk_type.value.upper()}] "
                        f"{f.severity.value.upper()} – {f.rule_id}**"
                    )
                    st.write(f.message)
                    if f.metadata and not screenshot_mode:
                        st.caption("Metadata:")
                        st.json(f.metadata)

        # --- Raw JSON (hidden in screenshot mode) --- #
        if not screenshot_mode:
            st.divider()
            st.markdown("#### Raw JSON record (for debugging/export)")
            st.json(
                {
                    "prompt": ctx.prompt,
                    "response": ctx.response,
                    "latency_ms": ctx.latency_ms,
                    "model_name": ctx.model_name,
                    "user_id": ctx.user_id,
                    "source": ctx.source,
                    "findings": [f.model_dump() for f in findings],
                }
            )
