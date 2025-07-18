"""
OutputWriter
Author: William Bowley
Version: 0.1 (Experimental)
Date: 2025-07-18
Description:
    A helper class for collecting and exporting simulation output data
    to JSON and CSV formats. Designed to modularize and simplify postprocessing
    in FEMM-based motor simulations.
"""

import os
import json
import csv

class OutputWriter:
    def __init__(self, fileBase="output"):
        self.fileBase = fileBase
        self.data = []

    def add(self, result):
        if isinstance(result, list):
            self.data.extend(result)
        else:
            self.data.append(result)


    def write_json(self, filename=None):
        path = filename or f"{self.fileBase}.json"
        dir_path = os.path.dirname(path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.data, f, indent=4)
        print(f"Saved output to {path}")


    def write_csv(self, filename=None):
        path = filename or f"{self.fileBase}.csv"
        dir_path = os.path.dirname(path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        # Flatten tuples/lists inside dict values for CSV writing
        if not self.data:
            print("No data to write.")
            return

        # Get all keys from all dicts to cover varying keys
        keys = set()
        for entry in self.data:
            keys.update(entry.keys())
        keys = list(keys)

        # Prepare rows for CSV: flatten tuple/list values by joining with '|'
        rows = []
        for entry in self.data:
            row = {}
            for k in keys:
                v = entry.get(k, "")
                if isinstance(v, (list, tuple)):
                    # flatten to string separated by '|'
                    v = "|".join(str(i) for i in v)
                row[k] = v
            rows.append(row)

        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)

        print(f"Saved CSV output to {path}")