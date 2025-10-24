"""
Phase 4: Document Profiles

This module implements document type-specific transformations to create three separate profiles:
- SROGs (Special Requests for Objections and General)
- PODs (Production of Documents) 
- Admissions (Request for Admissions)

Each profile has specific flags, templates, and interrogatory count mappings.
"""

from .base_profile import BaseDocumentProfile
from .profiles.srogs_complete import SROGsProfile
from .profiles.pods_complete import PODsProfile
from .profiles.admissions_complete import AdmissionsProfile
from .profile_pipeline import ProfilePipeline

__all__ = [
    'BaseDocumentProfile',
    'SROGsProfile', 
    'PODsProfile',
    'AdmissionsProfile',
    'ProfilePipeline'
]
