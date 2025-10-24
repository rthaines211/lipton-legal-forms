# Phase 2: Dataset Builder

## Overview
Build the Cartesian product of Head of Household plaintiffs × Defendants, creating one dataset for each combination. Each dataset will contain case information, plaintiff discovery data, and defendant details.

## Input (from Phase 1)
```json
{
  "case_info": {...},
  "plaintiffs": [
    {"is_head_of_household": true, "discovery": {...}},
    {"is_head_of_household": false},
    {"is_head_of_household": true, "discovery": {...}}
  ],
  "defendants": [{...}, {...}]
}
```

## Output (Dataset Collection)
```json
{
  "datasets": [
    {
      "dataset_id": "abc123-plaintiff1-defendant1",
      "case_id": "form-entry-1729123456789",
      "plaintiff": {
        "plaintiff_id": "4ck5Gw",
        "first_name": "Clark",
        "last_name": "Kent",
        "full_name": "Clark Kent",
        "unit_number": "1"
      },
      "defendant": {
        "defendant_id": "31rR5u",
        "first_name": "Tony",
        "last_name": "Stark",
        "full_name": "Tony Stark",
        "entity_type": "LLC",
        "role": "Manager"
      },
      "case_metadata": {
        "property_address": "1331 Yorkshire Place NW",
        "property_address_with_unit": "1331 Yorkshire Place NW Unit 1",
        "city": "Concord",
        "state": "NC",
        "zip": "28027",
        "filing_city": "Los Angeles",
        "filing_county": "Los Angeles County"
      },
      "discovery_data": {
        "vermin": ["Rats/Mice", "Bedbugs"],
        "insects": ["Roaches", "Ants"],
        ...all discovery arrays and booleans...
      }
    },
    {...more datasets for other HoH × Defendant combinations...}
  ],
  "metadata": {
    "total_datasets": 4,
    "hoh_count": 2,
    "defendant_count": 2,
    "non_hoh_plaintiffs": 1
  }
}
```

## Tasks

### Task 2.1: Create HoH Filter
**File**: `normalization work/src/phase2/hoh_filter.py`

**Functions**:
```python
def filter_heads_of_household(plaintiffs: list[dict]) -> list[dict]:
    """
    Filter plaintiffs to only those with is_head_of_household=true
    and valid discovery data.

    Args:
        plaintiffs: List of plaintiff objects

    Returns:
        List of HoH plaintiffs only
    """
    return [
        p for p in plaintiffs
        if p.get('is_head_of_household', False) and 'discovery' in p
    ]

def get_non_hoh_plaintiffs(plaintiffs: list[dict]) -> list[dict]:
    """Get non-HoH plaintiffs for metadata tracking."""
    return [
        p for p in plaintiffs
        if not p.get('is_head_of_household', False)
    ]
```

### Task 2.2: Create Cartesian Product Builder
**File**: `normalization work/src/phase2/cartesian_builder.py`

**Functions**:
```python
def build_cartesian_product(
    hoh_plaintiffs: list[dict],
    defendants: list[dict],
    case_info: dict
) -> list[dict]:
    """
    Build HoH × Defendant Cartesian product.

    For each HoH plaintiff:
        For each defendant:
            Create dataset with:
                - Plaintiff info
                - Defendant info
                - Case metadata
                - Discovery data

    Args:
        hoh_plaintiffs: Filtered HoH plaintiffs
        defendants: All defendants
        case_info: Case metadata

    Returns:
        List of datasets (one per HoH × Defendant combination)
    """
    datasets = []

    for plaintiff in hoh_plaintiffs:
        for defendant in defendants:
            dataset = {
                'dataset_id': generate_dataset_id(
                    case_info['case_id'],
                    plaintiff['plaintiff_id'],
                    defendant['defendant_id']
                ),
                'case_id': case_info['case_id'],
                'plaintiff': extract_plaintiff_info(plaintiff),
                'defendant': extract_defendant_info(defendant),
                'case_metadata': build_case_metadata(case_info, plaintiff),
                'discovery_data': plaintiff['discovery']
            }
            datasets.append(dataset)

    return datasets

def generate_dataset_id(case_id: str, plaintiff_id: str, defendant_id: str) -> str:
    """Generate unique dataset ID."""
    return f"{case_id}-{plaintiff_id}-{defendant_id}"
```

### Task 2.3: Create Address Builder
**File**: `normalization work/src/phase2/address_builder.py`

