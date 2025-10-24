# Testing Phase 5 with Your Real Data

## Quick Start

To test Phase 5 with your actual form data, simply run:

```bash
python test_phase5_with_real_data.py
```

This will:
1. Load your `formtest_phase4_output.json`
2. Process it through Phase 5 (set splitting)
3. Display detailed results
4. Save output to `formtest_phase5_output.json`

## What the Test Does

### Test 1: Single Dataset Processing
- Takes the first case from your data
- Shows input analysis (flags, interrogatories)
- Splits into sets with max 120 interrogatories per set
- Displays each set with:
  - Set number
  - Interrogatory range
  - Active flags
  - Generated filename
- Validates:
  - Total interrogatory count
  - All sets within limit
  - Continuous numbering
  - All flags included
  - First-set-only flags handled correctly

### Test 2: All Document Types
- Processes SROGs, PODs, and Admissions for one case
- Shows how each document type is split
- Demonstrates the complete workflow

### Test 3: All Cases
- Processes all 4 cases × 3 document types = 12 datasets
- Shows summary statistics:
  - Total sets created
  - Average interrogatories per set
  - Breakdown by document type

## Sample Output

```
================================================================================
TEST 1: Single Dataset Processing
================================================================================

Processing: Clark Kent vs Tony Stark
Dataset ID: 1-VTSxIZ-t5dfqS-srogs

Input Analysis:
  Total flags: 192
  True flags: 191
  First-set-only flags: 3
  Expected total interrogatories: 1206
  Expected sets: ~11

SET BREAKDOWN
────────────────────────────────────────────────────────────────────────────────

  📄 Set 1 of 11
     Interrogatories: 1-100 (Total: 100)
     First Set: ✓ Yes
     Flags: 3 active
     → IsManager, SROGsGeneral, HasMold
     Filename: Clark Kent vs Tony Stark - Discovery Propounded SROGs Set 1 of 11

  📄 Set 2 of 11
     Interrogatories: 101-220 (Total: 120)
     First Set: ✗ No
     Flags: 6 active
     → HasAgeDiscrimination, HasLeaksInGarage, ...
     Filename: Clark Kent vs Tony Stark - Discovery Propounded SROGs Set 2 of 11

  ... (9 more sets)

VALIDATION
────────────────────────────────────────────────────────────────────────────────
  ✓ Total interrogatories match: 1206
  ✓ All sets ≤ 120 interrogatories (or first set)
  ✓ Interrogatory numbering is continuous
  ✓ All 191 true flags included
  ✓ First-set-only flags handled correctly
```

## Your Real Data Results

From your `formtest.json`, Phase 5 successfully processed:

- **4 cases** (plaintiff-defendant pairs)
- **12 datasets** (4 cases × 3 document types)
- **50 sets total** (because some cases exceeded 120 interrogatories)
- **5,206 total interrogatories**

### Breakdown by Document Type:

| Document Type | Datasets | Sets | Interrogatories | Avg per Set |
|--------------|----------|------|-----------------|-------------|
| SROGs        | 4        | 26   | 2,760          | 106.2       |
| PODs         | 4        | 16   | 1,654          | 103.4       |
| Admissions   | 4        | 8    | 792            | 99.0        |

### Example: Clark Kent vs Tony Stark

This case had **191 true flags** and **1,206 interrogatories**, which were split into:

- **SROGs**: 11 sets (1,206 interrogatories)
- **PODs**: 4 sets (414 interrogatories)
- **Admissions**: 3 sets (333 interrogatories)

Each set respects the 120-interrogatory limit and has a professional filename like:
```
Clark Kent vs Tony Stark - Discovery Propounded SROGs Set 1 of 11
```

## Output File Structure

The `formtest_phase5_output.json` contains:

```json
{
  "phase": 5,
  "description": "Set splitting output - ready for Phase 6 (document generation)",
  "total_datasets": 12,
  "datasets": [
    {
      "doc_type": "SROGs",
      "dataset_id": "1-VTSxIZ-t5dfqS-srogs",
      "plaintiff": {...},
      "defendant": {...},
      "case_metadata": {...},
      "template": "SROGsMaster.docx",
      "filename_suffix": "Discovery Propounded SROGs",
      "sets": [
        {
          "set_number": 1,
          "interrogatory_start": 1,
          "interrogatory_end": 100,
          "total_interrogatories": 100,
          "is_first_set": true,
          "flags": {
            "IsManager": true,
            "SROGsGeneral": true,
            "HasMold": true
          },
          "filename": "Clark Kent vs Tony Stark - Discovery Propounded SROGs Set 1 of 11"
        },
        // ... more sets
      ],
      "metadata": {
        "total_sets": 11,
        "total_interrogatories": 1206,
        "max_per_set": 120
      }
    },
    // ... more datasets
  ]
}
```

## Validations Performed

The test script validates that Phase 5:

1. ✅ **Preserves interrogatory counts** - Total in = Total out
2. ✅ **Respects 120-interrogatory limit** - Each set ≤ 120 (except when a single flag exceeds)
3. ✅ **Maintains continuous numbering** - No gaps (1-100, 101-220, etc.)
4. ✅ **Includes all true flags** - No flags lost or added
5. ✅ **Handles first-set-only flags** - Only in Set 1, never in subsequent sets
6. ✅ **Generates valid filenames** - Professional court-ready format

## Next Steps

This output (`formtest_phase5_output.json`) is now ready for **Phase 6: Output Generation**, which will:

1. Load Word document templates (`.docx` files)
2. For each set, populate the template with:
   - Plaintiff/defendant information
   - Case metadata
   - Interrogatories based on active flags
3. Save as separate Word documents with the generated filenames

## Modifying the Test

You can customize the test script:

```python
# Change max interrogatories per set
test_single_dataset(phase4_data, max_interrogatories=100)

# Test with different dataset
dataset = phase4_data['datasets'][1]['srogs']  # Second case
```

## Troubleshooting

### "File not found" error
Make sure `formtest_phase4_output.json` is in the same directory as the test script.

### "Module not found" error
Make sure you're running from the virtual environment:
```bash
source venv/bin/activate
python test_phase5_with_real_data.py
```

### Unexpected set counts
- Check the `interrogatory_counts` in your Phase 4 output
- Verify first-set-only flags are correctly identified
- Remember: sets can exceed 120 if a single flag has >120 interrogatories

## Understanding the Algorithm

Phase 5 uses a **seed-accumulate-split** algorithm:

1. **SEED**: Add first-set-only flags (SROGsGeneral, IsOwner, IsManager) to Set 1
2. **ACCUMULATE**: Sort remaining flags by size (descending) and greedily pack into sets
3. **SPLIT**: When adding a flag would exceed 120, start a new set
4. **ENRICH**: Add metadata (set numbers, interrogatory ranges, filenames)

This ensures:
- Optimal number of sets (minimizes total sets)
- First-set-only flags never repeat
- Professional, court-ready output

---

**Ready for Phase 6!** 🚀
