# SPDX-License-Identifier: MIT
"""Unit tests for graph construction."""
import numpy as np

from line_noder._graph import build_graph


def _s(x0, y0, x1, y1):
    return np.array([[x0, y0], [x1, y1]])


def test_empty_input() -> None:
    g = build_graph([])
    assert len(g.nodes) == 0
    assert len(g.edges) == 0


def test_single_segment() -> None:
    g = build_graph([_s(0, 0, 1, 0)])
    assert len(g.nodes) == 2
    assert len(g.edges) == 1


def test_shared_endpoint_dedup() -> None:
    # Two segments sharing endpoint (1,0)
    g = build_graph([_s(0, 0, 1, 0), _s(1, 0, 2, 0)])
    assert len(g.nodes) == 3
    assert len(g.edges) == 2


def test_x_cross_four_edges() -> None:
    # Manual split of two crossing lines at (1,1)
    sub_segs = [
        _s(0, 0, 1, 1),
        _s(1, 1, 2, 2),
        _s(0, 2, 1, 1),
        _s(1, 1, 2, 0),
    ]
    g = build_graph(sub_segs)
    assert len(g.nodes) == 5
    assert len(g.edges) == 4


def test_duplicate_segment_ignored() -> None:
    # Degenerate: same start == end after snapping
    g = build_graph([np.array([[0.0, 0.0], [0.0, 0.0]])])
    assert len(g.edges) == 0


def test_adjacency() -> None:
    g = build_graph([_s(0, 0, 1, 0), _s(1, 0, 2, 0)])
    adj = g.to_adjacency()
    # Middle node (1,0) should connect to both endpoints
    middle = [i for i, c in enumerate(g.nodes) if abs(c[0] - 1.0) < 1e-9][0]
    assert len(adj[middle]) == 2


def test_snapping_tolerance() -> None:
    # Two points within 1e-9 should collapse to one node
    g = build_graph([
        _s(0.0, 0.0, 1.0, 0.0),
        _s(1.0 + 5e-10, 0.0, 2.0, 0.0),
    ])
    assert len(g.nodes) == 3  # (0,0), (1,0), (2,0)
