"""
Filename: output_selector.py
Author: William Bowley
Version: 1.2
Date: 2025-07-29

Description:
    OutputSelector dynamically selects and executes FEMM Heat
    post-processing output functions based on user requests.

    Supported outputs:
"""

import logging
from typing import Any, Callable, Union

from blueshark.solver.femm.thermal import (
    blocks,
    conductors as con
)


class OutputSelector:
    """
    Outputselector dymically selects and executes FEMM post-processing
    output functions.
    """
    def __init__(self, requested_outputs: list[str]) -> None:
        """
        Initialize the OutputSelector with requested output names.

        Args:
            requested_outputs (list): Output names to compute.
                Must be a subset of available outputs.

        Raises:
            ValueError: If unknown outputs are requested.
        """
        self.available_outputs = {
            "volume": (blocks.volume_block, self._run_group),
            "average_temp": (blocks.average_temp_block, self._run_group),
            "cross_section": (blocks.cross_section_block, self._run_group),
            "flux_over_group": (
                blocks.average_flux_over_block, self._run_group
            ),
            "gradient_over_group": (
                blocks.average_graident_over_block, self._run_group
            ),
            "conductor_flux": (con.conductor_heat_flux, self._run_conductor),
            "conductor_temp": (con.conductor_temperature, self._run_conductor)
        }

        unknown = set(requested_outputs) - set(self.available_outputs)
        if unknown:
            msg = (
                f"Unknown outputs requested: {unknown}. "
                f"Available: {list(self.available_outputs)}"
            )
            logging.critical(msg)
            raise ValueError(msg)

        self.outputs = requested_outputs

    def compute(self, subjects: dict) -> dict[str, Any]:
        """
        Compute all requested outputs using provided subjects.

        Args:
            subjects (dict): Should contain 'group' or 'conductorName' keys.

        Returns:
            dict: Output names mapped to results.
        """
        results = {}
        for name in self.outputs:
            func, runner = self.available_outputs[name]
            results[name] = runner(func, subjects)
        return results

    def _run_group(
        self,
        function: Callable[[int], Any],
        subjects: dict
    ) -> Union[Any, list[Any]]:
        """
        Apply a group-based output function.

        Args:
            function (callable): Expects a group ID.
            subjects (dict): Must include 'group'.

        Returns:
            Result or list of results.
        """
        groups = subjects.get("group")
        if groups is None:
            msg = f"Missing 'group' key; keys={list(subjects.keys())}"
            logging.critical(msg)
            raise ValueError(msg)

        if isinstance(groups, (list, tuple)):
            return [function(group) for group in groups]

        return function(groups)

    def _run_conductor(
        self,
        function: Callable[[str], Any],
        subjects: dict
    ) -> Union[Any, list[Any]]:
        """
        Apply a conductor-based output function.

        Args:
            function (callable): Expects a conductor name.
            subjects (dict): Must include 'conductorName'.

        Returns:
            Result or list of results.
        """
        names = subjects.get("conductorName")
        if names is None:
            msg = f"Missing 'conductorName' key; keys={list(subjects.keys())}"
            logging.critical(msg)
            raise ValueError(msg)

        if isinstance(names, (list, tuple)):
            return [function(name) for name in names]

        return function(names)
