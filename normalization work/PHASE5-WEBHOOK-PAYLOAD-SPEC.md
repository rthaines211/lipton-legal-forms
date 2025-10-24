# Phase 5 Webhook Payload Specification

## Overview

Phase 5 now generates webhook-ready payloads with all flags flattened to the top level and comprehensive case context included in each set. This document describes the complete payload structure and implementation.

## Design Philosophy: Enrich Early, Flow Through

Instead of reconstructing data at the end of the pipeline, we follow the principle:

1. **Phase 1**: Compute case-level aggregates (ALL plaintiffs, ALL defendants) once
2. **Phase 2**: Attach case context to each dataset
3. **Phase 3-4**: Pass through unchanged
4. **Phase 5**: Simple assembly from pre-computed data

This approach:
- ✅ Computes expensive operations once (not 44+ times)
- ✅ Each phase receives complete context it needs
- ✅ Cleaner separation of concerns
- ✅ Better performance and maintainability

---

## Complete Payload Structure

Each set in Phase 5 output is a complete, webhook-ready payload:

```json
{
  "SetNumber": 1,
  "SetNoWrite": "One",
  "SetLabel": "Set 1 of 12",
  "SetStart": 1,
  "SetEnd": 120,
  "InterrogatoryStart": 1,
  "InterrogatoryCount": 120,

  "HeadOfHousehold": "Clark Kent",
  "TargetDefendant": "Tony Stark",

  "Template": "SROGsMaster.docx",
  "OutputName": "Clark Kent vs Tony Stark - Discovery Propounded SROGs Set 1 of 12",

  "Case": {
    "FilingCounty": "Los Angeles",
    "FullAddress": "1331 Yorkshire Place NW Unit 1, Los Angeles, North Carolina, 28027"
  },

  "AllPlaintiffsUpperWithTypes": "CLARK KENT, INDIVIDUAL; LOIS LANE, GUARDIAN; BRUCE WAYNE, INDIVIDUAL",
  "AllDefendantsUpperWithTypes": "TONY STARK, MANAGER; STEVE ROGERS, OWNER",

  "Plaintiffs": [
    "Clark Kent",
    "Lois Lane",
    "Bruce Wayne"
  ],

  "IsManager": true,
  "SROGsGeneral": true,
  "HasMold": true,
  "HasVermin": true,
  "HasRatsMice": true
  // ... all other flags flattened at top level
}
```

---

## Field Reference

### Set Metadata Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `SetNumber` | integer | Sequential set number (1, 2, 3, ...) | `1` |
| `SetNoWrite` | string | Set number as word (One-Twenty, then numeric) | `"One"` |
| `SetLabel` | string | Human-readable set label | `"Set 1 of 12"` |
| `SetStart` | integer | Starting interrogatory number (same as InterrogatoryStart) | `1` |
| `SetEnd` | integer | Ending interrogatory number | `120` |
| `InterrogatoryStart` | integer | Starting interrogatory number for this set | `1` |
| `InterrogatoryCount` | integer | Total interrogatories in this set | `120` |

**Notes:**
- `SetStart` and `InterrogatoryStart` contain the same value (kept for compatibility)
- Interrogatories number continuously: Set 1 (1-120), Set 2 (121-240), etc.
- `SetNoWrite` converts 1-20 to words, falls back to string for larger numbers

### Party Information Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `HeadOfHousehold` | string | Full name of the HoH plaintiff for this dataset | `"Clark Kent"` |
| `TargetDefendant` | string | Full name of the defendant for this dataset | `"Tony Stark"` |

**Context:**
- Each dataset represents one HoH plaintiff × one defendant combination
- These fields identify which specific pair this set belongs to

### Template & Output Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `Template` | string | Docmosis template filename | `"SROGsMaster.docx"` |
| `OutputName` | string | Generated document filename | `"Clark Kent vs Tony Stark - Discovery Propounded SROGs Set 1 of 12"` |

**Usage:**
- `Template`: Tells the webhook which Docmosis template to use
- `OutputName`: The filename for the generated document

### Case Information (Nested)

The `Case` object contains case-level information:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `Case.FilingCounty` | string | County where case is filed | `"Los Angeles"` |
| `Case.FullAddress` | string | Complete property address with unit | `"1331 Yorkshire Place NW Unit 1, Los Angeles, North Carolina, 28027"` |

### Aggregate Party Fields

These fields provide information about **ALL** parties in the case (not just the current HoH/defendant pair):

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `AllPlaintiffsUpperWithTypes` | string | Semicolon-separated list of all plaintiffs (uppercase) with types | `"CLARK KENT, INDIVIDUAL; LOIS LANE, GUARDIAN"` |
| `AllDefendantsUpperWithTypes` | string | Semicolon-separated list of all defendants (uppercase) with roles | `"TONY STARK, MANAGER; STEVE ROGERS, OWNER"` |
| `Plaintiffs` | array | Array of all plaintiff names (strings) | `["Clark Kent", "Lois Lane", "Bruce Wayne"]` |

