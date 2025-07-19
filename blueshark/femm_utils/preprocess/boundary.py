"""
Filename: femm_boundary.py
Author: William Bowley
Version: 1.1
Date: 2025-07-19

Description:
    Boundary condition and domain setup functions for FEMM pre-processor.
"""

import femm


def add_bounds(
    origin: tuple[float, float],
    radius: float,
    num_shells: int = 7,
    bound_type: int = 1,
    material: str = "Air"
) -> None:
    """
    Adds a series of circular shells that emulate an unbounded domain.

    Assumes Neumann outer edges by default.

    Args:
        origin (tuple[float, float]): Center of the shells (x, y).
        radius (float): Radius of the outer shell.
        num_shells (int): Number of shells to create.
        bound_type (int): Boundary condition type (0 = Dirichlet, 1 = Neumann).
        material (str): Material name used for the shells.
    """
    femm.mi_makeABC(num_shells, radius, origin[0], origin[1], bound_type)

    # Shift block label up
    label_x = origin[0] + 0.5 * radius
    label_y = origin[1] + 0.5 * radius

    femm.mi_addblocklabel(label_x, label_y)
    femm.mi_selectlabel(label_x, label_y)
    femm.mi_setblockprop(material, 0, 0, "<None>", 0, 0, 0)
    femm.mi_clearselected()
