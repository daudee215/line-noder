# SPDX-License-Identifier: MIT
"""Tests for the STRtree backend (added in v0.2).

Strategy: every test compares ``method='strtree'`` output to the pairwise
backend on the same input.  Equivalence is checked by treating the result
as an unordered set of (i, j, t, u) tuples with floating-point tolerance
on the parameters.
"""
from __future__ import annotations

import numpy as np
import pytest

from line_noder import node_lines
from line_noder._geom import extract_segments, segment_bboxes
from line_noder._intersect import find_intersections

shapely = pytest.importorskip("shapely")


def _norm(hits: list[tuple[int, int, float, float]]) -> set[tuple[int, int, int, int]]:
    """Normalise hits to an order-insensitive comparable set.

    Stores the parameters as rounded ints (1e-9 precision) so float drift
    between backends — both use the same arithmetic, so drift is bounded by
    the last bit — does not produce spurious differences.
    """
    out = set()
    for i, j, t, u in hits:
        if i > j:
            i, j = j, i
            t, u = u, t
        out.add((i, j, round(t * 1e9), round(u * 1e9)))
    return out


def _equiv(lines: list[np.ndarray]) -> tuple[int, int]:
    """Run both backends and assert equivalent output. Returns (n_pw, n_st)."""
    segs, _ = extract_segments(lines)
    bbs = segment_bboxes(segs)
    pw = find_intersections(segs, bbs, method="pairwise")
    st = find_intersections(segs, bbs, method="strtree")
    assert _norm(pw) == _norm(st), (
        f"Backend mismatch: pairwise={len(pw)} strtree={len(st)} "
        f"sym_diff={len(_norm(pw) ^ _norm(st))}"
    )
    return len(pw), len(st)


# ---------------------------------------------------------------------------
# Basic shapes
# ---------------------------------------------------------------------------


def test_simple_x_cross() -> None:
    lines = [
        np.array([[0.0, 0.0], [2.0, 2.0]]),
        np.array([[0.0, 2.0], [2.0, 0.0]]),
    ]
    n_pw, _ = _equiv(lines)
    assert n_pw == 1


def test_parallel_no_intersection() -> None:
    lines = [
        np.array([[0.0, 0.0], [5.0, 0.0]]),
        np.array([[0.0, 1.0], [5.0, 1.0]]),
    ]
    n_pw, _ = _equiv(lines)
    assert n_pw == 0


def test_t_junction_not_interior() -> None:
    """T-junction (endpoint-on-interior) is NOT an interior crossing."""
    lines = [
        np.array([[0.0, 0.0], [2.0, 0.0]]),
        np.array([[1.0, 0.0], [1.0, 1.0]]),
    ]
    n_pw, _ = _equiv(lines)
    assert n_pw == 0


def test_disjoint_bboxes() -> None:
    lines = [
        np.array([[0.0, 0.0], [1.0, 0.0]]),
        np.array([[5.0, 0.0], [6.0, 0.0]]),
    ]
    n_pw, _ = _equiv(lines)
    assert n_pw == 0


# ---------------------------------------------------------------------------
# Degenerate-case fixtures (these motivated dropping the from-scratch
# Bentley-Ottmann implementation; STRtree handles them via GEOS).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("size", [3, 4, 5, 6, 7, 8, 10, 15, 20])
def test_regular_grid_equivalence(size: int) -> None:
    """N×N regular grid — many shared endpoints, simultaneous events."""
    lines = []
    for i in range(size):
        lines.append(np.array([[0.0, float(i)], [float(size - 1), float(i)]]))
    for j in range(size):
        lines.append(np.array([[float(j), 0.0], [float(j), float(size - 1)]]))
    n_pw, _ = _equiv(lines)
    expected_interior = max(0, size - 2) ** 2
    assert n_pw == expected_interior


def test_concurrent_lines_at_origin() -> None:
    """Three lines all passing through the same interior point."""
    lines = [
        np.array([[-1.0, -1.0], [1.0, 1.0]]),
        np.array([[-1.0, 1.0], [1.0, -1.0]]),
        np.array([[-1.0, 0.0], [1.0, 0.0]]),
    ]
    # 3 pairs all intersect at origin
    n_pw, _ = _equiv(lines)
    assert n_pw == 3


