"""
Phase 5: Set Splitting

This phase implements the set splitting algorithm that divides profiled datasets
into sets with a maximum of 120 interrogatories per set. It handles:
- First-set-only flags (seeding)
- Flag accumulation across sets
- Sequential interrogatory numbering
- Filename generation for each set
"""

from .set_splitter import SetSplitter
from .filename_generator import generate_filename
from .splitting_pipeline import SplittingPipeline

__all__ = [
    'SetSplitter',
    'generate_filename',
    'SplittingPipeline',
]
