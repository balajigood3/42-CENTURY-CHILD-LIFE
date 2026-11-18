import json
import numpy as np
import pytest
from compression_lab.compress import (
    quantize_int8, low_rank_approximation, compression_summary,
    save_compressed, restore_compressed
)

def test_int8_output_dtype_and_shape():
    result = quantize_int8([[0.0, 1.0], [-1.0, 0.5]])
    assert result["quantized"].dtype == np.int8
    assert result["restored"].shape == (2, 2)

def test_int8_zero_matrix():
    result = quantize_int8(np.zeros((2, 3)))
    assert np.all(result["restored"] == 0)

def test_int8_error_is_bounded():
    result = quantize_int8([[0.1, -0.7], [1.0, 0.3]])
    assert result["max_abs_error"] < 0.01

def test_rejects_non_matrix():
    with pytest.raises(ValueError):
        quantize_int8([1, 2, 3])

def test_rejects_nan():
    with pytest.raises(ValueError):
        quantize_int8([[float("nan")]])

def test_svd_exact_full_rank_reconstruction():
    matrix = np.array([[1, 2], [3, 4]], dtype=np.float32)
    result = low_rank_approximation(matrix, 2)
    assert np.allclose(result["restored"], matrix, atol=1e-5)

def test_svd_rejects_invalid_rank():
    with pytest.raises(ValueError):
        low_rank_approximation([[1, 2], [3, 4]], 0)

def test_svd_compressed_storage_for_low_rank_case():
    matrix = np.outer(np.arange(1, 6), np.arange(1, 5)).astype(np.float32)
    result = low_rank_approximation(matrix, 1)
    assert result["compressed_bytes"] < result["original_bytes"]
    assert result["mean_abs_error"] < 1e-4

def test_summary_contains_compression_metrics():
    summary = compression_summary(quantize_int8([[1, 2], [3, 4]]))
    assert "compression_ratio" in summary
    assert "space_reduction_percent" in summary

def test_quantized_save_restore(tmp_path):
    result = quantize_int8([[1, -1], [0.5, 0.2]])
    path = tmp_path / "q.json"
    save_compressed(result, path)
    restored = restore_compressed(path)
    assert restored.shape == (2, 2)
    assert np.allclose(restored, result["restored"])

def test_svd_save_restore(tmp_path):
    result = low_rank_approximation([[1, 2], [2, 4], [3, 6]], 1)
    path = tmp_path / "svd.json"
    save_compressed(result, path)
    assert np.allclose(restore_compressed(path), result["restored"])

def test_compression_rejects_unknown_format(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"method": "unknown"}))
    with pytest.raises(ValueError):
        restore_compressed(path)
