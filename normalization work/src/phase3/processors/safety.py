"""
Safety Flag Processor for Phase 3: Flag Processors

This processor converts safety discovery data into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class SafetyProcessor(BaseFlagProcessor):
    """
    Processor for safety-related discovery flags.
    
    Converts safety data into individual flags like {"HasSafety": True, "HasInoperableLocks": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for safety discovery data."""
        return "safety_issues"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map safety values to flag names.
        
        Returns:
            Dictionary mapping safety values to flag names
        """
        return {
            "Inoperable locks": "HasInoperableLocks",
            "Broken/inoperable security gate": "HasBrokenSecurityGate",
            "Security cameras": "HasSecurityCameras",
            "Broken buzzer to get in": "HasBrokenBuzzerToGetIn"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any safety issues."""
        return "HasSafety"

    def process(self, discovery_data: Dict[str, any]) -> Dict[str, bool]:
        """
        Process safety discovery data with custom logic.
        
        Args:
            discovery_data: Discovery object from dataset
            
        Returns:
            Dictionary of flags
        """
        flags = {}
        
        # Process individual safety flags from the normalized field name
        safety_array = discovery_data.get("safety_issues", [])
        for value, flag_name in self.flag_mappings.items():
            flags[flag_name] = any(
                v.lower() == value.lower() for v in safety_array
            )
        
        # Set aggregate flag
        flags[self.aggregate_flag_name] = any(flags.values())
        
        return flags
