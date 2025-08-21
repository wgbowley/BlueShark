"""
Filename: map.py
Author: William Bowley
Version: 0.1
Date: 2025-08-16

Description:
    This addon aims to add topology optimization
    to the framework for all solvers

    This module adds perimeters for the
    topology map
"""

from typing import List
from blueshark.domain.constants import Connection, Connectors
from blueshark.addons.topology.operators import draw_line, draw_arc


def draw_hybrid(
    topology_map: list[list[int]],
    material: int,
    edges: List[Connection]
) -> None:
    """
    Draws a hybrid geometry to topology map, using only lines and arcs.

    Args:
        edges: List of connections describing the shape in order
    """
    if not edges:
        raise ValueError("No edges provided for hybrid geometry")

    for edge in edges:
        edge_type = edge["type"]

        if edge_type == Connectors.LINE:
            draw_line(
                topology_map,
                edge["start"],
                edge["end"],
                material
            )

        elif edge_type == Connectors.ARC:
            if edge.get("angle") is None:
                raise ValueError("Arc edge requires an angle (degrees)")
            draw_arc(
                topology_map,
                edge["start"],
                edge["end"],
                edge["angle"],
                material
            )

        else:
            raise ValueError(f"Unknown edge type: {edge_type}")
