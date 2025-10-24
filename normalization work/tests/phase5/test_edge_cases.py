"""
Tests for Edge Cases

Comprehensive edge case testing including:
- Empty datasets
- Single flag scenarios
- Boundary conditions
- Large flag counts
- Pipeline integration
"""

import pytest
from src.phase5.set_splitter import SetSplitter
from src.phase5.splitting_pipeline import SplittingPipeline
from tests.fixtures.phase5_samples import (
    create_empty_flags_dataset,
    create_minimal_flags_dataset,
    create_dataset_with_custom_flags,
    create_profile_datasets,
    create_profiled_collection
)


class TestEmptyAndMinimalDatasets:
    """Test empty and minimal datasets."""

    def test_empty_flags_dataset(self):
        """Test dataset with no true flags."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_empty_flags_dataset()

        result = splitter.split_into_sets(dataset)

        # Should have 0 sets since no flags are true
        assert result['metadata']['total_sets'] == 0
        assert result['metadata']['total_interrogatories'] == 0
        assert len(result['sets']) == 0

    def test_minimal_flags_dataset(self):
        """Test dataset with only first-set-only flags."""
        splitter = SetSplitter(max_interrogatories_per_set=120)
        dataset = create_minimal_flags_dataset()

        result = splitter.split_into_sets(dataset)

        # Should have 1 set with only first-set-only flags
        assert result['metadata']['total_sets'] == 1
        assert result['sets'][0]['is_first_set'] is True

    def test_single_flag_dataset(self):
        """Test dataset with single flag."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={'OnlyFlag': True},
            counts_dict={'OnlyFlag': 25}
        )
        splitter = SetSplitter()

        result = splitter.split_into_sets(dataset)

        assert result['metadata']['total_sets'] == 1
        assert result['metadata']['total_interrogatories'] == 25

    def test_all_false_except_one(self):
        """Test dataset where all flags are false except one."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={
                'False1': False,
                'False2': False,
                'True1': True,
                'False3': False
            },
            counts_dict={
                'False1': 10,
                'False2': 15,
                'True1': 20,
                'False3': 25
            }
        )
        splitter = SetSplitter()

        result = splitter.split_into_sets(dataset)

        assert result['metadata']['total_sets'] == 1
        assert result['metadata']['total_interrogatories'] == 20
        assert 'True1' in result['sets'][0]['flags']


class TestBoundaryConditions:
    """Test boundary conditions."""

    def test_exactly_120_interrogatories(self):
        """Test dataset with exactly 120 interrogatories."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={'Exact120': True},
            counts_dict={'Exact120': 120}
        )
        splitter = SetSplitter(max_interrogatories_per_set=120)

        result = splitter.split_into_sets(dataset)

        assert result['metadata']['total_sets'] == 1
        assert result['sets'][0]['total_interrogatories'] == 120

    def test_121_interrogatories_splits(self):
        """Test 121 interrogatories splits into two sets."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={'Flag1': True, 'Flag2': True},
            counts_dict={'Flag1': 120, 'Flag2': 1}
        )
        splitter = SetSplitter(max_interrogatories_per_set=120)

        result = splitter.split_into_sets(dataset)

        assert result['metadata']['total_sets'] == 2
        assert result['sets'][0]['total_interrogatories'] == 120
        assert result['sets'][1]['total_interrogatories'] == 1

    def test_119_interrogatories_single_set(self):
        """Test 119 interrogatories stays in single set."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={'Flag1': True},
            counts_dict={'Flag1': 119}
        )
        splitter = SetSplitter(max_interrogatories_per_set=120)

        result = splitter.split_into_sets(dataset)

        assert result['metadata']['total_sets'] == 1

    def test_one_interrogatory(self):
        """Test single interrogatory."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={'Single': True},
            counts_dict={'Single': 1}
        )
        splitter = SetSplitter()

        result = splitter.split_into_sets(dataset)

        assert result['metadata']['total_sets'] == 1
        assert result['metadata']['total_interrogatories'] == 1
        assert result['sets'][0]['interrogatory_start'] == 1
        assert result['sets'][0]['interrogatory_end'] == 1

    def test_zero_interrogatory_count(self):
        """Test flag with zero interrogatory count."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={'ZeroFlag': True, 'NormalFlag': True},
            counts_dict={'ZeroFlag': 0, 'NormalFlag': 10}
        )
        splitter = SetSplitter()

        result = splitter.split_into_sets(dataset)

        # Zero-count flags should be included but not affect numbering
        assert 'ZeroFlag' in result['sets'][0]['flags']
        assert result['sets'][0]['total_interrogatories'] == 10


