"""
Test suite for Phase 1: Input Parser Module

Tests the input parsing functionality including case info extraction,
plaintiff extraction, and defendant extraction.
"""

import pytest
from typing import Any

from src.phase1.input_parser import (
    parse_form_json,
    extract_case_info,
    extract_plaintiffs,
    extract_defendants,
)
from tests.fixtures.phase1_samples import SIMPLE_CASE, COMPLEX_CASE, EDGE_CASE


class TestParseFormJson:
    """Test the parse_form_json function."""

    def test_parse_valid_json(self):
        """Test parsing valid JSON data."""
        result = parse_form_json(SIMPLE_CASE)
        assert isinstance(result, dict)
        assert "Form" in result
        assert "PlaintiffDetails" in result
        assert "DefendantDetails2" in result

    def test_parse_invalid_type(self):
        """Test parsing invalid input type."""
        with pytest.raises(TypeError):
            parse_form_json("not a dict")

        with pytest.raises(TypeError):
            parse_form_json(123)

        with pytest.raises(TypeError):
            parse_form_json(None)

    def test_parse_empty_dict(self):
        """Test parsing empty dictionary."""
        result = parse_form_json({})
        assert result == {}


class TestExtractCaseInfo:
    """Test the extract_case_info function."""

    def test_extract_simple_case(self):
        """Test extracting case info from simple case."""
        case_info = extract_case_info(SIMPLE_CASE)
        
        assert case_info["case_id"] == "1"
        assert case_info["property_address"] == "1331 Yorkshire Place NW"
        assert case_info["city"] == "Concord"
        assert case_info["state"] == "North Carolina"
        assert case_info["zip"] == "28027"
        assert case_info["filing_city"] == "Los Angeles"
        assert case_info["filing_county"] == "Los Angeles County"

    def test_extract_complex_case(self):
        """Test extracting case info from complex case."""
        case_info = extract_case_info(COMPLEX_CASE)
        
        assert case_info["case_id"] == "2"
        assert case_info["property_address"] == "123 Main Street"
        assert case_info["city"] == "Los Angeles"
        assert case_info["state"] == "California"
        assert case_info["zip"] == "90001"

    def test_extract_edge_case(self):
        """Test extracting case info from edge case with normalized keys."""
        case_info = extract_case_info(EDGE_CASE)
        
        assert case_info["case_id"] == "3"
        assert case_info["property_address"] == "456 Oak Ave"
        assert case_info["city"] == "San Francisco"
        assert case_info["state"] == "California"
        assert case_info["zip"] == "94102"
        assert case_info["filing_city"] == "San Francisco"
        assert case_info["filing_county"] == "San Francisco County"

    def test_extract_missing_address_components(self):
        """Test handling missing address components."""
        data = {
            "Form": {"Id": "test"},
            "Full_Address": {
                "City": "Test City",
                # Missing other address components
            }
        }
        
        case_info = extract_case_info(data)
        
        assert case_info["case_id"] == "test"
        assert case_info["property_address"] == ""
        assert case_info["city"] == "Test City"
        assert case_info["state"] == ""
        assert case_info["zip"] == ""

    def test_extract_address_fallbacks(self):
        """Test address extraction with fallbacks."""
        data = {
            "Form": {"Id": "test"},
            "Full_Address": {
                "Line1": "123 Fallback St",
                "City": "Test City",
                "State": "Test State",
                "PostalCode": "12345"
            }
        }
        
        case_info = extract_case_info(data)
        
        assert case_info["property_address"] == "123 Fallback St"

    def test_extract_both_filing_key_formats(self):
        """Test handling both original and normalized filing keys."""
        # Test original format
        data_original = {
            "Form": {"Id": "test"},
            "Full_Address": {"City": "Test", "State": "Test", "PostalCode": "12345"},
            "Filing city": "Original City",
            "Filing county": "Original County"
        }
        
        case_info = extract_case_info(data_original)
        assert case_info["filing_city"] == "Original City"
        assert case_info["filing_county"] == "Original County"

        # Test normalized format
        data_normalized = {
            "Form": {"Id": "test"},
            "Full_Address": {"City": "Test", "State": "Test", "PostalCode": "12345"},
            "FilingCity": "Normalized City",
            "FilingCounty": "Normalized County"
        }
        
        case_info = extract_case_info(data_normalized)
        assert case_info["filing_city"] == "Normalized City"
        assert case_info["filing_county"] == "Normalized County"

    def test_extract_missing_form_id(self):
        """Test handling missing Form.Id."""
        data = {
            "Form": {},
            "Full_Address": {"City": "Test", "State": "Test", "PostalCode": "12345"}
        }
        
        case_info = extract_case_info(data)
        assert case_info["case_id"] == "unknown"


