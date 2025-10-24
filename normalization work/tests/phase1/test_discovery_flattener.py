"""
Test suite for Phase 1: Discovery Flattener Module

Tests the discovery flattening functionality including key normalization,
array processing, and boolean flag extraction.
"""

import pytest
from typing import Any

from src.phase1.discovery_flattener import (
    normalize_array_keys,
    extract_boolean_flags,
    flatten_discovery,
    _create_empty_discovery,
    KEY_MAPPINGS,
)


class TestNormalizeArrayKeys:
    """Test the normalize_array_keys function."""

    def test_normalize_all_arrays(self):
        """Test normalizing all discovery arrays."""
        discovery = {
            "Vermin": ["Rats/Mice", "Bedbugs"],
            "Insects": ["Roaches", "Ants"],
            "HVAC": ["Air Conditioner"],
            "Electrical": ["Outlets", "Panel"],
            "Fire Hazard": ["Smoke Alarms"],
            "Specific Government Entity Contacted": ["Health Department"],
            "Appliances": ["Stove", "Refrigerator"],
            "Plumbing": ["Toilet", "Leaks"],
            "Cabinets": ["Broken"],
            "Flooring": ["Uneven", "Carpet"],
            "Windows": ["Broken", "Leaks"],
            "Doors": ["Broken", "Locks"],
            "Structure": ["Hole in wall"],
            "Common areas": ["Mailbox broken"],
            "Select Trash Problems": ["Inadequate receptacles"],
            "Nuisance": ["Noisy neighbors"],
            "Health hazard": ["Mold", "Mildew"],
            "Harassment": ["Eviction threats"],
            "Select Notices Issues": ["3-day", "30-day"],
            "Checkbox 44n6i": ["Water shutoffs"],
            "Select Safety Issues": ["Broken doors"],
        }
        
        normalized = normalize_array_keys(discovery)
        
        # Test array fields
        assert normalized["vermin"] == ["Rats/Mice", "Bedbugs"]
        assert normalized["insects"] == ["Roaches", "Ants"]
        assert normalized["hvac"] == ["Air Conditioner"]
        assert normalized["electrical"] == ["Outlets", "Panel"]
        assert normalized["fire_hazard"] == ["Smoke Alarms"]
        assert normalized["government_entities"] == ["Health Department"]
        assert normalized["appliances"] == ["Stove", "Refrigerator"]
        assert normalized["plumbing"] == ["Toilet", "Leaks"]
        assert normalized["cabinets"] == ["Broken"]
        assert normalized["flooring"] == ["Uneven", "Carpet"]
        assert normalized["windows"] == ["Broken", "Leaks"]
        assert normalized["doors"] == ["Broken", "Locks"]
        assert normalized["structure"] == ["Hole in wall"]
        assert normalized["common_areas"] == ["Mailbox broken"]
        assert normalized["trash_problems"] == ["Inadequate receptacles"]
        assert normalized["nuisance"] == ["Noisy neighbors"]
        assert normalized["health_hazard"] == ["Mold", "Mildew"]
        assert normalized["harassment"] == ["Eviction threats"]
        assert normalized["notices"] == ["3-day", "30-day"]
        assert normalized["utility_interruptions"] == ["Water shutoffs"]
        assert normalized["safety_issues"] == ["Broken doors"]

    def test_normalize_boolean_flags(self):
        """Test normalizing boolean flags."""
        discovery = {
            "Injury Issues": True,
            "Nonresponsive landlord Issues": False,
            "Unauthorized entries": True,
            "Stolen items": False,
            "Damaged items": True,
            "Age discrimination": False,
            "Racial Discrimination": True,
            "Disability discrimination": False,
            "Security Deposit": True,
        }
        
        normalized = normalize_array_keys(discovery)
        
        # Test boolean flags
        assert normalized["has_injury"] is True
        assert normalized["has_nonresponsive_landlord"] is False
        assert normalized["has_unauthorized_entries"] is True
        assert normalized["has_stolen_items"] is False
        assert normalized["has_damaged_items"] is True
        assert normalized["has_age_discrimination"] is False
        assert normalized["has_racial_discrimination"] is True
        assert normalized["has_disability_discrimination"] is False
        assert normalized["has_security_deposit_issues"] is True

    def test_normalize_missing_keys(self):
        """Test normalizing with missing keys."""
        discovery = {
            "Vermin": ["Rats/Mice"],
            "Insects": ["Roaches"],
            # Missing other keys
        }
        
        normalized = normalize_array_keys(discovery)
        
        # Present keys should be normalized
        assert normalized["vermin"] == ["Rats/Mice"]
        assert normalized["insects"] == ["Roaches"]
        
        # Missing array keys should be empty lists
        assert normalized["hvac"] == []
        assert normalized["electrical"] == []
        assert normalized["fire_hazard"] == []
        
        # Missing boolean keys should be False
        assert normalized["has_injury"] is False
        assert normalized["has_nonresponsive_landlord"] is False

    def test_normalize_empty_discovery(self):
        """Test normalizing empty discovery object."""
        discovery = {}
        
        normalized = normalize_array_keys(discovery)
        
        # All array keys should be empty lists
        array_keys = [
            "vermin", "insects", "hvac", "electrical", "fire_hazard",
            "government_entities", "appliances", "plumbing", "cabinets",
            "flooring", "windows", "doors", "structure", "common_areas",
            "trash_problems", "nuisance", "health_hazard", "harassment",
            "notices", "utility_interruptions", "safety_issues"
        ]
        
        for key in array_keys:
            assert normalized[key] == []
        
        # All boolean keys should be False
        boolean_keys = [
            "has_injury", "has_nonresponsive_landlord", "has_unauthorized_entries",
            "has_stolen_items", "has_damaged_items", "has_age_discrimination",
            "has_racial_discrimination", "has_disability_discrimination",
            "has_security_deposit_issues"
        ]
        
        for key in boolean_keys:
            assert normalized[key] is False

    def test_normalize_non_list_values(self):
        """Test normalizing non-list values."""
        discovery = {
            "Vermin": "Not a list",  # Should become empty list
            "Insects": ["Roaches"],  # Should remain as list
            "Injury Issues": "true",  # String boolean
        }
        
        normalized = normalize_array_keys(discovery)
        
        assert normalized["vermin"] == []  # Non-list becomes empty list
        assert normalized["insects"] == ["Roaches"]  # List remains
        assert normalized["has_injury"] is True  # String "true" becomes True

    def test_normalize_preserves_array_values(self):
        """Test that array values are preserved exactly."""
        discovery = {
            "Vermin": ["Rats/Mice", "Bedbugs", "Skunks"],
            "Insects": ["Roaches", "Ants", "Flies", "Bedbugs"],
            "HVAC": ["Air Conditioner", "Heater", "Venitlation"],  # Note: typo preserved
        }
        
        normalized = normalize_array_keys(discovery)
        
        # Values should be preserved exactly, including case and typos
        assert normalized["vermin"] == ["Rats/Mice", "Bedbugs", "Skunks"]
        assert normalized["insects"] == ["Roaches", "Ants", "Flies", "Bedbugs"]
        assert normalized["hvac"] == ["Air Conditioner", "Heater", "Venitlation"]


