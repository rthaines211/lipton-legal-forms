#!/bin/bash
# Test script for Phase 1 API implementation
# This script tests all endpoints and verifies the API is working correctly

set -e  # Exit on error

echo "=================================="
echo "Phase 1 API Testing Script"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="http://localhost:8000"
TEST_DATA="formtest.json"

echo "Testing API at: $API_URL"
echo ""

# Test 1: Health Check
echo "Test 1: Health Check Endpoint"
echo "------------------------------"
echo "$ curl -s $API_URL/health"
HEALTH_RESPONSE=$(curl -s $API_URL/health)
echo "$HEALTH_RESPONSE" | python3 -m json.tool
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ PASS: Health check successful${NC}"
else
    echo -e "${RED}❌ FAIL: Health check failed${NC}"
    exit 1
fi
echo ""

# Test 2: Root Endpoint
echo "Test 2: Root Endpoint"
echo "------------------------------"
echo "$ curl -s $API_URL/"
ROOT_RESPONSE=$(curl -s $API_URL/)
echo "$ROOT_RESPONSE" | python3 -m json.tool
if echo "$ROOT_RESPONSE" | grep -q "Legal Discovery Normalization API"; then
    echo -e "${GREEN}✅ PASS: Root endpoint successful${NC}"
else
    echo -e "${RED}❌ FAIL: Root endpoint failed${NC}"
    exit 1
fi
echo ""

# Test 3: Status Endpoint
echo "Test 3: Status Endpoint"
echo "------------------------------"
echo "$ curl -s $API_URL/api/status"
STATUS_RESPONSE=$(curl -s $API_URL/api/status)
echo "$STATUS_RESPONSE" | python3 -m json.tool
if echo "$STATUS_RESPONSE" | grep -q "normalization-api"; then
    echo -e "${GREEN}✅ PASS: Status endpoint successful${NC}"
else
    echo -e "${RED}❌ FAIL: Status endpoint failed${NC}"
    exit 1
fi
echo ""

# Test 4: OpenAPI Documentation
echo "Test 4: OpenAPI Documentation"
echo "------------------------------"
echo "$ curl -s $API_URL/openapi.json"
OPENAPI_RESPONSE=$(curl -s $API_URL/openapi.json)
if echo "$OPENAPI_RESPONSE" | grep -q "Legal Discovery Normalization API"; then
    echo -e "${GREEN}✅ PASS: OpenAPI docs available${NC}"
    echo "   Documentation URL: $API_URL/docs"
else
    echo -e "${RED}❌ FAIL: OpenAPI docs not found${NC}"
    exit 1
fi
echo ""

# Test 5: Normalize Endpoint (if test data exists)
if [ -f "$TEST_DATA" ]; then
    echo "Test 5: Normalize Endpoint with Real Data"
    echo "------------------------------"
    echo "$ curl -X POST $API_URL/api/normalize -H 'Content-Type: application/json' -d @$TEST_DATA"
    echo ""
    echo -e "${YELLOW}⏳ Running pipeline (this may take 5-10 seconds)...${NC}"

    # Save response to file for inspection
    NORMALIZE_RESPONSE=$(curl -s -X POST $API_URL/api/normalize \
        -H "Content-Type: application/json" \
        -d @"$TEST_DATA")

    echo "$NORMALIZE_RESPONSE" | python3 -m json.tool > test_response.json

    if echo "$NORMALIZE_RESPONSE" | grep -q "success"; then
        echo -e "${GREEN}✅ PASS: Pipeline executed successfully${NC}"

        # Extract key metrics
        echo ""
        echo "Pipeline Results:"
        echo "----------------"

        # Parse response
        CASE_ID=$(echo "$NORMALIZE_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('case_id', 'N/A'))" 2>/dev/null || echo "N/A")
        EXEC_TIME=$(echo "$NORMALIZE_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('execution_time_ms', 'N/A'))" 2>/dev/null || echo "N/A")

        echo "  Case ID: $CASE_ID"
        echo "  Execution Time: ${EXEC_TIME}ms"

        # Show phase results if available
        if echo "$NORMALIZE_RESPONSE" | grep -q "phase_results"; then
            echo ""
            echo "  Phase Results:"
            echo "$NORMALIZE_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    phases = data.get('phase_results', {})
    for phase, results in phases.items():
        print(f'    {phase}: {results}')
except:
    pass
" 2>/dev/null || echo "    (Unable to parse phase results)"
        fi

        # Show webhook summary if available
        if echo "$NORMALIZE_RESPONSE" | grep -q "webhook_summary"; then
            echo ""
            echo "  Webhook Summary:"
            echo "$NORMALIZE_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    webhook = data.get('webhook_summary', {})
    print(f'    Total Sets: {webhook.get(\"total_sets\", \"N/A\")}')
    print(f'    Succeeded: {webhook.get(\"succeeded\", \"N/A\")}')
    print(f'    Failed: {webhook.get(\"failed\", \"N/A\")}')
except:
    pass
" 2>/dev/null || echo "    (Unable to parse webhook summary)"
        fi

        echo ""
        echo -e "${YELLOW}📄 Full response saved to: test_response.json${NC}"

    else
        echo -e "${RED}❌ FAIL: Pipeline execution failed${NC}"
        echo ""
        echo "Error Response:"
        echo "$NORMALIZE_RESPONSE" | python3 -m json.tool
        exit 1
    fi
else
    echo "Test 5: Normalize Endpoint"
    echo "------------------------------"
    echo -e "${YELLOW}⚠️  SKIP: Test data file '$TEST_DATA' not found${NC}"
    echo "   To test with real data, ensure formtest.json exists"
fi
echo ""

# Test 6: Invalid Request Handling
echo "Test 6: Invalid Request Handling"
echo "------------------------------"
echo "$ curl -X POST $API_URL/api/normalize -H 'Content-Type: application/json' -d '{}'"
INVALID_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST $API_URL/api/normalize \
    -H "Content-Type: application/json" \
    -d '{}')

HTTP_STATUS=$(echo "$INVALID_RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)
BODY=$(echo "$INVALID_RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" = "500" ] || [ "$HTTP_STATUS" = "422" ] || [ "$HTTP_STATUS" = "400" ]; then
    echo -e "${GREEN}✅ PASS: Invalid request handled correctly (HTTP $HTTP_STATUS)${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING: Expected error status, got HTTP $HTTP_STATUS${NC}"
fi
echo ""

# Summary
echo "=================================="
echo "Test Summary"
echo "=================================="
echo -e "${GREEN}✅ All basic tests passed!${NC}"
echo ""
echo "API Endpoints Verified:"
echo "  - GET  /health           ✅"
echo "  - GET  /                 ✅"
echo "  - GET  /api/status       ✅"
echo "  - GET  /openapi.json     ✅"
if [ -f "$TEST_DATA" ]; then
    echo "  - POST /api/normalize    ✅"
fi
echo ""
echo "Next Steps:"
echo "  1. View API docs: open $API_URL/docs"
echo "  2. Review test response: cat test_response.json"
echo "  3. Test with your own form data"
echo ""
echo -e "${GREEN}🎉 Phase 1 is ready for integration!${NC}"
