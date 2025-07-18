"""
File: transforms.py
Author: William Bowley
Version: 1.1
Date: 2025-06-10
Description:
    Coordinate transformation functions for motor reference frames.

Functions:
- inverse_park_transform(d_current, q_current, elec_angle) -> (alpha, beta)
- inverse_clarke_transform(alpha, beta) -> (phase_a, phase_b, phase_c)
"""

from math import cos, sin, sqrt
from blueshark.configs import constants


def inverse_park_transform(
    d_current: float,
    q_current: float,
    elec_angle: float
) -> tuple[float, float]:
    """
    Convert d-q frame currents to stationary alpha-beta frame currents.
    Applicable for 3-phase motors only.

    Args:
        d_current (float): Current in the d-axis (flux axis).
        q_current (float): Current in the q-axis (torque axis).
        elec_angle (float): Electrical angle in radians.

    Returns:
        tuple[float, float]: Currents in alpha and beta stationary reference frame,
                             rounded to configured PRECISION.
    """
    alpha = d_current * cos(elec_angle) - q_current * sin(elec_angle)
    beta = d_current * sin(elec_angle) + q_current * cos(elec_angle)
    return round(alpha, constants.PRECISION), round(beta, constants.PRECISION)


def inverse_clarke_transform(
    alpha: float,
    beta: float
) -> tuple[float, float, float]:
    """
    Convert stationary alpha-beta frame currents to three-phase currents.
    Applicable for 3-phase motors only.

    Args:
        alpha (float): Alpha axis current.
        beta (float): Beta axis current.

    Returns:
        tuple[float, float, float]: Three-phase currents (a, b, c),
                                   rounded to configured PRECISION.
    """
    phase_a = round(alpha, constants.PRECISION)
    phase_b = round(0.5 * (sqrt(3) * beta - alpha), constants.PRECISION)
    phase_c = round(0.5 * (-sqrt(3) * beta - alpha), constants.PRECISION)
    return phase_a, phase_b, phase_c
