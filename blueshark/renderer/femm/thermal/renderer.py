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
import math
import logging
import femm


from blueshark.renderer.renderer_interface import BaseRenderer
from blueshark.domain.generation.geometric_centroid import centroid_point
from blueshark.renderer.femm.thermal.hybrid_geometry import draw_hybrid
from blueshark.renderer.femm.thermal.properties import (
    create_conductor, set_properties, assign_conductor, update_conductor,
    assign_boundary, assign_group
)
from blueshark.renderer.femm.thermal.primitives import (
    draw_polygon,
    draw_circle,
    draw_annulus_circle,
    draw_annulus_sector
)
from blueshark.domain.constants import (
    SimulationType,
    Units,
    Geometry,
    ShapeType,
    Connectors
)
from blueshark.renderer.femm.thermal.materials import (
    load_materials,
    add_femm_material
)
from blueshark.renderer.femm.thermal.boundary import (
    add_bounds
)
from blueshark.visualization.renderer import Visualize


class FEMMHeatflowRenderer(BaseRenderer):
    """
    Heat flow renderer for the femm simulator
    """
    def __init__(
        self,
        file_path: Path,
        grid_size: tuple[int, int],
        ambient_material: str,
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
        self.contours = {
            Connectors.LINE: [],
            Connectors.ARC: []
        }
        self.grid = Visualize(
            grid_size[0],
            grid_size[1],
            ambient_material,
            SimulationType.PLANAR  # This might fuck me over in the future
        )
        self.state = False
        self.ambient_material = ambient_material
        self.grid.initalize_map()

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
            self.state = True
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
        self._check_state()
        elements = _
        shape = geometry.get("shape")
        self.grid.draw(geometry, material, tag_coords)
        match shape:
            case ShapeType.POLYGON | ShapeType.RECTANGLE:
                elements = draw_polygon(
                    geometry["points"], geometry["enclosed"]
                )

            case ShapeType.CIRCLE:
                elements = draw_circle(
                    geometry["radius"],
                    geometry["center"]
                )

            case ShapeType.ANNULUS_SECTOR:
                elements = draw_annulus_sector(
                    geometry["center"],
                    geometry["radius_outer"],
                    geometry["radius_inner"],
                    geometry["start_angle"],
                    geometry["end_angle"]
                )

            case ShapeType.ANNULUS_CIRCLE:
                elements = draw_annulus_circle(
                    geometry["center"],
                    geometry["radius_outer"],
                    geometry["radius_inner"]
                )

            case ShapeType.HYBRID:
                if "edges" not in geometry:
                    raise ValueError("Hybrid shape requires 'edges' field")
                elements = draw_hybrid(geometry["edges"])

            case _:
                raise NotImplementedError(f"Shape '{shape}' not supported")

        elements_with_group = {}

        for connector_type, points in elements.items():
            elements_with_group[connector_type] = [
                (*pt, group_id) for pt in points
            ]

        if phase is None:
            self.contours[Connectors.LINE].extend(
                elements_with_group[Connectors.LINE]
            )
            self.contours[Connectors.ARC].extend(
                elements_with_group[Connectors.ARC]
            )

        # Assigns the group to the contours
        assign_group(
            elements_with_group
        )

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
            create_conductor(phase, 1)

        if phase in self.phases:
            assign_conductor(
                elements_with_group,
                phase
            )

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
        self._check_state()
        add_bounds(origin, radius)
        femm.hi_saveas(str(self.file_path))

    def change_phase_current(
        self,
        phase,
        heat_flux,
        current: int = 0  # required by ABC, Unused
    ) -> None:
        self._check_state()
        _ = current
        update_conductor(phase, heat_flux)
        femm.hi_saveas(str(self.file_path))

    def set_property(self, origin, group_id, material="Air"):
        self._check_state()
        set_properties(
            origin,
            group_id,
            material
        )
        femm.hi_saveas(str(self.file_path))

    def set_boundaries(self, boundpropname: str) -> None:
        self._check_state()
        # Step 1: find air boundaries
        air_boundaries = self.grid.find_boundary_segments(
            self.contours,
            self.ambient_material
        )
        # Step 2: assign AIR boundaries
        assign_boundary(air_boundaries, boundpropname)

        # Step 4: save
        femm.hi_saveas(str(self.file_path))

    def create_surface_condition(
        self,
        boundpropname: str,
        condition_type: str,
        Tset: float = 0.0,
        qs: float = 0.0,
        Tinf: float = 0.0,
        h: float = 0.0,
        beta: float = 0.0
    ) -> None:
        """
        Creates a surface boundary condition in FEMM.

        Args:
            boundpropname: Name of the boundary property
            condition_type: Type of boundary condition. One of:
                "fixed_temp", "heat_flux", "convection", "radiation",
                "periodic", "anti_periodic"
            Tset: Set temperature (used for fixed_temp)
            qs: Heat flux density (used for heat_flux)
            Tinf: External temperature (used for convection or radiation)
            h: Heat transfer coefficient (used for convection)
            beta: Emissivity (used for radiation)
        """
        self._check_state()
        match condition_type:
            case "fixed_temp":
                BdryFormat = 0
                femm.hi_addboundprop(
                    boundpropname, BdryFormat, Tset, 0, 0, 0, 0
                )

            case "heat_flux":
                BdryFormat = 1
                femm.hi_addboundprop(
                    boundpropname, BdryFormat, 0, qs, 0, 0, 0
                )

            case "convection":
                BdryFormat = 2
                femm.hi_addboundprop(
                    boundpropname, BdryFormat, 0, 0, Tinf, h, 0
                )

            case "radiation":
                BdryFormat = 3
                femm.hi_addboundprop(
                    boundpropname, BdryFormat, 0, 0, Tinf, 0, beta
                )

            case "periodic":
                BdryFormat = 4
                femm.hi_addboundprop(
                    boundpropname, BdryFormat, 0, 0, 0, 0, 0
                )

            case "anti_periodic":
                BdryFormat = 5
                femm.hi_addboundprop(
                    boundpropname, BdryFormat, 0, 0, 0, 0, 0
                )

            case _:
                raise ValueError(f"Unknown condition type: {condition_type}")

        femm.hi_saveas(str(self.file_path))

    def rotate_group(
        self,
        groups: int,
        axis: tuple[float, float],
        angle: float
    ) -> None:
        """
        Rotates a group by a angle around a point in space
        """
        self._check_state()
        x, y = axis
        if not isinstance(groups, (list, tuple)):
            groups_to_move = [groups]
        else:
            groups_to_move = groups

        for group in groups_to_move:
            femm.hi_selectgroup(group)

        femm.hi_moverotate(x, y, angle)
        femm.hi_clearselected()

        # Saves changes to femm file
        femm.hi_saveas(str(self.file_path))

    def move_group(
        self,
        groups: int,
        delta: tuple[float, float]
    ) -> None:
        """
        Moves a group by dx and dy
        """
        self._check_state()
        try:
            if not isinstance(groups, (list, tuple)):
                groups_to_move = [groups]
            else:
                groups_to_move = groups

            for group in groups_to_move:
                femm.hi_selectgroup(group)

            step, angle = delta
            sx = step * math.cos(angle)
            sy = step * math.sin(angle)

            femm.hi_movetranslate(sx, sy)
            femm.hi_clearselected()

        except Exception as e:
            msg = f"Failed to move group(s) {groups_to_move} in FEMM: {e}"
            logging.critical(msg)
            raise RuntimeError(msg) from {e}

    def _check_state(self) -> None:
        """
        Checks state if false reloads the femm simulation
        """
        if self.state:
            return None

        femm.openfemm()
        femm.opendocument(str(self.file_path))
        self.state = True

    def clean_up(self):
        """
        Manages the femm environment
        """
        femm.closefemm()
        self.state = False
