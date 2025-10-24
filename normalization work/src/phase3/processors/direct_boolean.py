"""
Direct Boolean Flag Processor for Phase 3: Flag Processors

This processor handles direct boolean flags from discovery data.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class DirectBooleanProcessor(BaseFlagProcessor):
    """
    Processor for direct boolean discovery flags.
    
    Converts boolean discovery values like {"has_injury": True} into
    individual flags like {"HasInjury": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for direct boolean discovery data."""
        return "direct_booleans"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map direct boolean values to flag names.
        
        Returns:
            Dictionary mapping boolean keys to flag names
        """
        return {
            "has_injury": "HasInjury",
            "has_nonresponsive_landlord": "HasNonresponsiveLandlord",
            "has_unauthorized_entries": "HasUnauthorizedEntries",
            "has_stolen_items": "HasStolenItems",
            "has_damaged_items": "HasDamagedItems"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """No aggregate flag for direct booleans."""
        return None

    def process(self, discovery_data: Dict[str, any]) -> Dict[str, bool]:
        """
        Process direct boolean discovery data.
        
        Args:
            discovery_data: Discovery object from dataset
            
        Returns:
            Dictionary of flags
        """
        flags = {}
        
        # Process each boolean flag
        for boolean_key, flag_name in self.flag_mappings.items():
            if boolean_key in discovery_data:
                # Convert to boolean if needed
                value = discovery_data[boolean_key]
                if isinstance(value, str):
                    flags[flag_name] = value.lower() in ['true', '1', 'yes']
                else:
                    flags[flag_name] = bool(value)
            else:
                flags[flag_name] = False

        return flags
