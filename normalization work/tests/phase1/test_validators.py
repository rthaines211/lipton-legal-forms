"""
Test suite for Phase 1: Validators Module

Tests the validation functionality for case info, plaintiffs, defendants,
and discovery data.
"""

import pytest
from typing import Any

from src.phase1.validators import (
    validate_case_info,
    validate_plaintiff,
    validate_defendant,
    validate_discovery,
    validate_normalized_data,
)


class TestValidateCaseInfo:
    """Test the validate_case_info function."""

    def test_validate_valid_case_info(self):
        """Test validating valid case info."""
        case_info = {
            "case_id": "test-123",
            "property_address": "123 Main St",
            "city": "Los Angeles",
            "state": "California",
            "zip": "90001",
            "filing_city": "Los Angeles",
            "filing_county": "Los Angeles County"
        }
        
        is_valid, errors = validate_case_info(case_info)
        
        assert is_valid is True
        assert errors == []

    def test_validate_case_info_missing_required_fields(self):
        """Test validating case info with missing required fields."""
        case_info = {
            "case_id": "test-123",
            "property_address": "123 Main St",
            # Missing city, state, zip
        }
        
        is_valid, errors = validate_case_info(case_info)
        
        assert is_valid is False
        assert "Missing required field: city" in errors
        assert "Missing required field: state" in errors
        assert "Missing required field: zip" in errors

    def test_validate_case_info_empty_required_fields(self):
        """Test validating case info with empty required fields."""
        case_info = {
            "case_id": "test-123",
            "property_address": "",  # Empty
            "city": "Los Angeles",
            "state": "California",
            "zip": "90001"
        }
        
        is_valid, errors = validate_case_info(case_info)
        
        assert is_valid is False
        assert "Required field is empty: property_address" in errors

    def test_validate_case_info_wrong_data_types(self):
        """Test validating case info with wrong data types."""
        case_info = {
            "case_id": 123,  # Should be string
            "property_address": "123 Main St",
            "city": "Los Angeles",
            "state": "California",
            "zip": 90001,  # Should be string
            "filing_city": "Los Angeles",
            "filing_county": "Los Angeles County"
        }
        
        is_valid, errors = validate_case_info(case_info)
        
        assert is_valid is False
        assert "Field must be string: case_id" in errors
        assert "Field must be string: zip" in errors

    def test_validate_case_info_optional_fields(self):
        """Test validating case info with optional fields."""
        case_info = {
            "property_address": "123 Main St",
            "city": "Los Angeles",
            "state": "California",
            "zip": "90001",
            "case_id": None,  # Optional field can be None
            "filing_city": None,  # Optional field can be None
        }
        
        is_valid, errors = validate_case_info(case_info)
        
        assert is_valid is True
        assert errors == []

    def test_validate_case_info_optional_fields_wrong_type(self):
        """Test validating case info with optional fields having wrong types."""
        case_info = {
            "property_address": "123 Main St",
            "city": "Los Angeles",
            "state": "California",
            "zip": "90001",
            "case_id": 123,  # Should be string or None
        }
        
        is_valid, errors = validate_case_info(case_info)
        
        assert is_valid is False
        assert "Field must be string: case_id" in errors


