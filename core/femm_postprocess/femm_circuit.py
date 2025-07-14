"""
Filename: femm_circuit.py
Author: William Bowley
Version: 1.0
Date: 2025-07-01
Description:
    Circuit analysis utilities for FEMM post-processing.
"""

import femm

def circuitAnalysis(circuitName: str) -> tuple[float, float]:
    """
    Calculates the inductance and peak voltage in the specified circuit.
    
    Parameters:
        circuitName (str): The circuit property name in FEMM.
        
    Returns:
        peakVoltage (float): Peak voltage in the circuit.
        inductance (float): Inductance calculated as fluxLinkage / current.
    """
    
    circuitProps = femm.mo_getcircuitproperties(circuitName)
    current = circuitProps[0]
    peakVoltage = circuitProps[1]
    fluxLinkage = circuitProps[2]
    
    inductance = fluxLinkage / current if current != 0 else 0
    
    return (peakVoltage, inductance)
