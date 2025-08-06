"""
Filename: motor_interface.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28

Description:
    Abstract base class defining the interface for linear motor models.

    This interface standardizes how motor models interact with the FEMM
    simulation, ensuring consistent setup, stepping, and parameter management.
"""

from abc import ABC, abstractmethod

from pathlib import Path
from typing import Union, List


class LinearBase(ABC):
    """
    Abstract base class for all linear motor models.

    Defines the required interface methods and properties.
    """

    @abstractmethod
    def __init__(self, parameter_file: Path) -> None:
        """
        Initialize the motor instance using a parameter file.

        Args:
            parameter_file (Path): Motor configuration parameter file
            (e.g., .yaml).
        """

    @abstractmethod
    def _unpack(self, parameter_file: Path) -> None:
        """
        Internal method to load motor parameters from parameter file.

        Args:
            parameter_file (Path): Motor configuration parameter file
            (e.g., .yaml).
        """

    @abstractmethod
    def _compute_geometry(self) -> None:
        """Compute motor geometry and geometry-based parameters."""

    @abstractmethod
    def _add_armature(self) -> None:
        """Add the armature to FEMM simulation space."""

    @abstractmethod
    def _add_stator(self) -> None:
        """Add the stator to FEMM simulation space."""

    @abstractmethod
    def _add_boundary(self) -> None:
        """Add the boundary to FEMM simulation space."""

    @abstractmethod
    def setup(self) -> None:
        """Setup the FEMM file and generate the motor geometry."""

    @abstractmethod
    def step(self, step: float) -> None:
        """
        Move the motor by a specific linear step.

        Args:
            step (float): Distance or angle to move.
        """

    @abstractmethod
    def set_currents(self, currents: tuple[float, float, float]) -> None:
        """
        Set the 3-phase currents (IA, IB, IC) for this simulation step.

        Args:
            currents (Tuple[float, float, float]): A, B, C current values.
        """

    @abstractmethod
    def get_parameters(self) -> dict:
        """
        Return all motor configuration parameters as a dictionary.
        Useful for debugging, logging, or saving snapshots.

        Returns:
            dict: A dictionary of motor parameters.
        """

    @property
    @abstractmethod
    def path(self) -> Path:
        """Path for files under the motor."""
        return Path

    @property
    @abstractmethod
    def moving_group(self) -> Union[int, List[int]]:
        """Group identifier(s) for the moving parts of the motor in FEMM."""
        return Union[int, list[int]]

    @property
    @abstractmethod
    def circumference(self) -> float:
        """'Circumference' of the motor (used for positioning)."""
        return float

    @property
    @abstractmethod
    def number_poles(self) -> int:
        """Number of magnetic poles in the motor."""
        return int

    @property
    @abstractmethod
    def number_slots(self) -> int:
        """Number of slots in the motor."""
        return int

    @property
    @abstractmethod
    def peak_currents(self) -> tuple[float, float]:
        """Current values as (flux_current_peak, force_current_peak)."""
        return tuple[float, float]
