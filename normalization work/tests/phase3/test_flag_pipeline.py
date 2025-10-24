"""
Tests for Phase 3: Flag Processor Pipeline

This module tests the flag processor pipeline.
"""

import pytest
from src.phase3.flag_pipeline import FlagProcessorPipeline
from tests.fixtures.phase3_samples import (
    SAMPLE_DATASET, SAMPLE_DATASET_COLLECTION, PARTIAL_DISCOVERY, EMPTY_DISCOVERY
)


class TestFlagProcessorPipeline:
    """Test the FlagProcessorPipeline class."""

    def test_pipeline_initialization(self):
        """Test pipeline can be initialized."""
        pipeline = FlagProcessorPipeline()
        assert len(pipeline.processors) > 0
        assert pipeline.processors is not None

    def test_process_dataset_basic(self):
        """Test processing a single dataset."""
        pipeline = FlagProcessorPipeline()
        dataset = SAMPLE_DATASET
        
        result = pipeline.process_dataset(dataset)
        
        # Should have flags
        assert "flags" in result
        assert isinstance(result["flags"], dict)
        
        # Should preserve original dataset structure
        assert result["dataset_id"] == dataset["dataset_id"]
        assert result["plaintiff"] == dataset["plaintiff"]
        assert result["defendant"] == dataset["defendant"]
        assert result["case_metadata"] == dataset["case_metadata"]
        assert result["discovery_data"] == dataset["discovery_data"]

    def test_process_dataset_with_flags(self):
        """Test processing generates expected flags."""
        pipeline = FlagProcessorPipeline()
        dataset = SAMPLE_DATASET
        
        result = pipeline.process_dataset(dataset)
        flags = result["flags"]
        
        # Should have some flags
        assert len(flags) > 0
        
        # Should have vermin flags (from partial discovery)
        assert "HasRatsMice" in flags
        assert "HasBedbugs" in flags
        assert "HasVermin" in flags
        
        # Should have insect flags
        assert "HasAnts" in flags
        assert "HasRoaches" in flags
        assert "HasInsects" in flags
        
        # Should have plumbing flags
        assert "HasToilet" in flags
        assert "HasLeaks" in flags
        assert "HasPlumbingIssues" in flags
        
        # Should have direct boolean flags
        assert "HasInjury" in flags
        assert flags["HasInjury"] is True

    def test_process_dataset_empty_discovery(self):
        """Test processing with empty discovery data."""
        pipeline = FlagProcessorPipeline()
        dataset = {
            **SAMPLE_DATASET,
            "discovery_data": EMPTY_DISCOVERY
        }
        
        result = pipeline.process_dataset(dataset)
        flags = result["flags"]
        
        # All flags should be False
        assert all(not flag for flag in flags.values())

    def test_process_all_datasets(self):
        """Test processing multiple datasets."""
        pipeline = FlagProcessorPipeline()
        collection = SAMPLE_DATASET_COLLECTION
        
        result = pipeline.process_all_datasets(collection)
        
        # Should have datasets
        assert "datasets" in result
        assert len(result["datasets"]) == 2
        
        # All datasets should have flags
        for dataset in result["datasets"]:
            assert "flags" in dataset
            assert isinstance(dataset["flags"], dict)
        
        # Should have metadata
        assert "metadata" in result
        assert "flags_generated" in result["metadata"]
        assert "processors_used" in result["metadata"]

    def test_process_all_datasets_empty_collection(self):
        """Test processing empty dataset collection."""
        pipeline = FlagProcessorPipeline()
        collection = {"datasets": [], "metadata": {}}
        
        result = pipeline.process_all_datasets(collection)
        
        assert "datasets" in result
        assert len(result["datasets"]) == 0
        assert "metadata" in result

    def test_get_processor_info(self):
        """Test getting processor information."""
        pipeline = FlagProcessorPipeline()
        info = pipeline.get_processor_info()
        
        assert isinstance(info, list)
        assert len(info) > 0
        
        # Each processor should have required info
        for processor_info in info:
            assert "category_name" in processor_info
            assert "individual_flags" in processor_info
            assert "aggregate_flag" in processor_info
            assert "total_flags" in processor_info
            assert "flag_names" in processor_info

    def test_get_total_expected_flags(self):
        """Test getting total expected flags count."""
        pipeline = FlagProcessorPipeline()
        total_flags = pipeline.get_total_expected_flags()
        
        assert isinstance(total_flags, int)
        assert total_flags > 0

    def test_validate_pipeline(self):
        """Test pipeline validation."""
        pipeline = FlagProcessorPipeline()
        validation = pipeline.validate_pipeline()
        
        assert "valid" in validation
        assert "errors" in validation
        assert "warnings" in validation
        assert "total_processors" in validation
        assert "total_expected_flags" in validation
        
        # Should be valid
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0

    def test_process_dataset_preserves_original_data(self):
        """Test that processing preserves all original data."""
        pipeline = FlagProcessorPipeline()
        original_dataset = SAMPLE_DATASET.copy()
        
        result = pipeline.process_dataset(original_dataset)
        
        # All original fields should be preserved
        for key, value in original_dataset.items():
            if key != "flags":  # flags is new
                assert result[key] == value

    def test_process_dataset_error_handling(self):
        """Test that pipeline handles processor errors gracefully."""
        pipeline = FlagProcessorPipeline()
        
        # Create dataset with invalid discovery data
        dataset = {
            **SAMPLE_DATASET,
            "discovery_data": {
                "vermin": "invalid data type",  # Should cause error
                "insects": ["Ants"],  # Should work fine
                "has_injury": True  # Should work fine
            }
        }
        
        # Should not raise exception
        result = pipeline.process_dataset(dataset)
        
        # Should still have flags (from working processors)
        assert "flags" in result
        assert len(result["flags"]) > 0

    def test_flag_count_verification(self):
        """Test that pipeline generates expected number of flags."""
        pipeline = FlagProcessorPipeline()
        dataset = SAMPLE_DATASET
        
        result = pipeline.process_dataset(dataset)
        flags = result["flags"]
        
        # Should have reasonable number of flags
        assert len(flags) > 50  # Should have many flags
        assert len(flags) < 200  # But not too many

    def test_aggregate_flags_work_correctly(self):
        """Test that aggregate flags are calculated correctly."""
        pipeline = FlagProcessorPipeline()
        dataset = SAMPLE_DATASET
        
        result = pipeline.process_dataset(dataset)
        flags = result["flags"]
        
        # Test vermin aggregate
        if "HasRatsMice" in flags and flags["HasRatsMice"]:
            assert flags["HasVermin"] is True
        
        # Test insect aggregate
        if "HasAnts" in flags and flags["HasAnts"]:
            assert flags["HasInsects"] is True
        
        # Test plumbing aggregate
        if "HasToilet" in flags and flags["HasToilet"]:
            assert flags["HasPlumbingIssues"] is True

    def test_case_insensitive_matching(self):
        """Test that flag processing is case-insensitive."""
        pipeline = FlagProcessorPipeline()
        dataset = {
            **SAMPLE_DATASET,
            "discovery_data": {
                "vermin": ["rats/mice", "BEDBUGS"],  # Mixed case
                "insects": ["ants", "ROACHES"],  # Mixed case
                "has_injury": True
            }
        }
        
        result = pipeline.process_dataset(dataset)
        flags = result["flags"]
        
        # Should match despite case differences
        assert flags["HasRatsMice"] is True
        assert flags["HasBedbugs"] is True
        assert flags["HasAnts"] is True
        assert flags["HasRoaches"] is True
