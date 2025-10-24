"""
Tests for Interrogatory Numbering

Tests the continuous interrogatory numbering across sets:
- Set 1: 1-120
- Set 2: 121-240
- Set 3: 241-360
- etc.
"""

import pytest
from src.phase5.set_splitter import SetSplitter
from tests.fixtures.phase5_samples import (
    create_small_dataset,
    create_medium_dataset,
    create_large_dataset,
    create_dataset_with_custom_flags
)


class TestInterrogatoryRanges:
    """Test interrogatory range calculations."""

    def test_single_set_starts_at_one(self):
        """Test single set starts at interrogatory 1."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_small_dataset()  # 60 interrogatories

        result = splitter.split_into_sets(dataset)

        set_1 = result['sets'][0]
        assert set_1['interrogatory_start'] == 1
        assert set_1['interrogatory_end'] == 60

    def test_interrogatory_ranges_continuous(self):
        """Test interrogatory ranges are continuous across sets."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_large_dataset()  # 280 interrogatories

        result = splitter.split_into_sets(dataset)

        # Verify continuous numbering
        expected_start = 1
        for set_data in result['sets']:
            assert set_data['interrogatory_start'] == expected_start
            expected_start = set_data['interrogatory_end'] + 1

    def test_no_gaps_in_numbering(self):
        """Test there are no gaps in interrogatory numbering."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_large_dataset()

        result = splitter.split_into_sets(dataset)

        # Check each set connects to the next
        for i in range(len(result['sets']) - 1):
            current_set = result['sets'][i]
            next_set = result['sets'][i + 1]

            # Next set should start immediately after current set ends
            assert next_set['interrogatory_start'] == current_set['interrogatory_end'] + 1

    def test_final_interrogatory_matches_total(self):
        """Test final interrogatory number matches total count."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_large_dataset()

        result = splitter.split_into_sets(dataset)

        # Last set's end should match total interrogatories
        last_set = result['sets'][-1]
        assert last_set['interrogatory_end'] == result['metadata']['total_interrogatories']


class TestStartEndCorrectness:
    """Test start/end numbers match total count."""

    def test_interrogatory_start_end_match_count(self):
        """Test start/end match total count for each set."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_medium_dataset()

        result = splitter.split_into_sets(dataset)

        for set_data in result['sets']:
            expected_count = set_data['interrogatory_end'] - set_data['interrogatory_start'] + 1
            assert set_data['total_interrogatories'] == expected_count

    def test_single_interrogatory_set(self):
        """Test set with single interrogatory."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={'SingleFlag': True},
            counts_dict={'SingleFlag': 1}
        )
        splitter = SetSplitter()

        result = splitter.split_into_sets(dataset)

        set_1 = result['sets'][0]
        assert set_1['interrogatory_start'] == 1
        assert set_1['interrogatory_end'] == 1
        assert set_1['total_interrogatories'] == 1

    def test_exact_120_interrogatories(self):
        """Test set with exactly 120 interrogatories."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={'ExactFlag': True},
            counts_dict={'ExactFlag': 120}
        )
        splitter = SetSplitter(max_interrogatories_per_set=120)

        result = splitter.split_into_sets(dataset)

        assert result['metadata']['total_sets'] == 1
        set_1 = result['sets'][0]
        assert set_1['interrogatory_start'] == 1
        assert set_1['interrogatory_end'] == 120
        assert set_1['total_interrogatories'] == 120

    def test_121_interrogatories_splits_into_two(self):
        """Test 121 interrogatories splits into two sets."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={'Flag1': True, 'Flag2': True},
            counts_dict={'Flag1': 120, 'Flag2': 1}
        )
        splitter = SetSplitter(max_interrogatories_per_set=120)

        result = splitter.split_into_sets(dataset)

        assert result['metadata']['total_sets'] == 2

        set_1 = result['sets'][0]
        assert set_1['interrogatory_start'] == 1
        assert set_1['interrogatory_end'] == 120

        set_2 = result['sets'][1]
        assert set_2['interrogatory_start'] == 121
        assert set_2['interrogatory_end'] == 121


