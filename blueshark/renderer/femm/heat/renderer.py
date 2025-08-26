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
from blueshark.domain.generation.geometric_centroid import centroid_point
from blueshark.renderer.femm.heat.hybrid_geometry import draw_hybrid
from blueshark.renderer.femm.heat.properties import (
    add_conductor, set_properties
)
from blueshark.renderer.femm.heat.primitives import (
    draw_polygon,
    draw_circle,
    draw_annulus_circle,
    draw_annulus_sector
)
from blueshark.domain.constants import (
    SimulationType,
    Units,
    Geometry,
    ShapeType
)
from blueshark.renderer.femm.heat.materials import (
    load_materials,
    add_femm_material
)


class FEMMHeatflowRenderer(BaseRenderer):
    """
    Heat flow renderer for the femm simulator
    """
    def __init__(
        self,
        file_path: Path,
        boundary_temperature: float = 288.15
    ) -> None:
        """
        Initializes the femm heat flow renderer
        under the file_path given by the user

        Sets boundary temperature to average room
        temperature of 15 degrees Celsius
        """

        self.file_path = file_path
        self.materials = load_materials()
        self.set_materials = []
        self.boundary = boundary_temperature
        self.phases = []

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
            femm.hi_probdef(
                units.value,
                problem_type,
                1e-8,
                depth
            )

            femm.hi_saveas(str(self.file_path))
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
        phase: str = None,
        turns: int = None,              # required by ABC, Unused
        magnetization: float = None     # required by ABC, Unused
    ) -> None:
        """
        Draws elements to the simulation through their geometry,
        and other properties
        """
        _ = turns
        _ = magnetization

        points = _
        shape = geometry.get("shape")
        match shape:
            case ShapeType.POLYGON | ShapeType.RECTANGLE:
                points = draw_polygon(geometry["points"])

            case ShapeType.CIRCLE:
                points = draw_circle(
                    geometry["radius"],
                    geometry["center"]
                )

            case ShapeType.ANNULUS_SECTOR:
                points = draw_annulus_sector(
                    geometry["center"],
                    geometry["radius_outer"],
                    geometry["radius_inner"],
                    geometry["start_angle"],
                    geometry["end_angle"]
                )

            case ShapeType.ANNULUS_CIRCLE:
                points = draw_annulus_circle(
                    geometry["center"],
                    geometry["radius_outer"],
                    geometry["radius_inner"]
                )

            case ShapeType.HYBRID:
                if "edges" not in geometry:
                    raise ValueError("Hybrid shape requires 'edges' field")
                draw_hybrid(geometry["edges"])
                points = geometry["edges"]

            case _:
                raise NotImplementedError(f"Shape '{shape}' not supported")

        # adds material to simulation space
        if material not in self.set_materials:
            self.set_materials.append(material)
            add_femm_material(
                self.materials,
                material
            )

        # Checks for phase and if not than adds the phase
        if phase is not None and phase not in self.phases:
            self.phases.append(phase)
            add_conductor(phase, 1)

        # Adds blocklabel and set properties of it
        if tag_coords is None:
            tag_coords = centroid_point(geometry)

        set_properties(
            tag_coords,
            group_id,
            material
        )

        femm.hi_saveas(str(self.file_path))

    def add_bounds(
        self,
        origin,
        radius,
        num_shells=7,
        bound_type=1,
        material="Air"
    ):
        return None

    def change_phase_current(self, phase, current):
        return None

    def move_group(self, group_id, delta):
        return None

    def rotate_group(self, group_id, point, angle):
        return None

    def set_property(self, origin, group_id, material="Air"):
        return None