class TestExtractBooleanFlags:
    """Test the extract_boolean_flags function."""

    def test_extract_all_boolean_flags(self):
        """Test extracting all boolean flags."""
        discovery = {
            "Injury Issues": True,
            "Nonresponsive landlord Issues": False,
            "Unauthorized entries": True,
            "Stolen items": False,
            "Damaged items": True,
            "Age discrimination": False,
            "Racial Discrimination": True,
            "Disability discrimination": False,
            "Security Deposit": True,
        }
        
        flags = extract_boolean_flags(discovery)
        
        assert flags["has_injury"] is True
        assert flags["has_nonresponsive_landlord"] is False
        assert flags["has_unauthorized_entries"] is True
        assert flags["has_stolen_items"] is False
        assert flags["has_damaged_items"] is True
        assert flags["has_age_discrimination"] is False
        assert flags["has_racial_discrimination"] is True
        assert flags["has_disability_discrimination"] is False
        assert flags["has_security_deposit_issues"] is True

    def test_extract_missing_boolean_flags(self):
        """Test extracting with missing boolean flags."""
        discovery = {
            "Injury Issues": True,
            # Missing other boolean flags
        }
        
        flags = extract_boolean_flags(discovery)
        
        assert flags["has_injury"] is True
        assert flags["has_nonresponsive_landlord"] is False  # Default
        assert flags["has_unauthorized_entries"] is False  # Default

    def test_extract_boolean_coercion(self):
        """Test boolean coercion for non-boolean values."""
        discovery = {
            "Injury Issues": "true",  # String
            "Nonresponsive landlord Issues": 1,  # Number
            "Unauthorized entries": "",  # Empty string
            "Stolen items": None,  # None
        }
        
        flags = extract_boolean_flags(discovery)
        
        assert flags["has_injury"] is True  # "true" -> True
        assert flags["has_nonresponsive_landlord"] is True  # 1 -> True
        assert flags["has_unauthorized_entries"] is False  # "" -> False
        assert flags["has_stolen_items"] is False  # None -> False

    def test_extract_empty_discovery(self):
        """Test extracting from empty discovery."""
        discovery = {}
        
        flags = extract_boolean_flags(discovery)
        
        # All flags should be False
        boolean_keys = [
            "has_injury", "has_nonresponsive_landlord", "has_unauthorized_entries",
            "has_stolen_items", "has_damaged_items", "has_age_discrimination",
            "has_racial_discrimination", "has_disability_discrimination",
            "has_security_deposit_issues"
        ]
        
        for key in boolean_keys:
            assert flags[key] is False


