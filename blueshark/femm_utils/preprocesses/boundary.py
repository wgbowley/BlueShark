"""
Filename: boundary.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28

Description:
    Boundary condition and domain setup functions for FEMM pre-processing.

    Provides utility to add concentric boundary shells emulating
    an unbounded domain for FEMM magnetic simulations.

Functions:
- add_bounds(origin, radius, num_shells=7, bound_type=1, material="Air"):
    Adds concentric boundary shells with specified conditions; returns None.

"""

import logging
import femm


def add_bounds(
    origin: tuple[float, float],
    radius: float,
    num_shells: int = 7,
    bound_type: int = 1,
    material: str = "Air"
) -> None:
    """
    Adds a series of concentric circular shells that emulate
    an unbounded domain in FEMM.

    By default, applies Neumann boundary conditions (zero normal derivative).
    Can be set to Dirichlet (fixed potential) by setting `bound_type`.

    Args:
        origin (tuple[float, float]): Center coordinates (x, y) for the shells.
        radius (float): Radius of the inter most shell (solution domain)
        num_shells (int): Number of concentric shells to create.
        bound_type (int): Boundary condition type.
                          0 = Dirichlet (fixed potential),
                          1 = Neumann (zero normal derivative).
        material (str): Name of the material assigned to the shells.
    """

    if radius <= 0:
        msg = f"Radius must be > 0, got {radius}"
        logging.error(msg)
        raise ValueError(msg)

    if not isinstance(num_shells, int) or num_shells <= 0:
        msg = f"Number of shells must be a positive integer, got {num_shells}"
        logging.error(msg)
        raise ValueError(msg)

    if bound_type not in (0, 1):
        msg = f"Bound must be 0/1 (Dirichlet/Neumann), got {bound_type}"
        logging.error(msg)
        raise ValueError(msg)

    if not isinstance(material, str) or not material.strip():
        msg = "Material name must be a non-empty string."
        logging.error(msg)
        raise ValueError(msg)

    try:
        femm.mi_makeABC(num_shells, radius, origin[0], origin[1], bound_type)

        # Label placement offset by 60% radius along x and y
        label_x = origin[0] + 0.6 * radius
        label_y = origin[1] + 0.6 * radius

        femm.mi_addblocklabel(label_x, label_y)
        femm.mi_selectlabel(label_x, label_y)
        femm.mi_setblockprop(material, 0, 0, "<None>", 0, 0, 0)
        femm.mi_clearselected()

    except Exception as e:
        msg = f"Failed to add FEMM boundary shells: {e}"
        logging.critical(msg)
        raise RuntimeError(msg) from e
