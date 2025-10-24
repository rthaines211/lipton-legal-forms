# How to Verify Phase 5 Completion Using formtest.json

This guide explains how to confirm that Phase 5 (Set Splitting) is complete and working correctly using the [formtest.json](formtest.json) test data file.

## Quick Start

Simply run the verification script:

```bash
cd "/Users/ryanhaines/Desktop/Test/normalization work"
python3 verify_phase5.py
```

If Phase 5 is working correctly, you'll see:
```
🎉 PHASE 5 IS COMPLETE AND VERIFIED!
```

---

## What the Verification Script Does

The [verify_phase5.py](verify_phase5.py) script:

1. **Loads formtest.json** - Your comprehensive test dataset with 3 plaintiffs (Clark Kent, Lois Lane, Bruce Wayne) and 2 defendants

2. **Runs the Complete Pipeline (Phases 1-5)**:
   - **Phase 1**: Normalizes the raw form data into structured plaintiffs, defendants, and case info
   - **Phase 2**: Builds Cartesian product datasets (plaintiff × defendant combinations)
   - **Phase 3**: Processes discovery data into boolean flags
   - **Phase 4**: Creates document profiles (SROGs, PODs, Admissions) with interrogatory counts
   - **Phase 5**: Splits profiles into sets with ≤120 interrogatories each

3. **Verifies All Exit Criteria**:
   - ✅ No set exceeds 120 interrogatories
   - ✅ Interrogatory numbering is continuous (Set 1: 1-N, Set 2: N+1 to M, etc.)
   - ✅ First-set-only flags only appear in Set 1
   - ✅ All sets have properly formatted filenames
   - ✅ No flags are lost during splitting

4. **Provides Detailed Output** including:
   - Number of sets created per document type
   - Interrogatory ranges for each set (start-end)
   - Generated filenames for each set
   - Summary statistics (total sets, total interrogatories, averages)

---

## Understanding the Output

### Phase Breakdown

Each phase shows its progress:

```
PHASE 1: Input Normalization
✓ Normalized data
  - Plaintiffs: 3
  - Defendants: 2
```

### Phase 5 Output Example

For each plaintiff-defendant combination and document type, you'll see:

```
Plaintiff: Clark Kent
  - SROGS: 1206 interrogatories → 11 set(s)
    Set 1: Interrogatories 1-100 (100 total)
            File: Clark Kent vs Tony Stark - Discovery Propounded SROGs Set 1 of 11
    Set 2: Interrogatories 101-220 (120 total)
            File: Clark Kent vs Tony Stark - Discovery Propounded SROGs Set 2 of 11
    ...
```

This shows:
- **Total interrogatories**: 1206 (from Phase 4 profiling)
- **Number of sets**: 11 (because 1206 > 120, split is required)
- **Each set details**: Range, count, and filename

### Exit Criteria Verification

The script validates all 5 critical requirements:

```
PHASE 5 EXIT CRITERIA VERIFICATION

1. Checking max 120 interrogatories per set...
   ✓ PASSED: All sets have ≤ 120 interrogatories

2. Checking continuous interrogatory numbering...
   ✓ PASSED: Interrogatory numbering is continuous
```

### Summary Statistics

```
Total Sets Generated: 50
Total Interrogatories: 5206
Average Interrogatories per Set: 104.1
```

---

## What Gets Tested with formtest.json

The formtest.json file contains a realistic legal case scenario:

### Plaintiffs
1. **Clark Kent** (Adult, Head of Household, Unit 1)
   - **Full discovery data** with extensive issues:
     - Vermin: Rats/Mice, Skunks, Bats, Raccoons, Pigeons, Opossums
     - Insects: All types (Ants, Roaches, Flies, Bedbugs, etc.)
     - HVAC, Electrical, Fire Hazard, Plumbing, Structural issues
     - Harassment, Discrimination, Safety issues
   - **Result**: Generates large datasets requiring multiple sets

2. **Lois Lane** (Guardian, Head of Household, Unit 2)
   - **Partial discovery data**:
     - Vermin: Rats/Mice, Skunks, Raccoons, Pigeons
     - Insects: Flies, Hornets, Termites, Bees
     - Trash problems
   - **Result**: Generates smaller datasets (1-2 sets per document type)

