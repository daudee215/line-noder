# line-noder

[![CI](https://github.com/daudee215/line-noder/actions/workflows/ci.yml/badge.svg)](https://github.com/daudee215/line-noder/actions)
[![PyPI](https://img.shields.io/pypi/v/line-noder)](https://pypi.org/project/line-noder/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)

**Detect all interior line-line intersections and build a planar edge-node graph — pure Python, no PostGIS required.**

## What it does

`line-noder` takes a collection of polylines and produces a fully planar topology graph:

- Every crossing point becomes a **node**.
- Every input segment is **split** at those points into sub-edges.
- No two edges cross except at shared nodes.

The output is a `PlanarGraph(nodes, edges)` directly usable with NetworkX, routing engines, or spatial databases.

## Why this exists

Converting raw line data to a planar graph is a prerequisite for routing, network analysis, and topology repair.
The existing Python options all fall short:

| Tool | Limitation |
|------|-----------|
| PostGIS `ST_Node` | Requires a running server |
| ArcGIS "Planarize Lines" | Proprietary licence |
| momepy / spaghetti / osmnx | Assume already-planar input |
| geoplanar | Polygon topology only, not polylines |

`line-noder` fills this gap. Pure NumPy, MIT licence, `pip install`.

**Source signals that motivated this tool:**
- [geopandas/geopandas#1592](https://github.com/geopandas/geopandas/issues/1592) — "ENH: Build line topology in dataframe for NetworkX" (open 2019–present)
- [libgeos/geos#967](https://github.com/libgeos/geos/issues/967) — GEOS noding API discussion (21 comments)
- [GIS.SE 198585](https://gis.stackexchange.com/questions/198585/split-lines-at-intersections-in-arcgis) — "Split lines at intersections" (no pure-Python answer accepted)

## Install

```bash
pip install line-noder              # NumPy core only — pairwise backend
pip install "line-noder[geo]"       # + Shapely / GeoPandas — enables strtree
```

**Requirements:** Python ≥ 3.10, NumPy ≥ 1.24. Shapely ≥ 2.0 unlocks the
`strtree` backend (v0.2+) and the GeoDataFrame I/O helpers.

## Quickstart

```python
import numpy as np
from line_noder import node_lines

lines = [
    np.array([[0.0, 0.0], [4.0, 4.0]]),
    np.array([[0.0, 4.0], [4.0, 0.0]]),
    np.array([[2.0, 0.0], [2.0, 4.0]]),
]
g = node_lines(lines)
print(f"{len(g.nodes)} nodes, {len(g.edges)} edges")
# → 7 nodes, 6 edges

# Build a NetworkX graph
import networkx as nx
G = nx.Graph()
G.add_nodes_from(range(len(g.nodes)))
G.add_edges_from(g.edges)
```

### With GeoPandas

```python
import geopandas as gpd
from line_noder.shapely_io import node_geodataframe

roads = gpd.read_file("roads.gpkg")
nodes_gdf, edges_gdf = node_geodataframe(roads)
edges_gdf.to_file("roads_planar.gpkg")
```

## API Reference

See the [full API docs](https://daudee215.github.io/line-noder/api/).

### `node_lines(lines, method="auto") → PlanarGraph`

| Parameter | Type | Description |
|-----------|------|-------------|
| `lines` | `list[ArrayLike]` | Each element: `(N, 2)` coordinate array, N ≥ 2 |
| `method` | `"auto" \| "pairwise" \| "strtree"` | Backend selector. `"auto"` picks `strtree` when Shapely is available and the input has ≥ 500 segments, otherwise `"pairwise"`. |

**Returns** `PlanarGraph` with `.nodes` `(N,2)` array and `.edges` list of `(int, int)` pairs.

### Backends

| Backend | Algorithm | Build | Query | Best for |
|---------|-----------|------:|------:|----------|
| `pairwise` (v0.1+) | x-sort bbox sweep + vectorised NumPy parametric test | — | O(n²) | small or dense inputs |
| `strtree` (v0.2+) | Shapely / GEOS Sort-Tile-Recursive R-tree + same parametric test | O(n log n) | O(log n + c) per segment | large sparse inputs (road / hydro networks) |

Both backends produce equivalent topology — only performance differs. Output equivalence is enforced by 50+ tests on regular grids, concurrent lines, shared endpoints, and random fuzzing.

## Benchmark

Single thread, NumPy 2.4 + Shapely 2.1 on Python 3.14:

| Workload | Segments | v0.1 pairwise | v0.2 strtree | Speedup |
|----------|---------:|--------------:|-------------:|--------:|
| Sparse network | 20 000 | 1 057 ms | 418 ms | **2.5×** |
| Sparse network | 5 000 | 113 ms | 83 ms | **1.4×** |
| Random lines | 1 000 | 2.1 s | 1.9 s | 1.1× |
| 100×100 grid | 200 | 129 ms | 149 ms | auto stays on pairwise |

Speedup grows with input size on sparse data. On dense or small inputs the pairwise NumPy inner loop is competitive on constant factor, so `method="auto"` keeps it as the default below 500 segments.

Reproduce with `pytest benchmark/ --benchmark-only`.

## Limitations

- Pairwise backend: O(N²) worst case on fully-dense inputs.
- Strtree backend: requires Shapely; falls back to pairwise when missing.
- Coordinate snapping tolerance is 1e-8 map units; geographic CRS near the poles will have reduced accuracy.
- Collinear overlapping segments are not merged in v0.2 — planned for v0.3.

## Architecture

See [docs/adr/0001-architecture.md](docs/adr/0001-architecture.md) for the algorithm choice and rejected alternatives.

## Citation

```bibtex
@software{tasleem2026linenoder,
  author  = {Tasleem, Daud},
  title   = {line-noder: planar edge-node graph from arbitrary polylines},
  year    = {2026},
  url     = {https://github.com/daudee215/line-noder},
  version = {0.2.0}
}
```

## License

MIT — see [LICENSE](LICENSE).
