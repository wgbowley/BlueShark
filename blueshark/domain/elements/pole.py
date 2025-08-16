"""
Filename: slot.py
Author: William Bowley
Version: 1.3
Date: 2025-08-12

Description:
    This class defines what a pole is within
    the simulator. It is used as a high-level
    interface between a motor model file
    and the solver.
"""

import logging

from blueshark.domain.constants import Geometry
from blueshark.renderer.renderer_interface import BaseRenderer


class Pole:
    """
    Poles are openings within the stator that
    house magnetic material that the armature slots interact against.
    """

    def __init__(
        self,
        geometry: Geometry,
        material: str,
        group_id: int,
        magnetization_angle: float
    ) -> None:
        """
        Initialize the Pole with its parameters.

        Args:
            geometry (Geometry): Defines the shape of pole in simulation space.
            material (str): Material of the pole.
            group_id (int): Group that the pole belongs to.
            magnetization_angle (float): Angle of magnetization of the
                                         pole material (radians).
        """

        if not isinstance(group_id, int):
            msg = f"Group_id must be an integer, got {group_id!r}"
            logging.critical(msg)
            raise ValueError(f"{self.__class__.__name__}: {msg}")

        # Normalize magnetization angle to [0, 360)
        if not 0 <= magnetization_angle < 360:
            old_angle = magnetization_angle
            magnetization_angle %= 360
            msg = (
                f"Mag angle: {old_angle:.3f}→{magnetization_angle:.3f} degrees"
            )
            logging.warning(msg)

        self.geometry = geometry
        self.material = material
        self.group_id = group_id
        self.magnetization_angle = magnetization_angle

    def draw(self, renderer: BaseRenderer) -> None:
        """
        Render the pole to the solver's simulation space.

        Args:
            renderer (Any): Specific renderer used by the solver.
        """

        renderer.draw(
            geometry=self.geometry,
            material=self.material,
            group_id=self.group_id,
            magnetization=self.magnetization_angle
        )
