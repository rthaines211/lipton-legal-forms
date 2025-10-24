# Phase 3: Flag Processors

## Overview
Transform multi-select discovery arrays and boolean fields into 180+ individual boolean flags. This is the most complex phase, implementing 25+ specialized processors that convert arrays like `["Rats/Mice", "Bedbugs"]` into individual flags like `HasRatsMice: true`, `HasBedbugs: true`.

## Input (from Phase 2)
```json
{
  "dataset_id": "...",
  "discovery_data": {
    "vermin": ["Rats/Mice", "Bedbugs"],
    "insects": ["Roaches", "Ants"],
    "plumbing": ["Toilet", "Leaks", "Clogged toilets"],
    "has_injury": true,
    ...
  }
}
```

## Output (Enriched Dataset with Flags)
```json
{
  "dataset_id": "...",
  "discovery_data": {...},  // Original preserved
  "flags": {
    // Vermin flags (7)
    "HasVermin": true,
    "HasRatsMice": true,
    "HasBedbugs": true,
    "HasSkunks": false,
    ...
    // Insect flags (10)
    "HasInsects": true,
    "HasRoaches": true,
    "HasAnts": true,
    ...
    // Plumbing flags (17 + aggregates)
    "HasPlumbingIssues": true,
    "HasToilet": true,
    "HasLeaks": true,
    "HasCloggedToilets": true,
    "HasClogs": true,  // Aggregate
    ...
    // 180+ total flags
  }
}
```

## Flag Processor Architecture

### Base Processor Interface
**File**: `normalization work/src/phase3/base_processor.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, List

class BaseFlagProcessor(ABC):
    """Base class for all flag processors."""

    @property
    @abstractmethod
    def category_name(self) -> str:
        """Category name (e.g., 'vermin', 'insects')"""
        pass

    @property
    @abstractmethod
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map array values to flag names.

        Example:
            {
                "Rats/Mice": "HasRatsMice",
                "Bedbugs": "HasBedbugs"
            }
        """
        pass

    @property
    def aggregate_flag_name(self) -> str | None:
        """
        Optional aggregate flag (e.g., HasVermin, HasInsects).
        Returns None if no aggregate flag.
        """
        return None

    def process(self, discovery_data: dict) -> dict:
        """
        Process discovery data and return flag dict.

        Args:
            discovery_data: Discovery object from dataset

        Returns:
            Dictionary of flags {flag_name: bool}
        """
        flags = {}
        array_values = discovery_data.get(self.category_name, [])

        # Process individual flags
        for value, flag_name in self.flag_mappings.items():
            # Case-insensitive matching
            flags[flag_name] = any(
                v.lower() == value.lower() for v in array_values
            )

        # Process aggregate flag
        if self.aggregate_flag_name:
            flags[self.aggregate_flag_name] = any(flags.values())

        return flags
```

## Task 3.1: Implement Core Processors

### Vermin Processor
**File**: `normalization work/src/phase3/processors/vermin.py`

```python
class VerminProcessor(BaseFlagProcessor):
    @property
    def category_name(self) -> str:
        return "vermin"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        return {
            "Rats/Mice": "HasRatsMice",
            "Bedbugs": "HasBedbugs",
            "Skunks": "HasSkunks",
            "Bats": "HasBats",
            "Raccoons": "HasRaccoons",
            "Pigeons": "HasPigeons",
            "Opossums": "HasOpossums"
        }

    @property
    def aggregate_flag_name(self) -> str:
        return "HasVermin"
```

### Insect Processor
**File**: `normalization work/src/phase3/processors/insects.py`

```python
class InsectProcessor(BaseFlagProcessor):
    @property
    def category_name(self) -> str:
        return "insects"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        return {
            "Ants": "HasAnts",
            "Roaches": "HasRoaches",
            "Flies": "HasFlies",
            "Bedbugs": "HasBedbugsInsects",  # Different from vermin bedbugs
            "Wasps": "HasWasps",
            "Hornets": "HasHornets",
            "Spiders": "HasSpiders",
            "Termites": "HasTermites",
            "Mosquitos": "HasMosquitos",
            "Bees": "HasBees"
        }

    @property
    def aggregate_flag_name(self) -> str:
        return "HasInsects"
```