class TestFlattenDiscovery:
    """Test the flatten_discovery function."""

    def test_flatten_complete_discovery(self):
        """Test flattening complete discovery object."""
        discovery = {
            "VerminIssue": True,
            "Vermin": ["Rats/Mice", "Bedbugs"],
            "InsectIssues": True,
            "Insects": ["Roaches", "Ants"],
            "HVACIssues": False,
            "HVAC": [],
            "Electrical": ["Outlets"],
            "ElectricalIssues": True,
            "FireHazardIssues": True,
            "Fire Hazard": ["Smoke Alarms"],
            "GovernmentEntityContacted": True,
            "Specific Government Entity Contacted": ["Health Department"],
            "AppliancesIssues": True,
            "Appliances": ["Stove", "Refrigerator"],
            "PlumbingIssues": True,
            "Plumbing": ["Toilet", "Leaks"],
            "CabinetsIssues": False,
            "Cabinets": [],
            "FlooringIssues": True,
            "Flooring": ["Uneven", "Carpet"],
            "WindowsIssues": True,
            "Windows": ["Broken", "Leaks"],
            "DoorIssues": True,
            "Doors": ["Broken", "Locks"],
            "StructureIssues": True,
            "Structure": ["Hole in wall"],
            "CommonAreasIssues": True,
            "Common areas": ["Mailbox broken"],
            "TrashProblems": True,
            "Select Trash Problems": ["Inadequate receptacles"],
            "NuisanceIssues": True,
            "Nuisance": ["Noisy neighbors"],
            "Health hazard": ["Mold", "Mildew"],
            "HealthHazardIssues": True,
            "HarassmentIssues": True,
            "Harassment": ["Eviction threats"],
            "NoticesIssues": True,
            "Select Notices Issues": ["3-day", "30-day"],
            "UtilityIssues": True,
            "Checkbox 44n6i": ["Water shutoffs"],
            "Injury Issues": True,
            "Nonresponsive landlord Issues": False,
            "Unauthorized entries": True,
            "Stolen items": False,
            "Damaged items": True,
            "Age discrimination": False,
            "Racial Discrimination": True,
            "Disability discrimination": False,
            "Unit": "1",
            "Safety": True,
            "Select Safety Issues": ["Broken doors"],
            "Security Deposit": True,
        }
        
        flattened = flatten_discovery(discovery)
        
        # Test array fields
        assert flattened["vermin"] == ["Rats/Mice", "Bedbugs"]
        assert flattened["insects"] == ["Roaches", "Ants"]
        assert flattened["hvac"] == []
        assert flattened["electrical"] == ["Outlets"]
        assert flattened["fire_hazard"] == ["Smoke Alarms"]
        assert flattened["government_entities"] == ["Health Department"]
        assert flattened["appliances"] == ["Stove", "Refrigerator"]
        assert flattened["plumbing"] == ["Toilet", "Leaks"]
        assert flattened["cabinets"] == []
        assert flattened["flooring"] == ["Uneven", "Carpet"]
        assert flattened["windows"] == ["Broken", "Leaks"]
        assert flattened["doors"] == ["Broken", "Locks"]
        assert flattened["structure"] == ["Hole in wall"]
        assert flattened["common_areas"] == ["Mailbox broken"]
        assert flattened["trash_problems"] == ["Inadequate receptacles"]
        assert flattened["nuisance"] == ["Noisy neighbors"]
        assert flattened["health_hazard"] == ["Mold", "Mildew"]
        assert flattened["harassment"] == ["Eviction threats"]
        assert flattened["notices"] == ["3-day", "30-day"]
        assert flattened["utility_interruptions"] == ["Water shutoffs"]
        assert flattened["safety_issues"] == ["Broken doors"]
        
        # Test boolean flags
        assert flattened["has_injury"] is True
        assert flattened["has_nonresponsive_landlord"] is False
        assert flattened["has_unauthorized_entries"] is True
        assert flattened["has_stolen_items"] is False
        assert flattened["has_damaged_items"] is True
        assert flattened["has_age_discrimination"] is False
        assert flattened["has_racial_discrimination"] is True
        assert flattened["has_disability_discrimination"] is False
        assert flattened["has_security_deposit_issues"] is True

    def test_flatten_empty_discovery(self):
        """Test flattening empty discovery object."""
        discovery = {}
        
        flattened = flatten_discovery(discovery)
        
        # Should return empty discovery structure
        expected = _create_empty_discovery()
        assert flattened == expected

    def test_flatten_none_discovery(self):
        """Test flattening None discovery."""
        flattened = flatten_discovery(None)
        
        # Should return empty discovery structure
        expected = _create_empty_discovery()
        assert flattened == expected

    def test_flatten_partial_discovery(self):
        """Test flattening discovery with only some fields."""
        discovery = {
            "Vermin": ["Rats/Mice"],
            "Injury Issues": True,
            # Missing most other fields
        }
        
        flattened = flatten_discovery(discovery)
        
        # Present fields should be normalized
        assert flattened["vermin"] == ["Rats/Mice"]
        assert flattened["has_injury"] is True
        
        # Missing fields should have defaults
        assert flattened["insects"] == []
        assert flattened["hvac"] == []
        assert flattened["has_nonresponsive_landlord"] is False

    def test_flatten_preserves_exact_values(self):
        """Test that flattening preserves exact array values."""
        discovery = {
            "Vermin": ["Rats/Mice", "Bedbugs", "Skunks", "Bats", "Racoons", "Pigeons", "Opossum"],
            "Insects": ["Ants", "Roaches", "Flies", "Bedbugs", "Wasps", "Hornets", "Spiders", "Termites", "Mosquitos", "Bees"],
            "HVAC": ["Air Conditioner", "Heater", "Venitlation"],  # Note: typo preserved
        }
        
        flattened = flatten_discovery(discovery)
        
        # Values should be preserved exactly
        assert flattened["vermin"] == ["Rats/Mice", "Bedbugs", "Skunks", "Bats", "Racoons", "Pigeons", "Opossum"]
        assert flattened["insects"] == ["Ants", "Roaches", "Flies", "Bedbugs", "Wasps", "Hornets", "Spiders", "Termites", "Mosquitos", "Bees"]
        assert flattened["hvac"] == ["Air Conditioner", "Heater", "Venitlation"]


