"""
File: hybrid_geometry.py
Author: William Bowley
Version: 1.1
Date: 2025-08-09
Description:
    Draws hybrid geometry to the heat flow
    simulation space for femm.

    Includes all shapes in connectors
"""

from typing import List
import femm
from blueshark.domain.constants import Connection, Connectors
from blueshark.renderer.femm.heat.primitives import (
    _mid_points_line,
    _mid_points_arc
)


def draw_hybrid(edges: List[Connection]) -> None:
    """
    Draws a hybrid geometry to FEMM, using only lines and arcs.

    Args:
        edges: List of connections describing the shape in order
    """
    if not edges:
        raise ValueError("No edges provided for hybrid geometry")

    elements = {
        Connectors.LINE: [],
        Connectors.ARC: []
    }
    for edge in edges:
        edge_type = edge["type"]

        if edge_type == Connectors.LINE:
            elements[Connectors.LINE].append(
                _mid_points_line(
                    edge["start"], edge["end"]
                )
            )
            femm.hi_drawline(
                edge["start"][0], edge["start"][1],
                edge["end"][0], edge["end"][1]
            )

        elif edge_type == Connectors.ARC:
            if edge.get("angle") is None:
                raise ValueError("Arc edge requires an angle (degrees)")
            elements[Connectors.ARC].append(
                _mid_points_arc(
                    edge["start"], edge["end"], (0, 0)
                )
            )
            femm.hi_drawarc(
                edge["start"][0], edge["start"][1],
                edge["end"][0], edge["end"][1],
                edge["angle"],
                1  # maxseg: can be increased for smoother arcs
            )

        else:
            raise ValueError(f"Unknown edge type: {edge_type}")

    return elements
