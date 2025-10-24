"""
Splitting Pipeline Module

Orchestrates the set splitting process for all profile datasets,
generating filenames and managing the complete splitting workflow.
"""

from typing import Dict, List, Any
from .set_splitter import SetSplitter
from .filename_generator import generate_filename


class SplittingPipeline:
    """
    Orchestrates set splitting for all profile datasets.

    This pipeline:
    1. Accepts profiled datasets from Phase 4
    2. Splits each dataset into sets with max interrogatories
    3. Generates filenames for each set
    4. Returns structured output ready for document generation

    The pipeline handles:
    - Multiple document types (SROGs, PODs, Admissions)
    - Multiple datasets (different plaintiffs/defendants)
    - Multiple sets per dataset (when > 120 interrogatories)

    Attributes:
        splitter: SetSplitter instance for performing splits
        max_interrogatories_per_set: Maximum interrogatories per set
    """

    def __init__(self, max_interrogatories_per_set: int = 120):
        """
        Initialize the SplittingPipeline.

        Args:
            max_interrogatories_per_set: Maximum interrogatories per set (default: 120)
        """
        self.splitter = SetSplitter(max_interrogatories_per_set)
        self.max_interrogatories_per_set = max_interrogatories_per_set

    def split_profile_datasets(self, profile_datasets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Split all three profile datasets (SROGs, PODs, Admissions) for a single case.

        This method processes the three document types for one plaintiff-defendant pair,
        splitting each into sets and generating filenames.

        Args:
            profile_datasets: Output from ProfilePipeline.apply_profiles()
                Expected structure:
                {
                    'srogs': {
                        'dataset_id': '...',
                        'doc_type': 'SROGs',
                        'flags': {...},
                        'interrogatory_counts': {...},
                        'first_set_only_flags': [...],
                        'plaintiff': {...},
                        'defendant': {...},
                        'case_metadata': {...},
                        'template': '...',
                        'filename_suffix': '...'
                    },
                    'pods': {...},
                    'admissions': {...}
                }

        Returns:
            Dictionary with split sets for each profile:
            {
                'srogs': {
                    'doc_type': 'SROGs',
                    'dataset_id': '...',
                    'plaintiff': {...},
                    'defendant': {...},
                    'case_metadata': {...},
                    'template': '...',
                    'filename_suffix': '...',
                    'sets': [
                        {
                            'set_number': 1,
                            'interrogatory_start': 1,
                            'interrogatory_end': 120,
                            'total_interrogatories': 120,
                            'is_first_set': True,
                            'flags': {...},
                            'filename': 'John Doe vs ABC Corp - SROGs Set 1 of 2'
                        },
                        ...
                    ],
                    'metadata': {
                        'total_sets': 2,
                        'total_interrogatories': 235,
                        'max_per_set': 120
                    }
                },
                'pods': {...},
                'admissions': {...}
            }

        Examples:
            >>> pipeline = SplittingPipeline()
            >>> profiles = {
            ...     'srogs': {...},  # From Phase 4
            ...     'pods': {...},
            ...     'admissions': {...}
            ... }
            >>> result = pipeline.split_profile_datasets(profiles)
            >>> result['srogs']['metadata']['total_sets']
            2
        """
        result = {}

        # Process each profile (srogs, pods, admissions)
        for profile_name, dataset in profile_datasets.items():
            # Split the dataset into sets
            # SetSplitter now generates filenames internally (as OutputName field)
            split_result = self.splitter.split_into_sets(dataset)
            result[profile_name] = split_result

        return result

    def split_all_datasets(self, profiled_collection: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split all datasets in collection across all profiles.

        This method handles multiple plaintiff-defendant pairs, each with
        three document types (SROGs, PODs, Admissions), splitting all into sets.

        Args:
            profiled_collection: Collection from Phase 4
                Expected structure:
                {
                    'datasets': [
                        {
                            'srogs': {...},
                            'pods': {...},
                            'admissions': {...}
                        },
                        {
                            'srogs': {...},
                            'pods': {...},
                            'admissions': {...}
                        },
                        ...
                    ]
                }

        Returns:
            Flat list of all split datasets (one entry per document type per case)
            [
                {
                    'doc_type': 'SROGs',
                    'dataset_id': '...',
                    'sets': [...],
                    'metadata': {...},
                    ...
                },
                {
                    'doc_type': 'PODs',
                    'dataset_id': '...',
                    'sets': [...],
                    'metadata': {...},
                    ...
                },
                ...
            ]

        Examples:
            >>> pipeline = SplittingPipeline()
            >>> collection = {
            ...     'datasets': [
            ...         {'srogs': {...}, 'pods': {...}, 'admissions': {...}},
            ...         {'srogs': {...}, 'pods': {...}, 'admissions': {...}}
            ...     ]
            ... }
            >>> result = pipeline.split_all_datasets(collection)
            >>> len(result)  # 2 cases * 3 doc types = 6 datasets
            6
        """
        all_sets = []

        # Process each dataset (plaintiff-defendant pair)
        for dataset_profiles in profiled_collection['datasets']:
            # Split the three profiles for this dataset
            split_profiles = self.split_profile_datasets(dataset_profiles)

            # Add each split profile to the flat list
            for profile_name, split_data in split_profiles.items():
                all_sets.append(split_data)

        return all_sets

    def get_summary_statistics(self, split_datasets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate summary statistics for split datasets.

        Provides useful metrics about the splitting process:
        - Total number of datasets processed
        - Total number of sets created
        - Total interrogatories across all sets
        - Average interrogatories per set
        - Distribution by document type

        Args:
            split_datasets: List of split datasets from split_all_datasets()

        Returns:
            Dictionary with summary statistics

        Examples:
            >>> pipeline = SplittingPipeline()
            >>> split_data = pipeline.split_all_datasets(collection)
            >>> stats = pipeline.get_summary_statistics(split_data)
            >>> stats['total_datasets']
            6
            >>> stats['total_sets']
            12
        """
        total_datasets = len(split_datasets)
        total_sets = sum(d['metadata']['total_sets'] for d in split_datasets)
        total_interrogatories = sum(d['metadata']['total_interrogatories'] for d in split_datasets)

        # Calculate by document type
        by_doc_type = {}
        for dataset in split_datasets:
            doc_type = dataset['doc_type']
            if doc_type not in by_doc_type:
                by_doc_type[doc_type] = {
                    'datasets': 0,
                    'sets': 0,
                    'interrogatories': 0
                }
            by_doc_type[doc_type]['datasets'] += 1
            by_doc_type[doc_type]['sets'] += dataset['metadata']['total_sets']
            by_doc_type[doc_type]['interrogatories'] += dataset['metadata']['total_interrogatories']

        return {
            'total_datasets': total_datasets,
            'total_sets': total_sets,
            'total_interrogatories': total_interrogatories,
            'average_interrogatories_per_set': total_interrogatories / total_sets if total_sets > 0 else 0,
            'max_per_set': self.max_interrogatories_per_set,
            'by_doc_type': by_doc_type
        }
