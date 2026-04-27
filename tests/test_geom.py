# SPDX-License-Identifier: MIT
"""Unit tests for _geom module."""
import numpy as np
import pytest

from line_noder._geom import extract_segments, segment_bboxes


def test_extract_two_lines() -> None:
    lines = [
        np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]]),
        np.array([[0.0, 1.0], [1.0, 1.0]]),
    ]
    segs, ids = extract_segments(lines)
    assert segs.shape == (3, 2, 2)
    assert list(ids) == [0, 0, 1]


def test_extract_single_segment() -> None:
    lines = [np.array([[0.0, 0.0], [1.0, 1.0]])]
    segs, ids = extract_segments(lines)
    assert segs.shape == (1, 2, 2)
    assert ids[0] == 0


def test_invalid_shape_raises() -> None:
    with pytest.raises(ValueError):
        extract_segments([np.array([1.0, 2.0])])  # 1-D array


def test_too_short_raises() -> None:
    with pytest.raises(ValueError):
        extract_segments([np.array([[1.0, 2.0]])])  # only one point


def test_bboxes_simple() -> None:
    lines = [np.array([[1.0, 3.0], [4.0, 0.0]])]
    segs, _ = extract_segments(lines)
    bb = segment_bboxes(segs)
    assert bb.shape == (1, 4)
    np.testing.assert_allclose(bb[0], [1.0, 0.0, 4.0, 3.0])


def test_bboxes_horizontal() -> None:
    lines = [np.array([[0.0, 2.0], [5.0, 2.0]])]
    segs, _ = extract_segments(lines)
    bb = segment_bboxes(segs)
    np.testing.assert_allclose(bb[0], [0.0, 2.0, 5.0, 2.0])