def test_collinear_overlapping_segments() -> None:
    """Collinear overlap is not an interior crossing — both backends agree."""
    lines = [
        np.array([[0.0, 0.0], [3.0, 0.0]]),
        np.array([[1.0, 0.0], [4.0, 0.0]]),  # overlaps [1,3]
    ]
    _equiv(lines)


def test_shared_endpoint_not_interior() -> None:
    """Two segments sharing exactly one endpoint — no interior crossing."""
    lines = [
        np.array([[0.0, 0.0], [1.0, 0.0]]),
        np.array([[0.0, 0.0], [0.0, 1.0]]),
    ]
    n_pw, _ = _equiv(lines)
    assert n_pw == 0


# ---------------------------------------------------------------------------
# Property-based: random inputs at varying densities
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("seed", range(8))
@pytest.mark.parametrize("n", [50, 200, 800])
def test_random_lines_equivalence(seed: int, n: int) -> None:
    """STRtree must produce same set as pairwise on random sparse inputs."""
    rng = np.random.default_rng(seed)
    starts = rng.uniform(0, 100, (n, 2))
    ends = rng.uniform(0, 100, (n, 2))
    lines = [np.stack([s, e]) for s, e in zip(starts, ends, strict=False)]
    _equiv(lines)


@pytest.mark.parametrize("seed", range(4))
def test_short_segments_sparse(seed: int) -> None:
    """Short segments — closer to real-world road / hydro topology."""
    rng = np.random.default_rng(seed)
    n = 500
    starts = rng.uniform(0, 1000, (n, 2))
    deltas = rng.normal(0, 5, (n, 2))
    ends = starts + deltas
    lines = [np.stack([s, e]) for s, e in zip(starts, ends, strict=False)]
    _equiv(lines)


# ---------------------------------------------------------------------------
# End-to-end: node_lines() with each backend produces equivalent topology.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", ["pairwise", "strtree", "auto"])
def test_node_lines_x_cross(method: str) -> None:
    lines = [
        np.array([[0.0, 0.0], [2.0, 2.0]]),
        np.array([[0.0, 2.0], [2.0, 0.0]]),
    ]
    g = node_lines(lines, method=method)  # type: ignore[arg-type]
    assert len(g.nodes) == 5
    assert len(g.edges) == 4


def test_node_lines_topology_equivalence_grid() -> None:
    """Same node + edge counts from each backend on a 10×10 grid."""
    lines = []
    for i in range(10):
        lines.append(np.array([[0.0, float(i)], [9.0, float(i)]]))
    for j in range(10):
        lines.append(np.array([[float(j), 0.0], [float(j), 9.0]]))
    g_pw = node_lines(lines, method="pairwise")
    g_st = node_lines(lines, method="strtree")
    assert len(g_pw.nodes) == len(g_st.nodes)
    assert len(g_pw.edges) == len(g_st.edges)


def test_node_lines_topology_equivalence_random() -> None:
    rng = np.random.default_rng(42)
    n = 300
    starts = rng.uniform(0, 100, (n, 2))
    ends = rng.uniform(0, 100, (n, 2))
    lines = [np.stack([s, e]) for s, e in zip(starts, ends, strict=False)]
    g_pw = node_lines(lines, method="pairwise")
    g_st = node_lines(lines, method="strtree")
    assert len(g_pw.nodes) == len(g_st.nodes)
    assert len(g_pw.edges) == len(g_st.edges)


def test_invalid_method_raises() -> None:
    with pytest.raises(ValueError, match="method must be"):
        node_lines([np.array([[0.0, 0.0], [1.0, 1.0]])], method="banana")  # type: ignore[arg-type]


def test_empty_input_strtree() -> None:
    g = node_lines([], method="strtree")
    assert len(g.nodes) == 0
    assert len(g.edges) == 0


def test_single_segment_strtree() -> None:
    g = node_lines(
        [np.array([[0.0, 0.0], [1.0, 1.0]])],
        method="strtree",
    )
    # No intersections possible with one segment; should return raw graph.
    assert len(g.nodes) == 2
    assert len(g.edges) == 1
