"""
Tests for Phase 2: Cartesian Product Builder Module

This module tests the Cartesian product building functionality.
"""

import pytest

from src.phase2.cartesian_builder import (
    build_cartesian_product,
    calculate_expected_datasets,
    extract_defendant_info,
    extract_plaintiff_info,
    generate_dataset_id,
    validate_cartesian_product,
)


class TestGenerateDatasetId:
    """Test dataset ID generation."""

    def test_generate_dataset_id(self):
        """Test basic dataset ID generation."""
        result = generate_dataset_id("C1", "P1", "D1")
        assert result == "C1-P1-D1"

    def test_generate_dataset_id_with_special_characters(self):
        """Test dataset ID generation with special characters."""
        result = generate_dataset_id("case-123", "plaintiff_456", "defendant_789")
        assert result == "case-123-plaintiff_456-defendant_789"

    def test_generate_dataset_id_empty_strings(self):
        """Test dataset ID generation with empty strings."""
        result = generate_dataset_id("", "", "")
        assert result == "--"

    def test_generate_dataset_id_numeric_ids(self):
        """Test dataset ID generation with numeric IDs."""
        result = generate_dataset_id("123", "456", "789")
        assert result == "123-456-789"


class TestExtractPlaintiffInfo:
    """Test plaintiff info extraction."""

    def test_extract_plaintiff_info_complete(self):
        """Test extracting complete plaintiff info."""
        plaintiff = {
            "plaintiff_id": "P1",
            "first_name": "Clark",
            "last_name": "Kent",
            "full_name": "Clark Kent",
            "unit_number": "1",
            "discovery": {"vermin": ["Rats"]}
        }
        result = extract_plaintiff_info(plaintiff)
        
        assert result["plaintiff_id"] == "P1"
        assert result["first_name"] == "Clark"
        assert result["last_name"] == "Kent"
        assert result["full_name"] == "Clark Kent"
        assert result["unit_number"] == "1"

    def test_extract_plaintiff_info_missing_fields(self):
        """Test extracting plaintiff info with missing fields."""
        plaintiff = {
            "plaintiff_id": "P1"
            # Missing other fields
        }
        result = extract_plaintiff_info(plaintiff)
        
        assert result["plaintiff_id"] == "P1"
        assert result["first_name"] == ""
        assert result["last_name"] == ""
        assert result["full_name"] == ""
        assert result["unit_number"] is None

    def test_extract_plaintiff_info_empty_plaintiff(self):
        """Test extracting from empty plaintiff object."""
        plaintiff = {}
        result = extract_plaintiff_info(plaintiff)
        
        assert result["plaintiff_id"] == ""
        assert result["first_name"] == ""
        assert result["last_name"] == ""
        assert result["full_name"] == ""
        assert result["unit_number"] is None


class TestExtractDefendantInfo:
    """Test defendant info extraction."""

    def test_extract_defendant_info_complete(self):
        """Test extracting complete defendant info."""
        defendant = {
            "defendant_id": "D1",
            "first_name": "Tony",
            "last_name": "Stark",
            "full_name": "Tony Stark",
            "entity_type": "LLC",
            "role": "Manager"
        }
        result = extract_defendant_info(defendant)
        
        assert result["defendant_id"] == "D1"
        assert result["first_name"] == "Tony"
        assert result["last_name"] == "Stark"
        assert result["full_name"] == "Tony Stark"
        assert result["entity_type"] == "LLC"
        assert result["role"] == "Manager"

    def test_extract_defendant_info_missing_fields(self):
        """Test extracting defendant info with missing fields."""
        defendant = {
            "defendant_id": "D1"
            # Missing other fields
        }
        result = extract_defendant_info(defendant)
        
        assert result["defendant_id"] == "D1"
        assert result["first_name"] == ""
        assert result["last_name"] == ""
        assert result["full_name"] == ""
        assert result["entity_type"] == ""
        assert result["role"] == ""

    def test_extract_defendant_info_empty_defendant(self):
        """Test extracting from empty defendant object."""
        defendant = {}
        result = extract_defendant_info(defendant)
        
        assert result["defendant_id"] == ""
        assert result["first_name"] == ""
        assert result["last_name"] == ""
        assert result["full_name"] == ""
        assert result["entity_type"] == ""
        assert result["role"] == ""


