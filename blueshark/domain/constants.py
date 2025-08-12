"""
Filename: constants.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28

Description:
    This file defines enums, fixed values and
    general constants within the simulator. These
    are indepedent of specific solver implementations
"""

from typing import TypedDict, List, Tuple, Optional
from enum import Enum, auto
from math import pi

PRECISION: int = 12
# Default number of decimal places for rounding or formatting output.

TWOPI = 2*pi


class SimulationType(Enum):
    """
    Types of simulation spaces
    - axi-symmetric
    - Planar (2D)
    """
    AXI_SYMMETRIC = auto()
    PLANAR = auto()


class Units(Enum):
    """
    All units supported by the simulator
    """
    MIRCOMETERS = "micrometers"
    CENTIMETERS = "centimeters"
    MILLIMETER = "millimeters"
    METER = "meters"
    INCH = "inches"
    MILS = "mils"


class ShapeType(Enum):
    """
    Possible shapes within the simulator
    """
    POLYGON = auto()
    RECTANGLE = auto()
    CIRCLE = auto()
    ANNULUS_SECTOR = auto()
    ANNULUS_CIRCLE = auto()


class Geometry(TypedDict, total=False):
    """
    Describes the geometry of an element.
    Uses the units selected by the user.
    Fields are optional depending on shape.
    """
    shape: ShapeType
    points: List[Tuple[float, float]]
    radius: Optional[float]                # For circles
    radius_inner: Optional[float]          # For arcs with thickness
    radius_outer: Optional[float]          # For arcs with thickness
    center: Optional[Tuple[float, float]]  # Center point for arcs/circles
    start_angle: Optional[float]           # Degrees, for arcs
    end_angle: Optional[float]             # Degrees, for arcs


class CurrentPolarity(Enum):
    """
    Describes how current passes through a element.
    """
    FORWARD = auto()
    REVERSE = auto()
