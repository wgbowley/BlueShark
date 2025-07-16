"""
Filename: output_selector.py
Author: William Bowley
Version: 1.0
Date: 2025-07-14
Description:
    OutputSelector class manages dynamic selection and execution of FEMM post-processing
    output functions based on user requests.
"""

from core.femm_postprocess import femm_force
from core.femm_postprocess import femm_torque
from core.femm_postprocess import femm_circuit

class OutputSelector:
    def __init__(self, requestedOutputs):
        self.availableOutputs = {
            "lorentz_force": (femm_force.lorentz_force, self._run_group),
            "lorentz_torque": (femm_torque.lorentz_torque, self._run_group),
            "force_via_stress_tensor": (femm_force.weighted_stress_tensor_force, self._run_group),
            "torque_via_stress_tensor": (femm_torque.weighted_stress_tensor_torque, self._run_group),
            "circuit_power": (femm_circuit.circuit_power, self._run_circuit),
            "circuit_voltage": (femm_circuit.circuit_voltage, self._run_circuit),
            "circuit_current": (femm_circuit.circuit_current, self._run_circuit),
            "circuit_inductance": (femm_circuit.circuit_inductance, self._run_circuit),
            "circuit_flux_linkage": (femm_circuit.circuit_flux_linkage, self._run_circuit)
        }

        unknown = set(requestedOutputs) - set(self.availableOutputs)
        if unknown:
            raise ValueError(f"Unknown outputs requested: {unknown}")

        self.outputs = requestedOutputs


    def compute(self, subjects) -> dict:
        results = {}
        for outputName in self.outputs:
            func, runner = self.availableOutputs[outputName]
            results[outputName] = runner(func, subjects)
        return results


    def _run_group(self, func, subjects):
        groups = subjects.get("group")

        if groups is None:
            raise ValueError("Missing 'group' in subjects for group-based output")

        if isinstance(groups, (list, tuple)):
            results = []
            for group in groups:
                results.append(func(group))
            return results

        return func(groups)


    def _run_circuit(self, func, subjects):
        circuitNames = subjects.get("circuitName")

        if circuitNames is None:
            raise ValueError("Missing 'circuitName' in subjects for circuit-based output")

        if isinstance(circuitNames, (list, tuple)):
            results = []
            for name in circuitNames:
                results.append(func(name))
            return results

        return func(circuitNames)



