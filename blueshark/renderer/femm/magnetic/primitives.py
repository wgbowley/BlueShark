"""
File: primitives.py
Author: William Bowley
Version: 1.2
Date: 2025-08-09
Description:
    Draws shapes to the magnetic simulation
    space for FEMM.

    Includes all shapes in ShapeType
"""

from math import cos, sin, radians

import femm
from blueshark.domain.geometry.validation import validate_shape
from blueshark.domain.definitions import (
    Connection, Connectors, Geometry, ShapeType
)
from blueshark.domain.geometry.utils import (
    mid_points_arc, mid_points_line, find_arc_center
)


def _draw_polygon(
    points: list[tuple[float, float]],
    enclosed: bool = True
) -> dict:
    """
    Draws a polygon to the simulation space.

    Args:
        points: lists of points to draw to simulation space
                Must be more than 2 points
    """
    contours = {
        Connectors.LINE: [],
        Connectors.ARC: []
    }

    pairs = len(points) - 1

    # Connects vertex pairs together
    for i in range(pairs):
        contours[Connectors.LINE].append(
            mid_points_line(points[i], points[i + 1])
        )
        femm.mi_drawline(
            points[i][0],
            points[i][1],
            points[i + 1][0],
            points[i + 1][1]
        )

    if enclosed:
        contours[Connectors.LINE].append(
            mid_points_line(points[-1], points[0])
        )
        # Connects first and last vertex
        femm.mi_drawline(
            points[-1][0],
            points[-1][1],
            points[0][0],
            points[0][1]
        )

    return contours


def _draw_circle(
    radius: float,
    center: tuple[float, float],
    maxseg: int = 1
) -> dict:
    """
    Draws a circle to the simulation space via
    drawarc command within FEMM.

    Circle makes up 4 x 90 degree arcs.

    Args:
        radius: Length from center to any point on circumference
        center: Center point of the circle
        maxseg: Resolution of the circle
    """
    contours = {
        Connectors.LINE: [],
        Connectors.ARC: []
    }

    cx, cy = center
    r = radius
    points = [
        (cx - r, cy),  # Left
        (cx, cy + r),  # Top
        (cx + r, cy),  # Right
        (cx, cy - r)   # Bottom
    ]

    # Left to top arc
    contours[Connectors.ARC].append(
        mid_points_arc(
            points[1],
            points[0],
            center
        )
    )
    femm.mi_drawarc(
        points[1][0], points[1][1],
        points[0][0], points[0][1],
        90,
        maxseg
    )

    # Right to top arc
    contours[Connectors.ARC].append(
        mid_points_arc(
            points[2],
            points[1],
            center
        )
    )
    femm.mi_drawarc(
        points[2][0], points[2][1],
        points[1][0], points[1][1],
        90,
        maxseg
    )

    # Bottom to right arc
    contours[Connectors.ARC].append(
        mid_points_arc(
            points[3],
            points[2],
            center
        )
    )
    femm.mi_drawarc(
        points[3][0], points[3][1],
        points[2][0], points[2][1],
        90,
        maxseg
    )

    # Left to bottom arc
    contours[Connectors.ARC].append(
        mid_points_arc(
            points[0],
            points[3],
            center
        )
    )
    femm.mi_drawarc(
        points[0][0], points[0][1],
        points[3][0], points[3][1],
        90,
        maxseg
    )

    return contours


def _draw_annulus_circle(
    center: tuple[float, float],
    r_outer: float,
    r_inner: float,
    maxseg: int = 1
) -> dict:
    """
    Draws an annulus (ring) by drawing two concentric circles:
    outer circle and inner circle (hole).
    """
    contours = {
        Connectors.LINE: [],
        Connectors.ARC: []
    }

    # Outer circle
    outer_contours = _draw_circle(r_outer, center, maxseg)
    # Inner circle
    inner_contours = _draw_circle(r_inner, center, maxseg)

    contours[Connectors.LINE].extend(outer_contours[Connectors.LINE])
    contours[Connectors.LINE].extend(inner_contours[Connectors.LINE])
    contours[Connectors.ARC].extend(outer_contours[Connectors.ARC])
    contours[Connectors.ARC].extend(inner_contours[Connectors.ARC])

    return contours