**Functions**:
```python
def build_property_address_with_unit(
    base_address: str,
    unit_number: str | None
) -> str:
    """
    Build property address with unit, ensuring unit appears only once.

    Rules:
    - If base_address already contains "Unit X", return as-is
    - If unit_number provided and not in address, append "Unit X"
    - Otherwise return base_address

    Args:
        base_address: Base property address
        unit_number: Unit number (can be None)

    Returns:
        Address with unit (idempotent)

    Examples:
        >>> build_property_address_with_unit("123 Main St", "5")
        "123 Main St Unit 5"

        >>> build_property_address_with_unit("123 Main St Unit 5", "5")
        "123 Main St Unit 5"

        >>> build_property_address_with_unit("123 Main St", None)
        "123 Main St"
    """
    if not unit_number:
        return base_address

    unit_marker = f"Unit {unit_number}"

    # Check if unit already in address (case-insensitive)
    if unit_marker.lower() in base_address.lower():
        return base_address

    # Append unit
    return f"{base_address} {unit_marker}"
```

### Task 2.4: Create Dataset Builder Pipeline
**File**: `normalization work/src/phase2/dataset_builder.py`

**Main Function**:
```python
def build_datasets(normalized_data: dict) -> dict:
    """
    Main dataset building pipeline.

    Args:
        normalized_data: Output from Phase 1 normalizer

    Returns:
        Dataset collection with metadata

    Raises:
        DatasetBuildError: If dataset building fails
    """
    case_info = normalized_data['case_info']
    plaintiffs = normalized_data['plaintiffs']
    defendants = normalized_data['defendants']

    # 1. Filter HoH plaintiffs
    hoh_plaintiffs = filter_heads_of_household(plaintiffs)
    non_hoh = get_non_hoh_plaintiffs(plaintiffs)

    # 2. Validate at least one HoH and one defendant
    if not hoh_plaintiffs:
        raise DatasetBuildError("No Head of Household plaintiffs found")
    if not defendants:
        raise DatasetBuildError("No defendants found")

    # 3. Build Cartesian product
    datasets = build_cartesian_product(hoh_plaintiffs, defendants, case_info)

    # 4. Build metadata
    metadata = {
        'total_datasets': len(datasets),
        'hoh_count': len(hoh_plaintiffs),
        'defendant_count': len(defendants),
        'non_hoh_plaintiffs': len(non_hoh),
        'expected_datasets': len(hoh_plaintiffs) * len(defendants)
    }

    # 5. Validate
    assert metadata['total_datasets'] == metadata['expected_datasets'], \
        "Dataset count mismatch"

    return {
        'datasets': datasets,
        'metadata': metadata
    }
```

## Test Plan

### Test 2.1: HoH Filtering
**File**: `tests/phase2/test_hoh_filter.py`

**Test Cases**:
```python
def test_filter_only_hoh():
    """Test filtering returns only HoH plaintiffs"""
    plaintiffs = [
        {'is_head_of_household': True, 'discovery': {}},
        {'is_head_of_household': False},
        {'is_head_of_household': True, 'discovery': {}}
    ]
    result = filter_heads_of_household(plaintiffs)
    assert len(result) == 2
    assert all(p['is_head_of_household'] for p in result)

def test_filter_requires_discovery():
    """Test HoH without discovery excluded"""
    plaintiffs = [
        {'is_head_of_household': True, 'discovery': {}},
        {'is_head_of_household': True}  # No discovery
    ]
    result = filter_heads_of_household(plaintiffs)
    assert len(result) == 1

def test_get_non_hoh_plaintiffs():
    """Test non-HoH plaintiff extraction"""
    plaintiffs = [
        {'is_head_of_household': True, 'discovery': {}},
        {'is_head_of_household': False, 'first_name': 'Bruce'}
    ]
    result = get_non_hoh_plaintiffs(plaintiffs)
    assert len(result) == 1
    assert result[0]['first_name'] == 'Bruce'
```

### Test 2.2: Cartesian Product
**File**: `tests/phase2/test_cartesian_builder.py`

**Test Cases**:
```python
def test_cartesian_product_count():
    """Test correct number of datasets generated"""
    # 2 HoH plaintiffs × 2 defendants = 4 datasets
    hoh_plaintiffs = [
        {'plaintiff_id': 'p1', 'discovery': {}},
        {'plaintiff_id': 'p2', 'discovery': {}}
    ]
    defendants = [
        {'defendant_id': 'd1'},
        {'defendant_id': 'd2'}
    ]
    result = build_cartesian_product(hoh_plaintiffs, defendants, {})
    assert len(result) == 4

def test_dataset_contains_all_components():
    """Test each dataset has required components"""
    # Single HoH, single defendant
    datasets = build_cartesian_product([...], [...], {...})
    dataset = datasets[0]

    assert 'dataset_id' in dataset
    assert 'plaintiff' in dataset
    assert 'defendant' in dataset
    assert 'case_metadata' in dataset
    assert 'discovery_data' in dataset

def test_dataset_id_uniqueness():
    """Test all dataset IDs are unique"""
    datasets = build_cartesian_product([...], [...], {...})
    ids = [d['dataset_id'] for d in datasets]
    assert len(ids) == len(set(ids))
```

### Test 2.3: Address Building
**File**: `tests/phase2/test_address_builder.py`

