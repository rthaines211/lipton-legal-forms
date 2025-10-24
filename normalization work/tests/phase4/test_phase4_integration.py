"""
Phase 4 Integration Tests

Integration tests for the complete Phase 4 document profile system.
"""

import pytest
from src.phase4 import ProfilePipeline, SROGsProfile, PODsProfile, AdmissionsProfile
from tests.fixtures.phase4_samples import (
    create_test_dataset,
    create_test_dataset_collection,
    create_owner_dataset,
    create_manager_dataset,
    create_los_angeles_dataset,
    create_san_francisco_dataset
)


class TestPhase4Integration:
    """Integration tests for Phase 4 document profiles."""

    def test_all_profiles_implement_base_interface(self):
        """Test that all profiles implement the base interface correctly."""
        profiles = [SROGsProfile(), PODsProfile(), AdmissionsProfile()]
        
        for profile in profiles:
            # Test abstract properties
            assert hasattr(profile, 'doc_type')
            assert hasattr(profile, 'template_name')
            assert hasattr(profile, 'filename_suffix')
            assert hasattr(profile, 'first_set_only_flags')
            assert hasattr(profile, 'interrogatory_counts')
            
            # Test abstract methods
            assert hasattr(profile, 'add_profile_specific_flags')
            assert hasattr(profile, 'apply_profile')
            
            # Test that properties return expected types
            assert isinstance(profile.doc_type, str)
            assert isinstance(profile.template_name, str)
            assert isinstance(profile.filename_suffix, str)
            assert isinstance(profile.first_set_only_flags, list)
            assert isinstance(profile.interrogatory_counts, dict)

    def test_profile_pipeline_completeness(self):
        """Test that ProfilePipeline handles all three profiles correctly."""
        pipeline = ProfilePipeline()
        dataset = create_test_dataset()
        
        result = pipeline.apply_profiles(dataset)
        
        # Should have all three profiles
        assert len(result) == 3
        assert 'srogs' in result
        assert 'pods' in result
        assert 'admissions' in result
        
        # Each profile should be complete
        for profile_name, profile_data in result.items():
            required_fields = [
                'dataset_id', 'doc_type', 'template', 'filename_suffix',
                'flags', 'interrogatory_counts', 'first_set_only_flags'
            ]
            for field in required_fields:
                assert field in profile_data

    def test_profile_differences(self):
        """Test that profiles have appropriate differences."""
        pipeline = ProfilePipeline()
        dataset = create_test_dataset()
        result = pipeline.apply_profiles(dataset)
        
        srogs = result['srogs']
        pods = result['pods']
        admissions = result['admissions']
        
        # Test doc_type differences
        assert srogs['doc_type'] == "SROGs"
        assert pods['doc_type'] == "PODs"
        assert admissions['doc_type'] == "Admissions"
        
        # Test template differences
        assert srogs['template'] == "SROGsMaster.docx"
        assert pods['template'] == "PODsMaster.docx"
        assert admissions['template'] == "AdmissionsMaster.docx"
        
        # Test filename suffix differences
        assert "SROGs" in srogs['filename_suffix']
        assert "PODs" in pods['filename_suffix']
        assert "Admissions" in admissions['filename_suffix']

    def test_interrogatory_count_hierarchy(self):
        """Test that interrogatory counts follow expected hierarchy."""
        pipeline = ProfilePipeline()
        dataset = create_test_dataset()
        result = pipeline.apply_profiles(dataset)
        
        srogs_counts = result['srogs']['interrogatory_counts']
        pods_counts = result['pods']['interrogatory_counts']
        admissions_counts = result['admissions']['interrogatory_counts']
        
        # SROGs should have highest counts
        for flag in ['HasMold', 'HasRatsMice', 'HasPlumbingIssues', 'HasRetaliation']:
            if flag in srogs_counts and flag in admissions_counts:
                assert srogs_counts[flag] >= admissions_counts[flag]
            if flag in srogs_counts and flag in pods_counts:
                assert srogs_counts[flag] >= pods_counts[flag]
        
        # Admissions should generally have higher counts than PODs
        for flag in ['HasMold', 'HasRatsMice', 'HasPlumbingIssues']:
            if flag in admissions_counts and flag in pods_counts:
                assert admissions_counts[flag] >= pods_counts[flag]

    def test_flag_specificity_by_profile(self):
        """Test that each profile has appropriate flag specificity."""
        pipeline = ProfilePipeline()
        dataset = create_test_dataset()
        result = pipeline.apply_profiles(dataset)
        
        srogs_flags = result['srogs']['flags']
        pods_flags = result['pods']['flags']
        admissions_flags = result['admissions']['flags']
        
        # SROGs-specific flags
        assert 'SROGsGeneral' in srogs_flags
        assert srogs_flags['SROGsGeneral'] == True
        
        # PODs-specific flags
        assert 'IsOwnerManager' in pods_flags
        assert 'SROGsGeneral' not in pods_flags
        
        # Admissions-specific flags
        assert 'AdmissionsGeneral' in admissions_flags
        assert admissions_flags['AdmissionsGeneral'] == True

    def test_geography_flags_in_admissions(self):
        """Test that geography flags work correctly in Admissions profile."""
        pipeline = ProfilePipeline()
        
        # Test Los Angeles
        la_dataset = create_los_angeles_dataset()
        la_result = pipeline.apply_single_profile(la_dataset, 'admissions')
        assert la_result['flags']['HasLosAngeles'] == True
        assert la_result['flags']['HasSanFrancisco'] == False
        
        # Test San Francisco
        sf_dataset = create_san_francisco_dataset()
        sf_result = pipeline.apply_single_profile(sf_dataset, 'admissions')
        assert sf_result['flags']['HasLosAngeles'] == False
        assert sf_result['flags']['HasSanFrancisco'] == True

    def test_defendant_role_handling(self):
        """Test that defendant roles are handled correctly across profiles."""
        pipeline = ProfilePipeline()
        
        # Test Owner role
        owner_dataset = create_owner_dataset()
        owner_result = pipeline.apply_profiles(owner_dataset)
        
        for profile_name, profile_data in owner_result.items():
            assert profile_data['flags']['IsOwner'] == True
            assert profile_data['flags']['IsManager'] == False
        
        # Test Manager role
        manager_dataset = create_manager_dataset()
        manager_result = pipeline.apply_profiles(manager_dataset)
        
        for profile_name, profile_data in manager_result.items():
            assert profile_data['flags']['IsOwner'] == False
            assert profile_data['flags']['IsManager'] == True

    def test_collection_processing(self):
        """Test processing of dataset collections."""
        pipeline = ProfilePipeline()
        collection = create_test_dataset_collection()
        
        result = pipeline.apply_profiles_to_collection(collection)
        
        # Should preserve collection structure
        assert 'datasets' in result
        assert 'metadata' in result
        assert len(result['datasets']) == len(collection['datasets'])
        
        # Each dataset should have three profiles
        for dataset in result['datasets']:
            assert len(dataset) == 3
            assert 'srogs' in dataset
            assert 'pods' in dataset
            assert 'admissions' in dataset

    def test_profile_validation(self):
        """Test profile validation functionality."""
        pipeline = ProfilePipeline()
        dataset = create_test_dataset()
        result = pipeline.apply_profiles(dataset)
        
        validation_results = pipeline.validate_profile_datasets(result)
        
        # All profiles should be valid
        for profile_name, missing_fields in validation_results.items():
            assert missing_fields == []

    def test_profile_info_completeness(self):
        """Test that profile info is complete and accurate."""
        pipeline = ProfilePipeline()
        info = pipeline.get_profile_info()
        
        for profile_name, profile_info in info.items():
            # Should have all required fields
            required_fields = [
                'doc_type', 'template', 'filename_suffix',
                'first_set_only_flags', 'total_interrogatory_mappings'
            ]
            for field in required_fields:
                assert field in profile_info
            
            # Should have positive interrogatory mappings
            assert profile_info['total_interrogatory_mappings'] > 0

    def test_error_handling(self):
        """Test error handling in profile pipeline."""
        pipeline = ProfilePipeline()
        dataset = create_test_dataset()
        
        # Test invalid profile type
        with pytest.raises(ValueError):
            pipeline.apply_single_profile(dataset, 'invalid_profile')
        
        # Test with minimal dataset
        minimal_dataset = {
            'dataset_id': 'minimal-001',
            'plaintiff': {'name': 'Test Plaintiff'},
            'defendant': {'name': 'Test Defendant', 'role': 'Owner'},
            'case_metadata': {'filing_city': 'Los Angeles'},
            'flags': {}
        }
        
        result = pipeline.apply_profiles(minimal_dataset)
        
        # Should still work with minimal data
        assert len(result) == 3
        for profile_name, profile_data in result.items():
            assert profile_data['doc_type'] in ['SROGs', 'PODs', 'Admissions']

    def test_performance_with_large_collection(self):
        """Test performance with larger dataset collections."""
        # Create a larger collection
        large_collection = {
            'datasets': [create_test_dataset(dataset_id=f'large-{i}') for i in range(10)],
            'metadata': {'total_datasets': 10, 'phase': 3}
        }
        
        pipeline = ProfilePipeline()
        result = pipeline.apply_profiles_to_collection(large_collection)
        
        # Should handle larger collections
        assert len(result['datasets']) == 10
        assert result['metadata']['total_profile_datasets'] == 30  # 10 datasets * 3 profiles
        
        # Each dataset should have three profiles
        for dataset in result['datasets']:
            assert len(dataset) == 3