class TestValidatePlaintiff:
    """Test the validate_plaintiff function."""

    def test_validate_valid_plaintiff(self):
        """Test validating valid plaintiff."""
        plaintiff = {
            "plaintiff_id": "P1",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
            "plaintiff_type": "Individual",
            "age_category": "Adult",
            "is_head_of_household": True,
            "unit_number": "101",
            "item_number": 1,
            "discovery": {}
        }
        
        is_valid, errors = validate_plaintiff(plaintiff)
        
        assert is_valid is True
        assert errors == []

    def test_validate_plaintiff_missing_required_fields(self):
        """Test validating plaintiff with missing required fields."""
        plaintiff = {
            "plaintiff_id": "P1",
            # Missing first_name, last_name, full_name
            "is_head_of_household": True,
            "item_number": 1
        }
        
        is_valid, errors = validate_plaintiff(plaintiff)
        
        assert is_valid is False
        assert "Plaintiff missing required field: first_name" in errors
        assert "Plaintiff missing required field: last_name" in errors
        assert "Plaintiff missing required field: full_name" in errors

    def test_validate_plaintiff_no_names(self):
        """Test validating plaintiff with no names."""
        plaintiff = {
            "plaintiff_id": "P1",
            "first_name": "",
            "last_name": "",
            "full_name": "",
            "is_head_of_household": True,
            "item_number": 1
        }
        
        is_valid, errors = validate_plaintiff(plaintiff)
        
        assert is_valid is False
        assert "Plaintiff must have at least first_name or last_name" in errors

    def test_validate_plaintiff_invalid_boolean_fields(self):
        """Test validating plaintiff with invalid boolean fields."""
        plaintiff = {
            "plaintiff_id": "P1",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
            "is_head_of_household": "true",  # Should be boolean
            "item_number": 1
        }
        
        is_valid, errors = validate_plaintiff(plaintiff)
        
        assert is_valid is False
        assert "is_head_of_household must be boolean" in errors

    def test_validate_plaintiff_invalid_item_number(self):
        """Test validating plaintiff with invalid item number."""
        plaintiff = {
            "plaintiff_id": "P1",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
            "item_number": 0,  # Should be positive
        }
        
        is_valid, errors = validate_plaintiff(plaintiff)
        
        assert is_valid is False
        assert "item_number must be positive integer" in errors

    def test_validate_plaintiff_invalid_discovery(self):
        """Test validating plaintiff with invalid discovery."""
        plaintiff = {
            "plaintiff_id": "P1",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
            "discovery": "not a dict",  # Should be dictionary
        }
        
        is_valid, errors = validate_plaintiff(plaintiff)
        
        assert is_valid is False
        assert "discovery must be dictionary" in errors

    def test_validate_plaintiff_minimal_valid(self):
        """Test validating plaintiff with minimal valid data."""
        plaintiff = {
            "plaintiff_id": "P1",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
        }
        
        is_valid, errors = validate_plaintiff(plaintiff)
        
        assert is_valid is True
        assert errors == []


class TestValidateDefendant:
    """Test the validate_defendant function."""

    def test_validate_valid_defendant(self):
        """Test validating valid defendant."""
        defendant = {
            "defendant_id": "D1",
            "first_name": "Evil",
            "last_name": "Corp",
            "full_name": "Evil Corp",
            "entity_type": "Corporation",
            "role": "Owner",
            "item_number": 1
        }
        
        is_valid, errors = validate_defendant(defendant)
        
        assert is_valid is True
        assert errors == []

    def test_validate_defendant_missing_required_fields(self):
        """Test validating defendant with missing required fields."""
        defendant = {
            "defendant_id": "D1",
            # Missing first_name, last_name, full_name
            "entity_type": "Corporation",
            "item_number": 1
        }
        
        is_valid, errors = validate_defendant(defendant)
        
        assert is_valid is False
        assert "Defendant missing required field: first_name" in errors
        assert "Defendant missing required field: last_name" in errors
        assert "Defendant missing required field: full_name" in errors

    def test_validate_defendant_no_names(self):
        """Test validating defendant with no names."""
        defendant = {
            "defendant_id": "D1",
            "first_name": "",
            "last_name": "",
            "full_name": "",
            "entity_type": "Corporation",
            "item_number": 1
        }
        
        is_valid, errors = validate_defendant(defendant)
        
        assert is_valid is False
        assert "Defendant must have at least first_name or last_name" in errors

    def test_validate_defendant_invalid_item_number(self):
        """Test validating defendant with invalid item number."""
        defendant = {
            "defendant_id": "D1",
            "first_name": "Evil",
            "last_name": "Corp",
            "full_name": "Evil Corp",
            "item_number": -1,  # Should be positive
        }
        
        is_valid, errors = validate_defendant(defendant)
        
        assert is_valid is False
        assert "item_number must be positive integer" in errors

    def test_validate_defendant_minimal_valid(self):
        """Test validating defendant with minimal valid data."""
        defendant = {
            "defendant_id": "D1",
            "first_name": "Evil",
            "last_name": "Corp",
            "full_name": "Evil Corp",
        }
        
        is_valid, errors = validate_defendant(defendant)
        
        assert is_valid is True
        assert errors == []


