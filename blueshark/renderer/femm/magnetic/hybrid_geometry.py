"""
File: hybrid_geometry.py
Author: William Bowley
Version: 1.1
Date: 2025-08-09
Description:
    Draws hybrid geometry to the magnetic simulation
    space for femm.

    Includes all shapes in connectors
"""

from typing import List
import femm
from blueshark.domain.constants import Connection, Connectors


def draw_hybrid(edges: List[Connection]) -> None:
    """
    Draws a hybrid geometry to FEMM, using only lines and arcs.

    Args:
        edges: List of connections describing the shape in order
    """
    if not edges:
        raise ValueError("No edges provided for hybrid geometry")

    for edge in edges:
        edge_type = edge["type"]

        if edge_type == Connectors.LINE:
            femm.mi_drawline(
                edge["start"][0], edge["start"][1],
                edge["end"][0], edge["end"][1]
            )

        elif edge_type == Connectors.ARC:
            if edge.get("angle") is None:
                raise ValueError("Arc edge requires an angle (degrees)")
            femm.mi_drawarc(
                edge["start"][0], edge["start"][1],
                edge["end"][0], edge["end"][1],
                edge["angle"],
                1  # maxseg: can be increased for smoother arcs
            )

        else:
            raise ValueError(f"Unknown edge type: {edge_type}")
