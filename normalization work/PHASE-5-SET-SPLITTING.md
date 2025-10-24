# Phase 5: Set Splitting

## Overview
Split profiled datasets into sets with maximum 120 interrogatories per set. Implements the seed-accumulate-split algorithm with first-set-only flag handling.

## Input (from Phase 4)
```json
{
  "dataset_id": "...-srogs",
  "doc_type": "SROGs",
  "flags": {
    "SROGsGeneral": true,  // First-set-only
    "IsOwner": true,       // First-set-only
    "HasMold": true,       // 24 interrogatories
    "HasRatsMice": true,   // 18 interrogatories
    // 180+ flags
  },
  "interrogatory_counts": {
    "HasMold": 24,
    "HasRatsMice": 18,
    ...
  },
  "first_set_only_flags": ["SROGsGeneral", "IsOwner", "IsManager"]
}
```

## Output (Split Sets)
```json
{
  "doc_type": "SROGs",
  "sets": [
    {
      "set_number": 1,
      "interrogatory_start": 1,
      "interrogatory_end": 120,
      "total_interrogatories": 120,
      "is_first_set": true,
      "flags": {
        "SROGsGeneral": true,  // Seeded
        "IsOwner": true,       // Seeded
        "HasMold": true,       // Accumulated
        "HasRatsMice": true,   // Accumulated
        "HasPlumbing": true,   // Accumulated
        // Flags that fit in 120 limit
      }
    },
    {
      "set_number": 2,
      "interrogatory_start": 121,
      "interrogatory_end": 235,
      "total_interrogatories": 115,
      "is_first_set": false,
      "flags": {
        "HasElectrical": true,  // Continued from Set 1
        "HasStructure": true,
        // Remaining flags
      }
    }
  ],
  "metadata": {
    "total_sets": 2,
    "total_interrogatories": 235,
    "max_per_set": 120
  }
}
```

## Set Splitting Algorithm

### Algorithm Overview
```
1. SEED PHASE (Set 1 only):
   - Add first-set-only flags
   - Calculate starting interrogatory count

2. ACCUMULATION PHASE (All sets):
   - For each remaining flag (True flags only):
       - Check if adding flag would exceed 120 limit
       - If yes: Close current set, start new set
       - If no: Add flag to current set

3. ENRICHMENT PHASE:
   - Add set metadata (SetNumber, InterrogatoryStart, etc.)
   - Calculate totals
```

### Key Rules
1. **First-Set-Only Flags**: Only appear in Set 1, never re-seed
2. **Max 120 Interrogatories**: Hard limit per set
3. **True Flags Only**: Only split flags that are `true`
4. **Sequential Numbering**: Set 1, Set 2, Set 3, etc.
5. **Continuous Interrogatory Range**: Set 1: 1-120, Set 2: 121-240, etc.

## Task 5.1: Create Set Splitter
**File**: `normalization work/src/phase5/set_splitter.py`

```python
from typing import List, Dict

class SetSplitter:
    """Implements set splitting algorithm."""

    def __init__(self, max_interrogatories_per_set: int = 120):
        self.max_interrogatories_per_set = max_interrogatories_per_set

    def split_into_sets(self, profiled_dataset: dict) -> dict:
        """
        Split profiled dataset into sets.

        Args:
            profiled_dataset: Dataset from Phase 4 with profile applied

        Returns:
            Dictionary with sets and metadata
        """
        flags = profiled_dataset['flags']
        interrogatory_counts = profiled_dataset['interrogatory_counts']
        first_set_only_flags = profiled_dataset.get('first_set_only_flags', [])

        # Get all TRUE flags
        true_flags = {k: v for k, v in flags.items() if v is True}

        # Separate first-set-only from regular flags
        first_set_flags = {
            k: v for k, v in true_flags.items()
            if k in first_set_only_flags
        }
        regular_flags = {
            k: v for k, v in true_flags.items()
            if k not in first_set_only_flags
        }

        # Sort regular flags by interrogatory count (descending)
        # This ensures larger flags are placed first
        sorted_flags = sorted(
            regular_flags.keys(),
            key=lambda k: interrogatory_counts.get(k, 0),
            reverse=True
        )

        # Initialize sets
        sets = []
        current_set = {
            'flags': {},
            'interrogatory_count': 0
        }

        # SEED PHASE: Add first-set-only flags to Set 1
        for flag_name in first_set_flags:
            count = interrogatory_counts.get(flag_name, 0)
            current_set['flags'][flag_name] = True
            current_set['interrogatory_count'] += count

        # ACCUMULATION PHASE: Add regular flags
        for flag_name in sorted_flags:
            count = interrogatory_counts.get(flag_name, 0)

            # Check if adding this flag would exceed limit
            if current_set['interrogatory_count'] + count > self.max_interrogatories_per_set:
                # Close current set and start new one
                if current_set['flags']:  # Only save if not empty
                    sets.append(current_set)

                current_set = {
                    'flags': {},
                    'interrogatory_count': 0
                }

            # Add flag to current set
            current_set['flags'][flag_name] = True
            current_set['interrogatory_count'] += count

        # Add final set
        if current_set['flags']:
            sets.append(current_set)

        # ENRICHMENT PHASE: Add metadata
        enriched_sets = self._enrich_sets(sets)

        return {
            'doc_type': profiled_dataset['doc_type'],
            'dataset_id': profiled_dataset['dataset_id'],
            'plaintiff': profiled_dataset['plaintiff'],
            'defendant': profiled_dataset['defendant'],
            'case_metadata': profiled_dataset['case_metadata'],
            'template': profiled_dataset['template'],
            'filename_suffix': profiled_dataset['filename_suffix'],
            'sets': enriched_sets,
            'metadata': {
                'total_sets': len(enriched_sets),
                'total_interrogatories': sum(s['total_interrogatories'] for s in enriched_sets),
                'max_per_set': self.max_interrogatories_per_set
            }
        }

    def _enrich_sets(self, sets: List[dict]) -> List[dict]:
        """Add metadata to each set."""
        enriched = []
        interrogatory_start = 1

        for i, set_data in enumerate(sets):
            interrogatory_count = set_data['interrogatory_count']
            interrogatory_end = interrogatory_start + interrogatory_count - 1

            enriched_set = {
                'set_number': i + 1,
                'interrogatory_start': interrogatory_start,
                'interrogatory_end': interrogatory_end,
                'total_interrogatories': interrogatory_count,
                'is_first_set': i == 0,
                'flags': set_data['flags']
            }

            enriched.append(enriched_set)
            interrogatory_start = interrogatory_end + 1

        return enriched
```