class TestValidateDiscovery:
    """Test the validate_discovery function."""

    def test_validate_valid_discovery(self):
        """Test validating valid discovery."""
        discovery = {
            "vermin": ["Rats/Mice", "Bedbugs"],
            "insects": ["Roaches", "Ants"],
            "hvac": ["Air Conditioner"],
            "electrical": ["Outlets"],
            "fire_hazard": ["Smoke Alarms"],
            "government_entities": ["Health Department"],
            "appliances": ["Stove"],
            "plumbing": ["Toilet"],
            "cabinets": ["Broken"],
            "flooring": ["Uneven"],
            "windows": ["Broken"],
            "doors": ["Broken"],
            "structure": ["Hole in wall"],
            "common_areas": ["Mailbox broken"],
            "trash_problems": ["Inadequate receptacles"],
            "nuisance": ["Noisy neighbors"],
            "health_hazard": ["Mold"],
            "harassment": ["Eviction threats"],
            "notices": ["3-day"],
            "utility_interruptions": ["Water shutoffs"],
            "safety_issues": ["Broken doors"],
            "has_injury": True,
            "has_nonresponsive_landlord": False,
            "has_unauthorized_entries": True,
            "has_stolen_items": False,
            "has_damaged_items": True,
            "has_age_discrimination": False,
            "has_racial_discrimination": True,
            "has_disability_discrimination": False,
            "has_security_deposit_issues": True,
        }
        
        is_valid, errors = validate_discovery(discovery)
        
        assert is_valid is True
        assert errors == []

    def test_validate_discovery_missing_array_fields(self):
        """Test validating discovery with missing array fields."""
        discovery = {
            "vermin": ["Rats/Mice"],
            # Missing other array fields
            "has_injury": True,
            "has_nonresponsive_landlord": False,
        }
        
        is_valid, errors = validate_discovery(discovery)
        
        assert is_valid is False
        assert "Missing array field: insects" in errors
        assert "Missing array field: hvac" in errors

    def test_validate_discovery_missing_boolean_fields(self):
        """Test validating discovery with missing boolean fields."""
        discovery = {
            "vermin": ["Rats/Mice"],
            "insects": ["Roaches"],
            "hvac": [],
            "electrical": [],
            "fire_hazard": [],
            "government_entities": [],
            "appliances": [],
            "plumbing": [],
            "cabinets": [],
            "flooring": [],
            "windows": [],
            "doors": [],
            "structure": [],
            "common_areas": [],
            "trash_problems": [],
            "nuisance": [],
            "health_hazard": [],
            "harassment": [],
            "notices": [],
            "utility_interruptions": [],
            "safety_issues": [],
            "has_injury": True,
            # Missing other boolean fields
        }
        
        is_valid, errors = validate_discovery(discovery)
        
        assert is_valid is False
        assert "Missing boolean field: has_nonresponsive_landlord" in errors

    def test_validate_discovery_wrong_array_types(self):
        """Test validating discovery with wrong array types."""
        discovery = {
            "vermin": "not a list",  # Should be list
            "insects": ["Roaches"],
            "hvac": [],
            "electrical": [],
            "fire_hazard": [],
            "government_entities": [],
            "appliances": [],
            "plumbing": [],
            "cabinets": [],
            "flooring": [],
            "windows": [],
            "doors": [],
            "structure": [],
            "common_areas": [],
            "trash_problems": [],
            "nuisance": [],
            "health_hazard": [],
            "harassment": [],
            "notices": [],
            "utility_interruptions": [],
            "safety_issues": [],
            "has_injury": True,
            "has_nonresponsive_landlord": False,
            "has_unauthorized_entries": True,
            "has_stolen_items": False,
            "has_damaged_items": True,
            "has_age_discrimination": False,
            "has_racial_discrimination": True,
            "has_disability_discrimination": False,
            "has_security_deposit_issues": True,
        }
        
        is_valid, errors = validate_discovery(discovery)
        
        assert is_valid is False
        assert "Array field must be list: vermin" in errors

    def test_validate_discovery_wrong_boolean_types(self):
        """Test validating discovery with wrong boolean types."""
        discovery = {
            "vermin": [],
            "insects": [],
            "hvac": [],
            "electrical": [],
            "fire_hazard": [],
            "government_entities": [],
            "appliances": [],
            "plumbing": [],
            "cabinets": [],
            "flooring": [],
            "windows": [],
            "doors": [],
            "structure": [],
            "common_areas": [],
            "trash_problems": [],
            "nuisance": [],
            "health_hazard": [],
            "harassment": [],
            "notices": [],
            "utility_interruptions": [],
            "safety_issues": [],
            "has_injury": "true",  # Should be boolean
            "has_nonresponsive_landlord": False,
            "has_unauthorized_entries": True,
            "has_stolen_items": False,
            "has_damaged_items": True,
            "has_age_discrimination": False,
            "has_racial_discrimination": True,
            "has_disability_discrimination": False,
            "has_security_deposit_issues": True,
        }
        
        is_valid, errors = validate_discovery(discovery)
        
        assert is_valid is False
        assert "Boolean field must be bool: has_injury" in errors

    def test_validate_discovery_empty_arrays_ok(self):
        """Test that empty arrays are valid."""
        discovery = {
            "vermin": [],
            "insects": [],
            "hvac": [],
            "electrical": [],
            "fire_hazard": [],
            "government_entities": [],
            "appliances": [],
            "plumbing": [],
            "cabinets": [],
            "flooring": [],
            "windows": [],
            "doors": [],
            "structure": [],
            "common_areas": [],
            "trash_problems": [],
            "nuisance": [],
            "health_hazard": [],
            "harassment": [],
            "notices": [],
            "utility_interruptions": [],
            "safety_issues": [],
            "has_injury": False,
            "has_nonresponsive_landlord": False,
            "has_unauthorized_entries": False,
            "has_stolen_items": False,
            "has_damaged_items": False,
            "has_age_discrimination": False,
            "has_racial_discrimination": False,
            "has_disability_discrimination": False,
            "has_security_deposit_issues": False,
        }
        
        is_valid, errors = validate_discovery(discovery)
        
        assert is_valid is True
        assert errors == []


