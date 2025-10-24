"""
PODs Profile Tests

Test suite for PODs document profile implementation.
"""

import pytest
from src.phase4.profiles.pods import PODsProfile
from tests.fixtures.phase4_samples import (
    create_test_dataset, 
    create_owner_dataset, 
    create_manager_dataset
)


class TestPODsProfile:
    """Test cases for PODs profile."""

    def test_doc_type_property(self):
        """Test doc_type property returns correct value."""
        profile = PODsProfile()
        assert profile.doc_type == "PODs"

    def test_template_name_property(self):
        """Test template_name property returns correct value."""
        profile = PODsProfile()
        assert profile.template_name == "PODsMaster.docx"

    def test_filename_suffix_property(self):
        """Test filename_suffix property returns correct value."""
        profile = PODsProfile()
        assert profile.filename_suffix == "Discovery Propounded PODs"

    def test_first_set_only_flags_property(self):
        """Test first_set_only_flags property returns correct flags."""
        profile = PODsProfile()
        expected_flags = ["IsOwner", "IsManager"]  # No SROGsGeneral
        assert profile.first_set_only_flags == expected_flags

    def test_interrogatory_counts_property(self):
        """Test interrogatory_counts property returns correct mappings."""
        profile = PODsProfile()
        counts = profile.interrogatory_counts
        
        # Test some key mappings (lower than SROGs)
        assert counts["HasMold"] == 4
        assert counts["HasRatsMice"] == 6
        assert counts["HasPlumbingIssues"] == 8
        assert counts["HasRetaliation"] == 6
        
        # Test that all counts are positive integers
        for flag, count in counts.items():
            assert isinstance(count, int)
            assert count > 0

    def test_no_srogs_general_flag(self):
        """Test PODs does not have SROGsGeneral flag."""
        profile = PODsProfile()
        dataset = create_test_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert 'SROGsGeneral' not in result['flags']

    def test_removes_srogs_general_if_present(self):
        """Test that SROGsGeneral is removed if present in input."""
        profile = PODsProfile()
        dataset = create_test_dataset()
        dataset['flags']['SROGsGeneral'] = True  # Add it first
        
        result = profile.apply_profile(dataset)
        
        assert 'SROGsGeneral' not in result['flags']

    def test_defendant_role_flags_owner(self):
        """Test IsOwner/IsManager flags for Owner defendant role."""
        profile = PODsProfile()
        dataset = create_owner_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert result['flags']['IsOwner'] == True
        assert result['flags']['IsManager'] == False
        assert result['flags']['IsOwnerManager'] == True

    def test_defendant_role_flags_manager(self):
        """Test IsOwner/IsManager flags for Manager defendant role."""
        profile = PODsProfile()
        dataset = create_manager_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert result['flags']['IsOwner'] == False
        assert result['flags']['IsManager'] == True
        assert result['flags']['IsOwnerManager'] == True

    def test_defendant_role_flags_other(self):
        """Test IsOwner/IsManager flags for other defendant roles."""
        profile = PODsProfile()
        dataset = create_test_dataset(defendant={'role': 'Tenant'})
        
        result = profile.apply_profile(dataset)
        
        assert result['flags']['IsOwner'] == False
        assert result['flags']['IsManager'] == False
        assert result['flags']['IsOwnerManager'] == False

    def test_is_owner_manager_combined_flag(self):
        """Test IsOwnerManager flag combines Owner and Manager roles."""
        profile = PODsProfile()
        
        # Test Owner
        dataset_owner = create_test_dataset(defendant={'role': 'Owner'})
        result_owner = profile.apply_profile(dataset_owner)
        assert result_owner['flags']['IsOwnerManager'] == True
        
        # Test Manager
        dataset_manager = create_test_dataset(defendant={'role': 'Manager'})
        result_manager = profile.apply_profile(dataset_manager)
        assert result_manager['flags']['IsOwnerManager'] == True
        
        # Test neither
        dataset_other = create_test_dataset(defendant={'role': 'Tenant'})
        result_other = profile.apply_profile(dataset_other)
        assert result_other['flags']['IsOwnerManager'] == False

    def test_apply_profile_metadata(self):
        """Test that apply_profile adds correct metadata."""
        profile = PODsProfile()
        dataset = create_test_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert result['doc_type'] == "PODs"
        assert result['template'] == "PODsMaster.docx"
        assert result['filename_suffix'] == "Discovery Propounded PODs"
        assert result['dataset_id'] == f"{dataset['dataset_id']}-pods"

    def test_apply_profile_preserves_original_data(self):
        """Test that apply_profile preserves original dataset data."""
        profile = PODsProfile()
        dataset = create_test_dataset()
        original_plaintiff = dataset['plaintiff'].copy()
        original_defendant = dataset['defendant'].copy()
        original_case_metadata = dataset['case_metadata'].copy()
        
        result = profile.apply_profile(dataset)
        
        assert result['plaintiff'] == original_plaintiff
        assert result['defendant'] == original_defendant
        assert result['case_metadata'] == original_case_metadata

    def test_apply_profile_adds_interrogatory_counts(self):
        """Test that apply_profile adds interrogatory counts."""
        profile = PODsProfile()
        dataset = create_test_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert 'interrogatory_counts' in result
        assert result['interrogatory_counts'] == profile.interrogatory_counts

    def test_apply_profile_adds_first_set_only_flags(self):
        """Test that apply_profile adds first_set_only_flags."""
        profile = PODsProfile()
        dataset = create_test_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert 'first_set_only_flags' in result
        assert result['first_set_only_flags'] == profile.first_set_only_flags

    def test_apply_profile_deep_copy(self):
        """Test that apply_profile doesn't mutate original dataset."""
        profile = PODsProfile()
        dataset = create_test_dataset()
        original_flags = dataset['flags'].copy()
        
        result = profile.apply_profile(dataset)
        
        # Original dataset should be unchanged
        assert dataset['flags'] == original_flags
        # Result should have additional flags
        assert len(result['flags']) > len(original_flags)

    def test_interrogatory_counts_completeness(self):
        """Test that interrogatory counts cover all expected flag categories."""
        profile = PODsProfile()
        counts = profile.interrogatory_counts
        
        # Test vermin & insects
        assert "HasRatsMice" in counts
        assert "HasBedbugs" in counts
        assert "HasRoaches" in counts
        
        # Test environmental
        assert "HasMold" in counts
        assert "HasLeadPaint" in counts
        
        # Test housing
        assert "HasPlumbingIssues" in counts
        assert "HasElectricalIssues" in counts
        
        # Test safety
        assert "HasInoperableLocks" in counts
        assert "HasSmokeDetectorIssues" in counts
        
        # Test legal
        assert "HasRetaliation" in counts
        assert "HasDiscrimination" in counts

    def test_pods_has_medium_counts(self):
        """Test that PODs has medium interrogatory counts."""
        profile = PODsProfile()
        counts = profile.interrogatory_counts
        
        # PODs should have medium counts
        assert counts["HasMold"] == 4  # Medium
        assert counts["HasRatsMice"] == 6  # Medium
        assert counts["HasPlumbingIssues"] == 8  # Medium
        assert counts["HasRetaliation"] == 6  # Medium

    def test_case_insensitive_role_matching(self):
        """Test that defendant role matching is case insensitive."""
        profile = PODsProfile()
        
        # Test various case combinations
        test_cases = [
            ('owner', True, False, True),
            ('Owner', True, False, True),
            ('OWNER', True, False, True),
            ('manager', False, True, True),
            ('Manager', False, True, True),
            ('MANAGER', False, True, True),
            ('tenant', False, False, False),
            ('', False, False, False)
        ]
        
        for role, expected_owner, expected_manager, expected_owner_manager in test_cases:
            dataset = create_test_dataset(defendant={'role': role})
            result = profile.apply_profile(dataset)
            
            assert result['flags']['IsOwner'] == expected_owner
            assert result['flags']['IsManager'] == expected_manager
            assert result['flags']['IsOwnerManager'] == expected_owner_manager
