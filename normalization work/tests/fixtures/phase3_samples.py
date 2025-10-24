"""
Test fixtures for Phase 3: Flag Processors

This module provides sample data for testing the flag processors.
"""

# Sample discovery data with all vermin types
FULL_VERMIN_DISCOVERY = {
    "vermin": ["Rats/Mice", "Bedbugs", "Skunks", "Bats", "Raccoons", "Pigeons", "Opossums"]
}

# Sample discovery data with all insect types
FULL_INSECT_DISCOVERY = {
    "insects": ["Ants", "Roaches", "Flies", "Bedbugs", "Wasps", "Hornets", "Spiders", "Termites", "Mosquitos", "Bees"]
}

# Sample discovery data with plumbing issues
FULL_PLUMBING_DISCOVERY = {
    "plumbing": [
        "Toilet", "Shower", "Bath", "Fixtures", "Leaks",
        "Insufficient water pressure", "No hot water", "No cold water",
        "Sewage coming out", "Clogged toilets", "Clogged bath",
        "Clogged sinks", "Clogged shower", "No Clean Water Supply", "Unsanitary water"
    ]
}

# Sample discovery data with HVAC issues
FULL_HVAC_DISCOVERY = {
    "hvac": ["Air Conditioner", "Heater", "Ventilation", "HVAC"]
}

# Sample discovery data with electrical issues
FULL_ELECTRICAL_DISCOVERY = {
    "electrical": ["Outlets", "Panel", "Wall Switches", "Exterior Lighting", "Interior Lighting", "Light Fixtures", "Fans"]
}

# Sample discovery data with fire hazard issues
FULL_FIRE_HAZARD_DISCOVERY = {
    "fire_hazard": ["Smoke Alarms", "Fire Extinguisher", "Non-compliant electricity", "Non-GFI outlets near water", "Carbon monoxide detectors"]
}

# Sample discovery data with government entities
FULL_GOVERNMENT_DISCOVERY = {
    "government_entities": [
        "Health Department", "Housing Authority", "Code Enforcement",
        "Fire Department", "Police Department", "Department of Environmental Health",
        "Department of Health Services"
    ]
}

# Sample discovery data with appliances
FULL_APPLIANCES_DISCOVERY = {
    "appliances": ["Stove", "Dishwasher", "Washer/dryer", "Oven", "Microwave", "Garbage disposal", "Refrigerator"]
}

# Sample discovery data with direct booleans
FULL_DIRECT_BOOLEAN_DISCOVERY = {
    "has_injury": True,
    "has_nonresponsive_landlord": True,
    "has_unauthorized_entries": False,
    "has_stolen_items": True,
    "has_damaged_items": False,
    "has_age_discrimination": False,
    "has_racial_discrimination": True,
    "has_disability_discrimination": False
}

# Empty discovery data
EMPTY_DISCOVERY = {
    "vermin": [],
    "insects": [],
    "plumbing": [],
    "hvac": [],
    "electrical": [],
    "fire_hazard": [],
    "government_entities": [],
    "appliances": [],
    "has_injury": False,
    "has_nonresponsive_landlord": False,
    "has_unauthorized_entries": False,
    "has_stolen_items": False,
    "has_damaged_items": False,
    "has_age_discrimination": False,
    "has_racial_discrimination": False,
    "has_disability_discrimination": False
}

# Partial discovery data (some categories populated)
PARTIAL_DISCOVERY = {
    "vermin": ["Rats/Mice", "Bedbugs"],
    "insects": ["Ants", "Roaches"],
    "plumbing": ["Toilet", "Leaks"],
    "hvac": [],
    "electrical": ["Outlets"],
    "fire_hazard": [],
    "government_entities": [],
    "appliances": [],
    "has_injury": True,
    "has_nonresponsive_landlord": False,
    "has_unauthorized_entries": False,
    "has_stolen_items": False,
    "has_damaged_items": False,
    "has_age_discrimination": False,
    "has_racial_discrimination": False,
    "has_disability_discrimination": False
}

# Complete discovery data (all categories populated)
COMPLETE_DISCOVERY = {
    **FULL_VERMIN_DISCOVERY,
    **FULL_INSECT_DISCOVERY,
    **FULL_PLUMBING_DISCOVERY,
    **FULL_HVAC_DISCOVERY,
    **FULL_ELECTRICAL_DISCOVERY,
    **FULL_FIRE_HAZARD_DISCOVERY,
    **FULL_GOVERNMENT_DISCOVERY,
    **FULL_APPLIANCES_DISCOVERY,
    **FULL_DIRECT_BOOLEAN_DISCOVERY
}

# Sample dataset for testing
SAMPLE_DATASET = {
    "dataset_id": "test-case-123",
    "case_id": "test-case",
    "plaintiff": {
        "plaintiff_id": "P1",
        "first_name": "Test",
        "last_name": "Plaintiff",
        "full_name": "Test Plaintiff",
        "unit_number": "1"
    },
    "defendant": {
        "defendant_id": "D1",
        "first_name": "Test",
        "last_name": "Defendant",
        "full_name": "Test Defendant",
        "entity_type": "LLC",
        "role": "Manager"
    },
    "case_metadata": {
        "property_address": "123 Test St",
        "property_address_with_unit": "123 Test St Unit 1",
        "city": "Test City",
        "state": "TC",
        "zip": "12345",
        "filing_city": "Test Filing City",
        "filing_county": "Test County"
    },
    "discovery_data": PARTIAL_DISCOVERY
}

# Sample dataset collection
SAMPLE_DATASET_COLLECTION = {
    "datasets": [
        SAMPLE_DATASET,
        {
            **SAMPLE_DATASET,
            "dataset_id": "test-case-456",
            "plaintiff": {
                **SAMPLE_DATASET["plaintiff"],
                "plaintiff_id": "P2",
                "full_name": "Test Plaintiff 2"
            }
        }
    ],
    "metadata": {
        "total_datasets": 2,
        "hoh_count": 1,
        "defendant_count": 1,
        "non_hoh_plaintiffs": 0
    }
}
