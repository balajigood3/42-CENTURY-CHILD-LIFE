"""Measure local inference energy proxies and estimate energy from power readings."""
from __future__ import annotations
import math
import statistics
import time

def validate_measurements(power_watts, duration_seconds):
    if not isinstance(power_watts, (int, float)) or not math.isfinite(power_watts) or power_watts < 0:
        raise ValueError("Power must be a finite non-negative number in watts.")
    if not isinstance(duration_seconds, (int, float)) or not math.isfinite(duration_seconds) or duration_seconds < 0:
        raise ValueError("Duration must be a finite non-negative number in seconds.")
    return True

def estimate_energy(power_watts, duration_seconds):
    validate_measurements(power_watts, duration_seconds)
    # Wh = W * seconds / 3600; kWh = Wh / 1000
    wh = power_watts * duration_seconds / 3600.0
    return {"power_watts": float(power_watts), "duration_seconds": float(duration_seconds),
            "energy_wh": wh, "energy_kwh": wh / 1000.0,
            "method": "Estimated from average power × elapsed wall time"}

def benchmark_callable(fn, iterations=5, warmup=1, estimated_power_watts=0.0):
    if not callable(fn):
        raise ValueError("fn must be callable.")
    if not isinstance(iterations, int) or iterations < 1:
        raise ValueError("iterations must be a positive integer.")
    if not isinstance(warmup, int) or warmup < 0:
        raise ValueError("warmup must be a non-negative integer.")
    if not isinstance(estimated_power_watts, (int, float)) or not math.isfinite(estimated_power_watts) or estimated_power_watts < 0:
        raise ValueError("estimated_power_watts must be finite and non-negative.")
    for _ in range(warmup):
        fn()
    durations = []
    for _ in range(iterations):
        start = time.perf_counter()
        fn()
        durations.append(time.perf_counter() - start)
    avg = statistics.mean(durations)
    total = sum(durations)
    energy = estimate_energy(estimated_power_watts, total)
    return {
        "iterations": iterations,
        "warmup_iterations": warmup,
        "durations_seconds": durations,
        "average_latency_seconds": avg,
        "p95_latency_seconds": sorted(durations)[min(len(durations)-1, math.ceil(0.95*len(durations))-1)],
        "total_measured_seconds": total,
        "estimated_energy": energy,
        "energy_per_iteration_wh": energy["energy_wh"] / iterations if iterations else 0,
        "measurement_note": "Energy is an estimate based on user-supplied average power; timing alone is not a power measurement."
    }

def compare_runs(baseline, optimized):
    for name, result in (("baseline", baseline), ("optimized", optimized)):
        if not isinstance(result, dict) or result.get("average_latency_seconds", -1) < 0:
            raise ValueError(f"Invalid {name} benchmark result.")
        if result.get("estimated_energy", {}).get("energy_wh", -1) < 0:
            raise ValueError(f"Invalid {name} energy estimate.")
    base_e = baseline["estimated_energy"]["energy_wh"]
    opt_e = optimized["estimated_energy"]["energy_wh"]
    base_l = baseline["average_latency_seconds"]
    opt_l = optimized["average_latency_seconds"]
    return {
        "energy_change_percent": ((opt_e - base_e) / base_e * 100) if base_e else None,
        "latency_change_percent": ((opt_l - base_l) / base_l * 100) if base_l else None,
        "energy_saving_percent": ((base_e - opt_e) / base_e * 100) if base_e else None,
        "interpretation": "Negative energy change means the optimized run used less estimated energy."
    }
