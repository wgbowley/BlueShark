"""
Filename: motor_interface.py
Author: William Bowley
Version: 1.0
Date: 2025-07-12
Description: 
    Abstract base class defining the interface for motor simulations.
"""

from abc import ABC, abstractmethod

class MotorBase(ABC):
    """
    Abstract base class defining the interface for motor simulation classes.
    
    Subclasses must implement these properties:
    - femmdocumentpath: str 
    - movingGroup: int  
    - motorCircumference: float
    - numberPoles: int
    - numberSlots: int
    - peakCurrents: Tuple[float, float]  # (flux, force)
    
    """
    
    @property
    @abstractmethod
    def femmdocumentpath(self) -> str:
        pass    
    
    @property
    @abstractmethod
    def movingGroup(self) -> str:
        pass 
    
    @property
    @abstractmethod
    def motorCircumference(self) -> float:
        pass

    @property
    @abstractmethod
    def numberPoles(self) -> int:
        pass

    @property
    @abstractmethod
    def numeberSlots(self) -> int:
        pass
    
    @property
    @abstractmethod
    def peakCurrents(self) -> tuple[float, float]:
        """Tuple representing (flux_current_peak, force_current_peak)"""
        pass
    
    @abstractmethod
    def __init__(self, configFile: dict):
        """Initialize the motor instance using configuration data."""
        pass

    @abstractmethod
    def unpack(self, configFile: dict) -> None:
        """Unpack the YAML configuration dictionary and set instance variables."""
        pass

    @abstractmethod
    def generate(self) -> None:
        """Generate the motor geometry or prepare the simulation environment."""
        pass

    @abstractmethod
    def step(self, step: float) -> None:
        """Move the motor by a specific step size from last point."""
        pass

    @abstractmethod
    def set_currents(self, currents: tuple[float, float, float]) -> None:
        """Set the phase currents for the motor simulation at the current step."""
        pass
