"""
Filename Generator Module

Generates standardized filenames for legal discovery document sets.
"""


def generate_filename(
    plaintiff_name: str,
    defendant_name: str,
    doc_type: str,
    set_number: int,
    total_sets: int,
    filename_suffix: str
) -> str:
    """
    Generate standardized filename for a legal discovery document set.

    The filename follows the format:
    "[Plaintiff] vs [Defendant] - [Suffix] Set [X] of [Y]"

    This format ensures:
    - Clear identification of parties (plaintiff vs defendant)
    - Document type specification via suffix
    - Set tracking (current set and total sets)
    - Professional, court-ready naming convention

    Args:
        plaintiff_name: Full name of the plaintiff
            Examples: "John Doe", "Jane Smith", "María José"
        defendant_name: Full name of the defendant
            Examples: "ABC Corp", "Smith LLC", "O'Brien Properties"
        doc_type: Document type identifier
            Examples: "SROGs", "PODs", "Admissions"
        set_number: Current set number (1-indexed)
            Examples: 1, 2, 3
        total_sets: Total number of sets in this document series
            Examples: 1, 2, 3
        filename_suffix: Profile-specific suffix describing the document
            Examples:
            - "Discovery Propounded SROGs"
            - "Responses to PODs"
            - "Requests for Admissions"

    Returns:
        Formatted filename string ready for file creation

    Examples:
        >>> generate_filename(
        ...     "John Doe",
        ...     "ABC Corp",
        ...     "SROGs",
        ...     1,
        ...     2,
        ...     "Discovery Propounded SROGs"
        ... )
        'John Doe vs ABC Corp - Discovery Propounded SROGs Set 1 of 2'

        >>> generate_filename(
        ...     "María José",
        ...     "O'Brien LLC",
        ...     "PODs",
        ...     1,
        ...     1,
        ...     "Discovery Propounded PODs"
        ... )
        "María José vs O'Brien LLC - Discovery Propounded PODs Set 1 of 1"

        >>> generate_filename(
        ...     "Jane Smith",
        ...     "XYZ Properties",
        ...     "Admissions",
        ...     3,
        ...     5,
        ...     "Requests for Admissions"
        ... )
        'Jane Smith vs XYZ Properties - Requests for Admissions Set 3 of 5'

    Notes:
        - Handles special characters (accents, apostrophes) correctly
        - Does not sanitize names (preserves legal accuracy)
        - Format is consistent with legal filing conventions
        - Set numbers are 1-indexed (first set is "Set 1 of N")
    """
    return f"{plaintiff_name} vs {defendant_name} - {filename_suffix} Set {set_number} of {total_sets}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for filesystem compatibility (optional helper).

    Removes or replaces characters that may cause issues on some filesystems.
    Note: This is optional and should only be used if filesystem compatibility
    issues arise. Legal names should be preserved as-is when possible.

    Args:
        filename: Original filename string

    Returns:
        Sanitized filename safe for most filesystems

    Examples:
        >>> sanitize_filename("John Doe vs ABC Corp - SROGs Set 1 of 2")
        'John Doe vs ABC Corp - SROGs Set 1 of 2'

        >>> sanitize_filename("Test/Name\\With:Bad*Chars")
        'Test_Name_With_Bad_Chars'
    """
    # Replace filesystem-unsafe characters with underscores
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    sanitized = filename

    for char in unsafe_chars:
        sanitized = sanitized.replace(char, '_')

    return sanitized
