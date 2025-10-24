# Using cleanjson.py with Form Entries

## Overview
`cleanjson.py` processes form entry JSON files and generates structured datasets for legal discovery documents (SROGs, PODs, and Admissions).

## Quick Start

### Method 1: Using process_form.py (Recommended)
```bash
python3 process_form.py data/form-entry-1759853343822-3o1kbrqvi.json
```

This wrapper script:
- Reads your form entry JSON
- Creates `data.json` for processing
- Runs `cleanjson.py` automatically
- Shows progress and interrogatory counts
- Outputs the JSON result to stdout

**Example Output:**
```
📄 Processing: data/form-entry-1759853343822-3o1kbrqvi.json
📋 Form: Auto-Population Form
👥 Plaintiffs: 3
⚖️  Defendants: 2

✅ Created data.json
🔄 Running cleanjson.py...
[JSON output here...]

✅ Processing complete!

📊 Summary:

📋 Overall Totals:
   SROGs: 4 documents, 24 sets, 2582 total interrogatories
   PODs: 4 documents, 14 sets, 1572 total interrogatories
   Admissions: 4 documents, 8 sets, 748 total interrogatories

👥 Breakdown by Head of Household:

   Clark Kent:
      SROGs: 20 sets, 2248 interrogatories
         vs Tony Stark, Steve Rogers
      PODs: 12 sets, 1393 interrogatories
         vs Tony Stark, Steve Rogers
      Admissions: 6 sets, 654 interrogatories
         vs Tony Stark, Steve Rogers

   Lois Lane:
      SROGs: 4 sets, 334 interrogatories
         vs Tony Stark, Steve Rogers
      PODs: 2 sets, 179 interrogatories
         vs Tony Stark, Steve Rogers
      Admissions: 2 sets, 94 interrogatories
         vs Tony Stark, Steve Rogers

⚖️  Breakdown by Head of Household → Defendant:

   Clark Kent:
      vs Steve Rogers:
         SROGs: 10 sets, 1125 interrogatories
         PODs: 6 sets, 699 interrogatories
         Admissions: 3 sets, 327 interrogatories
      vs Tony Stark:
         SROGs: 10 sets, 1123 interrogatories
         PODs: 6 sets, 694 interrogatories
         Admissions: 3 sets, 327 interrogatories

   Lois Lane:
      vs Steve Rogers:
         SROGs: 2 sets, 168 interrogatories
         PODs: 1 set, 92 interrogatories
         Admissions: 1 set, 47 interrogatories
      vs Tony Stark:
         SROGs: 2 sets, 166 interrogatories
         PODs: 1 set, 87 interrogatories
         Admissions: 1 set, 47 interrogatories
```

### Method 2: Direct execution
```bash
# Create data.json from your form entry
cp data/form-entry-XXXXX.json data.json

# Run cleanjson.py
python3 cleanjson.py
```

## Environment Variables

Control behavior with environment variables:

### VERBOSE_OUTPUT
Show detailed processing information:
```bash
VERBOSE_OUTPUT=true python3 process_form.py data/form-entry-XXXXX.json
```

### WRITE_OUTPUT_FILES
Write intermediate JSON files to disk:
```bash
WRITE_OUTPUT_FILES=true python3 process_form.py data/form-entry-XXXXX.json
```

This creates:
- `Master_<plaintiff>_<defendant>_<doctype>.json` - Master datasets
- `<plaintiff>_<defendant>_<doctype>_setN.json` - Individual sets

### ONLY_PROFILES
Process only specific document types:
```bash
# Only SROGs
ONLY_PROFILES=SROGs python3 process_form.py data/form-entry-XXXXX.json

# Only PODs and Admissions
ONLY_PROFILES="PODs,Admissions" python3 process_form.py data/form-entry-XXXXX.json
```

Available profiles:
- `SROGs` - Special Interrogatories
- `PODs` - Requests for Production of Documents
- `Admissions` - Requests for Admissions

### MAX_Q
Set maximum interrogatories per set (default: 120):
```bash
MAX_Q=100 python3 process_form.py data/form-entry-XXXXX.json
```

## Combined Examples

### Full verbose output with file writing
```bash
VERBOSE_OUTPUT=true WRITE_OUTPUT_FILES=true python3 process_form.py data/form-entry-XXXXX.json
```

### Process only SROGs with verbose output
```bash
VERBOSE_OUTPUT=true ONLY_PROFILES=SROGs python3 process_form.py data/form-entry-XXXXX.json
```

### Custom interrogatory limit with files
```bash
WRITE_OUTPUT_FILES=true MAX_Q=100 python3 process_form.py data/form-entry-XXXXX.json
```

## Output Format

The script outputs JSON to stdout containing:

### For local execution (non-Zapier):
```json
{
  "documents": [...],           // Document metadata
  "all_sets": [...],            // All sets for all documents
  "HeadOfHouseholds": [...],    // List of plaintiff names
  "Defendants": [...],          // List of defendant names
  "Plaintiff1Name": "...",      // Primary plaintiff
  "Street Address": "..."       // Property address
}
```

### For Zapier execution:
```json
{
  "all_sets": [...],            // All sets with custom_text field
  "HeadOfHouseholds": [...],    // List of plaintiff names
  "Defendants": [...],          // List of defendant names
  "Plaintiff1Name": "...",      // Primary plaintiff
  "Street Address": "..."       // Property address
}
```

Each set in `all_sets` contains:
- `DocType` - Document type (SROGs, PODs, Admissions)
- `Template` - Template filename
- `FileName` - Generated filename for the document
- `HeadOfHousehold` - Plaintiff name
- `TargetDefendant` - Defendant name
- `SetEnd` - Last interrogatory number
- `InterrogatoryCount` - Total interrogatories in set
- `sets_custom_text` - JSON string with full dataset

## Processing Logic

1. **Input Normalization**: Converts form entry JSON to normalized structure
2. **Dataset Preparation**: Creates datasets for each head of household × defendant pair
3. **Flag Generation**: Adds boolean flags for all discovery issues
4. **Set Splitting**: Divides interrogatories into sets based on MAX_Q limit
5. **Output Generation**: Creates structured output for Zapier or local use

## Common Use Cases

### Test form entry processing
```bash
python3 process_form.py data/form-entry-1759853343822-3o1kbrqvi.json | jq '.HeadOfHouseholds'
```

### Save output to file
```bash
python3 process_form.py data/form-entry-XXXXX.json > output.json
```

### Debug with verbose output
```bash
VERBOSE_OUTPUT=true python3 process_form.py data/form-entry-XXXXX.json 2>&1 | tee debug.log
```

### Generate only SROGs files
```bash
WRITE_OUTPUT_FILES=true ONLY_PROFILES=SROGs python3 process_form.py data/form-entry-XXXXX.json
```

## Troubleshooting

### "File not found" error
Make sure the file path is correct relative to your current directory:
```bash
ls data/form-entry-*.json  # List available files
```

### Empty output
Check that your form entry has required fields:
- `PlaintiffDetails` array
- `DefendantDetails2` array
- `Full_Address` object

### Python not found
Use `python3` instead of `python`:
```bash
python3 process_form.py ...
```

## File Structure

After running with `WRITE_OUTPUT_FILES=true`, you'll see:
```
Master_ClarkKent_TonyStark_SROGs.json
Master_ClarkKent_TonyStark_PODs.json
Master_ClarkKent_TonyStark_Admissions.json
ClarkKent_TonyStark_SROGs_set1.json
ClarkKent_TonyStark_SROGs_set2.json
...
```

Each set file is ready for use with document generation templates.
