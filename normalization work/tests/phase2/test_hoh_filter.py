"""
Tests for Phase 2: HoH Filter Module

This module tests the Head of Household filtering functionality.
"""

import pytest

from src.phase2.hoh_filter import (
    count_hoh_plaintiffs,
    count_non_hoh_plaintiffs,
    filter_heads_of_household,
    get_non_hoh_plaintiffs,
    validate_hoh_plaintiffs,
)


class TestFilterHeadsOfHousehold:
    """Test filtering HoH plaintiffs."""

    def test_filter_only_hoh(self):
        """Test filtering returns only HoH plaintiffs."""
        plaintiffs = [
            {"is_head_of_household": True, "discovery": {}},
            {"is_head_of_household": False},
            {"is_head_of_household": True, "discovery": {}}
        ]
        result = filter_heads_of_household(plaintiffs)
        assert len(result) == 2
        assert all(p["is_head_of_household"] for p in result)

    def test_filter_requires_discovery(self):
        """Test HoH without discovery excluded."""
        plaintiffs = [
            {"is_head_of_household": True, "discovery": {}},
            {"is_head_of_household": True}  # No discovery
        ]
        result = filter_heads_of_household(plaintiffs)
        assert len(result) == 1

    def test_filter_empty_list(self):
        """Test filtering empty plaintiff list."""
        result = filter_heads_of_household([])
        assert result == []

    def test_filter_no_hoh(self):
        """Test filtering when no HoH plaintiffs."""
        plaintiffs = [
            {"is_head_of_household": False},
            {"is_head_of_household": False}
        ]
        result = filter_heads_of_household(plaintiffs)
        assert result == []

    def test_filter_preserves_data(self):
        """Test filtering preserves plaintiff data."""
        plaintiffs = [
            {
                "plaintiff_id": "P1",
                "first_name": "Clark",
                "is_head_of_household": True,
                "discovery": {"vermin": ["Rats"]}
            }
        ]
        result = filter_heads_of_household(plaintiffs)
        assert len(result) == 1
        assert result[0]["plaintiff_id"] == "P1"
        assert result[0]["first_name"] == "Clark"
        assert result[0]["discovery"]["vermin"] == ["Rats"]


class TestGetNonHoHPlaintiffs:
    """Test getting non-HoH plaintiffs."""

    def test_get_non_hoh_plaintiffs(self):
        """Test non-HoH plaintiff extraction."""
        plaintiffs = [
            {"is_head_of_household": True, "discovery": {}},
            {"is_head_of_household": False, "first_name": "Bruce"}
        ]
        result = get_non_hoh_plaintiffs(plaintiffs)
        assert len(result) == 1
        assert result[0]["first_name"] == "Bruce"

    def test_get_non_hoh_empty(self):
        """Test getting non-HoH when none exist."""
        plaintiffs = [
            {"is_head_of_household": True, "discovery": {}},
            {"is_head_of_household": True, "discovery": {}}
        ]
        result = get_non_hoh_plaintiffs(plaintiffs)
        assert result == []

    def test_get_non_hoh_all_non_hoh(self):
        """Test getting non-HoH when all are non-HoH."""
        plaintiffs = [
            {"is_head_of_household": False, "first_name": "Bruce"},
            {"is_head_of_household": False, "first_name": "Diana"}
        ]
        result = get_non_hoh_plaintiffs(plaintiffs)
        assert len(result) == 2
        assert all(not p["is_head_of_household"] for p in result)


class TestCountFunctions:
    """Test counting functions."""

    def test_count_hoh_plaintiffs(self):
        """Test counting HoH plaintiffs."""
        plaintiffs = [
            {"is_head_of_household": True, "discovery": {}},
            {"is_head_of_household": False},
            {"is_head_of_household": True, "discovery": {}}
        ]
        count = count_hoh_plaintiffs(plaintiffs)
        assert count == 2

    def test_count_non_hoh_plaintiffs(self):
        """Test counting non-HoH plaintiffs."""
        plaintiffs = [
            {"is_head_of_household": True, "discovery": {}},
            {"is_head_of_household": False},
            {"is_head_of_household": True, "discovery": {}}
        ]
        count = count_non_hoh_plaintiffs(plaintiffs)
        assert count == 1

    def test_count_empty_list(self):
        """Test counting with empty list."""
        assert count_hoh_plaintiffs([]) == 0
        assert count_non_hoh_plaintiffs([]) == 0


class TestValidateHoHPlaintiffs:
    """Test HoH plaintiff validation."""

    def test_validate_valid_hoh(self):
        """Test validation with valid HoH plaintiffs."""
        plaintiffs = [
            {
                "is_head_of_household": True,
                "plaintiff_id": "P1",
                "discovery": {"vermin": []}
            }
        ]
        is_valid, errors = validate_hoh_plaintiffs(plaintiffs)
        assert is_valid
        assert errors == []

    def test_validate_no_hoh(self):
        """Test validation with no HoH plaintiffs."""
        plaintiffs = [
            {"is_head_of_household": False}
        ]
        is_valid, errors = validate_hoh_plaintiffs(plaintiffs)
        assert not is_valid
        assert "No Head of Household plaintiffs found" in errors

    def test_validate_missing_plaintiff_id(self):
        """Test validation with missing plaintiff_id."""
        plaintiffs = [
            {
                "is_head_of_household": True,
                "discovery": {}
                # Missing plaintiff_id
            }
        ]
        is_valid, errors = validate_hoh_plaintiffs(plaintiffs)
        assert not is_valid
        assert any("missing plaintiff_id" in error for error in errors)

    def test_validate_missing_discovery(self):
        """Test validation with missing discovery."""
        plaintiffs = [
            {
                "is_head_of_household": True,
                "plaintiff_id": "P1"
                # Missing discovery
            }
        ]
        is_valid, errors = validate_hoh_plaintiffs(plaintiffs)
        assert not is_valid
        assert any("missing discovery data" in error for error in errors)

    def test_validate_invalid_discovery_type(self):
        """Test validation with invalid discovery type."""
        plaintiffs = [
            {
                "is_head_of_household": True,
                "plaintiff_id": "P1",
                "discovery": "not a dict"  # Should be dict
            }
        ]
        is_valid, errors = validate_hoh_plaintiffs(plaintiffs)
        assert not is_valid
        assert any("discovery must be dictionary" in error for error in errors)

    def test_validate_multiple_errors(self):
        """Test validation with multiple errors."""
        plaintiffs = [
            {
                "is_head_of_household": True,
                # Missing plaintiff_id
                "discovery": "not a dict"  # Wrong type
            },
            {
                "is_head_of_household": True,
                "plaintiff_id": "P2"
                # Missing discovery
            }
        ]
        is_valid, errors = validate_hoh_plaintiffs(plaintiffs)
        assert not is_valid
        assert len(errors) >= 3  # Multiple errors expected
