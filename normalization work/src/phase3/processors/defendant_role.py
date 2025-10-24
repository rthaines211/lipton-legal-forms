"""
Defendant Role Flag Processor for Phase 3: Flag Processors

This processor converts defendant role data into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class DefendantRoleProcessor(BaseFlagProcessor):
    """
    Processor for defendant role-related discovery flags.
    
    Converts defendant role data into individual flags like {"IsOwner": True, "IsManager": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for defendant role discovery data."""
        return "defendant_role"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map defendant role values to flag names.
        
        Returns:
            Dictionary mapping defendant role values to flag names
        """
        return {
            "Owner": "IsOwner",
            "Manager": "IsManager"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for owner or manager."""
        return "IsOwnerManager"

    def process(self, dataset: Dict[str, any]) -> Dict[str, bool]:
        """
        Process defendant role data from the full dataset.
        
        Args:
            dataset: Full dataset object (not just discovery_data)
            
        Returns:
            Dictionary of flags
        """
        flags = {}
        
        # Get defendant role from dataset
        defendant = dataset.get("defendant", {})
        defendant_role = defendant.get("role", "").lower()
        
        # Process individual role flags
        flags["IsOwner"] = defendant_role == "owner"
        flags["IsManager"] = defendant_role == "manager"
        
        # Set aggregate flag
        flags[self.aggregate_flag_name] = flags["IsOwner"] or flags["IsManager"]

        return flags
