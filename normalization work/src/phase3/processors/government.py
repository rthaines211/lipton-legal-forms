"""
Government Flag Processor for Phase 3: Flag Processors

This processor converts government entity discovery arrays into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class GovernmentProcessor(BaseFlagProcessor):
    """
    Processor for government entity-related discovery flags.
    
    Converts government entity array values like ["Health Department", "Housing Authority"] into
    individual flags like {"HasHealthDepartment": True, "HasHousingAuthority": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for government entity discovery data."""
        return "government_entities"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map government entity array values to flag names.
        
        Returns:
            Dictionary mapping government entity values to flag names
        """
        return {
            "Health Department": "HasDepartmentOfPublicHealth",
            "Code Enforcement": "HasCodeEnforcement",
            "Fire Department": "HasFireDepartment",
            "Police Department": "HasPoliceDepartment",
            "Department of Environmental Health": "HasDepartmentOfEnvironmentalHealth",
            "Department of Health Services": "HasDepartmentOfHealthServices"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any government entity contact."""
        return "HasGovernmentEntityContacted"

    def process(self, discovery_data: Dict[str, list]) -> Dict[str, bool]:
        """
        Process government discovery data with custom aggregate logic.
        
        Args:
            discovery_data: Discovery object from dataset
            
        Returns:
            Dictionary of flags including custom aggregates
        """
        # Get base flags from parent class
        flags = super().process(discovery_data)

        # Add general government contact flag if any government entities were contacted
        gov_flags = [
            flags.get("HasDepartmentOfPublicHealth", False),
            flags.get("HasCodeEnforcement", False),
            flags.get("HasFireDepartment", False),
            flags.get("HasPoliceDepartment", False),
            flags.get("HasDepartmentOfEnvironmentalHealth", False),
            flags.get("HasDepartmentOfHealthServices", False)
        ]
        flags["HasGovContact"] = any(gov_flags)

        return flags
