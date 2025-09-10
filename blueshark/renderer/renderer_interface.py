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
    def __init__(self, file_path: Path) -> None:
        """
        Initializes the renderer
        under the file_path given by the user

        Args:
            file_path (Path): Path to save or load simulation files.
        """
        self.file_path = file_path

    @abstractmethod
    def setup(
        self,
        sim_type: SimulationType,
        units: Units,
        depth: float = 0,
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
        tag_coords: tuple[float, float],
        phase: str = None,
        turns: int = None,
        magnetization: float = None
    ) -> None:
        """
        Draw geometry with given material and group.

        Args:
            geometry (Geometry): The shape to render.
            material (str): Material of the element.
            group_id (int): Group identifier.
            tag_coords (tuple): x and y coordinates of the blocklabel
            phase (str, optional): The phase the element belongs to.
            turns (int, optional): Number of turns of material
                                   within the shape.
            magnetization (float, optional): Direction of the magnetic field.
        """

    @abstractmethod
    def add_bounds(
        self,
        origin: tuple[float, float],
        radius: float,
        num_shells: int = 7,
        bound_type: int = 1,
        material: str = "Air"
    ) -> None:
        """
        Adds bounds to the simulation space

        Args:
            origin (tuple[float, float]): Center coordinates (x, y)
            radius (float): Radius of the inter most shell (solution domain)
            num_shells (int): Number of concentric shells to create.
            bound_type (int): Boundary condition type.
                            0 = Dirichlet (fixed potential),
                            1 = Neumann (zero normal derivative).
            material (str): Name of the material assigned to the shells.
        """

    @abstractmethod
    def set_property(
        self,
        origin: tuple[float, float],
        group_id: int,
        material: str = "Air"
    ) -> None:
        """
        Sets property of a undefined region such
        as the gap between the stator and armuture

        Args:
            origin (tuple[float, float]): Center coordinates (x, y)
            group_id (int): Group identifier.
            material (str): Material of the region.
        """

    @abstractmethod
    def move_group(
        self,
        group_id: tuple[float],
        delta: tuple[float, float]
    ) -> None:
        """
        Moves a group by dx in the x direction
        and dy in the y direction

        Args:
            group_id (int or tuple/list): Group identifier.
            motion (tuple[]): Step in selected units and angle in radians
        """

    @abstractmethod
    def change_phase_current(
        self,
        phase: str,
        current: float
    ) -> None:
        """
        Changes the current flowing through a phase

        Args:
            phase: Name of a circuit or phase in the renderer
            current: Represents the current in amperes flowing in the element
        """