class TestBuildCartesianProduct:
    """Test Cartesian product building."""

    def test_cartesian_product_count(self):
        """Test correct number of datasets generated."""
        # 2 HoH plaintiffs × 2 defendants = 4 datasets
        hoh_plaintiffs = [
            {"plaintiff_id": "P1", "discovery": {}},
            {"plaintiff_id": "P2", "discovery": {}}
        ]
        defendants = [
            {"defendant_id": "D1"},
            {"defendant_id": "D2"}
        ]
        case_info = {"case_id": "C1"}
        
        result = build_cartesian_product(hoh_plaintiffs, defendants, case_info)
        assert len(result) == 4

    def test_cartesian_product_single_combinations(self):
        """Test single HoH and single defendant."""
        hoh_plaintiffs = [{"plaintiff_id": "P1", "discovery": {}}]
        defendants = [{"defendant_id": "D1"}]
        case_info = {"case_id": "C1"}
        
        result = build_cartesian_product(hoh_plaintiffs, defendants, case_info)
        assert len(result) == 1

    def test_cartesian_product_empty_inputs(self):
        """Test Cartesian product with empty inputs."""
        result = build_cartesian_product([], [], {})
        assert result == []

    def test_cartesian_product_contains_all_components(self):
        """Test each dataset has required components."""
        hoh_plaintiffs = [{"plaintiff_id": "P1", "discovery": {"vermin": ["Rats"]}}]
        defendants = [{"defendant_id": "D1", "first_name": "Tony"}]
        case_info = {"case_id": "C1", "property_address": "123 Main St"}
        
        datasets = build_cartesian_product(hoh_plaintiffs, defendants, case_info)
        dataset = datasets[0]
        
        assert "dataset_id" in dataset
        assert "case_id" in dataset
        assert "plaintiff" in dataset
        assert "defendant" in dataset
        assert "case_metadata" in dataset
        assert "discovery_data" in dataset

    def test_cartesian_product_dataset_id_uniqueness(self):
        """Test all dataset IDs are unique."""
        hoh_plaintiffs = [
            {"plaintiff_id": "P1", "discovery": {}},
            {"plaintiff_id": "P2", "discovery": {}}
        ]
        defendants = [
            {"defendant_id": "D1"},
            {"defendant_id": "D2"}
        ]
        case_info = {"case_id": "C1"}
        
        datasets = build_cartesian_product(hoh_plaintiffs, defendants, case_info)
        ids = [d["dataset_id"] for d in datasets]
        assert len(ids) == len(set(ids))

    def test_cartesian_product_preserves_discovery_data(self):
        """Test discovery data is preserved in datasets."""
        discovery_data = {"vermin": ["Rats", "Mice"], "insects": ["Ants"]}
        hoh_plaintiffs = [{"plaintiff_id": "P1", "discovery": discovery_data}]
        defendants = [{"defendant_id": "D1"}]
        case_info = {"case_id": "C1"}
        
        datasets = build_cartesian_product(hoh_plaintiffs, defendants, case_info)
        dataset = datasets[0]
        
        assert dataset["discovery_data"] == discovery_data

    def test_cartesian_product_case_metadata(self):
        """Test case metadata is properly built."""
        hoh_plaintiffs = [{"plaintiff_id": "P1", "unit_number": "5", "discovery": {}}]
        defendants = [{"defendant_id": "D1"}]
        case_info = {
            "case_id": "C1",
            "property_address": "123 Main St",
            "city": "Los Angeles"
        }
        
        datasets = build_cartesian_product(hoh_plaintiffs, defendants, case_info)
        dataset = datasets[0]
        
        assert dataset["case_id"] == "C1"
        assert "property_address_with_unit" in dataset["case_metadata"]
        assert dataset["case_metadata"]["property_address_with_unit"] == "123 Main St Unit 5"

    def test_cartesian_product_plaintiff_info(self):
        """Test plaintiff info is properly extracted."""
        hoh_plaintiffs = [{
            "plaintiff_id": "P1",
            "first_name": "Clark",
            "last_name": "Kent",
            "full_name": "Clark Kent",
            "unit_number": "1",
            "discovery": {}
        }]
        defendants = [{"defendant_id": "D1"}]
        case_info = {"case_id": "C1"}
        
        datasets = build_cartesian_product(hoh_plaintiffs, defendants, case_info)
        dataset = datasets[0]
        
        plaintiff = dataset["plaintiff"]
        assert plaintiff["plaintiff_id"] == "P1"
        assert plaintiff["first_name"] == "Clark"
        assert plaintiff["last_name"] == "Kent"
        assert plaintiff["full_name"] == "Clark Kent"
        assert plaintiff["unit_number"] == "1"

    def test_cartesian_product_defendant_info(self):
        """Test defendant info is properly extracted."""
        hoh_plaintiffs = [{"plaintiff_id": "P1", "discovery": {}}]
        defendants = [{
            "defendant_id": "D1",
            "first_name": "Tony",
            "last_name": "Stark",
            "full_name": "Tony Stark",
            "entity_type": "LLC",
            "role": "Manager"
        }]
        case_info = {"case_id": "C1"}
        
        datasets = build_cartesian_product(hoh_plaintiffs, defendants, case_info)
        dataset = datasets[0]
        
        defendant = dataset["defendant"]
        assert defendant["defendant_id"] == "D1"
        assert defendant["first_name"] == "Tony"
        assert defendant["last_name"] == "Stark"
        assert defendant["full_name"] == "Tony Stark"
        assert defendant["entity_type"] == "LLC"
        assert defendant["role"] == "Manager"


