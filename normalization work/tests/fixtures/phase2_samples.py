"""
Test fixtures for Phase 2: Dataset Builder

This module provides sample data for testing the dataset builder components.
"""

# Single HoH, Single Defendant (Expected: 1 dataset)
SINGLE_HOH_SINGLE_DEFENDANT = {
    "case_info": {
        "case_id": "form-entry-123",
        "property_address": "123 Main St",
        "city": "Los Angeles",
        "state": "CA",
        "zip": "90001",
        "filing_city": "Los Angeles",
        "filing_county": "Los Angeles County"
    },
    "plaintiffs": [
        {
            "plaintiff_id": "P1",
            "first_name": "Clark",
            "last_name": "Kent",
            "full_name": "Clark Kent",
            "is_head_of_household": True,
            "unit_number": "1",
            "discovery": {
                "vermin": ["Rats/Mice", "Skunks"],
                "insects": ["Ants", "Roaches"],
                "has_injury": True,
                "has_nonresponsive_landlord": False
            }
        }
    ],
    "defendants": [
        {
            "defendant_id": "D1",
            "first_name": "Tony",
            "last_name": "Stark",
            "full_name": "Tony Stark",
            "entity_type": "LLC",
            "role": "Manager"
        }
    ]
}

# Multiple HoH, Multiple Defendants (Expected: 4 datasets)
MULTI_HOH_MULTI_DEFENDANT = {
    "case_info": {
        "case_id": "form-entry-456",
        "property_address": "456 Oak Ave",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94102",
        "filing_city": "San Francisco",
        "filing_county": "San Francisco County"
    },
    "plaintiffs": [
        {
            "plaintiff_id": "P1",
            "first_name": "Clark",
            "last_name": "Kent",
            "full_name": "Clark Kent",
            "is_head_of_household": True,
            "unit_number": "1",
            "discovery": {
                "vermin": ["Rats/Mice", "Skunks"],
                "insects": ["Ants", "Roaches"],
                "has_injury": True,
                "has_nonresponsive_landlord": False
            }
        },
        {
            "plaintiff_id": "P2",
            "first_name": "Lois",
            "last_name": "Lane",
            "full_name": "Lois Lane",
            "is_head_of_household": True,
            "unit_number": "2",
            "discovery": {
                "vermin": ["Bats"],
                "insects": ["Flies"],
                "has_injury": False,
                "has_nonresponsive_landlord": True
            }
        }
    ],
    "defendants": [
        {
            "defendant_id": "D1",
            "first_name": "Tony",
            "last_name": "Stark",
            "full_name": "Tony Stark",
            "entity_type": "LLC",
            "role": "Manager"
        },
        {
            "defendant_id": "D2",
            "first_name": "Steve",
            "last_name": "Rogers",
            "full_name": "Steve Rogers",
            "entity_type": "LLC",
            "role": "Owner"
        }
    ]
}

# Mixed Plaintiffs (2 HoH, 1 non-HoH, 2 defendants - Expected: 4 datasets)
MIXED_PLAINTIFFS = {
    "case_info": {
        "case_id": "form-entry-789",
        "property_address": "789 Pine St",
        "city": "San Diego",
        "state": "CA",
        "zip": "92101",
        "filing_city": "San Diego",
        "filing_county": "San Diego County"
    },
    "plaintiffs": [
        {
            "plaintiff_id": "P1",
            "first_name": "Clark",
            "last_name": "Kent",
            "full_name": "Clark Kent",
            "is_head_of_household": True,
            "unit_number": "1",
            "discovery": {
                "vermin": ["Rats/Mice"],
                "insects": ["Ants"],
                "has_injury": True,
                "has_nonresponsive_landlord": False
            }
        },
        {
            "plaintiff_id": "P2",
            "first_name": "Lois",
            "last_name": "Lane",
            "full_name": "Lois Lane",
            "is_head_of_household": True,
            "unit_number": "2",
            "discovery": {
                "vermin": ["Bats"],
                "insects": ["Flies"],
                "has_injury": False,
                "has_nonresponsive_landlord": True
            }
        },
        {
            "plaintiff_id": "P3",
            "first_name": "Bruce",
            "last_name": "Wayne",
            "full_name": "Bruce Wayne",
            "is_head_of_household": False,
            "unit_number": None
            # No discovery data (non-HoH)
        }
    ],
    "defendants": [
        {
            "defendant_id": "D1",
            "first_name": "Tony",
            "last_name": "Stark",
            "full_name": "Tony Stark",
            "entity_type": "LLC",
            "role": "Manager"
        },
        {
            "defendant_id": "D2",
            "first_name": "Steve",
            "last_name": "Rogers",
            "full_name": "Steve Rogers",
            "entity_type": "LLC",
            "role": "Owner"
        }
    ]
}

