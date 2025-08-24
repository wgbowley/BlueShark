
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

        if tag_coords is None:
            tag_coords = centroid_point(geometry)

        tag_coords = (int(tag_coords[0]), int(tag_coords[1]))
        self._fill_region(tag_coords, self.materials[material])

    def boundary_mutation(
        self,
        material: int,
        p_remove: float = 0.1,
        p_add: float = 0.05,
        block_size: int = 3
    ) -> None:
        """
        Mutates only the boundary voxels of the selected material with
        block-based growth/removal.

        Args:
            Material: Material region to mutate shape
            p_remove: Probability that a boundary voxel filps material type
            p_add: Probability that a boundary voxel filps to material type
            block_size: How much material is growth/removed each time
        """

        voxel_map = self.topology_map
        mat = self.materials[material]
        rows, cols = len(voxel_map), len(voxel_map[0])
        boundaries = self._find_boundaries(mat)
        half = block_size // 2

        for y, x in boundaries:
            # Remove block
            if random() < p_remove:
                for dy in range(-half, half+1):
                    for dx in range(-half, half+1):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < rows and 0 <= nx < cols:
                            if voxel_map[ny][nx] == mat:
                                    voxel_map[ny][nx] = self._find_mat(
                                        voxel_map,
                                        ny,
                                        nx,
                                        mat
                                    )
                                    
            # Grow block into neighboring voids
            if random() < p_add:
                for dy in range(-half, half+1):
                    for dx in range(-half, half+1):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < rows and 0 <= nx < cols:
                            if voxel_map[ny][nx] == 0:
                                voxel_map[ny][nx] = mat

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
        self.topology_map[shifted[1]][shifted[0]] = material

    def _fill_region(
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
        voxel_map = self.topology_map

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
        material: int
    ) -> List[Tuple[int, int]]:
        """
        Finds all boundary voxels of the given material region

        A boundary bvoxel has at least one neighbor with a different material

        Args:
            Material: Material type of the enclosed region
        """
        voxel_map = self.topology_map
        boundaries = []
        m = self.window[1]
        n = self.window[0]
        for y in range(m):
            for x in range(n):
                if voxel_map[y][x] != material:
                    continue
                # Check neighbors
                neighbors = [
                    (y + 1, x), (y - 1, x),
                    (y, x + 1), (y, x - 1)
                ]
                for ny, nx in neighbors:
                    if 0 <= ny < m and 0 <= nx < n:
                        if voxel_map[ny][nx] != material:
                            boundaries.append((y, x))
                            break  # no need to check other neighbors

        return boundaries
    
    def _find_mat(self, voxel_map, y, x, target_material):
        rows, cols = self.window[0], self.window[1]
        visited = set()
        queue = [(y, x)]

        while queue:
            cy, cx = queue.pop(0)  # pop from front to mimic BFS
            if (cy, cx) in visited:
                continue
            visited.add((cy, cx))

            # If this voxel is a different material, return it
            mat = voxel_map[cy][cx]
            if mat != target_material:
                return mat

            # enqueue neighbors
            for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < rows and 0 <= nx < cols and (ny, nx) not in visited:
                    queue.append((ny, nx))

        return target_material  # fallback if nothing found