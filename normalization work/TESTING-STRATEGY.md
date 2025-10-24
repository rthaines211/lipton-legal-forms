# Testing Strategy - Legal Discovery Data Normalization

## Overview
Comprehensive testing strategy ensuring data integrity, correctness, and performance across all seven phases of the discovery processing pipeline.

## Testing Pyramid

```
                    ▲
                   ╱ ╲
                  ╱   ╲
                 ╱ E2E ╲          (5% - End-to-end tests)
                ╱───────╲
               ╱ Integr. ╲        (15% - Integration tests)
              ╱───────────╲
             ╱             ╲
            ╱     Unit      ╲     (80% - Unit tests)
           ╱─────────────────╲
```

## Testing Layers

### Layer 1: Unit Tests (80%)
**Target**: 300+ unit tests across all phases

#### Phase-by-Phase Breakdown
- **Phase 1**: 15 tests (parsing, flattening, validation)
- **Phase 2**: 15 tests (HoH filtering, Cartesian product, addresses)
- **Phase 3**: 75 tests (25+ processors × 3 tests each)
- **Phase 4**: 30 tests (3 profiles × 10 tests each)
- **Phase 5**: 20 tests (splitting algorithm, numbering, filenames)
- **Phase 6**: 20 tests (Zapier, Local, export)
- **Phase 7**: 25 tests (integration, database, API)

#### Test Coverage Requirements
- **Minimum**: 90% code coverage
- **Target**: 95% code coverage
- **Critical paths**: 100% coverage

### Layer 2: Integration Tests (15%)
**Target**: 50+ integration tests

#### Test Categories
1. **Phase-to-Phase Integration** (20 tests)
   - Phase 1 → Phase 2 handoff
   - Phase 2 → Phase 3 handoff
   - Phase 3 → Phase 4 handoff
   - Phase 4 → Phase 5 handoff
   - Phase 5 → Phase 6 handoff

2. **Database Integration** (15 tests)
   - Save/retrieve datasets
   - Save/retrieve sets
   - Transaction integrity
   - Query performance

3. **External System Integration** (15 tests)
   - Python-Node.js bridge
   - File system operations
   - Subprocess management

### Layer 3: End-to-End Tests (5%)
**Target**: 15+ end-to-end tests

#### Test Scenarios
1. **Happy Path** (5 tests)
   - Simple case (1 HoH, 1 defendant)
   - Complex case (3 HoH, 2 defendants)
   - Full discovery (all arrays populated)
   - Minimal discovery (empty arrays)
   - Mixed discovery (some arrays populated)

2. **Edge Cases** (5 tests)
   - Maximum plaintiffs (10 HoH)
   - Maximum defendants (10)
   - Maximum interrogatories (requiring many sets)
   - Special characters in names/addresses
   - Different filing locations

3. **Error Scenarios** (5 tests)
   - Invalid input data
   - Missing required fields
   - Database connection failure
   - Python process failure
   - Timeout scenarios

## Test Data Management

### Test Fixtures
**Location**: `tests/fixtures/`

```
tests/fixtures/
├── phase1_samples.py       # Normalized form data
├── phase2_samples.py       # Datasets
├── phase3_samples.py       # Enriched datasets
├── phase4_samples.py       # Profile datasets
├── phase5_samples.py       # Split sets
├── phase6_samples.py       # Output formats
└── goaloutput_examples.py  # Real-world examples
```

### Test Data Categories
1. **Minimal Cases**: Bare minimum required data
2. **Full Cases**: All fields populated
3. **Edge Cases**: Boundary conditions
4. **Error Cases**: Invalid/malformed data

## Testing Tools & Framework

### Python Testing Stack
```python
# requirements-test.txt
pytest==7.4.0              # Test framework
pytest-cov==4.1.0          # Coverage reporting
pytest-asyncio==0.21.0     # Async test support
pytest-mock==3.11.1        # Mocking support
pytest-benchmark==4.0.0    # Performance testing
faker==19.3.0              # Test data generation
hypothesis==6.82.0         # Property-based testing
```

### JavaScript Testing Stack
```json
{
  "devDependencies": {
    "jest": "^29.6.0",
    "supertest": "^6.3.3",
    "jest-extended": "^4.0.0"
  }
}
```

### Configuration Files

#### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=90
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow-running tests
```

## Test Execution Strategy

### Local Development
```bash
# Run all tests
pytest

# Run specific phase
pytest tests/phase1/

# Run specific test file
pytest tests/phase3/test_vermin_processor.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run only fast tests
pytest -m "not slow"
```

### Continuous Integration
```yaml
# .github/workflows/test.yml
name: Test Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run unit tests
        run: pytest -m unit

      - name: Run integration tests
        run: pytest -m integration

      - name: Run E2E tests
        run: pytest -m e2e

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Performance Testing

### Benchmarks
**Target Performance Metrics**:

| Metric | Target | Maximum |
|--------|--------|---------|
| Phase 1: Normalize | < 100ms | < 200ms |
| Phase 2: Build datasets | < 200ms | < 500ms |
| Phase 3: Generate flags | < 1s | < 2s |
| Phase 4: Apply profiles | < 500ms | < 1s |
| Phase 5: Split sets | < 500ms | < 1s |
| Phase 6: Generate output | < 200ms | < 500ms |
| **Total pipeline** | **< 3s** | **< 5s** |

### Benchmark Tests
**File**: `tests/performance/test_benchmarks.py`

