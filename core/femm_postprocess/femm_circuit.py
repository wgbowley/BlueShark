"""
Filename: femm_circuit.py
Author: William Bowley
Version: 1.0
Date: 2025-07-01
Description:
    Circuit analysis utilities for FEMM post-processing.
"""

import femm

# Modules
import configs.constants as constants 
import domain.physics.power as power 

def circuit_voltage(circuitName: str) -> float:
    
    """ Gets the voltage drop across the circuit """
    circuitProps = femm.mo_getcircuitproperties(circuitName)
    voltage = circuitProps[1]
    
    return voltage


def circuit_current(circuitName: str) -> float: 
    
    """ Gets the instanteous current across the circuit """
    circuitProps = femm.mo_getcircuitproperties(circuitName)
    current = circuitProps[0]
    
    return current 


def circuit_inductance(circuitName: str) -> float:
    
    """ Gets circuit properties and calculates the inductance of the circuit"""
    circuitProps = femm.mo_getcircuitproperties(circuitName)
    
    current = circuitProps[0]
    fluxLinkage = circuitProps[2]

    if abs(current) > constants.epsilon:
        inductance = fluxLinkage / current 
    else: 
        inductance = 0 
    
    return inductance


def circuit_flux_linkage(circuitName: str) -> float:
    
    """ Gets the flux linkage between the circuit and simulation elements"""
    circuitProps = femm.mo_getcircuitproperties(circuitName)
    fluxLinkage = circuitProps[2]
    return fluxLinkage


def circuit_power(circuitName: str) -> float:
    
    """ Gets the instantaneous power across the circuit"""
    circuitProps = femm.mo_getcircuitproperties(circuitName)
    
    current = circuitProps[0]
    voltage = circuitProps[1]
    
    power = current * voltage
    
    return power    