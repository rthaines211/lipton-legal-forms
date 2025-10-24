"""
Dataset Builder Pipeline Module for Phase 2: Dataset Builder

This module provides the main pipeline for building datasets from
normalized Phase 1 data.
"""

from typing import Any

from .cartesian_builder import (
    build_cartesian_product,
    calculate_expected_datasets,
    validate_cartesian_product,
)
from .hoh_filter import (
    count_hoh_plaintiffs,
    count_non_hoh_plaintiffs,
    filter_heads_of_household,
    get_non_hoh_plaintiffs,
    validate_hoh_plaintiffs,
)


class DatasetBuildError(Exception):
    """
    Exception raised when dataset building fails.

    Attributes:
        message: Explanation of the error
        errors: List of specific error messages
    """

    def __init__(self, message: str, errors: list[str] | None = None):
        self.message = message
        self.errors = errors or []
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.errors:
            error_list = "\n  - ".join(self.errors)
            return f"{self.message}:\n  - {error_list}"
        return self.message


def build_datasets(normalized_data: dict[str, Any]) -> dict[str, Any]:
    """
    Main dataset building pipeline.

    Args:
        normalized_data: Output from Phase 1 normalizer

    Returns:
        Dataset collection with metadata

    Raises:
        DatasetBuildError: If dataset building fails

    Example:
        >>> normalized_data = {
        ...     'case_info': {'case_id': 'C1', 'property_address': '123 Main St'},
        ...     'plaintiffs': [
        ...         {'is_head_of_household': True, 'plaintiff_id': 'P1', 'discovery': {}}
        ...     ],
        ...     'defendants': [{'defendant_id': 'D1'}]
        ... }
        >>> result = build_datasets(normalized_data)
        >>> result['metadata']['total_datasets']
        1
        >>> len(result['datasets'])
        1
    """
    # Extract components
    case_info = normalized_data['case_info']
    plaintiffs = normalized_data['plaintiffs']
    defendants = normalized_data['defendants']

    # 1. Filter HoH plaintiffs
    hoh_plaintiffs = filter_heads_of_household(plaintiffs)
    non_hoh = get_non_hoh_plaintiffs(plaintiffs)

    # 2. Validate inputs
    hoh_valid, hoh_errors = validate_hoh_plaintiffs(plaintiffs)
    if not hoh_valid:
        raise DatasetBuildError("HoH validation failed", hoh_errors)

    cartesian_valid, cartesian_errors = validate_cartesian_product(hoh_plaintiffs, defendants)
    if not cartesian_valid:
        raise DatasetBuildError("Cartesian product validation failed", cartesian_errors)

    # 3. Build Cartesian product
    datasets = build_cartesian_product(hoh_plaintiffs, defendants, case_info)

    # 4. Build metadata
    expected_datasets = calculate_expected_datasets(hoh_plaintiffs, defendants)
    metadata = {
        'total_datasets': len(datasets),
        'hoh_count': count_hoh_plaintiffs(plaintiffs),
        'defendant_count': len(defendants),
        'non_hoh_plaintiffs': count_non_hoh_plaintiffs(plaintiffs),
        'expected_datasets': expected_datasets
    }

    # 5. Validate results
    if metadata['total_datasets'] != metadata['expected_datasets']:
        raise DatasetBuildError(
            f"Dataset count mismatch: expected {metadata['expected_datasets']}, "
            f"got {metadata['total_datasets']}"
        )

    return {
        'datasets': datasets,
        'metadata': metadata
    }


def build_datasets_batch(normalized_data_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Build datasets for multiple normalized data objects.

    Args:
        normalized_data_list: List of normalized data from Phase 1

    Returns:
        List of dataset collections

    Raises:
        DatasetBuildError: If any dataset building fails

    Example:
        >>> data_list = [normalized_data1, normalized_data2]
        >>> results = build_datasets_batch(data_list)
        >>> len(results)
        2
    """
    results = []

    for i, normalized_data in enumerate(normalized_data_list):
        try:
            result = build_datasets(normalized_data)
            results.append(result)
        except DatasetBuildError as e:
            raise DatasetBuildError(
                f"Dataset building failed for case {i + 1}: {e.message}",
                e.errors
            )

    return results


def validate_dataset_structure(dataset: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate that a dataset has the required structure.

    Args:
        dataset: Dataset to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> dataset = {
        ...     'dataset_id': 'C1-P1-D1',
        ...     'plaintiff': {},
        ...     'defendant': {},
        ...     'case_metadata': {},
        ...     'discovery_data': {}
        ... }
        >>> is_valid, errors = validate_dataset_structure(dataset)
        >>> is_valid
        True
    """
    errors = []
    
    required_fields = ['dataset_id', 'case_id', 'plaintiff', 'defendant', 'case_metadata', 'discovery_data']
    
    for field in required_fields:
        if field not in dataset:
            errors.append(f"Missing required field: {field}")
    
    # Validate plaintiff structure
    if 'plaintiff' in dataset:
        plaintiff = dataset['plaintiff']
        plaintiff_fields = ['plaintiff_id', 'first_name', 'last_name', 'full_name']
        for field in plaintiff_fields:
            if field not in plaintiff:
                errors.append(f"Plaintiff missing field: {field}")
    
    # Validate defendant structure
    if 'defendant' in dataset:
        defendant = dataset['defendant']
        defendant_fields = ['defendant_id', 'first_name', 'last_name', 'full_name', 'entity_type', 'role']
        for field in defendant_fields:
            if field not in defendant:
                errors.append(f"Defendant missing field: {field}")
    
    # Validate case metadata structure
    if 'case_metadata' in dataset:
        case_metadata = dataset['case_metadata']
        metadata_fields = ['property_address', 'property_address_with_unit', 'city', 'state', 'zip']
        for field in metadata_fields:
            if field not in case_metadata:
                errors.append(f"Case metadata missing field: {field}")
    
    return (len(errors) == 0, errors)


def get_dataset_summary(datasets: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Get summary statistics for a collection of datasets.

    Args:
        datasets: List of datasets

    Returns:
        Summary statistics

    Example:
        >>> datasets = [dataset1, dataset2, dataset3]
        >>> summary = get_dataset_summary(datasets)
        >>> summary['total_datasets']
        3
    """
    if not datasets:
        return {
            'total_datasets': 0,
            'unique_plaintiffs': 0,
            'unique_defendants': 0,
            'unique_cases': 0
        }
    
    plaintiff_ids = set(d['plaintiff']['plaintiff_id'] for d in datasets)
    defendant_ids = set(d['defendant']['defendant_id'] for d in datasets)
    case_ids = set(d['case_id'] for d in datasets)
    
    return {
        'total_datasets': len(datasets),
        'unique_plaintiffs': len(plaintiff_ids),
        'unique_defendants': len(defendant_ids),
        'unique_cases': len(case_ids)
    }
