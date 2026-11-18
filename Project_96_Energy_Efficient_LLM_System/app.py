import json
import time
import streamlit as st
from energy_llm.benchmark import estimate_energy, benchmark_callable, compare_runs

st.set_page_config(page_title="Energy-Efficient LLM System", layout="wide")
st.title("Energy-Efficient LLM System")
st.caption("LLM workload latency மற்றும் estimated energy consumption-ஐ அளந்து ஒப்பிடும் local benchmarking dashboard.")

st.info("This project measures a supplied workload. It does not automatically optimize model weights or measure hardware power unless you provide a real power reading.")
tab1, tab2 = st.tabs(["Energy calculator", "Workload benchmark"])
with tab1:
    power = st.number_input("Average power (watts)", min_value=0.0, value=50.0)
    duration = st.number_input("Duration (seconds)", min_value=0.0, value=60.0)
    if st.button("Estimate energy"):
        try:
            st.json(estimate_energy(power, duration))
        except ValueError as exc:
            st.error(str(exc))
with tab2:
    st.markdown("Benchmark a deterministic local workload as a timing demonstration.")
    loops = st.slider("Workload size", 1000, 200000, 30000, 1000)
    iterations = st.slider("Iterations", 1, 20, 5)
    power = st.number_input("Assumed average power (watts)", min_value=0.0, value=35.0, key="bench_power")
    def workload():
        return sum((i % 97) * (i % 31) for i in range(loops))
    if st.button("Run benchmark"):
        result = benchmark_callable(workload, iterations=iterations, warmup=1,
                                    estimated_power_watts=power)
        st.session_state.benchmark = result
        st.json(result)
    if "benchmark" in st.session_state:
        st.download_button("Download benchmark JSON",
                           json.dumps(st.session_state.benchmark, indent=2),
                           file_name="energy_benchmark.json", mime="application/json")
