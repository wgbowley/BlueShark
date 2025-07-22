"""
File: ripple.py
Author: William Bowley
Version: 1.1
Date: 2025-07-22
Description:
    General-purpose functions to calculate ripple metrics (peak-to-peak, RMS, percentage)
    from a list of numeric values.
"""

from math import sqrt
from typing import Sequence
from configs import constants


def ripple_peak_to_peak(values: Sequence[float]) -> float:
    """
    Compute peak-to-peak ripple of a sequence of numeric values.

    Args:
        values (Sequence[float]): Input numeric values.

    Returns:
        float: Peak-to-peak ripple, rounded to configured precision.
    """
    if not values:
        return 0.0

    average = sum(values) / len(values)
    ripple = [v - average for v in values]
    return round(max(ripple) - min(ripple), constants.PRECISION)


def ripple_rms(values: Sequence[float]) -> float:
    """
    Compute RMS ripple of a sequence of numeric values.

    Args:
        values (Sequence[float]): Input numeric values.

    Returns:
        float: RMS ripple, rounded to configured precision.
    """
    if not values:
        return 0.0

    average = sum(values) / len(values)
    ripple = [v - average for v in values]
    rms = sqrt(sum(r ** 2 for r in ripple) / len(ripple))
    return round(rms, constants.PRECISION)


def ripple_percent(values: Sequence[float]) -> float:
    """
    Compute percentage ripple relative to average value.

    Args:
        values (Sequence[float]): Input numeric values.

    Returns:
        float: Percentage ripple (peak-to-peak / average * 100),
               rounded to configured precision.
    """
    if not values:
        return 0.0

    average = sum(values) / len(values)
    if average == 0:
        return 0.0

    peak_to_peak = ripple_peak_to_peak(values)
    return round((peak_to_peak / average) * 100, constants.PRECISION)
