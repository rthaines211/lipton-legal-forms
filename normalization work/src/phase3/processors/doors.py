"""
Doors Flag Processor for Phase 3: Flag Processors

This processor converts doors discovery arrays into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class DoorsProcessor(BaseFlagProcessor):
    """
    Processor for doors-related discovery flags.
    
    Converts doors array values like ["Broken", "Knobs"] into
    individual flags like {"HasBrokenDoors": True, "HasDoorKnobs": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for doors discovery data."""
        return "doors"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map doors array values to flag names.
        
        Returns:
            Dictionary mapping doors values to flag names
        """
        return {
            "Broken": "HasBrokenDoors",
            "Knobs": "HasDoorKnobs",
            "Locks": "HasDoorLocks",
            "Broken hinges": "HasBrokenHinges",
            "Sliding glass doors": "HasSlidingGlassDoors",
            "Ineffective waterproofing": "HasIneffectiveWaterproofing",
            "Water intrusion and/or insects": "HasWaterIntrusionInsects",
            "Do Not Close Properly": "HasDoorsDoNotCloseProperly"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any doors issues."""
        return "HasDoors"
