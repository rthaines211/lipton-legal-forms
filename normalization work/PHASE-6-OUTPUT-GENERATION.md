# Phase 6: Output Generation

## Overview
Generate both Zapier-mode (flattened for automation) and Local-mode (nested for human review) output formats from split sets.

## Input (from Phase 5)
```json
{
  "doc_type": "SROGs",
  "dataset_id": "...",
  "plaintiff": {...},
  "defendant": {...},
  "sets": [
    {
      "set_number": 1,
      "filename": "John Doe vs ABC Corp - Discovery Propounded SROGs Set 1 of 2",
      "flags": {...},
      "total_interrogatories": 120
    },
    {...}
  ]
}
```

## Output Formats

### Zapier Mode (Flat Array)
```json
{
  "all_sets": [
    {
      "DocType": "SROGs",
      "Template": "SROGsMaster.docx",
      "FileName": "John Doe vs ABC Corp - Discovery Propounded SROGs Set 1 of 2",
      "SetNumber": 1,
      "TotalSets": 2,
      "PlaintiffName": "John Doe",
      "DefendantName": "ABC Corp",
      "PropertyAddress": "1331 Yorkshire Place NW Unit 1",
      "sets_custom_text": "{...full dataset as JSON string...}"
    },
    {...more sets for all profiles...}
  ]
}
```

### Local Mode (Nested Structure)
```json
{
  "documents": [
    {
      "DocType": "SROGs",
      "Template": "SROGsMaster.docx",
      "PlaintiffName": "John Doe",
      "DefendantName": "ABC Corp",
      "Sets": [
        {
          "SetNumber": 1,
          "FileName": "John Doe vs ABC Corp - Discovery Propounded SROGs Set 1 of 2",
          "InterrogatoryStart": 1,
          "InterrogatoryEnd": 120,
          "TotalInterrogatories": 120,
          "Flags": {...}
        },
        {...}
      ]
    },
    {
      "DocType": "PODs",
      "Sets": [...]
    },
    {
      "DocType": "Admissions",
      "Sets": [...]
    }
  ],
  "all_sets": [...flat array same as Zapier mode...]
}
```

## Task 6.1: Create Output Formatters

### Zapier Mode Formatter
**File**: `normalization work/src/phase6/zapier_formatter.py`

```python
import json
from typing import List, Dict

class ZapierFormatter:
    """Formats output for Zapier automation."""

    def format_set_for_zapier(self, set_data: dict, split_result: dict) -> dict:
        """
        Format a single set for Zapier.

        Args:
            set_data: Individual set from split_result['sets']
            split_result: Full split result with metadata

        Returns:
            Zapier-formatted set
        """
        # Build full dataset JSON (for sets_custom_text)
        full_dataset = {
            'doc_type': split_result['doc_type'],
            'dataset_id': split_result['dataset_id'],
            'set_number': set_data['set_number'],
            'total_sets': split_result['metadata']['total_sets'],
            'plaintiff': split_result['plaintiff'],
            'defendant': split_result['defendant'],
            'case_metadata': split_result['case_metadata'],
            'interrogatory_start': set_data['interrogatory_start'],
            'interrogatory_end': set_data['interrogatory_end'],
            'total_interrogatories': set_data['total_interrogatories'],
            'flags': set_data['flags']
        }

        # Flatten to Zapier format
        return {
            'DocType': split_result['doc_type'],
            'Template': split_result['template'],
            'FileName': set_data['filename'],
            'SetNumber': set_data['set_number'],
            'TotalSets': split_result['metadata']['total_sets'],
            'PlaintiffName': split_result['plaintiff']['full_name'],
            'DefendantName': split_result['defendant']['full_name'],
            'PropertyAddress': split_result['case_metadata']['property_address_with_unit'],
            'City': split_result['case_metadata']['city'],
            'State': split_result['case_metadata']['state'],
            'Zip': split_result['case_metadata']['zip'],
            'FilingCity': split_result['case_metadata']['filing_city'],
            'FilingCounty': split_result['case_metadata']['filing_county'],
            'InterrogatoryStart': set_data['interrogatory_start'],
            'InterrogatoryEnd': set_data['interrogatory_end'],
            'TotalInterrogatories': set_data['total_interrogatories'],
            'IsFirstSet': set_data['is_first_set'],
            'sets_custom_text': json.dumps(full_dataset, indent=2)
        }

    def format_all_sets(self, all_split_results: List[dict]) -> dict:
        """
        Format all sets from all profiles.

        Args:
            all_split_results: List of split results from SplittingPipeline

        Returns:
            Zapier-mode output
        """
        all_sets = []

        for split_result in all_split_results:
            for set_data in split_result['sets']:
                zapier_set = self.format_set_for_zapier(set_data, split_result)
                all_sets.append(zapier_set)

        return {
            'all_sets': all_sets
        }
```

