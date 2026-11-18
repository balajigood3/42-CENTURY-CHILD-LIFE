# Project 93 — AI Model Compression Generator

A local educational lab for compressing dense numeric weight matrices using symmetric INT8 quantization and truncated SVD.

## Features
- Upload CSV numeric weight matrices
- Symmetric INT8 quantization
- Truncated singular value decomposition (low-rank approximation)
- Compare storage size and compression ratio
- Measure max and mean absolute reconstruction error
- Save and restore compressed matrix representations
- Streamlit UI, pytest, Docker and Docker Compose
- No paid API keys

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Open `http://localhost:8501`.

## Docker
```bash
docker compose up --build
```

## Tests
```bash
pytest -q
```

## CSV format
A headerless CSV containing a rectangular numeric matrix, for example:
```csv
0.1,0.2,0.3
0.4,0.5,0.6
```

## Methods
- INT8: symmetric scaling to signed 8-bit integers with one scale factor.
- SVD: retain the top-k singular values and corresponding factors.

## Limitations
- This project compresses a single dense matrix, not complete model checkpoints or transformer architectures.
- JSON export is for inspectability; JSON text can be larger than the original binary matrix. Reported compressed bytes measure the numeric representation, not JSON file size.
- SVD is a lossy approximation unless full rank is retained.
- Real model deployment requires framework-specific serialization, calibration data, accuracy benchmarks and hardware profiling.
