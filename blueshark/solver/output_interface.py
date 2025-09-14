"""
File: output_interface.py
Author: William Bowley
Version: 1.4
Date: 2025-09-14
Description:
    Abstract base class defining the output selector for solvers.

    - BaseSelector: Core generic methods
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Union


class BaseSelector(ABC):
    """
    Core interface for all output selectors.
    """
    @abstractmethod
    def __init__(
        self,
        requested_outputs: list[str]
    ) -> Any:
        """
        Initializes the output selector with requested outputs.
        """

    @abstractmethod
    def compute(
        self,
        subject: dict
    ) -> dict[str, Any]:
        """
        Computes all requested outputs using the provided subjects.
        """

    @abstractmethod
    def _run_element(
        self,
        function: Callable[[int], Any],
        subjects: dict
    ) -> Union[Any, list[Any]]:
        """
        Applies an element-based output function.

        Args:
            function (callable): Expects an element ID.
            subjects (dict): Must include the key `element`.
        """


class MagneticSelector(BaseSelector, ABC):
    """
    Output selector with magnetic-specific methods.
    """
    @abstractmethod
    def _run_circuit(
        self,
        function: Callable[[int], Any],
        subjects: dict
    ) -> Union[Any, list[Any]]:
        """
        Applies a circuit-based output function.

        Args:
            function (callable): Expects a circuit name.
            subjects (dict): Must include the key `circuit`.
        """


class ThermalSelector(BaseSelector, ABC):
    """
    Output selector with thermal-specific methods.
    """
    # Placeholder for any thermal-specific methods if required.


class ElectricalSelector(BaseSelector, ABC):
    """
    Output selector with electrical-specific methods.
    """
    # Placeholder for future electrical-specific methods.
    # Examples: setting electric circuits (conductors), changing voltage, etc.
