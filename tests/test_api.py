# SPDX-License-Identifier: MIT
"""Unit tests for the public node_lines API."""
import numpy as np
import pytest

from line_noder import node_lines


def test_x_cross_two_diagonals() -> None:
    lines = [
        np.array([[0.0, 0.0], [2.0, 2.0]]),
        np.array([[0.0, 2.0], [2.0, 0.0]]),
    ]
    g = node_lines(lines)
    assert len(g.nodes) == 5
    assert len(g.edges) == 4
    # Intersection node should be at (1, 1)
    dists = np.linalg.norm(g.nodes - [1.0, 1.0], axis=1)
    assert dists.min() < 1e-8


def test_empty_list() -> None:
    g = node_lines([])
    assert len(g.nodes) == 0
    assert len(g.edges) == 0


def test_single_line_no_split() -> None:
    g = node_lines([np.array([[0.0, 0.0], [1.0, 1.0], [2.0, 0.0]])])
    assert len(g.nodes) == 3
    assert len(g.edges) == 2


def test_parallel_lines_no_split() -> None:
    g = node_lines([
        np.array([[0.0, 0.0], [5.0, 0.0]]),
        np.array([[0.0, 1.0], [5.0, 1.0]]),
    ])
    assert len(g.nodes) == 4
    assert len(g.edges) == 2


def test_cross_reference_dataset() -> None:
    """4 lines all crossing at (2,2): 9 unique nodes, 8 edges."""
    import json
    import os
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    cross = np.load(os.path.join(data_dir, "cross.npy"))
    with open(os.path.join(data_dir, "cross_expected.json")) as f:
        expected = json.load(f)
    lines = [cross[i] for i in range(len(cross))]
    g = node_lines(lines)
    assert len(g.nodes) == expected["nodes"], \
        f"Expected {expected['nodes']} nodes, got {len(g.nodes)}"
    assert len(g.edges) == expected["edges"], \
        f"Expected {expected['edges']} edges, got {len(g.edges)}"


def test_invalid_input_raises() -> None:
    with pytest.raises((ValueError, Exception)):
        node_lines([np.array([1.0, 2.0])])  # wrong shape


def test_multipoint_polyline() -> None:
    """Polyline with 4 pts crossed by a line that crosses two of its segments."""
    # Line 0 segments: (0,0)->(1,1), (1,1)->(2,0), (2,0)->(3,1)
    # Line 1: (0,1)->(3,0) — crosses seg0 at (0.75,0.75) and seg2 at (2.25,0.25)
    g = node_lines([
        np.array([[0.0, 0.0], [1.0, 1.0], [2.0, 0.0], [3.0, 1.0]]),
        np.array([[0.0, 1.0], [3.0, 0.0]]),
    ])
    # 4 original endpoints + 2 line1 endpoints + 2 intersections = 8 nodes
    assert len(g.nodes) == 9
    # seg0 split→2, seg1 no split→1, seg2 split→2, line1 split twice→3 = 8 edges
    assert len(g.edges) == 10
