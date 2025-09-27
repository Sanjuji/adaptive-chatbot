#!/usr/bin/env python3
"""
Simple performance benchmark for Adaptive Chatbot API.

- Warmups the service
- Measures latency for /chat across N iterations
- Reports p50/p95/p99 and average
- Optionally prints cost estimate (static placeholder since local models)
Usage:
  python scripts/perf_bench.py --host http://127.0.0.1:8000 --iters 200 --payload "hello"
"""

from __future__ import annotations

import argparse
import statistics
import time
from typing import List

import requests


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    values_sorted = sorted(values)
    k = (len(values_sorted) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(values_sorted) - 1)
    if f == c:
        return values_sorted[int(k)]
    d0 = values_sorted[f] * (c - k)
    d1 = values_sorted[c] * (k - f)
    return d0 + d1


def run_benchmark(host: str, iters: int, payload: str, warmup: int = 10) -> None:
    s = requests.Session()

    # Warmup
    for _ in range(warmup):
        try:
            r = s.post(f"{host}/chat", json={"message": payload}, timeout=10)
            _ = r.json()
        except Exception:
            pass

    # Measure
    latencies = []
    errors = 0
    for i in range(iters):
        start = time.perf_counter()
        try:
            r = s.post(f"{host}/chat", json={"message": payload}, timeout=10)
            if r.status_code != 200:
                errors += 1
        except Exception:
            errors += 1
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            latencies.append(elapsed_ms)

    avg = statistics.mean(latencies) if latencies else 0.0
    p50 = percentile(latencies, 50)
    p95 = percentile(latencies, 95)
    p99 = percentile(latencies, 99)

    print("=== Performance Benchmark ===")
    print(f"host     : {host}")
    print(f"iters    : {iters}")
    print(f"errors   : {errors}")
    print(f"avg  (ms): {avg:.2f}")
    print(f"p50  (ms): {p50:.2f}")
    print(f"p95  (ms): {p95:.2f}")
    print(f"p99  (ms): {p99:.2f}")

    # Cost placeholder: local stack implies zero marginal cost; estimate remains zero
    print("cost_usd : ~0.0000 (local/inference-free track)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", type=str, default="http://127.0.0.1:8000", help="API host")
    ap.add_argument("--iters", type=int, default=200, help="number of iterations")
    ap.add_argument("--payload", type=str, default="hello", help="message payload for /chat")
    args = ap.parse_args()

    run_benchmark(args.host, args.iters, args.payload)


if __name__ == "__main__":
    main()