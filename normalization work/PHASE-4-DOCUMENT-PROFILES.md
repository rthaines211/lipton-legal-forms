# Phase 4: Document Profiles

## Overview
Apply document type-specific transformations to create three separate profiles: SROGs, PODs, and Admissions. Each profile has specific flags, templates, and interrogatory count mappings.

## Input (from Phase 3)
```json
{
  "dataset_id": "...",
  "plaintiff": {...},
  "defendant": {...},
  "case_metadata": {...},
  "flags": {
    "HasMold": true,
    "HasRatsMice": true,
    // 180+ flags
  }
}
```

## Output (Three Profile Datasets)
```json
{
  "srogs": {
    "dataset_id": "...-srogs",
    "doc_type": "SROGs",
    "template": "SROGsMaster.docx",
    "plaintiff": {...},
    "defendant": {...},
    "case_metadata": {...},
    "flags": {
      "SROGsGeneral": true,  // Profile-specific
      "IsOwner": true,       // First-set-only
      "IsManager": false,
      "HasMold": true,       // Inherited
      // All flags from Phase 3
    },
    "interrogatory_counts": {
      "HasMold": 24,
      "HasRatsMice": 18,
      // Profile-specific counts
    }
  },
  "pods": {
    "dataset_id": "...-pods",
    "doc_type": "PODs",
    "template": "PODsMaster.docx",
    "flags": {
      "IsOwnerManager": true,  // Different from SROGs
      "HasMold": true,
      // No SROGsGeneral flag
    },
    "interrogatory_counts": {
      "HasMold": 4,  // Different from SROGs
      "HasRatsMice": 6,
    }
  },
  "admissions": {
    "dataset_id": "...-admissions",
    "doc_type": "Admissions",
    "template": "AdmissionsMaster.docx",
    "flags": {
      "AdmissionsGeneral": true,
      "HasLosAngeles": true,  // Geography-based
      "HasMold": true,
    },
    "interrogatory_counts": {
      "HasMold": 6,
      "HasRatsMice": 8,
    }
  }
}
```

## Profile Specifications

### SROGs Profile
- **Template**: `SROGsMaster.docx`
- **Filename Suffix**: "Discovery Propounded SROGs"
- **Special Flags**:
  - `SROGsGeneral: true` (always in Set 1)
  - `IsOwner: true/false` (based on defendant role)
  - `IsManager: true/false` (based on defendant role)
- **First-Set-Only Flags**: `SROGsGeneral`, `IsOwner`, `IsManager`
- **Interrogatory Counts**: Highest counts (most detailed)

### PODs Profile
- **Template**: `PODsMaster.docx`
- **Filename Suffix**: "Discovery Propounded PODs"
- **Special Flags**:
  - `IsOwnerManager: true/false` (combines Owner + Manager)
  - No `SROGsGeneral`
- **First-Set-Only Flags**: `IsOwner`, `IsManager`
- **Interrogatory Counts**: Medium counts

### Admissions Profile
- **Template**: `AdmissionsMaster.docx`
- **Filename Suffix**: "Discovery Request for Admissions"
- **Special Flags**:
  - `AdmissionsGeneral: true` (always in Set 1)
  - `HasLosAngeles: true/false` (if filing_city contains "Los Angeles")
  - `HasSanFrancisco: true/false` (if filing_city contains "San Francisco")
- **First-Set-Only Flags**: `AdmissionsGeneral`, `IsOwner`, `IsManager`, `HasLosAngeles`
- **Interrogatory Counts**: Lower counts (yes/no admissions)

## Task 4.1: Create Profile Base Class
**File**: `normalization work/src/phase4/base_profile.py`

