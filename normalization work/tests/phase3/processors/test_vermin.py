"""
Tests for Phase 3: Vermin Flag Processor

This module tests the vermin flag processor.
"""

import pytest
from src.phase3.processors.vermin import VerminProcessor
from tests.fixtures.phase3_samples import FULL_VERMIN_DISCOVERY, EMPTY_DISCOVERY


class TestVerminProcessor:
    """Test the VerminProcessor class."""

    def test_processor_initialization(self):
        """Test processor can be initialized."""
        processor = VerminProcessor()
        assert processor.category_name == "vermin"
        assert processor.aggregate_flag_name == "HasVermin"

    def test_flag_mappings_completeness(self):
        """Test all expected vermin flags are mapped."""
        processor = VerminProcessor()
        mappings = processor.flag_mappings
        
        expected_flags = [
            "HasRatsMice", "HasBedbugs", "HasSkunks", "HasBats",
            "HasRaccoons", "HasPigeons", "HasOpossums"
        ]
        
        for flag in expected_flags:
            assert any(flag in mapping for mapping in mappings.values())

    def test_process_all_vermin_selected(self):
        """Test processing when all vermin types are selected."""
        processor = VerminProcessor()
        discovery_data = FULL_VERMIN_DISCOVERY
        
        flags = processor.process(discovery_data)
        
        # All individual flags should be True
        assert flags["HasRatsMice"] is True
        assert flags["HasBedbugs"] is True
        assert flags["HasSkunks"] is True
        assert flags["HasBats"] is True
        assert flags["HasRaccoons"] is True
        assert flags["HasPigeons"] is True
        assert flags["HasOpossums"] is True
        
        # Aggregate flag should be True
        assert flags["HasVermin"] is True
        
        # Should have 8 flags total (7 individual + 1 aggregate)
        assert len(flags) == 8

    def test_process_no_vermin_selected(self):
        """Test processing when no vermin types are selected."""
        processor = VerminProcessor()
        discovery_data = {"vermin": []}
        
        flags = processor.process(discovery_data)
        
        # All flags should be False
        assert all(not flag for flag in flags.values())
        assert flags["HasVermin"] is False

    def test_process_partial_vermin_selected(self):
        """Test processing when some vermin types are selected."""
        processor = VerminProcessor()
        discovery_data = {"vermin": ["Rats/Mice", "Bedbugs"]}
        
        flags = processor.process(discovery_data)
        
        # Selected flags should be True
        assert flags["HasRatsMice"] is True
        assert flags["HasBedbugs"] is True
        
        # Unselected flags should be False
        assert flags["HasSkunks"] is False
        assert flags["HasBats"] is False
        assert flags["HasRaccoons"] is False
        assert flags["HasPigeons"] is False
        assert flags["HasOpossums"] is False
        
        # Aggregate flag should be True (some selected)
        assert flags["HasVermin"] is True

    def test_process_case_insensitive_matching(self):
        """Test case-insensitive matching works."""
        processor = VerminProcessor()
        discovery_data = {"vermin": ["rats/mice", "BEDBUGS", "SKUNKS"]}
        
        flags = processor.process(discovery_data)
        
        assert flags["HasRatsMice"] is True
        assert flags["HasBedbugs"] is True
        assert flags["HasSkunks"] is True
        assert flags["HasVermin"] is True

    def test_process_missing_category(self):
        """Test processing when vermin category is missing."""
        processor = VerminProcessor()
        discovery_data = {}
        
        flags = processor.process(discovery_data)
        
        # All flags should be False
        assert all(not flag for flag in flags.values())
        assert flags["HasVermin"] is False

    def test_process_invalid_data_type(self):
        """Test processing with invalid data type."""
        processor = VerminProcessor()
        discovery_data = {"vermin": "not a list"}
        
        # Should handle gracefully
        flags = processor.process(discovery_data)
        
        # All flags should be False
        assert all(not flag for flag in flags.values())
        assert flags["HasVermin"] is False

    def test_get_expected_flags(self):
        """Test getting expected flags list."""
        processor = VerminProcessor()
        expected_flags = processor.get_expected_flags()
        
        assert len(expected_flags) == 8  # 7 individual + 1 aggregate
        assert "HasRatsMice" in expected_flags
        assert "HasBedbugs" in expected_flags
        assert "HasSkunks" in expected_flags
        assert "HasBats" in expected_flags
        assert "HasRaccoons" in expected_flags
        assert "HasPigeons" in expected_flags
        assert "HasOpossums" in expected_flags
        assert "HasVermin" in expected_flags

    def test_processor_info(self):
        """Test processor info generation."""
        processor = VerminProcessor()
        info = processor.get_processor_info()
        
        assert info["category_name"] == "vermin"
        assert info["individual_flags"] == 7
        assert info["aggregate_flag"] is True
        assert info["total_flags"] == 8
        assert len(info["flag_names"]) == 8

    def test_validate_discovery_data(self):
        """Test discovery data validation."""
        processor = VerminProcessor()
        
        # Valid data
        valid_data = {"vermin": ["Rats/Mice", "Bedbugs"]}
        assert processor.validate_discovery_data(valid_data) is True
        
        # Missing category
        missing_data = {"other": ["value"]}
        assert processor.validate_discovery_data(missing_data) is True
        
        # Invalid data type
        invalid_data = {"vermin": "not a list"}
        assert processor.validate_discovery_data(invalid_data) is False
        
        # Not a dict
        assert processor.validate_discovery_data("not a dict") is False
