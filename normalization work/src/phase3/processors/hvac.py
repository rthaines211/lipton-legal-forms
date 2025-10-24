"""
HVAC Flag Processor for Phase 3: Flag Processors

This processor converts HVAC discovery arrays into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class HVACProcessor(BaseFlagProcessor):
    """
    Processor for HVAC-related discovery flags.
    
    Converts HVAC array values like ["Air Conditioner", "Heater"] into
    individual flags like {"HasAirConditioner": True, "HasHeater": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for HVAC discovery data."""
        return "hvac"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map HVAC array values to flag names.
        
        Returns:
            Dictionary mapping HVAC values to flag names
        """
        return {
            "Air Conditioner": "HasAC",
            "Heater": "HasHeater",
            "Ventilation": "HasVentilation",
            "HVAC": "HasHVAC"  # Generic HVAC flag
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any HVAC issues."""
        return "HasHVAC"

    def process(self, discovery_data: Dict[str, list]) -> Dict[str, bool]:
        """
        Process HVAC discovery data with custom aggregate logic.
        
        Args:
            discovery_data: Discovery object from dataset
            
        Returns:
            Dictionary of flags including custom aggregates
        """
        # Get base flags from parent class
        flags = super().process(discovery_data)

        # Add general HVAC flag (lowercase 'v' for compatibility with manual conversion)
        hvac_flags = [
            flags.get("HasAC", False),
            flags.get("HasHeater", False),
            flags.get("HasVentilation", False),
            flags.get("HasHVAC", False)
        ]
        flags["HasHvac"] = any(hvac_flags)

        return flags
