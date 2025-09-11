"""
File: renderer.py
Author: William Bowley
Version: 1.3
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

import math
import femm

from blueshark.renderer.femm.magnetic.boundary import add_bounds
from blueshark.renderer.femm.magnetic.primitives import (
    draw_polygon,
    draw_circle,
    draw_annulus_sector,
    draw_annulus_circle,
    draw_hybrid
)
from blueshark.domain.generation.geometric_centroid import (
    centroid_point
)
from blueshark.renderer.femm.magnetic.properties import (
    set_properties,
    add_phase,
    assign_group
)
from blueshark.renderer.femm.magnetic.materials import (
    load_materials,
    add_femm_material
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
    def __init__(self, file_path: Path) -> None:
        """
        Initializes the femm magnetic renderer
        under the file_path given by the user
        """
        self.file_path = Path(file_path)
        self.materials = load_materials()
        self.set_materials = []
        self.phases = []
        self.state = False

    def setup(
        self,
        sim_type: SimulationType,
        units: Units,
        depth: float = 0,
        frequency: float = 0,
    ) -> None:
        """
        Setup the rendering environment and simulation space
        """

        try:
            femm.openfemm(1)  # Opens femm in hiden window
            femm.newdocument(0)  # Magnetic simulation
            self.state = True
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
            msg = f"FEMM Magnetic Setup failed ({sim_type}): {e}"
            logging.critical(msg)
            raise RuntimeError(f"{self.__class__.__name__}: {msg}") from e

    def import_geometry(
        self,
        dxf: Path,
    ) -> None:
        """
        Import geometry through a dxf file
        """
        self._check_state()
        try:
            femm.mi_readdxf(str(dxf))
            femm.mi_saveas(str(self.file_path))
        except Exception as e:
            msg = f"FEMM Magnetic dxf import failed: {e}"
            logging.warning(msg)

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
        and other properties
        """

        self._check_state()
        shape = geometry.get("shape")
        match shape:
            case ShapeType.POLYGON | ShapeType.RECTANGLE:
                contours = draw_polygon(
                    geometry["points"],
                    geometry["enclosed"]
                )

            case ShapeType.CIRCLE:
                contours = draw_circle(
                    geometry["radius"],
                    geometry["center"]
                )

            case ShapeType.ANNULUS_SECTOR:
                contours = draw_annulus_sector(
                    geometry["center"],
                    geometry["radius_outer"],
                    geometry["radius_inner"],
                    geometry["start_angle"],
                    geometry["end_angle"]
                )

            case ShapeType.ANNULUS_CIRCLE:
                contours = draw_annulus_circle(
                    geometry["center"],
                    geometry["radius_outer"],
                    geometry["radius_inner"]
                )

            case ShapeType.HYBRID:
                if "edges" not in geometry:
                    raise ValueError("Hybrid shape requires 'edges' field")
                contours = draw_hybrid(geometry["edges"])

            case _:
                raise NotImplementedError(f"Shape '{shape}' not supported")

        # Assigns the group to the contours
        assign_group(
            contours,
            group_id
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
            add_phase(phase, 1)

        # Adds blocklabel and sets properties of it
        if tag_coords is None:
            tag_coords = centroid_point(geometry)

        # Sets blocklabel properties
        set_properties(
            tag_coords,
            group_id,
            material,
            phase,
            turns,
            magnetization
        )

        # Saves changes to femm file
        femm.mi_saveas(str(self.file_path))

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

        self._check_state()
        if material not in self.set_materials:
            self.set_materials.append(material)
            add_femm_material(
                self.materials,
                material
            )

        # adds material to simulation space
        add_femm_material(
            self.materials,
            material
        )

        add_bounds(
            origin,
            radius,
            num_shells,
            bound_type,
            material
        )

        # Saves changes to femm file
        femm.mi_saveas(str(self.file_path))

    def set_property(
        self,
        origin: tuple[float, float],
        group_id: int,
        material: str = "Air"
    ) -> None:
        """
        Sets property of a undefined region such
        as the gap between the stator and armuture
        """

        self._check_state()
        if material not in self.set_materials:
            self.set_materials.append(material)
            add_femm_material(
                self.materials,
                material
            )

        set_properties(origin, group_id, material)

        # Saves changes to femm file
        femm.mi_saveas(str(self.file_path))

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
                femm.mi_selectgroup(group)

            step, angle = delta
            sx = step * math.cos(angle)
            sy = step * math.sin(angle)

            femm.mi_movetranslate(sx, sy)
            femm.mi_clearselected()

        except Exception as e:
            msg = f"Failed to move group(s) {groups_to_move} in FEMM: {e}"
            logging.critical(msg)
            raise RuntimeError(msg) from {e}

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
            femm.mi_selectgroup(group)

        femm.mi_moverotate(x, y, angle)
        femm.mi_clearselected()

        # Saves changes to femm file
        femm.mi_saveas(str(self.file_path))

    def change_phase_current(
        self,
        phase: str,
        current: float
    ) -> None:
        self._check_state()
        if phase is not None and phase not in self.phases:
            print("updating coils")
            self.phases.append(phase)
            add_phase(phase, current)

        femm.mi_setcurrent(phase, float(current))

        # Saves changes to femm file
        femm.mi_saveas(str(self.file_path))

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
