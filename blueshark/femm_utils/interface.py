"""
File: interface.py
Author: William Bowley
Version: 1.1
Date: 2025-08-09
Description:
    Setup FEMM simulation documents and generate motor geometry
    based on user-defined linear motor models.
"""

import logging
import pathlib
from typing import Optional

import femm
from blueshark.motor.interface import LinearBase


def _initialize_femm_model(motor: LinearBase) -> None:
    """
    Prepare the FEMM simulation space with the
    motor's circuits, materials, and geometry.
    """
    # Add phase circuits
    for phase in motor.phases:
        femm.mi_addcircprop(phase, 0, 1)

    # Add materials
    motor.add_materials()

    # Compute geometry and add components
    motor.compute_geometry()
    motor.add_armature()
    motor.add_stator()
    motor.add_boundary()


def femm_setup(
    motor: Optional[LinearBase],
    problem_type: str,
    path: pathlib.Path,
    axial_length: Optional[float] = None,
    units: str = "millimeters",
    depth: float = 1e-8,
) -> None:
    """
    Sets up a FEMM simulation document and draws the motor geometry.

    Args:
        motor: The motor model to draw
        problem_type: The type of simulation: 'axi' (axisymmetric) or 'planar'.
        path: The full path to save the FEMM file.
        axial_length: The axial length in the specified units.
                      This is a required parameter for planar problems.
        units: The length units for the problem. Defaults to "millimeters".
        depth: The depth for the problem. Defaults to 1e-8.
    """
    if problem_type not in {"axi", "planar"}:
        msg = (
            f"Invalid problem_type '{problem_type}'. "
            f"Must be 'axi' or 'planar'."
        )
        logging.error(msg)
        raise ValueError(msg)

    try:
        femm.openfemm(1)
        femm.newdocument(0)

        if problem_type == "planar":
            if axial_length is None:
                msg = "axial_length must be provided for planar problems."
                logging.error(msg)
                raise ValueError(msg)
            if not isinstance(axial_length, (int, float)) or axial_length <= 0:
                msg = (
                    f"Axial length must be a positive number, "
                    f"got {axial_length}"
                )
                logging.critical(msg)
                raise ValueError(msg)

            femm.mi_probdef(0, units, "planar", depth, axial_length)

        elif problem_type == "axi":
            femm.mi_probdef(0, units, "axi", depth)

        _initialize_femm_model(motor)

        femm.mi_saveas(str(path))
    except Exception as e:
        msg = f"FEMM setup failed ({problem_type}): {e}"
        logging.critical(msg)
        raise RuntimeError(msg) from e

    finally:
        femm.closefemm()