## Task 5.2: Create Filename Generator
**File**: `normalization work/src/phase5/filename_generator.py`

```python
def generate_filename(
    plaintiff_name: str,
    defendant_name: str,
    doc_type: str,
    set_number: int,
    total_sets: int,
    filename_suffix: str
) -> str:
    """
    Generate filename for set.

    Format: "[Plaintiff] vs [Defendant] - [Suffix] Set [X] of [Y]"

    Args:
        plaintiff_name: Full name of plaintiff
        defendant_name: Full name of defendant
        doc_type: Document type (SROGs, PODs, Admissions)
        set_number: Current set number
        total_sets: Total number of sets
        filename_suffix: Profile-specific suffix

    Returns:
        Formatted filename

    Examples:
        >>> generate_filename("John Doe", "ABC Corp", "SROGs", 1, 2,
        ...                   "Discovery Propounded SROGs")
        "John Doe vs ABC Corp - Discovery Propounded SROGs Set 1 of 2"
    """
    return f"{plaintiff_name} vs {defendant_name} - {filename_suffix} Set {set_number} of {total_sets}"
```

## Task 5.3: Create Set Splitting Pipeline
**File**: `normalization work/src/phase5/splitting_pipeline.py`

```python
class SplittingPipeline:
    """Orchestrates set splitting for all profile datasets."""

    def __init__(self, max_interrogatories_per_set: int = 120):
        self.splitter = SetSplitter(max_interrogatories_per_set)

    def split_profile_datasets(self, profile_datasets: dict) -> dict:
        """
        Split all three profile datasets (SROGs, PODs, Admissions).

        Args:
            profile_datasets: Output from ProfilePipeline.apply_profiles()
                {
                    'srogs': {...},
                    'pods': {...},
                    'admissions': {...}
                }

        Returns:
            Dictionary with split sets for each profile
        """
        result = {}

        for profile_name, dataset in profile_datasets.items():
            split_result = self.splitter.split_into_sets(dataset)

            # Add filenames to each set
            for set_data in split_result['sets']:
                set_data['filename'] = generate_filename(
                    plaintiff_name=dataset['plaintiff']['full_name'],
                    defendant_name=dataset['defendant']['full_name'],
                    doc_type=dataset['doc_type'],
                    set_number=set_data['set_number'],
                    total_sets=split_result['metadata']['total_sets'],
                    filename_suffix=dataset['filename_suffix']
                )

            result[profile_name] = split_result

        return result

    def split_all_datasets(self, profiled_collection: dict) -> list:
        """
        Split all datasets in collection across all profiles.

        Args:
            profiled_collection: Collection from Phase 4

        Returns:
            Flat list of all sets for all profiles and datasets
        """
        all_sets = []

        for dataset_profiles in profiled_collection['datasets']:
            split_profiles = self.split_profile_datasets(dataset_profiles)

            for profile_name, split_data in split_profiles.items():
                all_sets.append(split_data)

        return all_sets
```

## Test Plan

### Test 5.1: Basic Set Splitting
**File**: `tests/phase5/test_set_splitter.py`

