# SPDX-License-Identifier: MIT
"""Unit tests for segment splitting."""
import numpy as np

from line_noder._split import split_segments


def _seg(x0: float, y0: float, x1: float, y1: float) -> np.ndarray:
    return np.array([[x0, y0], [x1, y1]])


def test_no_split() -> None:
    segs = np.stack([_seg(0, 0, 1, 0), _seg(0, 1, 1, 1)])
    result = split_segments(segs, [])
    assert len(result) == 2
    np.testing.assert_allclose(result[0], segs[0])
    np.testing.assert_allclose(result[1], segs[1])


def test_single_split_midpoint() -> None:
    segs = np.stack([_seg(0, 0, 2, 0), _seg(0, 1, 0, -1)])
    # seg 0 split at t=0.5, seg 1 split at t=0.5
    result = split_segments(segs, [(0, 1, 0.5, 0.5)])
    assert len(result) == 4
    np.testing.assert_allclose(result[0], [[0, 0], [1, 0]])
    np.testing.assert_allclose(result[1], [[1, 0], [2, 0]])


def test_two_splits_on_one_segment() -> None:
    """Horizontal seg0 is split by two different crossing segments."""
    segs = np.stack([
        _seg(0, 0, 3, 0),   # seg 0: split at t=1/3 and t=2/3
        _seg(1, -1, 1, 1),  # seg 1: crosses seg 0 at t=1/3
        _seg(2, -1, 2, 1),  # seg 2: crosses seg 0 at t=2/3
    ])
    result = split_segments(segs, [(0, 1, 1 / 3, 0.5), (0, 2, 2 / 3, 0.5)])
    # seg 0: 3 sub-segs; seg 1: 2 sub-segs; seg 2: 2 sub-segs = 7 total
    assert len(result) == 7
    np.testing.assert_allclose(result[0], [[0, 0], [1, 0]], atol=1e-9)
    np.testing.assert_allclose(result[1], [[1, 0], [2, 0]], atol=1e-9)
    np.testing.assert_allclose(result[2], [[2, 0], [3, 0]], atol=1e-9)


def test_split_preserves_direction() -> None:
    segs = np.stack([_seg(4, 0, 0, 4)])
    result = split_segments(segs, [(0, 0, 0.5, 0.5)])
    assert len(result) == 2
    np.testing.assert_allclose(result[0][0], [4, 0])
    np.testing.assert_allclose(result[0][1], [2, 2])
    np.testing.assert_allclose(result[1][0], [2, 2])
    np.testing.assert_allclose(result[1][1], [0, 4])


def test_duplicate_t_deduplicated() -> None:
    """Same t-parameter from two different pairs collapses to one split."""
    segs = np.stack([
        _seg(0, 0, 2, 0),   # seg 0
        _seg(1, -1, 1, 1),  # seg 1: crosses seg 0 at t=0.5
        _seg(1, 2, 1, -2),  # seg 2: same crossing point on seg 0 (t=0.5)
    ])
    result = split_segments(segs, [(0, 1, 0.5, 0.5), (0, 2, 0.5, 0.5)])
    # Duplicate t=0.5 on seg 0 is deduped via set(); seg 0 -> 2 sub-segs
    assert len(result[0:2]) == 2
    np.testing.assert_allclose(result[0], [[0, 0], [1, 0]], atol=1e-9)
    np.testing.assert_allclose(result[1], [[1, 0], [2, 0]], atol=1e-9)
