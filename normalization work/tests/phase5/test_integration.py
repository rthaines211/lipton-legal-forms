"""
Integration Tests for Phase 5

End-to-end tests demonstrating the complete Phase 5 workflow.
"""

import pytest
from src.phase5 import SetSplitter, SplittingPipeline, generate_filename
from tests.fixtures.phase5_samples import (
    create_profiled_dataset,
    create_profile_datasets,
    create_profiled_collection,
    create_large_dataset
)


class TestEndToEndWorkflow:
    """Test complete Phase 5 workflow."""

    def test_single_dataset_workflow(self):
        """Test complete workflow for single dataset."""
        # Create profiled dataset (from Phase 4)
        profiled_dataset = create_profiled_dataset(
            dataset_id='integration-test-001-srogs',
            doc_type='SROGs',
            plaintiff={'full_name': 'Alice Johnson'},
            defendant={'full_name': 'Acme Properties LLC'},
            filename_suffix='Discovery Propounded SROGs'
        )

        # Step 1: Split into sets
        splitter = SetSplitter(max_interrogatories_per_set=120)
        split_result = splitter.split_into_sets(profiled_dataset)

        # Verify split successful
        assert 'sets' in split_result
        assert 'metadata' in split_result
        assert split_result['metadata']['total_sets'] > 0

        # Step 2: Generate filenames
        for set_data in split_result['sets']:
            filename = generate_filename(
                plaintiff_name=profiled_dataset['plaintiff']['full_name'],
                defendant_name=profiled_dataset['defendant']['full_name'],
                doc_type=profiled_dataset['doc_type'],
                set_number=set_data['set_number'],
                total_sets=split_result['metadata']['total_sets'],
                filename_suffix=profiled_dataset['filename_suffix']
            )

            # Verify filename format
            assert 'Alice Johnson' in filename
            assert 'Acme Properties LLC' in filename
            assert 'Discovery Propounded SROGs' in filename
            assert 'Set' in filename

        # Step 3: Verify data integrity
        # All true flags should be included
        all_flags_in_sets = set()
        for set_data in split_result['sets']:
            all_flags_in_sets.update(set_data['flags'].keys())

        true_flags = {k for k, v in profiled_dataset['flags'].items() if v}
        assert all_flags_in_sets == true_flags

    def test_three_profiles_workflow(self):
        """Test workflow for all three document types."""
        # Create three profiled datasets
        profiles = create_profile_datasets()

        # Process all three through pipeline
        pipeline = SplittingPipeline(max_interrogatories_per_set=120)
        result = pipeline.split_profile_datasets(profiles)

        # Verify all three profiles processed
        assert 'srogs' in result
        assert 'pods' in result
        assert 'admissions' in result

        # Verify each has sets with filenames
        for profile_name, split_data in result.items():
            assert 'sets' in split_data
            assert len(split_data['sets']) > 0

            for set_data in split_data['sets']:
                assert 'filename' in set_data
                assert 'set_number' in set_data
                assert 'interrogatory_start' in set_data
                assert 'interrogatory_end' in set_data
                assert 'flags' in set_data

    def test_multiple_cases_workflow(self):
        """Test workflow for multiple plaintiff-defendant pairs."""
        # Create collection with multiple cases
        collection = create_profiled_collection()

        # Process all datasets
        pipeline = SplittingPipeline(max_interrogatories_per_set=120)
        all_split_datasets = pipeline.split_all_datasets(collection)

        # Verify results
        # Should have 2 cases * 3 doc types = 6 datasets
        assert len(all_split_datasets) == 6

        # Each should have proper structure
        for split_dataset in all_split_datasets:
            assert 'doc_type' in split_dataset
            assert 'sets' in split_dataset
            assert 'metadata' in split_dataset

            # Each set should have filename
            for set_data in split_dataset['sets']:
                assert 'filename' in set_data
                assert len(set_data['filename']) > 0

        # Get summary statistics
        stats = pipeline.get_summary_statistics(all_split_datasets)

        assert stats['total_datasets'] == 6
        assert stats['total_sets'] > 0
        assert stats['total_interrogatories'] > 0
        assert 'by_doc_type' in stats


