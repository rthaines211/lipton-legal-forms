"""
Structure Flag Processor for Phase 3: Flag Processors

This processor converts structure discovery arrays into individual boolean flags
with complex aggregate logic.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class StructureProcessor(BaseFlagProcessor):
    """
    Processor for structure-related discovery flags.
    
    Converts structure array values like ["Hole in ceiling", "Water stains on wall"] into
    individual flags with additional aggregate flags for holes and water stains.
    """

    @property
    def category_name(self) -> str:
        """Category name for structure discovery data."""
        return "structure"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map structure array values to flag names.
        
        Returns:
            Dictionary mapping structure values to flag names
        """
        return {
            "Hole in ceiling": "HasHoleInCeiling",
            "Bumps in ceiling": "HasBumpsInCeiling",
            "Water stains on ceiling": "HasWaterStainsOnCeiling",
            "Water stains on wall": "HasWaterStainsOnWall",
            "Hole in wall": "HasHoleInWall",
            "Paint": "HasPaint",
            "Exterior deck/porch": "HasExteriorDeckPorch",
            "Waterproof toilet": "HasWaterproofToilet",
            "Waterproof tub": "HasWaterproofTub",
            "Staircase": "HasStaircase",
            "Basement flood": "HasBasementFlood",
            "Leaks in garage": "HasLeaksInGarage",
            "Ineffective Weatherproofing of any windows doors": "HasIneffectiveWeatherproofingOfAnyWindowsDoors",
            "Ineffective waterproofing of the tubs or toilet": "HasIneffectiveWaterproofingOfTheTubsToilet",
            "Soft Spots due to Leaks": "HasSoftSpotsDueToLeaks"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any structure issues."""
        return "HasStructure"

    def process(self, discovery_data: Dict[str, list]) -> Dict[str, bool]:
        """
        Process structure discovery data with custom aggregate logic.
        
        Args:
            discovery_data: Discovery object from dataset
            
        Returns:
            Dictionary of flags including custom aggregates
        """
        # Get base flags from parent class
        flags = super().process(discovery_data)

        # Additional aggregates: HasHolesInCeilingWalls and HasWaterStainsOnCeilingWalls
        flags["HasHolesInCeilingWalls"] = (
            flags.get("HasHoleInCeiling", False) or 
            flags.get("HasHoleInWall", False)
        )
        
        flags["HasWaterStainsOnCeilingWalls"] = (
            flags.get("HasWaterStainsOnCeiling", False) or 
            flags.get("HasWaterStainsOnWall", False)
        )

        return flags
