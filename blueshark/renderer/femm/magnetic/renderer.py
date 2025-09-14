"""
File: renderer.py
Author: William Bowley
Version: 1.4
Date: 2025-09-14
Description:
    Renderer based on MagneticRenderer
    for FEMM magnetic simulations

    Defines the problem and the elements,
    circuits and boundaries.
"""

import logging
import femm

from pathlib import Path
from typing import Any, Optional
from math import cos, sin, degrees

from blueshark.renderer.renderer_interface import MagneticRenderer
from blueshark.domain.geometry.graphical_centroid import centroid_point
from blueshark.domain.constants import SETUP_CURRENT, DEFAULT_TOLERANCE
from blueshark.renderer.femm.magnetic.materials import femm_add_material
from blueshark.renderer.femm.magnetic.boundary import concentric_boundary
from blueshark.domain.definitions import (
    Units,
    Geometry,
    CoordinateSystem,
    CircuitType,
    CurrentPolarity,
    BoundaryType,
    Problem
)
from blueshark.renderer.femm.magnetic.properties import (
    set_element_properties,
    assign_element_id,
    add_circuit
)
from blueshark.renderer.femm.magnetic.primitives import (
    draw_primitive
)


class FEMMagneticRenderer(MagneticRenderer):
    """
    Magnetic renderer for FEMM:Magnetic
    """
    def __init__(self, file_path: Path) -> None:
        """
        Initializes the renderer
        under the file_path given by the user

        Args:
            file_path: path to renderer file
        """
        self.file_path = Path(file_path)
        self.materials: set[str] = set()
        self.circuits: set[str] = set()
        self.is_active = False

        # Magnetic problem
        self.problem = Problem()

    def setup(
        self,
        system: CoordinateSystem,
        units: Units,
        depth: float = 0,
        tolerance: float = DEFAULT_TOLERANCE,
        frequency: float = 0
    ) -> None:
        """
        Setup the rendering environment and simulation space

        Args:
            system: Coordinate System (enum)
            units: Measurement system used by the renderer
            depth: [Optional] Into the paper length (planar only)
            tolerance: [Optional] Precision value,
                        tells solver to stop iterating on the problem
            frequency: [Optional] Approach with Care this implementation isn't
                        designed for AC (Also: Femm, disables magnets in AC)
        """
        if depth < 0 or frequency < 0:
            raise ValueError("Depth and frequency must be non-negative")

        problem_type = None
        if system == CoordinateSystem.AXI_SYMMETRIC:
            problem_type = "axi"
            if depth != 0:
                msg = (
                    "Axial Symmetric simulations don't have depth, "
                    f"got {depth}; defaulting to depth = 0"
                )
                logging.warning(msg)
                depth = 0
        elif system == CoordinateSystem.PLANAR:
            problem_type = "planar"
        else:
            msg = f"{system} isn't supported by FEMMagneticRenderer"
            raise ValueError(msg)

        femm_units = None
        match units:
            case Units.MICROMETERS:
                femm_units = "micrometers"
            case Units.CENTIMETERS:
                femm_units = "centimeters"
            case Units.MILLIMETER:
                femm_units = "millimeters"
            case Units.METER:
                femm_units = "meters"

            case _:
                msg = f"Unit '{units}' is not supported by FEMM"
                raise NotImplementedError(msg)

        try:
            femm.openfemm(1)  # Opens FEMM in hidden window
            femm.newdocument(0)  # Magnetic simulation

            # Records the problem parameters for solver
            self.problem.frequency = frequency
            self.problem.units = femm_units
            self.problem.type = problem_type
            self.problem.depth = depth
            self.problem.tolerance = tolerance

            # Defines the problem within femm renderer
            femm.mi_probdef(
                frequency,
                femm_units,
                problem_type,
                tolerance,
                depth
            )

            self.is_active = True
            self.save_changes()

        except Exception as e:
            msg = (
                f"FEMMagneticRenderer failed to launch or define problem: {e}"
            )
            logging.critical(msg)
            raise RuntimeError(f"{self.__class__.__name__}: {msg}") from e

    def draw(
        self,
        shape: Geometry,
        material: dict[str, Any],
        element_id: int,
        element_tag: Optional[tuple[float, float]] = None,
        circuit: Optional[str] = None,
        polarity: CurrentPolarity = CurrentPolarity.FORWARD,
        turns: int = 1,
        magnetization: float = 0.0
    ) -> None:
        """
        Draws elements to the simulation space
        and sets properties

        Args:
            shape: Defines the shape within the framework (Geometry (Enum))
            material: Material from imported from static material manager
            element_id: element identifier for element
            element_tag: [Optional] (x, y) coordinates of element tag
            circuit: [Optional] Circuit that the element is apart of
            polarity: [Optional] Directionally of current through the element
            turns: [Optional] Number of turns of material within the element
            magnetization: [Optional] Directionally of the magnetic field
        """
        self._check_active()
        contours = draw_primitive(shape)

        # Assign element identifier to contours
        assign_element_id(
            contours,
            element_id
        )

        # adds material to simulation space
        name = self._add_material(material)

        if circuit is not None and circuit not in self.circuits:
            self.circuits.add(circuit)
            add_circuit(circuit, CircuitType.SERIES, SETUP_CURRENT)
            msg = (
                f"{circuit} was not defined before trying to assign. "
                f"Defaulting to {CircuitType.SERIES} and {SETUP_CURRENT} A"
            )
            logging.warning(msg)

        # Set polarity for the circuit
        if polarity == CurrentPolarity.FORWARD:
            turns = abs(turns)

        elif polarity == CurrentPolarity.REVERSE:
            turns = -abs(turns)

        # Finds the graphical centroid for the properties tag
        if element_tag is None:
            element_tag = centroid_point(shape)

        # sets element properties
        set_element_properties(
            element_tag,
            element_id,
            name,
            circuit,
            turns,
            magnetization
        )

        self.save_changes()

    def create_circuit(
        self,
        circuit: str,
        circuit_type: CircuitType,
        initial_current: float = SETUP_CURRENT
    ) -> None:
        """
        Adds a circuit in either series or parallel with an
        initial current in Amps

        Args:
            circuit: circuit name
            circuit_type: parallel or series (CircuitType: Enum)
                        (ref. domain/definitions.py)
            initial_current: initial current in the circuit in amps
        """
        self._check_active()
        self.circuits.add(circuit)
        add_circuit(
            circuit,
            circuit_type,
            initial_current
        )

        self.save_changes()

    def add_concentric_boundary(
        self,
        origin: tuple[float, float],
        radius: float,
        material: dict[str, Any],
        num_shells: Optional[int] = 7,
        boundary_type: Optional[BoundaryType] = BoundaryType.NEUMANN
    ) -> None:
        """
        Adds a concentric boundary with boundary type, material and
        num_shells

        Args:
            origin: Center coordinates (x, y) for the shells
            radius: Radius of the innermost shell (solution domain)
            material: Material to be assigned to the outer domain
            num_shells: Number of concentric shells to create (defaults=7)
            boundary_type: Type of boundary (Defaults=NEUMANN)
        """
        self._check_active()
        name = self._add_material(material)
        concentric_boundary(
            origin,
            radius,
            name,
            num_shells,
            boundary_type
        )

        self.save_changes()

    def change_circuit_current(
        self,
        circuit: str,
        current: float
    ) -> None:
        """
        Changes the magnitude of the current flow through
        a circuit

        Args:
            circuit: circuit name
            current: New current value in amps
        """
        if circuit not in self.circuits:
            msg = f"'{circuit}' hasn't been initiated within the renderer"
            raise RuntimeError(msg)

        femm.mi_setcurrent(circuit, current)

        self.save_changes()

    def move_element(
        self,
        element_id: int | list[int],
        magnitude: float,
        angles: tuple[float, float, float],
    ) -> None:
        """
        Moves one or more blocks (elements) by a vector (magnitude, angle).
        Works like the old implementation that moved individual blocks.

        args:
            element_id: ID(s) of element blocks
            magnitude: displacement magnitude
            angles: tuple(theta, 0, 0) in radians
        """
        self._check_active()

        if len(angles) != 3:
            raise ValueError(f"Expected 3D angle tuple, got {angles}")

        if angles[1] != 0 or angles[2] != 0:
            logging.warning("FEMM supports only planar angles (theta, 0, 0).")

        theta = angles[0]

        # Ensure we have a list
        if not isinstance(element_id, (list, tuple)):
            elements_to_move = [element_id]
        else:
            elements_to_move = element_id

        dx = magnitude * cos(theta)
        dy = magnitude * sin(theta)

        # Select each block individually and move
        for element in elements_to_move:
            femm.mi_selectgroup(element)
            femm.mi_movetranslate(dx, dy)
            femm.mi_clearselected()

        self.save_changes()

    def rotate_element(
        self,
        element_id: int | list[int],
        axis: tuple[float, float, float],
        angles: tuple[float, float, float],
    ) -> None:
        """
        Rotates a element or set of elements
        by angle (theta, 0, 0)

        Implementation Note:
        - Given that femm is planar or axial symmetric.
        - Axis should be (x, y, 0)
        - Angle should be (theta, 0, 0)

        args:
            element_id: element or elements identifiers
            axis: Axis to rotate around
            angles: Angle with respect to the horizontal (Radians)
        """
        self._check_active()
        if len(axis) != 3 or len(angles) != 3:
            msg = f"Expected 3D axis/angles tuples, got {axis}, {angles}"
            raise ValueError(msg)

        if angles[1] != 0 or angles[2] != 0:
            msg = "FEMM supports only planar angles (theta, 0, 0)."
            logging.warning(msg)

        x, y, _ = axis
        angle = angles[0]

        if not isinstance(element_id, (list, tuple)):
            elements_to_move = [element_id]
        else:
            elements_to_move = element_id

        for element in elements_to_move:
            femm.mi_selectgroup(element)

        femm.mi_moverotate(x, y, degrees(angle))
        femm.mi_clearselected()

        self.save_changes()

    def define_environment_region(
        self,
        element_id: int,
        element_tag: tuple[float, float],
        material: dict[str, Any],
    ) -> None:
        """
        Sets property of a undefined region such
        as internal gaps between parts

        e.g (air_gaps, non-meshed regions, etc)

        Args:
            element_id: element identifier for element
            element_tag: (x, y) coordinates of element tag
            material: Material from imported from static material manager

        NOTE:
            If requested automatic filling for the
            ambient environment can be implemented.
            This is already done in FEMMThermalRenderer
        """
        self._check_active()
        name = self._add_material(material)

        set_element_properties(
            element_tag,
            element_id,
            name
        )

        self.save_changes()

    def save_changes(self) -> None:
        """
        Manages the changes to the femm file
        """
        self._check_active()
        femm.mi_saveas(str(self.file_path.resolve()))

    def _add_material(
        self,
        material: dict[str, Any]
    ) -> str:
        """
        Adds a material to the renderer

        Args:
            material: Material from imported from static material manager
        """
        self._check_active()
        name = material.get("name", "Unknown")
        if name not in self.materials:
            self.materials.add(name)
            femm_add_material(
                material
            )

        return name

    def _check_active(self) -> None:
        """
        Checks if FEMM is active
        """
        if self.is_active:
            return
        try:
            femm.openfemm(1)
            femm.opendocument(str(self.file_path.resolve()))
            self.is_active = True

        except Exception as e:
            msg = (
                f"FEMMagneticRenderer failed to reactivate: {e}"
            )
            logging.critical(msg)
            raise RuntimeError(f"{self.__class__.__name__}: {msg}") from e

    def clean_up(self) -> None:
        """
        Manages the femm environment
        """
        try:
            if self.is_active:
                femm.closefemm()

        except Exception as e:
            logging.warning(f"FEMM cleanup failed: {e}")

        finally:
            self.is_active = False
