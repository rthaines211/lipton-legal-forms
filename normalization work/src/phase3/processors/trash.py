"""
Trash Flag Processor for Phase 3: Flag Processors

This processor converts trash discovery data into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class TrashProcessor(BaseFlagProcessor):
    """
    Processor for trash-related discovery flags.
    
    Converts trash data into individual flags like {"HasTrashProblems": True, "HasInadequateNumberOfTrashReceptacles": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for trash discovery data."""
        return "trash"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map trash values to flag names.
        
        Returns:
            Dictionary mapping trash values to flag names
        """
        return {
            "Inadequate number of receptacles": "HasInadequateNumberOfTrashReceptacles",
            "Properly servicing and emptying receptacles": "HasInadequateServicingAndEmptyingTrashReceptacles"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any trash issues."""
        return "HasTrashProblems"

    def process(self, discovery_data: Dict[str, any]) -> Dict[str, bool]:
        """
        Process trash discovery data with custom logic.
        
        Args:
            discovery_data: Discovery object from dataset
            
        Returns:
            Dictionary of flags
        """
        flags = {}
        
        # Process individual trash flags from the normalized field name
        trash_array = discovery_data.get("trash_problems", [])
        for value, flag_name in self.flag_mappings.items():
            flags[flag_name] = any(
                v.lower() == value.lower() for v in trash_array
            )
        
        # Set aggregate flag
        flags[self.aggregate_flag_name] = any(flags.values())
        
        return flags