class TestLargeValues:
    """Test with large values."""

    def test_single_large_flag_exceeds_limit(self):
        """Test single flag with > 120 interrogatories."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={'HugeFlag': True},
            counts_dict={'HugeFlag': 150}
        )
        splitter = SetSplitter(max_interrogatories_per_set=120)

        result = splitter.split_into_sets(dataset)

        # Should still create a set even if it exceeds limit
        # (single flag cannot be split)
        assert result['metadata']['total_sets'] == 1
        assert result['sets'][0]['total_interrogatories'] == 150

    def test_many_small_flags(self):
        """Test many flags with small counts."""
        flags_dict = {f'Flag{i}': True for i in range(100)}
        counts_dict = {f'Flag{i}': 2 for i in range(100)}

        dataset = create_dataset_with_custom_flags(flags_dict, counts_dict)
        splitter = SetSplitter(max_interrogatories_per_set=120)

        result = splitter.split_into_sets(dataset)

        # 100 flags * 2 = 200 interrogatories
        assert result['metadata']['total_interrogatories'] == 200
        assert result['metadata']['total_sets'] >= 2

    def test_very_large_dataset(self):
        """Test dataset with 1000+ interrogatories."""
        flags_dict = {f'Flag{i}': True for i in range(50)}
        counts_dict = {f'Flag{i}': 25 for i in range(50)}

        dataset = create_dataset_with_custom_flags(flags_dict, counts_dict)
        splitter = SetSplitter(max_interrogatories_per_set=120)

        result = splitter.split_into_sets(dataset)

        # 50 flags * 25 = 1250 interrogatories
        assert result['metadata']['total_interrogatories'] == 1250
        # Should require at least 11 sets (1250 / 120 = 10.4)
        assert result['metadata']['total_sets'] >= 11

    def test_max_limit_of_1(self):
        """Test with max limit of 1 interrogatory per set."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={'Flag1': True, 'Flag2': True, 'Flag3': True},
            counts_dict={'Flag1': 1, 'Flag2': 1, 'Flag3': 1}
        )
        splitter = SetSplitter(max_interrogatories_per_set=1)

        result = splitter.split_into_sets(dataset)

        # Each flag in its own set
        assert result['metadata']['total_sets'] == 3
        for set_data in result['sets']:
            assert set_data['total_interrogatories'] == 1


class TestCustomMaxLimits:
    """Test custom max interrogatories limits."""

    def test_max_50_interrogatories(self):
        """Test with max 50 interrogatories per set."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={'Flag1': True, 'Flag2': True, 'Flag3': True},
            counts_dict={'Flag1': 40, 'Flag2': 40, 'Flag3': 40}
        )
        splitter = SetSplitter(max_interrogatories_per_set=50)

        result = splitter.split_into_sets(dataset)

        # Each set should have <= 50
        for set_data in result['sets']:
            assert set_data['total_interrogatories'] <= 50

    def test_max_200_interrogatories(self):
        """Test with max 200 interrogatories per set."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={'Flag1': True, 'Flag2': True},
            counts_dict={'Flag1': 150, 'Flag2': 100}
        )
        splitter = SetSplitter(max_interrogatories_per_set=200)

        result = splitter.split_into_sets(dataset)

        # Should fit in 2 sets
        assert result['metadata']['total_sets'] == 2

    def test_max_10_interrogatories(self):
        """Test with very small max limit."""
        dataset = create_dataset_with_custom_flags(
            flags_dict={'Flag1': True, 'Flag2': True},
            counts_dict={'Flag1': 8, 'Flag2': 8}
        )
        splitter = SetSplitter(max_interrogatories_per_set=10)

        result = splitter.split_into_sets(dataset)

        # Should create 2 sets
        assert result['metadata']['total_sets'] == 2