3. **Bruce Wayne** (Adult, NOT Head of Household)
   - **No discovery data**
   - **Result**: Minimal interrogatories (only general/first-set-only flags)

### Defendants
1. **Tony Stark** (LLC, Manager)
2. **Steve Rogers** (LLC, Owner)

### Test Coverage

This creates **4 datasets** (2 plaintiffs with discovery × 2 defendants) and tests:

- ✅ **Large datasets** (Clark Kent): 1200+ interrogatories → 11 sets
- ✅ **Medium datasets** (Lois Lane): 170-180 interrogatories → 2 sets
- ✅ **Small datasets** (Lois Lane PODs/Admissions): <120 interrogatories → 1 set
- ✅ **First-set-only flags**: General SROGs, PODs, Admissions questions
- ✅ **Continuous numbering** across all set boundaries
- ✅ **Filename generation** with plaintiff/defendant names
- ✅ **All three document types**: SROGs, PODs, Admissions

---

## Expected Results

### Total Output

| Metric | Value |
|--------|-------|
| **Total Plaintiffs** | 3 |
| **Total Defendants** | 2 |
| **Total Datasets** | 4 (only plaintiffs with discovery) |
| **Total Sets** | 50 (across all doc types) |
| **Total Interrogatories** | 5,206 |
| **Average per Set** | ~104 interrogatories |

### Breakdown by Plaintiff

**Clark Kent** (Heavy discovery):
- SROGS: ~1,200 interrogatories → 11 sets
- PODs: ~730 interrogatories → 7 sets
- Admissions: ~333 interrogatories → 3 sets

**Lois Lane** (Light discovery):
- SROGS: ~170 interrogatories → 2 sets
- PODs: ~92-97 interrogatories → 1 set
- Admissions: ~63 interrogatories → 1 set

---

## Key Features Verified

### 1. Seed-Accumulate-Split Algorithm

The script confirms the three-phase algorithm works:

- **SEED Phase**: First-set-only flags (SROGsGeneral, PODsGeneral, etc.) are added to Set 1
- **ACCUMULATE Phase**: Remaining flags are greedily packed into sets using descending sort
- **ENRICH Phase**: Metadata (interrogatory ranges, set numbers, filenames) is added

### 2. Max 120 Interrogatories

Each set is validated to ensure it has ≤120 interrogatories:

```python
if count > 120:
    print(f"   ✗ FAILED: Set has {count} interrogatories")
    all_passed = False
```

### 3. Continuous Interrogatory Numbering

Verifies no gaps in numbering:

```python
expected_start = 1 if i == 0 else sets[i-1]['interrogatory_end'] + 1
if set_data['interrogatory_start'] != expected_start:
    # FAIL
```

### 4. First-Set-Only Flag Placement

Ensures first-set-only flags:
- ✅ ARE in Set 1
- ✅ ARE NOT in Sets 2, 3, 4, etc.

### 5. Filename Generation

Confirms filenames follow the pattern:
```
[Plaintiff] vs [Defendant] - [Suffix] Set [X] of [Y]
```

Example:
```
Clark Kent vs Tony Stark - Discovery Propounded SROGs Set 1 of 11
```

### 6. Data Integrity

Verifies no flags are lost during the splitting process.

---

## Interpreting Results

### Success

If all checks pass, you'll see:

```
============================================================
✅ PHASE 5 VERIFICATION COMPLETE: ALL CRITERIA PASSED
============================================================

🎉 PHASE 5 IS COMPLETE AND VERIFIED!
```

**Exit code**: 0

### Failure

If any check fails, you'll see:

```
============================================================
❌ PHASE 5 VERIFICATION FAILED: Some criteria not met
============================================================

⚠️  PHASE 5 HAS ISSUES - See failures above
```

**Exit code**: 1

The output will show specific failures like:

```
1. Checking max 120 interrogatories per set...
   ✗ FAILED: Clark Kent srogs Set 3 has 125 interrogatories
```

---

## Troubleshooting

### Script Fails to Run

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Make sure you're in the correct directory:
```bash
cd "/Users/ryanhaines/Desktop/Test/normalization work"
```

