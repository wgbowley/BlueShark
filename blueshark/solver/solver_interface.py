"""
File: solver_interface.py
Author: William Bowley
Version: 1.1
Date: 2025-08-09
Description:
    Abstract base class defining the interface for solver.

    This interface standardizes how solvers interact with the
    framework, ensuring consistent usage.
"""

from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseSolver(ABC):
    """
    Standarized interface for solvers
    """
    @abstractmethod
    def __init__(
        self,
        file_path: Path,
        requested_ouputs: List[str],
        subjects: List[str]
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

    @abstractmethod
    def solve(self) -> Dict[str, Any]:
        """
        Solves the problem defined by the user in the
        renderer

        Returns: Outputs dict[str, Any]
        """

    @abstractmethod
    def _clean_up(self) -> None:
        """
        Cleans up an temporary files after solving the problem and closes
        the solver also.
        """
