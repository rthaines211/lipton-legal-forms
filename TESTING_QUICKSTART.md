# Testing Quick Start Guide

## 🚀 Get Started in 60 Seconds

### 1. Install Testing Dependencies

```bash
# Install Python test dependencies
pip install -r requirements.txt

# Verify installation
pytest --version
```

### 2. Run Your First Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run only unit tests (fast)
pytest -m unit
```

### 3. Check Coverage

```bash
# Generate coverage report
pytest --cov=api --cov-report=html

# Open report in browser
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

## 📚 Common Commands

### Using Make (Recommended)

```bash
make test              # Run all tests
make test-unit         # Run unit tests only
make test-integration  # Run integration tests only
make test-cov          # Run with coverage report
make test-watch        # Watch mode (auto-run on changes)
```

### Using pytest Directly

```bash
# Run specific test file
pytest api/tests/test_etl_service.py

# Run specific test
pytest api/tests/test_etl_service.py::TestFormETLService::test_insert_case_with_full_address

# Run tests matching pattern
pytest -k "insert_case"

# Run with markers
pytest -m "unit"           # Only unit tests
pytest -m "integration"    # Only integration tests
pytest -m "not slow"       # Skip slow tests
```

## 📂 Test Structure

```
api/tests/
├── conftest.py              # Shared fixtures
├── test_etl_service.py      # ETL service unit tests
├── test_api_endpoints.py    # API integration tests
├── test_models.py           # Model validation tests
└── README.md                # Comprehensive guide
```

## 🎯 What's Tested

### ✅ Unit Tests (50+ tests)
- ETL service methods
- Pydantic model validation
- Data transformation logic
- Error handling

### ✅ Integration Tests (25+ tests)
- API endpoints
- Database operations
- Request/response validation
- End-to-end flows

### ✅ E2E Tests (10 tests - Playwright)
- Full form submission flow
- UI interactions
- Pipeline integration

## 📖 Learn More

- **Comprehensive Guide**: See [`api/tests/README.md`](api/tests/README.md)
- **Implementation Details**: See [`docs/TDD_IMPLEMENTATION.md`](docs/TDD_IMPLEMENTATION.md)
- **TDD Principles**: See [`docs/agents/tdd-orchestrator.md`](docs/agents/tdd-orchestrator.md)

## 🆘 Need Help?

```bash
# Show all make commands
make help

# Show pytest help
pytest --help

# Show available test markers
pytest --markers
```

## 🎉 Quick Wins

### Verify Everything Works

```bash
# Run smoke tests
pytest -m smoke -v

# Run critical path tests
pytest -m critical -v
```

### Development Workflow

```bash
# Watch mode for TDD
make test-watch

# Or manually
pytest --watch
```

### Before Committing

```bash
# Run full CI checks
make ci

# Or step by step
make format   # Format code
make lint     # Check code quality
make test-cov # Run tests with coverage
```

## 📊 Coverage Goals

- **Overall**: >80%
- **Critical Paths**: >95%
- **ETL Service**: >90%
- **API Endpoints**: >85%

Current status: ✅ All goals achievable

## 💡 Pro Tips

1. **Use markers** to run specific test categories during development
2. **Use factories** from `conftest.py` to create test data easily
3. **Database tests** automatically rollback - no cleanup needed!
4. **Test names** are descriptive - read them to understand behavior
5. **AAA pattern** - all tests follow Arrange-Act-Assert

## 🔥 Example Test

```python
def test_submit_valid_form(client, sample_form_data):
    # Arrange
    # sample_form_data fixture provides valid form data
    
    # Act
    response = client.post("/api/form-submissions", json=sample_form_data)
    
    # Assert
    assert response.status_code == 201
    assert "case_id" in response.json()
```

---

**Ready to test?** Run `make test` and watch the magic happen! ✨

