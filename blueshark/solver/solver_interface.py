"""
File: solver_interface.py
Author: William Bowley
Version: 1.4
Date: 2025-09-14
Description:
    Abstract base classes defining the interface for solvers.

    - BaseSolver: Core generic methods
"""

from typing import Any
from abc import ABC, abstractmethod

from blueshark.renderer.renderer_interface import BaseRenderer


class BaseSolver(ABC):
    """
    Core interface for all solvers.
    """
    @abstractmethod
    def __init__(
        self,
        renderer: BaseRenderer,
        requested_outputs: list[str],
        elements: list[int] = None,
        circuits: list[str] = None
    ) -> Any:
        """
        Initializes the solver and links the data
        file from the renderer.
        """

    @abstractmethod
    def solve(self) -> dict[str, Any]:
        """
        Solves the problem defined by the user in the
        renderer.

        Returns:
            dict[str, Any]: Outputs mapped to their values.
        """

    @abstractmethod
    def clean_up(self) -> None:
        """
        Cleans up any temporary files and closes the solver.
        """
