# SPDX-License-Identifier: MIT
"""line-noder: planar edge-node graph from arbitrary polylines.

Detects all interior line-line intersections and splits source lines at those
points, yielding a fully planar graph where every edge connects two nodes and
no two edges cross except at shared nodes.

Quickstart::

    import numpy as np
    from line_noder import node_lines

    lines = [
        np.array([[0.0, 0.0], [2.0, 2.0]]),   # diagonal
        np.array([[0.0, 2.0], [2.0, 0.0]]),   # crosses at (1, 1)
    ]
    result = node_lines(lines)
    print(result.nodes)   # array([[0,0],[1,1],[2,2],[0,2],[2,0]])
    print(result.edges)   # [(0,1),(1,2),(3,1),(1,4)]
"""

from line_noder._graph import PlanarGraph
from line_noder.api import node_lines

__all__ = ["node_lines", "PlanarGraph"]
__version__ = "0.2.0"