```python
from abc import ABC, abstractmethod
from typing import Dict

class BaseDocumentProfile(ABC):
    """Base class for document profiles."""

    @property
    @abstractmethod
    def doc_type(self) -> str:
        """Document type name (SROGs, PODs, Admissions)"""
        pass

    @property
    @abstractmethod
    def template_name(self) -> str:
        """Template filename"""
        pass

    @property
    @abstractmethod
    def filename_suffix(self) -> str:
        """Suffix for generated filename"""
        pass

    @property
    @abstractmethod
    def first_set_only_flags(self) -> list[str]:
        """Flags that only appear in Set 1"""
        pass

    @property
    @abstractmethod
    def interrogatory_counts(self) -> Dict[str, int]:
        """
        Map flag names to interrogatory counts.

        Example:
            {
                "HasMold": 24,
                "HasRatsMice": 18,
                ...
            }
        """
        pass

    @abstractmethod
    def add_profile_specific_flags(self, dataset: dict) -> dict:
        """
        Add profile-specific flags to dataset.

        Args:
            dataset: Dataset with Phase 3 flags

        Returns:
            Dataset with additional profile flags
        """
        pass

    def apply_profile(self, dataset: dict) -> dict:
        """
        Apply profile transformation to dataset.

        Args:
            dataset: Enriched dataset from Phase 3

        Returns:
            Profile-specific dataset
        """
        # Deep copy to avoid mutation
        profiled_dataset = dataset.copy()
        profiled_dataset['flags'] = dataset['flags'].copy()

        # Add document type metadata
        profiled_dataset['doc_type'] = self.doc_type
        profiled_dataset['template'] = self.template_name
        profiled_dataset['filename_suffix'] = self.filename_suffix
        profiled_dataset['dataset_id'] = f"{dataset['dataset_id']}-{self.doc_type.lower()}"

        # Add profile-specific flags
        profiled_dataset = self.add_profile_specific_flags(profiled_dataset)

        # Add interrogatory counts
        profiled_dataset['interrogatory_counts'] = self.interrogatory_counts

        # Mark first-set-only flags
        profiled_dataset['first_set_only_flags'] = self.first_set_only_flags

        return profiled_dataset
```

## Task 4.2: Implement SROGs Profile
**File**: `normalization work/src/phase4/profiles/srogs.py`

```python
class SROGsProfile(BaseDocumentProfile):
    @property
    def doc_type(self) -> str:
        return "SROGs"

    @property
    def template_name(self) -> str:
        return "SROGsMaster.docx"

    @property
    def filename_suffix(self) -> str:
        return "Discovery Propounded SROGs"

    @property
    def first_set_only_flags(self) -> list[str]:
        return ["SROGsGeneral", "IsOwner", "IsManager"]

    @property
    def interrogatory_counts(self) -> Dict[str, int]:
        return {
            # Vermin & Insects
            "HasRatsMice": 18,
            "HasBedbugs": 16,
            "HasRoaches": 14,
            "HasAnts": 12,

            # Environmental
            "HasMold": 24,
            "HasLeadPaint": 20,

            # Housing
            "HasPlumbingIssues": 22,
            "HasElectricalIssues": 18,
            "HasHVACIssues": 16,

            # Safety
            "HasInoperableLocks": 14,
            "HasSmokeDetectorIssues": 12,

            # Legal
            "HasRetaliation": 20,
            "HasDiscrimination": 18,

            # ... (180+ mappings)
        }

    def add_profile_specific_flags(self, dataset: dict) -> dict:
        """Add SROGs-specific flags."""
        flags = dataset['flags']

        # Always add SROGsGeneral
        flags['SROGsGeneral'] = True

        # Add defendant role flags
        defendant_role = dataset.get('defendant', {}).get('role', '')
        flags['IsOwner'] = defendant_role.lower() == 'owner'
        flags['IsManager'] = defendant_role.lower() == 'manager'

        return dataset
```

## Task 4.3: Implement PODs Profile
**File**: `normalization work/src/phase4/profiles/pods.py`

