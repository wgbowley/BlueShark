
"""
Filename: renderer.py
Author: William Bowley
Version: 0.1
Date: 2025-08-16

Description:
    This addon aims to add topology optimization
    to the framework for all solvers
"""

from blueshark.domain.constants import (
    Geometry,
    ShapeType,
    SimulationType
)
# from blueshark.domain.generation.geometric_centroid import (
#     centroid_point
# )
# from blueshark.addons.topology.filling import (
#     fill_polygon
# )
from blueshark.addons.topology.primitives import (
    draw_hybrid,
    draw_annulus_circle,
    draw_annulus_sector,
    draw_circle,
    draw_polygon
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
        sim_type: SimulationType,
    ) -> None:
        """
        Initializes the topology optimizer
        """
        self.window = (x_size, y_size)
        self.materials = materials
        self.type = sim_type
        self.topology_map = []

        # Calculates shift value for simulation types
        x, y = 0, 0
        if sim_type == SimulationType.PLANAR:
            x = int(self.window[0] // 2)
            y = int(self.window[0] // 2)

        self.shift = (x, y)

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
        tag_coords: None = None
    ) -> None:
        """
        Draws element to the topology map
        """

        if material not in self.materials:
            raise ValueError(f"{material} was not defined in __init__")

        shape = geometry.get("shape")
        match shape:
            case ShapeType.POLYGON | ShapeType.RECTANGLE:
                points = draw_polygon(
                    geometry["points"],
                    self.materials[material]
                )

            case ShapeType.CIRCLE:
                points = draw_circle(
                    geometry["radius"],
                    geometry["center"],
                    self.materials[material]
                )

            case ShapeType.ANNULUS_SECTOR:
                points = draw_annulus_sector(
                    geometry["center"],
                    geometry["radius_outer"],
                    geometry["radius_inner"],
                    geometry["start_angle"],
                    geometry["end_angle"],
                    self.materials[material]
                )

            case ShapeType.ANNULUS_CIRCLE:
                points = draw_annulus_circle(
                    geometry["center"],
                    geometry["radius_outer"],
                    geometry["radius_inner"],
                    self.materials[material]
                )

            case ShapeType.HYBRID:
                points = draw_hybrid(
                    self.materials[material],
                    geometry["edges"]
                )

            case _:
                raise NotImplementedError(f"Shape '{shape}' not supported")

        # Draws the outline to the voxel map
        for point in points:
            self._set_points(point[0], point[1])

        # if tag_coords is None:
        #     tag_coords = centroid_point(geometry)

        # fill = fill_polygon(
        #     points,
        #     self.materials[material],
        #     2
        # )
        # for point in fill:
        #     self._set_points(point[0], point[1])

    def _set_points(
        self,
        coord: tuple[int, int],
        material: int
    ) -> None:
        """
        Sets the material of the topology map

        Args:
            Coord: (x,y) value of the point
            material: Material type of that point
        """
        x, y = coord
        shifted = (x + self.shift[0], y + self.shift[1])
        self.topology_map[shifted[1]][shifted[0]] = material
