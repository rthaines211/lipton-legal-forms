# Phase 1: Input Normalization

## Overview
Transform the current form JSON output into a normalized structure that the discovery processor can consume. This phase focuses on parsing, flattening, and validating the input data.

## Current Input Structure
```json
{
  "Form": {...},
  "PlaintiffDetails": [
    {
      "Id": "4ck5Gw",
      "PlaintiffItemNumberName": {...},
      "PlaintiffItemNumberType": "Individual",
      "PlaintiffItemNumberAgeCategory": ["Adult"],
      "PlaintiffItemNumberDiscovery": {
        "VerminIssue": true,
        "Vermin": ["Rats/Mice", "Bedbugs"],
        "InsectIssues": true,
        "Insects": ["Roaches", "Ants"],
        "Unit": "1",
        ...
      },
      "HeadOfHousehold": true,
      "ItemNumber": 1
    }
  ],
  "DefendantDetails2": [...],
  "Full_Address": {...},
  "Filing city": "Los Angeles",
  "Filing county": "Los Angeles County"
}
```

## Target Normalized Structure
```json
{
  "case_info": {
    "case_id": "form-entry-1729123456789",
    "property_address": "1331 Yorkshire Place NW",
    "city": "Concord",
    "state": "NC",
    "zip": "28027",
    "filing_city": "Los Angeles",
    "filing_county": "Los Angeles County"
  },
  "plaintiffs": [
    {
      "plaintiff_id": "4ck5Gw",
      "first_name": "Clark",
      "last_name": "Kent",
      "full_name": "Clark Kent",
      "plaintiff_type": "Individual",
      "age_category": "Adult",
      "is_head_of_household": true,
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
        "has_injury": false,
        "has_nonresponsive_landlord": false,
        "has_unauthorized_entries": false,
        "has_stolen_items": false,
        "has_damaged_items": false,
        "has_age_discrimination": false,
        "has_racial_discrimination": false,
        "has_disability_discrimination": false,
        "has_security_deposit_issues": false
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
```

## Tasks

### Task 1.1: Create Input Parser Module
**File**: `normalization work/src/phase1/input_parser.py`

**Functions**:
- `parse_form_json(json_data: dict) -> dict`
- `extract_case_info(json_data: dict) -> dict`
- `extract_plaintiffs(json_data: dict) -> list[dict]`
- `extract_defendants(json_data: dict) -> list[dict]`

**Requirements**:
- Handle both original format keys ("Filing city") and normalized keys ("FilingCity")
- Support Full_Address object with all variants (StreetAddress, Line1, etc.)
- Gracefully handle missing optional fields

### Task 1.2: Create Discovery Flattener
**File**: `normalization work/src/phase1/discovery_flattener.py`

**Functions**:
- `flatten_discovery(discovery_obj: dict) -> dict`
- `normalize_array_keys(discovery: dict) -> dict`
- `extract_boolean_flags(discovery: dict) -> dict`

**Mapping Rules**:
```python
KEY_MAPPINGS = {
    # Original Key → Normalized Key
    "Vermin": "vermin",
    "Insects": "insects",
    "HVAC": "hvac",
    "Electrical": "electrical",
    "Fire Hazard": "fire_hazard",
    "Specific Government Entity Contacted": "government_entities",
    "Appliances": "appliances",
    "Plumbing": "plumbing",
    "Cabinets": "cabinets",
    "Flooring": "flooring",
    "Windows": "windows",
    "Doors": "doors",
    "Structure": "structure",
    "Common areas": "common_areas",
    "Select Trash Problems": "trash_problems",
    "Nuisance": "nuisance",
    "Health hazard": "health_hazard",
    "Harassment": "harassment",
    "Select Notices Issues": "notices",
    "Checkbox 44n6i": "utility_interruptions",
    "Select Safety Issues": "safety_issues",
    # Boolean flags
    "Injury Issues": "has_injury",
    "Nonresponsive landlord Issues": "has_nonresponsive_landlord",
    "Unauthorized entries": "has_unauthorized_entries",
    "Stolen items": "has_stolen_items",
    "Damaged items": "has_damaged_items",
    "Age discrimination": "has_age_discrimination",
    "Racial Discrimination": "has_racial_discrimination",
    "Disability discrimination": "has_disability_discrimination",
    "Security Deposit": "has_security_deposit_issues"
}
```

### Task 1.3: Create Field Validator
**File**: `normalization work/src/phase1/validators.py`

**Functions**:
- `validate_case_info(case_info: dict) -> tuple[bool, list[str]]`
- `validate_plaintiff(plaintiff: dict) -> tuple[bool, list[str]]`
- `validate_defendant(defendant: dict) -> tuple[bool, list[str]]`
- `validate_discovery(discovery: dict) -> tuple[bool, list[str]]`

**Validation Rules**:
- Required fields: property_address, city, state, zip
- At least 1 plaintiff with valid name
- At least 1 defendant with valid name
- Discovery arrays must be lists (empty lists OK)
- Boolean flags must be actual booleans

### Task 1.4: Create Normalization Pipeline
**File**: `normalization work/src/phase1/normalizer.py`

