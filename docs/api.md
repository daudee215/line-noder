# API Reference

## `node_lines`

```python
from line_noder import node_lines

node_lines(lines: list[ArrayLike]) -> PlanarGraph
```

**Parameters**

- `lines` — list of coordinate arrays, each convertible to `(N, 2)` float64 with N ≥ 2.

**Returns** a `PlanarGraph` with:
- `.nodes` — `(N, 2)` float64 array of unique node coordinates.
- `.edges` — list of `(int, int)` node-index pairs.
- `.to_adjacency()` — returns `{node_idx: [neighbour_idx, ...]}` dict.

**Raises** `ValueError` if any element has wrong shape or fewer than 2 points.

---

## `PlanarGraph`

```python
from line_noder import PlanarGraph
```

Dataclass returned by `node_lines`.

| Attribute | Type | Description |
|-----------|------|-------------|
| `.nodes` | `ndarray (N, 2)` | Unique node coordinates |
| `.edges` | `list[tuple[int,int]]` | Edge pairs as node indices |
| `len(g)` | `int` | Number of edges |
| `.to_adjacency()` | `dict` | Adjacency list |

---

## `node_geodataframe` (optional, requires `[geo]` extra)

```python
from line_noder.shapely_io import node_geodataframe

nodes_gdf, edges_gdf = node_geodataframe(gdf)
```

**Parameters**

- `gdf` — `geopandas.GeoDataFrame` with `LineString` or `MultiLineString` geometry column.

**Returns**

- `nodes_gdf` — `GeoDataFrame` with `Point` geometry and `node_id` column.
- `edges_gdf` — `GeoDataFrame` with `LineString` geometry, `node_start`, `node_end` columns.
