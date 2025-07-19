"""
Filename: output_selector.py
Author: William Bowley
Version: 1.0
Date: 2025-07-14

Description:
    OutputSelector class manages dynamic selection and execution of FEMM post-processing
    output functions based on user requests.
"""

from femm_utils.postprocess import force
from femm_utils.postprocess import torque
from femm_utils.postprocess import circuits as phases


class OutputSelector:
    def __init__(self, requested_outputs):
        """
        Initialize the OutputSelector with requested output types.

        Args:
            requested_outputs (list[str]): List of output names to compute.
                Must be a subset of available outputs; unknown outputs raise ValueError.
        """
        self.available_outputs = {
            "force_lorentz": (force.lorentz, self._run_group),
            "torque_lorentz": (torque.lorentz, self._run_group),
            "force_via_stress_tensor": (force.weighted_stress_tensor, self._run_group),
            "torque_via_stress_tensor": (torque.weighted_stress_tensor, self._run_group),
            "phase_power": (phases.phase_power, self._run_phase),
            "phase_voltage": (phases.phase_voltage, self._run_phase),
            "phase_current": (phases.phase_current, self._run_phase),
            "phase_inductance": (phases.phase_inductance, self._run_phase),
            "phase_flux_linkage": (phases.phase_flux_linkage, self._run_phase),
        }

        unknown = set(requested_outputs) - set(self.available_outputs)
        if unknown:
            raise ValueError(f"Unknown outputs requested: {unknown}")

        self.outputs = requested_outputs

    def compute(self, subjects) -> dict:
        """
        Compute all requested outputs based on given subjects.

        Args:
            subjects (dict): Context dictionary that must include either:
                - 'group' (int or list[int]) for group-based FEMM elements, or
                - 'phaseName' (str or list[str]) for phase-based FEMM elements.

        Returns:
            dict: Mapping of output names to computed results.
        """
        results = {}
        for output_name in self.outputs:
            function, runner = self.available_outputs[output_name]
            results[output_name] = runner(function, subjects)
        return results

    def _run_group(self, function, subjects):
        """
        Run a group-based output function on one or more FEMM groups.

        Args:
            function (callable): Function to compute output from a group ID.
            subjects (dict): Must contain 'group' key with int or list[int].

        Returns:
            Computed result or list of results for each group.
        """
        groups = subjects.get("group")
        if groups is None:
            raise ValueError("Missing 'group' in subjects for group-based output")

        if isinstance(groups, (list, tuple)):
            return [function(group) for group in groups]

        return function(groups)

    def _run_phase(self, function, subjects):
        """
        Run a phase-based output function on one or more FEMM phase names.

        Args:
            function (callable): Function to compute output from a phase name.
            subjects (dict): Must contain 'phaseName' key with str or list[str].

        Returns:
            Computed result or list of results for each phase name.
        """
        phase_names = subjects.get("phaseName")
        if phase_names is None:
            raise ValueError("Missing 'phaseName' in subjects for phase-based output")

        if isinstance(phase_names, (list, tuple)):
            return [function(name) for name in phase_names]

        return function(phase_names)