class TestValidateCartesianProduct:
    """Test Cartesian product validation."""

    def test_validate_valid_inputs(self):
        """Test validation with valid inputs."""
        hoh_plaintiffs = [{"plaintiff_id": "P1", "discovery": {}}]
        defendants = [{"defendant_id": "D1"}]
        
        is_valid, errors = validate_cartesian_product(hoh_plaintiffs, defendants)
        assert is_valid
        assert errors == []

    def test_validate_no_hoh_plaintiffs(self):
        """Test validation with no HoH plaintiffs."""
        hoh_plaintiffs = []
        defendants = [{"defendant_id": "D1"}]
        
        is_valid, errors = validate_cartesian_product(hoh_plaintiffs, defendants)
        assert not is_valid
        assert "No HoH plaintiffs provided" in errors

    def test_validate_no_defendants(self):
        """Test validation with no defendants."""
        hoh_plaintiffs = [{"plaintiff_id": "P1", "discovery": {}}]
        defendants = []
        
        is_valid, errors = validate_cartesian_product(hoh_plaintiffs, defendants)
        assert not is_valid
        assert "No defendants provided" in errors

    def test_validate_missing_plaintiff_id(self):
        """Test validation with missing plaintiff_id."""
        hoh_plaintiffs = [{"discovery": {}}]  # Missing plaintiff_id
        defendants = [{"defendant_id": "D1"}]
        
        is_valid, errors = validate_cartesian_product(hoh_plaintiffs, defendants)
        assert not is_valid
        assert any("missing plaintiff_id" in error for error in errors)

    def test_validate_missing_discovery(self):
        """Test validation with missing discovery."""
        hoh_plaintiffs = [{"plaintiff_id": "P1"}]  # Missing discovery
        defendants = [{"defendant_id": "D1"}]
        
        is_valid, errors = validate_cartesian_product(hoh_plaintiffs, defendants)
        assert not is_valid
        assert any("missing discovery data" in error for error in errors)

    def test_validate_missing_defendant_id(self):
        """Test validation with missing defendant_id."""
        hoh_plaintiffs = [{"plaintiff_id": "P1", "discovery": {}}]
        defendants = [{}]  # Missing defendant_id
        
        is_valid, errors = validate_cartesian_product(hoh_plaintiffs, defendants)
        assert not is_valid
        assert any("missing defendant_id" in error for error in errors)

    def test_validate_multiple_errors(self):
        """Test validation with multiple errors."""
        hoh_plaintiffs = [
            {"discovery": {}},  # Missing plaintiff_id
            {"plaintiff_id": "P2"}  # Missing discovery
        ]
        defendants = [{}]  # Missing defendant_id
        
        is_valid, errors = validate_cartesian_product(hoh_plaintiffs, defendants)
        assert not is_valid
        assert len(errors) >= 3  # Multiple errors expected


class TestCalculateExpectedDatasets:
    """Test expected dataset calculation."""

    def test_calculate_expected_datasets(self):
        """Test calculating expected number of datasets."""
        hoh_plaintiffs = [
            {"plaintiff_id": "P1", "discovery": {}},
            {"plaintiff_id": "P2", "discovery": {}}
        ]
        defendants = [
            {"defendant_id": "D1"},
            {"defendant_id": "D2"}
        ]
        
        expected = calculate_expected_datasets(hoh_plaintiffs, defendants)
        assert expected == 4  # 2 × 2 = 4

    def test_calculate_expected_datasets_single_combinations(self):
        """Test calculating with single combinations."""
        hoh_plaintiffs = [{"plaintiff_id": "P1", "discovery": {}}]
        defendants = [{"defendant_id": "D1"}]
        
        expected = calculate_expected_datasets(hoh_plaintiffs, defendants)
        assert expected == 1  # 1 × 1 = 1

    def test_calculate_expected_datasets_empty_inputs(self):
        """Test calculating with empty inputs."""
        expected = calculate_expected_datasets([], [])
        assert expected == 0  # 0 × 0 = 0

    def test_calculate_expected_datasets_one_empty(self):
        """Test calculating with one empty input."""
        hoh_plaintiffs = [{"plaintiff_id": "P1", "discovery": {}}]
        defendants = []
        
        expected = calculate_expected_datasets(hoh_plaintiffs, defendants)
        assert expected == 0  # 1 × 0 = 0
