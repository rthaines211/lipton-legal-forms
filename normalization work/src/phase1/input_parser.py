"""
Input Parser Module for Phase 1: Input Normalization

This module provides functions to parse raw form JSON data and extract
structured information about cases, plaintiffs, and defendants.
"""

from typing import Any


def parse_form_json(json_data: dict[str, Any]) -> dict[str, Any]:
    """
    Parse raw form JSON and prepare for normalization.

    Args:
        json_data: Raw form JSON output from the legal form application

    Returns:
        Parsed dictionary ready for component extraction

    Example:
        >>> data = {"Form": {...}, "PlaintiffDetails": [...]}
        >>> parsed = parse_form_json(data)
    """
    if not isinstance(json_data, dict):
        raise TypeError(f"Expected dict, got {type(json_data).__name__}")

    return json_data


def extract_case_info(json_data: dict[str, Any]) -> dict[str, Any]:
    """
    Extract case-level information from form JSON.

    Handles both original format keys ("Filing city") and normalized keys ("FilingCity").
    Supports Full_Address object with all variants (StreetAddress, Line1, etc.).

    Args:
        json_data: Parsed form JSON data

    Returns:
        Dictionary containing case information with normalized keys:
        - case_id: Unique identifier (from Form.Id or generated)
        - property_address: Street address of the property
        - city: City name
        - state: State name
        - zip: Postal code
        - filing_city: City where case is filed
        - filing_county: County where case is filed

    Example:
        >>> case_info = extract_case_info(json_data)
        >>> case_info['property_address']
        '1331 Yorkshire Place NW'
    """
    full_address = json_data.get("Full_Address", {})

    # Extract address components with fallbacks
    property_address = (
        full_address.get("StreetAddress")
        or full_address.get("Line1")
        or ""
    )

    city = full_address.get("City", "")
    state = full_address.get("State", "")
    zip_code = full_address.get("PostalCode", "")

    # Handle both original and normalized filing location keys
    filing_city = (
        json_data.get("Filing city")
        or json_data.get("FilingCity")
        or ""
    )

    filing_county = (
        json_data.get("Filing county")
        or json_data.get("FilingCounty")
        or ""
    )

    # Generate case_id from Form.Id or use a placeholder
    form_info = json_data.get("Form", {})
    case_id = form_info.get("Id", "unknown")

    return {
        "case_id": case_id,
        "property_address": property_address,
        "city": city,
        "state": state,
        "zip": zip_code,
        "filing_city": filing_city,
        "filing_county": filing_county,
    }


def extract_plaintiffs(json_data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extract plaintiff information from form JSON.

    Args:
        json_data: Parsed form JSON data

    Returns:
        List of plaintiff dictionaries, each containing:
        - plaintiff_id: Unique identifier
        - first_name: First name
        - last_name: Last name
        - full_name: Full name (First Last)
        - plaintiff_type: Type (Individual, Guardian, etc.)
        - age_category: Age category (Adult, Minor, etc.)
        - is_head_of_household: Boolean flag
        - unit_number: Unit number (optional)
        - item_number: Plaintiff number
        - discovery: Raw discovery object (to be flattened later)

    Example:
        >>> plaintiffs = extract_plaintiffs(json_data)
        >>> plaintiffs[0]['first_name']
        'Clark'
    """
    plaintiff_details = json_data.get("PlaintiffDetails", [])
    plaintiffs = []

    for plaintiff in plaintiff_details:
        # Extract name information
        name_obj = plaintiff.get("PlaintiffItemNumberName", {})
        first_name = name_obj.get("First", "")
        last_name = name_obj.get("Last", "")
        full_name = name_obj.get("FirstAndLast", f"{first_name} {last_name}".strip())

        # Extract type and age category
        plaintiff_type = plaintiff.get("PlaintiffItemNumberType", "")
        age_category_list = plaintiff.get("PlaintiffItemNumberAgeCategory", [])
        age_category = age_category_list[0] if age_category_list else ""

        # Extract discovery information
        discovery = plaintiff.get("PlaintiffItemNumberDiscovery", {})
        unit_number = discovery.get("Unit")

        # Extract head of household status
        is_hoh = plaintiff.get("HeadOfHousehold", False)

        # Extract item number
        item_number = plaintiff.get("ItemNumber", 0)

        # Build plaintiff object
        plaintiff_obj = {
            "plaintiff_id": plaintiff.get("Id", ""),
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "plaintiff_type": plaintiff_type,
            "age_category": age_category,
            "is_head_of_household": is_hoh,
            "unit_number": unit_number,
            "item_number": item_number,
            "discovery": discovery,  # Will be flattened later
        }

        plaintiffs.append(plaintiff_obj)

    return plaintiffs


def extract_defendants(json_data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extract defendant information from form JSON.

    Args:
        json_data: Parsed form JSON data

    Returns:
        List of defendant dictionaries, each containing:
        - defendant_id: Unique identifier
        - first_name: First name
        - last_name: Last name
        - full_name: Full name (First Last)
        - entity_type: Entity type (LLC, Corporation, Individual, etc.)
        - role: Role (Manager, Owner, etc.)
        - item_number: Defendant number

    Example:
        >>> defendants = extract_defendants(json_data)
        >>> defendants[0]['entity_type']
        'LLC'
    """
    defendant_details = json_data.get("DefendantDetails2", [])
    defendants = []

    for defendant in defendant_details:
        # Extract name information
        name_obj = defendant.get("DefendantItemNumberName", {})
        first_name = name_obj.get("First", "")
        last_name = name_obj.get("Last", "")
        full_name = name_obj.get("FirstAndLast", f"{first_name} {last_name}".strip())

        # Extract entity type and role
        entity_type = defendant.get("DefendantItemNumberType", "")
        role = defendant.get("DefendantItemNumberManagerOwner", "")

        # Extract item number
        item_number = defendant.get("ItemNumber", 0)

        # Build defendant object
        defendant_obj = {
            "defendant_id": defendant.get("Id", ""),
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "entity_type": entity_type,
            "role": role,
            "item_number": item_number,
        }

        defendants.append(defendant_obj)

    return defendants
