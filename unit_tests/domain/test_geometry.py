"""
File: test_geometry.py
Author: William Bowley
Version: 1.4
Date: 2025-09-13

Description:
    Tests functions within domain/geometry
"""

import unittest

from math import sqrt
from blueshark.domain.constants import PRECISION, PI
from blueshark.domain.geometry.area import calculate_area
from blueshark.domain.geometry.validation import validate_shape
from blueshark.domain.geometry.graphical_centroid import centroid_point
from blueshark.domain.geometry.utils import mid_points_arc, mid_points_line


from blueshark.domain.definitions import (
    ShapeType, Geometry, Connection, Connectors
)


class ShapeArea(unittest.TestCase):
    """
    Tests the calculate area function in the geometry module
    """
    def test_standard_circle(self) -> None:
        """
        Tests standard use case of a circle
        """
        geometry: Geometry = {
            "shape": ShapeType.CIRCLE,
            "radius": 5.0
        }
        expected = round(25 * PI, PRECISION)
        result = calculate_area(geometry)
        self.assertEqual(result, expected)

    def test_standard_polygon(self) -> None:
        """
        Tests standard use case of a polygon but off-axis
        """
        geometry: Geometry = {
            "shape": ShapeType.POLYGON,
            "points": [(5, 5), (3, 4), (7, 3)]
        }
        expected = round(3, PRECISION)
        result = calculate_area(geometry)
        self.assertEqual(result, expected)

    def test_standard_annulus_circle(self) -> None:
        """
        Tests standard use case of a annulus circle
        """
        geometry: Geometry = {
            "shape": ShapeType.ANNULUS_CIRCLE,
            "radius_outer": 10.0,
            "radius_inner": 2.0
        }
        expected = round(96 * PI, PRECISION)
        result = calculate_area(geometry)
        self.assertEqual(result, expected)

    def test_standard_annulus_sector(self) -> None:
        """
        Tests standard use case of a annulus sector
        """
        geometry: Geometry = {
            "shape": ShapeType.ANNULUS_SECTOR,
            "radius_outer": 25.0,
            "radius_inner": 10.0,
            "start_angle": 20,
            "end_angle": 50
        }
        expected = round(525 * PI / 12, PRECISION)
        result = calculate_area(geometry)
        self.assertEqual(result, expected)

    def test_standard_hybrid(self) -> None:
        """
        Test standard use case of a hybrid geometry
        """
        edges: list[Connection] = [
            {"type": Connectors.LINE, "start": (0, 0), "end": (0, 5)},
            {"type": Connectors.LINE, "start": (0, 5), "end": (5, 5)},
            {"type": Connectors.LINE, "start": (5, 5), "end": (5, 0)},
        ]

        geometry: Geometry = {
            "shape": ShapeType.HYBRID,
            "edges": edges
        }
        expected = round(5*5, PRECISION)
        result = calculate_area(geometry)
        self.assertEqual(result, expected)

    def test_non_supported_shape(self) -> None:
        """
        invalid shape as input to test resilience of the function
        """
        geometry: Geometry = {
            "shape": "Heptagon",
            "radius": 10
        }

        with self.assertRaises(NotImplementedError):
            calculate_area(geometry)

    def test_2_point_polygon(self) -> None:
        """
        Invalid shape as a line doesn't have area
        """
        geometry: Geometry = {
            "shape": ShapeType.POLYGON,
            "points": [(5, 5), (3, 4)]
        }

        with self.assertRaises(ValueError):
            calculate_area(geometry)

    def test_no_shape(self) -> None:
        """
        Invalid geometry as it doesn't state its shape
        """
        geometry: Geometry = {
            "points": [(5, 5), (3, 4), (7, 3)]
        }

        with self.assertRaises(ValueError):
            calculate_area(geometry)

    def test_no_edges_hybrid(self) -> None:
        """
        invalid hybrid as it has no edges
        """
        edges: list[Connection] = []

        geometry: Geometry = {
            "shape": ShapeType.HYBRID,
            "edges": edges
        }
        with self.assertRaises(ValueError):
            calculate_area(geometry)


class GraphicalCentroid(unittest.TestCase):
    """
    Tests the calculate graphical centroid of a shape in
    geometry module
    """
    def test_standard_circle(self) -> None:
        """
        Tests standard use case of a circle
        """
        geometry: Geometry = {
            "shape": ShapeType.CIRCLE,
            "radius": 5.0,
            "center": (0, 0)
        }

        expected = (0, 0)
        result = centroid_point(geometry)
        self.assertEqual(result, expected)

    def test_standard_polygon(self) -> None:
        """
        Tests standard use of a polygon but off-axis
        """
        geometry: Geometry = {
            "shape": ShapeType.POLYGON,
            "points": [
                (5, 5),
                (3, 4),
                (7, 3)
            ]
        }

        expected = (5, 4)
        result = centroid_point(geometry)
        self.assertEqual(result, expected)

    def test_standard_annulus_circle(self) -> None:
        """
        Tests standard use case of a annulus circle
        """
        geometry: Geometry = {
            "shape": ShapeType.ANNULUS_CIRCLE,
            "radius_outer": 10.0,
            "radius_inner": 2.0,
            "center": (0, 0)
        }
        expected = (0, (10.0 + 2.0) / 2)
        result = centroid_point(geometry)
        self.assertEqual(result, expected)

    def test_standard_annulus_sector(self) -> None:
        """
        Tests standard use case of a annulus sector
        """
        geometry: Geometry = {
            "shape": ShapeType.ANNULUS_SECTOR,
            "radius_outer": 25.0,
            "radius_inner": 10.0,
            "start_angle": 20,
            "end_angle": 50,
            "center": (0, 0)
        }
        expected = (14.335160775057, 10.037587636143)
        result = centroid_point(geometry)
        self.assertEqual(result, expected)

    def test_standard_hybrid(self) -> None:
        """
        Test standard use case of a hybrid geometry
        """
        edges: list[Connection] = [
            {"type": Connectors.LINE, "start": (0, 0), "end": (0, 5)},
            {"type": Connectors.LINE, "start": (0, 5), "end": (5, 5)},
            {"type": Connectors.LINE, "start": (5, 5), "end": (5, 0)},
        ]

        geometry: Geometry = {
            "shape": ShapeType.HYBRID,
            "edges": edges
        }

        expected = (2.5, 2.5)
        result = centroid_point(geometry)
        self.assertEqual(result, expected)

    def test_same_points_polygon(self) -> None:
        """
        Invalid shape as a point doesn't have area and
        so no centroid point
        """
        geometry: Geometry = {
            "shape": ShapeType.POLYGON,
            "points": [(5, 5), (5, 5), (5, 5)]
        }
        with self.assertRaises(ValueError):
            centroid_point(geometry)

    def test_no_shape(self) -> None:
        """
        Invalid geometry as it doesn't state its shape
        """
        geometry: Geometry = {
            "points": [(5, 5), (3, 4), (7, 3)]
        }

        with self.assertRaises(ValueError):
            centroid_point(geometry)


