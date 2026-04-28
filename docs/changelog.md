# Changelog

## v0.2.0 (2026-04-28)

### Added

- **STRtree backend** for `node_lines()` / `find_intersections()` —
  Sort-Tile-Recursive R-tree (via Shapely / GEOS) replaces the v0.1 O(n²)
  bbox enumeration on large inputs.  Build is O(n log n); per-segment query
  is O(log n + c).
- **`method` parameter** on `node_lines()` and `find_intersections()`:
  `"auto"` (default), `"pairwise"`, `"strtree"`.  `"auto"` picks `strtree`
  when Shapely is installed and the input has ≥ 500 segments, otherwise
  falls back to `"pairwise"`.
- New benchmark suite comparing both backends side-by-side
  (`benchmark/bench_node_lines.py`).

### Performance

Measured on a single CPU thread (NumPy 2.4, Shapely 2.1, Python 3.14):

| Workload                | v0.1 pairwise | v0.2 strtree | Speedup |
|-------------------------|---------------|--------------|--------:|
| 20 000 sparse segments  | 1 057 ms      | 418 ms       |  **2.5×** |
| 5 000 sparse segments   | 113 ms        | 83 ms        |  **1.4×** |
| 1 000 random segments   | 2.1 s         | 1.9 s        |  **1.1×** |
| 100×100 grid            | 129 ms        | 149 ms       |  0.86× — auto stays on pairwise |

The win grows with input size on sparse inputs (road networks, hydro
networks).  On small or dense inputs the pairwise NumPy inner loop wins
on constant factor, so `method="auto"` keeps it as the default below
500 segments.

### Output equivalence

Both backends produce the same set of `(i, j, t, u)` tuples on
non-degenerate inputs — confirmed by 60+ equivalence tests including
regular grids, concurrent lines, and random-input fuzzing across multiple
seeds and sizes.  The order of pairs in the returned list is
implementation-defined and may differ between backends; consumers should
treat the result as a set.

### Notes

- An attempt at a from-scratch Bentley-Ottmann sweep was made but produced
  incorrect results on regular grids with shared endpoints; that work is
  deferred to v0.3.  See [ROADMAP.md](../ROADMAP.md).
- No breaking API changes — all v0.1 calls work unchanged on v0.2.

## v0.1.0 (2026-04-27)

- Initial release.
- Pure-NumPy sort-and-sweep intersection detection.
- `node_lines()` public API.
- Optional GeoPandas I/O via `line_noder.shapely_io`.
