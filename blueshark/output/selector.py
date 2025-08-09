"""
Filename: output_selector.py
Author: William Bowley
Version: 1.2
Date: 2025-07-29

Description:
    OutputSelector dynamically selects and executes FEMM post-processing
    output functions based on user requests.

    Supported outputs:
    - force_lorentz
    - torque_lorentz
    - force_via_stress_tensor
    - torque_via_stress_tensor
    - phase_power
    - phase_voltage
    - phase_current
    - phase_inductance
    - phase_flux_linkage
"""

import logging

from typing import Any, Callable, Union
from blueshark.femm_utils.postprocesses import forces as force
from blueshark.femm_utils.postprocesses import circuits as phases
from blueshark.femm_utils.postprocesses import torques


class OutputSelector:
    """
    Outputselector dymically selects and executes FEMM post-processing
    output functions.
    """
    def __init__(self, requested_outputs: list[str]) -> None:
        """
        Initialize the OutputSelector with requested output names.

        Args:
            requested_outputs (list): Output names to compute.
                Must be a subset of available outputs.

        Raises:
            ValueError: If unknown outputs are requested.
        """
        self.available_outputs = {
            "force_lorentz": (force.lorentz, self._run_group),
            "torque_lorentz": (torques.lorentz, self._run_group),
            "force_stress_tensor": (force.weighted_stress_tensor,
                                    self._run_group),
            "torque_stress_tensor": (torques.weighted_stress_tensor,
                                     self._run_group),
            "phase_power": (phases.phase_power, self._run_phase),
            "phase_voltage": (phases.phase_voltage, self._run_phase),
            "phase_current": (phases.phase_current, self._run_phase),
            "phase_inductance": (phases.phase_inductance, self._run_phase),
            "phase_flux_linkage": (phases.phase_flux_linkage, self._run_phase),
        }

        unknown = set(requested_outputs) - set(self.available_outputs)
        if unknown:
            msg = (
                f"Unknown outputs requested: {unknown}. "
                f"Available: {list(self.available_outputs)}"
            )
            logging.critical(msg)
            raise ValueError(msg)

        self.outputs = requested_outputs

    def compute(self, subjects: dict) -> dict[str, Any]:
        """
        Compute all requested outputs using provided subjects.

        Args:
            subjects (dict): Should contain 'group' or 'phaseName' keys.

        Returns:
            dict: Output names mapped to results.
        """
        results = {}
        for name in self.outputs:
            func, runner = self.available_outputs[name]
            results[name] = runner(func, subjects)
        return results

    def _run_group(
        self,
        function: Callable[[int], Any],
        subjects: dict
    ) -> Union[Any, list[Any]]:
        """
        Apply a group-based output function.

        Args:
            function (callable): Expects a group ID.
            subjects (dict): Must include 'group'.

        Returns:
            Result or list of results.
        """
        groups = subjects.get("group")
        if groups is None:
            msg = f"Missing 'group' key; keys={list(subjects.keys())}"
            logging.critical(msg)
            raise ValueError(msg)

        if isinstance(groups, (list, tuple)):
            return [function(group) for group in groups]

        return function(groups)

    def _run_phase(
        self,
        function: Callable[[str], Any],
        subjects: dict
    ) -> Union[Any, list[Any]]:
        """
        Apply a phase-based output function.

        Args:
            function (callable): Expects a phase name.
            subjects (dict): Must include 'phaseName'.

        Returns:
            Result or list of results.
        """
        names = subjects.get("phaseName")
        if names is None:
            msg = f"Missing 'phaseName' key; keys={list(subjects.keys())}"
            logging.critical(msg)
            raise ValueError(msg)

        if isinstance(names, (list, tuple)):
            return [function(name) for name in names]

        return function(names)
