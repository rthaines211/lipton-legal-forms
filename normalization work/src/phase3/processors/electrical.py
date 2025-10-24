"""
Electrical Flag Processor for Phase 3: Flag Processors

This processor converts electrical discovery arrays into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class ElectricalProcessor(BaseFlagProcessor):
    """
    Processor for electrical-related discovery flags.
    
    Converts electrical array values like ["Outlets", "Panel"] into
    individual flags like {"HasOutlets": True, "HasPanel": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for electrical discovery data."""
        return "electrical"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map electrical array values to flag names.
        
        Returns:
            Dictionary mapping electrical values to flag names
        """
        return {
            "Outlets": "HasOutlets",
            "Panel": "HasPanel",
            "Wall Switches": "HasWallSwitches",
            "Exterior Lighting": "HasExteriorLighting",
            "Interior Lighting": "HasInteriorLighting",
            "Light Fixtures": "HasLightFixtures",
            "Fans": "HasFans"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any electrical issues."""
        return "HasElectricalIssues"

    def process(self, discovery_data: Dict[str, list]) -> Dict[str, bool]:
        """
        Process electrical discovery data with custom aggregate logic.
        
        Args:
            discovery_data: Discovery object from dataset
            
        Returns:
            Dictionary of flags including custom aggregates
        """
        # Get base flags from parent class
        flags = super().process(discovery_data)

        # Add general electrical flag if any electrical issues exist
        electrical_flags = [
            flags.get("HasOutlets", False),
            flags.get("HasPanel", False),
            flags.get("HasWallSwitches", False),
            flags.get("HasExteriorLighting", False),
            flags.get("HasInteriorLighting", False),
            flags.get("HasLightFixtures", False),
            flags.get("HasFans", False)
        ]
        flags["HasElectrical"] = any(electrical_flags)

        return flags
