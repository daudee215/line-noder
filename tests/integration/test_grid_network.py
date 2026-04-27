# SPDX-License-Identifier: MIT
"""Integration test: planar grid network end-to-end.

Uses extended grid lines (start/end outside the intersection zone) so that
every crossing is strictly interior on both segments.  This avoids T-junctions
which are an explicitly documented v0.1 limitation.
"""
import os

import numpy as np

from line_noder import node_lines


def _make_grid(nx: int, ny: int) -> list[np.ndarray]:
    """Create an nx×ny grid of extended lines.

    H-lines at y=1..ny  from x=0 to x=nx+1  (extend past all V-lines)
    V-lines at x=1..nx  from y=0 to y=ny+1  (extend past all H-lines)
    Every crossing (xi, yj) is strictly interior on both lines.
    """
    lines = []
    for i in range(1, ny + 1):
        lines.append(np.array([[0.0, float(i)], [float(nx + 1), float(i)]]))
    for j in range(1, nx + 1):
        lines.append(np.array([[float(j), 0.0], [float(j), float(ny + 1)]]))
    return lines


def test_2x2_grid_topology() -> None:
    """2 h-lines × 2 v-lines: 4 interior intersections, 12 nodes, 12 edges."""
    lines = _make_grid(2, 2)
    g = node_lines(lines)
    # Nodes: 4 interior intersections + 4 H-endpoints + 4 V-endpoints = 12
    assert len(g.nodes) == 12
    # Each H-line (len 3 segs) + each V-line (len 3 segs) = 12 edges
    assert len(g.edges) == 12


def test_5x5_grid_planar() -> None:
    """5×5 grid: 25 interior intersections, verify node count and connectivity."""
    lines = _make_grid(5, 5)
    g = node_lines(lines)
    # 25 interior + 5*2 H-endpoints + 5*2 V-endpoints = 45 nodes
    assert len(g.nodes) == 45
    assert len(g.edges) == 60


def test_reference_grid_dataset() -> None:
    """50×50 reference grid dataset (all intersections interior)."""
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    grid = np.load(os.path.join(data_dir, "grid.npy"))
    lines = [grid[i] for i in range(len(grid))]
    g = node_lines(lines)
    with open(os.path.join(data_dir, "grid_expected.json")) as f:
        import json
        expected = json.load(f)
    assert len(g.nodes) == expected["nodes"], \
        f"Expected {expected['nodes']} nodes, got {len(g.nodes)}"
    assert len(g.edges) == expected["edges"], \
        f"Expected {expected['edges']} edges, got {len(g.edges)}"


def test_graph_connectivity_path() -> None:
    """Every node in a 4×4 extended grid must be reachable from node 0."""
    lines = _make_grid(4, 4)
    g = node_lines(lines)
    adj = g.to_adjacency()
    visited = {0}
    queue = [0]
    while queue:
        n = queue.pop()
        for nb in adj[n]:
            if nb not in visited:
                visited.add(nb)
                queue.append(nb)
    assert visited == set(range(len(g.nodes))), "Graph is not fully connected"
