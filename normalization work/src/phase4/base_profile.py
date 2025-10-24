"""
Base Document Profile

Abstract base class for document profiles that defines the interface
for creating document type-specific transformations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import copy


class BaseDocumentProfile(ABC):
    """Base class for document profiles."""

    @property
    @abstractmethod
    def doc_type(self) -> str:
        """Document type name (SROGs, PODs, Admissions)"""
        pass

    @property
    @abstractmethod
    def template_name(self) -> str:
        """Template filename"""
        pass

    @property
    @abstractmethod
    def filename_suffix(self) -> str:
        """Suffix for generated filename"""
        pass

    @property
    @abstractmethod
    def first_set_only_flags(self) -> list[str]:
        """Flags that only appear in Set 1"""
        pass

    @property
    @abstractmethod
    def interrogatory_counts(self) -> Dict[str, int]:
        """
        Map flag names to interrogatory counts.

        Example:
            {
                "HasMold": 24,
                "HasRatsMice": 18,
                ...
            }
        """
        pass

    @abstractmethod
    def add_profile_specific_flags(self, dataset: dict) -> dict:
        """
        Add profile-specific flags to dataset.

        Args:
            dataset: Dataset with Phase 3 flags

        Returns:
            Dataset with additional profile flags
        """
        pass

    def apply_profile(self, dataset: dict) -> dict:
        """
        Apply profile transformation to dataset.

        Args:
            dataset: Enriched dataset from Phase 3

        Returns:
            Profile-specific dataset
        """
        # Deep copy to avoid mutation
        profiled_dataset = copy.deepcopy(dataset)
        
        # Ensure flags dict exists
        if 'flags' not in profiled_dataset:
            profiled_dataset['flags'] = {}

        # Add document type metadata
        profiled_dataset['doc_type'] = self.doc_type
        profiled_dataset['template'] = self.template_name
        profiled_dataset['filename_suffix'] = self.filename_suffix
        profiled_dataset['dataset_id'] = f"{dataset['dataset_id']}-{self.doc_type.lower()}"

        # Add profile-specific flags
        profiled_dataset = self.add_profile_specific_flags(profiled_dataset)

        # Add interrogatory counts
        profiled_dataset['interrogatory_counts'] = self.interrogatory_counts

        # Filter flags to only include those with interrogatory counts > 0
        # This removes flags that:
        # 1. Don't exist in this profile's interrogatory_counts
        # 2. Have 0 interrogatories (aggregate flags that were commented out)
        filtered_flags = {}
        for flag, is_true in profiled_dataset['flags'].items():
            # Only keep flags that have interrogatory counts > 0
            if flag in self.interrogatory_counts and self.interrogatory_counts[flag] > 0:
                filtered_flags[flag] = is_true

        profiled_dataset['flags'] = filtered_flags

        # Mark first-set-only flags
        profiled_dataset['first_set_only_flags'] = self.first_set_only_flags

        return profiled_dataset
