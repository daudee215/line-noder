# Roadmap

## v0.1 — Initial release (current)

- Pure-NumPy sort-and-sweep bounding-box filter + vectorised parametric intersection.
- Strict interior-intersection detection; endpoint T-junctions handled via node snapping.
- `PlanarGraph(nodes, edges)` output with adjacency helper.
- Optional GeoPandas / Shapely I/O layer (`node_geodataframe`).
- Full test suite (unit + integration on 50×50 grid reference dataset).
- Benchmark suite.

## v0.2 — Performance + robustness

- Bentley-Ottmann sweep-line backend (`backend="bo"` kwarg) for O((N+K) log N) performance on dense networks.
- Collinear overlap detection and merging.
- Tolerance parameter exposed in public API.
- Streaming mode: process line-by-line from a file without loading all geometries into memory.
- CLI entry point: `line-noder node input.gpkg output.gpkg`.

## v1.0 — Stable API

- Stable public API with semantic versioning guarantees.
- Rust extension (via PyO3) for the inner intersection loop — target 10× speedup on 100k+ segment inputs.
- Full verification against PostGIS `ST_Node` reference output on 10 public datasets.
- GeoArrow / GeoParquet I/O.
- Published to conda-forge.
