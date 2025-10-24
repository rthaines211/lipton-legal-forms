"""
Set Splitter Module

Implements the seed-accumulate-split algorithm for dividing profiled datasets
into sets with a maximum number of interrogatories per set.
"""

from typing import List, Dict, Any


def _number_to_words(num: int) -> str:
    """
    Convert numbers 1-20 to words, fallback to string for larger numbers.

    Args:
        num: Number to convert

    Returns:
        Word representation of the number

    Examples:
        >>> _number_to_words(1)
        'One'
        >>> _number_to_words(12)
        'Twelve'
        >>> _number_to_words(25)
        '25'
    """
    words = {
        1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
        6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
        11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen",
        16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen", 20: "Twenty"
    }
    return words.get(num, str(num))


def _build_full_address(case_metadata: dict) -> str:
    """
    Build full address string from case metadata.

    Args:
        case_metadata: Case metadata dictionary

    Returns:
        Formatted full address string

    Examples:
        >>> metadata = {
        ...     'property_address_with_unit': '123 Main St Unit 5',
        ...     'city': 'Los Angeles',
        ...     'state': 'CA',
        ...     'zip': '90001'
        ... }
        >>> _build_full_address(metadata)
        '123 Main St Unit 5, Los Angeles, CA, 90001'
    """
    parts = []

    # Use property_address_with_unit if available, otherwise property_address
    if case_metadata.get('property_address_with_unit'):
        parts.append(case_metadata['property_address_with_unit'])
    elif case_metadata.get('property_address'):
        parts.append(case_metadata['property_address'])

    # Add city, state, zip
    if case_metadata.get('city'):
        parts.append(case_metadata['city'])
    if case_metadata.get('state'):
        parts.append(case_metadata['state'])
    if case_metadata.get('zip'):
        parts.append(case_metadata['zip'])

    return ', '.join(parts)


