"""
Geography Flag Processor for Phase 3: Flag Processors

This processor converts geography discovery data into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class GeographyProcessor(BaseFlagProcessor):
    """
    Processor for geography-related discovery flags.
    
    Converts geography data into individual flags like {"HasLosAngeles": True, "HasSanFrancisco": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for geography discovery data."""
        return "geography"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map geography values to flag names.
        
        Returns:
            Dictionary mapping geography values to flag names
        """
        return {
            "los angeles": "HasLosAngeles"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """No aggregate flag for geography."""
        return None

    def process(self, dataset: Dict[str, any]) -> Dict[str, bool]:
        """
        Process geography data from the full dataset.
        
        Args:
            dataset: Full dataset object (not just discovery_data)
            
        Returns:
            Dictionary of flags
        """
        flags = {}
        
        # Get city from case_metadata (where the pipeline stores it)
        case_metadata = dataset.get("case_metadata", {})
        city = case_metadata.get("city", "")
        
        # Process individual geography flags (check for "Los Angeles" with capital letters)
        flags["HasLosAngeles"] = "Los Angeles" in city

        return flags
