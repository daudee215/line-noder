# SPDX-License-Identifier: MIT
"""Benchmarks for node_lines on synthetic large datasets.

Run with: uv run pytest benchmark/ --benchmark-only -v
"""
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


@pytest.fixture
def grid_100x100():
    return _grid(100, 100)


@pytest.fixture
def random_1000():
    return _random_lines(1000)


@pytest.fixture
def random_5000():
    return _random_lines(5000)


def test_bench_grid_100x100(benchmark, grid_100x100):
    """100x100 regular grid — 10,000 lines, 10,000 interior intersections."""
    result = benchmark(node_lines, grid_100x100)
    assert len(result.nodes) > 0


def test_bench_random_1000(benchmark, random_1000):
    """1,000 random line segments."""
    result = benchmark(node_lines, random_1000)
    assert len(result.nodes) > 0


def test_bench_random_5000(benchmark, random_5000):
    """5,000 random line segments — stress test."""
    result = benchmark(node_lines, random_5000)
    assert len(result.nodes) > 0
