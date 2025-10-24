"""
Tests for Phase 2: Address Builder Module

This module tests the address building functionality with unit idempotency.
"""

import pytest

from src.phase2.address_builder import (
    _unit_already_present,
    build_case_metadata,
    build_property_address_with_unit,
    extract_unit_from_address,
    normalize_address_format,
)


class TestBuildPropertyAddressWithUnit:
    """Test building property addresses with units."""

    def test_add_unit_to_address(self):
        """Test unit added to address without unit."""
        result = build_property_address_with_unit("123 Main St", "5")
        assert result == "123 Main St Unit 5"

    def test_unit_already_present(self):
        """Test idempotency - unit already in address."""
        result = build_property_address_with_unit("123 Main St Unit 5", "5")
        assert result == "123 Main St Unit 5"
        assert result.count("Unit 5") == 1  # Only one occurrence

    def test_no_unit_number(self):
        """Test address unchanged when no unit."""
        result = build_property_address_with_unit("123 Main St", None)
        assert result == "123 Main St"

    def test_empty_unit_number(self):
        """Test address unchanged when empty unit."""
        result = build_property_address_with_unit("123 Main St", "")
        assert result == "123 Main St"

    def test_case_insensitive_unit_check(self):
        """Test unit detection is case-insensitive."""
        result = build_property_address_with_unit("123 Main St unit 5", "5")
        assert "unit 5" in result.lower()
        # Should not add duplicate
        assert result.count("unit") == 1

    def test_different_unit_already_present(self):
        """Test when different unit already present."""
        result = build_property_address_with_unit("123 Main St Unit 3", "5")
        assert result == "123 Main St Unit 3 Unit 5"  # Adds new unit

    def test_unit_in_middle_of_address(self):
        """Test unit detection in middle of address."""
        result = build_property_address_with_unit("123 Unit 5 Main St", "5")
        assert result == "123 Unit 5 Main St"  # Should not add duplicate

    def test_multiple_units_in_address(self):
        """Test address with multiple existing units."""
        result = build_property_address_with_unit("123 Unit 3 Main St Unit 4", "5")
        assert result == "123 Unit 3 Main St Unit 4 Unit 5"  # Adds new unit

    def test_empty_address(self):
        """Test with empty address."""
        result = build_property_address_with_unit("", "5")
        assert result == " Unit 5"

    def test_whitespace_handling(self):
        """Test handling of extra whitespace."""
        result = build_property_address_with_unit("  123 Main St  ", "5")
        assert result == "  123 Main St   Unit 5"


class TestUnitAlreadyPresent:
    """Test unit detection functionality."""

    def test_unit_already_present_true(self):
        """Test unit detection when unit is present."""
        assert _unit_already_present("123 Main St Unit 5", "5") is True

    def test_unit_already_present_case_insensitive(self):
        """Test unit detection is case-insensitive."""
        assert _unit_already_present("123 Main St unit 5", "5") is True
        assert _unit_already_present("123 Main St UNIT 5", "5") is True

    def test_unit_already_present_false(self):
        """Test unit detection when unit not present."""
        assert _unit_already_present("123 Main St", "5") is False

    def test_unit_already_present_partial_match(self):
        """Test unit detection with partial matches."""
        assert _unit_already_present("123 Main St Unit 50", "5") is False
        assert _unit_already_present("123 Main St Unit 15", "5") is False

    def test_unit_already_present_word_boundaries(self):
        """Test unit detection respects word boundaries."""
        assert _unit_already_present("123 Main St Unit 5A", "5") is False
        assert _unit_already_present("123 Main St Unit 5", "5") is True


class TestExtractUnitFromAddress:
    """Test unit extraction from addresses."""

    def test_extract_unit_success(self):
        """Test successful unit extraction."""
        assert extract_unit_from_address("123 Main St Unit 5") == "5"

    def test_extract_unit_case_insensitive(self):
        """Test unit extraction is case-insensitive."""
        assert extract_unit_from_address("123 Main St unit 5") == "5"
        assert extract_unit_from_address("123 Main St UNIT 5") == "5"

    def test_extract_unit_not_found(self):
        """Test unit extraction when no unit present."""
        assert extract_unit_from_address("123 Main St") is None

    def test_extract_unit_multiple_units(self):
        """Test unit extraction with multiple units."""
        # Should return first match
        result = extract_unit_from_address("123 Unit 3 Main St Unit 5")
        assert result in ["3", "5"]  # Either could be returned

    def test_extract_unit_numeric_only(self):
        """Test unit extraction with numeric units."""
        assert extract_unit_from_address("123 Main St Unit 123") == "123"

    def test_extract_unit_empty_address(self):
        """Test unit extraction from empty address."""
        assert extract_unit_from_address("") is None


