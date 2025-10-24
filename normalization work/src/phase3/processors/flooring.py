"""
Flooring Flag Processor for Phase 3: Flag Processors

This processor converts flooring discovery arrays into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class FlooringProcessor(BaseFlagProcessor):
    """
    Processor for flooring-related discovery flags.
    
    Converts flooring array values like ["Uneven", "Carpet"] into
    individual flags like {"HasUnevenFlooring": True, "HasCarpet": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for flooring discovery data."""
        return "flooring"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map flooring array values to flag names.
        
        Returns:
            Dictionary mapping flooring values to flag names
        """
        return {
            "Uneven": "HasUnevenFlooring",
            "Carpet": "HasCarpet",
            "Tiles": "HasTiles",
            "Nails sticking out": "HasNailsStickingOut"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any flooring issues."""
        return "HasFloors"
