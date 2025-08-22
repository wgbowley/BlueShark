"""
Filename: filling.py
Author: William Bowley
Version: 0.1
Date: 2025-08-16

Description:
    This addon aims to add topology optimization
    to the framework for all solvers

    This module fills geometry using scanline fill
"""


def fill_polygon(
    points: list[tuple[int, int]],
    material: int,
    gap_tolerance: int = 0
) -> list[tuple[tuple[int, int], int]]:

    """
    Fills the interior of a polygon defined by `points`.
    Returns a list of points [(x, y), material].
    Uses scanline fill.
    """
    if not points:
        return []

    filled_points = []

    # Extract coordinates (points might be [(x,y), mat])
    coords = [p[0] if isinstance(p[0], tuple) else p for p in points]

    # Bounding box
    min_y = min(p[1] for p in coords)
    max_y = max(p[1] for p in coords)

    for y in range(min_y, max_y + 1):
        intersections = []
        for i in range(len(coords)):
            p1 = coords[i]
            p2 = coords[(i + 1) % len(coords)]

            # Allow small gaps
            if abs(p1[1] - p2[1]) <= gap_tolerance:
                continue

            if (p1[1] <= y < p2[1]) or (p2[1] <= y < p1[1]):
                x = int(
                    round(
                        p1[0] + (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1])
                        )
                    )
                intersections.append(x)

        intersections.sort()

        for i in range(0, len(intersections), 2):
            if i + 1 < len(intersections):
                x_start = intersections[i]
                x_end = intersections[i + 1]
                for x in range(x_start, x_end + 1):
                    filled_points.append(((x, y), material))

    return filled_points
