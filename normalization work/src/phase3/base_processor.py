"""
Base Flag Processor Interface for Phase 3: Flag Processors

This module provides the abstract base class for all flag processors.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseFlagProcessor(ABC):
    """
    Base class for all flag processors.
    
    Each processor converts discovery array values into individual boolean flags.
    For example: ["Rats/Mice", "Bedbugs"] → {"HasRatsMice": True, "HasBedbugs": True}
    """

    @property
    @abstractmethod
    def category_name(self) -> str:
        """
        Category name (e.g., 'vermin', 'insects', 'plumbing').
        
        This should match the key in the discovery_data dictionary.
        
        Returns:
            Category name string
        """
        pass

    @property
    @abstractmethod
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map array values to flag names.
        
        Maps each possible array value to its corresponding flag name.
        Case-insensitive matching is performed automatically.
        
        Example:
            {
                "Rats/Mice": "HasRatsMice",
                "Bedbugs": "HasBedbugs",
                "Skunks": "HasSkunks"
            }
        
        Returns:
            Dictionary mapping array values to flag names
        """
        pass

    @property
    def aggregate_flag_name(self) -> Optional[str]:
        """
        Optional aggregate flag (e.g., HasVermin, HasInsects).
        
        If provided, this flag will be True if any individual flags are True.
        Returns None if no aggregate flag is needed.
        
        Returns:
            Aggregate flag name or None
        """
        return None

    def process(self, discovery_data: Dict[str, List[str]]) -> Dict[str, bool]:
        """
        Process discovery data and return flag dictionary.
        
        Args:
            discovery_data: Discovery object from dataset
            
        Returns:
            Dictionary of flags {flag_name: bool}
            
        Example:
            >>> processor = VerminProcessor()
            >>> discovery = {"vermin": ["Rats/Mice", "Bedbugs"]}
            >>> flags = processor.process(discovery)
            >>> flags["HasRatsMice"]
            True
            >>> flags["HasBedbugs"]
            True
            >>> flags["HasVermin"]  # Aggregate
            True
        """
        flags = {}
        array_values = discovery_data.get(self.category_name, [])

        # Process individual flags
        for value, flag_name in self.flag_mappings.items():
            # Case-insensitive matching
            flags[flag_name] = any(
                v.lower() == value.lower() for v in array_values
            )

        # Process aggregate flag
        if self.aggregate_flag_name:
            # Aggregate is True if any individual flags are True
            individual_flags = [flags.get(flag_name, False) for flag_name in self.flag_mappings.values()]
            flags[self.aggregate_flag_name] = any(individual_flags)

        return flags

    def get_expected_flags(self) -> List[str]:
        """
        Get list of all expected flag names for this processor.
        
        Returns:
            List of all flag names (individual + aggregate)
        """
        flags = list(self.flag_mappings.values())
        if self.aggregate_flag_name:
            flags.append(self.aggregate_flag_name)
        return flags

    def validate_discovery_data(self, discovery_data: Dict[str, List[str]]) -> bool:
        """
        Validate that discovery data has the expected structure.
        
        Args:
            discovery_data: Discovery data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(discovery_data, dict):
            return False
        
        category_data = discovery_data.get(self.category_name)
        if category_data is None:
            return True  # Missing category is OK (empty array)
        
        return isinstance(category_data, list)

    def get_processor_info(self) -> Dict[str, any]:
        """
        Get information about this processor.
        
        Returns:
            Dictionary with processor metadata
        """
        return {
            "category_name": self.category_name,
            "individual_flags": len(self.flag_mappings),
            "aggregate_flag": self.aggregate_flag_name is not None,
            "total_flags": len(self.get_expected_flags()),
            "flag_names": self.get_expected_flags()
        }
