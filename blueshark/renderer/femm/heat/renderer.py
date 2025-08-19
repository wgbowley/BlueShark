"""
File: renderer.py
Author: William Bowley
Version: 1.3
Date: 2025-08-19
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

from blueshark.renderer.renderer_interface import BaseRenderer
from blueshark.renderer.femm.magnetic.boundary import add_bounds
from blueshark.domain.constants import (
    SimulationType,
    Units,
    Geometry
)
# from blueshark.renderer.femm.magnetic.materials import (
#     load_materials,
#     add_femm_material
# )


class FEMMHeatflowRenderer(BaseRenderer):
    """
    Heat flow renderer for the femm simulator
    """
    def __init__(self, file_path: Path) -> None:
        """
        Initializes the femm heat flow renderer
        under the file_path given by the user
        """
        self.file_path = file_path
        # self.materials = load_materials()
        self.set_materials = []
        self.boundaries = []
        self.conductors = []

    def setup(
        self,
        sim_type: SimulationType,
        units: Units,
        depth: float = 0
    ) -> None:
        """
        Setup the rendering environment and simulation space
        """

        try:
            femm.openfemm(1)  # Opens femm in hiden window
            femm.newdocument(2)  # Magnetic simulation

            problem_type = None
            if sim_type == SimulationType.AXI_SYMMETRIC:
                problem_type = "axi"
            elif sim_type == SimulationType.PLANAR:
                problem_type = "planar"

            # Defines the problem
            femm.mi_probdef(
                problem_type,
                units.value,
                1e-8,
                depth
            )

            femm.mi_saveas(str(self.file_path))
        except Exception as e:
            msg = f"FEMM Heat flow Setup failed ({sim_type}): {e}"
            logging.critical(msg)
            raise RuntimeError(f"{self.__class__.__name__}: {msg}") from e

    def draw(
        self,
        geometry: Geometry,
        material: str,
        group_id: int,
        tag_coords: tuple[float, float] = None,
    ) -> None:
        """
        Draws elements to the simulation through their geometry,
        and other properties
        """

        shape = geometry.get("shape")
        match shape:
            case _:
                raise NotImplementedError(f"Shape '{shape}' not supported")

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
        """

        # adds material to simulation space
        # add_femm_material(
        #     self.materials,
        #     material
        # )

        add_bounds(
            origin,
            radius,
            num_shells,
            bound_type,
            material
        )

        # Saves changes to femm file
        femm.mi_saveas(str(self.file_path))
