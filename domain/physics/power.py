"""
Filename: power.py
Author: William Bowley
Version: 1.0
Date: 2025-06-10
Description:
    Functions to calculate motor power for different winding configurations.
    
Functions:
- motor_rms_power(lineVoltage, lineCurrent, powerFactor)      -> float
- wye_motor(voltagePhase, currentPhase, powerFactor)          -> float
- delta_motor(voltagePhase, currentPhase, powerFactor)        -> float
"""

from math import sqrt

def motor_rms_power(
        lineVoltage: complex | float,
        lineCurrent: complex | float,
        powerFactor: float
    ) -> float:
    
    """ Calculates the power (watts) being used by the motor """
    
    power = sqrt(3) * abs(lineVoltage) * abs(lineCurrent) * powerFactor
    return power


def wye_motor(
        voltagePhase: float,
        currentPhase: float,
        powerFactor:  float = 1
    ) -> float:
    
    """ Calculates the line voltage and power for a wye motor """
    
    lineVoltage = sqrt(3) / sqrt(2) * voltagePhase
    lineCurrent = currentPhase
    return motor_rms_power(lineVoltage, lineCurrent, powerFactor)


def delta_motor(
        voltagePhase: float,
        currentPhase: float,
        powerFactor:  float = 1
    ) -> float:
    
    """ Calculates the line voltage and power for a delta motor """
    
    lineVoltage = voltagePhase
    lineCurrent = sqrt(3) / sqrt(2) * currentPhase
    return motor_rms_power(lineVoltage, lineCurrent, powerFactor)
