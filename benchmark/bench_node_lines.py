# SPDX-License-Identifier: MIT
"""Benchmarks for node_lines on synthetic large datasets.

Run with: uv run pytest benchmark/ --benchmark-only -v

Each scenario runs both backends so the speedup is directly visible in
the pytest-benchmark summary.
"""
from __future__ import annotations

import numpy as np
import pytest

from line_noder import node_lines


def _grid(nx: int, ny: int) -> list[np.ndarray]:
    lines = []
    for i in range(ny):
        lines.append(np.array([[0.0, float(i)], [float(nx - 1), float(i)]]))
    for j in range(nx):
        lines.append(np.array([[float(j), 0.0], [float(j), float(ny - 1)]]))
    return lines


def _random_lines(n: int, seed: int = 0) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    starts = rng.uniform(0, 100, (n, 2))
    ends = rng.uniform(0, 100, (n, 2))
    return [np.stack([s, e]) for s, e in zip(starts, ends, strict=False)]


def _short_random_lines(n: int, seed: int = 0) -> list[np.ndarray]:
    """Sparse network (short segments) — closer to road / hydro networks."""
    rng = np.random.default_rng(seed)
    starts = rng.uniform(0, 1000, (n, 2))
    deltas = rng.normal(0, 5, (n, 2))
    ends = starts + deltas
    return [np.stack([s, e]) for s, e in zip(starts, ends, strict=False)]


# ---------------------------------------------------------------------------
# Pairwise (v0.1 default)
# ---------------------------------------------------------------------------


@pytest.mark.benchmark(group="grid_100x100")
def test_bench_grid_100x100_pairwise(benchmark):
    lines = _grid(100, 100)
    benchmark(node_lines, lines, method="pairwise")


@pytest.mark.benchmark(group="random_1000")
def test_bench_random_1000_pairwise(benchmark):
    lines = _random_lines(1000)
    benchmark(node_lines, lines, method="pairwise")


@pytest.mark.benchmark(group="sparse_5000")
def test_bench_sparse_5000_pairwise(benchmark):
    lines = _short_random_lines(5000)
    benchmark(node_lines, lines, method="pairwise")


@pytest.mark.benchmark(group="sparse_20000")
def test_bench_sparse_20000_pairwise(benchmark):
    lines = _short_random_lines(20000)
    benchmark(node_lines, lines, method="pairwise")


# ---------------------------------------------------------------------------
# STRtree (v0.2 speedup)
# ---------------------------------------------------------------------------


@pytest.mark.benchmark(group="grid_100x100")
def test_bench_grid_100x100_strtree(benchmark):
    pytest.importorskip("shapely")
    lines = _grid(100, 100)
    benchmark(node_lines, lines, method="strtree")


@pytest.mark.benchmark(group="random_1000")
def test_bench_random_1000_strtree(benchmark):
    pytest.importorskip("shapely")
    lines = _random_lines(1000)
    benchmark(node_lines, lines, method="strtree")


@pytest.mark.benchmark(group="sparse_5000")
def test_bench_sparse_5000_strtree(benchmark):
    pytest.importorskip("shapely")
    lines = _short_random_lines(5000)
    benchmark(node_lines, lines, method="strtree")


@pytest.mark.benchmark(group="sparse_20000")
def test_bench_sparse_20000_strtree(benchmark):
    pytest.importorskip("shapely")
    lines = _short_random_lines(20000)
    benchmark(node_lines, lines, method="strtree")
