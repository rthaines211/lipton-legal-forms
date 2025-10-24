"""
Tests for Phase 3: Base Flag Processor

This module tests the base flag processor interface.
"""

import pytest
from src.phase3.base_processor import BaseFlagProcessor


class TestBaseFlagProcessor:
    """Test the abstract base processor interface."""

    def test_abstract_class_cannot_be_instantiated(self):
        """Test that BaseFlagProcessor cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseFlagProcessor()

    def test_abstract_methods_must_be_implemented(self):
        """Test that subclasses must implement abstract methods."""
        
        class IncompleteProcessor(BaseFlagProcessor):
            pass
        
        with pytest.raises(TypeError):
            IncompleteProcessor()

    def test_concrete_processor_can_be_instantiated(self):
        """Test that concrete processors can be instantiated."""
        
        class ConcreteProcessor(BaseFlagProcessor):
            @property
            def category_name(self) -> str:
                return "test"
            
            @property
            def flag_mappings(self) -> dict:
                return {"test": "HasTest"}
        
        processor = ConcreteProcessor()
        assert processor.category_name == "test"
        assert processor.flag_mappings == {"test": "HasTest"}

    def test_aggregate_flag_name_defaults_to_none(self):
        """Test that aggregate_flag_name defaults to None."""
        
        class TestProcessor(BaseFlagProcessor):
            @property
            def category_name(self) -> str:
                return "test"
            
            @property
            def flag_mappings(self) -> dict:
                return {"test": "HasTest"}
        
        processor = TestProcessor()
        assert processor.aggregate_flag_name is None

    def test_get_expected_flags_includes_aggregate(self):
        """Test that get_expected_flags includes aggregate flag when present."""
        
        class TestProcessor(BaseFlagProcessor):
            @property
            def category_name(self) -> str:
                return "test"
            
            @property
            def flag_mappings(self) -> dict:
                return {"test1": "HasTest1", "test2": "HasTest2"}
            
            @property
            def aggregate_flag_name(self) -> str:
                return "HasTest"
        
        processor = TestProcessor()
        expected_flags = processor.get_expected_flags()
        
        assert "HasTest1" in expected_flags
        assert "HasTest2" in expected_flags
        assert "HasTest" in expected_flags
        assert len(expected_flags) == 3

    def test_get_expected_flags_excludes_aggregate_when_none(self):
        """Test that get_expected_flags excludes aggregate when None."""
        
        class TestProcessor(BaseFlagProcessor):
            @property
            def category_name(self) -> str:
                return "test"
            
            @property
            def flag_mappings(self) -> dict:
                return {"test1": "HasTest1", "test2": "HasTest2"}
        
        processor = TestProcessor()
        expected_flags = processor.get_expected_flags()
        
        assert "HasTest1" in expected_flags
        assert "HasTest2" in expected_flags
        assert len(expected_flags) == 2

    def test_validate_discovery_data_valid(self):
        """Test validation with valid discovery data."""
        
        class TestProcessor(BaseFlagProcessor):
            @property
            def category_name(self) -> str:
                return "test"
            
            @property
            def flag_mappings(self) -> dict:
                return {"test": "HasTest"}
        
        processor = TestProcessor()
        
        # Valid data
        valid_data = {"test": ["value1", "value2"]}
        assert processor.validate_discovery_data(valid_data) is True
        
        # Missing category (OK)
        missing_data = {"other": ["value"]}
        assert processor.validate_discovery_data(missing_data) is True

    def test_validate_discovery_data_invalid(self):
        """Test validation with invalid discovery data."""
        
        class TestProcessor(BaseFlagProcessor):
            @property
            def category_name(self) -> str:
                return "test"
            
            @property
            def flag_mappings(self) -> dict:
                return {"test": "HasTest"}
        
        processor = TestProcessor()
        
        # Invalid data types
        assert processor.validate_discovery_data("not a dict") is False
        assert processor.validate_discovery_data({"test": "not a list"}) is False

    def test_get_processor_info(self):
        """Test processor info generation."""
        
        class TestProcessor(BaseFlagProcessor):
            @property
            def category_name(self) -> str:
                return "test"
            
            @property
            def flag_mappings(self) -> dict:
                return {"test1": "HasTest1", "test2": "HasTest2"}
            
            @property
            def aggregate_flag_name(self) -> str:
                return "HasTest"
        
        processor = TestProcessor()
        info = processor.get_processor_info()
        
        assert info["category_name"] == "test"
        assert info["individual_flags"] == 2
        assert info["aggregate_flag"] is True
        assert info["total_flags"] == 3
        assert "HasTest1" in info["flag_names"]
        assert "HasTest2" in info["flag_names"]
        assert "HasTest" in info["flag_names"]
