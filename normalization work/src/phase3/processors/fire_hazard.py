"""
Fire Hazard Flag Processor for Phase 3: Flag Processors

This processor converts fire hazard discovery arrays into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class FireHazardProcessor(BaseFlagProcessor):
    """
    Processor for fire hazard-related discovery flags.
    
    Converts fire hazard array values like ["Smoke Alarms", "Fire Extinguisher"] into
    individual flags like {"HasSmokeAlarms": True, "HasFireExtinguisher": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for fire hazard discovery data."""
        return "fire_hazard"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map fire hazard array values to flag names.
        
        Returns:
            Dictionary mapping fire hazard values to flag names
        """
        return {
            "Smoke Alarms": "HasSmokeAlarms",
            "Fire Extinguisher": "HasFireExtinguisher",
            "Non-compliant electricity": "HasNonCompliantElectricity",
            "Non-GFI outlets near water": "HasNonGfiElectricalOutlets",
            "Carbon monoxide detectors": "HasCarbonMonoxideDetectors"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any fire hazard issues."""
        return "HasFireHazardIssues"

    def process(self, discovery_data: Dict[str, list]) -> Dict[str, bool]:
        """
        Process fire hazard discovery data with custom aggregate logic.
        
        Args:
            discovery_data: Discovery object from dataset
            
        Returns:
            Dictionary of flags including custom aggregates
        """
        # Get base flags from parent class
        flags = super().process(discovery_data)

        # Add general fire hazard flag if any fire hazard issues exist
        fire_hazard_flags = [
            flags.get("HasSmokeAlarms", False),
            flags.get("HasFireExtinguisher", False),
            flags.get("HasNonCompliantElectricity", False),
            flags.get("HasNonGfiElectricalOutlets", False),
            flags.get("HasCarbonMonoxideDetectors", False)
        ]
        flags["HasFireHazard"] = any(fire_hazard_flags)

        return flags