class TestCreateEmptyDiscovery:
    """Test the _create_empty_discovery function."""

    def test_create_empty_discovery_structure(self):
        """Test creating empty discovery structure."""
        empty = _create_empty_discovery()
        
        # All array fields should be empty lists
        array_keys = [
            "vermin", "insects", "hvac", "electrical", "fire_hazard",
            "government_entities", "appliances", "plumbing", "cabinets",
            "flooring", "windows", "doors", "structure", "common_areas",
            "trash_problems", "nuisance", "health_hazard", "harassment",
            "notices", "utility_interruptions", "safety_issues"
        ]
        
        for key in array_keys:
            assert key in empty
            assert empty[key] == []
        
        # All boolean fields should be False
        boolean_keys = [
            "has_injury", "has_nonresponsive_landlord", "has_unauthorized_entries",
            "has_stolen_items", "has_damaged_items", "has_age_discrimination",
            "has_racial_discrimination", "has_disability_discrimination",
            "has_security_deposit_issues"
        ]
        
        for key in boolean_keys:
            assert key in empty
            assert empty[key] is False

    def test_create_empty_discovery_completeness(self):
        """Test that empty discovery has all expected keys."""
        empty = _create_empty_discovery()
        
        # Should have exactly the keys from KEY_MAPPINGS
        expected_keys = set(KEY_MAPPINGS.values())
        actual_keys = set(empty.keys())
        
        assert expected_keys == actual_keys


