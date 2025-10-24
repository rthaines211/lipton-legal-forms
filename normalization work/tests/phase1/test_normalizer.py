"""
Test suite for Phase 1: Normalizer Pipeline

Tests the main normalization pipeline that orchestrates input parsing,
discovery flattening, and validation.
"""

import pytest
from typing import Any

from src.phase1.normalizer import (
    normalize_form_data,
    normalize_form_data_batch,
    ValidationError,
)
from tests.fixtures.phase1_samples import SIMPLE_CASE, COMPLEX_CASE, EDGE_CASE


class TestNormalizeFormData:
    """Test the normalize_form_data function."""

    def test_normalize_simple_case(self):
        """Test normalizing a simple case."""
        normalized = normalize_form_data(SIMPLE_CASE)
        
        # Verify structure
        assert "case_info" in normalized
        assert "plaintiffs" in normalized
        assert "defendants" in normalized
        
        # Verify case info
        case_info = normalized["case_info"]
        assert case_info["case_id"] == "1"
        assert case_info["property_address"] == "1331 Yorkshire Place NW"
        assert case_info["city"] == "Concord"
        assert case_info["state"] == "North Carolina"
        assert case_info["zip"] == "28027"
        assert case_info["filing_city"] == "Los Angeles"
        assert case_info["filing_county"] == "Los Angeles County"
        
        # Verify plaintiffs
        plaintiffs = normalized["plaintiffs"]
        assert len(plaintiffs) == 1
        
        plaintiff = plaintiffs[0]
        assert plaintiff["plaintiff_id"] == "4ck5Gw"
        assert plaintiff["first_name"] == "Clark"
        assert plaintiff["last_name"] == "Kent"
        assert plaintiff["full_name"] == "Clark Kent"
        assert plaintiff["is_head_of_household"] is True
        assert plaintiff["unit_number"] == "1"
        assert plaintiff["item_number"] == 1
        
        # Verify discovery is flattened
        discovery = plaintiff["discovery"]
        assert isinstance(discovery, dict)
        assert "vermin" in discovery
        assert "insects" in discovery
        assert "has_injury" in discovery
        assert discovery["vermin"] == ["Rats/Mice", "Bedbugs"]
        assert discovery["insects"] == ["Roaches", "Ants"]
        assert discovery["has_injury"] is False
        
        # Verify defendants
        defendants = normalized["defendants"]
        assert len(defendants) == 1
        
        defendant = defendants[0]
        assert defendant["defendant_id"] == "31rR5u"
        assert defendant["first_name"] == "Tony"
        assert defendant["last_name"] == "Stark"
        assert defendant["full_name"] == "Tony Stark"
        assert defendant["entity_type"] == "LLC"
        assert defendant["role"] == "Manager"
        assert defendant["item_number"] == 1

    def test_normalize_complex_case(self):
        """Test normalizing a complex case with multiple parties."""
        normalized = normalize_form_data(COMPLEX_CASE)
        
        # Verify structure
        assert "case_info" in normalized
        assert "plaintiffs" in normalized
        assert "defendants" in normalized
        
        # Verify case info
        case_info = normalized["case_info"]
        assert case_info["case_id"] == "2"
        assert case_info["property_address"] == "123 Main Street"
        assert case_info["city"] == "Los Angeles"
        assert case_info["state"] == "California"
        assert case_info["zip"] == "90001"
        
        # Verify plaintiffs (3 total)
        plaintiffs = normalized["plaintiffs"]
        assert len(plaintiffs) == 3
        
        # First plaintiff (HoH with discovery)
        plaintiff1 = plaintiffs[0]
        assert plaintiff1["plaintiff_id"] == "P1"
        assert plaintiff1["first_name"] == "John"
        assert plaintiff1["last_name"] == "Doe"
        assert plaintiff1["is_head_of_household"] is True
        assert plaintiff1["unit_number"] == "101"
        
        # Verify discovery is flattened for first plaintiff
        discovery1 = plaintiff1["discovery"]
        assert discovery1["vermin"] == ["Rats/Mice", "Bedbugs", "Skunks"]
        assert discovery1["insects"] == ["Roaches", "Ants", "Bedbugs"]
        assert discovery1["hvac"] == ["Air Conditioner", "Heater"]
        assert discovery1["has_injury"] is True
        assert discovery1["has_nonresponsive_landlord"] is True
        
        # Second plaintiff (HoH with minimal discovery)
        plaintiff2 = plaintiffs[1]
        assert plaintiff2["plaintiff_id"] == "P2"
        assert plaintiff2["first_name"] == "Jane"
        assert plaintiff2["last_name"] == "Smith"
        assert plaintiff2["is_head_of_household"] is True
        assert plaintiff2["unit_number"] == "102"
        
        # Third plaintiff (non-HoH, empty discovery)
        plaintiff3 = plaintiffs[2]
        assert plaintiff3["plaintiff_id"] == "P3"
        assert plaintiff3["first_name"] == "Bob"
        assert plaintiff3["last_name"] == "Johnson"
        assert plaintiff3["is_head_of_household"] is False
        assert plaintiff3["unit_number"] is None
        
        # Verify defendants (2 total)
        defendants = normalized["defendants"]
        assert len(defendants) == 2
        
        defendant1 = defendants[0]
        assert defendant1["defendant_id"] == "D1"
        assert defendant1["first_name"] == "Evil"
        assert defendant1["last_name"] == "Corp"
        assert defendant1["entity_type"] == "Corporation"
        assert defendant1["role"] == "Owner"
        
        defendant2 = defendants[1]
        assert defendant2["defendant_id"] == "D2"
        assert defendant2["first_name"] == "Bad"
        assert defendant2["last_name"] == "Manager"
        assert defendant2["entity_type"] == "Individual"
        assert defendant2["role"] == "Manager"

    def test_normalize_edge_case(self):
        """Test normalizing edge case with special characters and missing fields."""
        normalized = normalize_form_data(EDGE_CASE)
        
        # Verify structure
        assert "case_info" in normalized
        assert "plaintiffs" in normalized
        assert "defendants" in normalized
        
        # Verify case info with normalized keys
        case_info = normalized["case_info"]
        assert case_info["case_id"] == "3"
        assert case_info["property_address"] == "456 Oak Ave"
        assert case_info["city"] == "San Francisco"
        assert case_info["state"] == "California"
        assert case_info["zip"] == "94102"
        assert case_info["filing_city"] == "San Francisco"
        assert case_info["filing_county"] == "San Francisco County"
        
        # Verify plaintiff with special characters
        plaintiffs = normalized["plaintiffs"]
        assert len(plaintiffs) == 1
        
        plaintiff = plaintiffs[0]
        assert plaintiff["plaintiff_id"] == "E1"
        assert plaintiff["first_name"] == "José"
        assert plaintiff["last_name"] == "García-López"
        assert plaintiff["full_name"] == "José García-López"
        assert plaintiff["is_head_of_household"] is True
        
        # Verify empty discovery is handled correctly
        discovery = plaintiff["discovery"]
        assert isinstance(discovery, dict)
        assert discovery["vermin"] == []
        assert discovery["insects"] == []
        assert discovery["has_injury"] is False
        
        # Verify defendant with empty first name
        defendants = normalized["defendants"]
        assert len(defendants) == 1
        
        defendant = defendants[0]
        assert defendant["defendant_id"] == "ED1"
        assert defendant["first_name"] == ""
        assert defendant["last_name"] == "ABC Properties, LLC"
        assert defendant["full_name"] == "ABC Properties, LLC"
        assert defendant["entity_type"] == "LLC"
        assert defendant["role"] == "Owner"

    def test_normalize_invalid_input_type(self):
        """Test normalizing invalid input type."""
        with pytest.raises(ValidationError) as exc_info:
            normalize_form_data("not a dict")
        
        assert "Invalid input type" in str(exc_info.value)

    def test_normalize_missing_required_fields(self):
        """Test normalizing data with missing required fields."""
        invalid_data = {
            "Form": {"Id": "test"},
            "Full_Address": {
                "City": "Test",
                "State": "Test",
                "PostalCode": "12345"
                # Missing StreetAddress/Line1
            },
            "PlaintiffDetails": [],
            "DefendantDetails2": []
        }
        
        with pytest.raises(ValidationError) as exc_info:
            normalize_form_data(invalid_data)
        
        assert "Validation failed" in str(exc_info.value)
        assert "Required field is empty: property_address" in exc_info.value.errors

    def test_normalize_no_plaintiffs(self):
        """Test normalizing data with no plaintiffs."""
        invalid_data = {
            "Form": {"Id": "test"},
            "Full_Address": {
                "StreetAddress": "123 Main St",
                "City": "Test",
                "State": "Test",
                "PostalCode": "12345"
            },
            "PlaintiffDetails": [],
            "DefendantDetails2": [
                {
                    "Id": "D1",
                    "DefendantItemNumberName": {
                        "First": "Evil",
                        "FirstAndLast": "Evil Corp",
                        "Last": "Corp"
                    },
                    "DefendantItemNumberType": "Corporation",
                    "DefendantItemNumberManagerOwner": "Owner",
                    "ItemNumber": 1
                }
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            normalize_form_data(invalid_data)
        
        assert "Validation failed" in str(exc_info.value)
        assert "Must have at least 1 plaintiff" in exc_info.value.errors

    def test_normalize_no_defendants(self):
        """Test normalizing data with no defendants."""
        invalid_data = {
            "Form": {"Id": "test"},
            "Full_Address": {
                "StreetAddress": "123 Main St",
                "City": "Test",
                "State": "Test",
                "PostalCode": "12345"
            },
            "PlaintiffDetails": [
                {
                    "Id": "P1",
                    "PlaintiffItemNumberName": {
                        "First": "John",
                        "FirstAndLast": "John Doe",
                        "Last": "Doe"
                    },
                    "PlaintiffItemNumberType": "Individual",
                    "PlaintiffItemNumberAgeCategory": ["Adult"],
                    "PlaintiffItemNumberDiscovery": {},
                    "HeadOfHousehold": True,
                    "ItemNumber": 1
                }
            ],
            "DefendantDetails2": []
        }
        
        with pytest.raises(ValidationError) as exc_info:
            normalize_form_data(invalid_data)
        
        assert "Validation failed" in str(exc_info.value)
        assert "Must have at least 1 defendant" in exc_info.value.errors

    def test_normalize_preserves_all_data(self):
        """Test that normalization preserves all important data."""
        normalized = normalize_form_data(COMPLEX_CASE)
        
        # Verify all plaintiffs present
        assert len(normalized["plaintiffs"]) == 3
        plaintiff_ids = {p["plaintiff_id"] for p in normalized["plaintiffs"]}
        assert plaintiff_ids == {"P1", "P2", "P3"}
        
        # Verify all defendants present
        assert len(normalized["defendants"]) == 2
        defendant_ids = {d["defendant_id"] for d in normalized["defendants"]}
        assert defendant_ids == {"D1", "D2"}
        
        # Verify case info preserved
        assert normalized["case_info"]["case_id"] == "2"
        assert normalized["case_info"]["property_address"] == "123 Main Street"
        
        # Verify discovery data preserved
        plaintiff1 = normalized["plaintiffs"][0]
        discovery = plaintiff1["discovery"]
        assert discovery["vermin"] == ["Rats/Mice", "Bedbugs", "Skunks"]
        assert discovery["insects"] == ["Roaches", "Ants", "Bedbugs"]
        assert discovery["hvac"] == ["Air Conditioner", "Heater"]
        assert discovery["has_injury"] is True
        assert discovery["has_nonresponsive_landlord"] is True

    def test_normalize_discovery_flattening(self):
        """Test that discovery data is properly flattened."""
        normalized = normalize_form_data(SIMPLE_CASE)
        
        plaintiff = normalized["plaintiffs"][0]
        discovery = plaintiff["discovery"]
        
        # Test that original keys are normalized
        assert "vermin" in discovery
        assert "insects" in discovery
        assert "hvac" in discovery
        assert "electrical" in discovery
        
        # Test that boolean flags are extracted
        assert "has_injury" in discovery
        assert "has_nonresponsive_landlord" in discovery
        assert "has_unauthorized_entries" in discovery
        
        # Test that values are preserved
        assert discovery["vermin"] == ["Rats/Mice", "Bedbugs"]
        assert discovery["insects"] == ["Roaches", "Ants"]
        assert discovery["has_injury"] is False
        assert discovery["has_nonresponsive_landlord"] is False

    def test_normalize_handles_empty_discovery(self):
        """Test that empty discovery is handled correctly."""
        data_with_empty_discovery = {
            "Form": {"Id": "test"},
            "Full_Address": {
                "StreetAddress": "123 Main St",
                "City": "Test",
                "State": "Test",
                "PostalCode": "12345"
            },
            "PlaintiffDetails": [
                {
                    "Id": "P1",
                    "PlaintiffItemNumberName": {
                        "First": "John",
                        "FirstAndLast": "John Doe",
                        "Last": "Doe"
                    },
                    "PlaintiffItemNumberType": "Individual",
                    "PlaintiffItemNumberAgeCategory": ["Adult"],
                    "PlaintiffItemNumberDiscovery": {},  # Empty discovery
                    "HeadOfHousehold": True,
                    "ItemNumber": 1
                }
            ],
            "DefendantDetails2": [
                {
                    "Id": "D1",
                    "DefendantItemNumberName": {
                        "First": "Evil",
                        "FirstAndLast": "Evil Corp",
                        "Last": "Corp"
                    },
                    "DefendantItemNumberType": "Corporation",
                    "DefendantItemNumberManagerOwner": "Owner",
                    "ItemNumber": 1
                }
            ]
        }
        
        normalized = normalize_form_data(data_with_empty_discovery)
        
        plaintiff = normalized["plaintiffs"][0]
        discovery = plaintiff["discovery"]
        
        # All arrays should be empty
        array_keys = ["vermin", "insects", "hvac", "electrical", "fire_hazard", "government_entities", "appliances", "plumbing", "cabinets", "flooring", "windows", "doors", "structure", "common_areas", "trash_problems", "nuisance", "health_hazard", "harassment", "notices", "utility_interruptions", "safety_issues"]
        for key in array_keys:
            assert discovery[key] == []
        
        # All boolean flags should be False
        boolean_keys = ["has_injury", "has_nonresponsive_landlord", "has_unauthorized_entries", "has_stolen_items", "has_damaged_items", "has_age_discrimination", "has_racial_discrimination", "has_disability_discrimination", "has_security_deposit_issues"]
        for key in boolean_keys:
            assert discovery[key] is False


class TestNormalizeFormDataBatch:
    """Test the normalize_form_data_batch function."""

    def test_normalize_batch_valid_forms(self):
        """Test normalizing a batch of valid forms."""
        forms = [SIMPLE_CASE, COMPLEX_CASE, EDGE_CASE]
        
        normalized_forms = normalize_form_data_batch(forms)
        
        assert len(normalized_forms) == 3
        
        # Verify each form is normalized correctly
        assert normalized_forms[0]["case_info"]["case_id"] == "1"
        assert normalized_forms[1]["case_info"]["case_id"] == "2"
        assert normalized_forms[2]["case_info"]["case_id"] == "3"
        
        # Verify structure is consistent
        for normalized in normalized_forms:
            assert "case_info" in normalized
            assert "plaintiffs" in normalized
            assert "defendants" in normalized

    def test_normalize_batch_with_invalid_form(self):
        """Test normalizing a batch with one invalid form."""
        invalid_form = {
            "Form": {"Id": "invalid"},
            "Full_Address": {
                "City": "Test",
                "State": "Test",
                "PostalCode": "12345"
                # Missing StreetAddress
            },
            "PlaintiffDetails": [],
            "DefendantDetails2": []
        }
        
        forms = [SIMPLE_CASE, invalid_form, EDGE_CASE]
        
        with pytest.raises(ValidationError) as exc_info:
            normalize_form_data_batch(forms)
        
        assert "Validation failed for form 2" in str(exc_info.value)

    def test_normalize_batch_empty_list(self):
        """Test normalizing an empty batch."""
        normalized_forms = normalize_form_data_batch([])
        
        assert normalized_forms == []

    def test_normalize_batch_single_form(self):
        """Test normalizing a batch with a single form."""
        forms = [SIMPLE_CASE]
        
        normalized_forms = normalize_form_data_batch(forms)
        
        assert len(normalized_forms) == 1
        assert normalized_forms[0]["case_info"]["case_id"] == "1"


class TestValidationError:
    """Test the ValidationError exception class."""

    def test_validation_error_with_message(self):
        """Test ValidationError with just a message."""
        error = ValidationError("Test error")
        
        assert error.message == "Test error"
        assert error.errors == []
        assert str(error) == "Test error"

    def test_validation_error_with_errors(self):
        """Test ValidationError with message and errors."""
        errors = ["Error 1", "Error 2", "Error 3"]
        error = ValidationError("Test error", errors)
        
        assert error.message == "Test error"
        assert error.errors == errors
        assert "Error 1" in str(error)
        assert "Error 2" in str(error)
        assert "Error 3" in str(error)

    def test_validation_error_inheritance(self):
        """Test that ValidationError inherits from Exception."""
        error = ValidationError("Test error")
        
        assert isinstance(error, Exception)
        assert isinstance(error, ValidationError)


class TestIntegration:
    """Integration tests for the normalizer pipeline."""

    def test_normalize_goaloutput_example(self):
        """Test normalizing the complete goalOutput.md example."""
        # Load the goalOutput.md data
        with open("/Users/ryanhaines/Desktop/Test/goalOutput.md", "r") as f:
            import json
            goal_data = json.loads(f.read())
        
        normalized = normalize_form_data(goal_data)
        
        # Verify structure
        assert "case_info" in normalized
        assert "plaintiffs" in normalized
        assert "defendants" in normalized
        
        # Verify case info
        case_info = normalized["case_info"]
        assert case_info["case_id"] == "1"
        assert case_info["property_address"] == "1331 Yorkshire Place NW"
        assert case_info["city"] == "Concord"
        assert case_info["state"] == "North Carolina"
        assert case_info["zip"] == "28027"
        assert case_info["filing_city"] == "Los Angeles"
        assert case_info["filing_county"] == "North Carolina"
        
        # Verify plaintiffs (3 total)
        plaintiffs = normalized["plaintiffs"]
        assert len(plaintiffs) == 3
        
        # Clark Kent (HoH with full discovery)
        clark = plaintiffs[0]
        assert clark["plaintiff_id"] == "4ck5Gw"
        assert clark["first_name"] == "Clark"
        assert clark["last_name"] == "Kent"
        assert clark["is_head_of_household"] is True
        assert clark["unit_number"] == "1"
        
        # Verify Clark's discovery is flattened
        clark_discovery = clark["discovery"]
        assert clark_discovery["vermin"] == ["Rats/Mice", "Skunks", "Bats", "Racoons", "Pigeons", "Opossum"]
        assert clark_discovery["insects"] == ["Ants", "Roaches", "Flies", "Bedbugs", "Wasps", "Hornets", "Spiders", "Termites", "Mosquitos", "Bees"]
        assert clark_discovery["hvac"] == ["Air Conditioner", "Heater", "Venitlation"]
        assert clark_discovery["has_injury"] is True
        assert clark_discovery["has_nonresponsive_landlord"] is True
        assert clark_discovery["has_unauthorized_entries"] is True
        assert clark_discovery["has_stolen_items"] is True
        assert clark_discovery["has_damaged_items"] is True
        assert clark_discovery["has_age_discrimination"] is True
        assert clark_discovery["has_racial_discrimination"] is True
        assert clark_discovery["has_disability_discrimination"] is True
        assert clark_discovery["has_security_deposit_issues"] is True
        
        # Lois Lane (HoH with minimal discovery)
        lois = plaintiffs[1]
        assert lois["plaintiff_id"] == "29BQoV"
        assert lois["first_name"] == "Lois"
        assert lois["last_name"] == "Lane"
        assert lois["is_head_of_household"] is True
        assert lois["unit_number"] == "2"
        
        # Bruce Wayne (non-HoH, empty discovery)
        bruce = plaintiffs[2]
        assert bruce["plaintiff_id"] == "3kgBBo"
        assert bruce["first_name"] == "Bruce"
        assert bruce["last_name"] == "Wayne"
        assert bruce["is_head_of_household"] is False
        assert bruce["unit_number"] is None
        
        # Verify defendants (2 total)
        defendants = normalized["defendants"]
        assert len(defendants) == 2
        
        # Tony Stark
        tony = defendants[0]
        assert tony["defendant_id"] == "31rR5u"
        assert tony["first_name"] == "Tony"
        assert tony["last_name"] == "Stark"
        assert tony["entity_type"] == "LLC"
        assert tony["role"] == "Manager"
        
        # Steve Rogers
        steve = defendants[1]
        assert steve["defendant_id"] == "3UpIch"
        assert steve["first_name"] == "Steve"
        assert steve["last_name"] == "Rogers"
        assert steve["entity_type"] == "LLC"
        assert steve["role"] == "Owner"

    def test_normalize_performance(self):
        """Test that normalization meets performance requirements."""
        import time
        
        # Test with simple case
        start_time = time.time()
        normalized = normalize_form_data(SIMPLE_CASE)
        end_time = time.time()
        
        # Should complete in < 1 second
        assert (end_time - start_time) < 1.0
        
        # Verify result is correct
        assert normalized["case_info"]["case_id"] == "1"
        assert len(normalized["plaintiffs"]) == 1
        assert len(normalized["defendants"]) == 1

    def test_normalize_memory_usage(self):
        """Test that normalization doesn't use excessive memory."""
        import sys
        
        # Test with complex case
        normalized = normalize_form_data(COMPLEX_CASE)
        
        # Verify result is correct
        assert normalized["case_info"]["case_id"] == "2"
        assert len(normalized["plaintiffs"]) == 3
        assert len(normalized["defendants"]) == 2
        
        # Memory usage should be reasonable (this is a basic check)
        # In a real test, we'd use memory_profiler or similar
        assert sys.getsizeof(normalized) < 10000  # 10KB should be plenty

    def test_normalize_data_integrity(self):
        """Test that no data is lost during normalization."""
        original_data = COMPLEX_CASE.copy()
        normalized = normalize_form_data(original_data)
        
        # Verify all original plaintiffs are present
        original_plaintiff_ids = {p["Id"] for p in original_data["PlaintiffDetails"]}
        normalized_plaintiff_ids = {p["plaintiff_id"] for p in normalized["plaintiffs"]}
        assert original_plaintiff_ids == normalized_plaintiff_ids
        
        # Verify all original defendants are present
        original_defendant_ids = {d["Id"] for d in original_data["DefendantDetails2"]}
        normalized_defendant_ids = {d["defendant_id"] for d in normalized["defendants"]}
        assert original_defendant_ids == normalized_defendant_ids
        
        # Verify case info is preserved
        assert normalized["case_info"]["property_address"] == original_data["Full_Address"]["StreetAddress"]
        assert normalized["case_info"]["city"] == original_data["Full_Address"]["City"]
        assert normalized["case_info"]["state"] == original_data["Full_Address"]["State"]
        assert normalized["case_info"]["zip"] == original_data["Full_Address"]["PostalCode"]
