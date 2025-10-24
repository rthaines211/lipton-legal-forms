"""
Plumbing Flag Processor for Phase 3: Flag Processors

This processor converts plumbing discovery arrays into individual boolean flags
with complex aggregate logic.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class PlumbingProcessor(BaseFlagProcessor):
    """
    Processor for plumbing-related discovery flags.
    
    Converts plumbing array values like ["Toilet", "Leaks", "Clogged toilets"] into
    individual flags with additional aggregate flags for clogs.
    """

    @property
    def category_name(self) -> str:
        """Category name for plumbing discovery data."""
        return "plumbing"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map plumbing array values to flag names.
        
        Returns:
            Dictionary mapping plumbing values to flag names
        """
        return {
            "Toilet": "HasToilet",
            "Shower": "HasShower",
            "Bath": "HasBath",
            "Fixtures": "HasFixtures",
            "Leaks": "HasLeaks",
            "Insufficient water pressure": "HasInsufficientWaterPressure",
            "No hot water": "HasNoHotWater",
            "No cold water": "HasNoColdWater",
            "Sewage coming out": "HasSewageComingOut",
            "Clogged toilets": "HasCloggedToilets",
            "Clogged bath": "HasCloggedBath",
            "Clogged sinks": "HasCloggedSinks",
            "Clogged shower": "HasCloggedShower",
            "No Clean Water Supply": "HasNoCleanWaterSupply",
            "Unsanitary water": "HasUnsanitaryWater",
            # Add singular mappings for compatibility with manual conversion
            "Clogged sink": "HasCloggedSink",
            "Clogged toilet": "HasCloggedToilet"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any plumbing issues."""
        return "HasPlumbingIssues"

    def process(self, discovery_data: Dict[str, list]) -> Dict[str, bool]:
        """
        Process plumbing discovery data with custom aggregate logic.
        
        Args:
            discovery_data: Discovery object from dataset
            
        Returns:
            Dictionary of flags including custom aggregates
        """
        # Get base flags from parent class
        flags = super().process(discovery_data)

        # Additional aggregate: HasClogs
        # This aggregates all clog-related flags
        clog_flags = [
            flags.get("HasCloggedToilets", False),
            flags.get("HasCloggedBath", False),
            flags.get("HasCloggedSinks", False),
            flags.get("HasCloggedShower", False)
        ]
        flags["HasClogs"] = any(clog_flags)

        # Add singular flags for compatibility with manual conversion
        # Map plural flags to singular versions
        if flags.get("HasCloggedSinks", False):
            flags["HasCloggedSink"] = True
        if flags.get("HasCloggedToilets", False):
            flags["HasCloggedToilet"] = True

        # Add general plumbing flag if any plumbing issues exist
        plumbing_flags = [
            flags.get("HasToilet", False),
            flags.get("HasShower", False),
            flags.get("HasBath", False),
            flags.get("HasFixtures", False),
            flags.get("HasLeaks", False),
            flags.get("HasInsufficientWaterPressure", False),
            flags.get("HasNoHotWater", False),
            flags.get("HasNoColdWater", False),
            flags.get("HasSewageComingOut", False),
            flags.get("HasCloggedToilets", False),
            flags.get("HasCloggedBath", False),
            flags.get("HasCloggedSinks", False),
            flags.get("HasCloggedShower", False),
            flags.get("HasNoCleanWaterSupply", False),
            flags.get("HasUnsanitaryWater", False)
        ]
        flags["HasPlumbing"] = any(plumbing_flags)

        return flags