class TestKeyMappings:
    """Test the KEY_MAPPINGS constant."""

    def test_key_mappings_completeness(self):
        """Test that KEY_MAPPINGS covers all expected mappings."""
        # Test that all expected original keys are mapped
        expected_original_keys = [
            "Vermin", "Insects", "HVAC", "Electrical", "Fire Hazard",
            "Specific Government Entity Contacted", "Appliances", "Plumbing",
            "Cabinets", "Flooring", "Windows", "Doors", "Structure",
            "Common areas", "Select Trash Problems", "Nuisance",
            "Health hazard", "Harassment", "Select Notices Issues",
            "Checkbox 44n6i", "Select Safety Issues",
            "Injury Issues", "Nonresponsive landlord Issues",
            "Unauthorized entries", "Stolen items", "Damaged items",
            "Age discrimination", "Racial Discrimination",
            "Disability discrimination", "Security Deposit"
        ]
        
        for key in expected_original_keys:
            assert key in KEY_MAPPINGS, f"Missing mapping for key: {key}"
        
        # Test that all normalized keys are snake_case
        for normalized_key in KEY_MAPPINGS.values():
            assert "_" in normalized_key or normalized_key.startswith("has_") or normalized_key in ["vermin", "insects", "hvac", "electrical", "fire_hazard", "government_entities", "appliances", "plumbing", "cabinets", "flooring", "windows", "doors", "structure", "common_areas", "trash_problems", "nuisance", "health_hazard", "harassment", "notices", "utility_interruptions", "safety_issues"], f"Key not snake_case: {normalized_key}"

    def test_key_mappings_consistency(self):
        """Test that KEY_MAPPINGS is consistent."""
        # Test that boolean keys start with "has_"
        boolean_keys = [
            "Injury Issues", "Nonresponsive landlord Issues",
            "Unauthorized entries", "Stolen items", "Damaged items",
            "Age discrimination", "Racial Discrimination",
            "Disability discrimination", "Security Deposit"
        ]
        
        for original_key in boolean_keys:
            normalized_key = KEY_MAPPINGS[original_key]
            assert normalized_key.startswith("has_"), f"Boolean key should start with 'has_': {normalized_key}"
        
        # Test that array keys don't start with "has_"
        array_keys = [
            "Vermin", "Insects", "HVAC", "Electrical", "Fire Hazard",
            "Specific Government Entity Contacted", "Appliances", "Plumbing",
            "Cabinets", "Flooring", "Windows", "Doors", "Structure",
            "Common areas", "Select Trash Problems", "Nuisance",
            "Health hazard", "Harassment", "Select Notices Issues",
            "Checkbox 44n6i", "Select Safety Issues"
        ]
        
        for original_key in array_keys:
            normalized_key = KEY_MAPPINGS[original_key]
            assert not normalized_key.startswith("has_"), f"Array key should not start with 'has_': {normalized_key}"


