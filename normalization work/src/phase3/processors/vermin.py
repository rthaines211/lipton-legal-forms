"""
Vermin Flag Processor for Phase 3: Flag Processors

This processor converts vermin discovery arrays into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class VerminProcessor(BaseFlagProcessor):
    """
    Processor for vermin-related discovery flags.
    
    Converts vermin array values like ["Rats/Mice", "Bedbugs"] into
    individual flags like {"HasRatsMice": True, "HasBedbugs": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for vermin discovery data."""
        return "vermin"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map vermin array values to flag names.
        
        Returns:
            Dictionary mapping vermin values to flag names
        """
        return {
            "Rats/Mice": "HasRatsMice",
            "Bedbugs": "HasBedbugs",
            "Skunks": "HasSkunks",
            "Bats": "HasBats",
            "Raccoons": "HasRaccoons",
            "Pigeons": "HasPigeons",
            "Opossums": "HasOpossums"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any vermin presence."""
        return "HasVermin"

    def process(self, discovery_data: Dict[str, list]) -> Dict[str, bool]:
        """
        Process vermin discovery data with custom aggregate logic.
        
        Args:
            discovery_data: Discovery object from dataset
            
        Returns:
            Dictionary of flags including custom aggregates
        """
        # Get base flags from parent class
        flags = super().process(discovery_data)

        # Add alternative spelling for Raccoons
        if flags.get("HasRaccoons", False):
            flags["HasRacoons"] = True

        return flags