**Main Function**:
```python
def normalize_form_data(form_json: dict) -> dict:
    """
    Main normalization pipeline.

    Args:
        form_json: Raw form JSON output

    Returns:
        Normalized structure ready for dataset builder

    Raises:
        ValidationError: If input fails validation
    """
    # 1. Parse input
    parsed = parse_form_json(form_json)

    # 2. Extract components
    case_info = extract_case_info(parsed)
    plaintiffs = extract_plaintiffs(parsed)
    defendants = extract_defendants(parsed)

    # 3. Flatten discovery for each plaintiff
    for plaintiff in plaintiffs:
        if 'discovery' in plaintiff:
            plaintiff['discovery'] = flatten_discovery(plaintiff['discovery'])

    # 4. Validate
    is_valid, errors = validate_normalized_data({
        'case_info': case_info,
        'plaintiffs': plaintiffs,
        'defendants': defendants
    })

    if not is_valid:
        raise ValidationError(f"Validation failed: {errors}")

    # 5. Return normalized structure
    return {
        'case_info': case_info,
        'plaintiffs': plaintiffs,
        'defendants': defendants
    }
```

## Test Plan

### Test 1.1: Basic Input Parsing
**File**: `tests/phase1/test_input_parser.py`

**Test Cases**:
```python
def test_parse_simple_case():
    """Test parsing a simple case with 1 plaintiff, 1 defendant"""
    # Load sample data from goalOutput.md (Clark Kent example)
    # Assert all fields extracted correctly

def test_parse_complex_case():
    """Test parsing a case with multiple plaintiffs and defendants"""
    # 3 plaintiffs (2 HoH, 1 non-HoH)
    # 2 defendants
    # Assert correct counts and relationships

def test_handle_missing_optional_fields():
    """Test graceful handling of missing optional fields"""
    # Missing unit_number
    # Missing middle name
    # Assert defaults applied correctly

def test_handle_both_key_formats():
    """Test handling both 'Filing city' and 'FilingCity'"""
    # Test with original format
    # Test with normalized format
    # Assert both work
```

### Test 1.2: Discovery Flattening
**File**: `tests/phase1/test_discovery_flattener.py`

**Test Cases**:
```python
def test_flatten_all_arrays():
    """Test all discovery arrays flatten correctly"""
    # Input with all 25+ categories populated
    # Assert all keys normalized to snake_case

def test_preserve_array_values():
    """Test array values preserved exactly"""
    # "Rats/Mice" should remain "Rats/Mice"
    # "Air Conditioner" should remain "Air Conditioner"
    # Case-sensitive preservation

def test_extract_boolean_flags():
    """Test boolean flag extraction"""
    # "Injury Issues": true → has_injury: true
    # Assert all 9 boolean flags extracted

def test_empty_discovery():
    """Test handling of empty discovery (non-HoH plaintiff)"""
    # All arrays should be empty lists
    # All booleans should be false
```

### Test 1.3: Field Validation
**File**: `tests/phase1/test_validators.py`

**Test Cases**:
```python
def test_validate_required_fields():
    """Test required field validation"""
    # Missing property_address → fail
    # Missing plaintiff name → fail

def test_validate_data_types():
    """Test data type validation"""
    # Boolean flags must be bool, not string
    # Arrays must be lists, not strings

def test_validate_at_least_one_party():
    """Test at least 1 plaintiff and 1 defendant required"""
    # 0 plaintiffs → fail
    # 0 defendants → fail
    # 1 of each → pass
```

### Test 1.4: End-to-End Normalization
**File**: `tests/phase1/test_normalizer.py`

**Test Cases**:
```python
def test_normalize_goaloutput_example():
    """Test normalization of the goalOutput.md example"""
    # Load goalOutput.md JSON
    # Run normalize_form_data()
    # Assert output structure matches expected

def test_normalize_preserves_all_data():
    """Test no data loss during normalization"""
    # Verify all plaintiffs present
    # Verify all defendants present
    # Verify all discovery arrays preserved

def test_normalize_invalid_input_raises_error():
    """Test invalid input raises ValidationError"""
    # Test with invalid data
    # Assert ValidationError raised with clear message
```

## Exit Criteria

### All Tests Pass
- ✅ 15+ unit tests pass
- ✅ 100% code coverage for normalizer module
- ✅ Integration test with real form data passes

### Documentation Complete
- ✅ All functions have docstrings
- ✅ Example usage documented
- ✅ Error handling documented

### Performance
- ✅ Normalize 1,000 cases in < 1 second
- ✅ Memory usage < 50MB for large cases

### Code Quality
- ✅ Type hints on all functions
- ✅ Passes mypy type checking
- ✅ Passes flake8 linting
- ✅ Follows PEP 8 style guide

## Sample Test Data

### Create Test Fixtures
**File**: `tests/fixtures/phase1_samples.py`

```python
SIMPLE_CASE = {
    # 1 plaintiff (HoH), 1 defendant, minimal discovery
}

COMPLEX_CASE = {
    # 3 plaintiffs (2 HoH), 2 defendants, full discovery
}

EDGE_CASES = {
    # Missing optional fields
    # Empty discovery arrays
    # Special characters in names
}
```

## Dependencies
```txt
# requirements.txt for Phase 1
pytest==7.4.0
pytest-cov==4.1.0
mypy==1.5.0
flake8==6.1.0
```

## Deliverables
1. ✅ Input parser module
2. ✅ Discovery flattener module
3. ✅ Validator module
4. ✅ Normalizer pipeline
5. ✅ 15+ passing tests
6. ✅ Test fixtures
7. ✅ Documentation

---

**Phase Status**: 📋 Planning
**Estimated Duration**: 3-5 days
**Next Phase**: [Phase 2: Dataset Builder](PHASE-2-DATASET-BUILDER.md)