class TestExtractPlaintiffs:
    """Test the extract_plaintiffs function."""

    def test_extract_simple_plaintiff(self):
        """Test extracting single plaintiff."""
        plaintiffs = extract_plaintiffs(SIMPLE_CASE)
        
        assert len(plaintiffs) == 1
        
        plaintiff = plaintiffs[0]
        assert plaintiff["plaintiff_id"] == "4ck5Gw"
        assert plaintiff["first_name"] == "Clark"
        assert plaintiff["last_name"] == "Kent"
        assert plaintiff["full_name"] == "Clark Kent"
        assert plaintiff["plaintiff_type"] == "Individual"
        assert plaintiff["age_category"] == "Adult"
        assert plaintiff["is_head_of_household"] is True
        assert plaintiff["unit_number"] == "1"
        assert plaintiff["item_number"] == 1
        assert isinstance(plaintiff["discovery"], dict)

    def test_extract_multiple_plaintiffs(self):
        """Test extracting multiple plaintiffs."""
        plaintiffs = extract_plaintiffs(COMPLEX_CASE)
        
        assert len(plaintiffs) == 3
        
        # First plaintiff (HoH)
        plaintiff1 = plaintiffs[0]
        assert plaintiff1["plaintiff_id"] == "P1"
        assert plaintiff1["first_name"] == "John"
        assert plaintiff1["last_name"] == "Doe"
        assert plaintiff1["is_head_of_household"] is True
        assert plaintiff1["unit_number"] == "101"

        # Second plaintiff (HoH)
        plaintiff2 = plaintiffs[1]
        assert plaintiff2["plaintiff_id"] == "P2"
        assert plaintiff2["first_name"] == "Jane"
        assert plaintiff2["last_name"] == "Smith"
        assert plaintiff2["is_head_of_household"] is True
        assert plaintiff2["unit_number"] == "102"

        # Third plaintiff (non-HoH)
        plaintiff3 = plaintiffs[2]
        assert plaintiff3["plaintiff_id"] == "P3"
        assert plaintiff3["first_name"] == "Bob"
        assert plaintiff3["last_name"] == "Johnson"
        assert plaintiff3["is_head_of_household"] is False
        assert plaintiff3["unit_number"] is None

    def test_extract_plaintiff_with_special_characters(self):
        """Test extracting plaintiff with special characters in name."""
        plaintiffs = extract_plaintiffs(EDGE_CASE)
        
        assert len(plaintiffs) == 1
        
        plaintiff = plaintiffs[0]
        assert plaintiff["plaintiff_id"] == "E1"
        assert plaintiff["first_name"] == "José"
        assert plaintiff["last_name"] == "García-López"
        assert plaintiff["full_name"] == "José García-López"

    def test_extract_plaintiff_missing_optional_fields(self):
        """Test extracting plaintiff with missing optional fields."""
        data = {
            "PlaintiffDetails": [
                {
                    "Id": "test",
                    "PlaintiffItemNumberName": {
                        "First": "Test",
                        "FirstAndLast": "Test User",
                        "Last": "User"
                    },
                    "PlaintiffItemNumberType": "Individual",
                    "PlaintiffItemNumberAgeCategory": ["Adult"],
                    "PlaintiffItemNumberDiscovery": {
                        "Unit": None  # Missing unit
                    },
                    "HeadOfHousehold": True,
                    "ItemNumber": 1
                }
            ]
        }
        
        plaintiffs = extract_plaintiffs(data)
        
        assert len(plaintiffs) == 1
        plaintiff = plaintiffs[0]
        assert plaintiff["unit_number"] is None

    def test_extract_plaintiff_empty_list(self):
        """Test extracting from empty plaintiff list."""
        data = {"PlaintiffDetails": []}
        plaintiffs = extract_plaintiffs(data)
        assert plaintiffs == []

    def test_extract_plaintiff_missing_name_fields(self):
        """Test extracting plaintiff with missing name fields."""
        data = {
            "PlaintiffDetails": [
                {
                    "Id": "test",
                    "PlaintiffItemNumberName": {
                        "First": "",
                        "FirstAndLast": "",
                        "Last": ""
                    },
                    "PlaintiffItemNumberType": "Individual",
                    "PlaintiffItemNumberAgeCategory": ["Adult"],
                    "PlaintiffItemNumberDiscovery": {},
                    "HeadOfHousehold": True,
                    "ItemNumber": 1
                }
            ]
        }
        
        plaintiffs = extract_plaintiffs(data)
        
        assert len(plaintiffs) == 1
        plaintiff = plaintiffs[0]
        assert plaintiff["first_name"] == ""
        assert plaintiff["last_name"] == ""
        assert plaintiff["full_name"] == ""  # Empty FirstAndLast from data


