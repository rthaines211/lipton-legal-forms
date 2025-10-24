"""
Notices Flag Processor for Phase 3: Flag Processors

This processor converts notices discovery data into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class NoticesProcessor(BaseFlagProcessor):
    """
    Processor for notices-related discovery flags.
    
    Converts notices data into individual flags like {"HasNotices": True, "Has24HourNotices": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for notices discovery data."""
        return "notices"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map notices values to flag names.
        
        Returns:
            Dictionary mapping notices values to flag names
        """
        return {
            "24-hour": "Has24HourNotices",
            "3-day": "Has3DayNotices",
            "30-day": "Has30DayNotices",
            "60-day": "Has60DayNotices",
            "To quit": "HasToQuitNotices",
            "Perform or Quit": "HasPerformOrQuit"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any notices issues."""
        return "HasNotices"

    def process(self, discovery_data: Dict[str, any]) -> Dict[str, bool]:
        """
        Process notices discovery data with custom logic.
        
        Args:
            discovery_data: Discovery object from dataset
            
        Returns:
            Dictionary of flags
        """
        flags = {}
        
        # Process individual notices flags from the normalized field name
        notices_array = discovery_data.get("notices", [])
        for value, flag_name in self.flag_mappings.items():
            flags[flag_name] = any(
                v.lower() == value.lower() for v in notices_array
            )
        
        # Set aggregate flag
        flags[self.aggregate_flag_name] = any(flags.values())
        
        return flags
