"""
Filename: motor_physics.py
Author: William Bowley
Version: 1.0
Date: 24 - 06 - 2025
Description:
    This script contains functions that are used to process inputs & outputs 
    of the FEMM Program
    
    Functions:
    - inverted_park_transform(currentFlux, currentForce, electricalAngle)   -> (alpha, beta)
    - inverted_clark_transform(alpha, beta)                                 -> {a,b,c}
    
    - motor_power(lineVoltage, lineCurrent, powerFactor)                    -> (power)
    - wye_motor(voltagePhase, voltageCurrent, powerFactor)                  -> (power)
    - delta_motor(voltagePhase, voltageCurrent, powerFactor)                -> (power)
"""

from math import *


""" Converts flux-force frame currents to stationary alpha-beta frame currents"""
def inverted_park_transform(
        currentFlux:       float, 
        currentForce:      float, 
        electricalAngle:   float
    ) -> tuple[float, float]:
    
    # Reference: 
    # https://en.wikipedia.org/wiki/Direct-quadrature-zero_transformation
    alpha   = currentFlux * cos(electricalAngle) - currentForce * sin(electricalAngle)
    beta    = currentFlux * sin(electricalAngle) + currentForce * cos(electricalAngle)
    
    return (alpha, beta)


""" Converts alpha-beta frame currents to 3 phase step currents"""
def inverted_clarke_transform(
        alpha:  float,
        beta:   float,
    ) -> tuple[float, float, float]:
    
    # Reference: 
    # https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_transformation
    a = alpha
    b = 1/2 * (sqrt(3)*beta - alpha)
    c = 1/2 * (-sqrt(3)*beta - alpha)
    
    return (a,b,c)


""" Calculates the power (watts) being used by the motor"""
def motor_rms_power(
        lineVoltage:    complex | float,
        lineCurrent:    complex | float,
        powerFactor:    float
    ) -> float:
    
    # Reference: 
    # https://www.electricaltechnology.org/2020/10/power-formulas-ac-dc.html
    power = sqrt(3)*abs(lineVoltage)*abs(lineCurrent)*powerFactor
    
    return power


""" Calculates the line voltages for a wye motor and returns rms power. Assumes power factor of 1"""
def wye_motor(
        voltagePhase: float,
        currentPhase: float,
        powerFactor:  float = 1
    ) -> float:
    
    # Reference: 
    # https://www.allaboutcircuits.com/textbook/alternating-current/chpt-10/three-phase-y-delta-configurations/
    lineVoltage = sqrt(3)*voltagePhase
    lineCurrent = currentPhase
    wyePower = motor_rms_power(lineVoltage, lineCurrent, powerFactor)
    
    return wyePower


""" Calculates the line voltages for a delta motor and returns power used. Assumes power factor of 1"""
def delta_motor(
        voltagePhase: float,
        currentPhase: float,
        powerFactor:  float = 1
    ) -> float:
    
    # Reference: 
    # https://www.allaboutcircuits.com/textbook/alternating-current/chpt-10/three-phase-y-delta-configurations/
    lineVoltage = voltagePhase
    lineCurrent = sqrt(3)*currentPhase
    deltaPower = motor_rms_power(lineVoltage, lineCurrent, powerFactor)
    
    return deltaPower


""" Calculates the synchronous frequency of the motor for a given speed (m/s)"""
def synchronous_frequency(
        targetSpeed: float,
        polePitch: float
    ) -> float:
    
    frequency = (targetSpeed) / (2*polePitch)
    
    return frequency


""" Calculates the applied current density (J : MA/m^2)"""
def applied_current_density(
    wireLength: float,
    wireHeight: float,
    appliedCurrent: float
    ) -> float:
    
    # J = Ampres / Area
    currentDensity = appliedCurrent / (wireLength * wireHeight)
    
    return currentDensity