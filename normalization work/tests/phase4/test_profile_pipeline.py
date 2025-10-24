"""
Profile Pipeline Tests

Test suite for ProfilePipeline implementation.
"""

import pytest
from src.phase4.profile_pipeline import ProfilePipeline
from tests.fixtures.phase4_samples import (
    create_test_dataset,
    create_test_dataset_collection,
    create_owner_dataset,
    create_manager_dataset
)


class TestProfilePipeline:
    """Test cases for ProfilePipeline."""

    def test_initialization(self):
        """Test that ProfilePipeline initializes with all three profiles."""
        pipeline = ProfilePipeline()
        
        assert len(pipeline.profiles) == 3
        assert pipeline.profiles[0].doc_type == "SROGs"
        assert pipeline.profiles[1].doc_type == "PODs"
        assert pipeline.profiles[2].doc_type == "Admissions"

    def test_apply_profiles_single_dataset(self):
        """Test applying all profiles to a single dataset."""
        pipeline = ProfilePipeline()
        dataset = create_test_dataset()
        
        result = pipeline.apply_profiles(dataset)
        
        # Should return dictionary with three profiles
        assert 'srogs' in result
        assert 'pods' in result
        assert 'admissions' in result
        
        # Each profile should have correct doc_type
        assert result['srogs']['doc_type'] == "SROGs"
        assert result['pods']['doc_type'] == "PODs"
        assert result['admissions']['doc_type'] == "Admissions"

    def test_apply_profiles_preserves_original_data(self):
        """Test that apply_profiles preserves original dataset data."""
        pipeline = ProfilePipeline()
        dataset = create_test_dataset()
        original_plaintiff = dataset['plaintiff'].copy()
        original_defendant = dataset['defendant'].copy()
        original_case_metadata = dataset['case_metadata'].copy()
        
        result = pipeline.apply_profiles(dataset)
        
        # Check that original data is preserved in all profiles
        for profile_name, profile_data in result.items():
            assert profile_data['plaintiff'] == original_plaintiff
            assert profile_data['defendant'] == original_defendant
            assert profile_data['case_metadata'] == original_case_metadata

    def test_apply_profiles_collection(self):
        """Test applying profiles to a collection of datasets."""
        pipeline = ProfilePipeline()
        collection = create_test_dataset_collection()
        
        result = pipeline.apply_profiles_to_collection(collection)
        
        # Should have same number of datasets
        assert len(result['datasets']) == len(collection['datasets'])
        
        # Each dataset should have three profiles
        for dataset in result['datasets']:
            assert 'srogs' in dataset
            assert 'pods' in dataset
            assert 'admissions' in dataset
        
        # Metadata should be updated
        assert result['metadata']['profiles_applied'] == 3
        assert result['metadata']['total_profile_datasets'] == len(collection['datasets']) * 3

    def test_apply_single_profile_srogs(self):
        """Test applying single SROGs profile."""
        pipeline = ProfilePipeline()
        dataset = create_test_dataset()
        
        result = pipeline.apply_single_profile(dataset, 'srogs')
        
        assert result['doc_type'] == "SROGs"
        assert result['template'] == "SROGsMaster.docx"
        assert result['flags']['SROGsGeneral'] == True

    def test_apply_single_profile_pods(self):
        """Test applying single PODs profile."""
        pipeline = ProfilePipeline()
        dataset = create_test_dataset()
        
        result = pipeline.apply_single_profile(dataset, 'pods')
        
        assert result['doc_type'] == "PODs"
        assert result['template'] == "PODsMaster.docx"
        assert 'SROGsGeneral' not in result['flags']
        assert 'IsOwnerManager' in result['flags']

    def test_apply_single_profile_admissions(self):
        """Test applying single Admissions profile."""
        pipeline = ProfilePipeline()
        dataset = create_test_dataset()
        
        result = pipeline.apply_single_profile(dataset, 'admissions')
        
        assert result['doc_type'] == "Admissions"
        assert result['template'] == "AdmissionsMaster.docx"
        assert result['flags']['AdmissionsGeneral'] == True

    def test_apply_single_profile_invalid_type(self):
        """Test applying single profile with invalid type raises error."""
        pipeline = ProfilePipeline()
        dataset = create_test_dataset()
        
        with pytest.raises(ValueError, match="Unknown profile type"):
            pipeline.apply_single_profile(dataset, 'invalid')

    def test_get_profile_info(self):
        """Test getting profile information."""
        pipeline = ProfilePipeline()
        info = pipeline.get_profile_info()
        
        # Should have info for all three profiles
        assert 'srogs' in info
        assert 'pods' in info
        assert 'admissions' in info
        
        # Check SROGs info
        srogs_info = info['srogs']
        assert srogs_info['doc_type'] == "SROGs"
        assert srogs_info['template'] == "SROGsMaster.docx"
        assert srogs_info['filename_suffix'] == "Discovery Propounded SROGs"
        assert 'SROGsGeneral' in srogs_info['first_set_only_flags']
        assert srogs_info['total_interrogatory_mappings'] > 0
        
        # Check PODs info
        pods_info = info['pods']
        assert pods_info['doc_type'] == "PODs"
        assert pods_info['template'] == "PODsMaster.docx"
        assert pods_info['filename_suffix'] == "Discovery Propounded PODs"
        assert 'SROGsGeneral' not in pods_info['first_set_only_flags']
        assert pods_info['total_interrogatory_mappings'] > 0
        
        # Check Admissions info
        admissions_info = info['admissions']
        assert admissions_info['doc_type'] == "Admissions"
        assert admissions_info['template'] == "AdmissionsMaster.docx"
        assert admissions_info['filename_suffix'] == "Discovery Request for Admissions"
        assert 'AdmissionsGeneral' in admissions_info['first_set_only_flags']
        assert admissions_info['total_interrogatory_mappings'] > 0

    def test_validate_profile_datasets_valid(self):
        """Test validation of valid profile datasets."""
        pipeline = ProfilePipeline()
        dataset = create_test_dataset()
        profiled_datasets = pipeline.apply_profiles(dataset)
        
        validation_results = pipeline.validate_profile_datasets(profiled_datasets)
        
        # All profiles should be valid (no missing fields)
        for profile_name, missing_fields in validation_results.items():
            assert missing_fields == []

    def test_validate_profile_datasets_invalid(self):
        """Test validation of invalid profile datasets."""
        pipeline = ProfilePipeline()
        
        # Create invalid dataset (missing required fields)
        invalid_datasets = {
            'srogs': {'doc_type': 'SROGs'},  # Missing required fields
            'pods': {'doc_type': 'PODs', 'flags': {}},  # Missing required fields
            'admissions': {'doc_type': 'Admissions', 'template': 'test'}  # Missing required fields
        }
        
        validation_results = pipeline.validate_profile_datasets(invalid_datasets)
        
        # All profiles should have missing fields
        for profile_name, missing_fields in validation_results.items():
            assert len(missing_fields) > 0

    def test_interrogatory_counts_differ_by_profile(self):
        """Test that interrogatory counts differ appropriately between profiles."""
        pipeline = ProfilePipeline()
        dataset = create_test_dataset()
        profiled_datasets = pipeline.apply_profiles(dataset)
        
        srogs_counts = profiled_datasets['srogs']['interrogatory_counts']
        pods_counts = profiled_datasets['pods']['interrogatory_counts']
        admissions_counts = profiled_datasets['admissions']['interrogatory_counts']
        
        # SROGs should have highest counts
        assert srogs_counts['HasMold'] > admissions_counts['HasMold']
        assert srogs_counts['HasMold'] > pods_counts['HasMold']
        
        # Admissions should have higher counts than PODs
        assert admissions_counts['HasMold'] > pods_counts['HasMold']
        assert admissions_counts['HasRatsMice'] > pods_counts['HasRatsMice']

    def test_flags_differ_by_profile(self):
        """Test that flags differ appropriately between profiles."""
        pipeline = ProfilePipeline()
        dataset = create_test_dataset()
        profiled_datasets = pipeline.apply_profiles(dataset)
        
        srogs_flags = profiled_datasets['srogs']['flags']
        pods_flags = profiled_datasets['pods']['flags']
        admissions_flags = profiled_datasets['admissions']['flags']
        
        # SROGs should have SROGsGeneral
        assert 'SROGsGeneral' in srogs_flags
        assert srogs_flags['SROGsGeneral'] == True
        
        # PODs should not have SROGsGeneral
        assert 'SROGsGeneral' not in pods_flags
        
        # PODs should have IsOwnerManager
        assert 'IsOwnerManager' in pods_flags
        
        # Admissions should have AdmissionsGeneral
        assert 'AdmissionsGeneral' in admissions_flags
        assert admissions_flags['AdmissionsGeneral'] == True

    def test_first_set_only_flags_differ_by_profile(self):
        """Test that first_set_only_flags differ between profiles."""
        pipeline = ProfilePipeline()
        dataset = create_test_dataset()
        profiled_datasets = pipeline.apply_profiles(dataset)
        
        srogs_first_set = profiled_datasets['srogs']['first_set_only_flags']
        pods_first_set = profiled_datasets['pods']['first_set_only_flags']
        admissions_first_set = profiled_datasets['admissions']['first_set_only_flags']
        
        # SROGs should include SROGsGeneral
        assert 'SROGsGeneral' in srogs_first_set
        
        # PODs should not include SROGsGeneral
        assert 'SROGsGeneral' not in pods_first_set
        
        # Admissions should include AdmissionsGeneral
        assert 'AdmissionsGeneral' in admissions_first_set
        
        # All should include IsOwner and IsManager
        for first_set in [srogs_first_set, pods_first_set, admissions_first_set]:
            assert 'IsOwner' in first_set
            assert 'IsManager' in first_set

    def test_dataset_id_suffixes(self):
        """Test that dataset IDs have correct suffixes."""
        pipeline = ProfilePipeline()
        dataset = create_test_dataset()
        profiled_datasets = pipeline.apply_profiles(dataset)
        
        original_id = dataset['dataset_id']
        
        assert profiled_datasets['srogs']['dataset_id'] == f"{original_id}-srogs"
        assert profiled_datasets['pods']['dataset_id'] == f"{original_id}-pods"
        assert profiled_datasets['admissions']['dataset_id'] == f"{original_id}-admissions"

    def test_collection_metadata_preservation(self):
        """Test that collection metadata is preserved and updated."""
        pipeline = ProfilePipeline()
        collection = create_test_dataset_collection()
        original_metadata = collection['metadata'].copy()
        
        result = pipeline.apply_profiles_to_collection(collection)
        
        # Original metadata should be preserved
        for key, value in original_metadata.items():
            if key not in ['profiles_applied', 'total_profile_datasets']:
                assert result['metadata'][key] == value
        
        # New metadata should be added
        assert result['metadata']['profiles_applied'] == 3
        assert result['metadata']['total_profile_datasets'] == len(collection['datasets']) * 3
