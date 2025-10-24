"""
Insect Flag Processor for Phase 3: Flag Processors

This processor converts insect discovery arrays into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class InsectProcessor(BaseFlagProcessor):
    """
    Processor for insect-related discovery flags.
    
    Converts insect array values like ["Ants", "Roaches"] into
    individual flags like {"HasAnts": True, "HasRoaches": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for insect discovery data."""
        return "insects"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map insect array values to flag names.
        
        Returns:
            Dictionary mapping insect values to flag names
        """
        return {
            "Ants": "HasAnts",
            "Roaches": "HasRoaches",
            "Flies": "HasFlies",
            "Bedbugs": "HasBedbugs",
            "Wasps": "HasWasps",
            "Hornets": "HasHornets",
            "Spiders": "HasSpiders",
            "Termites": "HasTermites",
            "Mosquitos": "HasMosquitos",
            "Bees": "HasBees"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any insect presence."""
        return "HasInsects"
