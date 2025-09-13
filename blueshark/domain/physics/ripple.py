"""
File: ripple.py
Author: William Bowley
Version: 1.2
Date: 2025-07-27

Description:
    General-purpose functions to calculate ripple metrics
    (peak-to-peak, RMS, percentage) from sequences of numeric values.
"""

import logging
from math import sqrt
from typing import Sequence
from blueshark.domain.constants import PRECISION, EPSILON


def _validate_values(values: Sequence[int | float]) -> None:
    """
    Validate the input sequence of numeric values.

    Args:
        values (Sequence[int | float]): Sequence of values to validate.
    """
    if not values:
        msg = "Input sequence 'values' must not be empty."
        logging.error(msg)
        raise ValueError(msg)

    for element in values:
        if not isinstance(element, (int, float)):
            msg = (
                f"All elements in the sequence must be int or float, "
                f"found '{type(element).__name__}'."
            )
            logging.warning(msg)
            raise TypeError(msg)


def ripple_peak_to_peak(values: Sequence[int | float]) -> float:
    """
    Compute the peak-to-peak ripple of a numeric sequence.

    Args:
        values (Sequence[int | float]): Input numeric values.

    Returns:
        float: Peak-to-peak ripple, rounded to configured precision.
    """
    _validate_values(values)

    mean_value = sum(values) / len(values)
    ripple = [v - mean_value for v in values]
    peak_to_peak = max(ripple) - min(ripple)
    return round(peak_to_peak, PRECISION)


def ripple_rms(values: Sequence[int | float]) -> float:
    """
    Compute the RMS (root-mean-square) ripple of a numeric sequence.

    Args:
        values (Sequence[int | float]): Input numeric values.

    Returns:
        float: RMS ripple, rounded to configured precision.
    """
    _validate_values(values)

    mean_value = sum(values) / len(values)
    ripple = [v - mean_value for v in values]
    rms = sqrt(sum(r ** 2 for r in ripple) / len(ripple))
    return round(rms, PRECISION)


def ripple_percent(values: Sequence[int | float]) -> float:
    """
    Compute the peak-to-peak ripple as a percentage of the mean value.

    Args:
        values (Sequence[int | float]): Input numeric values.

    Returns:
        float: Percentage ripple (peak-to-peak / mean * 100),
               rounded to configured precision.
    """
    _validate_values(values)

    mean_value = sum(values) / len(values)
    if abs(mean_value) < EPSILON:
        return 0.0

    peak_to_peak = ripple_peak_to_peak(values)
    return round((peak_to_peak / mean_value) * 100, PRECISION)
