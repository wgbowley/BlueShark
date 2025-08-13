"""
File: renderer.py
Author: William Bowley
Version: 1.1
Date: 2025-08-09
Description:
    Renderer for FEMM based on the abtrast base
    BaseRenderer.

    This class is responsible for setup the femm
    enviroment and also drawing elements to the
    simulation space
"""

from pathlib import Path
import logging

import femm

from blueshark.renderer.femm.magnetic.primitives import (
    draw_polygon,
    draw_circle,
    draw_annulus_sector,
    draw_annulus_circle
)
from blueshark.domain.generation.geometric_centroid import (
    centroid_point
)
from blueshark.renderer.femm.magnetic.properties import (
    set_properties
)
from blueshark.renderer.renderer_interface import BaseRenderer
from blueshark.domain.constants import (
    SimulationType,
    Geometry,
    ShapeType,
    Units
)


class FEMMMagneticsRenderer(BaseRenderer):
    """
    Magnetic renderer for the femm simulator
    """

    def __init__(self, file_path: Path):
        """
        Initializes the femm magnetic renderer
        under the file_path given by the user
        """
        self.file_path = Path(file_path)

    def setup(
        self,
        sim_type: SimulationType,
        units: Units,
        depth: float = 0,
        frequency: float = 0,
    ) -> None:
        """
        Setup the rendering environment or simulation space
        """

        try:
            femm.openfemm(1)  # Opens femm in hiden window
            femm.newdocument(0)  # Magnetic simulation

            problem_type = None
            if sim_type == SimulationType.AXI_SYMMETRIC:
                problem_type = "axi"
            elif sim_type == SimulationType.PLANAR:
                problem_type = "planar"

            # Defines the problem
            femm.mi_probdef(
                frequency,
                units.value,
                problem_type,
                1e-8,
                depth
            )

            femm.mi_saveas(str(self.file_path))
        except Exception as e:
            msg = f"FEMM Setup failed ({sim_type}): {e}"
            logging.critical(msg)
            raise RuntimeError(f"{self.__class__.__name__}: {msg}") from e

    def draw(
        self,
        geometry: Geometry,
        material: str,
        group_id: int,
        tag_coords: tuple[float, float] = None,
        phase: str = None,
        turns: int = 0,
        magnetization: float = 0.0
    ) -> None:
        """
        Draws elements to the simulation through their geometry,
        and other properties (Work In progress)
        """

        shape = geometry.get("shape")
        match shape:
            case ShapeType.POLYGON | ShapeType.RECTANGLE:
                draw_polygon(geometry["points"])

            case ShapeType.CIRCLE:
                draw_circle(
                    geometry["radius"],
                    geometry["center"]
                )

            case ShapeType.ANNULUS_SECTOR:
                draw_annulus_sector(
                    geometry["center"],
                    geometry["radius_outer"],
                    geometry["radius_inner"],
                    geometry["start_angle"],
                    geometry["end_angle"]
                )

            case ShapeType.ANNULUS_CIRCLE:
                draw_annulus_circle(
                    geometry["center"],
                    geometry["radius_outer"],
                    geometry["radius_inner"]
                )

            case _:
                raise NotImplementedError(f"Shape '{shape}' not supported")

        # Adds blocklabel and sets properties of it
        if tag_coords is None:
            tag_coords = centroid_point(geometry)

        set_properties(
            tag_coords,
            group_id,
            material,
            magnetization
        )

        # Saves changes to femm file
        femm.mi_saveas(str(self.file_path))
