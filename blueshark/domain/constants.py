"""
Filename: constants.py
Author: William Bowley
Version: 1.3
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

EPSILON: float = 1e-10
# Minimum threshold to treat floating-point values as effectively zero.
# Prevents division-by-zero errors or instability due to numerical noise.


MAXIMUM_FAILS: int = 5
# Maximum allowed consecutive simulation failures (e.g., FEMM not converging)
# before aborting a run or skipping a parameter set.

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
    HYBRID = auto()


class Connectors(str, Enum):
    """
    Types of connectors for hybird shapes
    """
    LINE = "line"
    ARC = "arc"


class Connection(TypedDict, total=False):
    """
    Describes an connection in a hybrid geometry
    """
    type: Connectors
    start: Tuple[float, float]             # Start point for line/arc
    end: Tuple[float, float]               # End point for line/arc
    center: Optional[Tuple[float, float]]  # Center for arcs/circle
    angle: Optional[float]                 # Sweep angle for arcs
    radius: Optional[float]                # Radius for circle/arc


class Geometry(TypedDict, total=False):
    """
    Describes the geometry of an element.
    Uses the units selected by the user.
    Fields are optional depending on shape.
    """
    shape: ShapeType
    points: List[Tuple[float, float]]               # For POLYGON/RECTANGLE
    radius: Optional[float]                         # For CIRCLE
    radius_inner: Optional[float]                   # For arcs with thickness
    radius_outer: Optional[float]                   # For arcs with thickness
    center: Optional[Tuple[float, float]]           # Center point
    start_angle: Optional[float]                    # Degrees, for arcs
    end_angle: Optional[float]                      # Degrees, for arcs
    enclosed: bool                                  # Enclosed [true] / [false]
    edges: Optional[List[Connection]]               # <-- for HYBRID


class CurrentPolarity(Enum):
    """
    Describes how current passes through a element.
    """
    FORWARD = auto()
    REVERSE = auto()
