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
from pathlib import Path
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
) -> dict[str, Any] | None:
    """
    Simulates one frame of the motor in FEMM and extracts the requested outputs.

    Returns:
        Dictionary of output results, or None if simulation fails.
    """

    base_path = Path(motor.get_path())
    fem_path = base_path.with_suffix(".fem")
    ans_path = base_path.with_suffix(".ans")

    try:
        femm.openfemm(1)
    except Exception as e:
        print(f"[ERROR] Failed to start FEMM instance: {e}")
        return None

    try:
        femm.opendocument(str(fem_path))
    except Exception as e:
        print(f"[ERROR] Failed to open FEMM document: {fem_path} — {e}")
        femm.closefemm()
        return None

    try:
        if step != 0:
            motor.step(step)
        motor.set_currents(currents)
    except Exception as e:
        print(f"[ERROR] Failed to step motor or set currents: {e}")
        femm.closefemm()
        return None

    fail_count = 0
    while fail_count < MAXIMUM_FAILS:
        try:
            femm.mi_analyse(1)
            femm.mi_loadsolution()
            break
        except Exception as e:
            fail_count += 1
            if fail_count >= MAXIMUM_FAILS:
                print(f"[ERROR] FEMM analysis failed after {fail_count} attempts: {e}")
                femm.closefemm()
                return None

    frame_result = output_selector.compute(subjects)

    femm.closefemm()

    if os.path.exists(ans_path):
        os.remove(ans_path)

    return frame_result
