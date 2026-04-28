# SPDX-License-Identifier: MIT
"""Public API for line-noder."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

from line_noder._geom import extract_segments, segment_bboxes
from line_noder._graph import PlanarGraph, build_graph
from line_noder._intersect import Method, find_intersections
from line_noder._split import split_segments


def node_lines(
    lines: list[ArrayLike],
    method: Method = "auto",
) -> PlanarGraph:
    """Detect all interior line-line intersections and build a planar graph.

    Every input polyline is split at points where it crosses another
    polyline.  The resulting sub-segments are assembled into a
    :class:`~line_noder._graph.PlanarGraph` with unique, snapped nodes.

    Parameters
    ----------
    lines:
        List of coordinate arrays.  Each element must be convertible to an
        ``(N, 2)`` float64 array, where N >= 2.  Coordinates are assumed
        to be in a projected CRS (metres or feet); geographic long/lat is
        accepted but intersection accuracy degrades near the poles.
    method:
        Intersection-detection backend.

        * ``"auto"`` (default) — pick the faster backend automatically:
          ``strtree`` if Shapely is installed and the input has ≥500
          segments, ``pairwise`` otherwise.
        * ``"pairwise"`` — vectorised NumPy pairwise check (v0.1 default).
          O(n²) worst case but lowest constant on small inputs.
        * ``"strtree"`` — Shapely / GEOS Sort-Tile-Recursive R-tree
          spatial index (added in v0.2).  O(n log n) build, O(log n + c)
          per query.  Wins on large sparse inputs.  Requires
          ``pip install 'line-noder[geo]'``.

        All backends produce equivalent topology; only performance differs.

    Returns
    -------
    PlanarGraph
        ``.nodes`` — (N, 2) unique node coordinates.
        ``.edges`` — list of ``(node_idx_a, node_idx_b)`` pairs.

    Examples
    --------
    >>> import numpy as np
    >>> from line_noder import node_lines
    >>> lines = [
    ...     np.array([[0.0, 0.0], [2.0, 2.0]]),
    ...     np.array([[0.0, 2.0], [2.0, 0.0]]),
    ... ]
    >>> g = node_lines(lines)
    >>> len(g.nodes)   # 5 unique nodes
    5
    >>> len(g.edges)   # 4 edges
    4

    Raises
    ------
    ValueError
        If any element of *lines* cannot be converted to a valid (N, 2) array,
        or if *method* is not one of ``"auto" | "pairwise" | "sweep"``.
    """
    if not lines:
        return PlanarGraph()

    # Convert inputs
    np_lines: list[NDArray[np.float64]] = [
        np.asarray(ln, dtype=np.float64) for ln in lines
    ]

    segments, _seg_to_line = extract_segments(np_lines)
    bboxes = segment_bboxes(segments)
    intersections = find_intersections(segments, bboxes, method=method)
    sub_segs = split_segments(segments, intersections)
    return build_graph(sub_segs)
