"""
Filename: boundary.py
Author: William Bowley
Version: 1.3
Date: 2025-07-28

Description:
    Boundary condition and domain setup functions for FEMM pre-processing.

    Provides utility to add concentric boundary shells emulating
    an unbounded domain for FEMM heat simulations.
"""

import logging
import femm

from blueshark.renderer.femm.heat.primitives import _mid_points_arc


def add_bounds(
    origin: tuple[float, float],
    radius: float,
    temperature: float = 300,
    num_shells: int = 7,
    bound_type: int = 1,
    material: str = "Air"
) -> None:

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
        femm.hi_makeABC(num_shells, radius, origin[0], origin[1], bound_type)

        femm.hi_addboundprop("boundary", 0, temperature, 0, 0, 0, 0)

        # Label placement offset by 60% radius along x and y
        label_x = origin[0] + 0.6 * radius
        label_y = origin[1] + 0.6 * radius

        femm.hi_addblocklabel(label_x, label_y)
        femm.hi_selectlabel(label_x, label_y)
        femm.hi_setblockprop(material, 1, 0, 0)
        femm.hi_clearselected()

        point = _mid_points_arc((0, radius), (-radius, 0), origin)
        femm.hi_selectarcsegment(point[0], point[1])
        femm.hi_setarcsegmentprop(0, "boundary", 0, 0, "")
        femm.hi_clearselected()

        point = _mid_points_arc((radius, 0), (0, radius), origin)
        femm.hi_selectarcsegment(point[0], point[1])
        femm.hi_setarcsegmentprop(0, "boundary", 0, 0, "")
        femm.hi_clearselected()
    except Exception as e:
        msg = f"Failed to add FEMM boundary shells: {e}"
        logging.critical(msg)
        raise RuntimeError(msg) from e