```python
class PODsProfile(BaseDocumentProfile):
    @property
    def doc_type(self) -> str:
        return "PODs"

    @property
    def template_name(self) -> str:
        return "PODsMaster.docx"

    @property
    def filename_suffix(self) -> str:
        return "Discovery Propounded PODs"

    @property
    def first_set_only_flags(self) -> list[str]:
        return ["IsOwner", "IsManager"]  # No SROGsGeneral

    @property
    def interrogatory_counts(self) -> Dict[str, int]:
        return {
            # Lower counts than SROGs
            "HasRatsMice": 6,
            "HasBedbugs": 5,
            "HasMold": 4,
            "HasPlumbingIssues": 8,
            # ... (180+ mappings)
        }

    def add_profile_specific_flags(self, dataset: dict) -> dict:
        """Add PODs-specific flags."""
        flags = dataset['flags']

        # Remove SROGsGeneral if present
        flags.pop('SROGsGeneral', None)

        # Add IsOwnerManager (different from SROGs)
        defendant_role = dataset.get('defendant', {}).get('role', '')
        is_owner = defendant_role.lower() == 'owner'
        is_manager = defendant_role.lower() == 'manager'

        flags['IsOwner'] = is_owner
        flags['IsManager'] = is_manager
        flags['IsOwnerManager'] = is_owner or is_manager

        return dataset
```

## Task 4.4: Implement Admissions Profile
**File**: `normalization work/src/phase4/profiles/admissions.py`

```python
class AdmissionsProfile(BaseDocumentProfile):
    @property
    def doc_type(self) -> str:
        return "Admissions"

    @property
    def template_name(self) -> str:
        return "AdmissionsMaster.docx"

    @property
    def filename_suffix(self) -> str:
        return "Discovery Request for Admissions"

    @property
    def first_set_only_flags(self) -> list[str]:
        return ["AdmissionsGeneral", "IsOwner", "IsManager", "HasLosAngeles"]

    @property
    def interrogatory_counts(self) -> Dict[str, int]:
        return {
            # Lower counts (simple yes/no)
            "HasRatsMice": 8,
            "HasBedbugs": 6,
            "HasMold": 6,
            "HasPlumbingIssues": 10,
            # ... (180+ mappings)
        }

    def add_profile_specific_flags(self, dataset: dict) -> dict:
        """Add Admissions-specific flags."""
        flags = dataset['flags']

        # Add AdmissionsGeneral
        flags['AdmissionsGeneral'] = True

        # Add defendant role flags
        defendant_role = dataset.get('defendant', {}).get('role', '')
        flags['IsOwner'] = defendant_role.lower() == 'owner'
        flags['IsManager'] = defendant_role.lower() == 'manager'

        # Add geography flags
        filing_city = dataset.get('case_metadata', {}).get('filing_city', '').lower()
        flags['HasLosAngeles'] = 'los angeles' in filing_city
        flags['HasSanFrancisco'] = 'san francisco' in filing_city

        return dataset
```

## Task 4.5: Create Profile Pipeline
**File**: `normalization work/src/phase4/profile_pipeline.py`

```python
from .profiles import SROGsProfile, PODsProfile, AdmissionsProfile

class ProfilePipeline:
    """Applies all three document profiles to datasets."""

    def __init__(self):
        self.profiles = [
            SROGsProfile(),
            PODsProfile(),
            AdmissionsProfile()
        ]

    def apply_profiles(self, enriched_dataset: dict) -> dict:
        """
        Apply all profiles to a single dataset.

        Args:
            enriched_dataset: Dataset from Phase 3 with flags

        Returns:
            Dictionary with three profile datasets
        """
        return {
            'srogs': self.profiles[0].apply_profile(enriched_dataset),
            'pods': self.profiles[1].apply_profile(enriched_dataset),
            'admissions': self.profiles[2].apply_profile(enriched_dataset)
        }

    def apply_profiles_to_collection(self, dataset_collection: dict) -> dict:
        """
        Apply profiles to all datasets in collection.

        Args:
            dataset_collection: Collection from Phase 3

        Returns:
            Collection with profile datasets
        """
        profiled_datasets = []

        for dataset in dataset_collection['datasets']:
            profiles = self.apply_profiles(dataset)
            profiled_datasets.append(profiles)

        return {
            'datasets': profiled_datasets,
            'metadata': {
                **dataset_collection['metadata'],
                'profiles_applied': 3,
                'total_profile_datasets': len(profiled_datasets) * 3
            }
        }
```

## Test Plan

### Test 4.1: SROGs Profile Tests
**File**: `tests/phase4/test_srogs_profile.py`

