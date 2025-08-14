"""
File: solver.py
Author: William Bowley
Version: 1.3
Date: 2025-08-09
Description:
    Solver for FEMM based on the abtrast base
    BaseSolver.

    This class is responsible for solving
    femm mangetic problems and doing calculations
"""

import logging
from typing import Dict, Any

import femm
from blueshark.domain.constants import MAXIMUM_FAILS
from blueshark.solver.solver_interface import BaseSolver
from blueshark.solver.femm.magnetic.output_selector import (
    OutputSelector
)


class FEMMMagneticsSolver(BaseSolver):
    """
    Magnetic solver for the femm simulator
    """
    def __init__(
        self,
        file_path,
        requested_ouputs,
        subjects
    ) -> None:
        """
        Initializes the sovler under the file_path
        from the renderer given by the user

        Args:
            file_path (Path): Path to save or load simulation files.
            requested_ouputs (list): Output names to compute
                                    (must be subset of output names)
            subjects (list): List of group/phases to do calculations on
        """
        self.file_path = file_path
        self.subjects = subjects

        self.selector = OutputSelector(requested_ouputs)

    def solve(self) -> Dict[str, Any]:
        fail_count = 0
        while fail_count < MAXIMUM_FAILS:
            try:
                femm.mi_analyse(1)
                femm.mi_loadsolution()
                break
            except RuntimeError as e:
                fail_count += 1
                if fail_count >= MAXIMUM_FAILS:
                    msg = f"FEMM load failed ({fail_count} tries): {e}"
                    logging.critical(msg)
                    return None

        outputs = self.selector.compute(self.subjects)
        return outputs
