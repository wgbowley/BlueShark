
"""
Filename: renderer.py
Author: William Bowley
Version: 0.1
Date: 2025-08-16

Description:
    This addon aims to add topology optimization
    to the framework for all solvers
"""

from random import random
from typing import Tuple, Dict, List

from blueshark.domain.constants import (
    Geometry,
    ShapeType,
    SimulationType
)
from blueshark.domain.generation.geometric_centroid import (
    centroid_point
)

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
        materials: Dict[str, int],
        sim_type: SimulationType,
    ) -> None:
        """
        Initializes the topology optimizer
        """
        self.window = (x_size, y_size)
        self.materials = materials
        self.type = sim_type
        self.voxel_map = []

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
        Initalizes the voxel map
        """

        voxel_map = []
        for _ in range(0, self.window[1]):
            row = []
            for _ in range(0, self.window[0]):
                row.append(self.materials[default_material])
            voxel_map.append(row)

        self.voxel_map = voxel_map

    def draw(
        self,
        geometry: Geometry,
        material: str,
        tag_coords: None = None
    ) -> None:
        """
        Draws element to the voxel map

        Args:
            Geometry: Shape geometry
            material: Material type of that region
            tag_coords: Centroid of the shape
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

        # Gets centroid if no tags are prescribed
        if tag_coords is None:
            tag_coords = centroid_point(geometry)

        tag_coords = (int(tag_coords[0]), int(tag_coords[1]))
        self._fill__regions(tag_coords, self.materials[material])

    def mutation(
        self,
        material: int,
        probability: int,
    ) -> None:
        """
        Mutates only the boundary voxels of the selected material with
        probability of change p in [-1,1]. Where negative is removal
        and positive is addition
        """

        voxel_map = self.voxel_map
        columns, rows = self.window

        mat_index = self.materials[material]
        boundaries = self._find_boundaries(mat_index)
        step_pattern = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for y, x in boundaries:
            if probability < 0 and random() < abs(probability):
                voxel_map[y][x] = self._find_material(
                    (y, x),
                    mat_index
                )

            if probability > 0 and random() < abs(probability):
                for dy, dx in step_pattern:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < rows and 0 <= nx < columns:
                        voxel_map[ny][nx] = mat_index

    def _set_points(
        self,
        coord: Tuple[int, int],
        material: int
    ) -> None:
        """
        Sets the material of the topology map

        Args:
            Coord: (y,x) value of the point
            material: Material type of that point
        """
        x, y = coord
        shifted = (x + self.shift[0], y + self.shift[1])
        self.voxel_map[shifted[1]][shifted[0]] = material

    def _fill__regions(
        self,
        centroid: Tuple[int, int],
        material: int
    ) -> None:
        """
        Sets the material of a enclosed region using
        depth-first search (DFS) flood fill

        Args:
            Centroid: (x,y) Before shifting toward center
            Material: Material type of the enclosed region
        """
        x, y = (centroid[0] + self.shift[0], centroid[1] + self.shift[1])
        voxel_map = self.voxel_map

        # Checks if the region is already filled
        if voxel_map[y][x] == material:
            return

        original_material = voxel_map[y][x]
        m, n = len(voxel_map), len(voxel_map[0])
        stack = [(y, x)]

        while stack:
            cy, cx = stack.pop()
            if voxel_map[cy][cx] == original_material:
                voxel_map[cy][cx] = material

                # neighbors (up, down, left, right)
                if cy + 1 < m:
                    stack.append((cy + 1, cx))
                if cy - 1 >= 0:
                    stack.append((cy - 1, cx))
                if cx + 1 < n:
                    stack.append((cy, cx + 1))
                if cx - 1 >= 0:
                    stack.append((cy, cx - 1))

    def _find_boundaries(
        self,
        material_index: int
    ) -> List[Tuple[int, int]]:
        """
        Finds boundary voxels of the given material region

        Definition of boundary voxel:
        - Has at least one neighbor with a different material
          or lies on the edge of the map

        Args:
            material_index: Material designation in the map
        """

        voxel_map = self.voxel_map
        columns, rows = self.window

        step_pattern = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        boundaries = []

        for index in range(columns * rows):
            y, x = divmod(index, rows)

            if voxel_map[y][x] != material_index:
                continue

            is_boundary = False
            for dy, dx in step_pattern:
                ny, nx = y + dy, x + dx

                # Out-of-bounds check
                if not (0 <= ny < columns) or not (0 <= nx < rows):
                    is_boundary = True
                    break

                # Material Difference check
                if voxel_map[ny][nx] != material_index:
                    is_boundary = True
                    break

            if is_boundary:
                boundaries.append((y, x))

        return boundaries

    def _find_material(
        self,
        coords: Tuple[int, int],  # (y, x)
        target_material_index: int
    ) -> int:
        """
        Finds the closest different material to
        coords given

        Args:
            coords: (y, x) of the target material
            target_material_index: Material designation in the map
        """
        voxel_map = self.voxel_map
        columns, rows = self.window
        y, x = coords

        visited = set()
        queue = [(y, x)]
        step_pattern = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while queue:
            cy, cx = queue.pop(0)
            if (cy, cx) in visited:
                continue
            visited.add((cy, cx))

            material_index = voxel_map[cy][cx]
            if material_index != target_material_index:
                return material_index

            for dy, dx in step_pattern:
                ny, nx = cy + dy, cx + dx

                # Out-of-bounds check
                if not (0 <= ny < columns) or not (0 <= nx < rows):
                    queue.append((ny, nx))

                # Material Difference check
                if voxel_map[ny][nx] != material_index:
                    queue.append((ny, nx))

        # If material fails
        return target_material_index