**Plaintiffs Array Example:**
```json
[
  "Clark Kent",
  "Lois Lane",
  "Bruce Wayne"
]
```

### Flag Fields (Flattened)

**All boolean flags appear directly at the top level** (not nested in a `flags` object):

```json
{
  "HasMold": true,
  "HasVermin": true,
  "HasRatsMice": true,
  "IsManager": true,
  "SROGsGeneral": true,
  // ... 180+ other flags
}
```

**Key Points:**
- Only `true` flags are included (false flags are omitted)
- Flags use PascalCase naming (e.g., `HasMold`, not `has_mold`)
- First-set-only flags (like `SROGsGeneral`) only appear in Set 1

---

## Phase-by-Phase Data Flow

### Phase 1: Case Context Creation

**What happens:**
- Computes `AllPlaintiffsUpperWithTypes` from all 3 plaintiffs
- Computes `AllDefendantsUpperWithTypes` from all 2 defendants
- Creates `plaintiffs_array` with simplified plaintiff objects
- Stores in `case_info.case_context`

**Output:**
```json
{
  "case_info": {
    "case_id": "1",
    "filing_county": "Los Angeles",
    "case_context": {
      "all_plaintiffs_summary": [...],
      "all_defendants_summary": [...],
      "all_plaintiffs_upper_with_types": "CLARK KENT, INDIVIDUAL; LOIS LANE, GUARDIAN; BRUCE WAYNE, INDIVIDUAL",
      "all_defendants_upper_with_types": "TONY STARK, MANAGER; STEVE ROGERS, OWNER",
      "plaintiffs_array": [...],
      "filing_county": "Los Angeles"
    }
  }
}
```

### Phase 2: Context Attachment

**What happens:**
- Creates 4 datasets (2 HoH × 2 Defendants)
- Attaches `case_context` to each dataset
- Each dataset now carries complete case information

**Output:**
```json
{
  "datasets": [
    {
      "dataset_id": "1-VTSxIZ-t5dfqS",
      "plaintiff": {"full_name": "Clark Kent", ...},
      "defendant": {"full_name": "Tony Stark", ...},
      "case_context": {
        "all_plaintiffs_upper_with_types": "...",
        "all_defendants_upper_with_types": "...",
        // ... full context from Phase 1
      }
    }
  ]
}
```

### Phase 3-4: Pass Through

**What happens:**
- Phase 3 adds flags to each dataset
- Phase 4 creates 3 profiles per dataset (SROGs, PODs, Admissions)
- `case_context` passes through unchanged

### Phase 5: Payload Assembly

**What happens:**
- `SetSplitter._enrich_sets()` pulls pre-computed data from `case_context`
- Flattens flags using `enriched_set.update(set_data['flags'])`
- Generates `OutputName` using `_generate_output_name()`
- Builds complete webhook payload

---

## Implementation Details

### Helper Functions (Phase 1)

```python
def _build_plaintiffs_upper_with_types(plaintiffs: list) -> str:
    """Build semicolon-separated uppercase plaintiff list with types."""
    parts = []
    for p in plaintiffs:
        name = p.get('full_name', '').upper()
        plaintiff_type = p.get('plaintiff_type', 'Tenant').upper()
        if name:
            parts.append(f"{name}, {plaintiff_type}")
    return '; '.join(parts)

def _build_defendants_upper_with_types(defendants: list) -> str:
    """Build semicolon-separated uppercase defendant list with roles."""
    parts = []
    for d in defendants:
        name = d.get('full_name', '').upper()
        role = d.get('role', 'Defendant').upper()
        if name:
            parts.append(f"{name}, {role}")
    return '; '.join(parts)

def _build_case_context(case_info, plaintiffs, defendants) -> dict:
    """Build case-level context with aggregate information."""
    return {
        'all_plaintiffs_summary': [...],
        'all_defendants_summary': [...],
        'all_plaintiffs_upper_with_types': _build_plaintiffs_upper_with_types(plaintiffs),
        'all_defendants_upper_with_types': _build_defendants_upper_with_types(defendants),
        'plaintiffs_array': _build_plaintiffs_array(plaintiffs),
        'filing_county': case_info.get('filing_county', '')
    }
```

### Helper Functions (Phase 5)

```python
def _number_to_words(num: int) -> str:
    """Convert numbers 1-20 to words, fallback to string for larger."""
    words = {
        1: "One", 2: "Two", 3: "Three", ..., 20: "Twenty"
    }
    return words.get(num, str(num))

def _build_full_address(case_metadata: dict) -> str:
    """Build full address string from case metadata."""
    parts = []
    if case_metadata.get('property_address_with_unit'):
        parts.append(case_metadata['property_address_with_unit'])
    parts.append(case_metadata.get('city', ''))
    parts.append(case_metadata.get('state', ''))
    parts.append(case_metadata.get('zip', ''))
    return ', '.join(filter(None, parts))
```

### Flag Flattening

The key line that flattens flags:

