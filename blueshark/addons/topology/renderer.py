
"""
Filename: topology.py
Author: William Bowley
Version: 0.1
Date: 2025-08-16

Description:
    This addon aims to add topology optimization
    to the framework for all solvers
"""

from blueshark.domain.constants import (
    Geometry,
    ShapeType
)
from blueshark.addons.topology.primitives import (
    draw_hybrid
)


class TopologyRenderer:
    """
    Topology renderer for blueshark framework
    """
    def __init__(
        self,
        x_size: int,
        y_size: int,
        materials: dict[str, int],
        centered: bool = False, 
    ) -> None:
        """
        Initializes the topology optimizer
        """
        self.window = (x_size, y_size)
        self.materials = materials
        self.topology_map = []
        self.centered = centered

    def initalize_map(
        self,
        default_material: str
    ) -> list[list[int]]:
        """
        Initalizes the topology map
        """

        topology_map = []
        for _ in range(0, self.window[1]):
            row = []
            for _ in range(0, self.window[0]):
                row.append(self.materials[default_material])
            topology_map.append(row)

        self.topology_map = topology_map

    def draw(
        self,
        geometry: Geometry,
        material: str,
    ) -> None:
        """
        Draws element to the topology map
        """

        if material not in self.materials:
            raise ValueError(f"{material} was not defined in __init__")

        shape = geometry.get("shape")
        match shape:
            # case ShapeType.POLYGON | ShapeType.RECTANGLE:

            # case ShapeType.CIRCLE:

            # case ShapeType.ANNULUS_SECTOR:

            # case ShapeType.ANNULUS_CIRCLE:

            case ShapeType.HYBRID:
                draw_hybrid(
                    self.topology_map,
                    self.materials[material],
                    geometry["edges"]
                )

            case _:
                raise NotImplementedError(f"Shape '{shape}' not supported")
