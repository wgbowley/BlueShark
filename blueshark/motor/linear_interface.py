"""
Filename: motor_interface.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28

Description:
    Abstract base class defining the interface for linear motor models.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, List


class LinearBase(ABC):
    """
    Abstract base class for all linear motor models.

    Subclasses must implement all abstract methods and properties defined here:
    - path: Path
    - moving_group: int or List[int]
    - motor_circumference: float 
    - number_poles: int
    - number_slots: int
    - peak_currents: Tuple[float, float]
    """

    @abstractmethod
    def __init__(self, parameter_file: Path) -> None:
        """ 
        Initialize the motor instance using a parameter file.
        
        Args:
            parameter_file (Path): Motor configuration parameter file (e.g., .yaml).
        """
        pass

    @abstractmethod
    def _unpack(self, parameter_file: Path) -> None:
        """
        Internal method to load motor parameters from configuration parameter file.
        
        Args: 
            parameter_file (Path): Motor configuration parameter file (e.g., .yaml).
        """
        pass

    @abstractmethod
    def _compute_geometry(self) -> None:
        """Compute motor geometry and geometry-based parameters."""
        pass

    @abstractmethod
    def _add_armature(self) -> None:
        """Add the armature to FEMM simulation space."""
        pass

    @abstractmethod
    def _add_stator(self) -> None:
        """Add the stator to FEMM simulation space."""
        pass

    @abstractmethod
    def _add_boundary(self) -> None:
        """Add the boundary to FEMM simulation space."""
        pass

    @abstractmethod
    def setup(self) -> None:
        """Setup the FEMM file and generate the motor geometry."""
        pass

    @abstractmethod
    def step(self, step: float) -> None:
        """
        Move the motor by a specific linear step.

        Args:
            step (float): Distance or angle to move.
        """
        pass

    @abstractmethod
    def set_currents(self, currents: tuple[float, float, float]) -> None:
        """
        Set the 3-phase currents (IA, IB, IC) for this simulation step.

        Args:
            currents (Tuple[float, float, float]): Phase A, B, C current values.
        """
        pass
    
    @abstractmethod
    def get_parameters(self) -> dict:
        """
        Return all motor configuration parameters as a dictionary.
        Useful for debugging, logging, or saving snapshots.

        Returns:
            dict: A dictionary of motor parameters.
        """
        pass
    
    @property
    @abstractmethod
    def path(self) -> Path:
        """Path for files under the motor."""
        pass

    @property
    @abstractmethod
    def moving_group(self) -> Union[int, List[int]]:
        """Group identifier(s) for the moving parts of the motor in FEMM."""
        pass

    @property
    @abstractmethod
    def motor_circumference(self) -> float:
        """'Circumference' of the motor (used for positioning)."""
        pass

    @property
    @abstractmethod
    def number_poles(self) -> int:
        """Number of magnetic poles in the motor."""
        pass

    @property
    @abstractmethod
    def number_slots(self) -> int:
        """Number of slots in the motor."""
        pass

    @property
    @abstractmethod
    def peak_currents(self) -> tuple[float, float]:
        """Current values as (flux_current_peak, force_current_peak)."""
        pass
