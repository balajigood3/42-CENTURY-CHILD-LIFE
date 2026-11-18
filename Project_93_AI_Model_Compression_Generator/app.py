import json
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
from compression_lab.compress import quantize_int8, low_rank_approximation, compression_summary, save_compressed

st.set_page_config(page_title="AI Model Compression Generator", layout="wide")
st.title("AI Model Compression Generator")
st.caption("Neural-network weight matrices-ஐ INT8 quantization மற்றும் low-rank SVD மூலம் சுருக்கும் educational lab.")

st.info("Local demo: this tool compresses an uploaded numeric weight matrix. It does not automatically compress an entire PyTorch/LLM model.")
uploaded = st.file_uploader("Upload a CSV weight matrix", type=["csv"])
if uploaded:
    try:
        matrix = pd.read_csv(uploaded, header=None).to_numpy(dtype=np.float32)
        st.write("Matrix shape:", matrix.shape)
        st.dataframe(pd.DataFrame(matrix), use_container_width=True)
        method = st.radio("Compression method", ["INT8 quantization", "Low-rank SVD"])
        if method == "Low-rank SVD":
            rank = st.number_input("Target rank", min_value=1, max_value=min(matrix.shape), value=1)
        if st.button("Compress matrix", type="primary"):
            result = quantize_int8(matrix) if method == "INT8 quantization" else low_rank_approximation(matrix, int(rank))
            summary = compression_summary(result)
            st.session_state.compression_result = result
            st.session_state.compression_summary = summary
    except Exception as exc:
        st.error(f"Could not read matrix: {exc}")

if "compression_summary" in st.session_state:
    st.subheader("Compression report")
    summary = st.session_state.compression_summary
    c1, c2, c3 = st.columns(3)
    c1.metric("Compression ratio", f"{summary['compression_ratio']}×")
    c2.metric("Space reduction", f"{summary['space_reduction_percent']}%")
    c3.metric("Mean absolute error", f"{summary['mean_abs_error']:.6f}")
    st.json(summary)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "compressed_weights.json"
        save_compressed(st.session_state.compression_result, out)
        data = out.read_bytes()
    st.download_button("Download compressed weights", data,
                       file_name="compressed_weights.json", mime="application/json")
