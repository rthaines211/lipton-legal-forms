"""
Validators Module for Phase 1: Input Normalization

This module provides validation functions to ensure data integrity
during the normalization process.
"""

from typing import Any


def validate_case_info(case_info: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate case information structure and required fields.

    Args:
        case_info: Case information dictionary

    Returns:
        Tuple of (is_valid, error_messages)
        - is_valid: True if validation passes, False otherwise
        - error_messages: List of validation error messages

    Validation Rules:
        - Required fields: property_address, city, state, zip
        - All required fields must be non-empty strings

    Example:
        >>> case_info = {"property_address": "123 Main St", ...}
        >>> is_valid, errors = validate_case_info(case_info)
        >>> is_valid
        True
    """
    errors = []

    # Required fields
    required_fields = ["property_address", "city", "state", "zip"]

    for field in required_fields:
        if field not in case_info:
            errors.append(f"Missing required field: {field}")
        elif not case_info[field]:
            errors.append(f"Required field is empty: {field}")
        elif not isinstance(case_info[field], str):
            errors.append(f"Field must be string: {field}")

    # Optional fields that should be strings if present
    optional_string_fields = ["case_id", "filing_city", "filing_county"]
    for field in optional_string_fields:
        if field in case_info and case_info[field] is not None:
            if not isinstance(case_info[field], str):
                errors.append(f"Field must be string: {field}")

    return (len(errors) == 0, errors)


def validate_plaintiff(plaintiff: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate plaintiff structure and required fields.

    Args:
        plaintiff: Plaintiff information dictionary

    Returns:
        Tuple of (is_valid, error_messages)

    Validation Rules:
        - Required fields: plaintiff_id, first_name, last_name, full_name
        - At least one of first_name or last_name must be non-empty
        - is_head_of_household must be boolean
        - item_number must be positive integer
        - discovery must be a dictionary

    Example:
        >>> plaintiff = {"plaintiff_id": "123", "first_name": "John", ...}
        >>> is_valid, errors = validate_plaintiff(plaintiff)
    """
    errors = []

    # Required fields
    required_fields = ["plaintiff_id", "first_name", "last_name", "full_name"]

    for field in required_fields:
        if field not in plaintiff:
            errors.append(f"Plaintiff missing required field: {field}")

    # At least one name must be present
    if plaintiff.get("first_name") or plaintiff.get("last_name"):
        pass  # Valid
    else:
        errors.append("Plaintiff must have at least first_name or last_name")

    # Validate boolean fields
    if "is_head_of_household" in plaintiff:
        if not isinstance(plaintiff["is_head_of_household"], bool):
            errors.append("is_head_of_household must be boolean")

    # Validate item_number
    if "item_number" in plaintiff:
        item_num = plaintiff["item_number"]
        if not isinstance(item_num, int) or item_num < 1:
            errors.append("item_number must be positive integer")

    # Validate discovery is dictionary if present
    if "discovery" in plaintiff:
        if not isinstance(plaintiff["discovery"], dict):
            errors.append("discovery must be dictionary")

    return (len(errors) == 0, errors)


def validate_defendant(defendant: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate defendant structure and required fields.

    Args:
        defendant: Defendant information dictionary

    Returns:
        Tuple of (is_valid, error_messages)

    Validation Rules:
        - Required fields: defendant_id, first_name, last_name, full_name
        - At least one of first_name or last_name must be non-empty
        - item_number must be positive integer

    Example:
        >>> defendant = {"defendant_id": "456", "first_name": "Jane", ...}
        >>> is_valid, errors = validate_defendant(defendant)
    """
    errors = []

    # Required fields
    required_fields = ["defendant_id", "first_name", "last_name", "full_name"]

    for field in required_fields:
        if field not in defendant:
            errors.append(f"Defendant missing required field: {field}")

    # At least one name must be present
    if defendant.get("first_name") or defendant.get("last_name"):
        pass  # Valid
    else:
        errors.append("Defendant must have at least first_name or last_name")

    # Validate item_number
    if "item_number" in defendant:
        item_num = defendant["item_number"]
        if not isinstance(item_num, int) or item_num < 1:
            errors.append("item_number must be positive integer")

    return (len(errors) == 0, errors)


def validate_discovery(discovery: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate discovery structure and data types.

    Args:
        discovery: Flattened discovery dictionary

    Returns:
        Tuple of (is_valid, error_messages)

    Validation Rules:
        - Array fields must be lists (empty lists OK)
        - Boolean flags must be actual booleans
        - All expected keys should be present

    Example:
        >>> discovery = {"vermin": ["Rats"], "has_injury": True, ...}
        >>> is_valid, errors = validate_discovery(discovery)
    """
    errors = []

    # Expected array keys
    array_keys = [
        "vermin",
        "insects",
        "hvac",
        "electrical",
        "fire_hazard",
        "government_entities",
        "appliances",
        "plumbing",
        "cabinets",
        "flooring",
        "windows",
        "doors",
        "structure",
        "common_areas",
        "trash_problems",
        "nuisance",
        "health_hazard",
        "harassment",
        "notices",
        "utility_interruptions",
        "safety_issues",
    ]

    # Expected boolean keys
    boolean_keys = [
        "has_injury",
        "has_nonresponsive_landlord",
        "has_unauthorized_entries",
        "has_stolen_items",
        "has_damaged_items",
        "has_age_discrimination",
        "has_racial_discrimination",
        "has_disability_discrimination",
        "has_security_deposit_issues",
    ]

    # Validate array fields
    for key in array_keys:
        if key not in discovery:
            errors.append(f"Missing array field: {key}")
        elif not isinstance(discovery[key], list):
            errors.append(f"Array field must be list: {key}")

    # Validate boolean fields
    for key in boolean_keys:
        if key not in discovery:
            errors.append(f"Missing boolean field: {key}")
        elif not isinstance(discovery[key], bool):
            errors.append(f"Boolean field must be bool: {key}")

    return (len(errors) == 0, errors)


def validate_normalized_data(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate complete normalized data structure.

    This is the top-level validation function that validates the entire
    normalized output including case info, plaintiffs, and defendants.

    Args:
        data: Complete normalized data structure

    Returns:
        Tuple of (is_valid, error_messages)

    Validation Rules:
        - Must have case_info, plaintiffs, and defendants keys
        - At least 1 plaintiff with valid data
        - At least 1 defendant with valid data
        - All plaintiffs must pass validation
        - All defendants must pass validation
        - All plaintiff discoveries must pass validation

    Example:
        >>> normalized = {
        ...     "case_info": {...},
        ...     "plaintiffs": [...],
        ...     "defendants": [...]
        ... }
        >>> is_valid, errors = validate_normalized_data(normalized)
    """
    errors = []

    # Check top-level structure
    if "case_info" not in data:
        errors.append("Missing case_info")
    if "plaintiffs" not in data:
        errors.append("Missing plaintiffs")
    if "defendants" not in data:
        errors.append("Missing defendants")

    if errors:
        return (False, errors)

    # Validate case info
    case_valid, case_errors = validate_case_info(data["case_info"])
    if not case_valid:
        errors.extend(case_errors)

    # Validate plaintiffs
    plaintiffs = data.get("plaintiffs", [])
    if not plaintiffs:
        errors.append("Must have at least 1 plaintiff")
    else:
        for i, plaintiff in enumerate(plaintiffs):
            p_valid, p_errors = validate_plaintiff(plaintiff)
            if not p_valid:
                errors.extend([f"Plaintiff {i + 1}: {err}" for err in p_errors])

            # Validate discovery if present
            if "discovery" in plaintiff:
                d_valid, d_errors = validate_discovery(plaintiff["discovery"])
                if not d_valid:
                    errors.extend(
                        [f"Plaintiff {i + 1} discovery: {err}" for err in d_errors]
                    )

    # Validate defendants
    defendants = data.get("defendants", [])
    if not defendants:
        errors.append("Must have at least 1 defendant")
    else:
        for i, defendant in enumerate(defendants):
            d_valid, d_errors = validate_defendant(defendant)
            if not d_valid:
                errors.extend([f"Defendant {i + 1}: {err}" for err in d_errors])

    return (len(errors) == 0, errors)
