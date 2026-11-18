import json
import io
import pandas as pd
import streamlit as st
from synthetic_lab.generator import generate_rows, validate_dataset, profile_dataset

st.set_page_config(page_title="Synthetic Data Generation & Validation AI", layout="wide")
st.title("Synthetic Data Generation & Validation AI")
st.caption("Schema அடிப்படையில் synthetic tabular data உருவாக்கி, அதன் validity மற்றும் statistical profile-ஐ சரிபார்க்கும் local tool.")

st.info("This is a schema-driven synthetic data generator, not a privacy guarantee. Do not assume generated rows are anonymous or safe without a privacy assessment.")
schema_text = st.text_area("Schema JSON", json.dumps([
    {"name": "age", "type": "integer", "min": 18, "max": 80},
    {"name": "income", "type": "float", "min": 15000, "max": 200000},
    {"name": "department", "type": "category", "values": ["sales", "engineering", "finance"]},
    {"name": "active", "type": "boolean"}
], indent=2), height=260)
count = st.number_input("Rows to generate", min_value=1, max_value=100000, value=100)
seed = st.number_input("Random seed", min_value=0, max_value=999999, value=42)
if st.button("Generate and validate", type="primary"):
    try:
        schema = json.loads(schema_text)
        rows = generate_rows(schema, int(count), int(seed))
        validation = validate_dataset(rows, schema)
        profile = profile_dataset(rows, schema)
        st.session_state.synthetic_bundle = {"rows": rows, "validation": validation, "profile": profile}
    except Exception as exc:
        st.error(f"Generation failed: {exc}")

if "synthetic_bundle" in st.session_state:
    bundle = st.session_state.synthetic_bundle
    st.subheader("Generated data")
    st.success(f"Validation result: {'Valid' if bundle['validation']['valid'] else 'Invalid'}")
    st.dataframe(pd.DataFrame(bundle["rows"]), use_container_width=True)
    st.subheader("Validation report")
    st.json(bundle["validation"])
    st.subheader("Data profile")
    st.json(bundle["profile"])
    csv = pd.DataFrame(bundle["rows"]).to_csv(index=False).encode("utf-8")
    st.download_button("Download synthetic CSV", csv, file_name="synthetic_data.csv", mime="text/csv")
    st.download_button("Download validation JSON", json.dumps(bundle["validation"], indent=2),
                       file_name="validation_report.json", mime="application/json")