class TestIntegration:
    """Integration tests for the discovery flattener module."""

    def test_flatten_goaloutput_discovery(self):
        """Test flattening discovery from goalOutput.md example."""
        # Clark Kent's discovery from goalOutput.md
        clark_discovery = {
            "VerminIssue": True,
            "Vermin": ["Rats/Mice", "Skunks", "Bats", "Racoons", "Pigeons", "Opossum"],
            "InsectIssues": True,
            "Insects": ["Ants", "Roaches", "Flies", "Bedbugs", "Wasps", "Hornets", "Spiders", "Termites", "Mosquitos", "Bees"],
            "HVACIssues": True,
            "HVAC": ["Air Conditioner", "Heater", "Venitlation"],
            "Electrical": ["Outlets", "Panel", "Wall Switches", "Exterior Lighting", "Interior Lighting", "Light Fixtures", "Fans"],
            "ElectricalIssues": True,
            "FireHazardIssues": True,
            "GovernmentEntityContacted": True,
            "AppliancesIssues": True,
            "PlumbingIssues": True,
            "CabinetsIssues": True,
            "Fire Hazard": ["Smoke Alarms", "Fire Extinguisher", "Non-compliant electricity", "Non-gfi electrical outlets by water", "Carbon monoxide detectors"],
            "Specific Government Entity Contacted": ["Health Department", "Housing Authority", "Code Enforcement", "Fire Department", "Police Department", "Department of Environmental Health", "Department of Health Services"],
            "Appliances": ["Stove", "Dishwasher", "Washer/dryer", "Oven", "Microwave", "Garbage disposal", "Refrigerator"],
            "Plumbing": ["Toilet", "Shower", "Bath", "Fixtures", "Leaks", "Insufficient water pressure", "No hot water", "No cold water", "Sewage coming out", "Clogged toilets", "Clogged bath", "Clogged sinks", "Clogged shower", "No Clean Water Supply", "Unsanitary water"],
            "Cabinets": ["Broken", "Hinges", "Alignment"],
            "FlooringIssues": True,
            "WindowsIssues": True,
            "DoorIssues": True,
            "Flooring": ["Uneven", "Carpet", "Nails sticking out", "Tiles"],
            "Windows": ["Broken", "Screens", "Leaks", "Do not lock", "Missing Windows", "Broken or Missing screens"],
            "Doors": ["Broken", "Knobs", "Locks", "Broken hinges", "Sliding glass doors", "Ineffective waterproofing", "Water intrusion and/or insects", "Do Not Close Properly"],
            "StructureIssues": True,
            "Structure": ["Bumps in ceiling", "Hole in ceiling", "Water stains on ceiling", "Water stains on wall", "Hole in wall", "Paint", "Exterior deck/porch", "Waterproof toilet", "Waterproof tub", "Staircase", "Basement flood", "Leaks in garage", "Soft Spots due to Leaks", "Uneffective Waterproofing of the tubs or toilet", "Ineffective Weatherproofing of any windows doors"],
            "CommonAreasIssues": True,
            "Common areas": ["Mailbox broken", "Parking area issues", "Damage to cars", "Flooding", "Entrances blocked", "Swimming pool", "Jacuzzi", "Laundry room", "Recreation room", "Gym", "Elevator", "Filth Rubbish Garbage", "Vermin", "Insects", "Broken Gate", "Blocked areas/doors"],
            "TrashProblems": True,
            "Select Trash Problems": ["Inadequate number of receptacles", "Properly servicing and emptying receptacles"],
            "NuisanceIssues": True,
            "Nuisance": ["Drugs", "Smoking", "Noisy neighbors", "Gangs"],
            "Health hazard": ["Mold", "Mildew", "Mushrooms", "Raw sewage on exterior", "Noxious fumes", "Chemicals/paint contamination", "Toxic Water Pollution", "Offensive Odors"],
            "HealthHazardIssues": True,
            "HarassmentIssues": True,
            "Harassment": ["Unlawful Detainer", "Eviction threats", "By defendant", "By maintenance man/workers", "By manager/building staff", "By owner", "Other tenants", "Illegitimate notices", "Refusal to make timely repairs", "Written threats", "Aggressive/inappropriate language", "Physical threats or touching", "Notices singling out one tenant, but not uniformly given to all tenants", "Duplicative notices", "Untimely Response from Landlord"],
            "NoticesIssues": True,
            "Select Notices Issues": ["3-day", "24-hour", "30-day", "60-day", "To quit", "Perform or Quit"],
            "UtilityIssues": True,
            "Checkbox 44n6i": ["Gas leak", "Water shutoffs", "Electricity shutoffs", "Heat Shutoff", "Gas Shutoff"],
            "Injury Issues": True,
            "Nonresponsive landlord Issues": True,
            "Unauthorized entries": True,
            "Stolen items": True,
            "Damaged items": True,
            "Age discrimination": True,
            "Racial Discrimination": True,
            "Disability discrimination": True,
            "Unit": "1",
            "Safety": True,
            "Select Safety Issues": ["Broken/inoperable security gate", "Broken doors", "Unauthorized entries", "Broken buzzer to get in", "Security cameras", "Inoperable locks"],
            "Security Deposit": True
        }
        
        flattened = flatten_discovery(clark_discovery)
        
        # Test that all arrays are preserved with exact values
        assert flattened["vermin"] == ["Rats/Mice", "Skunks", "Bats", "Racoons", "Pigeons", "Opossum"]
        assert flattened["insects"] == ["Ants", "Roaches", "Flies", "Bedbugs", "Wasps", "Hornets", "Spiders", "Termites", "Mosquitos", "Bees"]
        assert flattened["hvac"] == ["Air Conditioner", "Heater", "Venitlation"]
        
        # Test that all boolean flags are extracted
        assert flattened["has_injury"] is True
        assert flattened["has_nonresponsive_landlord"] is True
        assert flattened["has_unauthorized_entries"] is True
        assert flattened["has_stolen_items"] is True
        assert flattened["has_damaged_items"] is True
        assert flattened["has_age_discrimination"] is True
        assert flattened["has_racial_discrimination"] is True
        assert flattened["has_disability_discrimination"] is True
        assert flattened["has_security_deposit_issues"] is True

    def test_flatten_empty_plaintiff_discovery(self):
        """Test flattening discovery for non-HoH plaintiff (empty discovery)."""
        # Bruce Wayne's discovery from goalOutput.md (non-HoH, empty discovery)
        bruce_discovery = {
            "VerminIssue": False,
            "Vermin": [],
            "InsectIssues": False,
            "Insects": [],
            "HVACIssues": False,
            "HVAC": [],
            "Electrical": [],
            "ElectricalIssues": False,
            "FireHazardIssues": False,
            "GovernmentEntityContacted": False,
            "AppliancesIssues": False,
            "PlumbingIssues": False,
            "CabinetsIssues": False,
            "Fire Hazard": [],
            "Specific Government Entity Contacted": [],
            "Appliances": [],
            "Plumbing": [],
            "Cabinets": [],
            "FlooringIssues": False,
            "WindowsIssues": False,
            "DoorIssues": False,
            "Flooring": [],
            "Windows": [],
            "Doors": [],
            "StructureIssues": False,
            "Structure": [],
            "CommonAreasIssues": False,
            "Common areas": [],
            "TrashProblems": False,
            "Select Trash Problems": [],
            "NuisanceIssues": False,
            "Nuisance": [],
            "Health hazard": [],
            "HealthHazardIssues": False,
            "HarassmentIssues": False,
            "Harassment": [],
            "NoticesIssues": False,
            "Select Notices Issues": [],
            "UtilityIssues": False,
            "Checkbox 44n6i": [],
            "Injury Issues": False,
            "Nonresponsive landlord Issues": False,
            "Unauthorized entries": False,
            "Stolen items": False,
            "Damaged items": False,
            "Age discrimination": False,
            "Racial Discrimination": False,
            "Disability discrimination": False,
            "Unit": None,
            "Safety": False,
            "Select Safety Issues": [],
            "Security Deposit": False
        }
        
        flattened = flatten_discovery(bruce_discovery)
        
        # All arrays should be empty
        array_keys = ["vermin", "insects", "hvac", "electrical", "fire_hazard", "government_entities", "appliances", "plumbing", "cabinets", "flooring", "windows", "doors", "structure", "common_areas", "trash_problems", "nuisance", "health_hazard", "harassment", "notices", "utility_interruptions", "safety_issues"]
        for key in array_keys:
            assert flattened[key] == []
        
        # All boolean flags should be False
        boolean_keys = ["has_injury", "has_nonresponsive_landlord", "has_unauthorized_entries", "has_stolen_items", "has_damaged_items", "has_age_discrimination", "has_racial_discrimination", "has_disability_discrimination", "has_security_deposit_issues"]
        for key in boolean_keys:
            assert flattened[key] is False