class TestNormalizeAddressFormat:
    """Test address format normalization."""

    def test_normalize_lowercase_unit(self):
        """Test normalizing lowercase unit to uppercase."""
        result = normalize_address_format("123 Main St unit 5")
        assert result == "123 Main St Unit 5"

    def test_normalize_uppercase_unit(self):
        """Test normalizing uppercase unit (no change)."""
        result = normalize_address_format("123 Main St UNIT 5")
        assert result == "123 Main St Unit 5"

    def test_normalize_mixed_case_unit(self):
        """Test normalizing mixed case unit."""
        result = normalize_address_format("123 Main St Unit 5")
        assert result == "123 Main St Unit 5"

    def test_normalize_no_unit(self):
        """Test normalizing address without unit."""
        result = normalize_address_format("123 Main St")
        assert result == "123 Main St"

    def test_normalize_multiple_units(self):
        """Test normalizing address with multiple units."""
        result = normalize_address_format("123 unit 3 Main St unit 5")
        # Should normalize first occurrence
        assert "Unit 3" in result or "Unit 5" in result

    def test_normalize_empty_address(self):
        """Test normalizing empty address."""
        result = normalize_address_format("")
        assert result == ""


class TestBuildCaseMetadata:
    """Test case metadata building."""

    def test_build_case_metadata_with_unit(self):
        """Test building case metadata with unit."""
        case_info = {
            "property_address": "123 Main St",
            "city": "Los Angeles",
            "state": "CA",
            "zip": "90001",
            "filing_city": "Los Angeles",
            "filing_county": "Los Angeles County"
        }
        plaintiff = {"unit_number": "5"}
        
        result = build_case_metadata(case_info, plaintiff)
        
        assert result["property_address"] == "123 Main St"
        assert result["property_address_with_unit"] == "123 Main St Unit 5"
        assert result["city"] == "Los Angeles"
        assert result["state"] == "CA"
        assert result["zip"] == "90001"
        assert result["filing_city"] == "Los Angeles"
        assert result["filing_county"] == "Los Angeles County"

    def test_build_case_metadata_without_unit(self):
        """Test building case metadata without unit."""
        case_info = {
            "property_address": "123 Main St",
            "city": "Los Angeles",
            "state": "CA",
            "zip": "90001"
        }
        plaintiff = {}  # No unit_number
        
        result = build_case_metadata(case_info, plaintiff)
        
        assert result["property_address"] == "123 Main St"
        assert result["property_address_with_unit"] == "123 Main St"
        assert result["city"] == "Los Angeles"

    def test_build_case_metadata_missing_fields(self):
        """Test building case metadata with missing fields."""
        case_info = {
            "property_address": "123 Main St"
            # Missing other fields
        }
        plaintiff = {"unit_number": "5"}
        
        result = build_case_metadata(case_info, plaintiff)
        
        assert result["property_address"] == "123 Main St"
        assert result["property_address_with_unit"] == "123 Main St Unit 5"
        assert result["city"] == ""  # Default empty string
        assert result["state"] == ""
        assert result["zip"] == ""

    def test_build_case_metadata_unit_already_in_address(self):
        """Test building case metadata when unit already in address."""
        case_info = {
            "property_address": "123 Main St Unit 5",
            "city": "Los Angeles"
        }
        plaintiff = {"unit_number": "5"}
        
        result = build_case_metadata(case_info, plaintiff)
        
        assert result["property_address"] == "123 Main St Unit 5"
        assert result["property_address_with_unit"] == "123 Main St Unit 5"  # No duplicate

    def test_build_case_metadata_none_unit(self):
        """Test building case metadata with None unit."""
        case_info = {
            "property_address": "123 Main St",
            "city": "Los Angeles"
        }
        plaintiff = {"unit_number": None}
        
        result = build_case_metadata(case_info, plaintiff)
        
        assert result["property_address"] == "123 Main St"
        assert result["property_address_with_unit"] == "123 Main St"
