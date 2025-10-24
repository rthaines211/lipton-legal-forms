"""
Integration Tests for Phase 1 to Phase 2 Pipeline

This module tests the full pipeline from form JSON to datasets.
"""

import json
import pytest

from src.phase1.normalizer import normalize_form_data
from src.phase2.dataset_builder import build_datasets


class TestPhase1ToPhase2Integration:
    """Test full pipeline from Phase 1 to Phase 2."""

    def test_end_to_end_phase1_to_phase2(self):
        """Test full pipeline from form JSON to datasets."""
        # Load goalOutput.md example (from Phase 1 fixtures)
        form_json = {
            "Form": {"Id": "1"},
            "PlaintiffDetails": [
                {
                    "Id": "4ck5Gw",
                    "PlaintiffItemNumberName": {
                        "First": "Clark",
                        "FirstAndLast": "Clark Kent",
                        "Last": "Kent"
                    },
                    "HeadOfHousehold": True,
                    "ItemNumber": 1,
                    "PlaintiffItemNumberDiscovery": {
                        "VerminIssue": True,
                        "Vermin": ["Rats/Mice", "Skunks", "Bats"],
                        "InsectIssues": True,
                        "Insects": ["Ants", "Roaches", "Flies"],
                        "Injury Issues": True,
                        "Nonresponsive landlord Issues": False
                    }
                },
                {
                    "Id": "4pyhfl",
                    "PlaintiffItemNumberName": {
                        "First": "Lois",
                        "FirstAndLast": "Lois Lane",
                        "Last": "Lane"
                    },
                    "HeadOfHousehold": True,
                    "ItemNumber": 2,
                    "PlaintiffItemNumberDiscovery": {
                        "VerminIssue": True,
                        "Vermin": ["Skunks", "Raccoons"],
                        "InsectIssues": False,
                        "Insects": [],
                        "Injury Issues": False,
                        "Nonresponsive landlord Issues": True
                    }
                },
                {
                    "Id": "ZbKVgB",
                    "PlaintiffItemNumberName": {
                        "First": "Bruce",
                        "FirstAndLast": "Bruce Wayne",
                        "Last": "Wayne"
                    },
                    "HeadOfHousehold": False,
                    "ItemNumber": 3
                    # No discovery data (non-HoH)
                }
            ],
            "DefendantDetails2": [
                {
                    "Id": "31rR5u",
                    "DefendantItemNumberName": {
                        "First": "Tony",
                        "FirstAndLast": "Tony Stark",
                        "Last": "Stark"
                    },
                    "DefendantItemNumberType": "LLC",
                    "DefendantItemNumberManagerOwner": "Manager",
                    "ItemNumber": 1
                },
                {
                    "Id": "8WCXCG",
                    "DefendantItemNumberName": {
                        "First": "Steve",
                        "FirstAndLast": "Steve Rogers",
                        "Last": "Rogers"
                    },
                    "DefendantItemNumberType": "LLC",
                    "DefendantItemNumberManagerOwner": "Owner",
                    "ItemNumber": 2
                }
            ],
            "Full_Address": {
                "StreetAddress": "1331 Yorkshire Place NW",
                "City": "Concord",
                "State": "North Carolina",
                "PostalCode": "28027"
            },
            "Filing city": "Los Angeles",
            "Filing county": "North Carolina"
        }

        # Phase 1: Normalize
        normalized = normalize_form_data(form_json)
        
        # Verify Phase 1 output
        assert "case_info" in normalized
        assert "plaintiffs" in normalized
        assert "defendants" in normalized
        assert len(normalized["plaintiffs"]) == 3
        assert len(normalized["defendants"]) == 2

        # Phase 2: Build datasets
        result = build_datasets(normalized)
        
        # Verify Phase 2 output
        assert "datasets" in result
        assert "metadata" in result
        
        # Should have 4 datasets: 2 HoH × 2 defendants
        assert result["metadata"]["total_datasets"] == 4
        assert result["metadata"]["hoh_count"] == 2
        assert result["metadata"]["defendant_count"] == 2
        assert result["metadata"]["non_hoh_plaintiffs"] == 1
        assert len(result["datasets"]) == 4

    def test_end_to_end_with_real_formtest_data(self):
        """Test full pipeline with real formtest.json data."""
        # Load the actual formtest.json file
        with open("formtest.json", "r") as f:
            form_json = json.loads(f.read())

        # Phase 1: Normalize
        normalized = normalize_form_data(form_json)
        
        # Verify Phase 1 output
        assert "case_info" in normalized
        assert "plaintiffs" in normalized
        assert "defendants" in normalized
        
        # Should have 3 plaintiffs (2 HoH, 1 non-HoH) and 2 defendants
        assert len(normalized["plaintiffs"]) == 3
        assert len(normalized["defendants"]) == 2

        # Phase 2: Build datasets
        result = build_datasets(normalized)
        
        # Verify Phase 2 output
        assert "datasets" in result
        assert "metadata" in result
        
        # Should have 4 datasets: 2 HoH × 2 defendants
        assert result["metadata"]["total_datasets"] == 4
        assert result["metadata"]["hoh_count"] == 2
        assert result["metadata"]["defendant_count"] == 2
        assert result["metadata"]["non_hoh_plaintiffs"] == 1
        assert len(result["datasets"]) == 4

        # Verify dataset structure
        for dataset in result["datasets"]:
            assert "dataset_id" in dataset
            assert "case_id" in dataset
            assert "plaintiff" in dataset
            assert "defendant" in dataset
            assert "case_metadata" in dataset
            assert "discovery_data" in dataset

        # Verify specific datasets exist
        dataset_ids = [d["dataset_id"] for d in result["datasets"]]
        expected_ids = [
            "1-VTSxIZ-t5dfqS",  # Clark Kent × Tony Stark
            "1-VTSxIZ-8WCXCG",  # Clark Kent × Steve Rogers
            "1-4pyhfl-t5dfqS",  # Lois Lane × Tony Stark
            "1-4pyhfl-8WCXCG"   # Lois Lane × Steve Rogers
        ]
        
        for expected_id in expected_ids:
            assert expected_id in dataset_ids

    def test_end_to_end_data_preservation(self):
        """Test that data is preserved through the pipeline."""
        # Simple test case
        form_json = {
            "Form": {"Id": "test-case"},
            "PlaintiffDetails": [
                {
                    "Id": "P1",
                    "PlaintiffItemNumberName": {
                        "First": "Test",
                        "FirstAndLast": "Test Plaintiff",
                        "Last": "Plaintiff"
                    },
                    "HeadOfHousehold": True,
                    "ItemNumber": 1,
                    "PlaintiffItemNumberDiscovery": {
                        "Vermin": ["Rats", "Mice"],
                        "Injury Issues": True
                    }
                }
            ],
            "DefendantDetails2": [
                {
                    "Id": "D1",
                    "DefendantItemNumberName": {
                        "First": "Test",
                        "FirstAndLast": "Test Defendant",
                        "Last": "Defendant"
                    },
                    "DefendantItemNumberType": "LLC",
                    "DefendantItemNumberManagerOwner": "Manager",
                    "ItemNumber": 1
                }
            ],
            "Full_Address": {
                "StreetAddress": "123 Test St",
                "City": "Test City",
                "State": "TC",
                "PostalCode": "12345"
            },
            "Filing city": "Test Filing City"
        }

        # Phase 1: Normalize
        normalized = normalize_form_data(form_json)
        
        # Phase 2: Build datasets
        result = build_datasets(normalized)
        
        # Verify data preservation
        dataset = result["datasets"][0]
        
        # Check plaintiff data
        assert dataset["plaintiff"]["plaintiff_id"] == "P1"
        assert dataset["plaintiff"]["full_name"] == "Test Plaintiff"
        
        # Check defendant data
        assert dataset["defendant"]["defendant_id"] == "D1"
        assert dataset["defendant"]["full_name"] == "Test Defendant"
        assert dataset["defendant"]["entity_type"] == "LLC"
        assert dataset["defendant"]["role"] == "Manager"
        
        # Check case metadata
        assert dataset["case_metadata"]["property_address"] == "123 Test St"
        assert dataset["case_metadata"]["city"] == "Test City"
        assert dataset["case_metadata"]["state"] == "TC"
        assert dataset["case_metadata"]["zip"] == "12345"
        assert dataset["case_metadata"]["filing_city"] == "Test Filing City"
        
        # Check discovery data
        assert dataset["discovery_data"]["vermin"] == ["Rats", "Mice"]
        assert dataset["discovery_data"]["has_injury"] is True

    def test_end_to_end_error_handling(self):
        """Test error handling in the pipeline."""
        # Test with invalid form data (no HoH plaintiffs)
        invalid_form = {
            "Form": {"Id": "invalid"},
            "PlaintiffDetails": [
                {
                    "Id": "P1",
                    "PlaintiffItemNumberName": {
                        "First": "Non",
                        "Last": "HoH",
                        "FirstAndLast": "Non HoH"
                    },
                    "HeadOfHousehold": False,
                    "ItemNumber": 1
                }
            ],
            "DefendantDetails2": [
                {
                    "Id": "D1",
                    "DefendantItemNumberName": {
                        "First": "Test",
                        "Last": "Defendant",
                        "FirstAndLast": "Test Defendant"
                    },
                    "DefendantItemNumberType": "LLC",
                    "DefendantItemNumberManagerOwner": "Manager",
                    "ItemNumber": 1
                }
            ],
            "Full_Address": {
                "StreetAddress": "123 Test St",
                "City": "Test City",
                "State": "TC",
                "PostalCode": "12345"
            },
            "Filing city": "Test City"
        }

        # Phase 1 should succeed
        normalized = normalize_form_data(invalid_form)
        
        # Phase 2 should fail with appropriate error
        with pytest.raises(Exception) as exc_info:
            build_datasets(normalized)
        
        assert "No Head of Household plaintiffs found" in str(exc_info.value)

    def test_end_to_end_performance(self):
        """Test pipeline performance with multiple cases."""
        import time
        
        # Create multiple test cases
        test_cases = []
        for i in range(10):
            form_json = {
                "Form": {"Id": f"case-{i}"},
                "PlaintiffDetails": [
                    {
                        "Id": f"P{i}",
                        "PlaintiffItemNumberName": {
                            "First": f"Plaintiff{i}",
                            "Last": "Test",
                            "FirstAndLast": f"Plaintiff {i} Test"
                        },
                        "HeadOfHousehold": True,
                        "ItemNumber": 1,
                        "PlaintiffItemNumberDiscovery": {"Vermin": ["Rats"]}
                    }
                ],
                "DefendantDetails2": [
                    {
                        "Id": f"D{i}",
                        "DefendantItemNumberName": {
                            "First": f"Defendant{i}",
                            "Last": "Test",
                            "FirstAndLast": f"Defendant {i} Test"
                        },
                        "DefendantItemNumberType": "LLC",
                        "DefendantItemNumberManagerOwner": "Manager",
                        "ItemNumber": 1
                    }
                ],
                "Full_Address": {
                    "StreetAddress": f"{i} Test St",
                    "City": "Test City",
                    "State": "TC",
                    "PostalCode": "12345"
                },
                "Filing city": "Test City"
            }
            test_cases.append(form_json)

        # Measure performance
        start_time = time.time()
        
        for form_json in test_cases:
            # Phase 1: Normalize
            normalized = normalize_form_data(form_json)
            
            # Phase 2: Build datasets
            result = build_datasets(normalized)
            
            # Verify output
            assert result["metadata"]["total_datasets"] == 1
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process 10 cases in reasonable time (< 1 second)
        assert processing_time < 1.0
        print(f"Processed 10 cases in {processing_time:.3f} seconds")