```python
def test_single_set_under_limit():
    """Test dataset with < 120 interrogatories stays in one set"""
    splitter = SetSplitter(max_interrogatories_per_set=120)
    dataset = create_dataset_with_flags({
        'HasMold': True,      # 24
        'HasRatsMice': True,  # 18
        'HasRoaches': True,   # 14
        # Total: 56
    })

    result = splitter.split_into_sets(dataset)

    assert result['metadata']['total_sets'] == 1
    assert result['metadata']['total_interrogatories'] == 56

def test_multiple_sets_over_limit():
    """Test dataset with > 120 interrogatories splits into multiple sets"""
    splitter = SetSplitter(max_interrogatories_per_set=120)
    dataset = create_dataset_with_many_flags()  # Total: 250 interrogatories

    result = splitter.split_into_sets(dataset)

    assert result['metadata']['total_sets'] >= 3
    # Verify each set <= 120
    for set_data in result['sets']:
        assert set_data['total_interrogatories'] <= 120

def test_first_set_only_flags_in_set_1():
    """Test first-set-only flags only appear in Set 1"""
    splitter = SetSplitter(max_interrogatories_per_set=120)
    dataset = create_dataset_with_first_set_flags()

    result = splitter.split_into_sets(dataset)

    # Check Set 1 has first-set-only flags
    set_1 = result['sets'][0]
    assert 'SROGsGeneral' in set_1['flags']
    assert 'IsOwner' in set_1['flags']

    # Check other sets do NOT have first-set-only flags
    if len(result['sets']) > 1:
        for set_data in result['sets'][1:]:
            assert 'SROGsGeneral' not in set_data['flags']
```

### Test 5.2: Interrogatory Numbering
**File**: `tests/phase5/test_interrogatory_numbering.py`

```python
def test_interrogatory_ranges_continuous():
    """Test interrogatory ranges are continuous"""
    splitter = SetSplitter()
    dataset = create_dataset_with_many_flags()

    result = splitter.split_into_sets(dataset)

    # Verify continuous numbering
    expected_start = 1
    for set_data in result['sets']:
        assert set_data['interrogatory_start'] == expected_start
        expected_start = set_data['interrogatory_end'] + 1

def test_interrogatory_start_end_correct():
    """Test start/end match total count"""
    splitter = SetSplitter()
    dataset = create_dataset_with_flags({'HasMold': True})  # 24 interrogatories

    result = splitter.split_into_sets(dataset)
    set_1 = result['sets'][0]

    assert set_1['interrogatory_start'] == 1
    assert set_1['interrogatory_end'] == 24
    assert set_1['total_interrogatories'] == 24
```

### Test 5.3: Filename Generation
**File**: `tests/phase5/test_filename_generator.py`

```python
def test_filename_format():
    """Test filename generated correctly"""
    filename = generate_filename(
        plaintiff_name="John Doe",
        defendant_name="ABC Corp",
        doc_type="SROGs",
        set_number=1,
        total_sets=2,
        filename_suffix="Discovery Propounded SROGs"
    )

    assert filename == "John Doe vs ABC Corp - Discovery Propounded SROGs Set 1 of 2"

def test_filename_special_characters():
    """Test filename handles special characters"""
    filename = generate_filename(
        plaintiff_name="María José",
        defendant_name="O'Brien LLC",
        doc_type="PODs",
        set_number=1,
        total_sets=1,
        filename_suffix="Discovery Propounded PODs"
    )

    assert "María José" in filename
    assert "O'Brien LLC" in filename
```

### Test 5.4: Edge Cases
**File**: `tests/phase5/test_edge_cases.py`

```python
def test_empty_flags():
    """Test dataset with no true flags"""
    splitter = SetSplitter()
    dataset = create_dataset_with_all_false_flags()

    result = splitter.split_into_sets(dataset)

    # Should have at least Set 1 with first-set-only flags
    assert result['metadata']['total_sets'] >= 1

def test_single_large_flag():
    """Test single flag with 120+ interrogatories"""
    splitter = SetSplitter(max_interrogatories_per_set=120)
    dataset = create_dataset_with_flags({
        'HugeFlag': True  # 150 interrogatories (hypothetical)
    })

    # Should still create set even if over limit
    # (single flag can't be split)
    result = splitter.split_into_sets(dataset)
    assert result['metadata']['total_sets'] >= 1
```

## Exit Criteria

### Algorithm Implementation
- ✅ Seed-accumulate-split algorithm works correctly
- ✅ First-set-only flags only in Set 1
- ✅ Max 120 interrogatories enforced

### All Tests Pass
- ✅ 20+ unit tests pass
- ✅ Edge case tests pass
- ✅ 100% code coverage

### Data Integrity
- ✅ No flags lost during splitting
- ✅ Interrogatory numbering continuous
- ✅ Set metadata accurate

### Performance
- ✅ Split 1,000 datasets in < 3 seconds

## Deliverables
1. ✅ Set splitter implementation
2. ✅ Filename generator
3. ✅ Splitting pipeline
4. ✅ 20+ passing tests
5. ✅ Algorithm documentation

---

**Phase Status**: 📋 Planning
**Estimated Duration**: 2-3 days
**Previous Phase**: [Phase 4: Document Profiles](PHASE-4-DOCUMENT-PROFILES.md)
**Next Phase**: [Phase 6: Output Generation](PHASE-6-OUTPUT-GENERATION.md)
