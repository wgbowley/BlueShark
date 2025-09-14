"""
Filename: static.py
Author: William Bowley
Version: 1.4
Date: 2025-09-14

Description:
    Executes a single static frame for a
    configured renderer.

    Responsibilities:
    - Runs solver analysis and computes post-processing outputs
    - Closes solver and deletes any temporary files
"""

import logging
from typing import Any, Sequence, Optional, Union

from blueshark.renderer.renderer_interface import BaseRenderer
from blueshark.solver.solver_interface import BaseSolver


def static_simulation(
    renderer: BaseRenderer,
    solver_cls: type[BaseSolver],
    requested_outputs: Union[str, list[str]],
    elements: Optional[Sequence[int]] | None = None,
    circuits: Optional[Sequence[str]] | None = None
) -> dict[str, Any]:
    """
    Runs a single static simulation using the provided solver class.

    Args:
        renderer: Specific instance of BaseRenderer
        solver_cls: Dependency injection of BaseSolver
        requested_outputs: Output(s) to compute (or "all").
        elements: List of element IDs for element-based outputs.
        circuits: List of circuit names for circuit-based outputs.

    returns:
        results: output dictionaries
    """
    elements = elements or []
    circuits = circuits or []

    solver = solver_cls(renderer, requested_outputs, elements, circuits)

    try:
        result = solver.solve()
        msg = (
            f"{solver_cls.__name__} successfully solved for {renderer}"
        )
        logging.debug(msg)
        return result

    except Exception as e:
        msg = f"{solver_cls.__name__} simulation failed for {renderer}: {e}"
        logging.error(msg)
        raise ValueError(msg) from e

    finally:
        try:
            solver.clean_up()
        except Exception as cleanup_err:
            msg = f"{solver_cls.__name__} cleanup failed: {cleanup_err}"
            logging.warning(msg)