class SetSplitter:
    """
    Implements set splitting algorithm for legal discovery interrogatories.

    The algorithm operates in three phases:
    1. SEED PHASE: Add first-set-only flags to Set 1
    2. ACCUMULATION PHASE: Distribute remaining flags across sets
    3. ENRICHMENT PHASE: Add metadata (set numbers, interrogatory ranges)

    Attributes:
        max_interrogatories_per_set: Maximum number of interrogatories allowed per set
    """

    def __init__(self, max_interrogatories_per_set: int = 120):
        """
        Initialize the SetSplitter.

        Args:
            max_interrogatories_per_set: Maximum interrogatories per set (default: 120)
        """
        self.max_interrogatories_per_set = max_interrogatories_per_set

    def split_into_sets(self, profiled_dataset: Dict[str, Any]) -> Dict[str, Any]:
        """
        Split profiled dataset into sets with max interrogatories per set.

        The algorithm:
        1. Separates first-set-only flags from regular flags
        2. Seeds Set 1 with first-set-only flags
        3. Sorts regular flags by interrogatory count (descending)
        4. Accumulates flags into sets, creating new sets when limit reached
        5. Enriches sets with metadata (set number, interrogatory ranges)

        Args:
            profiled_dataset: Dataset from Phase 4 with profile applied
                Expected keys:
                - flags: Dict of flag names to boolean values
                - interrogatory_counts: Dict of flag names to interrogatory counts
                - first_set_only_flags: List of flag names that only appear in Set 1
                - doc_type: Document type (SROGs, PODs, Admissions)
                - dataset_id: Unique dataset identifier
                - plaintiff: Plaintiff information dict
                - defendant: Defendant information dict
                - case_metadata: Case metadata dict
                - template: Template identifier
                - filename_suffix: Suffix for filename generation

        Returns:
            Dictionary containing:
            - doc_type: Document type
            - dataset_id: Dataset identifier
            - plaintiff: Plaintiff information
            - defendant: Defendant information
            - case_metadata: Case metadata
            - template: Template identifier
            - filename_suffix: Filename suffix
            - sets: List of set dictionaries with:
                - set_number: Sequential set number (1, 2, 3, ...)
                - interrogatory_start: Starting interrogatory number
                - interrogatory_end: Ending interrogatory number
                - total_interrogatories: Total count in this set
                - is_first_set: Boolean indicating if this is Set 1
                - flags: Dict of flag names to True for flags in this set
            - metadata: Summary metadata with:
                - total_sets: Total number of sets created
                - total_interrogatories: Sum of all interrogatories across sets
                - max_per_set: Maximum interrogatories per set

        Examples:
            >>> splitter = SetSplitter(max_interrogatories_per_set=120)
            >>> dataset = {
            ...     'flags': {'SROGsGeneral': True, 'HasMold': True},
            ...     'interrogatory_counts': {'SROGsGeneral': 10, 'HasMold': 24},
            ...     'first_set_only_flags': ['SROGsGeneral'],
            ...     'doc_type': 'SROGs',
            ...     # ... other required fields
            ... }
            >>> result = splitter.split_into_sets(dataset)
            >>> result['metadata']['total_sets']
            1
            >>> result['sets'][0]['total_interrogatories']
            34
        """
        flags = profiled_dataset['flags']
        interrogatory_counts = profiled_dataset['interrogatory_counts']
        first_set_only_flags = profiled_dataset.get('first_set_only_flags', [])

        # Get all TRUE flags only (False flags are not included in output)
        true_flags = {k: v for k, v in flags.items() if v is True}

        # Separate first-set-only flags from regular flags
        first_set_flags = {
            k: v for k, v in true_flags.items()
            if k in first_set_only_flags
        }
        regular_flags = {
            k: v for k, v in true_flags.items()
            if k not in first_set_only_flags
        }

        # Sort regular flags by interrogatory count (descending)
        # This greedy algorithm places larger flags first to minimize sets
        sorted_flags = sorted(
            regular_flags.keys(),
            key=lambda k: interrogatory_counts.get(k, 0),
            reverse=True
        )

        # Initialize sets list
        sets = []
        current_set = {
            'flags': {},
            'interrogatory_count': 0
        }

        # SEED PHASE: Add first-set-only flags to Set 1
        for flag_name in first_set_flags:
            count = interrogatory_counts.get(flag_name, 0)
            current_set['flags'][flag_name] = True
            current_set['interrogatory_count'] += count

        # ACCUMULATION PHASE: Add regular flags to sets
        for flag_name in sorted_flags:
            count = interrogatory_counts.get(flag_name, 0)

            # Check if adding this flag would exceed the limit
            if current_set['interrogatory_count'] + count > self.max_interrogatories_per_set:
                # Close current set and start new one
                if current_set['flags']:  # Only save if not empty
                    sets.append(current_set)

                # Start new set
                current_set = {
                    'flags': {},
                    'interrogatory_count': 0
                }

            # Add flag to current set
            current_set['flags'][flag_name] = True
            current_set['interrogatory_count'] += count

        # Add final set if it has any flags
        if current_set['flags']:
            sets.append(current_set)

        # ENRICHMENT PHASE: Add metadata to each set
        enriched_sets = self._enrich_sets(sets, profiled_dataset)

        # Return complete result with all necessary metadata
        return {
            'doc_type': profiled_dataset['doc_type'],
            'dataset_id': profiled_dataset['dataset_id'],
            'plaintiff': profiled_dataset['plaintiff'],
            'defendant': profiled_dataset['defendant'],
            'case_metadata': profiled_dataset['case_metadata'],
            'template': profiled_dataset['template'],
            'filename_suffix': profiled_dataset['filename_suffix'],
            'sets': enriched_sets,
            'metadata': {
                'total_sets': len(enriched_sets),
                'total_interrogatories': sum(s['InterrogatoryCount'] for s in enriched_sets),
                'max_per_set': self.max_interrogatories_per_set
            }
        }

    def _enrich_sets(
        self,
        sets: List[Dict[str, Any]],
        profiled_dataset: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Add metadata to each set including set numbers, interrogatory ranges, and case context.

        Creates webhook-ready payloads with:
        - Flattened flags (not nested)
        - PascalCase field names
        - All case context from Phase 1
        - Party information
        - Template and output name

        Interrogatories are numbered continuously across sets:
        - Set 1: 1-120
        - Set 2: 121-240
        - Set 3: 241-360
        - etc.

        Args:
            sets: List of raw set dictionaries with flags and interrogatory_count
            profiled_dataset: Complete profiled dataset with case context

        Returns:
            List of enriched set dictionaries ready for webhook payload
        """
        enriched = []
        interrogatory_start = 1  # Interrogatories start at 1
        total_sets = len(sets)

        # Extract context from profiled dataset
        case_context = profiled_dataset.get('case_context', {})
        plaintiff = profiled_dataset.get('plaintiff', {})
        defendant = profiled_dataset.get('defendant', {})
        case_metadata = profiled_dataset.get('case_metadata', {})
        template = profiled_dataset.get('template', '')
        filename_suffix = profiled_dataset.get('filename_suffix', '')

        for i, set_data in enumerate(sets):
            interrogatory_count = set_data['interrogatory_count']
            interrogatory_end = interrogatory_start + interrogatory_count - 1
            set_number = i + 1

            # Build the enriched set with flattened structure
            enriched_set = {
                # Set metadata (PascalCase as per Phase-5-Addendum)
                'SetNumber': set_number,
                'SetNoWrite': _number_to_words(set_number),
                'SetLabel': f"Set {set_number} of {total_sets}",
                'SetStart': interrogatory_start,
                'SetEnd': interrogatory_end,
                'InterrogatoryStart': interrogatory_start,
                'InterrogatoryCount': interrogatory_count,

                # Party information
                'HeadOfHousehold': plaintiff.get('full_name', ''),
                'TargetDefendant': defendant.get('full_name', ''),

                # Template and output information
                'Template': template,
                'OutputName': self._generate_output_name(
                    plaintiff.get('full_name', ''),
                    defendant.get('full_name', ''),
                    filename_suffix,
                    set_number,
                    total_sets
                ),

                # Case information (nested under Case key)
                'Case': {
                    'FilingCounty': case_context.get('filing_county', ''),
                    'FullAddress': _build_full_address(case_metadata)
                },

                # Aggregate plaintiff/defendant information
                'AllPlaintiffsUpperWithTypes': case_context.get('all_plaintiffs_upper_with_types', ''),
                'AllDefendantsUpperWithTypes': case_context.get('all_defendants_upper_with_types', ''),
                'Plaintiffs': case_context.get('plaintiffs_array', []),
            }

            # FLATTEN FLAGS: Unpack flags to top level (not nested in 'flags' object)
            enriched_set.update(set_data['flags'])

            enriched.append(enriched_set)

            # Next set starts after current set ends
            interrogatory_start = interrogatory_end + 1

        return enriched

    def _generate_output_name(
        self,
        plaintiff_name: str,
        defendant_name: str,
        filename_suffix: str,
        set_number: int,
        total_sets: int
    ) -> str:
        """
        Generate output filename for the set.

        Args:
            plaintiff_name: Plaintiff full name
            defendant_name: Defendant full name
            filename_suffix: Document type suffix
            set_number: Current set number
            total_sets: Total number of sets

        Returns:
            Formatted filename string with .docx extension

        Example:
            >>> self._generate_output_name('John Doe', 'ABC Corp', 'Discovery Propounded SROGs', 1, 2)
            'John Doe vs ABC Corp - Discovery Propounded SROGs Set 1 of 2.docx'
        """
        return f"{plaintiff_name} vs {defendant_name} - {filename_suffix} Set {set_number} of {total_sets}.docx"
