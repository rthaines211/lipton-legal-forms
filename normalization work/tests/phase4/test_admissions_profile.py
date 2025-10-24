"""
Admissions Profile Tests

Test suite for Admissions document profile implementation.
"""

import pytest
from src.phase4.profiles.admissions import AdmissionsProfile
from tests.fixtures.phase4_samples import (
    create_test_dataset, 
    create_owner_dataset, 
    create_manager_dataset,
    create_los_angeles_dataset,
    create_san_francisco_dataset
)


class TestAdmissionsProfile:
    """Test cases for Admissions profile."""

    def test_doc_type_property(self):
        """Test doc_type property returns correct value."""
        profile = AdmissionsProfile()
        assert profile.doc_type == "Admissions"

    def test_template_name_property(self):
        """Test template_name property returns correct value."""
        profile = AdmissionsProfile()
        assert profile.template_name == "AdmissionsMaster.docx"

    def test_filename_suffix_property(self):
        """Test filename_suffix property returns correct value."""
        profile = AdmissionsProfile()
        assert profile.filename_suffix == "Discovery Request for Admissions"

    def test_first_set_only_flags_property(self):
        """Test first_set_only_flags property returns correct flags."""
        profile = AdmissionsProfile()
        expected_flags = ["AdmissionsGeneral", "IsOwner", "IsManager", "HasLosAngeles"]
        assert profile.first_set_only_flags == expected_flags

    def test_interrogatory_counts_property(self):
        """Test interrogatory_counts property returns correct mappings."""
        profile = AdmissionsProfile()
        counts = profile.interrogatory_counts
        
        # Test some key mappings (lower than SROGs, higher than PODs)
        assert counts["HasMold"] == 6
        assert counts["HasRatsMice"] == 8
        assert counts["HasPlumbingIssues"] == 10
        assert counts["HasRetaliation"] == 8
        
        # Test that all counts are positive integers
        for flag, count in counts.items():
            assert isinstance(count, int)
            assert count > 0

    def test_adds_admissions_general_flag(self):
        """Test AdmissionsGeneral flag always added."""
        profile = AdmissionsProfile()
        dataset = create_test_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert result['flags']['AdmissionsGeneral'] == True

    def test_defendant_role_flags_owner(self):
        """Test IsOwner/IsManager flags for Owner defendant role."""
        profile = AdmissionsProfile()
        dataset = create_owner_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert result['flags']['IsOwner'] == True
        assert result['flags']['IsManager'] == False

    def test_defendant_role_flags_manager(self):
        """Test IsOwner/IsManager flags for Manager defendant role."""
        profile = AdmissionsProfile()
        dataset = create_manager_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert result['flags']['IsOwner'] == False
        assert result['flags']['IsManager'] == True

    def test_defendant_role_flags_other(self):
        """Test IsOwner/IsManager flags for other defendant roles."""
        profile = AdmissionsProfile()
        dataset = create_test_dataset(defendant={'role': 'Tenant'})
        
        result = profile.apply_profile(dataset)
        
        assert result['flags']['IsOwner'] == False
        assert result['flags']['IsManager'] == False

    def test_geography_flags_los_angeles(self):
        """Test geography-based flags for Los Angeles."""
        profile = AdmissionsProfile()
        dataset = create_los_angeles_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert result['flags']['HasLosAngeles'] == True
        assert result['flags']['HasSanFrancisco'] == False

    def test_geography_flags_san_francisco(self):
        """Test geography-based flags for San Francisco."""
        profile = AdmissionsProfile()
        dataset = create_san_francisco_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert result['flags']['HasLosAngeles'] == False
        assert result['flags']['HasSanFrancisco'] == True

    def test_geography_flags_case_insensitive(self):
        """Test geography flags are case insensitive."""
        profile = AdmissionsProfile()
        
        test_cases = [
            ('los angeles', True, False),
            ('Los Angeles', True, False),
            ('LOS ANGELES', True, False),
            ('san francisco', False, True),
            ('San Francisco', False, True),
            ('SAN FRANCISCO', False, True),
            ('oakland', False, False),
            ('', False, False)
        ]
        
        for city, expected_la, expected_sf in test_cases:
            dataset = create_test_dataset(case_metadata={'filing_city': city})
            result = profile.apply_profile(dataset)
            
            assert result['flags']['HasLosAngeles'] == expected_la
            assert result['flags']['HasSanFrancisco'] == expected_sf

    def test_additional_geography_flags(self):
        """Test additional geography flags for major California cities."""
        profile = AdmissionsProfile()
        
        test_cases = [
            ('oakland', 'HasOakland'),
            ('san diego', 'HasSanDiego'),
            ('sacramento', 'HasSacramento'),
            ('fresno', 'HasFresno'),
            ('long beach', 'HasLongBeach'),
            ('bakersfield', 'HasBakersfield'),
            ('anaheim', 'HasAnaheim'),
            ('santa ana', 'HasSantaAna')
        ]
        
        for city, expected_flag in test_cases:
            dataset = create_test_dataset(case_metadata={'filing_city': city})
            result = profile.apply_profile(dataset)
            
            assert result['flags'][expected_flag] == True

    def test_apply_profile_metadata(self):
        """Test that apply_profile adds correct metadata."""
        profile = AdmissionsProfile()
        dataset = create_test_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert result['doc_type'] == "Admissions"
        assert result['template'] == "AdmissionsMaster.docx"
        assert result['filename_suffix'] == "Discovery Request for Admissions"
        assert result['dataset_id'] == f"{dataset['dataset_id']}-admissions"

    def test_apply_profile_preserves_original_data(self):
        """Test that apply_profile preserves original dataset data."""
        profile = AdmissionsProfile()
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
        profile = AdmissionsProfile()
        dataset = create_test_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert 'interrogatory_counts' in result
        assert result['interrogatory_counts'] == profile.interrogatory_counts

    def test_apply_profile_adds_first_set_only_flags(self):
        """Test that apply_profile adds first_set_only_flags."""
        profile = AdmissionsProfile()
        dataset = create_test_dataset()
        
        result = profile.apply_profile(dataset)
        
        assert 'first_set_only_flags' in result
        assert result['first_set_only_flags'] == profile.first_set_only_flags

    def test_apply_profile_deep_copy(self):
        """Test that apply_profile doesn't mutate original dataset."""
        profile = AdmissionsProfile()
        dataset = create_test_dataset()
        original_flags = dataset['flags'].copy()
        
        result = profile.apply_profile(dataset)
        
        # Original dataset should be unchanged
        assert dataset['flags'] == original_flags
        # Result should have additional flags
        assert len(result['flags']) > len(original_flags)

    def test_interrogatory_counts_completeness(self):
        """Test that interrogatory counts cover all expected flag categories."""
        profile = AdmissionsProfile()
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

    def test_admissions_has_medium_counts(self):
        """Test that Admissions has medium interrogatory counts."""
        profile = AdmissionsProfile()
        counts = profile.interrogatory_counts
        
        # Admissions should have medium counts (between SROGs and PODs)
        assert counts["HasMold"] == 6  # Medium
        assert counts["HasRatsMice"] == 8  # Medium
        assert counts["HasPlumbingIssues"] == 10  # Medium
        assert counts["HasRetaliation"] == 8  # Medium

    def test_case_insensitive_role_matching(self):
        """Test that defendant role matching is case insensitive."""
        profile = AdmissionsProfile()
        
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

    def test_geography_flags_partial_matching(self):
        """Test that geography flags work with partial city name matching."""
        profile = AdmissionsProfile()
        
        # Test partial matches
        test_cases = [
            ('Los Angeles County', True, False),
            ('City of Los Angeles', True, False),
            ('San Francisco Bay Area', False, True),
            ('Greater San Francisco', False, True)
        ]
        
        for city, expected_la, expected_sf in test_cases:
            dataset = create_test_dataset(case_metadata={'filing_city': city})
            result = profile.apply_profile(dataset)
            
            assert result['flags']['HasLosAngeles'] == expected_la
            assert result['flags']['HasSanFrancisco'] == expected_sf
