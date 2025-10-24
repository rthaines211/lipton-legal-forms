"""
SROGs Profile Tests

Test suite for SROGs document profile implementation.
"""

import pytest
from src.phase4.profiles.srogs import SROGsProfile
from tests.fixtures.phase4_samples import (
    create_test_dataset, 
    create_owner_dataset, 
    create_manager_dataset
)


class TestSROGsProfile:
    """Test cases for SROGs profile."""

    def test_doc_type_property(self):
        """Test doc_type property returns correct value."""
        profile = SROGsProfile()
        assert profile.doc_type == "SROGs"

    def test_template_name_property(self):
        """Test template_name property returns correct value."""
        profile = SROGsProfile()
        assert profile.template_name == "SROGsMaster.docx"

    def test_filename_suffix_property(self):
        """Test filename_suffix property returns correct value."""
        profile = SROGsProfile()
        assert profile.filename_suffix == "Discovery Propounded SROGs"

    def test_first_set_only_flags_property(self):
        """Test first_set_only_flags property returns correct flags."""
        profile = SROGsProfile()
        expected_flags = ["SROGsGeneral", "IsOwner", "IsManager"]
        assert profile.first_set_only_flags == expected_flags

    def test_interrogatory_counts_property(self):
        """Test interrogatory_counts property returns correct mappings."""
        profile = SROGsProfile()
        counts = profile.interrogatory_counts
        
        # Test some key mappings
        assert counts["HasMold"] == 24
        assert counts["HasRatsMice"] == 18
        assert counts["HasPlumbingIssues"] == 22
        assert counts["HasRetaliation"] == 20
        
        # Test that all counts are positive integers
        for flag, count in counts.items():
            assert isinstance(count, int)
            assert count > 0

    def test_adds_srogs_general_flag(self):
        """Test SROGsGeneral flag always added."""
        profile = SROGsProfile()
        dataset = create_test_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert result['flags']['SROGsGeneral'] == True

    def test_defendant_role_flags_owner(self):
        """Test IsOwner/IsManager flags for Owner defendant role."""
        profile = SROGsProfile()
        dataset = create_owner_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert result['flags']['IsOwner'] == True
        assert result['flags']['IsManager'] == False

    def test_defendant_role_flags_manager(self):
        """Test IsOwner/IsManager flags for Manager defendant role."""
        profile = SROGsProfile()
        dataset = create_manager_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert result['flags']['IsOwner'] == False
        assert result['flags']['IsManager'] == True

    def test_defendant_role_flags_other(self):
        """Test IsOwner/IsManager flags for other defendant roles."""
        profile = SROGsProfile()
        dataset = create_test_dataset(defendant={'role': 'Tenant'})
        
        result = profile.apply_profile(dataset)
        
        assert result['flags']['IsOwner'] == False
        assert result['flags']['IsManager'] == False

    def test_apply_profile_metadata(self):
        """Test that apply_profile adds correct metadata."""
        profile = SROGsProfile()
        dataset = create_test_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert result['doc_type'] == "SROGs"
        assert result['template'] == "SROGsMaster.docx"
        assert result['filename_suffix'] == "Discovery Propounded SROGs"
        assert result['dataset_id'] == f"{dataset['dataset_id']}-srogs"

    def test_apply_profile_preserves_original_data(self):
        """Test that apply_profile preserves original dataset data."""
        profile = SROGsProfile()
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
        profile = SROGsProfile()
        dataset = create_test_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert 'interrogatory_counts' in result
        assert result['interrogatory_counts'] == profile.interrogatory_counts

    def test_apply_profile_adds_first_set_only_flags(self):
        """Test that apply_profile adds first_set_only_flags."""
        profile = SROGsProfile()
        dataset = create_test_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert 'first_set_only_flags' in result
        assert result['first_set_only_flags'] == profile.first_set_only_flags

    def test_apply_profile_deep_copy(self):
        """Test that apply_profile doesn't mutate original dataset."""
        profile = SROGsProfile()
        dataset = create_test_dataset()
        original_flags = dataset['flags'].copy()
        
        result = profile.apply_profile(dataset)
        
        # Original dataset should be unchanged
        assert dataset['flags'] == original_flags
        # Result should have additional flags
        assert len(result['flags']) > len(original_flags)

    def test_interrogatory_counts_completeness(self):
        """Test that interrogatory counts cover all expected flag categories."""
        profile = SROGsProfile()
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

    def test_srogs_has_highest_counts(self):
        """Test that SROGs has the highest interrogatory counts."""
        profile = SROGsProfile()
        counts = profile.interrogatory_counts
        
        # SROGs should have the highest counts for key issues
        assert counts["HasMold"] == 24  # Highest
        assert counts["HasRatsMice"] == 18  # High
        assert counts["HasPlumbingIssues"] == 22  # High
        assert counts["HasRetaliation"] == 20  # High

    def test_case_insensitive_role_matching(self):
        """Test that defendant role matching is case insensitive."""
        profile = SROGsProfile()
        
        # Test various case combinations
        test_cases = [
            ('owner', True, False),
            ('Owner', True, False),
            ('OWNER', True, False),
            ('manager', False, True),
            ('Manager', False, True),
            ('MANAGER', False, True),
            ('tenant', False, False),
            ('', False, False)
        ]
        
        for role, expected_owner, expected_manager in test_cases:
            dataset = create_test_dataset(defendant={'role': role})
            result = profile.apply_profile(dataset)
            
            assert result['flags']['IsOwner'] == expected_owner
            assert result['flags']['IsManager'] == expected_manager
