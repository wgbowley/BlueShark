"""
Filename: frame.py
Author: William Bowley
Version: 1.2
Date: 2025-08-26

Description:
    Executes a single simulation frame for a configured renderer file.

    Responsibilities:
    - Runs solver analysis and computes post processing outputs
    - Closes solver and deletes any temporary files
"""

from pathlib import Path
import logging
from typing import Any, Type

from blueshark.solver.solver_interface import BaseSolver


def simulate_frame(
    renderer_file: Path,
    solver_cls: Type[BaseSolver],
    requested_outputs: list[str],
    subjects: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Runs a single simulation frame using the provided solver class.

    Args:
        renderer_file (Path): Path to the renderer file.
        solver_cls (Type[BaseSolver]): Solver class (not an instance).
        requested_outputs (list[str]): Outputs to compute.
        subjects (dict[str, Any]): Subjects for the solver.

    Returns:
        dict[str, Any] | None: Solver outputs or None if failed.
    """
    try:
        solver = solver_cls(renderer_file, requested_outputs, subjects)
        return solver.solve()
    except Exception as e:
        logging.critical(f"Simulation failed: {e}")
        raise ValueError(e)
