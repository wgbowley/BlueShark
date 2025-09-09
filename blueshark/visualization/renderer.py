"""
Filename: renderer.py
Author: William Bowley
Version: 0.1
Date: 2025-08-16

Description:
    visualize the simulation
    model and is used for setting
    boundaries and materials.
"""

from typing import Tuple, Dict, List

from blueshark.domain.constants import (
    Geometry,
    ShapeType,
    SimulationType,
    Connectors
)

from blueshark.domain.generation.geometric_centroid import (
    centroid_point
)

from blueshark.visualization.primitives import (
    draw_hybrid,
    draw_annulus_circle,
    draw_annulus_sector,
    draw_circle,
    draw_polygon
)


class Visualize:
    """
    visualization renderer for blueshark framework with scaling
    """
    def __init__(
        self,
        x_size: int,
        y_size: int,
        ambient_material: Dict[str, int],
        sim_type: SimulationType,
        scale: int = 10,  # scaling factor
    ) -> None:
        self.scale = scale
        self.window = (int(x_size * scale), int(y_size * scale))
        self.materials = {}
        self.type = sim_type
        self.voxel_map = []

        # Calculates shift value for simulation types
        x, y = 0, 0
        if sim_type == SimulationType.PLANAR:
            x = self.window[0] // 2
            y = self.window[1] // 2

        self.ambient_material = ambient_material
        self.materials[ambient_material] = 0
        self.shift = (x, y)

    def initalize_map(
        self,
    ) -> list[list[int]]:
        """
        Initalizes the voxel map
        """

        voxel_map = []
        for _ in range(0, self.window[1]):
            row = []
            for _ in range(0, self.window[0]):
                row.append(self.materials[self.ambient_material])
            voxel_map.append(row)

        self.voxel_map = voxel_map

    def draw(
        self,
        geometry: Geometry,
        material: str,
        tag_coords: None = None
    ) -> None:
        """
        Draws element to the voxel map, scaling coordinates
        """
        if material not in self.materials:
            self.materials[material] = len(self.materials)

        shape = geometry.get("shape")

        # Generate points using the scaled geometry
        match shape:
            case ShapeType.POLYGON | ShapeType.RECTANGLE:
                points = draw_polygon(
                    [
                        (x * self.scale, y * self.scale)
                        for x, y in geometry["points"]
                    ],
                    self.materials[material]
                )
            case ShapeType.CIRCLE:
                points = draw_circle(
                    geometry["radius"] * self.scale,
                    (
                        geometry["center"][0] * self.scale,
                        geometry["center"][1] * self.scale
                    ),
                    self.materials[material]
                )

            case ShapeType.ANNULUS_SECTOR:
                points = draw_annulus_sector(
                    (
                        geometry["center"][0] * self.scale,
                        geometry["center"][1] * self.scale
                    ),
                    geometry["radius_outer"] * self.scale,
                    geometry["radius_inner"] * self.scale,
                    geometry["start_angle"],
                    geometry["end_angle"],
                    self.materials[material]
                )
            case ShapeType.ANNULUS_CIRCLE:
                points = draw_annulus_circle(
                    (
                        geometry["center"][0] * self.scale,
                        geometry["center"][1] * self.scale
                    ),
                    geometry["radius_outer"] * self.scale,
                    geometry["radius_inner"] * self.scale,
                    self.materials[material]
                )
            case ShapeType.HYBRID:
                points = draw_hybrid(
                    self.materials[material],
                    self._scale_hybrid_edges(geometry["edges"])
                )
            case _:
                raise NotImplementedError(f"Shape '{shape}' not supported")

        # Draw points
        for point in points:
            self._set_points(point[0], point[1])

        # Scale centroid if not provided
        if tag_coords is None:
            tag_coords = centroid_point(geometry)
        tag_coords = (
            int(tag_coords[0] * self.scale),
            int(tag_coords[1] * self.scale)
        )

        self._fill__regions(tag_coords, self.materials[material])

    def find_boundary_segments(
        self,
        connectors: Dict[Connectors, List[tuple[float, float]]],
        ambient_material: str
    ) -> Dict[Connectors, List[tuple[float, float]]]:
        """
        Filters connectors to only keep points whose shifted coordinates
        are **adjacent** to the ambient material (top/left/bottom/right).
        """

        columns, rows = len(self.voxel_map), len(self.voxel_map[0])
        shift_x, shift_y = self.shift
        filtered = {}
        material = self.materials[ambient_material]

        # Offsets for 4-connected neighbors
        neighbor_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for connector_type, points in connectors.items():
            new_points = []
            for x, y in points:
                # Apply shift
                sx, sy = self.scale*x + shift_x, self.scale*y + shift_y

                # Convert to voxel indices
                vx, vy = int(round(sx)), int(round(sy))

                # Bounds check
                if 0 <= vx < rows and 0 <= vy < columns:
                    # Check all 4 neighbors
                    is_adjacent_to_ambient = False
                    for dx, dy in neighbor_offsets:
                        nx, ny = vx + dx, vy + dy
                        if 0 <= nx < rows and 0 <= ny < columns:
                            if self.voxel_map[ny][nx] == material:
                                is_adjacent_to_ambient = True
                                break

                    if is_adjacent_to_ambient:
                        new_points.append((x, y))  # keep original point

            filtered[connector_type] = new_points

        return filtered

    def _set_points(
        self,
        coord: Tuple[int, int],
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

    def _scale_hybrid_edges(self, edges: list[dict]) -> list[dict]:
        scale = self.scale
        scaled = []
        for edge in edges:
            new_edge = edge.copy()
            new_edge['start'] = (
                edge['start'][0] * scale, edge['start'][1] * scale
            )
            new_edge['end'] = (edge['end'][0] * scale, edge['end'][1] * scale)
            # angle stays the same, only coordinates matter for draw_arc
            scaled.append(new_edge)
        return scaled
