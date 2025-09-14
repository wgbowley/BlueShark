"""
Filename: utils.py
Author: William Bowley
Version: 1.2
Date: 2025-07-29

Description:
    Utility functions for motor configuration
    parsing and validation.
"""

import logging

from collections.abc import Mapping


def require(key: str, group: Mapping) -> object:
    """
    Retrieve a required key from a mapping-like section.

    Args:
        key: The name of the required parameter.
        group: The dictionary-like section to search.

    Returns:
        The value associated with the given key.
    """

    if key not in group:
        msg = f"Missing required key '{key}' in section {group}"
        logging.critical(msg)
        raise KeyError(msg)

    return group[key]
