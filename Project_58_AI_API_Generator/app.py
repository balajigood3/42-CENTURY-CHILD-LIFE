import json, tempfile, os
import streamlit as st
from api_generator.generator import generate_files, export_project
from api_generator.schema import SpecError

st.set_page_config(page_title="AI API Generator", layout="wide")
st.title("AI API Generator")
st.caption("Generate a validated FastAPI CRUD starter from a structured API specification — no paid API keys.")
example = {
    "name": "Product",
    "endpoint": "/products",
    "fields": [
        {"name": "title", "type": "str", "required": True},
        {"name": "price", "type": "float", "required": True},
        {"name": "active", "type": "bool", "required": False}
    ],
    "methods": ["GET", "POST", "PUT", "PATCH", "DELETE"]
}
raw = st.text_area("API specification (JSON)", json.dumps(example, indent=2), height=320)
if st.button("Validate and generate API", type="primary"):
    try:
        spec = json.loads(raw)
        artifacts = generate_files(spec)
        st.success(f"Generated {len(artifacts)} project files.")
        st.json({"resource": spec["endpoint"], "methods": spec["methods"], "files": list(artifacts)})
        chosen = st.selectbox("Preview generated file", list(artifacts))
        st.code(artifacts[chosen], language="python" if chosen.endswith(".py") else "text")
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            tmp_path = tmp.name
        export_project(spec, tmp_path)
        with open(tmp_path, "rb") as handle:
            st.download_button("Download generated FastAPI project", handle.read(), file_name="generated_api.zip")
        os.unlink(tmp_path)
    except (json.JSONDecodeError, SpecError) as exc:
        st.error(str(exc))
st.info("Generated APIs use an in-memory store for demonstration. Add database persistence and security before production.")