```python
def test_srogs_adds_general_flag():
    """Test SROGsGeneral flag always added"""
    profile = SROGsProfile()
    dataset = create_test_dataset()

    result = profile.apply_profile(dataset)

    assert result['flags']['SROGsGeneral'] == True

def test_srogs_defendant_role_flags():
    """Test IsOwner/IsManager based on defendant role"""
    profile = SROGsProfile()

    # Test Owner
    dataset = create_test_dataset(defendant_role='Owner')
    result = profile.apply_profile(dataset)
    assert result['flags']['IsOwner'] == True
    assert result['flags']['IsManager'] == False

    # Test Manager
    dataset = create_test_dataset(defendant_role='Manager')
    result = profile.apply_profile(dataset)
    assert result['flags']['IsOwner'] == False
    assert result['flags']['IsManager'] == True
```

### Test 4.2: PODs Profile Tests
**File**: `tests/phase4/test_pods_profile.py`

```python
def test_pods_no_srogs_general():
    """Test PODs does not have SROGsGeneral flag"""
    profile = PODsProfile()
    dataset = create_test_dataset()

    result = profile.apply_profile(dataset)

    assert 'SROGsGeneral' not in result['flags']

def test_pods_owner_manager_combined():
    """Test IsOwnerManager flag"""
    profile = PODsProfile()

    dataset = create_test_dataset(defendant_role='Owner')
    result = profile.apply_profile(dataset)
    assert result['flags']['IsOwnerManager'] == True
```

### Test 4.3: Admissions Profile Tests
**File**: `tests/phase4/test_admissions_profile.py`

```python
def test_admissions_general_flag():
    """Test AdmissionsGeneral flag always added"""
    profile = AdmissionsProfile()
    dataset = create_test_dataset()

    result = profile.apply_profile(dataset)

    assert result['flags']['AdmissionsGeneral'] == True

def test_admissions_geography_flags():
    """Test geography-based flags"""
    profile = AdmissionsProfile()

    # Test Los Angeles
    dataset = create_test_dataset(filing_city='Los Angeles')
    result = profile.apply_profile(dataset)
    assert result['flags']['HasLosAngeles'] == True
    assert result['flags']['HasSanFrancisco'] == False

    # Test San Francisco
    dataset = create_test_dataset(filing_city='San Francisco')
    result = profile.apply_profile(dataset)
    assert result['flags']['HasLosAngeles'] == False
    assert result['flags']['HasSanFrancisco'] == True
```

### Test 4.4: Interrogatory Counts
**File**: `tests/phase4/test_interrogatory_counts.py`

```python
def test_interrogatory_counts_differ_by_profile():
    """Test each profile has different counts"""
    dataset = create_test_dataset()

    srogs = SROGsProfile().apply_profile(dataset)
    pods = PODsProfile().apply_profile(dataset)
    admissions = AdmissionsProfile().apply_profile(dataset)

    # SROGs should have highest counts
    assert srogs['interrogatory_counts']['HasMold'] == 24
    assert pods['interrogatory_counts']['HasMold'] == 4
    assert admissions['interrogatory_counts']['HasMold'] == 6
```

## Exit Criteria

### All Profiles Implemented
- ✅ SROGs profile complete
- ✅ PODs profile complete
- ✅ Admissions profile complete

### All Tests Pass
- ✅ 30+ unit tests pass
- ✅ Integration tests pass
- ✅ 100% code coverage

### Profile Integrity
- ✅ Each profile has correct flags
- ✅ Interrogatory counts differ appropriately
- ✅ First-set-only flags identified

## Deliverables
1. ✅ Base profile class
2. ✅ Three profile implementations
3. ✅ Profile pipeline
4. ✅ 30+ passing tests
5. ✅ Interrogatory count mappings documentation

---

**Phase Status**: 📋 Planning
**Estimated Duration**: 3-4 days
**Previous Phase**: [Phase 3: Flag Processors](PHASE-3-FLAG-PROCESSORS.md)
**Next Phase**: [Phase 5: Set Splitting](PHASE-5-SET-SPLITTING.md)