class TestExtractDefendants:
    """Test the extract_defendants function."""

    def test_extract_simple_defendant(self):
        """Test extracting single defendant."""
        defendants = extract_defendants(SIMPLE_CASE)
        
        assert len(defendants) == 1
        
        defendant = defendants[0]
        assert defendant["defendant_id"] == "31rR5u"
        assert defendant["first_name"] == "Tony"
        assert defendant["last_name"] == "Stark"
        assert defendant["full_name"] == "Tony Stark"
        assert defendant["entity_type"] == "LLC"
        assert defendant["role"] == "Manager"
        assert defendant["item_number"] == 1

    def test_extract_multiple_defendants(self):
        """Test extracting multiple defendants."""
        defendants = extract_defendants(COMPLEX_CASE)
        
        assert len(defendants) == 2
        
        # First defendant
        defendant1 = defendants[0]
        assert defendant1["defendant_id"] == "D1"
        assert defendant1["first_name"] == "Evil"
        assert defendant1["last_name"] == "Corp"
        assert defendant1["entity_type"] == "Corporation"
        assert defendant1["role"] == "Owner"

        # Second defendant
        defendant2 = defendants[1]
        assert defendant2["defendant_id"] == "D2"
        assert defendant2["first_name"] == "Bad"
        assert defendant2["last_name"] == "Manager"
        assert defendant2["entity_type"] == "Individual"
        assert defendant2["role"] == "Manager"

    def test_extract_defendant_with_empty_name(self):
        """Test extracting defendant with empty first name."""
        defendants = extract_defendants(EDGE_CASE)
        
        assert len(defendants) == 1
        
        defendant = defendants[0]
        assert defendant["defendant_id"] == "ED1"
        assert defendant["first_name"] == ""
        assert defendant["last_name"] == "ABC Properties, LLC"
        assert defendant["full_name"] == "ABC Properties, LLC"

    def test_extract_defendant_empty_list(self):
        """Test extracting from empty defendant list."""
        data = {"DefendantDetails2": []}
        defendants = extract_defendants(data)
        assert defendants == []

    def test_extract_defendant_missing_optional_fields(self):
        """Test extracting defendant with missing optional fields."""
        data = {
            "DefendantDetails2": [
                {
                    "Id": "test",
                    "DefendantItemNumberName": {
                        "First": "Test",
                        "FirstAndLast": "Test Corp",
                        "Last": "Corp"
                    },
                    "DefendantItemNumberType": "LLC",
                    "DefendantItemNumberManagerOwner": "",
                    "ItemNumber": 1
                }
            ]
        }
        
        defendants = extract_defendants(data)
        
        assert len(defendants) == 1
        defendant = defendants[0]
        assert defendant["role"] == ""


class TestIntegration:
    """Integration tests for the input parser module."""

    def test_parse_complete_goaloutput_example(self):
        """Test parsing the complete goalOutput.md example."""
        # Load the goalOutput.md data
        with open("/Users/ryanhaines/Desktop/Test/goalOutput.md", "r") as f:
            import json
            goal_data = json.loads(f.read())
        
        # Parse the data
        parsed = parse_form_json(goal_data)
        case_info = extract_case_info(parsed)
        plaintiffs = extract_plaintiffs(parsed)
        defendants = extract_defendants(parsed)
        
        # Verify structure
        assert case_info["case_id"] == "1"
        assert case_info["property_address"] == "1331 Yorkshire Place NW"
        assert len(plaintiffs) == 3
        assert len(defendants) == 2
        
        # Verify first plaintiff (Clark Kent)
        clark = plaintiffs[0]
        assert clark["first_name"] == "Clark"
        assert clark["last_name"] == "Kent"
        assert clark["is_head_of_household"] is True
        
        # Verify first defendant (Tony Stark)
        tony = defendants[0]
        assert tony["first_name"] == "Tony"
        assert tony["last_name"] == "Stark"
        assert tony["entity_type"] == "LLC"

    def test_parse_preserves_all_data(self):
        """Test that parsing preserves all important data."""
        parsed = parse_form_json(COMPLEX_CASE)
        case_info = extract_case_info(parsed)
        plaintiffs = extract_plaintiffs(parsed)
        defendants = extract_defendants(parsed)
        
        # Verify all plaintiffs present
        assert len(plaintiffs) == 3
        plaintiff_ids = {p["plaintiff_id"] for p in plaintiffs}
        assert plaintiff_ids == {"P1", "P2", "P3"}
        
        # Verify all defendants present
        assert len(defendants) == 2
        defendant_ids = {d["defendant_id"] for d in defendants}
        assert defendant_ids == {"D1", "D2"}
        
        # Verify case info preserved
        assert case_info["case_id"] == "2"
        assert case_info["property_address"] == "123 Main Street"

    def test_parse_handles_missing_sections(self):
        """Test parsing data with missing sections."""
        incomplete_data = {
            "Form": {"Id": "test"},
            "Full_Address": {"City": "Test", "State": "Test", "PostalCode": "12345"}
            # Missing PlaintiffDetails and DefendantDetails2
        }
        
        parsed = parse_form_json(incomplete_data)
        case_info = extract_case_info(parsed)
        plaintiffs = extract_plaintiffs(parsed)
        defendants = extract_defendants(parsed)
        
        assert case_info["case_id"] == "test"
        assert plaintiffs == []
        assert defendants == []
