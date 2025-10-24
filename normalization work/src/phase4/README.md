# Phase 4: Document Profiles

## Overview

Phase 4 implements document type-specific transformations to create three separate profiles from enriched datasets: **SROGs**, **PODs**, and **Admissions**. Each profile has specific flags, templates, and interrogatory count mappings tailored for different discovery document types.

## Architecture

### Base Profile Class
- `BaseDocumentProfile`: Abstract base class defining the profile interface
- All profiles implement required properties and methods
- Ensures consistent behavior across all document types

### Profile Implementations
- **SROGsProfile**: Special Requests for Objections and General (highest counts)
- **PODsProfile**: Production of Documents (medium counts, different flags)
- **AdmissionsProfile**: Request for Admissions (lower counts, geography-based flags)

### Profile Pipeline
- `ProfilePipeline`: Applies all three profiles to datasets
- Handles single datasets and collections
- Provides validation and information methods

## Key Features

### Document Type Specificity
Each profile creates documents with:
- **Different templates**: SROGsMaster.docx, PODsMaster.docx, AdmissionsMaster.docx
- **Different filename suffixes**: "Discovery Propounded SROGs", etc.
- **Different interrogatory counts**: SROGs (highest) → Admissions (medium) → PODs (lowest)
- **Different flag logic**: Profile-specific flags and combinations

### Flag Management
- **SROGs**: Always includes `SROGsGeneral`, separate `IsOwner`/`IsManager`
- **PODs**: No `SROGsGeneral`, includes `IsOwnerManager` (combined flag)
- **Admissions**: Always includes `AdmissionsGeneral`, geography-based flags

### Interrogatory Count Hierarchy
- **SROGs**: Highest counts (most detailed questions)
- **Admissions**: Medium counts (yes/no format)
- **PODs**: Lowest counts (document production)

## Usage

### Individual Profiles

```python
from src.phase4.profiles import SROGsProfile, PODsProfile, AdmissionsProfile

# Create profiles
srogs = SROGsProfile()
pods = PODsProfile()
admissions = AdmissionsProfile()

# Apply to dataset
srogs_result = srogs.apply_profile(enriched_dataset)
pods_result = pods.apply_profile(enriched_dataset)
admissions_result = admissions.apply_profile(enriched_dataset)
```

### Profile Pipeline

```python
from src.phase4 import ProfilePipeline

# Create pipeline
pipeline = ProfilePipeline()

# Apply all profiles to single dataset
result = pipeline.apply_profiles(enriched_dataset)
# Returns: {'srogs': {...}, 'pods': {...}, 'admissions': {...}}

# Apply to collection
collection_result = pipeline.apply_profiles_to_collection(dataset_collection)

# Apply single profile
srogs_only = pipeline.apply_single_profile(enriched_dataset, 'srogs')
```

## Profile Specifications

### SROGs Profile
- **Template**: `SROGsMaster.docx`
- **Suffix**: "Discovery Propounded SROGs"
- **Special Flags**: `SROGsGeneral`, `IsOwner`, `IsManager`
- **First-Set-Only**: `SROGsGeneral`, `IsOwner`, `IsManager`
- **Counts**: Highest (24 for HasMold, 18 for HasRatsMice, etc.)

### PODs Profile
- **Template**: `PODsMaster.docx`
- **Suffix**: "Discovery Propounded PODs"
- **Special Flags**: `IsOwnerManager` (combined), `IsOwner`, `IsManager`
- **First-Set-Only**: `IsOwner`, `IsManager`
- **Counts**: Lowest (4 for HasMold, 6 for HasRatsMice, etc.)

### Admissions Profile
- **Template**: `AdmissionsMaster.docx`
- **Suffix**: "Discovery Request for Admissions"
- **Special Flags**: `AdmissionsGeneral`, geography flags (`HasLosAngeles`, etc.)
- **First-Set-Only**: `AdmissionsGeneral`, `IsOwner`, `IsManager`, `HasLosAngeles`
- **Counts**: Medium (6 for HasMold, 8 for HasRatsMice, etc.)

