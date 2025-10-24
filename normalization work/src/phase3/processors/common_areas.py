"""
Common Areas Flag Processor for Phase 3: Flag Processors

This processor converts common areas discovery arrays into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class CommonAreasProcessor(BaseFlagProcessor):
    """
    Processor for common areas-related discovery flags.
    
    Converts common areas array values like ["Mailbox broken", "Parking area issues"] into
    individual flags like {"HasMailboxBroken": True, "HasParkingAreaIssues": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for common areas discovery data."""
        return "common_areas"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map common areas array values to flag names.
        
        Returns:
            Dictionary mapping common areas values to flag names
        """
        return {
            "Mailbox broken": "HasMailboxBroken",
            "Parking area issues": "HasParkingAreaIssues",
            "Damage to cars": "HasDamageToCars",
            "Flooding": "HasFlooding",
            "Entrances blocked": "HasEntrancesBlocked",
            "Swimming pool": "HasSwimmingPool",
            "Jacuzzi": "HasJacuzzi",
            "Laundry room": "HasLaundryRoom",
            "Recreation room": "HasRecreationRoom",
            "Gym": "HasGym",
            "Blocked areas/doors": "HasBlockedAreasDoors",
            "Elevator": "HasElevator",
            "Filth Rubbish Garbage": "HasFilthRubbishGarbage",
            "Vermin": "HasCommonAreaVermin",
            "Broken Gate": "HasBrokenGate",
            "Insects": "HasCommonAreaInsects"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any common areas issues."""
        return "HasCommonArea"
