# Test-Driven Development Guide for Lipton Webserver API

This guide provides comprehensive information on the TDD practices implemented for the Lipton Webserver API, following principles from the TDD Orchestrator.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Writing Tests](#writing-tests)
5. [Test Patterns](#test-patterns)
6. [Continuous Integration](#continuous-integration)
7. [Best Practices](#best-practices)

## Overview

### Test Philosophy

Our testing approach follows the **red-green-refactor** cycle:

1. **🔴 Red**: Write a failing test first
2. **🟢 Green**: Write minimal code to make it pass
3. **🔵 Refactor**: Improve code while keeping tests green

### Test Pyramid

We maintain a balanced test suite following the test pyramid:

```
        /\
       /E2E\      <- Few end-to-end tests (Playwright)
      /------\
     /  API  \    <- Moderate integration tests
    /--------\
   /   UNIT   \   <- Many unit tests (fast, isolated)
  /------------\
```

- **Unit Tests**: 70% - Fast, isolated, test individual functions
- **Integration Tests**: 25% - Test API endpoints with database
- **E2E Tests**: 5% - Full system tests (Playwright)

## Test Structure

```
api/tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared fixtures and configuration
├── test_etl_service.py      # Unit tests for ETL service
├── test_api_endpoints.py    # Integration tests for API endpoints
├── test_models.py           # Unit tests for Pydantic models
└── README.md                # This file
```

### Test Organization

Tests are organized by:

1. **Type**: Unit tests vs Integration tests
2. **Module**: Each source module has corresponding test file
3. **Markers**: `@pytest.mark` for categorization

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest api/tests/test_etl_service.py

# Run specific test
pytest api/tests/test_etl_service.py::TestFormETLService::test_insert_case_with_full_address

# Run with coverage report
pytest --cov=api --cov-report=html
```

### Test Markers

Run specific test categories:

```bash
# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run critical path tests
pytest -m critical

# Run smoke tests
pytest -m smoke

# Exclude slow tests
pytest -m "not slow"
```

### Coverage

```bash
# Generate coverage report
pytest --cov=api --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=api --cov-report=html

# Open coverage report in browser
open htmlcov/index.html
```

### Continuous Testing

For development, use watch mode:

```bash
# Install pytest-watch
pip install pytest-watch

# Run tests on file changes
ptw -- -v
```

## Writing Tests

### Test Structure: AAA Pattern

All tests follow the **Arrange-Act-Assert** pattern:

```python
def test_example():
    # Arrange: Set up test data and preconditions
    service = FormETLService()
    form_data = create_test_form()
    
    # Act: Execute the code being tested
    result = service.ingest_form_submission(form_data)
    
    # Assert: Verify the outcome
    assert result["case_id"] is not None
    assert result["plaintiff_count"] == 1
```

### Naming Conventions

Test names should be descriptive and follow this pattern:

```python
def test_[unit_under_test]_[scenario]_[expected_behavior]:
    pass

# Examples:
def test_insert_case_with_full_address():
    """Test inserting a case with complete address information"""
    pass

def test_submit_form_without_plaintiffs_returns_error():
    """Test submitting form without plaintiffs returns 400"""
    pass
```

### Using Fixtures

Leverage fixtures from `conftest.py`:

```python
def test_with_fixtures(
    db_connection,
    form_submission_factory,
    plaintiff_factory
):
    # Use factories to create test data
    plaintiff = plaintiff_factory(
        item_number=1,
        name=plaintiff_name_factory(first="John", last="Doe")
    )
    
    form_data = form_submission_factory(plaintiffs=[plaintiff])
    
    # Test logic here
```

### Test Isolation

Each test should be independent:

```python
@pytest.fixture
def db_connection(db_pool):
    """Each test gets a fresh transaction that's rolled back"""
    conn = get_db_connection()
    conn.autocommit = False
    cursor = conn.cursor()
    cursor.execute("BEGIN")
    
    yield conn
    
    # Rollback ensures no test data persists
    cursor.execute("ROLLBACK")
    cursor.close()
    conn.close()
```

## Test Patterns

### Unit Test Pattern

```python
@pytest.mark.unit
class TestETLService:
    """Test suite for ETL service unit tests"""
    
    def test_specific_behavior(self, db_connection):
        # Arrange
        service = FormETLService()
        
        # Act
        result = service.some_method()
        
        # Assert
        assert result is not None
```

### Integration Test Pattern

```python
@pytest.mark.integration
class TestAPIEndpoints:
    """Test suite for API endpoint integration tests"""
    
    def test_complete_flow(self, client: TestClient, sample_form_data):
        # Arrange
        # sample_form_data from fixture
        
        # Act
        response = client.post("/api/form-submissions", json=sample_form_data)
        
        # Assert
        assert response.status_code == 201
        assert "case_id" in response.json()
```

### Error Handling Pattern

```python
def test_handles_error_gracefully(self):
    # Arrange
    invalid_data = create_invalid_data()
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        service.process(invalid_data)
    
    assert exc_info.value.status_code == 400
    assert "error message" in str(exc_info.value.detail)
```

### Parameterized Testing

Test multiple scenarios efficiently:

```python
@pytest.mark.parametrize("input,expected", [
    ("CA", "CA"),
    ("California", "Ca"),
    ("ca", "ca"),
])
def test_state_code_normalization(input, expected):
    # Arrange
    form = create_form(state=input)
    
    # Act
    result = normalize_state(form)
    
    # Assert
    assert result == expected
```

## Continuous Integration

### Pre-commit Checks

Before committing code:

```bash
# Run all tests
pytest

# Check coverage (should be > 80%)
pytest --cov=api --cov-report=term

# Run linting
flake8 api/
black api/ --check
mypy api/
```

### CI Pipeline

Our CI pipeline runs:

1. **Lint**: Code quality checks
2. **Unit Tests**: Fast isolated tests
3. **Integration Tests**: API and database tests
4. **Coverage**: Ensure >80% coverage
5. **E2E Tests**: Playwright tests

### GitHub Actions Example

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: pytest --cov=api --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Best Practices

### 1. Test Independence

✅ **DO**: Each test should run independently

```python
def test_creates_case(self, db_connection, form_factory):
    form = form_factory()  # Fresh data each test
    result = service.create_case(form)
    assert result is not None
```

❌ **DON'T**: Share state between tests

```python
# Bad - tests depend on order
class TestSuite:
    case_id = None
    
    def test_create(self):
        self.case_id = service.create_case()
    
    def test_update(self):
        service.update_case(self.case_id)  # Fails if test_create didn't run
```

### 2. Clear Test Names

✅ **DO**: Descriptive names that explain behavior

```python
def test_submit_form_without_plaintiffs_returns_400_error():
    pass

def test_insert_case_with_missing_address_uses_defaults():
    pass
```

❌ **DON'T**: Generic or unclear names

```python
def test_case():
    pass

def test_1():
    pass
```

### 3. Single Responsibility

✅ **DO**: Test one thing at a time

```python
def test_insert_case_creates_database_record():
    """Test only that case is created"""
    case_id = service.insert_case(form)
    assert case_id is not None

def test_insert_case_stores_correct_address():
    """Test only address storage"""
    case_id = service.insert_case(form)
    case = db.get_case(case_id)
    assert case.address == form.address
```

❌ **DON'T**: Test multiple behaviors in one test

```python
def test_everything():
    """This tests too much"""
    case_id = service.insert_case(form)
    assert case_id is not None
    assert case.address == form.address
    assert case.parties == form.parties
    # ... 20 more assertions
```

### 4. Use Factories

✅ **DO**: Use factories for flexible test data

```python
def test_with_factory(plaintiff_factory):
    # Easy to customize
    plaintiff = plaintiff_factory(
        name="John Doe",
        age_category="adult"
    )
```

❌ **DON'T**: Hardcode test data everywhere

```python
def test_without_factory():
    plaintiff = {
        "ItemNumber": 1,
        "PlaintiffItemNumberName": {
            "First": "John",
            "Last": "Doe",
            # ... 20 more fields
        }
    }
```

### 5. Test Edge Cases

Always test:

- ✅ Happy path (normal case)
- ✅ Edge cases (empty, null, boundary values)
- ✅ Error cases (invalid input, exceptions)
- ✅ Boundary conditions

```python
@pytest.mark.parametrize("input,expected", [
    ([], 0),           # Empty
    ([1], 1),          # Single item
    ([1, 2, 3], 3),    # Multiple items
    (None, 0),         # Null
])
def test_count_items_handles_all_cases(input, expected):
    result = count_items(input)
    assert result == expected
```

### 6. Mock External Dependencies

✅ **DO**: Mock external services

```python
@patch('api.external_service.call_api')
def test_handles_api_failure(mock_api):
    mock_api.side_effect = ConnectionError()
    
    result = service.process_with_api()
    
    assert result["error"] is not None
```

### 7. Readable Assertions

✅ **DO**: Use clear, specific assertions

```python
assert response.status_code == 201
assert "case_id" in response.json()
assert UUID(response.json()["case_id"])  # Validates UUID format
```

❌ **DON'T**: Vague or complex assertions

```python
assert response  # What does this test?
assert len(str(response.json()["case_id"])) == 36  # Unclear intent
```

## Performance Metrics

Track these metrics:

- **Test Execution Time**: Unit tests < 0.1s, Integration < 1s
- **Test Coverage**: Target > 80%, Critical paths > 95%
- **Test Count**: Grow with codebase
- **Flaky Tests**: Should be 0
- **Test Maintenance Cost**: Monitor time spent fixing tests

## Troubleshooting

### Common Issues

**Issue**: Tests pass locally but fail in CI

**Solution**: Check for:
- Environment differences
- Timing issues (add appropriate waits)
- Database state dependencies

**Issue**: Slow tests

**Solution**:
- Use `pytest -m "not slow"` to skip slow tests
- Optimize database fixtures
- Mock external services

**Issue**: Flaky tests

**Solution**:
- Ensure test isolation
- Fix timing issues
- Remove shared state

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Test Pyramid by Martin Fowler](https://martinfowler.com/articles/practical-test-pyramid.html)
- [TDD by Example - Kent Beck](https://www.oreilly.com/library/view/test-driven-development/0321146530/)

## Contributing

When adding new features:

1. ✅ Write tests first (red)
2. ✅ Implement feature (green)
3. ✅ Refactor (blue)
4. ✅ Ensure coverage > 80%
5. ✅ Update documentation

---

**Remember**: Good tests are an investment in code quality and team velocity. Write tests you'd want to debug at 2 AM.