class TestMultipleSetNumbering:
    """Test numbering across multiple sets."""

    def test_three_sets_numbering(self):
        """Test three sets have correct continuous numbering."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_large_dataset()  # Should create 3+ sets

        result = splitter.split_into_sets(dataset)

        assert result['metadata']['total_sets'] >= 3

        # Check first three sets
        set_1 = result['sets'][0]
        set_2 = result['sets'][1]
        set_3 = result['sets'][2]

        # Set 1 should start at 1
        assert set_1['interrogatory_start'] == 1

        # Set 2 should start after Set 1 ends
        assert set_2['interrogatory_start'] == set_1['interrogatory_end'] + 1

        # Set 3 should start after Set 2 ends
        assert set_3['interrogatory_start'] == set_2['interrogatory_end'] + 1

    def test_large_dataset_numbering_consistency(self):
        """Test large dataset maintains numbering consistency."""
        splitter = SetSplitter(max_interrogatories_per_set=50)
        dataset = create_large_dataset()  # 280 interrogatories

        result = splitter.split_into_sets(dataset)

        # With max=50, should have 6+ sets
        assert result['metadata']['total_sets'] >= 6

        # Verify all sets have continuous numbering
        for i in range(len(result['sets']) - 1):
            current = result['sets'][i]
            next_set = result['sets'][i + 1]
            assert next_set['interrogatory_start'] == current['interrogatory_end'] + 1

    def test_uneven_set_sizes(self):
        """Test numbering works with uneven set sizes."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={
                'Flag1': True,  # 100
                'Flag2': True,  # 50
                'Flag3': True,  # 30
            },
            counts_dict={
                'Flag1': 100,
                'Flag2': 50,
                'Flag3': 30
            }
        )
        splitter = SetSplitter(max_interrogatories_per_set=120)

        result = splitter.split_into_sets(dataset)

        # Set 1: Flag1 (100) + Flag2 (50) = 150, but Flag2 won't fit
        # Set 1: Flag1 (100)
        # Set 2: Flag2 (50) + Flag3 (30) = 80

        set_1 = result['sets'][0]
        set_2 = result['sets'][1]

        assert set_1['interrogatory_start'] == 1
        assert set_1['interrogatory_end'] == 100

        assert set_2['interrogatory_start'] == 101
        assert set_2['interrogatory_end'] == 180


class TestEdgeCaseNumbering:
    """Test edge cases in numbering."""

    def test_zero_interrogatories_numbering(self):
        """Test numbering with zero interrogatories."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={'ZeroFlag': True, 'NormalFlag': True},
            counts_dict={'ZeroFlag': 0, 'NormalFlag': 10}
        )
        splitter = SetSplitter()

        result = splitter.split_into_sets(dataset)

        set_1 = result['sets'][0]
        assert set_1['interrogatory_start'] == 1
        assert set_1['interrogatory_end'] == 10
        assert set_1['total_interrogatories'] == 10

    def test_multiple_zero_count_flags(self):
        """Test multiple flags with zero counts."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={
                'Zero1': True,
                'Zero2': True,
                'Normal': True,
                'Zero3': True
            },
            counts_dict={
                'Zero1': 0,
                'Zero2': 0,
                'Normal': 25,
                'Zero3': 0
            }
        )
        splitter = SetSplitter()

        result = splitter.split_into_sets(dataset)

        # Only Normal flag contributes to count
        set_1 = result['sets'][0]
        assert set_1['total_interrogatories'] == 25
        assert set_1['interrogatory_start'] == 1
        assert set_1['interrogatory_end'] == 25

    def test_custom_max_interrogatories_numbering(self):
        """Test numbering with custom max interrogatories."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={'Flag1': True, 'Flag2': True, 'Flag3': True},
            counts_dict={'Flag1': 30, 'Flag2': 30, 'Flag3': 30}
        )
        splitter = SetSplitter(max_interrogatories_per_set=50)

        result = splitter.split_into_sets(dataset)

        # Should create 2 sets
        # Set 1: Flag1 (30) + Flag2 (30) = 60, but exceeds 50
        # Set 1: Flag1 (30)
        # Set 2: Flag2 (30) + Flag3 (30) = 60, but exceeds 50
        # Set 2: Flag2 (30)
        # Set 3: Flag3 (30)

        assert result['metadata']['total_sets'] == 3

        assert result['sets'][0]['interrogatory_start'] == 1
        assert result['sets'][0]['interrogatory_end'] == 30

        assert result['sets'][1]['interrogatory_start'] == 31
        assert result['sets'][1]['interrogatory_end'] == 60

        assert result['sets'][2]['interrogatory_start'] == 61
        assert result['sets'][2]['interrogatory_end'] == 90


class TestTotalCount:
    """Test total interrogatory counts."""

    def test_sum_equals_total(self):
        """Test sum of all set counts equals total."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_large_dataset()

        result = splitter.split_into_sets(dataset)

        # Sum all set interrogatories
        sum_of_sets = sum(s['total_interrogatories'] for s in result['sets'])

        assert sum_of_sets == result['metadata']['total_interrogatories']

    def test_total_matches_input_flags(self):
        """Test total interrogatories match sum of input flag counts."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_medium_dataset()

        result = splitter.split_into_sets(dataset)

        # Calculate expected total from true flags
        expected_total = sum(
            dataset['interrogatory_counts'][flag]
            for flag, value in dataset['flags'].items()
            if value is True
        )

        assert result['metadata']['total_interrogatories'] == expected_total

    def test_range_span_equals_count(self):
        """Test interrogatory range span equals count."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_small_dataset()

        result = splitter.split_into_sets(dataset)

        for set_data in result['sets']:
            span = set_data['interrogatory_end'] - set_data['interrogatory_start'] + 1
            assert span == set_data['total_interrogatories']
