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
            motion_values = step.get("motion")
            groups = step.get("groups")

            if "step" in motion_values and "angle" in motion_values:
                # Linear motion
                renderer.move_group(
                    groups,
                    (
                        motion_values["step"],
                        motion_values["angle"]
                    )
                )

            elif "axis" in motion_values and "angle" in motion_values:
                # Rotational motion
                print("axis")
                renderer.rotate_group(
                    groups,
                    motion_values["axis"],
                    motion_values["angle"]
                )

            else:
                raise ValueError(f"Unknown motion dict: {motion_values}")

            current_values, phases = step["currents"]
            for i in range(0, len(current_values)):
                renderer.change_phase_current(
                    phases[i],
                    current_values[i]
                )

            # Clears up files and services related to renderer
            renderer.clean_up()

            # Simulates the frame
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


def _transient_thermal(
    renderer: BaseRenderer,
    solver: BaseSolver,
    requested_outputs: list[str],
    subjects: dict[str, Any],
    frames: Sequence[dict[str, Any]],
) -> dict[str, Any] | None:
    has_flux = any("heat_flux" in frame for frame in frames)
    if not has_flux:
        msg = "Frames must include at least 'heat flux' entry for thermal."
        logging.critical(msg)
        raise ValueError(msg)

    results = []
    try:
        for step in frames:
            motion_values = step.get("motion")
            groups = step.get("groups")

            if "step" in motion_values and "angle" in motion_values:
                # Linear motion
                renderer.move_group(
                    groups,
                    (
                        motion_values["step"],
                        motion_values["angle"]
                    )
                )

            elif "axis" in motion_values and "angle" in motion_values:
                # Rotational motion
                renderer.rotate_group(
                    groups,
                    motion_values["axis"],
                    motion_values["angle"]
                )

            else:
                raise ValueError(f"Unknown motion dict: {motion_values}")

            heat_flux_values, conductor = step["heat_flux"]
            for i in range(0, len(heat_flux_values)):
                renderer.change_phase_current(
                    conductor[i],
                    heat_flux_values[i]
                )

            # Clears up files and services related to renderer
            renderer.clean_up()

            # Simulates the frame
            frame_results = simulate_frame(
                renderer.file_path,
                solver,
                requested_outputs,
                subjects
            )
            results.append(frame_results)

        return results

    except Exception as e:
        msg = f"Failed to perform trasisent thermal simulation: {e}"
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

        case PhysicsType.THERMAL:
            return _transient_thermal(
                renderer,
                solver,
                requested_outputs,
                subjects,
                frames
            )

        case _:
            msg = f"Physics Type '{physics}' is not supported"
            raise NotImplementedError(msg)
