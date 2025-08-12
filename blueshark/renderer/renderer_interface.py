"""
File: renderer_interface.py
Author: William Bowley
Version: 1.1
Date: 2025-08-09
Description:
    Abstract base class defining the interface for renderers.

    This interface standardizes how renderers interact with the
    framework, ensuring consistent usage.
"""

from pathlib import Path
from abc import ABC, abstractmethod
from blueshark.domain.constants import (
    Geometry, Units, SimulationType
)


class BaseRenderer(ABC):
    """
    Standardized interface for renderers.
    """
    @abstractmethod
    def setup(
        self,
        sim_type: SimulationType,
        units: Units,
        file_path: Path,
        depth: float = 0,
        frequency: float = 0,
    ) -> None:
        """
        Setup the rendering environment or simulation space.

        Args:
            file_path (Path): Path to save or load simulation files.
        """

    @abstractmethod
    def draw(
        self,
        geometry: Geometry,
        material: str,
        group_id: int,
        phase: str = None,
        turns: int = 0,
        magnetization: float = 0.0
    ) -> None:
        """
        Draw geometry with given material and group.

        Args:
            geometry (Geometry): The shape to render.
            material (str): Material of the element.
            group_id (int): Group identifier.
            phase (str, optional): The phase the element belongs to.
            turns (int, optional): Number of turns of material
                                   within the shape.
            magnetization (float, optional): Direction of the magnetic field.
        """
