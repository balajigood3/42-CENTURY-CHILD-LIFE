"""Educational model-compression utilities for dense NumPy weight matrices."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

def _validate_matrix(weights):
    arr = np.asarray(weights, dtype=np.float32)
    if arr.ndim != 2 or arr.size == 0:
        raise ValueError("Weights must be a non-empty 2D matrix.")
    if not np.isfinite(arr).all():
        raise ValueError("Weights must contain only finite numbers.")
    return arr

def quantize_int8(weights):
    arr = _validate_matrix(weights)
    max_abs = float(np.max(np.abs(arr)))
    scale = max_abs / 127.0 if max_abs else 1.0
    quantized = np.clip(np.round(arr / scale), -127, 127).astype(np.int8)
    restored = quantized.astype(np.float32) * scale
    return {
        "method": "symmetric_int8",
        "quantized": quantized,
        "scale": scale,
        "restored": restored,
        "original_bytes": int(arr.nbytes),
        "compressed_bytes": int(quantized.nbytes + 4),
        "max_abs_error": float(np.max(np.abs(arr - restored))),
        "mean_abs_error": float(np.mean(np.abs(arr - restored)))
    }

def low_rank_approximation(weights, rank):
    arr = _validate_matrix(weights)
    max_rank = min(arr.shape)
    if not isinstance(rank, int) or rank < 1 or rank > max_rank:
        raise ValueError(f"rank must be an integer between 1 and {max_rank}.")
    u, singular, vt = np.linalg.svd(arr, full_matrices=False)
    left = u[:, :rank] * singular[:rank]
    right = vt[:rank, :]
    restored = left @ right
    original_bytes = int(arr.nbytes)
    compressed_bytes = int(left.nbytes + right.nbytes)
    return {
        "method": "truncated_svd",
        "left": left.astype(np.float32),
        "right": right.astype(np.float32),
        "restored": restored.astype(np.float32),
        "rank": rank,
        "original_bytes": original_bytes,
        "compressed_bytes": compressed_bytes,
        "max_abs_error": float(np.max(np.abs(arr - restored))),
        "mean_abs_error": float(np.mean(np.abs(arr - restored)))
    }

def compression_summary(result):
    original = result["original_bytes"]
    compressed = result["compressed_bytes"]
    return {
        "method": result["method"],
        "original_bytes": original,
        "compressed_bytes": compressed,
        "compression_ratio": round(original / compressed, 4) if compressed else None,
        "space_reduction_percent": round((1 - compressed / original) * 100, 2),
        "max_abs_error": result["max_abs_error"],
        "mean_abs_error": result["mean_abs_error"]
    }

def save_compressed(result, path):
    payload = {"method": result["method"], "metadata": compression_summary(result)}
    if result["method"] == "symmetric_int8":
        payload.update({"quantized": result["quantized"].tolist(), "scale": result["scale"]})
    else:
        payload.update({"left": result["left"].tolist(), "right": result["right"].tolist(),
                        "rank": result["rank"]})
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

def restore_compressed(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload["method"] == "symmetric_int8":
        return np.asarray(payload["quantized"], dtype=np.int8).astype(np.float32) * float(payload["scale"])
    if payload["method"] == "truncated_svd":
        return np.asarray(payload["left"], dtype=np.float32) @ np.asarray(payload["right"], dtype=np.float32)
    raise ValueError("Unknown compression method.")
