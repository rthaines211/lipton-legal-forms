"""
Discovery Flattener Module for Phase 1: Input Normalization

This module provides functions to flatten and normalize discovery/issue data
from the complex nested structure to a simplified format.
"""

from typing import Any, Union


# Key mappings from original form keys to normalized snake_case keys
KEY_MAPPINGS: dict[str, str] = {
    # Array keys - multi-select issue categories
    "Vermin": "vermin",
    "Insects": "insects",
    "HVAC": "hvac",
    "Electrical": "electrical",
    "Fire Hazard": "fire_hazard",
    "Specific Government Entity Contacted": "government_entities",
    "Appliances": "appliances",
    "Plumbing": "plumbing",
    "Cabinets": "cabinets",
    "Flooring": "flooring",
    "Windows": "windows",
    "Doors": "doors",
    "Structure": "structure",
    "Common areas": "common_areas",
    "Select Trash Problems": "trash_problems",
    "Nuisance": "nuisance",
    "Health hazard": "health_hazard",
    "Harassment": "harassment",
    "Select Notices Issues": "notices",
    "Checkbox 44n6i": "utility_interruptions",
    "Select Safety Issues": "safety_issues",
    # Boolean flag keys
    "Injury Issues": "has_injury",
    "Nonresponsive landlord Issues": "has_nonresponsive_landlord",
    "Unauthorized entries": "has_unauthorized_entries",
    "Stolen items": "has_stolen_items",
    "Damaged items": "has_damaged_items",
    "Age discrimination": "has_age_discrimination",
    "Racial Discrimination": "has_racial_discrimination",
    "Disability discrimination": "has_disability_discrimination",
    "Security Deposit": "has_security_deposit_issues",
}


def normalize_array_keys(discovery: dict[str, Any]) -> dict[str, Union[list[Any], bool]]:
    """
    Normalize array keys from original format to snake_case format.

    Args:
        discovery: Raw discovery object from form JSON

    Returns:
        Dictionary with normalized array keys (e.g., "Vermin" -> "vermin")

    Example:
        >>> discovery = {"Vermin": ["Rats/Mice"], "Insects": ["Roaches"]}
        >>> normalized = normalize_array_keys(discovery)
        >>> normalized['vermin']
        ['Rats/Mice']
    """
    normalized: dict[str, Union[list[Any], bool]] = {}

    for original_key, normalized_key in KEY_MAPPINGS.items():
        if original_key in discovery:
            value = discovery[original_key]
            # Ensure arrays are actual lists
            if isinstance(value, list):
                normalized[normalized_key] = value
            elif value is True or value is False:
                # Boolean flags
                normalized[normalized_key] = value
            elif normalized_key.startswith("has_"):
                # Boolean flag - coerce to boolean
                normalized[normalized_key] = bool(value)
            else:
                # Default to empty list for non-list, non-boolean values
                normalized[normalized_key] = []
        else:
            # Key not present - set default
            if normalized_key.startswith("has_"):
                # Boolean flag - default to False
                normalized[normalized_key] = False
            else:
                # Array - default to empty list
                normalized[normalized_key] = []

    return normalized


def extract_boolean_flags(discovery: dict[str, Any]) -> dict[str, bool]:
    """
    Extract boolean flags from discovery object.

    Args:
        discovery: Raw discovery object from form JSON

    Returns:
        Dictionary containing only boolean flags with normalized keys

    Example:
        >>> discovery = {"Injury Issues": True, "Stolen items": False}
        >>> flags = extract_boolean_flags(discovery)
        >>> flags['has_injury']
        True
    """
    flags = {}

    boolean_keys = {
        "Injury Issues": "has_injury",
        "Nonresponsive landlord Issues": "has_nonresponsive_landlord",
        "Unauthorized entries": "has_unauthorized_entries",
        "Stolen items": "has_stolen_items",
        "Damaged items": "has_damaged_items",
        "Age discrimination": "has_age_discrimination",
        "Racial Discrimination": "has_racial_discrimination",
        "Disability discrimination": "has_disability_discrimination",
        "Security Deposit": "has_security_deposit_issues",
    }

    for original_key, normalized_key in boolean_keys.items():
        value = discovery.get(original_key, False)
        # Ensure value is actually a boolean
        if isinstance(value, bool):
            flags[normalized_key] = value
        else:
            # Coerce to boolean if needed
            flags[normalized_key] = bool(value)

    return flags


def flatten_discovery(discovery_obj: dict[str, Any]) -> dict[str, Union[list[Any], bool]]:
    """
    Flatten discovery object into normalized structure.

    This is the main function that combines array normalization and boolean
    flag extraction into a single, flat discovery structure.

    Args:
        discovery_obj: Raw discovery object from plaintiff data

    Returns:
        Flattened discovery dictionary with:
        - All array keys normalized to snake_case
        - All boolean flags extracted with has_ prefix
        - Empty arrays for missing categories
        - False for missing boolean flags

    Example:
        >>> discovery = {
        ...     "VerminIssue": True,
        ...     "Vermin": ["Rats/Mice", "Bedbugs"],
        ...     "Injury Issues": True
        ... }
        >>> flattened = flatten_discovery(discovery)
        >>> flattened['vermin']
        ['Rats/Mice', 'Bedbugs']
        >>> flattened['has_injury']
        True
    """
    if not discovery_obj:
        # Empty discovery - return structure with all defaults
        return _create_empty_discovery()

    # Step 1: Normalize array keys
    normalized = normalize_array_keys(discovery_obj)

    # Step 2: Extract boolean flags (already included in normalize_array_keys)
    # This ensures we have a complete structure

    return normalized


def _create_empty_discovery() -> dict[str, Union[list[Any], bool]]:
    """
    Create an empty discovery structure with all default values.

    Returns:
        Discovery dictionary with empty arrays and False boolean flags

    Example:
        >>> empty = _create_empty_discovery()
        >>> empty['vermin']
        []
        >>> empty['has_injury']
        False
    """
    return {
        # Array fields - all empty lists
        "vermin": [],
        "insects": [],
        "hvac": [],
        "electrical": [],
        "fire_hazard": [],
        "government_entities": [],
        "appliances": [],
        "plumbing": [],
        "cabinets": [],
        "flooring": [],
        "windows": [],
        "doors": [],
        "structure": [],
        "common_areas": [],
        "trash_problems": [],
        "nuisance": [],
        "health_hazard": [],
        "harassment": [],
        "notices": [],
        "utility_interruptions": [],
        "safety_issues": [],
        # Boolean flags - all False
        "has_injury": False,
        "has_nonresponsive_landlord": False,
        "has_unauthorized_entries": False,
        "has_stolen_items": False,
        "has_damaged_items": False,
        "has_age_discrimination": False,
        "has_racial_discrimination": False,
        "has_disability_discrimination": False,
        "has_security_deposit_issues": False,
    }
