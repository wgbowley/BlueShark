"""
Filename: frame.py
Author: William Bowley
Version: 1.2
Date: 2025-07-29

Description:
    Function to run a single FEMM simulation frame for a given motor setup.

    Responsibilities include:
    - Opening FEMM and loading the motor's FEMM file.
    - Applying position steps and phase currents.
    - Running FEMM analysis with retry on failure.
    - Computing requested post-processing outputs.
    - Cleaning up FEMM session and temporary files.
"""

import femm
import os

from typing import Any
from blueshark.configs import MAXIMUM_FAILS
from blueshark.output.selector import OutputSelector 
from blueshark.motor.linear_interface import LinearBase


def simulate_frame(
    motor: LinearBase,
    output_selector: OutputSelector,
    subjects: dict[str, Any],
    step: float,
    currents: tuple[float, float, float]
) -> dict[str, Any]:
    """
    Simulates one frame of the motor in FEMM and extracts the requested outputs.

    Args:
        motor: The LinearBase motor instance.
        output_selector: OutputSelector object for post-processing.
        subjects: Context for output functions (e.g., phase or group names).
        step: Linear displacement step to apply before simulation.
        currents: Phase current values (pa, pb, pc) to apply.

    Returns:
        Dictionary of output results.

    Raises:
        FileNotFoundError: If the FEMM .fem file cannot be opened.
        RuntimeError: If FEMM cannot be started.
    """
    fem_path = motor.get_path() + ".fem"
    ans_path = motor.get_path() + ".ans"

    try:
        femm.openfemm(1)
    except Exception as e:
        raise RuntimeError("Failed to start FEMM instance.") from e

    try:
        femm.opendocument(fem_path)
    except Exception as e:
        femm.closefemm()
        raise FileNotFoundError(f"Failed to open FEMM document: {fem_path}") from e

    if step != 0:
        motor.step(step)

    motor.set_currents(currents)

    fail_count = 0
    while fail_count < MAXIMUM_FAILS:
        try:
            femm.mi_analyse(1)
            femm.mi_loadsolution()
            break
        except Exception as e:
            fail_count += 1
            if fail_count >= MAXIMUM_FAILS:
                femm.closefemm()
                raise RuntimeError(f"FEMM analysis failed after {fail_count} attempts.") from e

    frame_result = output_selector.compute(subjects)

    femm.closefemm()

    if os.path.exists(ans_path):
        os.remove(ans_path)

    return frame_result