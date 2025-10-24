"""
Tests for Phase 2: Dataset Builder Pipeline

This module tests the main dataset building pipeline.
"""

import pytest

from src.phase2.dataset_builder import (
    DatasetBuildError,
    build_datasets,
    build_datasets_batch,
    get_dataset_summary,
    validate_dataset_structure,
)
from tests.fixtures.phase2_samples import (
    COMPLEX_DISCOVERY,
    INVALID_NO_DEFENDANTS,
    INVALID_NO_HOH,
    MIXED_PLAINTIFFS,
    MULTI_HOH_MULTI_DEFENDANT,
    SINGLE_HOH_SINGLE_DEFENDANT,
)


class TestBuildDatasets:
    """Test main dataset building pipeline."""

    def test_build_datasets_simple_case(self):
        """Test building datasets for simple case."""
        # 1 HoH, 1 defendant → 1 dataset
        result = build_datasets(SINGLE_HOH_SINGLE_DEFENDANT)
        
        assert result["metadata"]["total_datasets"] == 1
        assert result["metadata"]["hoh_count"] == 1
        assert result["metadata"]["defendant_count"] == 1
        assert result["metadata"]["non_hoh_plaintiffs"] == 0
        assert result["metadata"]["expected_datasets"] == 1
        assert len(result["datasets"]) == 1

    def test_build_datasets_complex_case(self):
        """Test building datasets for complex case."""
        # 2 HoH, 2 defendants → 4 datasets
        result = build_datasets(MULTI_HOH_MULTI_DEFENDANT)
        
        assert result["metadata"]["total_datasets"] == 4
        assert result["metadata"]["hoh_count"] == 2
        assert result["metadata"]["defendant_count"] == 2
        assert result["metadata"]["non_hoh_plaintiffs"] == 0
        assert result["metadata"]["expected_datasets"] == 4
        assert len(result["datasets"]) == 4

    def test_build_datasets_mixed_plaintiffs(self):
        """Test building datasets with mixed plaintiffs."""
        # 2 HoH, 1 non-HoH, 2 defendants → 4 datasets (non-HoH excluded)
        result = build_datasets(MIXED_PLAINTIFFS)
        
        assert result["metadata"]["total_datasets"] == 4
        assert result["metadata"]["hoh_count"] == 2
        assert result["metadata"]["defendant_count"] == 2
        assert result["metadata"]["non_hoh_plaintiffs"] == 1
        assert result["metadata"]["expected_datasets"] == 4
        assert len(result["datasets"]) == 4

    def test_build_datasets_preserves_discovery(self):
        """Test discovery data preserved in datasets."""
        result = build_datasets(SINGLE_HOH_SINGLE_DEFENDANT)
        dataset = result["datasets"][0]
        
        assert "vermin" in dataset["discovery_data"]
        assert "insects" in dataset["discovery_data"]
        assert "has_injury" in dataset["discovery_data"]
        assert "has_nonresponsive_landlord" in dataset["discovery_data"]
        
        # Verify specific values
        assert dataset["discovery_data"]["vermin"] == ["Rats/Mice", "Skunks"]
        assert dataset["discovery_data"]["insects"] == ["Ants", "Roaches"]
        assert dataset["discovery_data"]["has_injury"] is True
        assert dataset["discovery_data"]["has_nonresponsive_landlord"] is False

    def test_build_datasets_dataset_structure(self):
        """Test dataset structure is correct."""
        result = build_datasets(SINGLE_HOH_SINGLE_DEFENDANT)
        dataset = result["datasets"][0]
        
        # Check required fields
        assert "dataset_id" in dataset
        assert "case_id" in dataset
        assert "plaintiff" in dataset
        assert "defendant" in dataset
        assert "case_metadata" in dataset
        assert "discovery_data" in dataset
        
        # Check dataset_id format
        assert dataset["dataset_id"] == "form-entry-123-P1-D1"
        assert dataset["case_id"] == "form-entry-123"

    def test_build_datasets_plaintiff_info(self):
        """Test plaintiff info in dataset."""
        result = build_datasets(SINGLE_HOH_SINGLE_DEFENDANT)
        dataset = result["datasets"][0]
        plaintiff = dataset["plaintiff"]
        
        assert plaintiff["plaintiff_id"] == "P1"
        assert plaintiff["first_name"] == "Clark"
        assert plaintiff["last_name"] == "Kent"
        assert plaintiff["full_name"] == "Clark Kent"
        assert plaintiff["unit_number"] == "1"

    def test_build_datasets_defendant_info(self):
        """Test defendant info in dataset."""
        result = build_datasets(SINGLE_HOH_SINGLE_DEFENDANT)
        dataset = result["datasets"][0]
        defendant = dataset["defendant"]
        
        assert defendant["defendant_id"] == "D1"
        assert defendant["first_name"] == "Tony"
        assert defendant["last_name"] == "Stark"
        assert defendant["full_name"] == "Tony Stark"
        assert defendant["entity_type"] == "LLC"
        assert defendant["role"] == "Manager"

    def test_build_datasets_case_metadata(self):
        """Test case metadata in dataset."""
        result = build_datasets(SINGLE_HOH_SINGLE_DEFENDANT)
        dataset = result["datasets"][0]
        case_metadata = dataset["case_metadata"]
        
        assert case_metadata["property_address"] == "123 Main St"
        assert case_metadata["property_address_with_unit"] == "123 Main St Unit 1"
        assert case_metadata["city"] == "Los Angeles"
        assert case_metadata["state"] == "CA"
        assert case_metadata["zip"] == "90001"
        assert case_metadata["filing_city"] == "Los Angeles"
        assert case_metadata["filing_county"] == "Los Angeles County"

    def test_build_datasets_complex_discovery(self):
        """Test building datasets with complex discovery data."""
        result = build_datasets(COMPLEX_DISCOVERY)
        dataset = result["datasets"][0]
        discovery = dataset["discovery_data"]
        
        # Check array fields
        assert "vermin" in discovery
        assert "insects" in discovery
        assert "hvac" in discovery
        assert "electrical" in discovery
        assert "fire_hazard" in discovery
        assert "government_entities" in discovery
        assert "appliances" in discovery
        assert "plumbing" in discovery
        assert "flooring" in discovery
        assert "windows" in discovery
        assert "doors" in discovery
        assert "structure" in discovery
        assert "common_areas" in discovery
        assert "nuisance" in discovery
        assert "health_hazard" in discovery
        assert "harassment" in discovery
        
        # Check boolean fields
        assert "has_injury" in discovery
        assert "has_nonresponsive_landlord" in discovery
        assert "has_unauthorized_entries" in discovery
        assert "has_stolen_items" in discovery
        assert "has_damaged_items" in discovery
        assert "has_age_discrimination" in discovery
        assert "has_racial_discrimination" in discovery
        assert "has_disability_discrimination" in discovery

    def test_build_datasets_no_hoh_raises_error(self):
        """Test error raised when no HoH plaintiffs."""
        with pytest.raises(DatasetBuildError) as exc_info:
            build_datasets(INVALID_NO_HOH)
        
        assert "HoH validation failed" in str(exc_info.value)
        assert "No Head of Household plaintiffs found" in str(exc_info.value)

    def test_build_datasets_no_defendants_raises_error(self):
        """Test error raised when no defendants."""
        with pytest.raises(DatasetBuildError) as exc_info:
            build_datasets(INVALID_NO_DEFENDANTS)
        
        assert "Cartesian product validation failed" in str(exc_info.value)
        assert "No defendants provided" in str(exc_info.value)

    def test_build_datasets_dataset_count_validation(self):
        """Test dataset count validation."""
        result = build_datasets(MULTI_HOH_MULTI_DEFENDANT)
        
        # Verify count matches expected
        assert result["metadata"]["total_datasets"] == result["metadata"]["expected_datasets"]
        
        # Verify all datasets have unique IDs
        dataset_ids = [d["dataset_id"] for d in result["datasets"]]
        assert len(dataset_ids) == len(set(dataset_ids))

    def test_build_datasets_all_combinations_present(self):
        """Test all HoH × Defendant combinations are present."""
        result = build_datasets(MULTI_HOH_MULTI_DEFENDANT)
        
        # Should have P1×D1, P1×D2, P2×D1, P2×D2
        expected_ids = [
            "form-entry-456-P1-D1",
            "form-entry-456-P1-D2", 
            "form-entry-456-P2-D1",
            "form-entry-456-P2-D2"
        ]
        actual_ids = [d["dataset_id"] for d in result["datasets"]]
        
        for expected_id in expected_ids:
            assert expected_id in actual_ids


