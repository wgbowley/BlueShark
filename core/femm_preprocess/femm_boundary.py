"""
Filename: femm_boundary.py
Author: William Bowley
Version: 1.0
Date: 2025-07-01
Description:
    Boundary condition and domain setup functions for FEMM pre-processor.
"""

import femm


def add_bounds(
        origin: tuple[float, float],
        radius: float,
        numShells: int = 7,
        boundType: int = 1,
        material: str = "Air"
    ) -> None:
    """
    Adds a series of circular shells that emulate an unbounded domain 
    (Assumes Neumann outer edges by default).

    Parameters:
        origin (tuple): Center of the shells (x, y).
        radius (float): Radius of the outer shell.
        numShells (int): Number of shells to create.
        boundType (int): Boundary condition type (0=Dirichlet, 1=Neumann).
        material (str): Material for the shells.
    """
    
    femm.mi_makeABC(numShells, radius, origin[0], origin[1], boundType)
    
    # Shift block label up.
    objectLabel = (origin[0] + 0.5 * radius, origin[1] + 0.5 * radius)
    
    femm.mi_addblocklabel(objectLabel[0], objectLabel[1])
    femm.mi_selectlabel(objectLabel[0], objectLabel[1])
    femm.mi_setblockprop(material, 0, 0, "<None>", 0, 0, 0)
    femm.mi_clearselected()
