# line-noder

**Detect all interior line-line intersections and build a planar edge-node graph — pure Python, no PostGIS required.**

## What it does

`line-noder` takes an arbitrary collection of polylines (as NumPy coordinate arrays or a GeoPandas GeoDataFrame) and produces a fully planar topology graph:

- Every crossing point becomes a node.
- Every input segment is split at those points into sub-edges.
- No two edges cross except at shared nodes.

The output is a `PlanarGraph(nodes, edges)` ready for network analysis with NetworkX, routing engines, or spatial databases.

## Why this exists

Pure-Python GIS workflows routinely need to convert a raw line dataset (e.g. road centrelines, utility networks, terrain contours) into a planar graph before routing or topology-based analysis. The existing options require either:

- **PostGIS** — `ST_Node()` is accurate but requires a running server and round-tripping data.
- **ArcGIS** — "Planarize Lines" tool, proprietary licence.
- **momepy / spaghetti / osmnx** — all assume *already-planar* input; none detect crossings.

`line-noder` fills this gap: a single `pip install`, pure NumPy core, MIT licence.

**Source signals:**
- [geopandas/geopandas#1592](https://github.com/geopandas/geopandas/issues/1592) — "ENH: Build line topology for NetworkX" (open since 2019)
- [libgeos/geos#967](https://github.com/libgeos/geos/issues/967) — GEOS noding API discussion
- [GIS.SE 198585](https://gis.stackexchange.com/questions/198585) — "Split lines at intersections" (no pure-Python answer)

## Install

```bash
pip install line-noder            # NumPy core only
pip install "line-noder[geo]"     # + Shapely / GeoPandas helpers
```

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

# With GeoPandas
from line_noder.shapely_io import node_geodataframe
nodes_gdf, edges_gdf = node_geodataframe(road_gdf)
```

## Benchmark

Measured on a 2024 laptop (Intel i7, single thread):

| Dataset | Lines | Intersections | Time |
|---------|-------|---------------|------|
| 100×100 grid | 200 | 10,000 | ~0.4 s |
| 1,000 random | 1,000 | ~variable | ~0.2 s |
| 5,000 random | 5,000 | ~variable | ~4 s |

## Limitations

- O(N²) worst case in the number of segments (bounding-box pre-filter reduces constant significantly for sparse networks).
- Coordinate snapping tolerance is 1e-8 map units; inputs in geographic long/lat near poles will have accuracy issues.
- Collinear overlapping segments are not merged (only crossing intersections are detected).

## Citation

```bibtex
@software{tasleem2026linenoder,
  author  = {Tasleem, Daud},
  title   = {line-noder: planar edge-node graph from arbitrary polylines},
  year    = {2026},
  url     = {https://github.com/daudee215/line-noder},
  version = {0.1.0}
}
```

## License

MIT — see [LICENSE](https://github.com/daudee215/line-noder/blob/main/LICENSE).
