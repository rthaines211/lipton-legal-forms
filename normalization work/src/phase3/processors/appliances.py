"""
Appliances Flag Processor for Phase 3: Flag Processors

This processor converts appliances discovery arrays into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class AppliancesProcessor(BaseFlagProcessor):
    """
    Processor for appliances-related discovery flags.
    
    Converts appliances array values like ["Stove", "Dishwasher"] into
    individual flags like {"HasStove": True, "HasDishwasher": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for appliances discovery data."""
        return "appliances"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map appliances array values to flag names.
        
        Returns:
            Dictionary mapping appliances values to flag names
        """
        return {
            "Stove": "HasStove",
            "Dishwasher": "HasDishwasher",
            "Washer/dryer": "HasWasherDryer",
            "Oven": "HasOven",
            "Microwave": "HasMicrowave",
            "Garbage disposal": "HasGarbageDisposal",
            "Refrigerator": "HasRefrigerator"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any appliances issues."""
        return "HasAppliances"
