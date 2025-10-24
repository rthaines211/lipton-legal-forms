# Legal Discovery Data Normalization - Project Plan

![Status](https://img.shields.io/badge/status-planning-blue)
![Phases](https://img.shields.io/badge/phases-7-green)
![Estimated%20Duration](https://img.shields.io/badge/duration-4--7%20weeks-orange)

## Project Overview

Transform the legal form application output into a comprehensive discovery document generation system that produces California discovery documents (SROGs, PODs, and Admissions) with intelligent interrogatory splitting and flag-based processing.

## Quick Start

### For Project Managers
1. Read [00-OVERVIEW.md](00-OVERVIEW.md) for high-level project understanding
2. Review phase breakdown and timeline
3. Check testing strategy in [TESTING-STRATEGY.md](TESTING-STRATEGY.md)

### For Developers
1. Start with [PHASE-1-INPUT-NORMALIZATION.md](PHASE-1-INPUT-NORMALIZATION.md)
2. Follow phases sequentially
3. Write tests after each phase (see Testing Strategy)
4. Review integration requirements in [PHASE-7-INTEGRATION.md](PHASE-7-INTEGRATION.md)

## Project Structure

```
normalization work/
├── README.md                           ← You are here
├── 00-OVERVIEW.md                      ← Project overview & timeline
│
├── PHASE-1-INPUT-NORMALIZATION.md      ← Parse & normalize form JSON
├── PHASE-2-DATASET-BUILDER.md          ← Build HoH × Defendant datasets
├── PHASE-3-FLAG-PROCESSORS.md          ← Transform to 180+ flags
├── PHASE-4-DOCUMENT-PROFILES.md        ← Apply SROGs/PODs/Admissions profiles
├── PHASE-5-SET-SPLITTING.md            ← Split into sets (max 120 interrogatories)
├── PHASE-6-OUTPUT-GENERATION.md        ← Generate Zapier & Local outputs
├── PHASE-7-INTEGRATION.md              ← Database & API integration
│
└── TESTING-STRATEGY.md                 ← Comprehensive testing approach
```

## Phase Summary

| Phase | Name | Duration | Deliverables | Tests |
|-------|------|----------|--------------|-------|
| 1 | Input Normalization | 3-5 days | Parser, Flattener, Validator | 15+ |
| 2 | Dataset Builder | 2-3 days | HoH Filter, Cartesian Builder | 15+ |
| 3 | Flag Processors | 7-10 days | 25+ Processors, 180+ Flags | 75+ |
| 4 | Document Profiles | 3-4 days | SROGs, PODs, Admissions | 30+ |
| 5 | Set Splitting | 2-3 days | Splitting Algorithm | 20+ |
| 6 | Output Generation | 2-3 days | Zapier/Local Formatters | 20+ |
| 7 | Integration | 3-5 days | DB Schema, API, Bridge | 25+ |
| **Total** | **Full Pipeline** | **22-33 days** | **Complete System** | **200+** |

## Key Features

### Input Processing
- ✅ Normalize form JSON from `goalOutput.md` format
- ✅ Flatten nested discovery structures
- ✅ Validate required fields and data types

### Dataset Generation
- ✅ Filter Head of Household plaintiffs
- ✅ Build Cartesian product (HoH × Defendant)
- ✅ Ensure unit address idempotency

### Flag Processing
- ✅ Transform multi-select arrays to boolean flags
- ✅ Calculate aggregate flags (HasVermin, HasClogs, etc.)
- ✅ Case-insensitive matching
- ✅ 180+ total flags generated

### Document Profiles
- ✅ **SROGs**: Highest interrogatory counts, SROGsGeneral flag
- ✅ **PODs**: Medium counts, IsOwnerManager flag
- ✅ **Admissions**: Lower counts, geography flags, AdmissionsGeneral

### Set Splitting
- ✅ Max 120 interrogatories per set
- ✅ First-set-only flags (only in Set 1)
- ✅ Continuous interrogatory numbering
- ✅ Intelligent filename generation

### Output Formats
- ✅ **Zapier Mode**: Flat array for automation
- ✅ **Local Mode**: Nested structure for review
- ✅ JSON export with timestamps

## Data Flow

```
Form Submission (JSON)
         ↓
┌────────────────────┐
│ Phase 1: Normalize │ → Normalized structure
└────────────────────┘
         ↓
┌────────────────────┐
│ Phase 2: Datasets  │ → HoH × Defendant combinations
└────────────────────┘
         ↓
┌────────────────────┐
│ Phase 3: Flags     │ → 180+ boolean flags
└────────────────────┘
         ↓
┌────────────────────┐
│ Phase 4: Profiles  │ → SROGs, PODs, Admissions
└────────────────────┘
         ↓
┌────────────────────┐
│ Phase 5: Splitting │ → Sets with max 120 interrogatories
└────────────────────┘
         ↓
┌────────────────────┐
│ Phase 6: Output    │ → Zapier & Local JSON
└────────────────────┘
         ↓
┌────────────────────┐
│ Phase 7: Database  │ → PostgreSQL storage
└────────────────────┘
```

## Technology Stack

### Core Technologies
- **Python 3.10+**: Discovery processing pipeline
- **Node.js 18+**: Existing web server
- **PostgreSQL 14+**: Database storage
- **pytest**: Testing framework

### Key Libraries
- **Python**:
  - `pydantic`: Data validation
  - `pytest`: Testing
  - `hypothesis`: Property-based testing

- **JavaScript**:
  - `express`: Web server
  - `pg`: PostgreSQL client
  - `jest`: Testing

## Success Metrics

### Code Quality
- ✅ 200+ automated tests
- ✅ 95% code coverage
- ✅ Type hints on all functions
- ✅ Comprehensive documentation

### Performance
- ✅ Process case in < 5 seconds
- ✅ Phase 1-2 in < 500ms
- ✅ Phase 3-5 in < 3s
- ✅ Phase 6-7 in < 1s

### Data Integrity
- ✅ No data loss across phases
- ✅ All flags calculated correctly
- ✅ Set splitting algorithm verified
- ✅ Output matches specification exactly

## Getting Started

### 1. Review Requirements
```bash
# Read the overview
cat 00-OVERVIEW.md

# Understand the data model
cat ../data_model.md
```

### 2. Set Up Environment
```bash
# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (when available)
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### 3. Begin Phase 1
```bash
# Create Phase 1 directory structure
mkdir -p src/phase1
mkdir -p tests/phase1

# Read Phase 1 documentation
cat PHASE-1-INPUT-NORMALIZATION.md
```

### 4. Run Tests
```bash
# Run all tests
pytest

# Run specific phase
pytest tests/phase1/

# Run with coverage
pytest --cov=src --cov-report=html
```

## Development Workflow

### For Each Phase:

1. **Read Phase Documentation**
   - Understand inputs/outputs
   - Review task breakdown
   - Note test requirements

2. **Implement Core Logic**
   - Create module files
   - Implement functions
   - Add type hints and docstrings

3. **Write Tests**
   - Unit tests for each function
   - Integration tests for phase handoffs
   - Achieve 90%+ coverage

4. **Verify Exit Criteria**
   - All tests passing
   - Code coverage met
   - Documentation complete
   - Performance targets met

5. **Move to Next Phase**

## Common Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/phase3/test_vermin_processor.py

# Run with coverage report
pytest --cov=src --cov-report=html

# Run only fast tests
pytest -m "not slow"

# Run benchmarks
pytest -m benchmark

# Generate documentation
pydoc-markdown > docs/API.md
```

## Troubleshooting

### Issue: Tests failing after Phase 1
**Solution**: Verify Phase 1 output structure matches expected input for Phase 2

### Issue: Flag counts don't match
**Solution**: Check case-insensitive matching and aggregate flag calculation

### Issue: Set splitting creates sets > 120
**Solution**: Review accumulation phase logic and interrogatory count mappings

### Issue: Python-Node.js bridge not working
**Solution**: Check Python path, temp file permissions, and subprocess error handling

## Contributing

### Code Style
- **Python**: Follow PEP 8, use Black formatter
- **JavaScript**: Follow ESLint config
- **Tests**: Use descriptive names, follow AAA pattern

### Commit Messages
```
Phase 3: Implement VerminProcessor

- Add VerminProcessor class
- Implement 7 flag mappings
- Add HasVermin aggregate flag
- Include 12 unit tests
```

### Pull Request Checklist
- [ ] All tests pass locally
- [ ] Code coverage ≥ 90%
- [ ] Documentation updated
- [ ] Type hints added
- [ ] Docstrings complete

## Resources

### Related Documentation
- [Data Model Specification](../data_model.md)
- [Goal Output Format](../goalOutput.md)
- [Database Schema](../database/schema.sql)
- [Server Implementation](../server.js)

### External References
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)
- [PostgreSQL JSON Functions](https://www.postgresql.org/docs/current/functions-json.html)

## Project Status

### Current Phase: Planning
- [x] Overview created
- [x] All 7 phases documented
- [x] Testing strategy defined
- [ ] Phase 1 implementation started

### Next Steps
1. Set up Python environment
2. Create directory structure
3. Begin Phase 1 implementation
4. Write initial tests

## Contact & Support

For questions about this project:
- Review phase documentation first
- Check testing strategy
- Consult data model specification
- Review existing codebase ([server.js](../server.js))

---

**Project Start Date**: 2025-10-13
**Estimated Completion**: 4-7 weeks
**Total Phases**: 7
**Target Test Count**: 200+
**Target Coverage**: 95%

🎯 **Goal**: Transform legal form data into production-ready discovery documents with 180+ intelligent flags and document automation.
