"""
File: properties.py
Author: William Bowley
Version: 1.3
Date: 2025-08-13
Description:
    Sets the properties of shapes within
    magnetic simulation space for femm.
"""

from typing import Tuple
import femm

from blueshark.domain.constants import Connectors

def set_properties(
    tag_coords: Tuple[float, float],
    group_id: int,
    material: str,
    phase: str = None,
    turns: int = 0,
    magnetization: float = 0.0
) -> None:
    """
    Add block label to simulation space and sets
    properties of the label.

    Args:
        tag_coords (tuple): x and y coordinates of the blocklabel
        material (str): Material of the element.
        group_id (int): Group identifier.
        phase (str, optional): The phase the element belongs to.
        turns (int, optional): Number of turns of material
                                within the shape.
        magnetization (float, optional): Direction of the magnetic field.

    """
    femm.mi_addblocklabel(tag_coords[0], tag_coords[1])
    femm.mi_selectlabel(tag_coords[0], tag_coords[1])
    femm.mi_setblockprop(
        material,       # 'blockname' material
        1,              # Mesher automatically chooses the mesh density
        0,              # Size constraint on the mesh in the block
        phase,          # 'Incirucit' Member of the circuit
        magnetization,  # Magnetization directed along an angle in degrees
        group_id,       # Member of group 'number group'
        turns           # Number of turns associated with this label
    )

    femm.mi_clearselected()


def add_phase(
    phase: str,
    inital_current: float = 0.0
) -> None:
    """
    Adds a phase to the simulation space with
    inital current of 0 Amps
    """
    femm.mi_addcircprop(phase, inital_current, 1)


def assign_group(
    element: dict[Connectors, tuple[float, float]],
    group: int
) -> None:
    """
    Assigns a group number to the perimeter of a shape.

    Args:
        element: ShapeType object containing line and arc segments
        group: Group number to assign
    """

    # Assign group to line segments
    for point in element[Connectors.LINE]:
        femm.mi_selectsegment(point[0], point[1])   # select line
        femm.mi_setgroup(group)                     # assign group
        femm.mi_clearselected()                     # clear selection

    # Assign group to arc segments
    for point in element[Connectors.ARC]:
        femm.mi_selectarcsegment(point[0], point[1])  # select arc
        femm.mi_setgroup(group)                        # assign group
        femm.mi_clearselected()                        # clear selection