class TestRealWorldScenarios:
    """Test realistic real-world scenarios."""

    def test_large_case_many_sets(self):
        """Test case requiring many sets."""
        # Create large dataset
        large_dataset = create_large_dataset()

        # Split with standard limit
        splitter = SetSplitter(max_interrogatories_per_set=120)
        result = splitter.split_into_sets(large_dataset)

        # Should create multiple sets
        assert result['metadata']['total_sets'] >= 3

        # Verify each set respects limit
        for set_data in result['sets']:
            # Allow first set to exceed due to first-set-only flags
            if set_data['set_number'] > 1 or set_data['is_first_set'] is False:
                assert set_data['total_interrogatories'] <= 120

        # Verify continuous numbering
        prev_end = 0
        for set_data in result['sets']:
            assert set_data['interrogatory_start'] == prev_end + 1
            prev_end = set_data['interrogatory_end']

    def test_special_characters_in_names(self):
        """Test handling of special characters in party names."""
        # Create dataset with special characters
        dataset = create_profiled_dataset(
            plaintiff={'full_name': "María José O'Brien"},
            defendant={'full_name': "Smith & Associates LLC"}
        )

        # Split and generate filename
        splitter = SetSplitter()
        result = splitter.split_into_sets(dataset)

        # Generate filename
        filename = generate_filename(
            plaintiff_name=dataset['plaintiff']['full_name'],
            defendant_name=dataset['defendant']['full_name'],
            doc_type=dataset['doc_type'],
            set_number=1,
            total_sets=result['metadata']['total_sets'],
            filename_suffix=dataset['filename_suffix']
        )

        # Verify special characters preserved
        assert "María José O'Brien" in filename
        assert "Smith & Associates LLC" in filename

    def test_minimal_case_single_set(self):
        """Test minimal case with only a few interrogatories."""
        # Create small dataset using custom flags to ensure clean state
        from tests.fixtures.phase5_samples import create_dataset_with_custom_flags

        dataset = create_dataset_with_custom_flags(
            flags_dict={
                'SROGsGeneral': True,
                'HasMold': True,
                'IsOwner': False,
                'IsManager': False
            },
            counts_dict={
                'SROGsGeneral': 10,
                'HasMold': 24,
                'IsOwner': 15,
                'IsManager': 12
            }
        )

        # Split
        splitter = SetSplitter(max_interrogatories_per_set=120)
        result = splitter.split_into_sets(dataset)

        # Should have single set
        assert result['metadata']['total_sets'] == 1

        # Should have 34 interrogatories (10 + 24)
        # SROGsGeneral (10) is first-set-only but not in first_set_only_flags after custom creation
        # So we count: SROGsGeneral (10) + HasMold (24) = 34
        assert result['metadata']['total_interrogatories'] == 34

        # Verify filename
        set_1 = result['sets'][0]
        filename = generate_filename(
            plaintiff_name=dataset['plaintiff']['full_name'],
            defendant_name=dataset['defendant']['full_name'],
            doc_type=dataset['doc_type'],
            set_number=set_1['set_number'],
            total_sets=result['metadata']['total_sets'],
            filename_suffix=dataset['filename_suffix']
        )

        assert 'Set 1 of 1' in filename


class TestDataIntegrityThroughPipeline:
    """Test data integrity through complete pipeline."""

    def test_no_data_loss_through_pipeline(self):
        """Verify no data is lost through the pipeline."""
        # Create profiled datasets
        profiles = create_profile_datasets()

        # Process through pipeline
        pipeline = SplittingPipeline()
        result = pipeline.split_profile_datasets(profiles)

        # For each profile, verify all data preserved
        for profile_name in ['srogs', 'pods', 'admissions']:
            original = profiles[profile_name]
            split = result[profile_name]

            # Verify metadata preserved
            assert split['doc_type'] == original['doc_type']
            assert split['dataset_id'] == original['dataset_id']
            assert split['plaintiff'] == original['plaintiff']
            assert split['defendant'] == original['defendant']

            # Verify all true flags included
            original_true_flags = {k for k, v in original['flags'].items() if v}
            split_flags = set()
            for set_data in split['sets']:
                split_flags.update(set_data['flags'].keys())

            assert split_flags == original_true_flags

    def test_interrogatory_count_preservation(self):
        """Verify total interrogatory count preserved."""
        # Create dataset
        dataset = create_large_dataset()

        # Calculate expected total
        expected_total = sum(
            dataset['interrogatory_counts'][flag]
            for flag, value in dataset['flags'].items()
            if value is True
        )

        # Split
        splitter = SetSplitter()
        result = splitter.split_into_sets(dataset)

        # Verify total preserved
        assert result['metadata']['total_interrogatories'] == expected_total

        # Verify sum of all sets equals total
        sum_of_sets = sum(s['total_interrogatories'] for s in result['sets'])
        assert sum_of_sets == expected_total