```python
# In SetSplitter._enrich_sets()
enriched_set = {
    'SetNumber': set_number,
    'HeadOfHousehold': plaintiff['full_name'],
    # ... other fields ...
}

# FLATTEN FLAGS: Unpack flags dict to top level
enriched_set.update(set_data['flags'])
```

This uses Python's `dict.update()` to merge all flags directly into the set dictionary.

---

## Webhook Integration

### Sending Payloads

Each set in `output_phase5_*.json` is ready to send to a webhook:

```javascript
// Node.js example
const phase5Output = require('./output_phase5_20251017_131945.json');

for (const dataset of phase5Output.datasets) {
  for (const set of dataset.sets) {
    // Send to webhook
    await fetch('https://webhook.site/your-endpoint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(set)
    });
  }
}
```

### Webhook Endpoint Requirements

The webhook endpoint receives:
- `Template`: Which Docmosis template to use
- `OutputName`: What to name the generated document
- All flags as top-level boolean fields
- Complete case and party context
- Set metadata for multi-set handling

Example webhook processing:

```python
@app.route('/generate-document', methods=['POST'])
def generate_document():
    payload = request.json

    # Extract template and output name
    template = payload['Template']
    output_name = payload['OutputName']

    # Extract flags for conditional content
    has_mold = payload.get('HasMold', False)
    is_manager = payload.get('IsManager', False)

    # Generate document with Docmosis
    doc = docmosis.generate(
        template=template,
        data=payload,
        output_name=output_name
    )

    return doc
```

---

## Migration Notes

### Old Structure (Before Changes)

```json
{
  "set_number": 1,
  "interrogatory_start": 1,
  "total_interrogatories": 120,
  "is_first_set": true,
  "flags": {
    "HasMold": true,
    "HasVermin": true
  },
  "filename": "Clark Kent vs Tony Stark - Discovery Propounded SROGs Set 1 of 12"
}
```

### New Structure (After Changes)

```json
{
  "SetNumber": 1,
  "SetNoWrite": "One",
  "SetLabel": "Set 1 of 12",
  "SetStart": 1,
  "SetEnd": 120,
  "InterrogatoryStart": 1,
  "InterrogatoryCount": 120,
  "HeadOfHousehold": "Clark Kent",
  "TargetDefendant": "Tony Stark",
  "Template": "SROGsMaster.docx",
  "OutputName": "Clark Kent vs Tony Stark - Discovery Propounded SROGs Set 1 of 12",
  "Case": {...},
  "AllPlaintiffsUpperWithTypes": "...",
  "AllDefendantsUpperWithTypes": "...",
  "Plaintiffs": [...],
  "HasMold": true,
  "HasVermin": true
}
```

### Key Differences

| Aspect | Old | New |
|--------|-----|-----|
| **Flag structure** | Nested in `flags` object | Flattened to top level |
| **Field names** | snake_case | PascalCase |
| **Filename** | `filename` | `OutputName` |
| **Party context** | Not included | Complete context included |
| **Template** | Not included | Included as `Template` |
| **Case info** | Not included | Nested in `Case` object |

---

## Testing

### Verification Commands

```bash
cd "normalization work"
source venv/bin/activate

# Run complete pipeline
python3 run_pipeline.py

# Verify Phase 1 case context
python3 -c "
import json
data = json.load(open('output_phase1_*.json'))
print(data['case_info']['case_context'])
"

# Verify Phase 5 set structure
python3 -c "
import json
data = json.load(open('output_phase5_*.json'))
first_set = data['datasets'][0]['sets'][0]
print('SetNumber:', first_set['SetNumber'])
print('HasMold (flattened):', first_set.get('HasMold'))
print('flags object exists:', 'flags' in first_set)
"
```

### Expected Results

- ✅ Phase 1 includes `case_context` in `case_info`
- ✅ Phase 2 datasets include `case_context`
- ✅ Phase 5 sets have all flags flattened
- ✅ Phase 5 sets use PascalCase field names
- ✅ Phase 5 sets include all new fields from Phase-5-Addendum

---

## Performance Impact

### Before Changes (Reconstruct in Phase 5)
- Aggregate strings computed: **44 times** (once per set)
- Plaintiff/defendant lists built: **44 times**
- Total computation: **O(n × m)** where n = sets, m = parties

### After Changes (Enrich in Phase 1)
- Aggregate strings computed: **1 time** (in Phase 1)
- Plaintiff/defendant lists built: **1 time**
- Total computation: **O(m)** where m = parties

**Result:** ~44x fewer computations for aggregate operations

---

## Future Enhancements

Possible future additions to the payload:

1. **Defendant-specific fields**: `IsOwner`, `IsManager`, `EntityType` at top level
2. **Date fields**: `FilingDate`, `ServeBy` date calculations
3. **Attorney information**: If added to form intake
4. **Court information**: Court name, department, judge (if available)
5. **Tracking fields**: `GeneratedAt` timestamp, `PipelineVersion`

---

**Last Updated**: 2025-10-17
**Pipeline Version**: 2.0
**Author**: Claude (Anthropic)
**Status**: ✅ Implemented and Tested
