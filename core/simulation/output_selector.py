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
from core.femm_postprocess import femm_circuit

class OutputSelector:
    def __init__(self, requestedOutputs):
        
        self.availableOutputs = {
            "lorentz_force": femm_force.lorentz_force,
            "force_via_stress_tensor": femm_force.weighted_stress_tensor_force,
            "circuit_analysis": femm_circuit.circuitAnalysis,
        }
        
        invalid = set(requestedOutputs) - set(self.availableOutputs)
        if invalid:
            raise ValueError(f"Unknown outputs requested: {invalid}")
        
        self.outputs = requestedOutputs

    def compute(self, stepContext) -> dict:
        results = {}
        for outputName in self.outputs:
            func = self.availableOutputs[outputName]

            if outputName == "circuit_analysis":
                circuitNames = stepContext.get("circuitName")
                if circuitNames is None:
                    raise ValueError("stepContext missing required 'circuitName' for circuit_analysis")

                if isinstance(circuitNames, (list, tuple)):
                    results[outputName] = [func(name) for name in circuitNames]
                else:
                    results[outputName] = func(circuitNames)

            else:
                groups = stepContext.get("group")
                if groups is None:
                    raise ValueError(f"stepContext missing required 'group' for {outputName}")

                if isinstance(groups, (list, tuple)):
                    results[outputName] = [func(group) for group in groups]
                else:
                    results[outputName] = func(groups)

        return results