class TestStatisticsGeneration:
    """Test statistics generation functionality."""

    def test_summary_statistics_accuracy(self):
        """Test summary statistics are accurate."""
        # Create collection
        collection = create_profiled_collection()

        # Process
        pipeline = SplittingPipeline()
        split_datasets = pipeline.split_all_datasets(collection)

        # Get statistics
        stats = pipeline.get_summary_statistics(split_datasets)

        # Verify statistics
        assert stats['total_datasets'] == len(split_datasets)

        # Verify total sets
        manual_count = sum(d['metadata']['total_sets'] for d in split_datasets)
        assert stats['total_sets'] == manual_count

        # Verify total interrogatories
        manual_total = sum(d['metadata']['total_interrogatories'] for d in split_datasets)
        assert stats['total_interrogatories'] == manual_total

        # Verify average
        expected_avg = manual_total / manual_count if manual_count > 0 else 0
        assert abs(stats['average_interrogatories_per_set'] - expected_avg) < 0.01

    def test_by_doc_type_breakdown(self):
        """Test statistics broken down by document type."""
        # Create collection
        collection = create_profiled_collection()

        # Process
        pipeline = SplittingPipeline()
        split_datasets = pipeline.split_all_datasets(collection)

        # Get statistics
        stats = pipeline.get_summary_statistics(split_datasets)

        # Verify by_doc_type breakdown
        assert 'by_doc_type' in stats
        assert 'SROGs' in stats['by_doc_type']
        assert 'PODs' in stats['by_doc_type']
        assert 'Admissions' in stats['by_doc_type']

        # Each should have correct counts
        for doc_type, type_stats in stats['by_doc_type'].items():
            assert 'datasets' in type_stats
            assert 'sets' in type_stats
            assert 'interrogatories' in type_stats


def test_phase_5_complete_example():
    """
    Complete example demonstrating Phase 5 usage.

    This test serves as documentation for how to use Phase 5.
    """
    # Setup: Create profiled dataset (output from Phase 4)
    profiled_dataset = create_profiled_dataset(
        dataset_id='example-plaintiff-1-defendant-1-srogs',
        doc_type='SROGs',
        plaintiff={
            'full_name': 'Example Plaintiff',
            'first_name': 'Example',
            'last_name': 'Plaintiff'
        },
        defendant={
            'full_name': 'Example Defendant LLC',
            'entity_type': 'LLC',
            'role': 'Owner'
        },
        filename_suffix='Discovery Propounded SROGs'
    )

    # Step 1: Initialize splitter
    splitter = SetSplitter(max_interrogatories_per_set=120)

    # Step 2: Split into sets
    result = splitter.split_into_sets(profiled_dataset)

    # Step 3: Process results
    print(f"\n{'='*60}")
    print(f"Phase 5 Output Example")
    print(f"{'='*60}")
    print(f"Document Type: {result['doc_type']}")
    print(f"Total Sets: {result['metadata']['total_sets']}")
    print(f"Total Interrogatories: {result['metadata']['total_interrogatories']}")
    print(f"\nSets:")

    for set_data in result['sets']:
        # Generate filename for this set
        filename = generate_filename(
            plaintiff_name=profiled_dataset['plaintiff']['full_name'],
            defendant_name=profiled_dataset['defendant']['full_name'],
            doc_type=profiled_dataset['doc_type'],
            set_number=set_data['set_number'],
            total_sets=result['metadata']['total_sets'],
            filename_suffix=profiled_dataset['filename_suffix']
        )

        print(f"\n  Set {set_data['set_number']}:")
        print(f"    Interrogatories: {set_data['interrogatory_start']}-{set_data['interrogatory_end']}")
        print(f"    Total: {set_data['total_interrogatories']}")
        print(f"    Is First Set: {set_data['is_first_set']}")
        print(f"    Flags: {', '.join(set_data['flags'].keys())}")
        print(f"    Filename: {filename}")

    print(f"\n{'='*60}\n")

    # Verify results
    assert result['metadata']['total_sets'] > 0
    assert result['metadata']['total_interrogatories'] > 0
    assert len(result['sets']) == result['metadata']['total_sets']
