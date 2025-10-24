"""
Profile Pipeline

Applies all three document profiles (SROGs, PODs, Admissions) to datasets
from Phase 3 to create profile-specific datasets.
"""

from typing import Dict, List, Any
from .profiles import SROGsProfile, PODsProfile, AdmissionsProfile


class ProfilePipeline:
    """Applies all three document profiles to datasets."""

    def __init__(self):
        """Initialize the profile pipeline with all three profiles."""
        self.profiles = [
            SROGsProfile(),
            PODsProfile(),
            AdmissionsProfile()
        ]

    def apply_profiles(self, enriched_dataset: dict) -> dict:
        """
        Apply all profiles to a single dataset.

        Args:
            enriched_dataset: Dataset from Phase 3 with flags

        Returns:
            Dictionary with three profile datasets
        """
        return {
            'srogs': self.profiles[0].apply_profile(enriched_dataset),
            'pods': self.profiles[1].apply_profile(enriched_dataset),
            'admissions': self.profiles[2].apply_profile(enriched_dataset)
        }

    def apply_profiles_to_collection(self, dataset_collection: dict) -> dict:
        """
        Apply profiles to all datasets in collection.

        Args:
            dataset_collection: Collection from Phase 3

        Returns:
            Collection with profile datasets
        """
        profiled_datasets = []

        for dataset in dataset_collection['datasets']:
            profiles = self.apply_profiles(dataset)
            profiled_datasets.append(profiles)

        return {
            'datasets': profiled_datasets,
            'metadata': {
                **dataset_collection['metadata'],
                'profiles_applied': 3,
                'total_profile_datasets': len(profiled_datasets) * 3
            }
        }

    def apply_single_profile(self, enriched_dataset: dict, profile_type: str) -> dict:
        """
        Apply a single profile to a dataset.

        Args:
            enriched_dataset: Dataset from Phase 3 with flags
            profile_type: Type of profile ('srogs', 'pods', 'admissions')

        Returns:
            Single profile dataset

        Raises:
            ValueError: If profile_type is not recognized
        """
        profile_map = {
            'srogs': self.profiles[0],
            'pods': self.profiles[1],
            'admissions': self.profiles[2]
        }

        if profile_type not in profile_map:
            raise ValueError(f"Unknown profile type: {profile_type}. "
                           f"Must be one of: {list(profile_map.keys())}")

        return profile_map[profile_type].apply_profile(enriched_dataset)

    def get_profile_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all profiles.

        Returns:
            Dictionary with profile information
        """
        return {
            'srogs': {
                'doc_type': self.profiles[0].doc_type,
                'template': self.profiles[0].template_name,
                'filename_suffix': self.profiles[0].filename_suffix,
                'first_set_only_flags': self.profiles[0].first_set_only_flags,
                'total_interrogatory_mappings': len(self.profiles[0].interrogatory_counts)
            },
            'pods': {
                'doc_type': self.profiles[1].doc_type,
                'template': self.profiles[1].template_name,
                'filename_suffix': self.profiles[1].filename_suffix,
                'first_set_only_flags': self.profiles[1].first_set_only_flags,
                'total_interrogatory_mappings': len(self.profiles[1].interrogatory_counts)
            },
            'admissions': {
                'doc_type': self.profiles[2].doc_type,
                'template': self.profiles[2].template_name,
                'filename_suffix': self.profiles[2].filename_suffix,
                'first_set_only_flags': self.profiles[2].first_set_only_flags,
                'total_interrogatory_mappings': len(self.profiles[2].interrogatory_counts)
            }
        }

    def validate_profile_datasets(self, profiled_datasets: dict) -> Dict[str, List[str]]:
        """
        Validate that profile datasets have required fields.

        Args:
            profiled_datasets: Dictionary with three profile datasets

        Returns:
            Dictionary with validation results for each profile
        """
        required_fields = [
            'dataset_id', 'doc_type', 'template', 'filename_suffix',
            'flags', 'interrogatory_counts', 'first_set_only_flags'
        ]

        validation_results = {}

        for profile_name, dataset in profiled_datasets.items():
            missing_fields = []
            for field in required_fields:
                if field not in dataset:
                    missing_fields.append(field)

            validation_results[profile_name] = missing_fields

        return validation_results
