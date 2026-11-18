import json
import streamlit as st
from app.decision import build_decision_report, DecisionError

st.set_page_config(page_title="AI Decision Support Agent", layout="wide")
st.title("AI Decision Support Agent")
st.caption("Compare options using transparent weighted scoring, then ask a local LLM to explain trade-offs.")

problem = st.text_input("Decision problem", "Choose a project management tool for a small team")
options_text = st.text_area("Options (one per line)", "Tool A\nTool B\nTool C")
criteria_text = st.text_area(
    "Criteria and weights (one per line: criterion,weight)",
    "Cost,30\nEase of use,25\nFeatures,25\nPrivacy,20"
)
context = st.text_area("Additional context (optional)", "")
use_llm = st.toggle("Use local Ollama for explanation", value=True)

def parse_lines():
    options = [x.strip() for x in options_text.splitlines() if x.strip()]
    criteria = []
    for line in criteria_text.splitlines():
        if not line.strip():
            continue
        parts = line.rsplit(",", 1)
        if len(parts) != 2:
            raise DecisionError("Criteria format must be: criterion,weight")
        criteria.append({"name": parts[0].strip(), "weight": float(parts[1].strip())})
    return options, criteria

if st.button("Continue to ratings"):
    try:
        options, criteria = parse_lines()
        st.session_state["options"] = options
        st.session_state["criteria"] = criteria
        st.session_state["problem"] = problem
        st.success("Options and criteria loaded. Enter ratings below.")
    except (ValueError, DecisionError) as exc:
        st.error(str(exc))

if "options" in st.session_state:
    st.subheader("Rate each option")
    ratings = {}
    for option in st.session_state["options"]:
        st.markdown(f"**{option}**")
        ratings[option] = {}
        cols = st.columns(min(3, len(st.session_state["criteria"])))
        for idx, criterion in enumerate(st.session_state["criteria"]):
            with cols[idx % len(cols)]:
                ratings[option][criterion["name"]] = st.slider(
                    f"{criterion['name']} ({criterion['weight']}%)",
                    1, 5, 3, key=f"{option}_{criterion['name']}"
                )
    if st.button("Generate decision report", type="primary"):
        try:
            report = build_decision_report(
                st.session_state["problem"], st.session_state["options"],
                st.session_state["criteria"], ratings, context, use_llm
            )
            st.subheader("Weighted ranking")
            for rank, option in enumerate(report["scoring"]["ranking"], 1):
                st.write(f"{rank}. **{option}** — {report['scoring']['scores'][option]['score']}/5")
            st.subheader("Decision analysis")
            st.markdown(report["explanation"])
            st.download_button("Download decision report",
                json.dumps(report, ensure_ascii=False, indent=2),
                file_name="decision_report.json", mime="application/json")
        except DecisionError as exc:
            st.error(str(exc))
st.info("Ratings are supplied by you. AI explains the result; it does not make the final decision.")