def _draw_annulus_sector(
    center: tuple[float, float],
    r_outer: float,
    r_inner: float,
    start_angle: float,
    end_angle: float,
    maxseg: int = 1
) -> dict:
    """
    Draw an annulus sector in magnetic FEMM.
    """
    contours = {
        Connectors.LINE: [],
        Connectors.ARC: []
    }
    cx, cy = center

    # Convert angles to radians & calculate angle
    start_rad = radians(start_angle)
    end_rad = radians(end_angle)
    arc_angle = end_angle - start_angle

    # Calculate vertex points on outer & inner arcs
    outer_points = [
        (cx + r_outer * cos(start_rad), cy + r_outer * sin(start_rad)),
        (cx + r_outer * cos(end_rad), cy + r_outer * sin(end_rad))
    ]

    inner_points = [
        (cx + r_inner * cos(start_rad), cy + r_inner * sin(start_rad)),
        (cx + r_inner * cos(end_rad), cy + r_inner * sin(end_rad))
    ]

    # Outer arc
    contours[Connectors.ARC].append(
        mid_points_arc(
            outer_points[0],
            outer_points[1],
            center
        )
    )
    femm.mi_drawarc(
        outer_points[0][0], outer_points[0][1],
        outer_points[1][0], outer_points[1][1],
        arc_angle, maxseg
    )

    # Inner arc
    contours[Connectors.ARC].append(
        mid_points_arc(
            inner_points[0],
            inner_points[1],
            center
        )
    )
    femm.mi_drawarc(
        inner_points[0][0], inner_points[0][1],
        inner_points[1][0], inner_points[1][1],
        arc_angle, maxseg
    )

    # Connect outer end to inner end
    contours[Connectors.LINE].append(
        mid_points_line(
            outer_points[1],
            inner_points[1]
        )
    )
    femm.mi_drawline(
        outer_points[1][0], outer_points[1][1],
        inner_points[1][0], inner_points[1][1]
    )

    # Connect inner start back to outer start
    contours[Connectors.LINE].append(
        mid_points_line(
            inner_points[0],
            outer_points[0]
        )
    )
    femm.mi_drawline(
        inner_points[0][0], inner_points[0][1],
        outer_points[0][0], outer_points[0][1]
    )

    return contours


def _draw_hybrid(edges: list[Connection]) -> dict:
    """
    Draws a hybrid geometry to FEMM, using only lines and arcs.

    Args:
        edges: list of connections describing the shape in order
    """
    if not edges:
        raise ValueError("No edges provided for hybrid geometry")

    contours = {
        Connectors.LINE: [],
        Connectors.ARC: []
    }

    for edge in edges:
        edge_type = edge["type"]

        if edge_type == Connectors.LINE:
            contours[Connectors.LINE].append(
                mid_points_line(
                    edge["start"],
                    edge["end"]
                )
            )
            femm.mi_drawline(
                edge["start"][0], edge["start"][1],
                edge["end"][0], edge["end"][1]
            )

        elif edge_type == Connectors.ARC:
            contours[Connectors.ARC].append(
                mid_points_arc(
                    edge["start"],
                    edge["end"],
                    find_arc_center(
                        edge["start"],
                        edge["end"],
                        edge["start_angle"],
                        edge["end_angle"]
                    )
                )
            )

            femm.mi_drawarc(
                edge["start"][0], edge["start"][1],
                edge["end"][0], edge["end"][1],
                edge["angle"],
                1
            )

        else:
            raise ValueError(f"Unknown edge type: {edge_type}")

    return contours


def draw_primitive(
    shape: Geometry
) -> dict:
    """
    Draws the shape to the FEMMagneticRenderer and returns
    the shapes contours

    Args:
        shape: Geometry dictionary (Enum)
    """
    validate_shape(shape)

    contours = None
    shape_type = shape.get("shape")
    match shape_type:
        case ShapeType.POLYGON | ShapeType.RECTANGLE:
            contours = _draw_polygon(
                shape["points"],
                shape["enclosed"]
            )

        case ShapeType.CIRCLE:
            contours = _draw_circle(
                shape["radius"],
                shape["center"]
            )

        case ShapeType.ANNULUS_CIRCLE:
            contours = _draw_annulus_circle(
                shape["center"],
                shape["radius_outer"],
                shape["radius_inner"]
            )

        case ShapeType.ANNULUS_SECTOR:
            contours = _draw_annulus_sector(
                shape["center"],
                shape["radius_outer"],
                shape["radius_inner"],
                shape["start_angle"],
                shape["end_angle"]
            )

        case ShapeType.HYBRID:
            if "edges" not in shape:
                raise ValueError("Hybrid shape requires 'edges' field")
            contours = _draw_hybrid(shape["edges"])

        case _:
            raise NotImplementedError(f"Shape '{shape_type}' not supported")

    return contours