# Edge Cases
EDGE_CASES = {
    "case_info": {
        "case_id": "form-entry-edge",
        "property_address": "999 Edge St Unit 5",  # Address already has unit
        "city": "Edge City",
        "state": "EC",
        "zip": "99999",
        "filing_city": "Edge City",
        "filing_county": "Edge County"
    },
    "plaintiffs": [
        {
            "plaintiff_id": "P1",
            "first_name": "Edge",
            "last_name": "Case",
            "full_name": "Edge Case",
            "is_head_of_household": True,
            "unit_number": "5",  # Same unit as in address
            "discovery": {
                "vermin": [],
                "insects": [],
                "has_injury": False,
                "has_nonresponsive_landlord": False
            }
        }
    ],
    "defendants": [
        {
            "defendant_id": "D1",
            "first_name": "Edge",
            "last_name": "Defendant",
            "full_name": "Edge Defendant",
            "entity_type": "Corporation",
            "role": "CEO"
        }
    ]
}

# Invalid Cases (for error testing)
INVALID_NO_HOH = {
    "case_info": {
        "case_id": "form-entry-no-hoh",
        "property_address": "123 No HoH St",
        "city": "No HoH City",
        "state": "NH",
        "zip": "00000"
    },
    "plaintiffs": [
        {
            "plaintiff_id": "P1",
            "first_name": "Non",
            "last_name": "HoH",
            "full_name": "Non HoH",
            "is_head_of_household": False,
            "unit_number": None
            # No discovery data
        }
    ],
    "defendants": [
        {
            "defendant_id": "D1",
            "first_name": "Valid",
            "last_name": "Defendant",
            "full_name": "Valid Defendant",
            "entity_type": "LLC",
            "role": "Manager"
        }
    ]
}

INVALID_NO_DEFENDANTS = {
    "case_info": {
        "case_id": "form-entry-no-defendants",
        "property_address": "456 No Defendants St",
        "city": "No Defendants City",
        "state": "ND",
        "zip": "00001"
    },
    "plaintiffs": [
        {
            "plaintiff_id": "P1",
            "first_name": "Valid",
            "last_name": "HoH",
            "full_name": "Valid HoH",
            "is_head_of_household": True,
            "unit_number": "1",
            "discovery": {
                "vermin": [],
                "insects": [],
                "has_injury": False,
                "has_nonresponsive_landlord": False
            }
        }
    ],
    "defendants": []  # Empty defendants list
}

# Complex Discovery Data
COMPLEX_DISCOVERY = {
    "case_info": {
        "case_id": "form-entry-complex",
        "property_address": "789 Complex St",
        "city": "Complex City",
        "state": "CC",
        "zip": "12345",
        "filing_city": "Complex City",
        "filing_county": "Complex County"
    },
    "plaintiffs": [
        {
            "plaintiff_id": "P1",
            "first_name": "Complex",
            "last_name": "Plaintiff",
            "full_name": "Complex Plaintiff",
            "is_head_of_household": True,
            "unit_number": "1",
            "discovery": {
                "vermin": ["Rats/Mice", "Skunks", "Bats", "Raccoons", "Pigeons"],
                "insects": ["Ants", "Roaches", "Flies", "Bedbugs", "Wasps", "Hornets", "Spiders"],
                "hvac": ["Air Conditioner", "Heater", "Ventilation"],
                "electrical": ["Outlets", "Panel", "Wall Switches", "Exterior Lighting"],
                "fire_hazard": ["Smoke Alarms", "Fire Extinguisher", "Non-compliant electricity"],
                "government_entities": ["Health Department", "Housing Authority", "Code Enforcement"],
                "appliances": ["Stove", "Dishwasher", "Washer/dryer", "Oven", "Microwave"],
                "plumbing": ["Toilet", "Insufficient water pressure", "Clogged bath", "Shower"],
                "flooring": ["Uneven", "Carpet", "Nails sticking out", "Tiles"],
                "windows": ["Broken", "Screens", "Leaks", "Do not lock"],
                "doors": ["Broken", "Knobs", "Locks", "Broken hinges"],
                "structure": ["Bumps in ceiling", "Hole in ceiling", "Water stains on ceiling"],
                "common_areas": ["Mailbox broken", "Parking area issues", "Damage to cars"],
                "nuisance": ["Drugs", "Smoking", "Noisy neighbors", "Gangs"],
                "health_hazard": ["Mold", "Mildew", "Mushrooms", "Raw sewage on exterior"],
                "harassment": ["Unlawful Detainer", "Eviction threats", "By defendant"],
                "has_injury": True,
                "has_nonresponsive_landlord": True,
                "has_unauthorized_entries": True,
                "has_stolen_items": True,
                "has_damaged_items": True,
                "has_age_discrimination": False,
                "has_racial_discrimination": False,
                "has_disability_discrimination": False
            }
        }
    ],
    "defendants": [
        {
            "defendant_id": "D1",
            "first_name": "Complex",
            "last_name": "Defendant",
            "full_name": "Complex Defendant",
            "entity_type": "Corporation",
            "role": "CEO"
        }
    ]
}