class TestValidateNormalizedData:
    """Test the validate_normalized_data function."""

    def test_validate_valid_normalized_data(self):
        """Test validating valid normalized data."""
        data = {
            "case_info": {
                "case_id": "test-123",
                "property_address": "123 Main St",
                "city": "Los Angeles",
                "state": "California",
                "zip": "90001"
            },
            "plaintiffs": [
                {
                    "plaintiff_id": "P1",
                    "first_name": "John",
                    "last_name": "Doe",
                    "full_name": "John Doe",
                    "is_head_of_household": True,
                    "item_number": 1,
                    "discovery": {
                        "vermin": ["Rats/Mice"],
                        "insects": [],
                        "hvac": [],
                        "electrical": [],
                        "fire_hazard": [],
                        "government_entities": [],
                        "appliances": [],
                        "plumbing": [],
                        "cabinets": [],
                        "flooring": [],
                        "windows": [],
                        "doors": [],
                        "structure": [],
                        "common_areas": [],
                        "trash_problems": [],
                        "nuisance": [],
                        "health_hazard": [],
                        "harassment": [],
                        "notices": [],
                        "utility_interruptions": [],
                        "safety_issues": [],
                        "has_injury": True,
                        "has_nonresponsive_landlord": False,
                        "has_unauthorized_entries": True,
                        "has_stolen_items": False,
                        "has_damaged_items": True,
                        "has_age_discrimination": False,
                        "has_racial_discrimination": True,
                        "has_disability_discrimination": False,
                        "has_security_deposit_issues": True,
                    }
                }
            ],
            "defendants": [
                {
                    "defendant_id": "D1",
                    "first_name": "Evil",
                    "last_name": "Corp",
                    "full_name": "Evil Corp",
                    "entity_type": "Corporation",
                    "role": "Owner",
                    "item_number": 1
                }
            ]
        }
        
        is_valid, errors = validate_normalized_data(data)
        
        assert is_valid is True
        assert errors == []

    def test_validate_missing_top_level_keys(self):
        """Test validating data with missing top-level keys."""
        data = {
            "case_info": {"property_address": "123 Main St", "city": "LA", "state": "CA", "zip": "90001"},
            # Missing plaintiffs and defendants
        }
        
        is_valid, errors = validate_normalized_data(data)
        
        assert is_valid is False
        assert "Missing plaintiffs" in errors
        assert "Missing defendants" in errors

    def test_validate_no_plaintiffs(self):
        """Test validating data with no plaintiffs."""
        data = {
            "case_info": {"property_address": "123 Main St", "city": "LA", "state": "CA", "zip": "90001"},
            "plaintiffs": [],
            "defendants": [{"defendant_id": "D1", "first_name": "Evil", "last_name": "Corp", "full_name": "Evil Corp"}]
        }
        
        is_valid, errors = validate_normalized_data(data)
        
        assert is_valid is False
        assert "Must have at least 1 plaintiff" in errors

    def test_validate_no_defendants(self):
        """Test validating data with no defendants."""
        data = {
            "case_info": {"property_address": "123 Main St", "city": "LA", "state": "CA", "zip": "90001"},
            "plaintiffs": [{"plaintiff_id": "P1", "first_name": "John", "last_name": "Doe", "full_name": "John Doe"}],
            "defendants": []
        }
        
        is_valid, errors = validate_normalized_data(data)
        
        assert is_valid is False
        assert "Must have at least 1 defendant" in errors

    def test_validate_invalid_plaintiff(self):
        """Test validating data with invalid plaintiff."""
        data = {
            "case_info": {"property_address": "123 Main St", "city": "LA", "state": "CA", "zip": "90001"},
            "plaintiffs": [
                {
                    "plaintiff_id": "P1",
                    # Missing required fields
                }
            ],
            "defendants": [{"defendant_id": "D1", "first_name": "Evil", "last_name": "Corp", "full_name": "Evil Corp"}]
        }
        
        is_valid, errors = validate_normalized_data(data)
        
        assert is_valid is False
        assert "Plaintiff 1: Plaintiff missing required field: first_name" in errors

    def test_validate_invalid_defendant(self):
        """Test validating data with invalid defendant."""
        data = {
            "case_info": {"property_address": "123 Main St", "city": "LA", "state": "CA", "zip": "90001"},
            "plaintiffs": [{"plaintiff_id": "P1", "first_name": "John", "last_name": "Doe", "full_name": "John Doe"}],
            "defendants": [
                {
                    "defendant_id": "D1",
                    # Missing required fields
                }
            ]
        }
        
        is_valid, errors = validate_normalized_data(data)
        
        assert is_valid is False
        assert "Defendant 1: Defendant missing required field: first_name" in errors

    def test_validate_invalid_discovery(self):
        """Test validating data with invalid discovery."""
        data = {
            "case_info": {"property_address": "123 Main St", "city": "LA", "state": "CA", "zip": "90001"},
            "plaintiffs": [
                {
                    "plaintiff_id": "P1",
                    "first_name": "John",
                    "last_name": "Doe",
                    "full_name": "John Doe",
                    "discovery": {
                        "vermin": "not a list",  # Invalid
                        "insects": [],
                        "hvac": [],
                        "electrical": [],
                        "fire_hazard": [],
                        "government_entities": [],
                        "appliances": [],
                        "plumbing": [],
                        "cabinets": [],
                        "flooring": [],
                        "windows": [],
                        "doors": [],
                        "structure": [],
                        "common_areas": [],
                        "trash_problems": [],
                        "nuisance": [],
                        "health_hazard": [],
                        "harassment": [],
                        "notices": [],
                        "utility_interruptions": [],
                        "safety_issues": [],
                        "has_injury": True,
                        "has_nonresponsive_landlord": False,
                        "has_unauthorized_entries": True,
                        "has_stolen_items": False,
                        "has_damaged_items": True,
                        "has_age_discrimination": False,
                        "has_racial_discrimination": True,
                        "has_disability_discrimination": False,
                        "has_security_deposit_issues": True,
                    }
                }
            ],
            "defendants": [{"defendant_id": "D1", "first_name": "Evil", "last_name": "Corp", "full_name": "Evil Corp"}]
        }
        
        is_valid, errors = validate_normalized_data(data)
        
        assert is_valid is False
        assert "Plaintiff 1 discovery: Array field must be list: vermin" in errors

    def test_validate_multiple_errors(self):
        """Test validating data with multiple validation errors."""
        data = {
            "case_info": {
                "property_address": "",  # Empty required field
                "city": "LA",
                "state": "CA",
                "zip": "90001"
            },
            "plaintiffs": [],  # No plaintiffs
            "defendants": []  # No defendants
        }
        
        is_valid, errors = validate_normalized_data(data)
        
        assert is_valid is False
        assert len(errors) >= 3  # Multiple errors
        assert "Required field is empty: property_address" in errors
        assert "Must have at least 1 plaintiff" in errors
        assert "Must have at least 1 defendant" in errors


