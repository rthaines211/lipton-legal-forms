"""
Phase 5 Test Fixtures

Sample datasets for set splitting testing with realistic interrogatory counts.
"""


def create_profiled_dataset(**kwargs):
    """
    Create a profiled dataset with flags and interrogatory counts.

    This represents the output from Phase 4 that serves as input to Phase 5.

    Args:
        **kwargs: Override default values

    Returns:
        dict: Profiled dataset ready for set splitting
    """
    default_dataset = {
        'dataset_id': 'test-dataset-001-srogs',
        'doc_type': 'SROGs',
        'plaintiff': {
            'full_name': 'John Doe',
            'first_name': 'John',
            'last_name': 'Doe',
            'address': '123 Main St, Los Angeles, CA 90210'
        },
        'defendant': {
            'full_name': 'ABC Property Management',
            'entity_type': 'LLC',
            'role': 'Manager',
            'address': '456 Business Ave, Los Angeles, CA 90210'
        },
        'case_metadata': {
            'case_number': 'BC123456',
            'filing_city': 'Los Angeles',
            'court_name': 'Los Angeles Superior Court'
        },
        'template': 'SROGS_OWNER_LA',
        'filename_suffix': 'Discovery Propounded SROGs',
        'flags': {
            'SROGsGeneral': True,
            'IsOwner': False,
            'IsManager': True,
            'HasMold': True,
            'HasRatsMice': True,
            'HasBedbugs': False,
            'HasRoaches': True,
            'HasPlumbingIssues': True,
            'HasElectricalIssues': False,
            'HasRetaliation': True
        },
        'interrogatory_counts': {
            'SROGsGeneral': 10,
            'IsOwner': 15,
            'IsManager': 12,
            'HasMold': 24,
            'HasRatsMice': 18,
            'HasBedbugs': 16,
            'HasRoaches': 14,
            'HasPlumbingIssues': 22,
            'HasElectricalIssues': 20,
            'HasRetaliation': 28
        },
        'first_set_only_flags': ['SROGsGeneral', 'IsOwner', 'IsManager']
    }

    # Apply overrides
    for key, value in kwargs.items():
        if key in default_dataset:
            if isinstance(value, dict) and isinstance(default_dataset[key], dict):
                default_dataset[key].update(value)
            else:
                default_dataset[key] = value
        else:
            default_dataset[key] = value

    return default_dataset


def create_small_dataset():
    """
    Create dataset with < 120 interrogatories (single set).

    Total: 60 interrogatories (10 + 12 + 24 + 14)
    """
    return create_profiled_dataset(
        dataset_id='small-test-001-srogs',
        flags={
            'SROGsGeneral': True,    # 10 (first-set-only)
            'IsManager': True,       # 12 (first-set-only)
            'HasMold': True,         # 24
            'HasRoaches': True,      # 14
            'HasRatsMice': False,
            'HasBedbugs': False,
            'HasPlumbingIssues': False,
            'HasElectricalIssues': False,
            'HasRetaliation': False
        }
    )


def create_medium_dataset():
    """
    Create dataset with > 120 but < 240 interrogatories (2 sets).

    Total: 156 interrogatories
    """
    return create_profiled_dataset(
        dataset_id='medium-test-001-srogs',
        flags={
            'SROGsGeneral': True,        # 10 (first-set-only)
            'IsManager': True,           # 12 (first-set-only)
            'HasMold': True,             # 24
            'HasRatsMice': True,         # 18
            'HasRoaches': True,          # 14
            'HasPlumbingIssues': True,   # 22
            'HasElectricalIssues': True, # 20
            'HasRetaliation': True,      # 28
            'HasBedbugs': True,          # 16
            'IsOwner': False
        },
        interrogatory_counts={
            'SROGsGeneral': 10,
            'IsOwner': 15,
            'IsManager': 12,
            'HasMold': 24,
            'HasRatsMice': 18,
            'HasBedbugs': 16,
            'HasRoaches': 14,
            'HasPlumbingIssues': 22,
            'HasElectricalIssues': 20,
            'HasRetaliation': 28,
            'HasAC': 26,
            'HasPests': 12
        }
    )


def create_large_dataset():
    """
    Create dataset with 250+ interrogatories (3+ sets).

    Total: 280 interrogatories
    """
    return create_profiled_dataset(
        dataset_id='large-test-001-srogs',
        flags={
            'SROGsGeneral': True,
            'IsOwner': True,
            'HasMold': True,
            'HasRatsMice': True,
            'HasRoaches': True,
            'HasBedbugs': True,
            'HasPlumbingIssues': True,
            'HasElectricalIssues': True,
            'HasRetaliation': True,
            'HasDiscrimination': True,
            'HasAC': True,
            'HasHeat': True,
            'HasPests': True,
            'HasStructure': True,
            'HasSafety': True,
            'IsManager': False
        },
        interrogatory_counts={
            'SROGsGeneral': 10,
            'IsOwner': 15,
            'IsManager': 12,
            'HasMold': 24,
            'HasRatsMice': 18,
            'HasBedbugs': 16,
            'HasRoaches': 14,
            'HasPlumbingIssues': 22,
            'HasElectricalIssues': 20,
            'HasRetaliation': 28,
            'HasDiscrimination': 26,
            'HasAC': 26,
            'HasHeat': 24,
            'HasPests': 12,
            'HasStructure': 18,
            'HasSafety': 15
        }
    )


