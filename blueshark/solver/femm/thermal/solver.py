"""
File: solver.py
Author: William Bowley
Version: 1.3
Date: 2025-08-09
Description:
    Solver for FEMM based on the abtrast base
    BaseSolver.

    This class is responsible for solving
    femm heat problems and doing calculations
"""

import logging
from pathlib import Path
from typing import Dict, Any

import femm
from blueshark.domain.constants import MAXIMUM_FAILS
from blueshark.solver.solver_interface import BaseSolver
from blueshark.solver.femm.thermal.output_selector import (
    OutputSelector
)


class FEMMHeatSolver(BaseSolver):
    """
    Heat solver for the femm simulator
    """
    def __init__(
        self,
        file_path: Path,
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
        self.state = False
        self.selector = OutputSelector(requested_ouputs)

    def solve(self) -> Dict[str, Any]:
        """
        Solves the magnetic problem defined by the renderer
        """
        fail_count = 0
        while fail_count < MAXIMUM_FAILS:
            try:
                femm.openfemm()
                self.state = True
                femm.opendocument(str(self.file_path))
                femm.hi_analyse(1)
                femm.hi_loadsolution()
                break
            except RuntimeError as e:
                fail_count += 1
                if fail_count >= MAXIMUM_FAILS:
                    msg = f"FEMM load failed ({fail_count} tries): {e}"
                    logging.critical(msg)
                    return None

        outputs = self.selector.compute(self.subjects)
        self._clean_up()
        return outputs

    def _clean_up(self) -> None:
        """
        Removes the temp .ans file and closes the FEMM solver.
        """
        # Ensure file_path is a Path object
        file_path = Path(self.file_path)
        ans_path = file_path.with_suffix(".ans")

        if ans_path.exists():
            try:
                ans_path.unlink()  # cleaner than os.remove
            except Exception as e:
                logging.warning(f"Could not delete .ans file: {e}")

        try:
            femm.closefemm()
            self.state = False
        except Exception as e:
            logging.warning(f"Could not close FEMM instance: {e}")
