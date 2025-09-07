import math

from blueshark.addons.topology.extraction import _order_points


def _min_point_to_geometry(
    point_1: tuple[int, int],
    geometry_2: list[tuple[int, int]]
) -> tuple[int, int]:
    """
    Finds the point on geometry_2 that is closest to point_1.
    """
    min_distance = float('inf')
    closest_point = None
    x, y = point_1

    for x1, y1 in geometry_2:
        distance = math.hypot(x - x1, y - y1)
        if distance < min_distance:
            min_distance = distance  
            closest_point = (x1, y1)

    return closest_point


def _shared_points(
    geometry_1: list[tuple[int, int]],
    geometry_2: list[tuple[int, int]],
    threshold: int = 4
) -> list[tuple[int, int]]:
    """
    Removes points in geometry_1 that are
    within 'threshold' distance of any
    point in reference_points.
    """
    list = []
    filtered_points = []
    for tx, ty in geometry_1:
        too_close = False
        for rx, ry in geometry_2:
            dist = math.hypot(rx - tx, ry - ty)
            if dist <= threshold:
                list.append((rx, ry))
                too_close = True
                break
        if not too_close:
            filtered_points.append((tx, ty))
    return filtered_points


def interfaced_geometry(
    geometry_1: list[tuple[int, int]],
    geometry_2: list[tuple[int, int]],
    threshold: int = 5
) -> list[tuple[int, int]]:
    """"
    Removes shared points and than finds points on
    geometry 2 to connect to.
    """
    geometry_1 = _shared_points(
        geometry_1,
        geometry_2,
        threshold
    )
    points = _order_points(geometry_1)

    start = _min_point_to_geometry(
        points[0],
        geometry_2
    )
    end = _min_point_to_geometry(
        points[-1],
        geometry_2
    )
    points = _order_points([start] + geometry_1 + [end])

    return points