def create_first_set_only_dataset():
    """
    Create dataset where first-set-only flags dominate.

    Tests that first-set-only flags only appear in Set 1.
    """
    return create_profiled_dataset(
        dataset_id='first-set-test-001-srogs',
        flags={
            'SROGsGeneral': True,
            'IsOwner': True,
            'IsManager': True,
            'HasMold': True,
            'HasRatsMice': True,
            'HasRoaches': False,
            'HasBedbugs': False,
            'HasPlumbingIssues': False,
            'HasElectricalIssues': False,
            'HasRetaliation': False
        },
        interrogatory_counts={
            'SROGsGeneral': 10,
            'IsOwner': 15,
            'IsManager': 12,
            'HasMold': 24,
            'HasRatsMice': 18,
            'HasBedbugs': 16,
            'HasRoaches': 14,
            'HasPlumbingIssues': 22,
            'HasElectricalIssues': 20,
            'HasRetaliation': 28
        },
        first_set_only_flags=['SROGsGeneral', 'IsOwner', 'IsManager']
    )


def create_minimal_flags_dataset():
    """
    Create dataset with minimal flags (only first-set-only).

    Tests edge case where no regular flags are true.
    """
    return create_profiled_dataset(
        dataset_id='minimal-test-001-srogs',
        flags={
            'SROGsGeneral': True,
            'IsManager': True,
            'IsOwner': False,
            'HasMold': False,
            'HasRatsMice': False,
            'HasRoaches': False,
            'HasBedbugs': False,
            'HasPlumbingIssues': False,
            'HasElectricalIssues': False,
            'HasRetaliation': False
        }
    )


def create_empty_flags_dataset():
    """
    Create dataset with all flags false.

    Tests edge case where no flags are true.
    """
    return create_profiled_dataset(
        dataset_id='empty-test-001-srogs',
        flags={
            'SROGsGeneral': False,
            'IsOwner': False,
            'IsManager': False,
            'HasMold': False,
            'HasRatsMice': False,
            'HasRoaches': False,
            'HasBedbugs': False,
            'HasPlumbingIssues': False,
            'HasElectricalIssues': False,
            'HasRetaliation': False
        }
    )


def create_profile_datasets():
    """
    Create all three profile datasets (SROGs, PODs, Admissions) for one case.

    Returns:
        dict: Three profiled datasets
    """
    return {
        'srogs': create_profiled_dataset(
            dataset_id='test-001-srogs',
            doc_type='SROGs',
            filename_suffix='Discovery Propounded SROGs'
        ),
        'pods': create_profiled_dataset(
            dataset_id='test-001-pods',
            doc_type='PODs',
            filename_suffix='Discovery Propounded PODs'
        ),
        'admissions': create_profiled_dataset(
            dataset_id='test-001-admissions',
            doc_type='Admissions',
            filename_suffix='Requests for Admissions'
        )
    }


def create_profiled_collection():
    """
    Create collection of profiled datasets (multiple cases).

    Returns:
        dict: Collection with multiple datasets
    """
    return {
        'datasets': [
            create_profile_datasets(),
            {
                'srogs': create_profiled_dataset(
                    dataset_id='test-002-srogs',
                    plaintiff={'full_name': 'Jane Smith'},
                    defendant={'full_name': 'XYZ Properties'}
                ),
                'pods': create_profiled_dataset(
                    dataset_id='test-002-pods',
                    doc_type='PODs',
                    plaintiff={'full_name': 'Jane Smith'},
                    defendant={'full_name': 'XYZ Properties'}
                ),
                'admissions': create_profiled_dataset(
                    dataset_id='test-002-admissions',
                    doc_type='Admissions',
                    plaintiff={'full_name': 'Jane Smith'},
                    defendant={'full_name': 'XYZ Properties'}
                )
            }
        ]
    }


def create_dataset_with_custom_flags(flags_dict: dict, counts_dict: dict):
    """
    Create dataset with custom flags and counts.

    This completely replaces the default flags and counts with the provided ones.

    Args:
        flags_dict: Dictionary of flag names to boolean values
        counts_dict: Dictionary of flag names to interrogatory counts

    Returns:
        dict: Profiled dataset
    """
    dataset = create_profiled_dataset()
    # Completely replace flags and counts (don't merge)
    dataset['flags'] = flags_dict.copy()
    dataset['interrogatory_counts'] = counts_dict.copy()
    # Remove first_set_only_flags that don't exist in custom flags
    dataset['first_set_only_flags'] = [
        flag for flag in dataset.get('first_set_only_flags', [])
        if flag in flags_dict
    ]
    return dataset
