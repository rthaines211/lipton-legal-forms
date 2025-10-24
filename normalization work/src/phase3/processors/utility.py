"""
Utility Flag Processor for Phase 3: Flag Processors

This processor converts utility discovery arrays into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class UtilityProcessor(BaseFlagProcessor):
    """
    Processor for utility-related discovery flags.
    
    Converts utility array values like ["Water shutoffs", "Gas leak"] into
    individual flags like {"HasWaterShutoffs": True, "HasGasLeaks": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for utility discovery data."""
        return "utility_interruptions"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map utility array values to flag names.
        
        Returns:
            Dictionary mapping utility values to flag names
        """
        return {
            "Water shutoffs": "HasWaterShutoffs",
            "Gas leak": "HasGasLeaks",
            "Electricity shutoffs": "HasElectricityShutoffs",
            "Heat Shutoff": "HasHeatShutoffs",
            "Gas Shutoff": "HasGasShutoffs"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """No aggregate flag for utility issues."""
        return None
