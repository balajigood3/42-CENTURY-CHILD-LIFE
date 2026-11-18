import json
import tempfile
from pathlib import Path
import pandas as pd
import streamlit as st
from business_report.analyzer import parse_csv_text, analyze_metrics
from business_report.exporter import export_markdown

st.set_page_config(page_title="AI Business Report Generator", layout="wide")
st.title("AI Business Report Generator")
st.caption("Business metrics-ஐ ஆய்வு செய்து KPI, trends, insights மற்றும் management report உருவாக்கும் local-first tool.")

sample = """period,revenue,expenses,orders
2026-Q1,120000,85000,900
2026-Q2,135000,91000,980
2026-Q3,149000,97000,1050
"""
uploaded = st.file_uploader("Upload metrics CSV", type=["csv"])
csv_text = uploaded.getvalue().decode("utf-8-sig") if uploaded else st.text_area("Or paste CSV data", sample, height=150)
title = st.text_input("Report title", "Quarterly Business Performance")
if st.button("Generate report", type="primary"):
    try:
        rows = parse_csv_text(csv_text)
        report = analyze_metrics(rows, title)
        st.session_state["business_report_result"] = report
    except (ValueError, UnicodeDecodeError) as exc:
        st.error(str(exc))

report = st.session_state.get("business_report_result")
if report:
    k = report["kpis"]
    st.success("Business report generated.")
    cols = st.columns(4)
    cols[0].metric("Revenue", f"{k['total_revenue']:,.2f}")
    cols[1].metric("Expenses", f"{k['total_expenses']:,.2f}")
    cols[2].metric("Profit", f"{k['profit']:,.2f}")
    cols[3].metric("Orders", f"{k['total_orders']:,}")
    st.subheader("Period performance")
    frame = pd.DataFrame(report["periods"]).set_index("period")
    st.line_chart(frame[["revenue", "expenses"]])
    st.bar_chart(frame[["orders"]])
    st.subheader("Insights")
    for item in report["insights"]:
        st.write("• " + item)
    st.subheader("Recommendations")
    for item in report["recommendations"]:
        st.write("• " + item)
    st.caption("Currency and accounting basis are not inferred. Add labels before sharing.")
    st.download_button("Download JSON", json.dumps(report, ensure_ascii=False, indent=2),
                       file_name="business_report.json", mime="application/json")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "business_report.md"
        export_markdown(report, path)
        content = path.read_text(encoding="utf-8")
    st.download_button("Download Markdown report", content,
                       file_name="business_report.md", mime="text/markdown")
