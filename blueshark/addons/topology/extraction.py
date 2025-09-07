import math
from blueshark.addons.topology.renderer import TopologyRenderer


def _distance(
    point_1: tuple[int, int],
    point_2: tuple[int, int]
) -> float:
    """
    Calculates the distance between two points
    """
    x0, y0 = point_1
    x1, y1 = point_2
    return math.hypot(x0-x1, y0-y1)


def _influence_points(
    points: list[tuple[int, int]],
    current_point: tuple[int, int],
    radius: int,
) -> list[tuple[int, int]]:
    """
    Finds local points to a point within a square area
    """
    influence_points = []
    x0, y0 = current_point

    for x, y in points:
        if abs(x - x0) < radius and abs(y - y0) < radius:
            influence_points.append((x, y))

    return influence_points


def _order_points(
    points: list[tuple[int, int]],
    radius: int = 20
) -> list[tuple[float, float]]:
    """
    Orders the points into a series of connected
    points perimeter
    """
    if not points:
        return []

    temp_points = points.copy()
    ordered = [temp_points.pop(0)]

    for _ in range(len(points) - 1):
        current_point = ordered[-1]
        local_points = _influence_points(temp_points, current_point, radius)

        if local_points:
            nearest_point = min(
                local_points,
                key=lambda p: _distance(p, current_point)
            )

            temp_points.remove(nearest_point)
            ordered.append(nearest_point)

    return ordered


def _materials_boundaries(
    topology: TopologyRenderer
) -> dict[int, list[tuple[int, int]]]:
    """
    Finds all points along the boundaries of materials
    expect for zero. Which is considered empty space
    """
    materials = topology.materials

    boundaries = {}
    for i in materials:
        if i != 0:
            material_index = materials[i]
            points = topology._find_boundaries(material_index)
            boundaries[i] = points

    return boundaries


def _material_perimeters(
    points: list[tuple[int, int]],
    radius: int = 10
) -> list[list[tuple[int, int]]]:
    """
    Finds material perimeters from a set of
    randomly ordered boundary points.

    Each returned list is one connected island.

    Note:
        This is my first "novel" alogithrm,
        hence frontward its called "bowely's islands" lol.
    """
    perimeters = []
    remaining_points = set(points)  # use set for O(1) removals

    while remaining_points:
        # Pick the point with the most neighbors as starting point
        start_point = max(
            remaining_points,
            key=lambda p: len(
                _influence_points(list(remaining_points), p, radius)
            )
        )

        ordered = [start_point]
        remaining_points.remove(start_point)

        frontier = [start_point]
        while frontier:
            current_point = frontier.pop()
            local_points = _influence_points(
                list(remaining_points),
                current_point,
                radius
            )

            for neighbor in local_points:
                if neighbor in remaining_points:
                    remaining_points.remove(neighbor)
                    frontier.append(neighbor)
                    ordered.append(neighbor)

        # Optionally close the loop
        if ordered[0] != ordered[-1]:
            ordered.append(ordered[0])

        perimeters.append(ordered)

    order_perimeters = []
    for index in perimeters:
        points = _order_points(index, radius)
        order_perimeters.append(points)

    return order_perimeters