class TestBuildDatasetsBatch:
    """Test batch dataset building."""

    def test_build_datasets_batch_success(self):
        """Test successful batch building."""
        data_list = [SINGLE_HOH_SINGLE_DEFENDANT, MULTI_HOH_MULTI_DEFENDANT]
        results = build_datasets_batch(data_list)
        
        assert len(results) == 2
        assert results[0]["metadata"]["total_datasets"] == 1
        assert results[1]["metadata"]["total_datasets"] == 4

    def test_build_datasets_batch_with_error(self):
        """Test batch building with error."""
        data_list = [SINGLE_HOH_SINGLE_DEFENDANT, INVALID_NO_HOH]
        
        with pytest.raises(DatasetBuildError) as exc_info:
            build_datasets_batch(data_list)
        
        assert "Dataset building failed for case 2" in str(exc_info.value)

    def test_build_datasets_batch_empty_list(self):
        """Test batch building with empty list."""
        results = build_datasets_batch([])
        assert results == []


class TestValidateDatasetStructure:
    """Test dataset structure validation."""

    def test_validate_dataset_structure_valid(self):
        """Test validation with valid dataset structure."""
        dataset = {
            "dataset_id": "C1-P1-D1",
            "case_id": "C1",
            "plaintiff": {
                "plaintiff_id": "P1",
                "first_name": "Clark",
                "last_name": "Kent",
                "full_name": "Clark Kent"
            },
            "defendant": {
                "defendant_id": "D1",
                "first_name": "Tony",
                "last_name": "Stark",
                "full_name": "Tony Stark",
                "entity_type": "LLC",
                "role": "Manager"
            },
            "case_metadata": {
                "property_address": "123 Main St",
                "property_address_with_unit": "123 Main St Unit 1",
                "city": "Los Angeles",
                "state": "CA",
                "zip": "90001"
            },
            "discovery_data": {"vermin": ["Rats"]}
        }
        
        is_valid, errors = validate_dataset_structure(dataset)
        assert is_valid
        assert errors == []

    def test_validate_dataset_structure_missing_required_field(self):
        """Test validation with missing required field."""
        dataset = {
            "case_id": "C1",
            "plaintiff": {},
            "defendant": {},
            "case_metadata": {},
            "discovery_data": {}
            # Missing dataset_id
        }
        
        is_valid, errors = validate_dataset_structure(dataset)
        assert not is_valid
        assert "Missing required field: dataset_id" in errors

    def test_validate_dataset_structure_missing_plaintiff_field(self):
        """Test validation with missing plaintiff field."""
        dataset = {
            "dataset_id": "C1-P1-D1",
            "case_id": "C1",
            "plaintiff": {
                "plaintiff_id": "P1"
                # Missing other fields
            },
            "defendant": {},
            "case_metadata": {},
            "discovery_data": {}
        }
        
        is_valid, errors = validate_dataset_structure(dataset)
        assert not is_valid
        assert any("Plaintiff missing field" in error for error in errors)

    def test_validate_dataset_structure_missing_defendant_field(self):
        """Test validation with missing defendant field."""
        dataset = {
            "dataset_id": "C1-P1-D1",
            "case_id": "C1",
            "plaintiff": {},
            "defendant": {
                "defendant_id": "D1"
                # Missing other fields
            },
            "case_metadata": {},
            "discovery_data": {}
        }
        
        is_valid, errors = validate_dataset_structure(dataset)
        assert not is_valid
        assert any("Defendant missing field" in error for error in errors)

    def test_validate_dataset_structure_missing_metadata_field(self):
        """Test validation with missing case metadata field."""
        dataset = {
            "dataset_id": "C1-P1-D1",
            "case_id": "C1",
            "plaintiff": {},
            "defendant": {},
            "case_metadata": {
                "property_address": "123 Main St"
                # Missing other fields
            },
            "discovery_data": {}
        }
        
        is_valid, errors = validate_dataset_structure(dataset)
        assert not is_valid
        assert any("Case metadata missing field" in error for error in errors)


