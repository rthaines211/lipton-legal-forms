"""
Tests for SetSplitter class

Tests the core set splitting algorithm including:
- Single set under limit
- Multiple sets over limit
- First-set-only flag handling
- Flag distribution
"""

import pytest
from src.phase5.set_splitter import SetSplitter
from tests.fixtures.phase5_samples import (
    create_small_dataset,
    create_medium_dataset,
    create_large_dataset,
    create_first_set_only_dataset,
    create_minimal_flags_dataset,
    create_empty_flags_dataset,
    create_dataset_with_custom_flags
)


class TestBasicSetSplitting:
    """Test basic set splitting functionality."""

    def test_single_set_under_limit(self):
        """Test dataset with < 120 interrogatories stays in one set."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_small_dataset()  # 60 interrogatories

        result = splitter.split_into_sets(dataset)

        assert result['metadata']['total_sets'] == 1
        assert result['metadata']['total_interrogatories'] == 60
        assert result['metadata']['max_per_set'] == 120

        # Check that doc_type is preserved
        assert result['doc_type'] == 'SROGs'

    def test_multiple_sets_over_limit(self):
        """Test dataset with > 120 interrogatories splits into multiple sets."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_large_dataset()  # 280 interrogatories

        result = splitter.split_into_sets(dataset)

        # Should require at least 3 sets (280 / 120 = 2.33)
        assert result['metadata']['total_sets'] >= 3

        # Verify each set has <= 120 interrogatories
        for set_data in result['sets']:
            assert set_data['total_interrogatories'] <= 120

        # Verify total interrogatories preserved
        total_interrog = sum(s['total_interrogatories'] for s in result['sets'])
        assert total_interrog == result['metadata']['total_interrogatories']

    def test_medium_dataset_two_sets(self):
        """Test dataset requiring exactly 2 sets."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_medium_dataset()  # 156 interrogatories

        result = splitter.split_into_sets(dataset)

        assert result['metadata']['total_sets'] == 2
        assert result['sets'][0]['total_interrogatories'] <= 120
        assert result['sets'][1]['total_interrogatories'] <= 120

    def test_dataset_metadata_preserved(self):
        """Test that dataset metadata is preserved in output."""
        splitter = SetSplitter()
        dataset = create_small_dataset()

        result = splitter.split_into_sets(dataset)

        # Check all metadata fields preserved
        assert result['dataset_id'] == dataset['dataset_id']
        assert result['plaintiff'] == dataset['plaintiff']
        assert result['defendant'] == dataset['defendant']
        assert result['case_metadata'] == dataset['case_metadata']
        assert result['template'] == dataset['template']
        assert result['filename_suffix'] == dataset['filename_suffix']


class TestFirstSetOnlyFlags:
    """Test first-set-only flag handling."""

    def test_first_set_only_flags_in_set_1(self):
        """Test first-set-only flags only appear in Set 1."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_large_dataset()

        result = splitter.split_into_sets(dataset)

        # Check Set 1 has first-set-only flags
        set_1 = result['sets'][0]
        assert 'SROGsGeneral' in set_1['flags']
        assert set_1['flags']['SROGsGeneral'] is True

        # If IsOwner is true in dataset, it should be in Set 1
        if dataset['flags'].get('IsOwner'):
            assert 'IsOwner' in set_1['flags']
            assert set_1['flags']['IsOwner'] is True

        # Check other sets do NOT have first-set-only flags
        if len(result['sets']) > 1:
            for set_data in result['sets'][1:]:
                assert 'SROGsGeneral' not in set_data['flags']
                assert 'IsOwner' not in set_data['flags']
                assert 'IsManager' not in set_data['flags']

    def test_first_set_flags_count_toward_limit(self):
        """Test first-set-only flags count toward 120 limit."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_first_set_only_dataset()

        result = splitter.split_into_sets(dataset)

        set_1 = result['sets'][0]

        # First-set-only flags: SROGsGeneral (10) + IsOwner (15) + IsManager (12) = 37
        # Regular flags: HasMold (24) + HasRatsMice (18) = 42
        # Total: 79
        assert set_1['total_interrogatories'] == 79

    def test_only_first_set_flags_present(self):
        """Test dataset with only first-set-only flags."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_minimal_flags_dataset()

        result = splitter.split_into_sets(dataset)

        assert result['metadata']['total_sets'] == 1
        set_1 = result['sets'][0]

        # Should only have first-set-only flags
        assert 'SROGsGeneral' in set_1['flags']
        assert 'IsManager' in set_1['flags']

        # Total should be 10 + 12 = 22
        assert set_1['total_interrogatories'] == 22


