"""
Filename: motor_interface.py
Author: William Bowley
Version: 1.1
Date: 2025-07-12

Description:
    Abstract base class defining the interface for motor models.
"""

from abc import ABC, abstractmethod
from typing import Tuple


class MotorBase(ABC):
    """
    Abstract base class for motor simulation models.

    Subclasses must implement:
    - path: str
    - movingGroup: int
    - motorCircumference: float
    - numberPoles: int
    - numberSlots: int
    - peakCurrents: Tuple[float, float]  # (flux, force)
    """

    @property
    @abstractmethod
    def path(self) -> str:
        """Path for files under the motor."""
        pass

    @property
    @abstractmethod
    def movingGroup(self) -> int:
        """Group identifier for the moving part of the motor in FEMM."""
        pass

    @property
    @abstractmethod
    def motorCircumference(self) -> float:
        """Circumference of the motor (used for torque or positioning)."""
        pass

    @property
    @abstractmethod
    def numberPoles(self) -> int:
        """Number of magnetic poles in the motor."""
        pass

    @property
    @abstractmethod
    def numberSlots(self) -> int:
        """Number of coil slots in the stator or moving part."""
        pass

    @property
    @abstractmethod
    def peakCurrents(self) -> Tuple[float, float]:
        """Peak current values as (flux_current_peak, force_current_peak)."""
        pass

    @abstractmethod
    def __init__(self, config_file: dict):
        """
        Initialize the motor instance using a configuration dictionary.

        Args:
            config_file (dict): Motor configuration parameters.
        """
        pass

    @abstractmethod
    def _unpack(self, config_file: dict) -> None:
        """
        Internal method to load motor parameters from a configuration dictionary.

        Args:
            config_file (dict): Dictionary of motor settings.
        """
        pass

    @abstractmethod
    def generate(self) -> None:
        """Generate the motor geometry and setup in FEMM."""
        pass

    @abstractmethod
    def step(self, step: float) -> None:
        """
        Move the motor by a specific linear or angular step.

        Args:
            step (float): Distance or angle to move.
        """
        pass

    @abstractmethod
    def set_currents(self, currents: Tuple[float, float, float]) -> None:
        """
        Set the 3-phase currents (IA, IB, IC) for this simulation step.

        Args:
            currents (Tuple[float, float, float]): Phase A, B, C current values.
        """
        pass