### Phase 1-4 Errors

If errors occur before Phase 5, check:
- formtest.json is present and valid
- All source modules (phase1-5) are installed correctly
- Run the unit tests for earlier phases:
  ```bash
  pytest tests/phase1/ -v
  pytest tests/phase2/ -v
  pytest tests/phase3/ -v
  pytest tests/phase4/ -v
  ```

### Phase 5 Exit Criteria Failures

If specific Phase 5 checks fail:

1. **Max 120 exceeded**: Check the `set_splitter.py` greedy packing logic
2. **Numbering gaps**: Check the `ENRICH` phase in `set_splitter.py`
3. **First-set-only in wrong sets**: Check the `SEED` phase logic
4. **Filename issues**: Check `filename_generator.py`

---

## Advanced Usage

### Run Unit Tests

To run Phase 5's 91 unit tests:

```bash
pytest tests/phase5/ -v --cov=src.phase5
```

Expected output:
```
============================== 91 passed in 0.36s ==============================

---------- coverage: platform darwin, python 3.13.7-final-0 ----------
Name                               Stmts   Miss  Cover
------------------------------------------------------
src/phase5/__init__.py                 4      0   100%
src/phase5/filename_generator.py       8      0   100%
src/phase5/set_splitter.py            40      0   100%
src/phase5/splitting_pipeline.py      35      0   100%
------------------------------------------------------
TOTAL                                 87      0   100%
```

### Verbose Output

For more debugging detail, modify the script to print intermediate data:

```python
# In verify_phase5.py
import json
print(json.dumps(split_data, indent=2))
```

### Custom Test Data

To test with your own data, replace `formtest.json` or create a new test file:

```python
# In verify_phase5.py
def load_formtest_data():
    formtest_path = Path(__file__).parent / "your_test_file.json"
    with open(formtest_path, 'r') as f:
        return json.load(f)
```

---

## What This Confirms

Running this verification successfully confirms:

✅ **Phase 5 Implementation is Complete**
- Set splitter algorithm works correctly
- Filename generator produces valid names
- Splitting pipeline orchestrates the process

✅ **All Exit Criteria Met**
- Max 120 interrogatories enforced
- Continuous interrogatory numbering
- First-set-only flags handled correctly
- Filenames properly formatted
- Data integrity maintained

✅ **Integration with Previous Phases**
- Phase 1 normalization → Phase 2 datasets → Phase 3 flags → Phase 4 profiles → Phase 5 splitting
- End-to-end pipeline works seamlessly

✅ **Ready for Phase 6**
- Output structure includes all necessary metadata
- Set data can be consumed by document generation
- Filenames ready for .docx file creation

---

## Next Steps

After confirming Phase 5 is complete:

1. **Review the Phase 5 Completion Summary**: [PHASE-5-COMPLETION-SUMMARY.md](PHASE-5-COMPLETION-SUMMARY.md)

2. **Understand the Phase 5 Architecture**: [src/phase5/README.md](src/phase5/README.md)

3. **Begin Phase 6**: Output Generation
   - Read Word document templates (.docx)
   - Populate templates with split set data
   - Generate final discovery documents
   - Save with generated filenames

4. **Integration Testing**: Test the complete end-to-end pipeline with multiple cases

---

## Summary

The `verify_phase5.py` script provides a **comprehensive, automated verification** that Phase 5 is complete and working correctly. By using the realistic `formtest.json` data, it tests:

- ✅ All algorithm phases (SEED, ACCUMULATE, ENRICH)
- ✅ All edge cases (large/small datasets, multiple defendants)
- ✅ All document types (SROGs, PODs, Admissions)
- ✅ All exit criteria (max 120, numbering, first-set-only flags, filenames, integrity)

**When you see** `🎉 PHASE 5 IS COMPLETE AND VERIFIED!`, you can be confident that Phase 5 is production-ready and ready for integration with Phase 6.

---

**Created**: October 17, 2025
**Script**: [verify_phase5.py](verify_phase5.py)
**Test Data**: [formtest.json](formtest.json)
**Phase 5 Docs**: [PHASE-5-COMPLETION-SUMMARY.md](PHASE-5-COMPLETION-SUMMARY.md)
