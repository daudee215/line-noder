# SPDX-License-Identifier: MIT
"""Build a planar node-edge graph from split sub-segments."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

_SNAP = 1e-8  # coordinate tolerance for node deduplication


@dataclass
class PlanarGraph:
    """Result of :func:`~line_noder.api.node_lines`.

    Attributes
    ----------
    nodes : (N, 2) float64 array
        Unique node coordinates.  Nodes include all original polyline
        endpoints and every interior intersection point.
    edges : list of (int, int) tuples
        Each edge is a pair of node indices.  The graph is undirected;
        each edge is stored once (lower index first is not guaranteed —
        use ``frozenset(e)`` for equality checks).
    """

    nodes: NDArray[np.float64] = field(default_factory=lambda: np.empty((0, 2)))
    edges: list[tuple[int, int]] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.edges)

    def to_adjacency(self) -> dict[int, list[int]]:
        """Return adjacency list {node_idx: [neighbour_idx, ...]}."""
        adj: dict[int, list[int]] = {i: [] for i in range(len(self.nodes))}
        for a, b in self.edges:
            adj[a].append(b)
            adj[b].append(a)
        return adj


def build_graph(sub_segments: list[NDArray[np.float64]]) -> PlanarGraph:
    """Build a :class:`PlanarGraph` from a list of split sub-segments.

    Parameters
    ----------
    sub_segments:
        Each element is a (2, 2) array ``[[x0,y0],[x1,y1]]``.

    Returns
    -------
    PlanarGraph with deduplicated nodes and edges.
    """
    if not sub_segments:
        return PlanarGraph()

    node_coords: list[NDArray[np.float64]] = []
    node_lookup: dict[tuple[float, float], int] = {}

    def _snap(pt: NDArray[np.float64]) -> tuple[float, float]:
        # Round to SNAP grid for deduplication
        factor = 1.0 / _SNAP
        return (round(float(pt[0]) * factor) / factor,
                round(float(pt[1]) * factor) / factor)

    def _get_or_add(pt: NDArray[np.float64]) -> int:
        key = _snap(pt)
        if key not in node_lookup:
            node_lookup[key] = len(node_coords)
            node_coords.append(np.array([key[0], key[1]], dtype=np.float64))
        return node_lookup[key]

    edges: list[tuple[int, int]] = []
    for seg in sub_segments:
        a = _get_or_add(seg[0])
        b = _get_or_add(seg[1])
        if a != b:
            edges.append((a, b))

    nodes = np.stack(node_coords, axis=0) if node_coords else np.empty((0, 2))
    return PlanarGraph(nodes=nodes, edges=edges)
