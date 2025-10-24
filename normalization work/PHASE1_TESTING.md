# Phase 1 Testing Guide

Quick guide to verify Phase 1 API implementation is working correctly.

## Prerequisites

1. Virtual environment activated
2. Dependencies installed
3. API server running on port 8000

## Quick Test Commands

### 1. Start the API Server

```bash
cd "normalization work"
source venv/bin/activate
uvicorn api.main:app --reload --port 8000
```

Keep this terminal open. The server should show:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Run Automated Test Script (Recommended)

In a **new terminal**, run:

```bash
cd "normalization work"
./test_api.sh
```

This will test all endpoints and show detailed results.

### 3. Manual Testing (Alternative)

If you prefer to test manually, here are the individual commands:

#### Test 1: Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"normalization-api"}
```

#### Test 2: Root Endpoint
```bash
curl http://localhost:8000/ | python3 -m json.tool
# Expected: Service info with version 1.0.0
```

#### Test 3: Status Endpoint
```bash
curl http://localhost:8000/api/status | python3 -m json.tool
# Expected: Configuration details
```

#### Test 4: API Documentation
```bash
# Open in browser
open http://localhost:8000/docs

# Or check OpenAPI spec
curl http://localhost:8000/openapi.json | python3 -m json.tool
```

#### Test 5: Execute Pipeline (with formtest.json)
```bash
curl -X POST http://localhost:8000/api/normalize \
  -H "Content-Type: application/json" \
  -d @formtest.json | python3 -m json.tool
```

This will take 5-10 seconds and return complete phase results.

#### Test 6: Execute Pipeline (with custom data)
```bash
curl -X POST http://localhost:8000/api/normalize \
  -H "Content-Type: application/json" \
  -d '{
    "Form": {
      "Id": "test-1",
      "InternalName": "TestForm",
      "Name": "Test Form"
    },
    "PlaintiffDetails": [
      {
        "Id": "1",
        "FirstName": "John",
        "LastName": "Doe",
        "IsHeadOfHousehold": true,
        "Discovery": {
          "Vermin": ["RatsMice"],
          "Environmental": ["Mold"]
        }
      }
    ],
    "DefendantDetails2": [
      {
        "Id": "1",
        "FirstName": "Jane",
        "LastName": "Smith",
        "EntityType": "LLC"
      }
    ],
    "Full_Address": {
      "Street": "123 Main St",
      "City": "New York",
      "State": "NY",
      "PostalCode": "10001"
    }
  }' | python3 -m json.tool
```

## Expected Results

### Successful Pipeline Execution

You should see output like:

```json
{
  "success": true,
  "case_id": "abc123",
  "execution_time_ms": 5420,
  "phase_results": {
    "phase1": {
      "plaintiffs": 1,
      "defendants": 1,
      "case_id": "abc123"
    },
    "phase2": {
      "datasets": 1,
      "hoh_count": 1,
      "defendant_count": 1
    },
    "phase3": {
      "datasets": 1,
      "flags_applied": 180,
      "sample_true_flags": 2
    },
    "phase4": {
      "profile_datasets": 3,
      "profiles_applied": 3
    },
    "phase5": {
      "split_datasets": 3,
      "total_sets": 3,
      "max_per_set": 120
    }
  },
  "webhook_summary": {
    "total_sets": 3,
    "succeeded": 0,
    "failed": 3
  }
}
```

**Note**: Webhooks may fail if `ENABLE_WEBHOOKS=true` but webhook URL is not configured. This is expected for local testing.

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti :8000 | xargs kill -9

# Or use a different port
uvicorn api.main:app --port 8001
```

### Module Import Errors

Make sure you're in the correct directory:

```bash
cd "normalization work"
python3 -c "import api.main"  # Should not error
```

### Connection Refused

Make sure the server is running:

```bash
# Check if server is listening
lsof -i :8000
```

## Success Criteria

✅ Phase 1 is ready if:

1. **Health check** returns `{"status":"healthy"}`
2. **Status endpoint** shows configuration
3. **API docs** are accessible at `/docs`
4. **Pipeline endpoint** executes all 5 phases successfully
5. **Error handling** works (invalid requests return errors)
6. **Response time** is reasonable (< 30 seconds for typical form)

## Next Steps After Verification

Once Phase 1 tests pass:

1. ✅ **Phase 1 Complete** - API service working
2. ⬜ **Phase 2** - Integrate with Node.js server
3. ⬜ **Phase 3** - Docker & GCP configuration
4. ⬜ **Phase 4** - Environment & security
5. ⬜ **Phase 5** - Frontend status indicators

## Performance Benchmarks

Typical execution times on Apple Silicon Mac:

- Phase 1: ~200-500ms
- Phase 2: ~100-300ms
- Phase 3: ~1-2s
- Phase 4: ~500ms-1s
- Phase 5: ~500ms-1s
- **Total**: ~3-5 seconds (without webhooks)

If execution takes significantly longer, check:
- System resources (CPU, memory)
- Input data size (number of plaintiffs/defendants)
- Debug logging overhead

## Additional Testing

### Load Testing (Optional)

Test with multiple concurrent requests:

```bash
# Install Apache Bench if needed
brew install apache2

# Run 10 concurrent requests
ab -n 10 -c 2 -p formtest.json -T application/json \
  http://localhost:8000/api/normalize
```

### Memory Testing (Optional)

Monitor memory usage during pipeline execution:

```bash
# Terminal 1: Start server
uvicorn api.main:app --port 8000

# Terminal 2: Watch memory
while true; do
  ps aux | grep uvicorn | grep -v grep
  sleep 1
done

# Terminal 3: Send requests
curl -X POST http://localhost:8000/api/normalize \
  -H "Content-Type: application/json" \
  -d @formtest.json
```

## Support

If you encounter issues:

1. Check server logs in the terminal running uvicorn
2. Check [api/README.md](api/README.md) for detailed documentation
3. Review [PIPELINE_INTEGRATION_PLAN.md](../PIPELINE_INTEGRATION_PLAN.md) for architecture
