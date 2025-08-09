"""
File: ripple.py
Author: William Bowley
Version: 1.2
Date: 2025-07-27
Description:
    General-purpose functions to calculate ripple metrics
    (peak-to-peak, RMS, percentage) from sequences of numeric values.

Functions:
- ripple_peak_to_peak(values):
    Returns the magitude of difference between minimum and maximum values

- ripple_rms(values):
    Returns the root mean square of the waveform

- ripple_percent(values):
    Returns the percent that the ripple takes of the whole waveform
"""

import logging

from math import sqrt
from typing import Sequence
from blueshark.configs import PRECISION, EPSILON


def _validate_values(values: Sequence[int | float]) -> None:
    """
    Helper function to validate the input sequence.
    """
    if not values:
        msg = "Input sequence 'values' must not be empty."
        logging.error(msg)
        raise ValueError(msg)

    for element in values:
        if not isinstance(element, (int, float)):
            msg = (
                f"All elements in the series must be int or float,"
                f"found '{type(element).__name__}'."
            )
            logging.error(msg)

            raise TypeError(msg)


def ripple_peak_to_peak(values: Sequence[int | float]) -> float:
    """
    Compute peak-to-peak ripple of a sequence of numeric values.

    Args:
        values (Sequence[int | float]): Input numeric values.

    Returns:
        float: Peak-to-peak ripple, rounded to configured precision.
    """

    _validate_values(values)

    average = sum(values) / len(values)
    ripple = [v - average for v in values]
    peak = max(ripple) - min(ripple)
    return round(peak, PRECISION)


def ripple_rms(values: Sequence[int | float]) -> float:
    """
    Compute RMS ripple of a sequence of numeric values.

    Args:
        values (Sequence[int | float]): Input numeric values.

    Returns:
        float: RMS ripple, rounded to configured precision.
    """

    _validate_values(values)

    average = sum(values) / len(values)
    ripple = [v - average for v in values]
    rms = sqrt(sum(r ** 2 for r in ripple) / len(ripple))
    return round(rms, PRECISION)


def ripple_percent(values: Sequence[int | float]) -> float:
    """
    Compute percentage ripple relative to average value.

    Args:
        values (Sequence[int | float]): Input numeric values.

    Returns:
        float: Percentage ripple (peak-to-peak / average * 100),
               rounded to configured precision.
    """

    _validate_values(values)

    average = sum(values) / len(values)
    if abs(average) < EPSILON:
        return 0.0

    peak_to_peak = ripple_peak_to_peak(values)
    return round((peak_to_peak / average) * 100, PRECISION)
