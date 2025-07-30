"""
Filename: utils.py
Author: William Bowley
Version: 1.2
Date: 2025-07-29

Description:
    Utility functions for motor configuration and validation.
    
    Functions:
        - require(key, group): Ensure required parameters exist in a configuration section.
"""

def require(key: str, group: dict) -> object:
    """
    Retrieve a required key from a dictionary-like section.

    Args:
        key (str): The name of the required parameter.
        group (dict): The dictionary (e.g., a section from a config file) to search in.

    Returns:
        object: The value associated with the given key.

    Raises:
        KeyError: If the key is not found in the dictionary.
    """
    if key not in group:
        raise KeyError(f"Missing required key '{key}' in section {group}")
    return group[key]