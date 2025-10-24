"""
Health Hazard Flag Processor for Phase 3: Flag Processors

This processor converts health hazard discovery arrays into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class HealthHazardProcessor(BaseFlagProcessor):
    """
    Processor for health hazard-related discovery flags.
    
    Converts health hazard array values like ["Mold", "Mildew"] into
    individual flags like {"HasMold": True, "HasMildew": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for health hazard discovery data."""
        return "health_hazard"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map health hazard array values to flag names.
        
        Returns:
            Dictionary mapping health hazard values to flag names
        """
        return {
            "Mold": "HasMold",
            "Mildew": "HasMildew",
            "Mushrooms": "HasMushrooms",
            "Raw sewage on exterior": "HasRawSewageOnExterior",
            "Noxious fumes": "HasNoxiousFumes",
            "Chemical/paint contamination": "HasChemicalsPaintContamination",
            "Toxic Water Pollution": "HasToxicWaterPollution",
            "Offensive Odors": "HasOffensiveOdors"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any health hazard issues."""
        return "HasHealthHazards"
