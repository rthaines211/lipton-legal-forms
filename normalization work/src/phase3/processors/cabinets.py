"""
Cabinets Flag Processor for Phase 3: Flag Processors

This processor converts cabinets discovery data into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class CabinetsProcessor(BaseFlagProcessor):
    """
    Processor for cabinets-related discovery flags.
    
    Converts cabinets data into individual flags like {"HasCabinets": True, "HasCabinetsBroken": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for cabinets discovery data."""
        return "cabinets"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map cabinets values to flag names.
        
        Returns:
            Dictionary mapping cabinets values to flag names
        """
        return {
            "Broken": "HasCabinetsBroken",
            "Hinges": "HasCabinetHinges",
            "Alignment": "HasCabinetAlignment"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any cabinets issues."""
        return "HasCabinets"

    def process(self, discovery_data: Dict[str, any]) -> Dict[str, bool]:
        """
        Process cabinets discovery data with custom logic.
        
        Args:
            discovery_data: Discovery object from dataset
            
        Returns:
            Dictionary of flags
        """
        flags = {}
        
        # Process individual cabinet flags from the normalized field name
        cabinets_array = discovery_data.get("cabinets", [])
        for value, flag_name in self.flag_mappings.items():
            flags[flag_name] = any(
                v.lower() == value.lower() for v in cabinets_array
            )
        
        # Set aggregate flag
        flags[self.aggregate_flag_name] = any(flags.values())
        
        return flags
