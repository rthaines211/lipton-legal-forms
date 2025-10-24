# Legal Discovery Data Normalization - Project Overview

## Project Goal
Transform the legal form application output into a structured discovery document generation system that produces California discovery documents (SROGs, PODs, and Admissions) based on the data model specification.

## Current State
- **Form Output**: JSON with `PlaintiffDetails[]`, `DefendantDetails2[]`, nested discovery objects
- **Database**: PostgreSQL schema with cases, parties, issues (normalized relational structure)
- **Server**: Node.js/Express with transformation logic in `server.js`

## Target State
- **Discovery Processor**: Python-based system that transforms form data into 180+ boolean flags
- **Dataset Generation**: Create HoH × Defendant cross-product datasets
- **Document Profiles**: Three separate profiles (SROGs, PODs, Admissions) with specific flag sets
- **Set Splitting**: Intelligent splitting into sets with max 120 interrogatories per set
- **Output Formats**: Both Zapier-mode (flattened) and Local-mode (nested) outputs

## Key Metrics
- **25+ Flag Processors**: Transform multi-select arrays into boolean flags
- **180+ Boolean Flags**: Comprehensive flag coverage across all issue categories
- **3 Document Types**: SROGs, PODs, Admissions
- **120 Max Interrogatories**: Per set splitting threshold
- **2 Output Modes**: Zapier and Local

## Project Structure
```
/normalization work/
├── 00-OVERVIEW.md                  # This file
├── PHASE-1-INPUT-NORMALIZATION.md  # Normalize form output
├── PHASE-2-DATASET-BUILDER.md      # Build HoH × Defendant datasets
├── PHASE-3-FLAG-PROCESSORS.md      # 25+ flag processor implementations
├── PHASE-4-DOCUMENT-PROFILES.md    # Profile-specific transformations
├── PHASE-5-SET-SPLITTING.md        # Set splitting algorithm
├── PHASE-6-OUTPUT-GENERATION.md    # Output formatting
├── PHASE-7-INTEGRATION.md          # Database & server integration
└── TESTING-STRATEGY.md             # Comprehensive testing approach
```

## Development Phases

### Phase 1: Input Normalization (3-5 days)
- Parse current form JSON output
- Flatten discovery data structures
- Validate and normalize field names
- **Exit Criteria**: All test cases pass normalization

### Phase 2: Dataset Builder (2-3 days)
- Implement HoH filtering logic
- Build Cartesian product (HoH × Defendant)
- Add case metadata to each dataset
- **Exit Criteria**: Correct number of datasets generated per case

### Phase 3: Flag Processors (7-10 days)
- Implement 25+ flag processors
- Handle multi-select → boolean transformations
- Calculate aggregate flags
- **Exit Criteria**: All 180+ flags generate correctly

### Phase 4: Document Profiles (3-4 days)
- Implement SROGs profile logic
- Implement PODs profile logic
- Implement Admissions profile logic
- **Exit Criteria**: Profile-specific flags apply correctly

### Phase 5: Set Splitting (2-3 days)
- Implement seed-accumulate-split algorithm
- Add set metadata (SetNumber, InterrogatoryStart, etc.)
- Handle first-set-only flags
- **Exit Criteria**: Sets split correctly with max 120 interrogatories

### Phase 6: Output Generation (2-3 days)
- Generate Zapier-mode output
- Generate Local-mode output
- Format filenames correctly
- **Exit Criteria**: Output matches expected structure

### Phase 7: Integration (3-5 days)
- Database schema updates
- Server endpoint integration
- End-to-end testing
- **Exit Criteria**: Full pipeline works from form submission to document generation

## Total Timeline
**Estimated: 22-33 days** (4-7 weeks)

## Success Criteria
1. ✅ All phase tests pass
2. ✅ Integration tests pass end-to-end
3. ✅ Performance: Process case in < 5 seconds
4. ✅ Output matches data model specification exactly
5. ✅ Documentation complete for all phases

## Dependencies
- Python 3.10+ (for discovery processor)
- Node.js 18+ (existing server)
- PostgreSQL 14+ (existing database)
- pytest (for testing)

## Next Steps
1. Review this overview with team
2. Begin Phase 1: Input Normalization
3. Set up testing infrastructure
4. Create sample test data based on existing form outputs

---

**Document Version**: 1.0
**Last Updated**: 2025-10-13
**Owner**: Development Team
