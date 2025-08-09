"""
Filename: actions.py
Author: William Bowley
Version: 0.1
Date: 2025-08-09
Description:
    Functions for moving armuture or stator and
    setting currents within the motors phases.
"""

import math
import logging
import femm


def femm_step(
    groups: tuple[float],
    step: float,
    angle: float
) -> None:
    """
    Translates one or more selected groups by a specified step and angle.

    The function decomposes the step magnitude and angle into X and Y
    components and applies a single translation to all specified groups.

    Args:
        groups: An integer or a list/tuple of integers representing the
                FEMM group numbers to be moved.
        step: The magnitude of the linear step in millimeters.
        angle: The direction of the step in radians.

    Raises:
        RuntimeError: If the translation in FEMM fails for any reason.
    """
    try:
        if not isinstance(groups, (list, tuple)):
            groups_to_move = [groups]
        else:
            groups_to_move = groups

        for group in groups_to_move:
            femm.mi_selectgroup(group)

        sx = step * math.cos(angle)
        sy = step * math.sin(angle)

        femm.mi_movetranslate(sx, sy)
        femm.mi_clearselected()

    except Exception as e:
        msg = f"Failed to move group(s) {groups_to_move} in FEMM: {e}"
        logging.critical(msg)
        raise RuntimeError(msg) from {e}


def femm_set_currents(
    phases: list[str],
    currents: tuple[float]
) -> None:
    """
    Sets the currents for specified phases in a FEMM simulation.

    This function iterates through a list of phase names and a tuple of
    current values, setting the current for each phase in order.

    Args:
        phases: A list of strings, where each string is the name of a
                circuit or phase in the FEMM model.
        currents: A tuple of floats, with each float representing the
                  current in Amperes for the corresponding phase.

    Raises:
        RuntimeError: If there is a failure when setting the currents
                      in the FEMM simulation.
    """
    try:
        for phase, current in zip(phases, currents):
            femm.mi_setcurrent(phase, float(current))

    except Exception as e:
        msg = f"Failed to set currents in FEMM: {e}"
        logging.critical(msg)
        raise RuntimeError(msg) from e
