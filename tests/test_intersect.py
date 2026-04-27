# SPDX-License-Identifier: MIT
"""Unit tests for segment-segment intersection detection."""
import numpy as np

from line_noder._geom import extract_segments, segment_bboxes
from line_noder._intersect import find_intersections


def _setup(lines: list) -> tuple:
    segs, _ = extract_segments([np.asarray(ln, float) for ln in lines])
    bbs = segment_bboxes(segs)
    return segs, bbs


def test_simple_x_cross() -> None:
    segs, bbs = _setup([
        [[0.0, 0.0], [2.0, 2.0]],
        [[0.0, 2.0], [2.0, 0.0]],
    ])
    hits = find_intersections(segs, bbs)
    assert len(hits) == 1
    si, sj, ti, tj = hits[0]
    assert si == 0 and sj == 1
    np.testing.assert_allclose(ti, 0.5, atol=1e-9)
    np.testing.assert_allclose(tj, 0.5, atol=1e-9)


def test_parallel_no_intersection() -> None:
    segs, bbs = _setup([
        [[0.0, 0.0], [1.0, 0.0]],
        [[0.0, 1.0], [1.0, 1.0]],
    ])
    assert len(find_intersections(segs, bbs)) == 0


def test_t_junction_not_interior() -> None:
    # Endpoint of seg1 lands exactly on the interior of seg0 — should NOT be
    # reported as an interior-interior intersection
    segs, bbs = _setup([
        [[0.0, 0.0], [2.0, 0.0]],
        [[1.0, 0.0], [1.0, 1.0]],  # starts ON seg0's interior (t_j=0)
    ])
    hits = find_intersections(segs, bbs)
    assert len(hits) == 0


def test_cross_at_third() -> None:
    segs, bbs = _setup([
        [[0.0, 0.0], [3.0, 0.0]],
        [[1.0, -1.0], [1.0, 1.0]],
    ])
    hits = find_intersections(segs, bbs)
    assert len(hits) == 1
    _, _, ti, tj = hits[0]
    np.testing.assert_allclose(ti, 1 / 3, atol=1e-9)
    np.testing.assert_allclose(tj, 0.5, atol=1e-9)


def test_no_overlap_bbox() -> None:
    segs, bbs = _setup([
        [[0.0, 0.0], [1.0, 0.0]],
        [[5.0, 0.0], [6.0, 0.0]],
    ])
    assert len(find_intersections(segs, bbs)) == 0


def test_grid_2x2() -> None:
    """2 horizontal x 2 vertical, all intersections strictly interior.

    Horizontals extend from x=0 to x=3 (past both verticals at x=1, x=2).
    Verticals extend from y=-1 to y=4 (past both horizontals at y=1, y=2).
    All four intersection t-parameters are strictly in (0,1).
    """
    segs, bbs = _setup([
        [[0.0, 1.0], [3.0, 1.0]],   # H y=1
        [[0.0, 2.0], [3.0, 2.0]],   # H y=2
        [[1.0, -1.0], [1.0, 4.0]],  # V x=1
        [[2.0, -1.0], [2.0, 4.0]],  # V x=2
    ])
    hits = find_intersections(segs, bbs)
    assert len(hits) == 4, f"Expected 4 interior intersections, got {len(hits)}"
