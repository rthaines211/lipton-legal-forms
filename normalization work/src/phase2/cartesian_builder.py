"""
Cartesian Product Builder Module for Phase 2: Dataset Builder

This module provides functions to build the Cartesian product of
Head of Household plaintiffs × Defendants, creating datasets.
"""

from typing import Any


def build_cartesian_product(
    hoh_plaintiffs: list[dict[str, Any]],
    defendants: list[dict[str, Any]],
    case_info: dict[str, Any]
) -> list[dict[str, Any]]:
    """
    Build HoH × Defendant Cartesian product.

    For each HoH plaintiff:
        For each defendant:
            Create dataset with:
                - Plaintiff info
                - Defendant info
                - Case metadata
                - Discovery data

    Args:
        hoh_plaintiffs: Filtered HoH plaintiffs
        defendants: All defendants
        case_info: Case metadata

    Returns:
        List of datasets (one per HoH × Defendant combination)

    Example:
        >>> hoh_plaintiffs = [
        ...     {'plaintiff_id': 'P1', 'first_name': 'Clark', 'discovery': {}}
        ... ]
        >>> defendants = [
        ...     {'defendant_id': 'D1', 'first_name': 'Tony'}
        ... ]
        >>> case_info = {'case_id': 'C1', 'property_address': '123 Main St'}
        >>> datasets = build_cartesian_product(hoh_plaintiffs, defendants, case_info)
        >>> len(datasets)
        1
        >>> datasets[0]['dataset_id']
        'C1-P1-D1'
    """
    datasets = []

    for plaintiff in hoh_plaintiffs:
        for defendant in defendants:
            dataset = {
                'dataset_id': generate_dataset_id(
                    case_info['case_id'],
                    plaintiff['plaintiff_id'],
                    defendant['defendant_id']
                ),
                'case_id': case_info['case_id'],
                'plaintiff': extract_plaintiff_info(plaintiff),
                'defendant': extract_defendant_info(defendant),
                'case_metadata': build_case_metadata(case_info, plaintiff),
                'discovery_data': plaintiff['discovery'],
                # Pass through case context from Phase 1 for use in Phase 5
                'case_context': case_info.get('case_context', {})
            }
            datasets.append(dataset)

    return datasets


def generate_dataset_id(case_id: str, plaintiff_id: str, defendant_id: str) -> str:
    """
    Generate unique dataset ID.

    Args:
        case_id: Case identifier
        plaintiff_id: Plaintiff identifier
        defendant_id: Defendant identifier

    Returns:
        Unique dataset ID in format: {case_id}-{plaintiff_id}-{defendant_id}

    Example:
        >>> generate_dataset_id("C1", "P1", "D1")
        "C1-P1-D1"
    """
    return f"{case_id}-{plaintiff_id}-{defendant_id}"


def extract_plaintiff_info(plaintiff: dict[str, Any]) -> dict[str, Any]:
    """
    Extract relevant plaintiff information for dataset.

    Args:
        plaintiff: Full plaintiff object from Phase 1

    Returns:
        Simplified plaintiff info for dataset

    Example:
        >>> plaintiff = {
        ...     'plaintiff_id': 'P1',
        ...     'first_name': 'Clark',
        ...     'last_name': 'Kent',
        ...     'full_name': 'Clark Kent',
        ...     'unit_number': '1',
        ...     'discovery': {}
        ... }
        >>> info = extract_plaintiff_info(plaintiff)
        >>> info['plaintiff_id']
        'P1'
    """
    return {
        'plaintiff_id': plaintiff.get('plaintiff_id', ''),
        'first_name': plaintiff.get('first_name', ''),
        'last_name': plaintiff.get('last_name', ''),
        'full_name': plaintiff.get('full_name', ''),
        'unit_number': plaintiff.get('unit_number')
    }


def extract_defendant_info(defendant: dict[str, Any]) -> dict[str, Any]:
    """
    Extract relevant defendant information for dataset.

    Args:
        defendant: Full defendant object from Phase 1

    Returns:
        Simplified defendant info for dataset

    Example:
        >>> defendant = {
        ...     'defendant_id': 'D1',
        ...     'first_name': 'Tony',
        ...     'last_name': 'Stark',
        ...     'entity_type': 'LLC',
        ...     'role': 'Manager'
        ... }
        >>> info = extract_defendant_info(defendant)
        >>> info['defendant_id']
        'D1'
    """
    return {
        'defendant_id': defendant.get('defendant_id', ''),
        'first_name': defendant.get('first_name', ''),
        'last_name': defendant.get('last_name', ''),
        'full_name': defendant.get('full_name', ''),
        'entity_type': defendant.get('entity_type', ''),
        'role': defendant.get('role', '')
    }


def build_case_metadata(case_info: dict[str, Any], plaintiff: dict[str, Any]) -> dict[str, str]:
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
    from .address_builder import build_property_address_with_unit
    
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


def validate_cartesian_product(
    hoh_plaintiffs: list[dict[str, Any]],
    defendants: list[dict[str, Any]]
) -> tuple[bool, list[str]]:
    """
    Validate inputs for Cartesian product building.

    Args:
        hoh_plaintiffs: HoH plaintiffs to validate
        defendants: Defendants to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> hoh_plaintiffs = [{'plaintiff_id': 'P1', 'discovery': {}}]
        >>> defendants = [{'defendant_id': 'D1'}]
        >>> is_valid, errors = validate_cartesian_product(hoh_plaintiffs, defendants)
        >>> is_valid
        True
    """
    errors = []
    
    if not hoh_plaintiffs:
        errors.append("No HoH plaintiffs provided")
    
    if not defendants:
        errors.append("No defendants provided")
    
    # Validate HoH plaintiffs have required fields
    for i, plaintiff in enumerate(hoh_plaintiffs):
        if 'plaintiff_id' not in plaintiff or not plaintiff['plaintiff_id']:
            errors.append(f"HoH plaintiff {i + 1} missing plaintiff_id")
        
        if 'discovery' not in plaintiff:
            errors.append(f"HoH plaintiff {i + 1} missing discovery data")
    
    # Validate defendants have required fields
    for i, defendant in enumerate(defendants):
        if 'defendant_id' not in defendant or not defendant['defendant_id']:
            errors.append(f"Defendant {i + 1} missing defendant_id")
    
    return (len(errors) == 0, errors)


def calculate_expected_datasets(
    hoh_plaintiffs: list[dict[str, Any]],
    defendants: list[dict[str, Any]]
) -> int:
    """
    Calculate expected number of datasets.

    Args:
        hoh_plaintiffs: HoH plaintiffs
        defendants: Defendants

    Returns:
        Expected number of datasets (HoH count × Defendant count)

    Example:
        >>> hoh_plaintiffs = [{'plaintiff_id': 'P1'}, {'plaintiff_id': 'P2'}]
        >>> defendants = [{'defendant_id': 'D1'}, {'defendant_id': 'D2'}]
        >>> calculate_expected_datasets(hoh_plaintiffs, defendants)
        4
    """
    return len(hoh_plaintiffs) * len(defendants)
