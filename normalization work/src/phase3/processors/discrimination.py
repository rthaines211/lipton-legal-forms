"""
Discrimination Flag Processor for Phase 3: Flag Processors

This processor converts discrimination discovery data into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class DiscriminationProcessor(BaseFlagProcessor):
    """
    Processor for discrimination-related discovery flags.
    
    Converts discrimination data into individual flags like {"HasAgeDiscrimination": True, "HasRacialDiscrimination": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for discrimination discovery data."""
        return "discrimination"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map discrimination values to flag names.
        
        Returns:
            Dictionary mapping discrimination values to flag names
        """
        return {
            "Age discrimination": "HasAgeDiscrimination",
            "Disability discrimination": "HasDisabilityDiscrimination",
            "Racial Discrimination": "HasRacialDiscrimination",
            "Security Deposit": "HasSecurityDeposit"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """No aggregate flag for discrimination."""
        return None

    def process(self, discovery_data: Dict[str, any]) -> Dict[str, bool]:
        """
        Process discrimination discovery data.
        
        Args:
            discovery_data: Discovery object from dataset
            
        Returns:
            Dictionary of flags
        """
        flags = {}
        
        # Process each discrimination flag using the normalized field names
        field_mappings = {
            "has_age_discrimination": "HasAgeDiscrimination",
            "has_disability_discrimination": "HasDisabilityDiscrimination", 
            "has_racial_discrimination": "HasRacialDiscrimination",
            "has_security_deposit_issues": "HasSecurityDeposit"
        }
        
        for field_key, flag_name in field_mappings.items():
            if field_key in discovery_data:
                # Convert to boolean if needed
                value = discovery_data[field_key]
                if isinstance(value, str):
                    flags[flag_name] = value.lower() in ['yes', 'true', '1']
                else:
                    flags[flag_name] = bool(value)
            else:
                flags[flag_name] = False

        return flags
