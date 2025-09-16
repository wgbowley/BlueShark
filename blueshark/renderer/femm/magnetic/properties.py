"""
File: properties.py
Author: William Bowley
Version: 1.3
Date: 2025-09-14
Description:
    Sets the properties of elements and circuits
    within the FEMMagneticRenderer.
"""

import femm

from typing import Optional
from blueshark.domain.definitions import Connectors, CircuitType


def set_element_properties(
    element_tag: tuple[float, float],
    element_id: int,
    material_name: str,
    circuit: Optional[str] = None,
    turns: Optional[int] = 1,
    magnetization: Optional[float] = 0.0
) -> None:
    """
    Set element properties via adding a blocklabel
    and setting its properties

    Args:
        element_tag: (x, y) coordinates of blocklabel
        element_id: element identifier for blocklabel
        material_name: name of the material to assign to blocklabel
        circuit: The circuit the element belongs to.
        turns: The number of turns of the material
        magnetization: Direction of the magnetic field.
    """
    try:
        femm.mi_addblocklabel(element_tag[0], element_tag[1])
        femm.mi_selectlabel(element_tag[0], element_tag[1])

        femm.mi_setblockprop(
            material_name,
            1,  # Mesher automatically chooses the mesh density
            0,  # Size constraint of mesh in the block
            circuit,
            magnetization,
            element_id,
            turns
        )

        femm.mi_clearselected()
    except Exception as e:
        msg = f"Failed to set properties in FEMMagneticRenderer: {e}"
        raise RuntimeError(msg) from e


def add_circuit(
    circuit: str,
    circuit_type: CircuitType,
    initial_current: float
) -> None:
    """
    Adds a circuit in either series or parallel with
    an initial current

    Args:
        circuit: name of the circuit
        circuit_type: Type of circuit (series or parallel)
        initial_current: Current in amps
    """
    femm_circuit = None
    match circuit_type:
        case CircuitType.PARALLEL:
            femm_circuit = 0
        case CircuitType.SERIES:
            femm_circuit = 1

        case _:
            msg = (
                f"CircuitType '{circuit_type}' not supported by FEMM"
            )
            raise NotImplementedError(msg)

    try:
        femm.mi_addcircprop(circuit, initial_current, femm_circuit)
    except Exception as e:
        msg = f"Failed to add circuit to FEMMagneticRenderer {e}"
        raise RuntimeError(msg) from e


def assign_element_id(
    contours: dict[Connectors, tuple[float, float]],
    element_id: int
) -> None:
    """
    Assigns a element id to the contours of a shape

    Args:
        contours: ShapeType object containing line and arc segments
        element_id: element id to assign to individual contours
    """

    # Assign element id to line segments
    try:
        for segment in contours[Connectors.LINE]:
            femm.mi_selectsegment(segment[0], segment[1])
            femm.mi_setgroup(element_id)
            femm.mi_clearselected()
    except Exception as e:
        msg = (
            "Failed to add assign elements to line segments "
            f"in FEMMagneticRenderer {e}"
        )
        raise RuntimeError(msg) from e

    # Assign element id to arc segment:
    try:
        for segment in contours[Connectors.ARC]:
            femm.mi_selectarcsegment(segment[0], segment[1])
            femm.mi_setgroup(element_id)
            femm.mi_clearselected()
    except Exception as e:
        msg = (
            "Failed to add assign elements to arc segments "
            f"in FEMMagneticRenderer {e}"
        )
        raise RuntimeError(msg) from e


def assign_boundary(
    contours: dict[Connectors, tuple[float, float]],
    boundary: str
) -> None:
    """
    Assigns a boundary to the contours of a shape

    Args:
        contours: ShapeType object containing line and arc segments
        boundary: boundary name to assign to individual contours
    """

    # Assign boundary to line segments
    try:
        for segment in contours[Connectors.LINE]:
            femm.mi_selectsegment(segment[0], segment[1])
            femm.mi_setsegmentprop(boundary, 0, 0, 0, 0)
            femm.mi_clearselected()
    except Exception as e:
        msg = (
            "Failed to add assign boundary to line segments "
            f"in FEMMagneticRenderer {e}"
        )
        raise RuntimeError(msg) from e

    # Assign boundary to arc segment:
    try:
        for segment in contours[Connectors.ARC]:
            femm.mi_selectarcsegment(segment[0], segment[1])
            femm.mi_setarcsegmentprop(0, boundary, 0, 0)
            femm.mi_clearselected()
    except Exception as e:
        msg = (
            "Failed to add assign elements to arc segments "
            f"in FEMMagneticRenderer {e}"
        )
        raise RuntimeError(msg) from e
