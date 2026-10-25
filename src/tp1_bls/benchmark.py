from __future__ import annotations

import csv
import statistics
import time
from pathlib import Path

from tp1_bls.bls_core import (
    aggregate,
    aggregate_verify,
    keygen_from_seed,
    sign,
    sk_to_pk,
    verify,
)


def generate_batch(size: int):
    sks = []
    pks = []
    msgs = []
    for i in range(size):
        seed = f"sensor-{i:04d}-seed".encode()
        sk = keygen_from_seed(seed)
        sks.append(sk)
        pks.append(sk_to_pk(sk))
        msgs.append(f"sensor-{i:04d}:temperature={20 + (i % 10) * 0.5}".encode())
    return sks, pks, msgs


def benchmark_case(size: int, rounds: int = 3):
    key_times = []
    sign_times = []
    verify_times = []
    aggregate_times = []
    agg_verify_times = []
    sig_sizes = []

    for _ in range(rounds):
        t0 = time.perf_counter()
        sks, pks, msgs = generate_batch(size)
        key_times.append((time.perf_counter() - t0) * 1000.0)

        t0 = time.perf_counter()
        sigs = [sign(sk, msg) for sk, msg in zip(sks, msgs)]
        sign_times.append((time.perf_counter() - t0) * 1000.0)

        sig_sizes.append(len(sigs[0]))

        t0 = time.perf_counter()
        for pk, msg, sig in zip(pks, msgs, sigs):
            assert verify(pk, msg, sig) is True
        verify_times.append((time.perf_counter() - t0) * 1000.0)

        t0 = time.perf_counter()
        agg = aggregate(sigs)
        aggregate_times.append((time.perf_counter() - t0) * 1000.0)

        t0 = time.perf_counter()
        assert aggregate_verify(pks, msgs, agg) is True
        agg_verify_times.append((time.perf_counter() - t0) * 1000.0)

    return {
        "n": size,
        "keygen_ms_median": statistics.median(key_times),
        "sign_ms_median": statistics.median(sign_times),
        "verify_ms_median": statistics.median(verify_times),
        "aggregate_ms_median": statistics.median(aggregate_times),
        "aggregate_verify_ms_median": statistics.median(agg_verify_times),
        "sig_size_bytes": statistics.median(sig_sizes),
    }


def main():
    sizes = [2, 8, 32, 128]
    results = [benchmark_case(size) for size in sizes]

    output_dir = Path(__file__).resolve().parents[2] / "benchmarks"
    output_dir.mkdir(exist_ok=True)
    csv_path = output_dir / "bls_aggregate_benchmark.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "n",
                "keygen_ms_median",
                "sign_ms_median",
                "verify_ms_median",
                "aggregate_ms_median",
                "aggregate_verify_ms_median",
                "sig_size_bytes",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    print("Benchmark results:")
    for row in results:
        print(row)
    print(f"CSV written to: {csv_path}")


if __name__ == "__main__":
    main()
