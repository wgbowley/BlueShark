"""
Filename: quasi_transient
Author: William
Version: 1.4
Data: 2025-09-15

Description:
    Executes a series of static frames
    to build a quasi_transient output

    Responsibilities:
    - Performs changes per frame to elements, materials,
      boundaries and circuits
    - Feeds data into static frames to get results
"""

import logging
from typing import Sequence, Any, Optional, Union
from dataclasses import dataclass

from blueshark.solver.solver_interface import BaseSolver
from blueshark.simulate.static import static_simulation
from blueshark.renderer.renderer_interface import (
    MagneticRenderer, BaseRenderer
)


@dataclass
class LinearMotion:
    magnitude: float
    angles: tuple[float, float, float]


@dataclass
class Currents:
    values: Sequence[float]
    circuits: Sequence[str]


@dataclass
class RotationalMotion:
    axis: tuple[float, float, float]
    angle: tuple[float, float, float]


@dataclass
class VolumetricHeating:
    heating: Sequence[float]
    material_name: Sequence[str]


@dataclass
class Frame:
    motion: Optional[LinearMotion | RotationalMotion] = None
    volumetric: Optional[VolumetricHeating] = None
    elements: Optional[Sequence[int]] = None
    currents: Optional[Currents] = None


def _step_magnetic(
    renderer: MagneticRenderer,
    frame: Frame
) -> None:
    """
    Performs magnetic-specific operations

    args:
        renderer: instance of the MagneticRenderer
        frame: frame dataclass instance
    """
    if frame.currents is None:
        return
    for i, val in enumerate(frame.currents.values):
        renderer.change_circuit_current(
            frame.currents.circuits[i],
            val
        )


def quasi_transient(
    renderer: BaseRenderer,
    solver_cls: type[BaseSolver],
    frames: Sequence[Frame],
    requested_outputs: Union[str, list[str]],
    elements: Optional[Sequence[int]] = None,
    circuits: Optional[Sequence[str]] = None,
    status: bool = False
) -> list[dict[str, Any]]:
    """
    Generic quasi-transient simulation.

    args:
        renderer: Specific instance of BaseRenderer
        solver: Dependency injection of BaseSolver
        frames: Sequence of frame dataclasses
        requested_outputs: Solver specific outputs
        elements: List of element IDs for element-based outputs.
        circuits: List of circuit names for circuit-based outputs.
        status: Reports progress of the quasi_transient simulation

    returns:
        results: list of output dictionaries
    """
    results = []

    try:
        for step_idx, frame in enumerate(frames, start=1):
            # Apply motion, currents, or other frame-specific effects
            if isinstance(frame.motion, LinearMotion):
                print(frame)
                renderer.move_element(
                    frame.elements,
                    frame.motion.magnitude,
                    frame.motion.angles
                )

            elif isinstance(frame.motion, RotationalMotion):
                renderer.rotate_element(
                    frame.elements,
                    frame.motion.axis,
                    frame.motion.angle
                )

            if isinstance(renderer, MagneticRenderer):
                _step_magnetic(renderer, frame)

            # Clear renderer state
            renderer.clean_up()

            # Solve the frame
            frame_result = static_simulation(
                renderer,
                solver_cls,
                requested_outputs,
                elements,
                circuits
            )
            results.append(frame_result)

            if status:
                remaining = len(frames) - step_idx
                print(f"Remaining quasi_transient frames: {remaining}")

        return results

    except Exception as e:
        msg = f"Failed at frame {step_idx}: {e}"
        logging.critical(msg)
        raise RuntimeError(msg) from e
