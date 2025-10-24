"""
Nuisance Flag Processor for Phase 3: Flag Processors

This processor converts nuisance discovery arrays into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class NuisanceProcessor(BaseFlagProcessor):
    """
    Processor for nuisance-related discovery flags.
    
    Converts nuisance array values like ["Drugs", "Smoking"] into
    individual flags like {"HasDrugs": True, "HasSmoking": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for nuisance discovery data."""
        return "nuisance"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map nuisance array values to flag names.
        
        Returns:
            Dictionary mapping nuisance values to flag names
        """
        return {
            "Drugs": "HasDrugs",
            "Smoking": "HasSmoking",
            "Noisy neighbors": "HasNoisyNeighbors",
            "Gangs": "HasGangs"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any nuisance issues."""
        return "HasNuisance"
