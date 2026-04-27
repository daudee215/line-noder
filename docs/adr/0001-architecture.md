# ADR-0001: Core intersection detection algorithm

**Status:** Accepted  
**Date:** 2026-04-27  
**Context:** line-noder v0.1.0

## Context

To build a planar edge-node graph from arbitrary polylines we must detect all
interior segment-segment intersections efficiently and correctly.  The key
constraints are: (1) pure Python with NumPy only (no PostGIS, no GEOS binding),
(2) correctness verifiable against `ST_Node` reference output, (3) benchmark on
networks of 10,000+ segments in under 10 seconds on commodity hardware.

## Decision

**Sort-and-sweep bounding-box filter + vectorised parametric intersection.**

1. **Bounding-box pre-filter (sweep on x-axis):** Sort segments by `x_min`.
   Walk pairs; for each pair `(i, j)` with `x_min[j] > x_max[i]`, break (no
   more candidates in the sweep window).  Y-overlap is checked explicitly.
   Reduces O(N²) naive pairs to O(N log N + K) where K is the number of
   bbox-overlapping pairs.

2. **Vectorised parametric intersection:** For all candidate pairs gathered in
   step 1, compute `t` and `u` in a single batched NumPy operation using the
   classic cross-product form.  Strictly-interior test: `_INTERIOR < t < 1 -
   _INTERIOR` and same for `u`.  Collinear / parallel pairs (cross product ≈ 0)
   are skipped.

3. **Segment splitting:** For each segment, collect all `t` values, sort, and
   split into sub-segments.  Preserves original coordinate direction.

4. **Node snapping:** Endpoints of sub-segments are rounded to a grid of
   spacing `1e-8` to collapse near-duplicate points into a single node.  This
   prevents the graph from accumulating ghost nodes from floating-point drift.

## Rejected alternatives

### Alternative A: Shamos-Hoey / Bentley-Ottmann sweep line

The Bentley-Ottmann algorithm achieves O((N + K) log N) time, which is
asymptotically superior.  It was rejected for v0.1 because:
- A correct Python implementation of the event-queue + segment-order BST is
  ~500 lines of careful code with many degenerate-case traps.
- For the target use case (road networks: N ≤ 50,000 segments with sparse
  intersections) the sort-and-sweep pre-filter achieves similar practical
  performance.
- Scheduled for v0.2 as an opt-in backend.

### Alternative B: Shapely STRtree bulk query

`shapely.STRtree.query(geom, predicate="crosses")` would find all crossing
pairs in ~5 lines.  Rejected because it introduces Shapely as a hard
dependency, making the pure-NumPy core unachievable.  Shapely is available as
an optional `[geo]` extra and is used for GeoDataFrame I/O.

### Alternative C: PostGIS `ST_Node` via psycopg2

Accurate but requires a running PostgreSQL/PostGIS instance, round-trip
serialisation, and a network connection.  Excluded by the "no server required"
design constraint.

## Consequences

- Pure-NumPy core is importable in any Python 3.10+ environment.
- The sort-and-sweep filter degrades to O(N²) on fully-dense inputs (every
  bbox overlaps every other); this is acceptable for v0.1 and documented in
  the Limitations section.
- Bentley-Ottmann backend is the primary v0.2 milestone.
