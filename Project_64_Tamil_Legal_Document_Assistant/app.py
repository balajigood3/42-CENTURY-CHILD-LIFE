import streamlit as st
import tempfile, json
from pathlib import Path
from legal_assistant.extract import extract_text, DocumentError
from legal_assistant.analyzer import analyze_document, build_report
from legal_assistant.qa import find_passages

st.set_page_config(page_title="Tamil Legal Document Assistant", layout="wide")
st.title("Tamil Legal Document Assistant")
st.warning("முக்கிய குறிப்பு: இது ஆரம்பநிலை ஆவண ஆய்வு உதவி மட்டுமே; சட்ட ஆலோசனை அல்ல.")
st.caption("தமிழ் / English legal documents: clause spotting, searchable passages and review report.")
upload = st.file_uploader("Upload legal document", type=["txt", "md", "pdf", "docx"])
if upload:
    suffix = Path(upload.name).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp.write(upload.getvalue())
        temp_path = temp.name
    try:
        text = extract_text(temp_path)
        report = analyze_document(text)
        st.metric("Detected clause topics", len(report["clause_findings"]))
        st.write(f"Words: {report['word_count']} | Characters: {report['character_count']}")
        for item in report["clause_findings"]:
            with st.expander(f"{item['label']} — {item['mentions']} mention(s)"):
                st.write(item["review_guidance"])
                for snippet in item["snippets"]:
                    st.write(snippet)
        st.subheader("Document question search")
        query = st.text_input("Search for a term or clause")
        if st.button("Search", disabled=not query.strip()):
            matches = find_passages(text, query)
            if matches:
                for match in matches:
                    st.write(match["text"])
            else:
                st.info("No matching passage found.")
        st.download_button("Download review report", build_report(report, upload.name),
                           "legal_review_report.md")
        st.download_button("Download risk data JSON", json.dumps(report, ensure_ascii=False, indent=2),
                           "legal_review_report.json")
    except (DocumentError, ValueError) as exc:
        st.error(str(exc))
    finally:
        Path(temp_path).unlink(missing_ok=True)