```python
import pytest

@pytest.mark.benchmark
def test_phase1_performance(benchmark):
    """Benchmark Phase 1 normalization"""
    form_json = load_large_form_json()

    result = benchmark(normalize_form_data, form_json)

    # Assert performance target
    assert benchmark.stats['mean'] < 0.1  # 100ms

@pytest.mark.benchmark
def test_full_pipeline_performance(benchmark):
    """Benchmark complete pipeline"""
    form_json = load_large_form_json()

    result = benchmark(process_form_submission, form_json)

    # Assert performance target
    assert benchmark.stats['mean'] < 3.0  # 3 seconds
```

## Data Integrity Testing

### Property-Based Testing
Use Hypothesis for property-based testing to discover edge cases.

**File**: `tests/property/test_invariants.py`

```python
from hypothesis import given, strategies as st

@given(st.lists(st.text(min_size=1), min_size=1))
def test_vermin_flags_match_input(vermin_list):
    """Property: Output flags should match input vermin list"""
    discovery_data = {'vermin': vermin_list}
    processor = VerminProcessor()

    flags = processor.process(discovery_data)

    # Property: HasVermin should be True if any vermin present
    assert flags['HasVermin'] == (len(vermin_list) > 0)

@given(st.integers(min_value=1, max_value=10))
def test_dataset_count_property(num_hoh, num_defendants):
    """Property: Dataset count = HoH count × Defendant count"""
    plaintiffs = create_plaintiffs(num_hoh, hoh=True)
    defendants = create_defendants(num_defendants)

    datasets = build_cartesian_product(plaintiffs, defendants, {})

    assert len(datasets) == num_hoh * num_defendants
```

## Regression Testing

### Golden Files
Maintain "golden" output files for regression detection.

**Directory**: `tests/golden/`

```
tests/golden/
├── goaloutput_example_output.json    # Expected output
├── simple_case_output.json
└── complex_case_output.json
```

**Test Implementation**:
```python
def test_regression_goaloutput_example():
    """Regression test against golden output"""
    form_json = load_fixture('goaloutput_example.json')
    golden_output = load_fixture('golden/goaloutput_example_output.json')

    result = process_form_submission(form_json)

    # Compare against golden file
    assert_json_equal(result['output'], golden_output)
```

## Test Reporting

### Coverage Reports
- **HTML Report**: `htmlcov/index.html`
- **Terminal Report**: Displayed after each test run
- **CI Integration**: Uploaded to Codecov

### Test Execution Report
```
================= test session starts =================
platform darwin -- Python 3.10.0
plugins: pytest-cov-4.1.0

tests/phase1/test_normalizer.py ............   [12/300]
tests/phase2/test_dataset_builder.py ....     [16/300]
tests/phase3/test_vermin_processor.py ...     [19/300]
...

================= 300 passed in 45.23s ================

---------- coverage: platform darwin ----------
Name                                 Stmts   Miss  Cover
--------------------------------------------------------
src/phase1/normalizer.py              145      5    97%
src/phase2/dataset_builder.py         120      3    98%
src/phase3/processors/vermin.py        45      0   100%
...
--------------------------------------------------------
TOTAL                                 2341     89    96%
```

## Testing Checklist

### Before Each Phase Completion
- [ ] All unit tests pass
- [ ] Code coverage ≥ 90%
- [ ] Integration tests with previous phase pass
- [ ] Documentation updated
- [ ] Performance benchmarks met

### Before Final Integration
- [ ] All 300+ unit tests pass
- [ ] All 50+ integration tests pass
- [ ] All 15+ E2E tests pass
- [ ] Overall coverage ≥ 95%
- [ ] All benchmarks within targets
- [ ] Regression tests pass
- [ ] Manual testing completed

### Production Readiness
- [ ] All tests passing in CI
- [ ] Security audit completed
- [ ] Load testing completed
- [ ] Monitoring configured
- [ ] Rollback plan tested

## Common Testing Patterns

### Test Structure (AAA Pattern)
```python
def test_example():
    # Arrange - Set up test data
    processor = VerminProcessor()
    discovery_data = {'vermin': ['Rats/Mice']}

    # Act - Execute the code
    flags = processor.process(discovery_data)

    # Assert - Verify results
    assert flags['HasRatsMice'] == True
```

### Parameterized Tests
```python
@pytest.mark.parametrize("input,expected", [
    (['Rats/Mice'], {'HasRatsMice': True}),
    (['Bedbugs'], {'HasBedbugs': True}),
    ([], {'HasVermin': False}),
])
def test_vermin_variations(input, expected):
    processor = VerminProcessor()
    flags = processor.process({'vermin': input})

    for key, value in expected.items():
        assert flags[key] == value
```

### Mock External Dependencies
```python
@pytest.fixture
def mock_database():
    """Mock database connection"""
    with patch('psycopg2.connect') as mock:
        yield mock

def test_save_to_database(mock_database):
    """Test database save with mocked connection"""
    # Test implementation
```

## Continuous Testing

### Pre-commit Hooks
```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest tests/
        language: system
        pass_filenames: false
        always_run: true
```

### CI/CD Pipeline
1. **On every push**: Run unit tests
2. **On pull request**: Run all tests
3. **Before merge**: Require 100% test pass rate
4. **On deploy**: Run E2E tests in staging

---

**Document Version**: 1.0
**Last Updated**: 2025-10-13
**Testing Coverage Target**: 95%
**Total Test Count Target**: 365+ tests