### Local Mode Formatter
**File**: `normalization work/src/phase6/local_formatter.py`

```python
class LocalFormatter:
    """Formats output for local file review."""

    def format_document(self, split_result: dict) -> dict:
        """
        Format a single document (one profile) for local mode.

        Args:
            split_result: Split result for one profile (SROGs, PODs, or Admissions)

        Returns:
            Local-formatted document
        """
        return {
            'DocType': split_result['doc_type'],
            'Template': split_result['template'],
            'PlaintiffName': split_result['plaintiff']['full_name'],
            'DefendantName': split_result['defendant']['full_name'],
            'PropertyAddress': split_result['case_metadata']['property_address_with_unit'],
            'TotalSets': split_result['metadata']['total_sets'],
            'TotalInterrogatories': split_result['metadata']['total_interrogatories'],
            'Sets': [
                {
                    'SetNumber': s['set_number'],
                    'FileName': s['filename'],
                    'InterrogatoryStart': s['interrogatory_start'],
                    'InterrogatoryEnd': s['interrogatory_end'],
                    'TotalInterrogatories': s['total_interrogatories'],
                    'IsFirstSet': s['is_first_set'],
                    'Flags': s['flags']
                }
                for s in split_result['sets']
            ]
        }

    def format_all_documents(
        self,
        all_split_results: List[dict],
        include_zapier_flat: bool = True
    ) -> dict:
        """
        Format all documents for local mode.

        Args:
            all_split_results: List of split results from all profiles
            include_zapier_flat: Whether to include flat all_sets array

        Returns:
            Local-mode output
        """
        documents = []

        for split_result in all_split_results:
            doc = self.format_document(split_result)
            documents.append(doc)

        result = {
            'documents': documents
        }

        # Optionally include flat array for compatibility
        if include_zapier_flat:
            zapier_formatter = ZapierFormatter()
            zapier_output = zapier_formatter.format_all_sets(all_split_results)
            result['all_sets'] = zapier_output['all_sets']

        return result
```

## Task 6.2: Create Output Generator Pipeline
**File**: `normalization work/src/phase6/output_generator.py`

```python
from enum import Enum

class OutputMode(Enum):
    """Output format modes."""
    ZAPIER = "zapier"
    LOCAL = "local"
    BOTH = "both"

class OutputGenerator:
    """Main output generation pipeline."""

    def __init__(self):
        self.zapier_formatter = ZapierFormatter()
        self.local_formatter = LocalFormatter()

    def generate_output(
        self,
        all_split_results: List[dict],
        mode: OutputMode = OutputMode.BOTH
    ) -> dict:
        """
        Generate output in specified mode.

        Args:
            all_split_results: List of split results from Phase 5
            mode: Output mode (zapier, local, or both)

        Returns:
            Formatted output
        """
        if mode == OutputMode.ZAPIER:
            return self.zapier_formatter.format_all_sets(all_split_results)

        elif mode == OutputMode.LOCAL:
            return self.local_formatter.format_all_documents(all_split_results)

        elif mode == OutputMode.BOTH:
            return {
                'zapier': self.zapier_formatter.format_all_sets(all_split_results),
                'local': self.local_formatter.format_all_documents(all_split_results)
            }

        else:
            raise ValueError(f"Unknown output mode: {mode}")
```

## Task 6.3: Create JSON Export Utilities
**File**: `normalization work/src/phase6/json_export.py`

```python
import json
from pathlib import Path
from datetime import datetime

class JSONExporter:
    """Export output to JSON files."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_zapier_output(self, zapier_output: dict, case_id: str) -> Path:
        """
        Export Zapier-mode output to JSON file.

        Args:
            zapier_output: Zapier-formatted output
            case_id: Case ID for filename

        Returns:
            Path to exported file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{case_id}_zapier_{timestamp}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(zapier_output, f, indent=2, ensure_ascii=False)

        return filepath

    def export_local_output(self, local_output: dict, case_id: str) -> Path:
        """
        Export Local-mode output to JSON file.

        Args:
            local_output: Local-formatted output
            case_id: Case ID for filename

        Returns:
            Path to exported file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{case_id}_local_{timestamp}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(local_output, f, indent=2, ensure_ascii=False)

        return filepath

    def export_both(self, output: dict, case_id: str) -> dict:
        """
        Export both Zapier and Local outputs.

        Args:
            output: Output with both 'zapier' and 'local' keys
            case_id: Case ID for filenames

        Returns:
            Dictionary with paths to both files
        """
        return {
            'zapier_file': self.export_zapier_output(output['zapier'], case_id),
            'local_file': self.export_local_output(output['local'], case_id)
        }
```

