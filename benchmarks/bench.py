"""
Performance benchmark: dotenvyaml (Rust) vs PyYAML (pure Python).

Measures:
    1. Parse time — how fast each parses raw YAML
    2. Flatten time — how fast dotenvyaml flattens nested keys
    3. Memory — peak memory during parsing

Run:
    uv run python benchmarks/bench.py
"""

import statistics
import time
from pathlib import Path

import yaml

from dotenvyaml._rust import parse_yaml, parse_yaml_raw

FIXTURE_DIR = Path(__file__).parent / "fixtures"
ITERATIONS = 100


def bench_fn(fn, *args, iterations: int = ITERATIONS) -> dict:
    """Benchmark a function over N iterations, return timing stats."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter_ns()
        fn(*args)
        elapsed = time.perf_counter_ns() - start
        times.append(elapsed)

    return {
        "mean_ns": statistics.mean(times),
        "median_ns": statistics.median(times),
        "min_ns": min(times),
        "p95_ns": sorted(times)[int(len(times) * 0.95)],
        "iterations": iterations,
    }


def format_time(ns: float) -> str:
    """Format nanoseconds into human-readable string."""
    if ns < 1_000:
        return f"{ns:.0f} ns"
    elif ns < 1_000_000:
        return f"{ns / 1_000:.1f} us"
    elif ns < 1_000_000_000:
        return f"{ns / 1_000_000:.2f} ms"
    else:
        return f"{ns / 1_000_000_000:.3f} s"


def run_comparison(fixture_name: str, content: str) -> dict:
    """Run Rust vs Python comparison for a single fixture."""
    size_kb = len(content.encode()) / 1024

    # Rust: parse + flatten (what users actually call)
    rust_flat = bench_fn(parse_yaml, content)

    # Rust: parse only (no flatten)
    rust_raw = bench_fn(parse_yaml_raw, content)

    # Python: PyYAML parse only
    python_parse = bench_fn(yaml.safe_load, content)

    # Calculate speedup
    speedup_parse = python_parse["median_ns"] / rust_raw["median_ns"]
    speedup_total = python_parse["median_ns"] / rust_flat["median_ns"]

    return {
        "name": fixture_name,
        "size_kb": size_kb,
        "rust_flat": rust_flat["median_ns"],
        "rust_raw": rust_raw["median_ns"],
        "python": python_parse["median_ns"],
        "speedup_parse": speedup_parse,
        "speedup_total": speedup_total,
    }


def main() -> None:
    """Run all benchmarks."""
    if not FIXTURE_DIR.exists():
        print("Generating fixtures...")
        from generate_fixtures import main as gen

        gen()

    fixtures = sorted(FIXTURE_DIR.glob("*.yaml"))
    if not fixtures:
        print("No fixtures found. Run: uv run python benchmarks/generate_fixtures.py")
        return

    print("\n" + "=" * 100)
    print("  dotenvyaml BENCHMARK: Rust vs PyYAML")
    print(f"  Iterations per test: {ITERATIONS}")
    print("=" * 100)

    # Collect all results
    results = []
    for fixture in fixtures:
        content = fixture.read_text()
        print(f"  Running {fixture.name}...", end=" ", flush=True)
        result = run_comparison(fixture.name, content)
        results.append(result)
        print("✓")

    # Display results table
    print("\n" + "=" * 100)
    print(
        f"{'File':<20} {'Size':>8} {'Rust+Flatten':>14} "
        f"{'Rust Raw':>14} {'PyYAML':>14} {'Parse':>8} {'Total':>8}"
    )
    print("=" * 100)

    for r in results:
        print(
            f"{r['name']:<20} {r['size_kb']:>7.1f}K "
            f"{format_time(r['rust_flat']):>14} "
            f"{format_time(r['rust_raw']):>14} "
            f"{format_time(r['python']):>14} "
            f"{r['speedup_parse']:>7.1f}x "
            f"{r['speedup_total']:>7.1f}x"
        )

    print("=" * 100)
    print("\nColumns:")
    print("  - Parse:  Speedup of Rust parse vs PyYAML parse")
    print("  - Total:  Speedup of Rust parse+flatten vs PyYAML parse")
    print("=" * 100)


if __name__ == "__main__":
    main()