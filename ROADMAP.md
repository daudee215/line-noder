# Roadmap

## v0.1 — Initial release

- Pure-NumPy sort-and-sweep bounding-box filter + vectorised parametric intersection.
- Strict interior-intersection detection; endpoint T-junctions handled via node snapping.
- `PlanarGraph(nodes, edges)` output with adjacency helper.
- Optional GeoPandas / Shapely I/O layer (`node_geodataframe`).
- Full test suite (unit + integration on 50×50 grid reference dataset).
- Benchmark suite.

## v0.2 — STRtree backend (current)

- ✅ STRtree (Sort-Tile-Recursive R-tree, via Shapely / GEOS) backend for the
  candidate-pair stage. O(n log n) build, O(log n + c) per query.
- ✅ `method="auto" | "pairwise" | "strtree"` parameter on `node_lines()` and
  `find_intersections()`. `"auto"` picks `strtree` when Shapely is available
  and n ≥ 500.
- ✅ 50+ new equivalence tests across regular grids, concurrent lines,
  shared endpoints, and random-input fuzzing.
- ✅ Side-by-side benchmark suite — 2.5× speedup at 20k sparse segments.

## v0.3 — Algorithmic depth

- Bentley-Ottmann sweep-line backend (`method="sweep"`) — true O((n+k) log n).
  An initial implementation was attempted in v0.2 but produced incorrect
  output on configurations with many coincident endpoints (e.g. regular
  grids).  The next attempt will use either symbolic perturbation or
  GEOS's noding API for the degenerate cases.
- Collinear overlap detection and merging.
- Tolerance parameter exposed in public API.
- CLI entry point: `line-noder node input.gpkg output.gpkg`.

## v1.0 — Stable API

- Stable public API with semantic versioning guarantees.
- Rust extension (via PyO3) for the inner intersection loop — target 10×
  speedup on 100k+ segment inputs.
- Streaming mode: process line-by-line from a file without loading all
  geometries into memory.
- Full verification against PostGIS `ST_Node` reference output on 10 public
  datasets.
- GeoArrow / GeoParquet I/O.
- Published to conda-forge.