## Test Plan

### Test 6.1: Zapier Formatting
**File**: `tests/phase6/test_zapier_formatter.py`

```python
def test_zapier_format_single_set():
    """Test Zapier formatting for single set"""
    formatter = ZapierFormatter()
    set_data = create_test_set()
    split_result = create_test_split_result()

    result = formatter.format_set_for_zapier(set_data, split_result)

    assert result['DocType'] == 'SROGs'
    assert result['Template'] == 'SROGsMaster.docx'
    assert result['FileName'] is not None
    assert result['sets_custom_text'] is not None
    # Verify sets_custom_text is valid JSON
    json.loads(result['sets_custom_text'])

def test_zapier_all_sets_flat():
    """Test Zapier output is flat array"""
    formatter = ZapierFormatter()
    split_results = create_multiple_split_results()  # 2 profiles, 2 sets each

    result = formatter.format_all_sets(split_results)

    assert 'all_sets' in result
    assert isinstance(result['all_sets'], list)
    assert len(result['all_sets']) == 4  # Flat array of all sets
```

### Test 6.2: Local Formatting
**File**: `tests/phase6/test_local_formatter.py`

```python
def test_local_format_document():
    """Test Local formatting for single document"""
    formatter = LocalFormatter()
    split_result = create_test_split_result()

    result = formatter.format_document(split_result)

    assert result['DocType'] == 'SROGs'
    assert 'Sets' in result
    assert isinstance(result['Sets'], list)

def test_local_nested_structure():
    """Test Local output has nested structure"""
    formatter = LocalFormatter()
    split_results = create_multiple_split_results()

    result = formatter.format_all_documents(split_results)

    assert 'documents' in result
    assert isinstance(result['documents'], list)
    # Each document has sets nested within
    for doc in result['documents']:
        assert 'Sets' in doc
```

### Test 6.3: Output Generation
**File**: `tests/phase6/test_output_generator.py`

```python
def test_generate_zapier_mode():
    """Test generating Zapier-only output"""
    generator = OutputGenerator()
    split_results = create_test_split_results()

    result = generator.generate_output(split_results, OutputMode.ZAPIER)

    assert 'all_sets' in result
    assert 'documents' not in result

def test_generate_local_mode():
    """Test generating Local-only output"""
    generator = OutputGenerator()
    split_results = create_test_split_results()

    result = generator.generate_output(split_results, OutputMode.LOCAL)

    assert 'documents' in result
    # May or may not include all_sets depending on config

def test_generate_both_modes():
    """Test generating both outputs"""
    generator = OutputGenerator()
    split_results = create_test_split_results()

    result = generator.generate_output(split_results, OutputMode.BOTH)

    assert 'zapier' in result
    assert 'local' in result
```

### Test 6.4: JSON Export
**File**: `tests/phase6/test_json_export.py`

```python
def test_export_creates_file(tmp_path):
    """Test JSON export creates file"""
    exporter = JSONExporter(output_dir=str(tmp_path))
    output = {'all_sets': []}

    filepath = exporter.export_zapier_output(output, 'test-case-123')

    assert filepath.exists()
    assert filepath.suffix == '.json'

def test_exported_json_valid(tmp_path):
    """Test exported JSON is valid"""
    exporter = JSONExporter(output_dir=str(tmp_path))
    output = create_test_output()

    filepath = exporter.export_zapier_output(output, 'test-case')

    # Verify can be loaded
    with open(filepath, 'r') as f:
        loaded = json.load(f)

    assert loaded == output
```

## Exit Criteria

### Formatting Complete
- ✅ Zapier formatter works correctly
- ✅ Local formatter works correctly
- ✅ Both formats generate valid JSON

### All Tests Pass
- ✅ 20+ unit tests pass
- ✅ Integration tests pass
- ✅ 100% code coverage

### Output Validation
- ✅ Zapier output matches spec
- ✅ Local output matches spec
- ✅ sets_custom_text is valid JSON

### File Export
- ✅ JSON files created successfully
- ✅ Filenames include timestamp and case ID
- ✅ Output directory created if missing

## Deliverables
1. ✅ Zapier formatter
2. ✅ Local formatter
3. ✅ Output generator pipeline
4. ✅ JSON exporter
5. ✅ 20+ passing tests
6. ✅ Output format documentation

---

**Phase Status**: 📋 Planning
**Estimated Duration**: 2-3 days
**Previous Phase**: [Phase 5: Set Splitting](PHASE-5-SET-SPLITTING.md)
**Next Phase**: [Phase 7: Integration](PHASE-7-INTEGRATION.md)
