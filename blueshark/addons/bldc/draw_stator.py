"""
File: draw_bldc.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28
Description:
    This is an addon for drawing bldc
    motors stators through the renderer interface.

    (Tests)
"""

from math import pi

from blueshark.domain.constants import (
    Geometry,
    ShapeType
)


def _back_iron_geometry(
    radius_inner: float,
    radius_outer: float
) -> Geometry:

    black_iron: Geometry = {
        'shape': ShapeType.ANNULUS_CIRCLE,
        "center": (0, 0),
        "radius_inner": radius_inner,
        "radius_outer": radius_outer
    }

    return black_iron


def _poles_geometries(
    number_poles: int,
    pole_radial_length: float,
    pole_radial_thickness: float,
    radius_inner: float
) -> list[Geometry]:
    pole_angle = 360/number_poles
    arc_anlge = pole_radial_length/(radius_inner-pole_radial_thickness)

    geometries = []
    for pole in range(0, number_poles):
        geometry: Geometry = {
            'shape': ShapeType.ANNULUS_SECTOR,
            'center': (0, 0),
            'radius_outer': radius_inner,
            'radius_inner': radius_inner - pole_radial_thickness,
            'start_angle': pole_angle * pole,
            'end_angle': pole_angle * pole + arc_anlge * 180 / pi
        }
        geometries.append(geometry)
    return geometries


def stator_geometries(
    number_poles: int,
    pole_radial_length: float,
    pole_radial_thickness: float,
    radius_inner: float,
    radius_outer: float,
) -> None:

    """
    Generates the geometries for the stator of a bldc motor
    """

    back_iron = _back_iron_geometry(
        radius_inner,
        radius_outer
    )

    poles = _poles_geometries(
        number_poles,
        pole_radial_length,
        pole_radial_thickness,
        radius_inner
    )

    return {"back_iron": back_iron, "poles": poles}
