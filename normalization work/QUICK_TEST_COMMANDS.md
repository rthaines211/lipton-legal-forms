# Quick Test Commands - Phase 1 API

Copy and paste these commands to test Phase 1 implementation.

## 1. Start the API Server

```bash
cd "/Users/ryanhaines/Desktop/Lipton Webserver/normalization work"
source venv/bin/activate
uvicorn api.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 2. Open New Terminal for Testing

In a **new terminal window**, run these commands:

### Test 1: Health Check ✅
```bash
curl http://localhost:8000/health
```
**Expected:** `{"status":"healthy","service":"normalization-api"}`

---

### Test 2: Service Status ✅
```bash
curl http://localhost:8000/api/status | python3 -m json.tool
```
**Expected:** JSON with service configuration

---

### Test 3: API Documentation ✅
```bash
open http://localhost:8000/docs
```
**Expected:** Interactive Swagger UI opens in browser

---

### Test 4: Execute Pipeline (Quick Test) ✅
```bash
cd "/Users/ryanhaines/Desktop/Lipton Webserver/normalization work"

curl -X POST http://localhost:8000/api/normalize \
  -H "Content-Type: application/json" \
  -d '{
    "Form": {"Id": "test-1", "InternalName": "TestForm", "Name": "Test"},
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

**Expected:** JSON response with `"success": true` and phase results

---

### Test 5: Execute with Real Form Data ✅
```bash
cd "/Users/ryanhaines/Desktop/Lipton Webserver/normalization work"

curl -X POST http://localhost:8000/api/normalize \
  -H "Content-Type: application/json" \
  -d @formtest.json | python3 -m json.tool
```

**Expected:** Complete pipeline execution (takes 5-10 seconds)

---

### Test 6: Run All Tests Automatically ✅
```bash
cd "/Users/ryanhaines/Desktop/Lipton Webserver/normalization work"
./test_api.sh
```

**Expected:** All tests pass with green checkmarks

---

## 3. View Results

### Check Server Logs
Look at the terminal running uvicorn to see:
- Request logs
- Phase execution logs
- Any errors

### Check Response
The API returns:
```json
{
  "success": true,
  "case_id": "...",
  "execution_time_ms": 5000,
  "phase_results": {
    "phase1": {...},
    "phase2": {...},
    "phase3": {...},
    "phase4": {...},
    "phase5": {...}
  }
}
```

---

## Quick Troubleshooting

### Port Already in Use?
```bash
lsof -ti :8000 | xargs kill -9
```

### Can't Connect?
```bash
# Check if server is running
lsof -i :8000

# Check if it's listening
curl http://localhost:8000/health
```

### Import Errors?
```bash
cd "/Users/ryanhaines/Desktop/Lipton Webserver/normalization work"
source venv/bin/activate
python3 -c "import api.main"  # Should not error
```

---

## Success Criteria ✅

Phase 1 is working if:

1. ✅ Server starts without errors
2. ✅ Health check returns `{"status":"healthy"}`
3. ✅ Status endpoint returns configuration
4. ✅ API docs accessible at http://localhost:8000/docs
5. ✅ Pipeline executes all 5 phases successfully
6. ✅ Response includes `"success": true`

---

## Next Steps

Once all tests pass:
1. ✅ Phase 1 Complete
2. → Proceed to Phase 2: Node.js Integration
3. → See [PIPELINE_INTEGRATION_PLAN.md](../PIPELINE_INTEGRATION_PLAN.md)

---

**Need help?** See [PHASE1_TESTING.md](PHASE1_TESTING.md) for detailed testing guide.
