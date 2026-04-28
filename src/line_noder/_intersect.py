# SPDX-License-Identifier: MIT
"""Segment-segment interior intersection detection.

Two backends are available:

* ``"pairwise"`` (v0.1 default) — bbox-x-sort pre-filter + vectorised
  parametric intersection on candidate pairs.  Worst case O(n²); fast on
  small or dense inputs because the inner loop is pure NumPy.
* ``"strtree"`` (added in v0.2) — Sort-Tile-Recursive R-tree (via Shapely
  / GEOS) for the candidate-pair stage, then the same vectorised parametric
  test as the pairwise backend.  O(n log n) build + O(log n + c) per query.
  Wins on large sparse inputs (road networks, river networks).  Requires
  ``pip install 'line-noder[geo]'``.

Both produce identical output on non-degenerate inputs: interior-only
intersections, where endpoints touching another segment are NOT reported.
"""

from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import NDArray

_EPS = 1e-10  # parallel / collinear tolerance
_INTERIOR = 1e-9  # strict interior: t, u must be in (_INTERIOR, 1-_INTERIOR)

# Switchover threshold for method="auto".  The STRtree backend has a higher
# per-segment constant (LineString construction, R-tree build) than the
# pure-NumPy pairwise check, so for small n the pairwise backend is faster
# despite the worse asymptotic.  Empirically the crossover is around 500
# segments on sparse inputs.
_AUTO_THRESHOLD = 500

Method = Literal["auto", "pairwise", "strtree"]


def _auto_pick(n: int) -> Method:
    """Resolve ``method='auto'`` to a concrete backend.

    Picks ``strtree`` when shapely is importable and the input is large
    enough to justify the per-segment overhead; otherwise ``pairwise``.
    """
    if n < _AUTO_THRESHOLD:
        return "pairwise"
    try:
        import shapely  # noqa: F401
    except ImportError:
        return "pairwise"
    return "strtree"


def _bbox_candidates(
    bboxes: NDArray[np.float64],
) -> tuple[NDArray[np.intp], NDArray[np.intp]]:
    """Return index pairs (i, j) with i < j whose bounding boxes overlap."""
    xmin, ymin, xmax, ymax = (bboxes[:, k] for k in range(4))
    n = len(bboxes)
    order = np.argsort(xmin)
    pairs_i: list[int] = []
    pairs_j: list[int] = []
    for k in range(n):
        i = order[k]
        for m in range(k + 1, n):
            j = order[m]
            if xmin[j] > xmax[i] + _EPS:
                break
            if ymax[i] >= ymin[j] - _EPS and ymax[j] >= ymin[i] - _EPS:
                pairs_i.append(i)
                pairs_j.append(j)
    if not pairs_i:
        return np.empty(0, np.intp), np.empty(0, np.intp)
    return np.array(pairs_i, np.intp), np.array(pairs_j, np.intp)


def find_intersections(
    segments: NDArray[np.float64],
    bboxes: NDArray[np.float64],
    method: Method = "auto",
) -> list[tuple[int, int, float, float]]:
    """Find all interior-interior segment intersections.

    Parameters
    ----------
    segments : (M, 2, 2)
    bboxes   : (M, 4)  [xmin, ymin, xmax, ymax]
    method   : ``"auto"`` (default), ``"pairwise"``, or ``"sweep"``.
        ``"auto"`` picks ``sweep`` when M ≥ 300 and ``pairwise`` otherwise.

    Returns
    -------
    List of ``(i, j, t_i, t_j)`` where ``t_i`` is the parameter on segment
    i (0 = start, 1 = end) and ``t_j`` likewise, both strictly interior.
    The order of pairs in the returned list is implementation-defined and
    differs between backends; consumers should treat the result as a set.
    """
    if method == "auto":
        method = _auto_pick(len(segments))
    if method == "strtree":
        from line_noder._strtree import find_intersections_strtree
        return find_intersections_strtree(segments, bboxes)
    if method != "pairwise":
        raise ValueError(
            f"method must be 'auto', 'pairwise', or 'strtree'; got {method!r}"
        )
    ci, cj = _bbox_candidates(bboxes)
    if len(ci) == 0:
        return []

    # Vectorised parametric intersection for all candidate pairs
    # Segment i: P = p0 + t*(p1-p0)
    # Segment j: Q = q0 + u*(q1-q0)
    p0 = segments[ci, 0]   # (K, 2)
    p1 = segments[ci, 1]
    q0 = segments[cj, 0]
    q1 = segments[cj, 1]

    rv = p1 - p0   # direction vectors (K, 2)
    sv = q1 - q0
    rxs = rv[:, 0] * sv[:, 1] - rv[:, 1] * sv[:, 0]  # cross(r, s)
    non_parallel = np.abs(rxs) > _EPS

    results: list[tuple[int, int, float, float]] = []
    if not np.any(non_parallel):
        return results

    idx = np.where(non_parallel)[0]
    ac = q0[idx] - p0[idx]  # (P, 2)

    t = (ac[:, 0] * sv[idx, 1] - ac[:, 1] * sv[idx, 0]) / rxs[idx]
    u = (ac[:, 0] * rv[idx, 1] - ac[:, 1] * rv[idx, 0]) / rxs[idx]

    interior = (
        (t > _INTERIOR) & (t < 1.0 - _INTERIOR) &
        (u > _INTERIOR) & (u < 1.0 - _INTERIOR)
    )
    for k in np.where(interior)[0]:
        orig = idx[k]
        results.append((int(ci[orig]), int(cj[orig]), float(t[k]), float(u[k])))
    return results
