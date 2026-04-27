# SPDX-License-Identifier: MIT
"""Split segments at detected intersection t-parameters."""

from __future__ import annotations

from collections import defaultdict

import numpy as np
from numpy.typing import NDArray


def split_segments(
    segments: NDArray[np.float64],
    intersections: list[tuple[int, int, float, float]],
) -> list[NDArray[np.float64]]:
    """Split each segment at all intersection t-parameters.

    Parameters
    ----------
    segments : (M, 2, 2)
    intersections : list of (seg_i, seg_j, t_i, t_j)

    Returns
    -------
    List of (2, 2) arrays — the sub-segments after splitting.
    The order within each original segment is preserved (sorted by t).
    """
    # Collect split parameters per segment
    split_params: dict[int, list[float]] = defaultdict(list)
    for si, sj, ti, tj in intersections:
        split_params[si].append(ti)
        split_params[sj].append(tj)

    result: list[NDArray[np.float64]] = []
    for idx in range(len(segments)):
        seg_start = segments[idx, 0]
        seg_end   = segments[idx, 1]
        ts = sorted(set(split_params.get(idx, [])))
        breakpoints = [0.0] + ts + [1.0]
        for k in range(len(breakpoints) - 1):
            t0, t1 = breakpoints[k], breakpoints[k + 1]
            p0 = seg_start + t0 * (seg_end - seg_start)
            p1 = seg_start + t1 * (seg_end - seg_start)
            result.append(np.stack([p0, p1]))
    return result
