"""
Filename: output_writer.py
Author: William Bowley
Version: 1.0
Date: 2025-08-03

Description:
    Standalone utility functions for exporting simulation output data
    to JSON and CSV formats.

Functions:
- write_output_json(data, filename = "output.json", status = true):
    Writes the data to json file; Returns None

- write_output_csv(data, filename = "output.csv", status = true, sep = "|"):
    Writes the data to csv file; Returns None
"""

import os
import logging
import json
import csv

from typing import List, Dict, Any


def write_output_json(
    data: List[Dict[str, Any]],
    filename: str = "output.json"
) -> None:
    """
    Write a list of dictionaries to a JSON file.

    Args:
        data (List[Dict]): List of dicts to write.
        filename (str): Output filename (default: "output.json").

    Raises:
        RuntimeError: If the directory or file cannot be written.
    """
    try:
        dir_path = os.path.dirname(filename)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        logging.info(f"Successfully saved output to {filename}")

    except OSError as e:
        msg = f"Error writing to directory or file: {e}"
        logging.error(msg)
        raise RuntimeError(msg) from e

    except Exception as e:
        msg = f"An unexpected error occurred while writing JSON: {e}"
        logging.error(msg)
        raise RuntimeError(msg) from e


def write_output_csv(
    data: List[Dict[str, Any]],
    filename: str = "output.csv",
    sep: str = "|"
) -> None:
    """
    Write a list of dictionaries to a CSV file.
    Tuple or list values are flattened with the given separator.

    Args:
        data (List[Dict]): List of dicts to write.
        filename (str): Output filename (default: "output.csv").
        sep (str): Separator for flattening list/tuple values (default: "|").

    Raises:
        RuntimeError: If the directory or file cannot be written.
    """
    if not data:
        msg = "No data given to write to CSV. Skipping file creation."
        logging.warning(msg)
        return

    try:
        dir_path = os.path.dirname(filename)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        keys = sorted({k for entry in data for k in entry})

        rows = []
        for entry in data:
            row = {}
            for k in keys:
                v = entry.get(k, "")
                if isinstance(v, (list, tuple)):
                    v = sep.join(str(i) for i in v)
                row[k] = v
            rows.append(row)

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)

        logging.info(f"Successfully saved CSV output to {filename}")

    except OSError as e:
        msg = f"Error writing to directory or file: {e}"
        logging.error(msg)
        raise RuntimeError(msg) from e

    except Exception as e:
        msg = f"An unexpected error occurred while writing CSV: {e}"
        logging.error(msg)
        raise RuntimeError(msg) from e
