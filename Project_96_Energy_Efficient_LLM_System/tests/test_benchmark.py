import pytest
from energy_llm.benchmark import estimate_energy, benchmark_callable, compare_runs

def test_energy_calculation():
    result = estimate_energy(100, 3600)
    assert result["energy_wh"] == pytest.approx(100)

def test_zero_power():
    assert estimate_energy(0, 10)["energy_wh"] == 0

def test_reject_negative_power():
    with pytest.raises(ValueError):
        estimate_energy(-1, 10)

def test_reject_negative_duration():
    with pytest.raises(ValueError):
        estimate_energy(10, -1)

def test_reject_nan():
    with pytest.raises(ValueError):
        estimate_energy(float("nan"), 10)

def test_benchmark_callable_runs_iterations():
    calls = []
    result = benchmark_callable(lambda: calls.append(1), iterations=3, warmup=1, estimated_power_watts=20)
    assert len(calls) == 4
    assert result["iterations"] == 3
    assert result["estimated_energy"]["energy_wh"] >= 0

def test_benchmark_invalid_iterations():
    with pytest.raises(ValueError):
        benchmark_callable(lambda: None, iterations=0)

def test_benchmark_non_callable_rejected():
    with pytest.raises(ValueError):
        benchmark_callable("not callable")

def test_compare_runs_energy_saving():
    baseline = {"average_latency_seconds": 2, "estimated_energy": {"energy_wh": 1.0}}
    optimized = {"average_latency_seconds": 1.5, "estimated_energy": {"energy_wh": 0.5}}
    result = compare_runs(baseline, optimized)
    assert result["energy_saving_percent"] == 50

def test_compare_zero_baseline_safe():
    baseline = {"average_latency_seconds": 0, "estimated_energy": {"energy_wh": 0}}
    optimized = {"average_latency_seconds": 1, "estimated_energy": {"energy_wh": 1}}
    assert compare_runs(baseline, optimized)["energy_saving_percent"] is None

def test_compare_reject_invalid_result():
    with pytest.raises(ValueError):
        compare_runs({}, {})

def test_latency_metric_present():
    result = benchmark_callable(lambda: sum(range(100)), iterations=2)
    assert result["average_latency_seconds"] >= 0