**Test Cases**:
```python
def test_add_unit_to_address():
    """Test unit added to address without unit"""
    result = build_property_address_with_unit("123 Main St", "5")
    assert result == "123 Main St Unit 5"

def test_unit_already_present():
    """Test idempotency - unit already in address"""
    result = build_property_address_with_unit("123 Main St Unit 5", "5")
    assert result == "123 Main St Unit 5"
    assert result.count("Unit 5") == 1  # Only one occurrence

def test_no_unit_number():
    """Test address unchanged when no unit"""
    result = build_property_address_with_unit("123 Main St", None)
    assert result == "123 Main St"

def test_case_insensitive_unit_check():
    """Test unit detection is case-insensitive"""
    result = build_property_address_with_unit("123 Main St unit 5", "5")
    assert "Unit 5" in result or "unit 5" in result
    # Should not add duplicate
```

### Test 2.4: End-to-End Dataset Building
**File**: `tests/phase2/test_dataset_builder.py`

**Test Cases**:
```python
def test_build_datasets_simple_case():
    """Test building datasets for simple case"""
    # 1 HoH, 1 defendant → 1 dataset
    normalized_data = {...}
    result = build_datasets(normalized_data)

    assert result['metadata']['total_datasets'] == 1
    assert result['metadata']['hoh_count'] == 1
    assert result['metadata']['defendant_count'] == 1
    assert len(result['datasets']) == 1

def test_build_datasets_complex_case():
    """Test building datasets for complex case"""
    # 2 HoH, 2 defendants → 4 datasets
    normalized_data = {...}
    result = build_datasets(normalized_data)

    assert result['metadata']['total_datasets'] == 4
    assert result['metadata']['expected_datasets'] == 4

def test_build_datasets_no_hoh_raises_error():
    """Test error raised when no HoH plaintiffs"""
    normalized_data = {
        'plaintiffs': [{'is_head_of_household': False}],
        'defendants': [{}]
    }

    with pytest.raises(DatasetBuildError):
        build_datasets(normalized_data)

def test_build_datasets_preserves_discovery():
    """Test discovery data preserved in datasets"""
    normalized_data = {...}  # With specific discovery data
    result = build_datasets(normalized_data)

    dataset = result['datasets'][0]
    assert 'vermin' in dataset['discovery_data']
    assert 'insects' in dataset['discovery_data']
    # Verify all discovery fields present
```

### Test 2.5: Integration with Phase 1
**File**: `tests/integration/test_phase1_to_phase2.py`

**Test Cases**:
```python
def test_end_to_end_phase1_to_phase2():
    """Test full pipeline from form JSON to datasets"""
    # Load goalOutput.md example
    form_json = load_fixture('goaloutput_example.json')

    # Phase 1: Normalize
    normalized = normalize_form_data(form_json)

    # Phase 2: Build datasets
    result = build_datasets(normalized)

    # Verify output
    assert result['metadata']['total_datasets'] == 6  # 3 HoH × 2 defendants
    assert all('discovery_data' in d for d in result['datasets'])
```

## Exit Criteria

### All Tests Pass
- ✅ 15+ unit tests pass
- ✅ Integration test with Phase 1 passes
- ✅ 100% code coverage for dataset builder module

### Data Integrity
- ✅ No data loss from Phase 1 to Phase 2
- ✅ All discovery data preserved in datasets
- ✅ Correct number of datasets generated (HoH × Defendant)

### Address Handling
- ✅ Unit idempotency enforced (unit appears only once)
- ✅ Case-insensitive unit detection works
- ✅ Handles missing unit numbers gracefully

### Performance
- ✅ Build 1,000 datasets in < 2 seconds
- ✅ Memory efficient (no data duplication)

## Sample Test Data

### Create Test Fixtures
**File**: `tests/fixtures/phase2_samples.py`

```python
SINGLE_HOH_SINGLE_DEFENDANT = {
    # Expected: 1 dataset
}

MULTI_HOH_MULTI_DEFENDANT = {
    # 2 HoH, 2 defendants
    # Expected: 4 datasets
}

MIXED_PLAINTIFFS = {
    # 2 HoH, 1 non-HoH, 2 defendants
    # Expected: 4 datasets (non-HoH excluded)
}

EDGE_CASES = {
    # HoH without discovery → error
    # No defendants → error
    # Address with existing unit
}
```

## Dependencies
```txt
# Additional requirements for Phase 2
# (inherits from Phase 1)
```

## Deliverables
1. ✅ HoH filter module
2. ✅ Cartesian product builder
3. ✅ Address builder with unit idempotency
4. ✅ Dataset builder pipeline
5. ✅ 15+ passing tests
6. ✅ Integration test with Phase 1
7. ✅ Documentation

---

**Phase Status**: 📋 Planning
**Estimated Duration**: 2-3 days
**Previous Phase**: [Phase 1: Input Normalization](PHASE-1-INPUT-NORMALIZATION.md)
**Next Phase**: [Phase 3: Flag Processors](PHASE-3-FLAG-PROCESSORS.md)