### Plumbing Processor (Complex with Aggregates)
**File**: `normalization work/src/phase3/processors/plumbing.py`

```python
class PlumbingProcessor(BaseFlagProcessor):
    @property
    def category_name(self) -> str:
        return "plumbing"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        return {
            "Toilet": "HasToilet",
            "Shower": "HasShower",
            "Bath": "HasBath",
            "Fixtures": "HasFixtures",
            "Leaks": "HasLeaks",
            "Insufficient water pressure": "HasInsufficientWaterPressure",
            "No hot water": "HasNoHotWater",
            "No cold water": "HasNoColdWater",
            "Sewage coming out": "HasSewageComingOut",
            "Clogged toilets": "HasCloggedToilets",
            "Clogged bath": "HasCloggedBath",
            "Clogged sinks": "HasCloggedSinks",
            "Clogged shower": "HasCloggedShower",
            "No Clean Water Supply": "HasNoCleanWaterSupply",
            "Unsanitary water": "HasUnsanitaryWater"
        }

    @property
    def aggregate_flag_name(self) -> str:
        return "HasPlumbingIssues"

    def process(self, discovery_data: dict) -> dict:
        """Override to add custom aggregate logic."""
        flags = super().process(discovery_data)

        # Additional aggregate: HasClogs
        clog_flags = [
            flags.get("HasCloggedToilets", False),
            flags.get("HasCloggedBath", False),
            flags.get("HasCloggedSinks", False),
            flags.get("HasCloggedShower", False)
        ]
        flags["HasClogs"] = any(clog_flags)

        return flags
```

## Task 3.2: Implement All 25+ Processors

### Complete Processor List
1. ✅ **VerminProcessor** (7 flags + 1 aggregate)
2. ✅ **InsectProcessor** (10 flags + 1 aggregate)
3. ✅ **HVACProcessor** (4 flags + 1 aggregate)
4. ✅ **ElectricalProcessor** (7 flags + 1 aggregate)
5. ✅ **FireHazardProcessor** (5 flags + 1 aggregate)
6. ✅ **GovernmentProcessor** (7 flags + 1 aggregate)
7. ✅ **AppliancesProcessor** (7 flags + 1 aggregate)
8. ✅ **PlumbingProcessor** (17 flags + 2 aggregates)
9. ✅ **CabinetsProcessor** (3 flags + 1 aggregate)
10. ✅ **FlooringProcessor** (4 flags + 1 aggregate)
11. ✅ **WindowsProcessor** (6 flags + 1 aggregate)
12. ✅ **DoorsProcessor** (8 flags + 1 aggregate)
13. ✅ **StructureProcessor** (18 flags + 2 aggregates)
14. ✅ **CommonAreasProcessor** (16 flags + 1 aggregate)
15. ✅ **TrashProcessor** (2 flags + 1 aggregate)
16. ✅ **NuisanceProcessor** (4 flags + 1 aggregate)
17. ✅ **HealthHazardProcessor** (8 flags + 1 aggregate)
18. ✅ **HarassmentProcessor** (16 flags + 1 aggregate)
19. ✅ **NoticesProcessor** (6 flags + 1 aggregate)
20. ✅ **UtilityProcessor** (5 flags + 1 aggregate)
21. ✅ **SafetyProcessor** (6 flags + 1 aggregate)
22. ✅ **DiscriminationProcessor** (4 flags from booleans)
23. ✅ **DirectBooleanProcessor** (injury, nonresponsive landlord, etc.)
24. ✅ **DefendantRoleProcessor** (IsOwner, IsManager, IsOwnerManager)
25. ✅ **GeographyProcessor** (HasLosAngeles, HasSanFrancisco)

