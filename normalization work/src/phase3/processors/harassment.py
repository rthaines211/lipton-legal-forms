"""
Harassment Flag Processor for Phase 3: Flag Processors

This processor converts harassment discovery arrays into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class HarassmentProcessor(BaseFlagProcessor):
    """
    Processor for harassment-related discovery flags.
    
    Converts harassment array values like ["Unlawful Detainer", "Eviction threats"] into
    individual flags like {"HasUnlawfulDetainer": True, "HasEvictionThreat": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for harassment discovery data."""
        return "harassment"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map harassment array values to flag names.
        
        Returns:
            Dictionary mapping harassment values to flag names
        """
        return {
            "Unlawful Detainer": "HasUnlawfulDetainer",
            "Eviction threats": "HasEvictionThreat",
            "By defendant": "HasHarrassmentByDefendants",
            "By maintenance man/workers": "HasHarrassmentMaintenanceManWorkers",
            "By manager/building staff": "HasHarrassmentManagerStaff",
            "By owner": "HasHarrassmentByOwnerAndTheirGuests",
            "Other tenants": "HasHarrassmentOtherTenants",
            "Illegitimate notices": "HasIllegitimateNotices",
            "Refusal to make timely repairs": "HasRefusalToMakeTimelyRepairs",
            "Written threats": "HasWrittenThreats",
            "Aggressive/inappropriate language": "HasAggressiveInappropriateLanguage",
            "Physical threats or touching": "HasPhysicalThreatsOrTouching",
            "Notices singling out one tenant, but not uniformly given to all tenants": "HasNoticesSinglingOutOneTenant",
            "Duplicative notices": "HasDuplicativeNotices",
            "Untimely Response from Landlord": "HasUntimelyResponseFromLandlord"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any harassment issues."""
        return "HasHarassment"
