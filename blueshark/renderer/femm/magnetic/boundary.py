"""
Filename: boundary.py
Author: William Bowley
Version: 1.4
Date: 2025-07-28

Description:
    Adds custom shape and boundary type to the FEMMagneticRenderer
"""

import femm

from blueshark.domain.definitions import Geometry, ShapeType, BoundaryType
from blueshark.renderer.femm.magnetic.primitives import draw_primitive
from blueshark.renderer.femm.magnetic.properties import assign_boundary
from blueshark.domain.geometry.validation import validate_shape


def _neumann(shape: Geometry, shells: int = 7) -> None:
    """
    Creates a Neumann ABC boundary domain using FEMM's built-in method.

    Args:
        shape: Shape definition (dict-like with 'type' and size info)
        shells: Number of concentric shells to create
    """
    name = shape.get("shape")
    match name:
        case ShapeType.CIRCLE:
            origin = shape["center"]
            radius = shape["radius"]
            femm.mi_makeABC(shells, radius, origin[0], origin[1], 1)

        case ShapeType.ANNULUS_SECTOR:
            origin = shape["center"]
            radius = shape["radius_outer"]
            femm.mi_makeABC(shells, radius, origin[0], origin[1], 1)

        case _:
            msg = (
                f"Shape '{name}' not supported for Neumann boundary in FEMM"
            )
            raise NotImplementedError(msg)


def _dirichlet(shape: Geometry) -> None:
    """
    Creates the Dirichlet boundary domain by setting vector
    potential at boundary to 0 (A=0).

    Args:
        shape: Shape definition (Enum)
    """
    femm.mi_addboundprop("A=0", 0, 0, 0, 0)
    contours = draw_primitive(shape)
    assign_boundary(contours, "A=0")


def draw_domain(
    shape: Geometry,
    boundary_type: BoundaryType,
    shells: int = 7
) -> None:
    """
    Draws the boundary domain in FEMMagneticRenderer.

    Args:
        shape: Shape definition (dict-like)
        boundary_type: Type of boundary (NEUMANN or DIRICHLET)
        shells: Number of concentric shells for Neumann boundary
    """
    validate_shape(shape)

    match boundary_type:
        case BoundaryType.NEUMANN:
            _neumann(shape, shells)
        case BoundaryType.DIRICHLET:
            _dirichlet(shape)
        case _:
            msg = f"BoundaryType '{boundary_type}' not supported"
            raise NotImplementedError(msg)
