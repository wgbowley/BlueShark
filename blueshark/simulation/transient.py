"""
Filename: transient.py
Author: William Bowley
Version: 1.2
Date: 2025-08-26

Description:
    Executes a transient simulation for a configured renderer.

    Responsibilities:
    - Steps the specific groups and applies phase currents, heat flux or other
    - Uses the solver class inputed to solve the individual frames.
    - Results the data from output selector.
"""

import logging
from typing import Sequence, Any

from blueshark.domain.constants import PhysicsType
from blueshark.renderer.renderer_interface import BaseRenderer
from blueshark.solver.solver_interface import BaseSolver
from blueshark.simulation.frame import simulate_frame


def _transient_magnetic(
    renderer: BaseRenderer,
    solver: BaseSolver,
    requested_outputs: list[str],
    subjects: dict[str, Any],
    frames: Sequence[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Simulates the transisent problem and
    returns the outputs.

    Requires timeline entires for 'currents'
    """
    has_current = any("currents" in frame for frame in frames)
    if not has_current:
        msg = "Frames must include at least 'currents' entry for magnetic."
        logging.critical(msg)
        raise ValueError(msg)

    results = []
    try:
        for step in frames:
            if "motion" in step:
                motion_values, groups = step["motion"]
                renderer.move_group(
                    groups,
                    motion_values
                )
            if "currents" in step:
                current_values, phases = step["currents"]
                for i in range(0, len(current_values)):
                    renderer.change_phase_current(
                        phases[i],
                        current_values[i]
                    )
            frame_results = simulate_frame(
                renderer.file_path,
                solver,
                requested_outputs,
                subjects
            )
            results.append(frame_results)

        return results

    except Exception as e:
        msg = f"Failed to perform trasisent magnetic simulation: {e}"
        logging.critical(msg)
        raise ValueError(msg)


def transient_simulate(
    physics: PhysicsType,
    renderer: BaseRenderer,
    solver: BaseSolver,
    requested_outputs: list[str],
    subjects: dict[str, Any],
    frames: Sequence[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Choices the correct method for transient
    simulation of the problem.
    """
    match physics:
        case PhysicsType.MAGNETIC:
            return _transient_magnetic(
                renderer,
                solver,
                requested_outputs,
                subjects,
                frames
            )
