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

from blueshark.renderer.femm.magnetic.shapes import (
    draw_polygon,
    draw_circle,
    draw_annulus_sector,
    draw_annulus_circle
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
    def setup(
        self,
        sim_type: SimulationType,
        units: Units,
        file_path: Path,
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

            self.file_path = file_path  # Really bad pratice lol

            femm.mi_saveas(str(file_path))
        except Exception as e:
            msg = f"FEMM Setup failed ({sim_type}): {e}"
            logging.critical(msg)
            raise RuntimeError(f"{self.__class__.__name__}: {msg}") from e

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
        Draws elements to the simulation through their geometry,
        and other properties (Work In progress)
        """

        shape = geometry.get("shape")
        points = geometry.get("points", [])
        match shape:
            case ShapeType.POLYGON | ShapeType.RECTANGLE:
                if not points or len(points) < 3:
                    msg = (
                        "At least 3 points required for polygon/rectangle area"
                    )
                    logging.error(msg)
                    raise RuntimeError(f"{__name__}: {msg}")

                draw_polygon(geometry["points"])

            case ShapeType.CIRCLE:
                radius = geometry.get("radius")
                center = geometry.get("center")

                if radius is None or center is None:
                    msg = "Circle radius and center must be defined"
                    logging.error(msg)
                    raise ValueError(f"{__name__}: {msg}")

                draw_circle(radius, center)

            case ShapeType.ANNULUS_SECTOR:
                center = geometry.get("center")
                r_outer = geometry.get("radius_outer")
                r_inner = geometry.get("radius_inner")
                start_angle = geometry.get("start_angle")
                end_angle = geometry.get("end_angle")

                if None in (r_outer, r_inner, start_angle, end_angle):
                    msg = "Annulus Sector parameters missing"
                    logging.error(msg)
                    raise ValueError(f"{__name__}: {msg}")

                draw_annulus_sector(
                    center,
                    r_outer,
                    r_inner,
                    start_angle,
                    end_angle
                )

            case ShapeType.ANNULUS_CIRCLE:
                center = geometry.get("center")
                r_outer = geometry.get("radius_outer")
                r_inner = geometry.get("radius_inner", 0)

                if r_outer is None:
                    msg = "Annulus Circle parameters missing"
                    logging.error(msg)
                    raise ValueError(f"{__name__}: {msg}")

                draw_annulus_circle(
                    center,
                    r_outer,
                    r_inner
                )

            case _:
                raise NotImplementedError(f"Shape '{shape}' not supported")

        # Saves changes to femm file
        femm.mi_saveas(str(self.file_path))