## Task 3.3: Create Flag Processor Pipeline
**File**: `normalization work/src/phase3/flag_pipeline.py`

```python
from typing import List, Dict
from .processors import *

class FlagProcessorPipeline:
    """Orchestrates all flag processors."""

    def __init__(self):
        self.processors = self._initialize_processors()

    def _initialize_processors(self) -> List[BaseFlagProcessor]:
        """Initialize all processors in order."""
        return [
            VerminProcessor(),
            InsectProcessor(),
            HVACProcessor(),
            ElectricalProcessor(),
            FireHazardProcessor(),
            GovernmentProcessor(),
            AppliancesProcessor(),
            PlumbingProcessor(),
            CabinetsProcessor(),
            FlooringProcessor(),
            WindowsProcessor(),
            DoorsProcessor(),
            StructureProcessor(),
            CommonAreasProcessor(),
            TrashProcessor(),
            NuisanceProcessor(),
            HealthHazardProcessor(),
            HarassmentProcessor(),
            NoticesProcessor(),
            UtilityProcessor(),
            SafetyProcessor(),
            DiscriminationProcessor(),
            DirectBooleanProcessor(),
            DefendantRoleProcessor(),
            GeographyProcessor()
        ]

    def process_dataset(self, dataset: dict) -> dict:
        """
        Process a single dataset through all flag processors.

        Args:
            dataset: Dataset from Phase 2

        Returns:
            Dataset enriched with 180+ flags
        """
        flags = {}

        # Run each processor
        for processor in self.processors:
            processor_flags = processor.process(dataset)
            flags.update(processor_flags)

        # Add flags to dataset
        enriched_dataset = dataset.copy()
        enriched_dataset['flags'] = flags

        return enriched_dataset

    def process_all_datasets(self, dataset_collection: dict) -> dict:
        """
        Process all datasets in collection.

        Args:
            dataset_collection: Output from Phase 2

        Returns:
            Collection with all datasets enriched
        """
        enriched_datasets = []

        for dataset in dataset_collection['datasets']:
            enriched = self.process_dataset(dataset)
            enriched_datasets.append(enriched)

        return {
            'datasets': enriched_datasets,
            'metadata': {
                **dataset_collection['metadata'],
                'flags_generated': len(enriched_datasets[0]['flags']) if enriched_datasets else 0
            }
        }
```

## Test Plan

### Test 3.1: Individual Processor Tests
**File**: `tests/phase3/processors/test_[processor_name].py`

**Example for Vermin Processor**:
```python
def test_vermin_processor_all_selected():
    """Test all vermin options selected"""
    processor = VerminProcessor()
    discovery_data = {
        'vermin': ['Rats/Mice', 'Bedbugs', 'Skunks', 'Bats',
                   'Raccoons', 'Pigeons', 'Opossums']
    }
    flags = processor.process(discovery_data)

    assert flags['HasRatsMice'] == True
    assert flags['HasBedbugs'] == True
    assert flags['HasVermin'] == True  # Aggregate
    assert len(flags) == 8  # 7 individual + 1 aggregate

def test_vermin_processor_none_selected():
    """Test empty vermin array"""
    processor = VerminProcessor()
    discovery_data = {'vermin': []}
    flags = processor.process(discovery_data)

    assert all(not v for v in flags.values())
    assert flags['HasVermin'] == False

def test_vermin_processor_case_insensitive():
    """Test case-insensitive matching"""
    processor = VerminProcessor()
    discovery_data = {'vermin': ['rats/mice', 'BEDBUGS']}
    flags = processor.process(discovery_data)

    assert flags['HasRatsMice'] == True
    assert flags['HasBedbugs'] == True
```

### Test 3.2: Complex Aggregate Tests
**File**: `tests/phase3/test_aggregates.py`