class TestGetDatasetSummary:
    """Test dataset summary functionality."""

    def test_get_dataset_summary_empty(self):
        """Test summary with empty dataset list."""
        summary = get_dataset_summary([])
        
        assert summary["total_datasets"] == 0
        assert summary["unique_plaintiffs"] == 0
        assert summary["unique_defendants"] == 0
        assert summary["unique_cases"] == 0

    def test_get_dataset_summary_single_dataset(self):
        """Test summary with single dataset."""
        datasets = [{
            "case_id": "C1",
            "plaintiff": {"plaintiff_id": "P1"},
            "defendant": {"defendant_id": "D1"}
        }]
        
        summary = get_dataset_summary(datasets)
        
        assert summary["total_datasets"] == 1
        assert summary["unique_plaintiffs"] == 1
        assert summary["unique_defendants"] == 1
        assert summary["unique_cases"] == 1

    def test_get_dataset_summary_multiple_datasets(self):
        """Test summary with multiple datasets."""
        datasets = [
            {"case_id": "C1", "plaintiff": {"plaintiff_id": "P1"}, "defendant": {"defendant_id": "D1"}},
            {"case_id": "C1", "plaintiff": {"plaintiff_id": "P1"}, "defendant": {"defendant_id": "D2"}},
            {"case_id": "C1", "plaintiff": {"plaintiff_id": "P2"}, "defendant": {"defendant_id": "D1"}},
            {"case_id": "C2", "plaintiff": {"plaintiff_id": "P3"}, "defendant": {"defendant_id": "D3"}}
        ]
        
        summary = get_dataset_summary(datasets)
        
        assert summary["total_datasets"] == 4
        assert summary["unique_plaintiffs"] == 3  # P1, P2, P3
        assert summary["unique_defendants"] == 3  # D1, D2, D3
        assert summary["unique_cases"] == 2  # C1, C2


class TestDatasetBuildError:
    """Test DatasetBuildError exception."""

    def test_dataset_build_error_message_only(self):
        """Test error with message only."""
        error = DatasetBuildError("Test error")
        assert str(error) == "Test error"
        assert error.errors == []

    def test_dataset_build_error_with_errors(self):
        """Test error with message and error list."""
        errors = ["Error 1", "Error 2"]
        error = DatasetBuildError("Test error", errors)
        assert "Test error" in str(error)
        assert "Error 1" in str(error)
        assert "Error 2" in str(error)
        assert error.errors == errors
