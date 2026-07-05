"""
app.py — Streamlit interface for the AI Estimator (painting).
A thin layer over the Week 3 core function (estimate_from_text).
Run with:  streamlit run code/app.py
"""

import json
import os
import streamlit as st

st.set_page_config(page_title="AI Estimator", page_icon="🎨", layout="wide")

st.title("🎨 AI Estimator — Painting Jobs")
st.write(
    "Paste a painting job description below and click **Estimate**. "
    "The tool returns an itemized cost estimate with a grand total. "
    "Fields it can't determine are flagged for review."
)

SAMPLE_DIR = "sample_data"
sample_files = []
if os.path.isdir(SAMPLE_DIR):
    sample_files = sorted(f for f in os.listdir(SAMPLE_DIR) if f.endswith(".txt"))

col_pick, _ = st.columns([1, 2])
with col_pick:
    chosen = st.selectbox(
        "Or load a sample document:",
        ["— none —"] + sample_files,
    )

default_text = ""
if chosen and chosen != "— none —":
    with open(os.path.join(SAMPLE_DIR, chosen), "r") as f:
        default_text = f.read()

left, right = st.columns(2)

with left:
    st.subheader("Job description")
    job_text = st.text_area("Job description", value=default_text, height=400)
    run = st.button("Estimate")

with right:
    st.subheader("Estimate")

    if run:
        if not job_text.strip():
            st.warning("Please paste a job description or load a sample first.")
        else:
            try:
                from estimator import estimate_from_text

                with st.spinner("Estimating..."):
                    result = estimate_from_text(job_text)

                estimate = result["estimate"]
                problems = result["problems"]

                if estimate is None:
                    st.error("The tool couldn't produce a valid estimate for this input.")
                    for p in problems:
                        st.write(f"• {p}")
                else:
                    st.markdown(f"**{estimate.get('job_title', 'Untitled job')}**")

                    rows = []
                    for item in estimate.get("line_items", []):
                        def show(v):
                            return "— not found —" if v is None else v
                        rows.append({
                            "Task": show(item.get("task")),
                            "Category": show(item.get("category")),
                            "Qty": show(item.get("quantity")),
                            "Unit": show(item.get("unit")),
                            "Unit price": show(item.get("unit_price")),
                            "Line total": show(item.get("line_total")),
                        })
                    st.table(rows)

                    gt = estimate.get("grand_total")
                    st.markdown(f"### Grand total: {'— not found —' if gt is None else f'${gt:,.2f}'}")

                    if estimate.get("notes"):
                        st.info(f"Notes: {estimate['notes']}")

                    if problems:
                        st.warning("Some fields need a human review:")
                        for p in problems:
                            st.write(f"• {p}")
                    else:
                        st.success("All fields present and the math checks out.")

            except Exception as e:
                st.error(
                    "Couldn't run the estimator. This usually means the API key "
                    "isn't set yet. Once a valid key is in your .env, this will work."
                )
                st.caption(f"Technical detail: {e}")
    else:
        st.caption("Your estimate will appear here.")