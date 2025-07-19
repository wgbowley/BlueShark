"""
Filename: output_writer.py
Author: William Bowley
Version: 0.1 (Experimental)
Date: 2025-07-19

Description:
    A helper class for collecting and exporting simulation output data
    to JSON and CSV formats. Designed to modularize and simplify post-processing
    in FEMM-based motor simulations.
"""

import os
import json
import csv
from typing import Union


class OutputWriter:
    """
    Collects and writes simulation results to JSON and CSV.
    """

    def __init__(self, file_base: str = "output") -> None:
        """
        Initializes the OutputWriter instance.

        Args:
            file_base (str): Base name used for output files if no filename is given.
        """
        self.file_base = file_base
        self.data = []

    def add(self, result: Union[dict, list]) -> None:
        """
        Adds a result or list of results to the output.

        Args:
            result (dict or list of dicts): Output data to append.
        """
        if isinstance(result, list):
            self.data.extend(result)
        else:
            self.data.append(result)

    def write_json(self, filename: str = None) -> None:
        """
        Writes stored data to a JSON file.

        Args:
            filename (str, optional): Custom output path. Uses file_base if not provided.
        """
        path = filename or f"{self.file_base}.json"
        dir_path = os.path.dirname(path)

        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        with open(path, 'w') as f:
            json.dump(self.data, f, indent=4)

        print(f"Saved JSON output to {path}")

    def write_csv(self, filename: str = None) -> None:
        """
        Writes stored data to a CSV file.

        Args:
            filename (str, optional): Custom output path. Uses file_base if not provided.
        """
        if not self.data:
            print("No data to write.")
            return

        path = filename or f"{self.file_base}.csv"
        dir_path = os.path.dirname(path)

        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        # Extract all unique keys across entries
        keys = sorted({key for entry in self.data for key in entry})

        # Flatten tuples/lists inside values
        rows = []
        for entry in self.data:
            row = {}
            for key in keys:
                value = entry.get(key, "")
                if isinstance(value, (list, tuple)):
                    value = "|".join(str(v) for v in value)
                row[key] = value
            rows.append(row)

        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)

        print(f"Saved CSV output to {path}")
