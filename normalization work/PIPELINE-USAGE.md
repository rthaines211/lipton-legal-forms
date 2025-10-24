# Pipeline Usage Guide

## Running formtest.json Through Phases 1-5

This guide explains how to run the complete normalization pipeline on `formtest.json`.

## Quick Start

```bash
cd "/Users/ryanhaines/Desktop/Test/normalization work"
source venv/bin/activate
python3 run_pipeline.py
```

## What Happens

The `run_pipeline.py` script will:

1. **Load** `formtest.json` from the current directory
2. **Run Phase 1** - Input Normalization
3. **Run Phase 2** - Dataset Builder (HoH × Defendant combinations)
4. **Run Phase 3** - Flag Processors (180+ boolean flags)
5. **Run Phase 4** - Document Profiles (SROGs, PODs, Admissions)
6. **Run Phase 5** - Set Splitting (max 120 interrogatories per set)
7. **Save output** from each phase to timestamped JSON files

## Output Files

After running, you'll see 5 output files with timestamps:

```
output_phase1_<timestamp>.json  - Normalized form data
output_phase2_<timestamp>.json  - HoH × Defendant datasets
output_phase3_<timestamp>.json  - Enriched datasets with 180+ flags
output_phase4_<timestamp>.json  - Profiled datasets (SROGs, PODs, Admissions)
output_phase5_<timestamp>.json  - Split sets with max 120 interrogatories
```

## Output File Details

### Phase 1 Output
- **Structure**: Case info, plaintiffs array, defendants array
- **Size**: ~9 KB
- **Contains**: Normalized and flattened form data

### Phase 2 Output
- **Structure**: Datasets array + metadata
- **Datasets**: 4 (2 HoH × 2 Defendants)
- **Size**: ~17 KB
- **Contains**: Cartesian product of HoH plaintiffs and defendants

### Phase 3 Output
- **Structure**: Datasets array + metadata
- **Datasets**: 4 enriched datasets
- **Size**: ~44 KB
- **Contains**: Each dataset with 199 boolean flags

### Phase 4 Output
- **Structure**: Datasets array + metadata
- **Datasets**: 4 original datasets, each containing 3 profiles (12 total)
- **Size**: ~213 KB
- **Contains**: SROGs, PODs, and Admissions profiles for each dataset

### Phase 5 Output
- **Structure**: Datasets array + metadata
- **Datasets**: 12 profile datasets (flattened from Phase 4)
- **Total Sets**: 44 sets across all datasets
- **Size**: ~71 KB
- **Contains**: Split sets with max 120 interrogatories, each with filename

## Example Output

```bash
======================================================================
  LEGAL DISCOVERY NORMALIZATION PIPELINE
  Phases 1-5: Complete Processing
======================================================================

✅ Phase 1 complete!
   - Plaintiffs: 3
   - Defendants: 2
   - Case ID: 1

✅ Phase 2 complete!
   - Total datasets: 4
   - HoH plaintiffs: 2
   - Defendants: 2
   - Non-HoH plaintiffs: 1

✅ Phase 3 complete!
   - Enriched datasets: 4
   - Sample true flags (first dataset): 198/199

✅ Phase 4 complete!
   - Original datasets: 4
   - Profile datasets: 12
   - Profiles applied: 3 (SROGs, PODs, Admissions)

✅ Phase 5 complete!
   - Profile datasets processed: 12
   - Total sets created: 44
```

## Viewing Output

To view any output file in a readable format:

```bash
# View Phase 1 output
python3 -m json.tool output_phase1_<timestamp>.json | less

# View Phase 5 metadata
python3 -c "import json; data = json.load(open('output_phase5_<timestamp>.json')); print(json.dumps(data['metadata'], indent=2))"

# Count sets in Phase 5
python3 -c "import json; data = json.load(open('output_phase5_<timestamp>.json')); print(f\"Total sets: {data['metadata']['total_sets']}\")"
```

## Troubleshooting

### Error: "No such file or directory: formtest.json"
**Solution**: Make sure you're running from the `normalization work` directory and `formtest.json` exists there.

```bash
cd "/Users/ryanhaines/Desktop/Test/normalization work"
ls formtest.json  # Should show the file
```

### Error: "ModuleNotFoundError"
**Solution**: Make sure the virtual environment is activated.

```bash
source venv/bin/activate
```

### Error: "No module named 'src.phase1'"
**Solution**: Make sure you're running from the correct directory.

```bash
cd "/Users/ryanhaines/Desktop/Test/normalization work"
pwd  # Should show .../normalization work
```

## Command Reference

```bash
# Run complete pipeline
python3 run_pipeline.py

# Make script executable (already done)
chmod +x run_pipeline.py

# Run as executable
./run_pipeline.py

# View help (script has docstrings)
python3 -c "import run_pipeline; help(run_pipeline)"
```

## Performance

Expected processing time: < 3 seconds

Actual results from formtest.json:
- Phase 1: < 100ms
- Phase 2: < 100ms
- Phase 3: < 500ms (25+ processors, 180+ flags)
- Phase 4: < 500ms (3 profiles × 4 datasets)
- Phase 5: < 500ms (12 datasets, 44 sets)

## Next Steps

After running the pipeline, the Phase 5 output is ready for:
- **Phase 6**: Output Generation (Zapier & Local formats)
- **Phase 7**: Integration with PostgreSQL database

## Notes

- The script creates timestamped files, so running it multiple times won't overwrite previous outputs
- Each phase's output is independent and can be inspected separately
- All files use UTF-8 encoding with pretty-printed JSON (indent=2)
- The pipeline includes error handling and will show helpful error messages if something fails

---

**Last Updated**: 2025-10-17
**Script Version**: 1.0
**Python Version**: 3.13+