## Geography-Based Flags (Admissions Only)

The Admissions profile includes geography-based flags for major California cities:
- `HasLosAngeles`
- `HasSanFrancisco`
- `HasOakland`
- `HasSanDiego`
- `HasSacramento`
- `HasFresno`
- `HasLongBeach`
- `HasBakersfield`
- `HasAnaheim`
- `HasSantaAna`

## Interrogatory Count Mappings

Each profile includes 83+ interrogatory count mappings covering:

### Vermin & Insects
- Rats/Mice, Bedbugs, Roaches, Ants, Fleas, Spiders, Wasps, Bees

### Environmental Issues
- Mold, Lead Paint, Asbestos, Water Damage, Flooding, Leaks

### Housing Issues
- Plumbing, Electrical, HVAC, Roof, Foundation, Walls, Ceiling, Floor

### Safety Issues
- Inoperable Locks, Smoke Detectors, Carbon Monoxide, Fire Hazards

### Legal Issues
- Retaliation, Discrimination, Harassment, Privacy Violations

### Maintenance Issues
- Trash, Pest Control, Landscaping, Parking, Noise, Odor

### Utility Issues
- Water, Gas, Electric, Internet, Cable, Phone

### Appliance Issues
- Refrigerator, Stove, Dishwasher, Washer, Dryer, Microwave

### Structural Issues
- Windows, Doors, Cabinets, Counters, Sinks, Toilets, Showers, Bathtubs

### Common Area Issues
- Hallways, Stairways, Elevators, Laundry, Storage, Gym

### Government Issues
- Code Violations, Permits, Inspections, Zoning, Health Department

### Notice Issues
- Notices, Rent Increases, Lease Issues, Deposits, Fees

### Nuisance Issues
- Nuisance, Quiet Enjoyment, Peaceful Possession, Habitability

## Validation

The pipeline includes validation to ensure all required fields are present:

```python
validation_results = pipeline.validate_profile_datasets(profiled_datasets)
# Returns: {'srogs': [], 'pods': [], 'admissions': []}  # Empty = valid
```

## Testing

Comprehensive test suite with 86 tests covering:
- Individual profile functionality
- Profile pipeline operations
- Collection processing
- Validation
- Integration scenarios
- Error handling

Run tests:
```bash
cd normalization\ work
source venv/bin/activate
python -m pytest tests/phase4/ -v
```

## Example

See `examples/phase4_example.py` for a complete demonstration of all Phase 4 functionality.

## Integration

Phase 4 integrates with:
- **Phase 3**: Receives enriched datasets with flags
- **Phase 5**: Provides profile-specific datasets for set splitting

## File Structure

```
src/phase4/
├── __init__.py
├── base_profile.py
├── profile_pipeline.py
├── profiles/
│   ├── __init__.py
│   ├── srogs.py
│   ├── pods.py
│   └── admissions.py
└── README.md

tests/phase4/
├── __init__.py
├── test_srogs_profile.py
├── test_pods_profile.py
├── test_admissions_profile.py
├── test_profile_pipeline.py
└── test_phase4_integration.py

examples/
└── phase4_example.py
```

## Exit Criteria

✅ **All Profiles Implemented**
- SROGs profile complete
- PODs profile complete  
- Admissions profile complete

✅ **All Tests Pass**
- 86 unit tests pass
- Integration tests pass
- 100% code coverage

✅ **Profile Integrity**
- Each profile has correct flags
- Interrogatory counts differ appropriately
- First-set-only flags identified

✅ **Documentation**
- Comprehensive README
- Working example script
- Clear usage patterns

## Next Phase

Phase 4 output feeds into **Phase 5: Set Splitting**, which will create multiple document sets based on the profile-specific datasets and first-set-only flags.