class TestFlagDistribution:
    """Test flag distribution across sets."""

    def test_all_true_flags_included(self):
        """Test that all true flags are included in output."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_large_dataset()

        result = splitter.split_into_sets(dataset)

        # Collect all flags from all sets
        all_flags_in_sets = set()
        for set_data in result['sets']:
            all_flags_in_sets.update(set_data['flags'].keys())

        # Get all true flags from input
        true_flags = {k for k, v in dataset['flags'].items() if v is True}

        # All true flags should be in output
        assert all_flags_in_sets == true_flags

    def test_false_flags_excluded(self):
        """Test that false flags are not included in output."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_small_dataset()

        result = splitter.split_into_sets(dataset)

        # Collect all flags from all sets
        all_flags_in_sets = set()
        for set_data in result['sets']:
            all_flags_in_sets.update(set_data['flags'].keys())

        # Get all false flags from input
        false_flags = {k for k, v in dataset['flags'].items() if v is False}

        # No false flags should be in output
        assert all_flags_in_sets.isdisjoint(false_flags)

    def test_no_duplicate_flags_across_sets(self):
        """Test that flags don't appear in multiple sets."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_large_dataset()

        result = splitter.split_into_sets(dataset)

        # Track flags seen
        seen_flags = set()
        for set_data in result['sets']:
            for flag in set_data['flags'].keys():
                assert flag not in seen_flags, f"Flag {flag} appears in multiple sets"
                seen_flags.add(flag)

    def test_larger_flags_placed_first(self):
        """Test that larger flags are placed first (greedy algorithm)."""
        splitter = SetSplitter(max_interrogatories_per_set=120)

        # Create dataset with specific flag sizes
        dataset = create_dataset_with_custom_flags(
            flags_dict={
                'SmallFlag': True,
                'MediumFlag': True,
                'LargeFlag': True,
                'ExtraLargeFlag': True
            },
            counts_dict={
                'SmallFlag': 5,
                'MediumFlag': 15,
                'LargeFlag': 30,
                'ExtraLargeFlag': 50
            }
        )

        result = splitter.split_into_sets(dataset)

        # Get flags from first set (after first-set-only flags)
        first_set_flags = list(result['sets'][0]['flags'].keys())

        # ExtraLargeFlag should come before SmallFlag
        # (after any first-set-only flags)
        if 'ExtraLargeFlag' in first_set_flags and 'SmallFlag' in first_set_flags:
            extra_large_idx = first_set_flags.index('ExtraLargeFlag')
            small_idx = first_set_flags.index('SmallFlag')
            assert extra_large_idx < small_idx


class TestSetNumbering:
    """Test set numbering and metadata."""

    def test_sets_numbered_sequentially(self):
        """Test sets are numbered 1, 2, 3, etc."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_large_dataset()

        result = splitter.split_into_sets(dataset)

        for i, set_data in enumerate(result['sets']):
            assert set_data['set_number'] == i + 1

    def test_first_set_marked_correctly(self):
        """Test first set is marked with is_first_set=True."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_large_dataset()

        result = splitter.split_into_sets(dataset)

        assert result['sets'][0]['is_first_set'] is True

        # Other sets should be False
        for set_data in result['sets'][1:]:
            assert set_data['is_first_set'] is False

    def test_single_set_marked_as_first(self):
        """Test single set is marked as first set."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_small_dataset()

        result = splitter.split_into_sets(dataset)

        assert len(result['sets']) == 1
        assert result['sets'][0]['is_first_set'] is True


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_flags_dataset(self):
        """Test dataset with no true flags."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_empty_flags_dataset()

        result = splitter.split_into_sets(dataset)

        # Should have 0 sets since no flags are true
        assert result['metadata']['total_sets'] == 0
        assert result['metadata']['total_interrogatories'] == 0
        assert len(result['sets']) == 0

    def test_custom_max_interrogatories(self):
        """Test custom max interrogatories per set."""
        splitter = SetSplitter(max_interrogatories_per_set=50)
        dataset = create_small_dataset()  # 56 interrogatories

        result = splitter.split_into_sets(dataset)

        # Should require 2 sets with max=50
        assert result['metadata']['total_sets'] >= 2
        assert result['metadata']['max_per_set'] == 50

    def test_very_small_max_limit(self):
        """Test with very small max limit."""
        splitter = SetSplitter(max_interrogatories_per_set=10)
        dataset = create_small_dataset()  # 60 interrogatories

        result = splitter.split_into_sets(dataset)

        # Note: First-set-only flags (SROGsGeneral=10 + IsManager=12 = 22)
        # exceed the limit, so first set will have 22 interrogatories.
        # This is expected behavior - first-set-only flags cannot be split.
        # Regular flags (HasMold=24, HasRoaches=14) will each be in their own sets.

        # First set will have first-set-only flags (22)
        assert result['sets'][0]['total_interrogatories'] == 22

        # Remaining sets should have <= limit for regular flags
        for set_data in result['sets'][1:]:
            assert set_data['total_interrogatories'] <= 10 or \
                   set_data['total_interrogatories'] == 14 or \
                   set_data['total_interrogatories'] == 24  # Single flags can exceed limit

    def test_interrogatory_count_zero(self):
        """Test flag with zero interrogatory count."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={'ZeroFlag': True},
            counts_dict={'ZeroFlag': 0}
        )
        splitter = SetSplitter()

        result = splitter.split_into_sets(dataset)

        # Should handle gracefully
        assert 'ZeroFlag' in result['sets'][0]['flags']
        assert result['sets'][0]['total_interrogatories'] == 0