class TestPipelineIntegration:
    """Test SplittingPipeline integration."""

    def test_split_profile_datasets(self):
        """Test splitting all three profile datasets."""
        pipeline = SplittingPipeline(max_interrogatories_per_set=120)
        profiles = create_profile_datasets()

        result = pipeline.split_profile_datasets(profiles)

        # Should have all three profiles
        assert 'srogs' in result
        assert 'pods' in result
        assert 'admissions' in result

        # Each should have sets
        for profile_name, split_data in result.items():
            assert 'sets' in split_data
            assert 'metadata' in split_data
            assert len(split_data['sets']) > 0

            # Each set should have filename
            for set_data in split_data['sets']:
                assert 'filename' in set_data
                assert len(set_data['filename']) > 0

    def test_split_all_datasets(self):
        """Test splitting multiple datasets."""
        pipeline = SplittingPipeline(max_interrogatories_per_set=120)
        collection = create_profiled_collection()

        result = pipeline.split_all_datasets(collection)

        # Should have 2 datasets * 3 profiles = 6 split datasets
        assert len(result) == 6

        # Each should have required fields
        for split_dataset in result:
            assert 'doc_type' in split_dataset
            assert 'sets' in split_dataset
            assert 'metadata' in split_dataset

    def test_pipeline_preserves_metadata(self):
        """Test pipeline preserves all metadata."""
        pipeline = SplittingPipeline()
        profiles = create_profile_datasets()

        result = pipeline.split_profile_datasets(profiles)

        # Check SROGS metadata preserved
        srogs = result['srogs']
        assert srogs['doc_type'] == 'SROGs'
        assert 'plaintiff' in srogs
        assert 'defendant' in srogs
        assert 'case_metadata' in srogs

    def test_pipeline_generates_filenames(self):
        """Test pipeline generates filenames for all sets."""
        pipeline = SplittingPipeline()
        profiles = create_profile_datasets()

        result = pipeline.split_profile_datasets(profiles)

        # Check all sets have filenames
        for profile_name, split_data in result.items():
            for set_data in split_data['sets']:
                assert 'filename' in set_data
                # Filename should contain plaintiff and defendant
                assert 'John Doe' in set_data['filename']
                assert 'ABC Property Management' in set_data['filename']
                # Should contain set number
                assert 'Set' in set_data['filename']

    def test_summary_statistics(self):
        """Test pipeline summary statistics."""
        pipeline = SplittingPipeline()
        collection = create_profiled_collection()
        split_datasets = pipeline.split_all_datasets(collection)

        stats = pipeline.get_summary_statistics(split_datasets)

        # Should have expected statistics
        assert 'total_datasets' in stats
        assert 'total_sets' in stats
        assert 'total_interrogatories' in stats
        assert 'by_doc_type' in stats

        # Should have 6 datasets (2 cases * 3 doc types)
        assert stats['total_datasets'] == 6

        # Should have breakdown by doc type
        assert 'SROGs' in stats['by_doc_type']
        assert 'PODs' in stats['by_doc_type']
        assert 'Admissions' in stats['by_doc_type']


class TestDataIntegrity:
    """Test data integrity across splitting."""

    def test_no_flags_lost(self):
        """Test no flags are lost during splitting."""
        splitter = SetSplitter()
        dataset = create_dataset_with_custom_flags(
            flags_dict={
                'Flag1': True,
                'Flag2': True,
                'Flag3': False,
                'Flag4': True,
                'Flag5': False
            },
            counts_dict={
                'Flag1': 30,
                'Flag2': 40,
                'Flag3': 50,
                'Flag4': 60,
                'Flag5': 70
            }
        )

        result = splitter.split_into_sets(dataset)

        # Collect all flags from output
        output_flags = set()
        for set_data in result['sets']:
            output_flags.update(set_data['flags'].keys())

        # Get all true flags from input
        input_true_flags = {k for k, v in dataset['flags'].items() if v is True}

        # Should match exactly
        assert output_flags == input_true_flags

    def test_interrogatory_count_preserved(self):
        """Test total interrogatory count is preserved."""
        splitter = SetSplitter()
        dataset = create_dataset_with_custom_flags(
            flags_dict={f'Flag{i}': True for i in range(20)},
            counts_dict={f'Flag{i}': i * 5 for i in range(20)}
        )

        result = splitter.split_into_sets(dataset)

        # Calculate expected total
        expected_total = sum(i * 5 for i in range(20))

        assert result['metadata']['total_interrogatories'] == expected_total

    def test_flag_values_all_true(self):
        """Test all output flag values are True."""
        splitter = SetSplitter()
        dataset = create_dataset_with_custom_flags(
            flags_dict={'Flag1': True, 'Flag2': True, 'Flag3': True},
            counts_dict={'Flag1': 30, 'Flag2': 40, 'Flag3': 50}
        )

        result = splitter.split_into_sets(dataset)

        # All flags in output should be True
        for set_data in result['sets']:
            for flag_name, flag_value in set_data['flags'].items():
                assert flag_value is True

    def test_set_metadata_consistency(self):
        """Test set metadata is consistent."""
        splitter = SetSplitter()
        dataset = create_dataset_with_custom_flags(
            flags_dict={f'Flag{i}': True for i in range(10)},
            counts_dict={f'Flag{i}': 20 for i in range(10)}
        )

        result = splitter.split_into_sets(dataset)

        # Verify metadata consistency
        total_from_sets = sum(s['total_interrogatories'] for s in result['sets'])
        assert total_from_sets == result['metadata']['total_interrogatories']

        assert len(result['sets']) == result['metadata']['total_sets']
