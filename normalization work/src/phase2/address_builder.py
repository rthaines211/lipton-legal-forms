"""
Address Builder Module for Phase 2: Dataset Builder

This module provides functions to build property addresses with unit numbers,
ensuring idempotency (unit appears only once).
"""

import re
from typing import Optional


def build_property_address_with_unit(
    base_address: str,
    unit_number: Optional[str]
) -> str:
    """
    Build property address with unit, ensuring unit appears only once.

    Rules:
    - If base_address already contains "Unit X", return as-is
    - If unit_number provided and not in address, append "Unit X"
    - Otherwise return base_address

    Args:
        base_address: Base property address
        unit_number: Unit number (can be None)

    Returns:
        Address with unit (idempotent)

    Examples:
        >>> build_property_address_with_unit("123 Main St", "5")
        "123 Main St Unit 5"

        >>> build_property_address_with_unit("123 Main St Unit 5", "5")
        "123 Main St Unit 5"

        >>> build_property_address_with_unit("123 Main St", None)
        "123 Main St"

        >>> build_property_address_with_unit("123 Main St unit 5", "5")
        "123 Main St unit 5"
    """
    if not unit_number:
        return base_address

    unit_marker = f"Unit {unit_number}"
    
    # Check if unit already in address (case-insensitive)
    if _unit_already_present(base_address, unit_number):
        return base_address

    # Append unit
    return f"{base_address} {unit_marker}"


def _unit_already_present(address: str, unit_number: str) -> bool:
    """
    Check if unit number is already present in address (case-insensitive).

    Args:
        address: Property address
        unit_number: Unit number to check for

    Returns:
        True if unit already present, False otherwise

    Examples:
        >>> _unit_already_present("123 Main St Unit 5", "5")
        True
        >>> _unit_already_present("123 Main St unit 5", "5")
        True
        >>> _unit_already_present("123 Main St", "5")
        False
    """
    # Create case-insensitive pattern for unit
    unit_pattern = rf"\bunit\s+{re.escape(unit_number)}\b"
    return bool(re.search(unit_pattern, address, re.IGNORECASE))


def extract_unit_from_address(address: str) -> Optional[str]:
    """
    Extract unit number from address if present.

    Args:
        address: Property address

    Returns:
        Unit number if found, None otherwise

    Examples:
        >>> extract_unit_from_address("123 Main St Unit 5")
        "5"
        >>> extract_unit_from_address("123 Main St unit 5")
        "5"
        >>> extract_unit_from_address("123 Main St")
        None
    """
    # Pattern to match "Unit X" or "unit X" (case-insensitive)
    unit_pattern = r"\bunit\s+(\d+)\b"
    match = re.search(unit_pattern, address, re.IGNORECASE)
    return match.group(1) if match else None


def normalize_address_format(address: str) -> str:
    """
    Normalize address format to consistent "Unit X" format.

    Args:
        address: Property address

    Returns:
        Address with normalized unit format

    Examples:
        >>> normalize_address_format("123 Main St unit 5")
        "123 Main St Unit 5"
        >>> normalize_address_format("123 Main St Unit 5")
        "123 Main St Unit 5"
        >>> normalize_address_format("123 Main St")
        "123 Main St"
    """
    # Find unit pattern and normalize to "Unit X"
    unit_pattern = r"\bunit\s+(\d+)\b"
    match = re.search(unit_pattern, address, re.IGNORECASE)
    
    if match:
        unit_number = match.group(1)
        # Replace with normalized format
        normalized_unit = f"Unit {unit_number}"
        return re.sub(unit_pattern, normalized_unit, address, flags=re.IGNORECASE)
    
    return address


def build_case_metadata(case_info: dict[str, str], plaintiff: dict[str, str]) -> dict[str, str]:
    """
    Build case metadata for a dataset.

    Args:
        case_info: Case information from Phase 1
        plaintiff: Plaintiff information

    Returns:
        Case metadata dictionary

    Example:
        >>> case_info = {
        ...     'property_address': '123 Main St',
        ...     'city': 'Los Angeles',
        ...     'state': 'CA',
        ...     'zip': '90001'
        ... }
        >>> plaintiff = {'unit_number': '5'}
        >>> metadata = build_case_metadata(case_info, plaintiff)
        >>> metadata['property_address_with_unit']
        '123 Main St Unit 5'
    """
    base_address = case_info.get('property_address', '')
    unit_number = plaintiff.get('unit_number')
    
    return {
        'property_address': base_address,
        'property_address_with_unit': build_property_address_with_unit(base_address, unit_number),
        'city': case_info.get('city', ''),
        'state': case_info.get('state', ''),
        'zip': case_info.get('zip', ''),
        'filing_city': case_info.get('filing_city', ''),
        'filing_county': case_info.get('filing_county', '')
    }
