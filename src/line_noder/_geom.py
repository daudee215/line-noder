# SPDX-License-Identifier: MIT
"""Geometry primitives — segment extraction and bounding-box helpers."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def extract_segments(
    lines: list[NDArray[np.float64]],
) -> tuple[NDArray[np.float64], NDArray[np.intp]]:
    """Flatten a list of polylines into individual segments.

    Parameters
    ----------
    lines:
        Each element is an (N, 2) coordinate array representing one polyline.

    Returns
    -------
    segments : (M, 2, 2) array
        ``segments[i] = [[x0,y0],[x1,y1]]`` for the i-th segment.
    seg_to_line : (M,) int array
        ``seg_to_line[i]`` is the index of the source polyline.
    """
    all_segs: list[NDArray[np.float64]] = []
    all_ids: list[int] = []
    for line_idx, coords in enumerate(lines):
        coords = np.asarray(coords, dtype=np.float64)
        if coords.ndim != 2 or coords.shape[1] != 2:
            raise ValueError(
                f"Line {line_idx}: expected shape (N, 2), got {coords.shape}"
            )
        if len(coords) < 2:
            raise ValueError(f"Line {line_idx}: needs at least 2 points")
        for i in range(len(coords) - 1):
            all_segs.append(coords[i : i + 2])
            all_ids.append(line_idx)
    segments = np.stack(all_segs, axis=0)  # (M, 2, 2)
    seg_to_line = np.array(all_ids, dtype=np.intp)
    return segments, seg_to_line


def segment_bboxes(segments: NDArray[np.float64]) -> NDArray[np.float64]:
    """Return (M, 4) array of [xmin, ymin, xmax, ymax] for each segment."""
    xs = segments[:, :, 0]  # (M, 2)
    ys = segments[:, :, 1]
    return np.column_stack([xs.min(1), ys.min(1), xs.max(1), ys.max(1)])
