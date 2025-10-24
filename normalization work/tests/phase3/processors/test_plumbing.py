"""
Tests for Phase 3: Plumbing Flag Processor

This module tests the plumbing flag processor with complex aggregate logic.
"""

import pytest
from src.phase3.processors.plumbing import PlumbingProcessor
from tests.fixtures.phase3_samples import FULL_PLUMBING_DISCOVERY, EMPTY_DISCOVERY


class TestPlumbingProcessor:
    """Test the PlumbingProcessor class."""

    def test_processor_initialization(self):
        """Test processor can be initialized."""
        processor = PlumbingProcessor()
        assert processor.category_name == "plumbing"
        assert processor.aggregate_flag_name == "HasPlumbingIssues"

    def test_flag_mappings_completeness(self):
        """Test all expected plumbing flags are mapped."""
        processor = PlumbingProcessor()
        mappings = processor.flag_mappings
        
        expected_flags = [
            "HasToilet", "HasShower", "HasBath", "HasFixtures", "HasLeaks",
            "HasInsufficientWaterPressure", "HasNoHotWater", "HasNoColdWater",
            "HasSewageComingOut", "HasCloggedToilets", "HasCloggedBath",
            "HasCloggedSinks", "HasCloggedShower", "HasNoCleanWaterSupply", "HasUnsanitaryWater"
        ]
        
        for flag in expected_flags:
            assert any(flag in mapping for mapping in mappings.values())

    def test_process_all_plumbing_selected(self):
        """Test processing when all plumbing types are selected."""
        processor = PlumbingProcessor()
        discovery_data = FULL_PLUMBING_DISCOVERY
        
        flags = processor.process(discovery_data)
        
        # All individual flags should be True
        assert flags["HasToilet"] is True
        assert flags["HasShower"] is True
        assert flags["HasBath"] is True
        assert flags["HasFixtures"] is True
        assert flags["HasLeaks"] is True
        assert flags["HasInsufficientWaterPressure"] is True
        assert flags["HasNoHotWater"] is True
        assert flags["HasNoColdWater"] is True
        assert flags["HasSewageComingOut"] is True
        assert flags["HasCloggedToilets"] is True
        assert flags["HasCloggedBath"] is True
        assert flags["HasCloggedSinks"] is True
        assert flags["HasCloggedShower"] is True
        assert flags["HasNoCleanWaterSupply"] is True
        assert flags["HasUnsanitaryWater"] is True
        
        # Aggregate flags should be True
        assert flags["HasPlumbingIssues"] is True
        assert flags["HasClogs"] is True  # Custom aggregate
        
        # Should have 17 flags total (15 individual + 2 aggregates)
        assert len(flags) == 17

    def test_process_no_plumbing_selected(self):
        """Test processing when no plumbing types are selected."""
        processor = PlumbingProcessor()
        discovery_data = {"plumbing": []}
        
        flags = processor.process(discovery_data)
        
        # All flags should be False
        assert all(not flag for flag in flags.values())
        assert flags["HasPlumbingIssues"] is False
        assert flags["HasClogs"] is False

    def test_process_partial_plumbing_selected(self):
        """Test processing when some plumbing types are selected."""
        processor = PlumbingProcessor()
        discovery_data = {"plumbing": ["Toilet", "Leaks"]}
        
        flags = processor.process(discovery_data)
        
        # Selected flags should be True
        assert flags["HasToilet"] is True
        assert flags["HasLeaks"] is True
        
        # Unselected flags should be False
        assert flags["HasShower"] is False
        assert flags["HasBath"] is False
        assert flags["HasFixtures"] is False
        
        # Aggregate flags
        assert flags["HasPlumbingIssues"] is True  # Some selected
        assert flags["HasClogs"] is False  # No clogs selected

    def test_process_clogs_aggregate(self):
        """Test the custom HasClogs aggregate flag."""
        processor = PlumbingProcessor()
        
        # Test with clogged toilets only
        discovery_data = {"plumbing": ["Clogged toilets"]}
        flags = processor.process(discovery_data)
        assert flags["HasCloggedToilets"] is True
        assert flags["HasClogs"] is True
        
        # Test with multiple clogs
        discovery_data = {"plumbing": ["Clogged toilets", "Clogged sinks", "Clogged bath"]}
        flags = processor.process(discovery_data)
        assert flags["HasCloggedToilets"] is True
        assert flags["HasCloggedSinks"] is True
        assert flags["HasCloggedBath"] is True
        assert flags["HasClogs"] is True
        
        # Test with no clogs
        discovery_data = {"plumbing": ["Toilet", "Leaks"]}
        flags = processor.process(discovery_data)
        assert flags["HasClogs"] is False

    def test_process_case_insensitive_matching(self):
        """Test case-insensitive matching works."""
        processor = PlumbingProcessor()
        discovery_data = {"plumbing": ["toilet", "LEAKS", "clogged toilets"]}
        
        flags = processor.process(discovery_data)
        
        assert flags["HasToilet"] is True
        assert flags["HasLeaks"] is True
        assert flags["HasCloggedToilets"] is True
        assert flags["HasClogs"] is True

    def test_process_missing_category(self):
        """Test processing when plumbing category is missing."""
        processor = PlumbingProcessor()
        discovery_data = {}
        
        flags = processor.process(discovery_data)
        
        # All flags should be False
        assert all(not flag for flag in flags.values())
        assert flags["HasPlumbingIssues"] is False
        assert flags["HasClogs"] is False

    def test_get_expected_flags(self):
        """Test getting expected flags list."""
        processor = PlumbingProcessor()
        expected_flags = processor.get_expected_flags()
        
        assert len(expected_flags) == 16  # 15 individual + 1 aggregate (HasClogs not included in base)
        assert "HasToilet" in expected_flags
        assert "HasShower" in expected_flags
        assert "HasBath" in expected_flags
        assert "HasPlumbingIssues" in expected_flags

    def test_processor_info(self):
        """Test processor info generation."""
        processor = PlumbingProcessor()
        info = processor.get_processor_info()
        
        assert info["category_name"] == "plumbing"
        assert info["individual_flags"] == 15
        assert info["aggregate_flag"] is True
        assert info["total_flags"] == 16  # Base aggregate only

    def test_validate_discovery_data(self):
        """Test discovery data validation."""
        processor = PlumbingProcessor()
        
        # Valid data
        valid_data = {"plumbing": ["Toilet", "Leaks"]}
        assert processor.validate_discovery_data(valid_data) is True
        
        # Missing category
        missing_data = {"other": ["value"]}
        assert processor.validate_discovery_data(missing_data) is True
        
        # Invalid data type
        invalid_data = {"plumbing": "not a list"}
        assert processor.validate_discovery_data(invalid_data) is False
        
        # Not a dict
        assert processor.validate_discovery_data("not a dict") is False
