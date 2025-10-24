# Process Form Summary

## ✅ Complete Implementation

Your `process_form.py` script now provides:
- **Granular interrogatory counts broken down by Head of Household AND Defendant**
- **Automatic file output to "Processed Test/" folder** with organized JSON files

## Quick Usage

```bash
python3 process_form.py data/form-entry-XXXXX.json
```

This will automatically:
1. Process the form entry
2. Generate all interrogatory sets
3. Save individual set files to `Processed Test/` folder
4. Display detailed summary statistics

## Output Features

### 1. Input Information
- File name
- Form type
- Number of plaintiffs
- Number of defendants

### 2. File Output ⭐ NEW!
All JSON files are automatically saved to **"Processed Test/"** folder:
- **Set Files**: Individual files for each set (e.g., `ClarkKent_TonyStark_SROGs_set1.json`)
- **Master Files**: Complete documents with all sets (e.g., `Master_ClarkKent_TonyStark_SROGs.json`)
- **Organized naming**: `{Plaintiff}_{Defendant}_{DocType}_set{N}.json`

### 3. Processing Status
- Creates `data.json` for cleanjson.py
- Runs cleanjson.py with environment variables
- Outputs complete JSON to stdout
- Saves all files to organized folder

### 4. Overall Totals
Shows aggregate statistics across all documents:
- Number of documents (plaintiff-defendant pairs)
- Total sets
- Total interrogatories

### 5. Head of Household Breakdown
Detailed breakdown for each plaintiff marked as Head of Household:
- Sets per document type
- Interrogatory counts per document type
- Target defendants listed

### 6. Head of Household → Defendant Breakdown
Most granular breakdown showing each plaintiff vs each defendant:
- Exact set counts per plaintiff-defendant pair
- Exact interrogatory counts per plaintiff-defendant pair
- Broken down by document type (SROGs, PODs, Admissions)

## Example Output

```
📄 Processing: data/form-entry-1759853343822-3o1kbrqvi.json
📋 Form: Auto-Population Form
👥 Plaintiffs: 3
⚖️  Defendants: 2

✅ Created data.json
🔄 Running cleanjson.py...
[JSON output...]

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

## Environment Variables

Control processing behavior:

- `VERBOSE_OUTPUT=true` - Show detailed processing
- `WRITE_OUTPUT_FILES=true` - Write JSON files to disk
- `ONLY_PROFILES=SROGs` - Process specific document types only
- `MAX_Q=120` - Set maximum interrogatories per set

## Files Created

1. **[process_form.py](process_form.py)** - Main wrapper script with granular statistics
2. **[CLEANJSON_USAGE.md](CLEANJSON_USAGE.md)** - Complete documentation
3. **[run_cleanjson.py](run_cleanjson.py)** - Alternative helper script

## Understanding the Output

### Documents
Each "document" represents a **plaintiff-defendant pair**. If you have 2 head of households and 2 defendants, you get 4 documents per document type.

### Sets
Interrogatories are divided into **sets** based on the `MAX_Q` limit (default: 120). Each set contains up to MAX_Q interrogatories.

### Head of Household Breakdown
Shows interrogatory counts for each plaintiff who is the head of household, broken down by:
- Document type (SROGs, PODs, Admissions)
- Number of sets
- Total interrogatories
- Which defendants they're against

This helps you see exactly how many interrogatories each head of household has against each defendant.

## Tips

### Save JSON output only
```bash
python3 process_form.py data/form-entry-XXXXX.json 2>/dev/null | head -1 > output.json
```

### See only the summary
```bash
python3 process_form.py data/form-entry-XXXXX.json 2>&1 | grep -A 50 "Processing complete"
```

### Process with custom limits
```bash
MAX_Q=100 python3 process_form.py data/form-entry-XXXXX.json
```

---

**Last Updated:** 2025-01-07
