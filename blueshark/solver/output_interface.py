"""
File: output_interface.py
Author: William Bowley
Version: 1.3
Date: 2025-08-26
Description:
    Abstract base class defining the output selector for solvers.

    This interface standardizes how solvers interact with the
    framework, ensuring consistent usage.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Union


class BaseSelector(ABC):
    """
    Standarized interface for output selectors
    """

    def __init__(
        self,
        requested_outputs: list[str]
    ) -> None:
        """
        Initialize the output selector with requested
        output names

        Args:
            requested_outputs (list): Output names to compute.
            Must be a subset of available outputs.
        """
        self.requested_outputs = requested_outputs

    @abstractmethod
    def compute(
        self,
        subject: dict
    ) -> dict[str, Any]:
        """
        Compute all requested outputs using provided subjects.

        Args:
            subjects (dict): Should contain 'group' or 'phaseName' keys.

        Returns:
            dict: Output names mapped to results.
        """

    @abstractmethod
    def _run_group(
        self,
        function: Callable[[int], Any],
        subjects: dict
    ) -> Union[Any, list[Any]]:
        """
        Apply a group-based output function.

        Args:
            function (callable): Expects a group ID.
            subjects (dict): Must include 'group'.

        Returns:
            Result or list of results.
        """

    @abstractmethod
    def _run_phase(
        self,
        function: Callable[[str], Any],
        subjects: dict
    ) -> Union[Any, list[Any]]:
        """
        Apply a phase-based output function.

        Args:
            function (callable): Expects a phase name.
            subjects (dict): Must include 'phaseName'.

        Returns:
            Result or list of results.
        """