```python
def test_plumbing_clogs_aggregate():
    """Test HasClogs aggregate flag"""
    processor = PlumbingProcessor()
    discovery_data = {
        'plumbing': ['Clogged toilets', 'Clogged sinks']
    }
    flags = processor.process(discovery_data)

    assert flags['HasCloggedToilets'] == True
    assert flags['HasCloggedSinks'] == True
    assert flags['HasClogs'] == True  # Aggregate

def test_structure_holes_aggregate():
    """Test HasHolesInCeilingWalls aggregate"""
    processor = StructureProcessor()
    discovery_data = {
        'structure': ['Hole in ceiling', 'Hole in wall']
    }
    flags = processor.process(discovery_data)

    assert flags['HasHoleInCeiling'] == True
    assert flags['HasHoleInWall'] == True
    assert flags['HasHolesInCeilingWalls'] == True  # Aggregate
```

### Test 3.3: Pipeline Integration Tests
**File**: `tests/phase3/test_flag_pipeline.py`

```python
def test_pipeline_processes_all_flags():
    """Test pipeline generates all 180+ flags"""
    pipeline = FlagProcessorPipeline()
    dataset = create_full_discovery_dataset()  # All arrays populated

    result = pipeline.process_dataset(dataset)

    assert 'flags' in result
    assert len(result['flags']) >= 180
    assert 'HasVermin' in result['flags']
    assert 'HasInsects' in result['flags']
    # ... check key flags

def test_pipeline_handles_empty_discovery():
    """Test pipeline with empty discovery data"""
    pipeline = FlagProcessorPipeline()
    dataset = {
        'dataset_id': 'test',
        'discovery_data': {
            'vermin': [],
            'insects': [],
            # All empty arrays
        }
    }

    result = pipeline.process_dataset(dataset)

    assert 'flags' in result
    # All flags should be False
    assert all(not v for v in result['flags'].values())

def test_pipeline_process_multiple_datasets():
    """Test processing collection with multiple datasets"""
    pipeline = FlagProcessorPipeline()
    collection = {
        'datasets': [
            create_dataset_1(),
            create_dataset_2()
        ],
        'metadata': {}
    }

    result = pipeline.process_all_datasets(collection)

    assert len(result['datasets']) == 2
    assert all('flags' in d for d in result['datasets'])
```

### Test 3.4: Flag Count Verification
**File**: `tests/phase3/test_flag_counts.py`

```python
def test_flag_count_matches_spec():
    """Verify total flag count matches data model spec (180+)"""
    pipeline = FlagProcessorPipeline()
    dataset = create_full_discovery_dataset()

    result = pipeline.process_dataset(dataset)

    expected_categories = {
        'vermin': 8,
        'insects': 11,
        'hvac': 5,
        'electrical': 8,
        'fire_hazard': 6,
        'government': 8,
        'appliances': 8,
        'plumbing': 19,  # Including aggregates
        # ... etc.
    }

    # Verify minimum flag count
    assert len(result['flags']) >= 180
```

## Exit Criteria

### All Processors Implemented
- ✅ 25+ processors created
- ✅ All inherit from BaseFlagProcessor
- ✅ Case-insensitive matching works

### All Tests Pass
- ✅ 75+ unit tests (3+ per processor)
- ✅ Integration tests pass
- ✅ 100% code coverage

### Flag Coverage
- ✅ 180+ flags generated
- ✅ All aggregate flags calculated correctly
- ✅ No duplicate flag names

### Performance
- ✅ Process 1,000 datasets in < 5 seconds
- ✅ Memory efficient (flags cached appropriately)

## Deliverables
1. ✅ Base processor interface
2. ✅ 25+ processor implementations
3. ✅ Flag pipeline orchestrator
4. ✅ 75+ passing tests
5. ✅ Flag catalog documentation
6. ✅ Performance benchmarks

---

**Phase Status**: 📋 Planning
**Estimated Duration**: 7-10 days
**Previous Phase**: [Phase 2: Dataset Builder](PHASE-2-DATASET-BUILDER.md)
**Next Phase**: [Phase 4: Document Profiles](PHASE-4-DOCUMENT-PROFILES.md)
