"""
File: tubular_motor.py
Author: William Bowley
Version: 1.1
Date: 2025-07-19

Description:
    Base model of a tubular linear motor for use in the motor simulation framework.

    This class implements the MotorBase interface and provides core
    functionality such as:
    - Geometry setup from YAML config
    - FEMM-compatible drawing
    - Stepping through linear positions
    - Applying 3-phase currents

    Adapted and extended from the "DIY-Linear-Motor" project by cmore839:
    https://github.com/cmore839/DIY-Linear-Motor

    FEMM simulation structure partially based on contributions by JuPrgn.
"""

import os
import yaml
import femm

from configs import constants
from motors.motor_interface import MotorBase
from femm_utils.preprocess import draw, geometry, boundary
from domain.generation.turns import number_turns


class TubularMotor(MotorBase):
    def __init__(self, config_file: str) -> None:
        """
        Initialize motor from a YAML configuration file path.

        Args:
            config_file (str): Path to the YAML config file.
        """
        try:
            self._unpack(config_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
        except yaml.YAMLError as e:
            raise RuntimeError(f"Error parsing YAML config file: {e}")
        except KeyError as e:
            raise RuntimeError(f"Missing required config key: {e}")

        # Ensure output folder exists
        os.makedirs(self.folder_path, exist_ok=True)

        # FEMM groups
        self.group_boundary = 0
        self.group_slot = 1
        self.group_pole = 2

        # Motor phase and slot configuration
        self.phases = ['pa', 'pb', 'pc']

    def generate(self) -> None:
        """Generate the motor geometry and setup in FEMM."""
        try:
            femm.openfemm(1)
            femm.newdocument(0)
            femm.mi_probdef(0, "millimeters", "axi", 1e-8)

            # Add phase circuits
            for phase in self.phases:
                femm.mi_addcircprop(phase, 0, 1)

            # Add materials
            femm.mi_getmaterial(self.pole_material)
            femm.mi_getmaterial(str(self.slot_material) + "mm")
            femm.mi_getmaterial("Air")

            # Add motor parts
            self._compute_geometry()
            self._add_armature()
            self._add_stator()
            self._add_boundary()

            femm.mi_saveas(os.path.join(self.folder_path, self.file_name + ".fem"))
            femm.closefemm()
        except Exception as e:
            raise RuntimeError(f"FEMM simulation setup failed: {e}")

    def set_currents(self, currents: tuple[float, float, float]) -> None:
        """Set 3-phase currents for the simulation step."""
        try:
            for phase, current in zip(self.phases, currents):
                femm.mi_setcurrent(phase, float(current))
        except Exception as e:
            raise RuntimeError(f"Failed to set currents in FEMM: {e}")

    def step(self, step: float) -> None:
        """Move the motor by a specified linear step."""
        try:
            femm.mi_selectgroup(self.movingGroup)
            femm.mi_movetranslate(0, step)
            femm.mi_clearselected()
        except Exception as e:
            raise RuntimeError(f"Failed to move motor in FEMM: {e}")

    @property
    def path(self) -> str:
        """Path for files under the motor."""
        return os.path.join(self.folder_path, self.file_name)

    @property
    def movingGroup(self) -> int:
        """Group identifier for the moving part of the motor in FEMM."""
        return self.group_slot

    @property
    def motorCircumference(self) -> float:
        """Circumference of the motor (used for torque or positioning)."""
        return self.pole_height * self.num_poles

    @property
    def numberPoles(self) -> int:
        """Number of magnetic poles in the motor."""
        return self.num_poles

    @property
    def numberSlots(self) -> int:
        """Number of coil slots in the stator or moving part."""
        return self.number_slots

    @property
    def peakCurrents(self) -> tuple[float, float]:
        """Peak current values as (flux_current_peak, force_current_peak)."""
        return self.i_flux_peak, self.i_force_peak

    def _add_armature(self) -> None:
        """Adds the armature to the simulation space."""
        for slot_index in range(len(self.slot_origins)):
            slot_phase = self.phases[slot_index % len(self.phases)]

            # Alternate turns positive and negative by slot index parity
            if slot_index % 2 == 0:
                turns = self.number_turns
            else:
                turns = -self.number_turns

            draw.draw_and_set_properties(
                origin=self.slot_origins[slot_index],
                length=self.slot_radius,
                height=self.slot_height,
                material=(str(self.slot_material) + "mm"),
                direction=0,
                incircuit=slot_phase,
                group=self.group_slot,
                turns=turns
            )

    def _add_stator(self) -> None:
        """Adds the stator to the simulation space."""
        total_num_poles = int((4 * constants.PAIRAPPOX) + self.num_poles)

        for pole in range(total_num_poles):
            pole_magnetization = 90 if pole % 2 == 0 else -90

            draw.draw_and_set_properties(
                origin=self.pole_origins[pole],
                length=self.pole_radius,
                height=self.pole_height,
                group=self.group_pole,
                direction=pole_magnetization,
                incircuit="<none>",
                material=self.pole_material,
                turns=0,
            )

    def _add_boundary(self) -> None:
        """Adds the Neumann outer edge boundary to the simulation space."""
        boundary_origin = (0, self.pole_height*self.num_poles*1/2)
        radius = (self.num_poles + 2*constants.PAIRAPPOX + 1) * self.pole_pitch
        boundary.add_bounds(origin=boundary_origin, radius=radius)

    def _compute_geometry(self) -> None:
        """Computes turns, pitches, and origins for the motor geometry."""
        self.number_turns = number_turns(
            length=self.slot_radius,
            height=self.slot_height,
            wire_diameter=self.slot_material,
            waste_factor=self.waste_factor
        )

        self.slot_pitch = self.slot_height + self.slot_spacing
        
        # Scales magnet length to make sure that the ratio of pairs to slot matches
        motor_length = self.slot_pitch*self.numberSlots
        self.pole_height = motor_length / self.numberPoles
        
        self.pole_pitch  = self.pole_height

        self.slot_origins = geometry.origin_points(
            object_num=self.number_slots,
            x_pitch=0,
            y_pitch=self.slot_pitch,
            x_offset=self.pole_radius + self.magnetic_gap,
        )

        self.pole_origins = geometry.origin_points(
            object_num=int((4 * constants.PAIRAPPOX) + self.num_poles),
            x_pitch=0,
            y_pitch=self.pole_pitch,
            y_offset=-2 * (constants.PAIRAPPOX * self.pole_pitch),
        )

    def _unpack(self, config_file: str) -> None:
        """Internal method to load motor parameters from YAML config file."""
        with open(config_file, "r") as file:
            params = yaml.safe_load(file)

        model = params.get("model", {})
        self.number_slots = model["numSlots"]
        self.num_poles = model["numPoles"]
        self.i_force_peak = model["iForcePeak"]
        self.i_flux_peak = model["iFluxPeak"]
        self.waste_factor = model["wasteFactor"]

        slot = params.get("slot", {})
        self.slot_radius = slot["radius"]
        self.slot_height = slot["height"]
        self.slot_spacing = slot["spacing"]
        self.slot_material = slot["material"]
        self.magnetic_gap = slot["magneticGap"]

        pole = params.get("pole", {})
        self.pole_radius = pole["radius"]
        self.pole_height = pole["height"]
        self.pole_material = pole["material"]

        output = params.get("output", {})
        self.folder_path = output.get("folder_path", "data/tubular")
        self.file_name = output.get("file_name", "tubular")
