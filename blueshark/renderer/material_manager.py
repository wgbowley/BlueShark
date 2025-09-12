"""
File: material_manager.py
Author: William Bowley
Version: 1.1
Date: 2025-08-09
Description:
    Manages material request from the renderers
    and send them the materials properties depending on
    their physics type. Also enforces choosing specific
    parameters
"""

import logging
import tomllib

from typing import List, Dict, Any, Optional
from importlib import resources


class MaterialManager:
    """
    Generic material manager that loads all materials at initialization.
    Tracks used materials for the renderer.
    """

    def __init__(
        self,
        library_path: Optional[str] = None
    ) -> None:
        """
        Args:
            library_path: Optional path to an external material library (TOML)
        """
        self.used_materials: List[str] = []
        self.materials: Dict[str, Dict[str, Any]] = {}
        if library_path is None:
            try:
                # Load from package resources
                with resources.open_text(
                    "blueshark.lib",
                    "materials.toml"
                ) as file:
                    text = file.read()
                    self.materials = tomllib.loads(text)
            except Exception as error:
                msg = (
                    "Failed to load material library from package resources: "
                    f"{error}"
                )
                logging.critical(msg)
                raise RuntimeError(msg) from error
        else:
            # Load from external path
            try:
                with open(library_path, "rb") as file:
                    self.materials = tomllib.load(file)
            except Exception as error:
                msg = (
                    "Failed to load material library from "
                    f"'{library_path}': {error}"
                )
                logging.critical(msg)
                raise RuntimeError(msg) from error

    def use_material(
        self,
        name: str,
        **params: Any
    ) -> dict[str, Any]:
        """
        Gets the material from the list
        """
        material_list = self.materials.get("material", [])
        for mat in material_list:
            if mat["name"] == name:
                material = mat.copy()  # work on a copy

                # Switch/case for special materials
                match name:
                    case "Copper Wire":
                        if "wire_diameter" in params:
                            material["wire_diameter"] = params["wire_diameter"]

                    case "Neodymium":
                        if "grade" in params:
                            mat_grade = params["grade"]
                            grades = material.get(
                                "runtime", {}
                            ).get("grades", {})

                            if mat_grade in grades:
                                material["coercivity"] = grades[mat_grade]
                                material["runtime"]["grade"] = mat_grade
                            else:
                                msg = f"Invalid Neodymium grade '{mat_grade}'"
                                logging.critical(msg)
                                raise ValueError(msg)

                    # Add more cases for other special materials
                    case _:
                        pass  # default behavior for regular materials

                # Track usage
                if name not in self.used_materials:
                    self.used_materials.append(name)

                return material

        # If material not found
        raise KeyError(f"Material '{name}' not found in library.")
