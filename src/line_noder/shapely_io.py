# SPDX-License-Identifier: MIT
"""Optional Shapely / GeoPandas I/O helpers.

Install the ``geo`` extra to use these::

    pip install line-noder[geo]
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import geopandas as gpd

from line_noder.api import node_lines


def node_geodataframe(
    gdf: gpd.GeoDataFrame,
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Node a GeoDataFrame of LineString / MultiLineString geometries.

    Parameters
    ----------
    gdf:
        A GeoDataFrame whose geometry column contains LineString or
        MultiLineString geometries.

    Returns
    -------
    nodes_gdf, edges_gdf : GeoDataFrames
        *nodes_gdf* has a ``Point`` geometry column.
        *edges_gdf* has a ``LineString`` geometry column, plus
        ``node_start`` and ``node_end`` integer columns.

    Raises
    ------
    ImportError
        If ``geopandas`` or ``shapely`` are not installed.
    """
    try:
        import geopandas as gpd_rt
        from shapely.geometry import LineString, Point
    except ImportError as exc:
        raise ImportError(
            "Install the 'geo' extra: pip install line-noder[geo]"
        ) from exc

    lines = []
    for geom in gdf.geometry:
        if geom.geom_type == "LineString":
            lines.append(np.array(geom.coords))
        elif geom.geom_type == "MultiLineString":
            for part in geom.geoms:
                lines.append(np.array(part.coords))
        else:
            raise ValueError(
                f"Unsupported geometry type: {geom.geom_type}. "
                "Expected LineString or MultiLineString."
            )

    graph = node_lines(lines)

    nodes_gdf = gpd_rt.GeoDataFrame(
        {"node_id": range(len(graph.nodes))},
        geometry=[Point(xy) for xy in graph.nodes],
        crs=gdf.crs,
    )
    edges_gdf = gpd_rt.GeoDataFrame(
        {
            "node_start": [e[0] for e in graph.edges],
            "node_end": [e[1] for e in graph.edges],
        },
        geometry=[
            LineString([graph.nodes[a], graph.nodes[b]])
            for a, b in graph.edges
        ],
        crs=gdf.crs,
    )
    return nodes_gdf, edges_gdf
