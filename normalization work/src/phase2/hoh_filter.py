"""
HoH Filter Module for Phase 2: Dataset Builder

This module provides functions to filter Head of Household plaintiffs
and separate them from non-HoH plaintiffs.
"""

from typing import Any


def filter_heads_of_household(plaintiffs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Filter plaintiffs to only those with is_head_of_household=true
    and valid discovery data.

    Args:
        plaintiffs: List of plaintiff objects from Phase 1 normalization

    Returns:
        List of HoH plaintiffs only (those with discovery data)

    Example:
        >>> plaintiffs = [
        ...     {'is_head_of_household': True, 'discovery': {'vermin': []}},
        ...     {'is_head_of_household': False},
        ...     {'is_head_of_household': True, 'discovery': {'insects': []}}
        ... ]
        >>> hoh_plaintiffs = filter_heads_of_household(plaintiffs)
        >>> len(hoh_plaintiffs)
        2
        >>> all(p['is_head_of_household'] for p in hoh_plaintiffs)
        True
    """
    return [
        p for p in plaintiffs
        if p.get('is_head_of_household', False) and 'discovery' in p
    ]


def get_non_hoh_plaintiffs(plaintiffs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Get non-HoH plaintiffs for metadata tracking.

    Args:
        plaintiffs: List of plaintiff objects from Phase 1 normalization

    Returns:
        List of non-HoH plaintiffs (those without discovery data)

    Example:
        >>> plaintiffs = [
        ...     {'is_head_of_household': True, 'discovery': {}},
        ...     {'is_head_of_household': False, 'first_name': 'Bruce'},
        ...     {'is_head_of_household': True, 'discovery': {}}
        ... ]
        >>> non_hoh = get_non_hoh_plaintiffs(plaintiffs)
        >>> len(non_hoh)
        1
        >>> non_hoh[0]['first_name']
        'Bruce'
    """
    return [
        p for p in plaintiffs
        if not p.get('is_head_of_household', False)
    ]


def count_hoh_plaintiffs(plaintiffs: list[dict[str, Any]]) -> int:
    """
    Count the number of Head of Household plaintiffs.

    Args:
        plaintiffs: List of plaintiff objects

    Returns:
        Number of HoH plaintiffs

    Example:
        >>> plaintiffs = [
        ...     {'is_head_of_household': True, 'discovery': {}},
        ...     {'is_head_of_household': False},
        ...     {'is_head_of_household': True, 'discovery': {}}
        ... ]
        >>> count_hoh_plaintiffs(plaintiffs)
        2
    """
    return len(filter_heads_of_household(plaintiffs))


def count_non_hoh_plaintiffs(plaintiffs: list[dict[str, Any]]) -> int:
    """
    Count the number of non-Head of Household plaintiffs.

    Args:
        plaintiffs: List of plaintiff objects

    Returns:
        Number of non-HoH plaintiffs

    Example:
        >>> plaintiffs = [
        ...     {'is_head_of_household': True, 'discovery': {}},
        ...     {'is_head_of_household': False},
        ...     {'is_head_of_household': True, 'discovery': {}}
        ... ]
        >>> count_non_hoh_plaintiffs(plaintiffs)
        1
    """
    return len(get_non_hoh_plaintiffs(plaintiffs))


def validate_hoh_plaintiffs(plaintiffs: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    """
    Validate that HoH plaintiffs have required data.

    Args:
        plaintiffs: List of plaintiff objects

    Returns:
        Tuple of (is_valid, error_messages)

    Validation Rules:
        - At least one HoH plaintiff required
        - All HoH plaintiffs must have discovery data
        - All HoH plaintiffs must have valid plaintiff_id

    Example:
        >>> plaintiffs = [
        ...     {'is_head_of_household': True, 'discovery': {}, 'plaintiff_id': 'P1'}
        ... ]
        >>> is_valid, errors = validate_hoh_plaintiffs(plaintiffs)
        >>> is_valid
        True
        >>> errors
        []
    """
    errors = []
    
    # Get all HoH plaintiffs (not just those with discovery)
    hoh_plaintiffs = [p for p in plaintiffs if p.get('is_head_of_household', False)]
    
    if not hoh_plaintiffs:
        errors.append("No Head of Household plaintiffs found")
        return (False, errors)
    
    for i, plaintiff in enumerate(hoh_plaintiffs):
        if 'plaintiff_id' not in plaintiff or not plaintiff['plaintiff_id']:
            errors.append(f"HoH plaintiff {i + 1} missing plaintiff_id")
        
        if 'discovery' not in plaintiff:
            errors.append(f"HoH plaintiff {i + 1} missing discovery data")
        
        if not isinstance(plaintiff.get('discovery'), dict):
            errors.append(f"HoH plaintiff {i + 1} discovery must be dictionary")
    
    return (len(errors) == 0, errors)
