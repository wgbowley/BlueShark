"""
Filename: boundary.py
Author: William Bowley
Version: 1.4
Date: 2025-07-28

Description:
    Sets concentric boundary shells emulating an unbounded domain
    for the FEMMagneticRenderer
"""

import logging
import femm

from typing import Optional
from blueshark.domain.definitions import BoundaryType


def concentric_boundary(
    origin: tuple[float, float],
    radius: float,
    material_name: str,
    num_shells: Optional[int] = 7,
    boundary_type: Optional[BoundaryType] = BoundaryType.NEUMANN
) -> None:
    """
    Adds a series of concentric circular shells that emulate
    an unbounded domain.

    By default, applies Neumann boundary conditions.

    Args:
        origin: Center coordinates (x, y) for the shells
        radius: Radius of the innermost shell (solution domain)
        material_name: Name of the material assigned to outer domain
        num_shells: Number of concentric shells to create
        boundary_type: Type of boundary (Ref. domain/definitions.py)
    """

    if radius <= 0 or not isinstance(radius, (float, int)):
        raise ValueError(f"Radius must be a positive float, got {radius}")

    if not isinstance(material_name, str) or not material_name.strip():
        raise ValueError("Material name must be a non-empty string")

    if boundary_type not in (BoundaryType.NEUMANN, BoundaryType.DIRICHLET):
        logging.warning(
            f"Boundary type '{boundary_type}' not supported; "
            "defaulting to Neumann"
        )
    femm_boundary = 0 if boundary_type == BoundaryType.DIRICHLET else 1

    try:
        femm.mi_makeABC(
            num_shells,
            radius,
            origin[0],
            origin[1],
            femm_boundary
        )

        # Label placement offset by 60& radius along x and y
        label_x = origin[0] + 0.6 * radius
        label_y = origin[1] + 0.6 * radius

        femm.mi_addblocklabel(label_x, label_y)
        femm.mi_selectlabel(label_x, label_y)
        femm.mi_setblockprop(material_name, 0, 0, "<None>", 0, 0, 0)
        femm.mi_clearselected()

    except Exception as e:
        msg = f"Failed to add concentric boundary to FEMMagneticRenderer: {e}"
        raise RuntimeError(msg) from e