class TestIntegration:
    """Integration tests for the validators module."""

    def test_validate_complete_goaloutput_example(self):
        """Test validating the complete goalOutput.md example."""
        # This would be a comprehensive test with the actual goalOutput.md data
        # For now, we'll test with a representative sample
        data = {
            "case_info": {
                "case_id": "1",
                "property_address": "1331 Yorkshire Place NW",
                "city": "Concord",
                "state": "North Carolina",
                "zip": "28027",
                "filing_city": "Los Angeles",
                "filing_county": "North Carolina"
            },
            "plaintiffs": [
                {
                    "plaintiff_id": "4ck5Gw",
                    "first_name": "Clark",
                    "last_name": "Kent",
                    "full_name": "Clark Kent",
                    "plaintiff_type": "Individual",
                    "age_category": "Adult",
                    "is_head_of_household": True,
                    "unit_number": "1",
                    "item_number": 1,
                    "discovery": {
                        "vermin": ["Rats/Mice", "Bedbugs"],
                        "insects": ["Roaches", "Ants"],
                        "hvac": [],
                        "electrical": [],
                        "fire_hazard": [],
                        "government_entities": [],
                        "appliances": [],
                        "plumbing": [],
                        "cabinets": [],
                        "flooring": [],
                        "windows": [],
                        "doors": [],
                        "structure": [],
                        "common_areas": [],
                        "trash_problems": [],
                        "nuisance": [],
                        "health_hazard": [],
                        "harassment": [],
                        "notices": [],
                        "utility_interruptions": [],
                        "safety_issues": [],
                        "has_injury": False,
                        "has_nonresponsive_landlord": False,
                        "has_unauthorized_entries": False,
                        "has_stolen_items": False,
                        "has_damaged_items": False,
                        "has_age_discrimination": False,
                        "has_racial_discrimination": False,
                        "has_disability_discrimination": False,
                        "has_security_deposit_issues": False,
                    }
                }
            ],
            "defendants": [
                {
                    "defendant_id": "31rR5u",
                    "first_name": "Tony",
                    "last_name": "Stark",
                    "full_name": "Tony Stark",
                    "entity_type": "LLC",
                    "role": "Manager",
                    "item_number": 1
                }
            ]
        }
        
        is_valid, errors = validate_normalized_data(data)
        
        assert is_valid is True
        assert errors == []
