"""
File: manager.py
Author: William Bowley
Version: 1.4
Date: 2025-09-13
Description:
    Manages material request from the renderers
    and enforces specific parameters for material types.

    NOTE:
        Material manager is independent of specific renderer/
        solver implementations.
"""

import tomllib

from typing import Optional, Any
from importlib import resources


class MaterialManager:
    """
    Manages material usage for the user. Enforces specific parameters,
    keeps track of used materials
    """
    def __init__(
        self,
        library_path: Optional[str] = None
    ) -> None:
        """
        Initialization of the material manager

        Args:
            library_path: Optional path to an external material library (TOML)
        """
        self.used_materials: list[str] = []
        self.materials: dict[str, dict[str, Any]] = {}

        if library_path is None:
            self._load_from_package()
        else:
            self._load_from_path(library_path)

    def use_material(
        self,
        name: str,
        **params: Any
    ) -> dict[str, Any]:
        """
        Retrieve a material by name and apply required parameters

        Args:
            name: Material name to retrieve
            **params: Required parameter (e.g. wire_diameter, grade)

        Return:
            A copy of the material dictionary with applied params

        Example:
            manager.use_material("NdFeB", grade="N35")
            manager.use_material("copper wire", wire_diameter=0.5)
        """
        material = self._lookup_material(name)
        material = self._apply_parameter(material, params)
        self._track_usage(name)
        return material

    def _lookup_material(self, name: str) -> dict[str, Any]:
        """
        Look up a material by name, case-insensitive.

        Raises:
            KeyError: if material is not found.
        """
        name_lower = name.lower()
        for mat in self.materials.get("material", []):
            if mat["name"].lower() == name_lower:
                return mat.copy()
        raise KeyError(f"Material '{name}' not found in library.")

    def _apply_parameter(
        self,
        material: dict[str, Any],
        params: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Applies required parameters based on material tag

        Raises:
            ValueError: if a required param is missing or invalid
            TypeError: if param type is invalid
        """
        name = material.get("name", "<unknown>")
        tag = material.get("tag", "").lower()

        match tag:
            case "magnet":
                if "grade" not in params:
                    msg = f"Material '{name}' requires parameter 'grade'"
                    raise ValueError(msg)

                grade_value = params["grade"]
                if not isinstance(grade_value, str):
                    msg = f"'grade' must be a string for material '{name}'"
                    raise TypeError(msg)

                grades = material.get("grades", {})
                if grade_value not in grades:
                    msg = (
                        f"Invalid grade '{grade_value}' for material '{name}'"
                    )
                    raise ValueError(msg)

                # Apply all grade-dependent properties to magnetic section
                grade_props = grades[grade_value]
                for key, value in grade_props.items():
                    material["magnetic"][key] = value

            case "wire":

                if "wire_diameter" not in params:
                    msg = f"Material '{name}' requires parameter wire_diameter"
                    raise ValueError(msg)

                wire_diameter = params["wire_diameter"]
                if not isinstance(wire_diameter, (int, float)):
                    msg = (
                        f"wire_diameter must be numeric for material '{name}'"
                    )
                    raise TypeError(msg)

                material["physical"]["wire_diameter"] = wire_diameter

            case "":
                # Generic material, no mandatory parameters
                pass

            case _:
                raise ValueError(f"Unknown tag '{tag}' for material '{name}'")

        return material

    def _track_usage(self, name: str) -> None:
        """Track that this material was used at runtime."""
        if name not in self.used_materials:
            self.used_materials.append(name)

    def _load_from_package(self) -> None:
        """
        Loads the material library that is included in blueshark
        """
        try:
            with resources.open_text(
                "blueshark.library",
                "materials.toml"
            ) as file:
                text = file.read()
                self.materials = tomllib.loads(text)

        except Exception as error:
            msg = (
                "Failed to load material library from package resources: "
                f"{error}"
            )
            raise RuntimeError(msg) from error

    def _load_from_path(self, path: str) -> None:
        """
        Loads the user material library from path
        """
        try:
            with open(path, "rb") as file:
                self.materials = tomllib.load(file)

        except Exception as error:
            msg = f"Failed to load material library from '{path}': {error}"
            raise RuntimeError(msg) from error
