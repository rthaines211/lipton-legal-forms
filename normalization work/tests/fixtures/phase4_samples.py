"""
Phase 4 Test Fixtures

Sample datasets and test data for document profile testing.
"""

def create_test_dataset(**kwargs):
    """
    Create a test dataset with default values that can be overridden.
    
    Args:
        **kwargs: Override default values
        
    Returns:
        dict: Test dataset
    """
    default_dataset = {
        'dataset_id': 'test-dataset-001',
        'plaintiff': {
            'name': 'John Doe',
            'address': '123 Main St, Los Angeles, CA 90210',
            'phone': '(555) 123-4567',
            'email': 'john.doe@example.com'
        },
        'defendant': {
            'name': 'ABC Property Management',
            'role': 'Manager',
            'address': '456 Business Ave, Los Angeles, CA 90210',
            'phone': '(555) 987-6543',
            'email': 'contact@abcproperty.com'
        },
        'case_metadata': {
            'case_number': 'BC123456',
            'filing_city': 'Los Angeles',
            'filing_date': '2024-01-15',
            'court_name': 'Los Angeles Superior Court'
        },
        'flags': {
            'HasMold': True,
            'HasRatsMice': True,
            'HasBedbugs': False,
            'HasPlumbingIssues': True,
            'HasElectricalIssues': False,
            'HasRetaliation': True,
            'HasDiscrimination': False
        }
    }
    
    # Apply any overrides
    for key, value in kwargs.items():
        if key in default_dataset:
            if isinstance(value, dict) and isinstance(default_dataset[key], dict):
                default_dataset[key].update(value)
            else:
                default_dataset[key] = value
        else:
            # Handle nested updates
            if '.' in key:
                parts = key.split('.')
                current = default_dataset
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                default_dataset[key] = value
    
    return default_dataset


def create_test_dataset_collection():
    """
    Create a collection of test datasets.
    
    Returns:
        dict: Collection of test datasets
    """
    return {
        'datasets': [
            create_test_dataset(dataset_id='test-001', defendant={'role': 'Owner'}),
            create_test_dataset(dataset_id='test-002', defendant={'role': 'Manager'}),
            create_test_dataset(dataset_id='test-003', case_metadata={'filing_city': 'San Francisco'})
        ],
        'metadata': {
            'total_datasets': 3,
            'created_at': '2024-01-15T10:00:00Z',
            'phase': 3
        }
    }


def create_owner_dataset():
    """Create dataset with Owner defendant role."""
    return create_test_dataset(
        dataset_id='owner-test-001',
        defendant={'role': 'Owner', 'name': 'Property Owner LLC'}
    )


def create_manager_dataset():
    """Create dataset with Manager defendant role."""
    return create_test_dataset(
        dataset_id='manager-test-001',
        defendant={'role': 'Manager', 'name': 'Management Company Inc'}
    )


def create_los_angeles_dataset():
    """Create dataset with Los Angeles filing city."""
    return create_test_dataset(
        dataset_id='la-test-001',
        case_metadata={'filing_city': 'Los Angeles', 'court_name': 'Los Angeles Superior Court'}
    )


def create_san_francisco_dataset():
    """Create dataset with San Francisco filing city."""
    return create_test_dataset(
        dataset_id='sf-test-001',
        case_metadata={'filing_city': 'San Francisco', 'court_name': 'San Francisco Superior Court'}
    )


def create_minimal_dataset():
    """Create minimal dataset with only required fields."""
    return {
        'dataset_id': 'minimal-test-001',
        'plaintiff': {'name': 'Jane Doe'},
        'defendant': {'name': 'Test Defendant', 'role': 'Owner'},
        'case_metadata': {'filing_city': 'Los Angeles'},
        'flags': {}
    }