class ValidateShape(unittest.TestCase):
    """
    Tests the validate shape function in geometry module
    """
    def test_standard_circle(self) -> None:
        """
        Tests standard use case of a circle
        """
        geometry: Geometry = {
            "shape": ShapeType.CIRCLE,
            "center": (0, 0),
            "radius": 5.0
        }

        validate_shape(geometry)

    def test_standard_polygon(self) -> None:
        """
        Tests standard use case of a polygon but off-axis
        """
        geometry: Geometry = {
            "shape": ShapeType.POLYGON,
            "points": [(5, 5), (3, 4), (7, 3)]
        }
        validate_shape(geometry)

    def test_standard_annulus_circle(self) -> None:
        """
        Tests standard use case of a annulus circle
        """
        geometry: Geometry = {
            "shape": ShapeType.ANNULUS_CIRCLE,
            "center": (0, 0),
            "radius_outer": 10.0,
            "radius_inner": 2.0
        }
        validate_shape(geometry)

    def test_standard_annulus_sector(self) -> None:
        """
        Tests standard use case of a annulus sector
        """
        geometry: Geometry = {
            "shape": ShapeType.ANNULUS_SECTOR,
            "center": (0, 0),
            "radius_outer": 25.0,
            "radius_inner": 10.0,
            "start_angle": 20,
            "end_angle": 50
        }
        validate_shape(geometry)

    def test_standard_hybrid(self) -> None:
        """
        Test standard use case of a hybrid geometry
        """
        edges: list[Connection] = [
            {"type": Connectors.LINE, "start": (0, 0), "end": (0, 5)},
            {"type": Connectors.LINE, "start": (0, 5), "end": (5, 5)},
            {"type": Connectors.LINE, "start": (5, 5), "end": (5, 0)},
        ]

        geometry: Geometry = {
            "shape": ShapeType.HYBRID,
            "edges": edges
        }
        validate_shape(geometry)

    def test_int_edge_hybrid(self) -> None:
        """
        invalid hybrid as it has no edges
        """

        geometry: Geometry = {
            "shape": ShapeType.HYBRID,
            "edges": 420
        }
        with self.assertRaises(ValueError):
            validate_shape(geometry)

    def test_no_center_annulus_sector(self) -> None:
        """
        invalid annulus sector as it has no center point
        """
        geometry: Geometry = {
            "shape": ShapeType.ANNULUS_SECTOR,
            "radius_outer": 25.0,
            "radius_inner": 10.0,
            "start_angle": 20,
            "end_angle": 50
        }

        with self.assertRaises(ValueError):
            validate_shape(geometry)

    def test_polygon_with_one_point(self) -> None:
        """
        Invalid polygon as it only has one point
        """
        geometry: Geometry = {
            "shape": ShapeType.POLYGON,
            "points": (5, 5)
        }

        with self.assertRaises(ValueError):
            validate_shape(geometry)

    def test_no_shape(self) -> None:
        """
        Invalid geometry as it doesn't state its shape
        """
        geometry: Geometry = {
            "points": [(5, 5), (3, 4), (7, 3)]
        }

        with self.assertRaises(ValueError):
            validate_shape(geometry)


class MidPointsArc(unittest.TestCase):
    """
    Tests the calculate area function under geometry module
    """
    def test_standard_line_segment(self) -> None:
        """
        Tests standard line segment use case
        """
        point_1 = (10, 10)
        point_2 = (40, 40)

        expected_value = (25, 25)
        result = mid_points_line(point_1, point_2)
        self.assertEqual(result, expected_value)

    def test_standard_arc_segment(self) -> None:
        """
        Tests standard arc segment use case
        """
        start_point = (0, 10)
        end_point = (10, 0)
        center = (0, 0)

        expected = (
            round(sqrt(50), PRECISION),
            round(sqrt(50), PRECISION)
        )

        result = mid_points_arc(
            start_point,
            end_point,
            center
        )
        self.assertEqual(result, expected)

    def test_invalid_line_segment(self) -> None:
        """
        Invalid line segment with (x,y,z) instead of (x,y)
        """
        point_1 = (10, 2, 12)
        point_2 = (40, 40)

        with self.assertRaises(ValueError):
            mid_points_line(point_1, point_2)

    def test_invalid_arc_segment(self) -> None:
        """
        Invalid arc segment as it has no center
        """
        start_point = (0, 10)
        end_point = (10, 0)
        center = None

        with self.assertRaises(ValueError):
            mid_points_arc(start_point, end_point, center)
