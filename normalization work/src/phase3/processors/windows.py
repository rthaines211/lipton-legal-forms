"""
Windows Flag Processor for Phase 3: Flag Processors

This processor converts windows discovery arrays into individual boolean flags.
"""

from typing import Dict
from ..base_processor import BaseFlagProcessor


class WindowsProcessor(BaseFlagProcessor):
    """
    Processor for windows-related discovery flags.
    
    Converts windows array values like ["Broken", "Screens"] into
    individual flags like {"HasBrokenWindows": True, "HasWindowScreens": True}.
    """

    @property
    def category_name(self) -> str:
        """Category name for windows discovery data."""
        return "windows"

    @property
    def flag_mappings(self) -> Dict[str, str]:
        """
        Map windows array values to flag names.
        
        Returns:
            Dictionary mapping windows values to flag names
        """
        return {
            "Broken": "HasBrokenWindows",
            "Screens": "HasWindowScreens",
            "Leaks": "HasWindowLeaks",
            "Do not lock": "HasWindowsDoNotLock",
            "Missing Windows": "HasMissingWindows",
            "Broken or Missing screens": "HasBrokenMissingScreens"
        }

    @property
    def aggregate_flag_name(self) -> str:
        """Aggregate flag for any windows issues."""
        return "HasWindows"
