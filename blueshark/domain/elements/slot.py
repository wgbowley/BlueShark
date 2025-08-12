"""
Filename: slot.py
Author: William Bowley
Version: 1.3
Date: 2025-08-12

Description:
    This class defines what a slot is within
    the simulator. It is used as a high-level
    interface between a motor model file
    and the solver.
"""

import logging
import warnings

from math import ceil
from blueshark.domain.generation.geometry import calculate_area
from blueshark.renderer.renderer_interface import BaseRenderer
from blueshark.domain.constants import (
    CurrentPolarity, Geometry
)


class Slot:
    """
    Slots are openings within the armature that
    have the function of housing the windings
    that carry electrical current
    """
    def __init__(
        self,
        phase: str,
        polarity: CurrentPolarity,
        geometry: Geometry,
        material: str,
        group_id: int,
        wire_diameter: float,
        fill_factor: float = 1.0,
    ) -> None:
        """
        Initial setup of the slot class with its
        parameters

        Args:
            phase: The phase of the slot
            polarity: The direction of the current through it
            material: Material of the slot
            group_id: Group that the slot belongs to
            wire_diameter: The diameter of the wire used
            fill_factor: How effectively the coils are winded
            geometry: Defines the shape of the slot in simulation space
        """

        if not isinstance(group_id, int):
            msg = f"Group_id must an integer, got {group_id}"
            logging.critical(msg)
            raise ValueError(f"{self.__class__.__name__}: {msg}")

        if wire_diameter <= 0 or not isinstance(wire_diameter, float):
            msg = f"Wire diameter must an positive float, got {wire_diameter}"
            logging.critical(msg)
            raise ValueError(f"{self.__class__.__name__}: {msg}")

        if fill_factor <= 0 or fill_factor >= 1:
            msg = f"Fill factor must be between 0 and 1, got {fill_factor}"
            logging.critical(msg)
            raise ValueError(f"{self.__class__.__name__}: {msg}")

        self.phase = phase
        self.polarity = polarity
        self.material = material
        self.group_id = group_id
        self.geometry = geometry
        self.fill_factor = fill_factor
        self.wire_diameter = wire_diameter

    def estimate_turns(self) -> int:
        """
        Calculates the approximate number of turns
        for any slot with area
        """
        slot_area = self._area()
        wire_area = self.wire_diameter ** 2
        effective_area = slot_area * self.fill_factor

        if wire_area == 0:
            msg = "Calculated number of turns is zero"
            logging.error(msg)
            warnings.warn(f"{self.__class__.__name__}: {msg}")
            return 0

        turns = effective_area / wire_area
        return ceil(turns)

    def draw(self, renderer: BaseRenderer) -> None:
        """
        Renders the slot to the solver's simulation space

        Args:
            Renderer: Specific renderer used by the solver
        """
        turns = self.estimate_turns()

        renderer.draw(
            self.geometry,
            self.material,
            self.group_id,
            phase=self.phase,
            turns=turns
        )

    def _area(self) -> float:
        return calculate_area(self.geometry)
