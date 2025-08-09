"""
Filename: frame.py
Author: William Bowley
Version: 1.2
Date: 2025-07-29

Description:
    Executes a single FEMM simulation frame for a configured motor instance.

    Responsibilities:
    - Opens FEMM and loads the motor's `.fem` file
    - Steps the motor and applies appropriate phase currents
    - Runs FEMM analysis, with retry logic on failure
    - Computes post-processing outputs as requested
    - Closes FEMM and deletes the temporary `.ans` file
"""

import os
import logging
from typing import Any
from pathlib import Path

import femm
from blueshark.output.selector import OutputSelector
from blueshark.motor.interface import LinearBase

from blueshark.configs import MAXIMUM_FAILS


def simulate_frame(
    motor: LinearBase,
    output_selector: OutputSelector,
    subjects: dict[str, Any],
    step: float,
    currents: tuple[float, float, float]
) -> dict[str, Any] | None:
    """
    Run a single FEMM frame and extract selected outputs.

    Args:
        motor (LinearBase): Motor instance to simulate.
        output_selector (OutputSelector): Defines which outputs to extract.
        subjects (dict[str, Any]): Extra metadata/context for the run.
        step (float): Displacement to move the motor to.
        currents (tuple[float, float, float]): Phase currents in amps.

    Returns:
        dict[str, Any] | None: Extracted results, or None if simulation fails.
    """

    base_path = Path(motor.path)
    fem_path = base_path.with_suffix(".fem")
    ans_path = base_path.with_suffix(".ans")

    try:
        try:
            femm.openfemm(1)
        except Exception as e:
            msg = f"Failed to start FEMM instance: {e}"
            logging.critical(msg)
            return None

        try:
            femm.opendocument(str(fem_path))
        except Exception as e:
            msg = f"Failed to open FEMM document: {fem_path} - {e}"
            logging.critical(msg)
            return None

        try:
            if step != 0:
                motor.step(step)
            motor.set_currents(currents)
        except Exception as e:
            msg = f"Failed to step motor or set currents: {e}"
            logging.error(msg)
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
                    msg = f"FEMM load failed ({fail_count} tries): {e}"
                    logging.critical(msg)
                    return None

        frame_result = output_selector.compute(subjects)

    finally:
        try:
            femm.closefemm()
        except Exception as e:
            logging.warning(f"Could not close FEMM instance: {e}")

        if os.path.exists(ans_path):
            try:
                os.remove(ans_path)
            except Exception as e:
                logging.warning(f"Could not delete .ans file {e}")

    return frame_result
