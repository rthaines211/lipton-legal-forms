# Webhook Integration Documentation

## Overview

After Phase 5 splits the discovery datasets into individual sets, each set can be sent to a Docmosis rendering webhook for document generation. This integration is optional and can be enabled via command-line flag.

## Architecture

```
Phase 5 Output (JSON)
       ↓
Webhook Sender Module
       ↓
HTTP POST Request
       ↓
Docmosis API (https://docs.liptonlegal.com/api/render)
       ↓
Generated Document
```

## Configuration

### Webhook Configuration File

Create `webhook_config.json` in the `normalization work/` directory:

```json
{
  "webhook_url": "https://docs.liptonlegal.com/api/render",
  "access_key": "YjcyM2Q0MzYtOTJiZi00NGI1LTlhMzQtYWIwZjFhNGYxNGE1OjMxMTY3MjM1Ng",
  "timeout_seconds": 30,
  "retry_attempts": 3,
  "retry_delay_seconds": 2
}
```

**Configuration Fields:**

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `webhook_url` | string | **Required.** Webhook endpoint URL | - |
| `access_key` | string | **Required.** Authentication key for webhook | - |
| `timeout_seconds` | number | Request timeout in seconds | 30 |
| `retry_attempts` | number | Maximum retry attempts on failure | 3 |
| `retry_delay_seconds` | number | Base delay between retries (exponential backoff) | 2 |

**Security Note:** The `webhook_config.json` file should be added to `.gitignore` to avoid committing sensitive access keys to version control.

## Webhook Payload Structure

Each set is sent with the following payload structure:

```json
{
  "data": {
    "SetNumber": 1,
    "SetNoWrite": "One",
    "SetLabel": "Set 1 of 12",
    "Template": "SROGsMaster.docx",
    "OutputName": "Clark Kent vs Tony Stark - Discovery Propounded SROGs Set 1 of 12.docx",
    "HeadOfHousehold": "Clark Kent",
    "TargetDefendant": "Tony Stark",
    "Case": {
      "FilingCounty": "Los Angeles",
      "FullAddress": "1331 Yorkshire Place NW Unit 1, Los Angeles, North Carolina, 28027"
    },
    "AllPlaintiffsUpperWithTypes": "CLARK KENT, INDIVIDUAL; LOIS LANE, GUARDIAN",
    "AllDefendantsUpperWithTypes": "TONY STARK, MANAGER; STEVE ROGERS, OWNER",
    "Plaintiffs": ["Clark Kent", "Lois Lane", "Bruce Wayne"],
    "HasMold": true,
    "HasVermin": true,
    "IsManager": true
    // ... all other flags and fields
  },
  "accessKey": "YjcyM2Q0MzYtOTJiZi00NGI1LTlhMzQtYWIwZjFhNGYxNGE1OjMxMTY3MjM1Ng",
  "templateName": "SROGsMaster.docx",
  "outputName": "Clark Kent vs Tony Stark - Discovery Propounded SROGs Set 1 of 12.docx"
}
```

**Key Points:**
- `data`: Complete set object with all fields from Phase 5 output
- `accessKey`: Authentication key from config
- `templateName`: Extracted from `data.Template`
- `outputName`: Extracted from `data.OutputName`

## Usage

### Option 1: Run Full Pipeline with Webhooks

Run the complete pipeline from Phase 1-5 and automatically send all sets to webhook:

```bash
cd "normalization work"
source venv/bin/activate
python3 run_pipeline.py --send-webhooks
```

**Output:**
```
======================================================================
  LEGAL DISCOVERY NORMALIZATION PIPELINE
  Phases 1-5: Complete Processing
  Webhook Sending: ENABLED
======================================================================

[... Phase 1-5 output ...]

======================================================================
  WEBHOOK SENDING
======================================================================
ℹ️  Webhook URL: https://docs.liptonlegal.com/api/render
ℹ️  Config: webhook_config.json

🔄 Sending set 1: Clark Kent vs Tony Stark - Discovery Propounded SROGs Set 1 of 12.docx
   ✅ Success [200]
🔄 Sending set 2: Clark Kent vs Tony Stark - Discovery Propounded SROGs Set 2 of 12.docx
   ✅ Success [200]
[...]

======================================================================
✅ Webhook sending complete!
   - Total sets: 44
   - Succeeded: 44
   - Failed: 0
======================================================================
```

### Option 2: Send Existing Phase 5 Output

Send an existing Phase 5 output file to webhook without re-running the pipeline:

```bash
cd "normalization work"
source venv/bin/activate
python3 send_to_webhook.py output_phase5_20251017_145943.json
```

**With custom config file:**
```bash
python3 send_to_webhook.py output_phase5_20251017_145943.json --config prod_config.json
```

**Quiet mode (no progress output):**
```bash
python3 send_to_webhook.py output_phase5_20251017_145943.json --quiet
```

### Option 3: Run Pipeline Without Webhooks (Default)

Run the pipeline normally without sending to webhook:

```bash
python3 run_pipeline.py
```

## Response Handling

### Non-JSON Responses

The webhook sender gracefully handles both JSON and non-JSON responses:

**JSON Response (if API returns JSON):**
```json
{
  "success": true,
  "status_code": 200,
  "response": {
    "document_id": "12345",
    "status": "generated"
  }
}
```

**Non-JSON Response (e.g., binary document, plain text):**
```json
{
  "success": true,
  "status_code": 200,
  "response": {
    "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "content_length": 45678,
    "raw_text": "Binary document content...",
    "note": "Response was not JSON (likely binary document or plain text)"
  }
}
```

**Key Points:**
- ✅ HTTP 200 status = success (regardless of response format)
- ✅ Handles Word documents (.docx binary data)
- ✅ Handles plain text responses
- ✅ Handles HTML responses
- ✅ Stores response metadata when JSON parsing fails

## Error Handling

### Retry Logic

The webhook sender implements automatic retry with exponential backoff:

1. **First attempt** fails → Wait 2 seconds → **Retry (attempt 2)**
2. **Second attempt** fails → Wait 4 seconds → **Retry (attempt 3)**
3. **Third attempt** fails → Mark as failed

**Retriable errors:**
- HTTP 5xx status codes (server errors)
- Timeout errors
- Network connection errors

**Non-retriable errors:**
- HTTP 4xx status codes (client errors - likely config issue)
- Invalid payload structure
- Unexpected exceptions

### Error Messages

**Config file not found:**
```
❌ Error: Webhook config not found: webhook_config.json
   Please create webhook_config.json with webhook_url and access_key
```

**Missing required config field:**
```
❌ Configuration error: Missing required config field: access_key
```

**Webhook send failure:**
```
🔄 Sending set 5: John Doe vs XYZ Corp - SROGs Set 1 of 3
   ❌ Failed: HTTP 500: Internal Server Error
```

**Summary with failures:**
```
⚠️  2 sets failed to send

❌ Failed sets:
   - John Doe vs XYZ Corp - SROGs Set 1 of 3: Request timeout after 30 seconds
   - Jane Smith vs ABC LLC - PODs Set 2 of 5: HTTP 503: Service Unavailable
```

## Testing

### Run Webhook Tests

```bash
cd "normalization work"
source venv/bin/activate
pytest tests/phase5/test_webhook_sender.py -v
```

**Test coverage includes:**
- Configuration loading and validation
- Payload construction
- HTTP request handling
- Retry logic
- Error handling
- Empty datasets handling

### Mock Webhook Testing

For testing without hitting the real webhook endpoint:

```python
import pytest
from unittest.mock import patch

@patch('src.phase5.webhook_sender.requests.post')
def test_webhook_integration(mock_post):
    """Test webhook with mocked HTTP requests."""
    # Mock successful response
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {'status': 'success'}

    # Run webhook sender
    summary = send_all_sets(phase5_output, config, verbose=False)

    assert summary['succeeded'] == expected_count
```

## Monitoring and Logging

### Tracking Webhook Calls

The webhook sender returns detailed results for each set:

```python
summary = send_all_sets(phase5_output, config, verbose=True)

# Check summary
print(f"Total: {summary['total_sets']}")
print(f"Succeeded: {summary['succeeded']}")
print(f"Failed: {summary['failed']}")

# Check individual results
for result in summary['results']:
    if result['success']:
        print(f"✅ {result['set_name']}: {result['status_code']}")
    else:
        print(f"❌ {result['set_name']}: {result['error']}")
```

### Exit Codes

The scripts use standard exit codes:

- `0`: Success (all sets sent successfully)
- `1`: Failure (one or more sets failed to send, or other error)

This allows integration with shell scripts:

```bash
python3 run_pipeline.py --send-webhooks
if [ $? -eq 0 ]; then
    echo "Pipeline and webhook sending completed successfully"
else
    echo "Pipeline or webhook sending failed"
    exit 1
fi
```

## Troubleshooting

### Issue: "Request error: Expecting value: line 1 column 1 (char 0)"

**Status:** ✅ **FIXED** - This error has been resolved in the current version.

**What it was:** This JSON parsing error occurred when the Docmosis API returned a non-JSON response (like a binary Word document) but the code expected JSON.

**Solution:** The webhook sender now automatically handles non-JSON responses. If you still see this error:
1. Ensure you're using the latest version of [webhook_sender.py](src/phase5/webhook_sender.py)
2. The fix treats HTTP 200 responses as success regardless of content type
3. Non-JSON responses are stored as metadata instead of causing errors

### Issue: "Config file not found"

**Solution:** Create `webhook_config.json` in the `normalization work/` directory with required fields:

```json
{
  "webhook_url": "https://docs.liptonlegal.com/api/render",
  "access_key": "your-access-key-here"
}
```

### Issue: "HTTP 401: Unauthorized"

**Solution:** Check that the `access_key` in your config file is correct and has not expired.

### Issue: "HTTP 500: Internal Server Error"

**Solution:** This is a server-side error. The webhook sender will automatically retry. If the issue persists:
1. Check the webhook endpoint status
2. Verify the payload structure matches what the endpoint expects
3. Contact the API administrator

### Issue: "Request timeout after 30 seconds"

**Solution:**
1. Increase the `timeout_seconds` value in config:
   ```json
   {
     "timeout_seconds": 60
   }
   ```
2. Check network connectivity to the webhook endpoint
3. Verify the webhook endpoint is responding

### Issue: Some sets succeeded, others failed

**Solution:**
1. Check the error messages for failed sets in the summary
2. Review the Phase 5 output to ensure data quality for failed sets
3. Try re-sending just the failed sets by extracting them into a new JSON file

### Issue: All sets failing with the same error

**Solution:** Likely a configuration or connectivity issue:
1. Verify `webhook_url` is correct
2. Test connectivity: `curl -X POST https://docs.liptonlegal.com/api/render`
3. Verify network/firewall settings

## Advanced Usage

### Programmatic Usage

You can import and use the webhook sender in your own Python scripts:

```python
from src.phase5.webhook_sender import send_all_sets, load_webhook_config
import json

# Load Phase 5 output
with open('output_phase5_20251017_145943.json', 'r') as f:
    phase5_output = json.load(f)

# Load config
config = load_webhook_config('webhook_config.json')

# Send all sets
summary = send_all_sets(phase5_output, config, verbose=True)

# Process results
if summary['failed'] > 0:
    print("Some sets failed. Retrying failed sets...")
    # Custom retry logic here
```

### Sending Individual Sets

To send just one specific set:

```python
from src.phase5.webhook_sender import send_set_to_webhook, load_webhook_config

# Get a specific set from Phase 5 output
set_data = phase5_output['datasets'][0]['sets'][0]

# Load config
config = load_webhook_config()

# Send individual set
result = send_set_to_webhook(set_data, config)

if result['success']:
    print(f"✅ Sent successfully: {result['status_code']}")
else:
    print(f"❌ Failed: {result['error']}")
```

### Multiple Environment Configs

For different environments (development, staging, production):

```bash
# Development
python3 send_to_webhook.py output.json --config webhook_config_dev.json

# Staging
python3 send_to_webhook.py output.json --config webhook_config_staging.json

# Production
python3 send_to_webhook.py output.json --config webhook_config_prod.json
```

## Performance

### Expected Throughput

- **Single set send time**: ~1-2 seconds (depends on webhook response time)
- **44 sets** (typical case): ~1-2 minutes
- **Network latency**: Primary bottleneck

### Optimization Tips

1. **Parallel sending** (future enhancement): Send multiple sets concurrently
2. **Batch mode** (future enhancement): Send multiple sets in one request
3. **Adjust timeouts**: Lower timeout for faster failure detection

## Security Best Practices

1. **Never commit access keys** to version control
   - Add `webhook_config.json` to `.gitignore`
   - Use environment-specific config files

2. **Rotate access keys regularly**
   - Update `access_key` in config file
   - Notify team members of key changes

3. **Use HTTPS only**
   - Webhook URL should always use `https://`
   - Never send access keys over unencrypted connections

4. **Limit access key permissions**
   - Use API keys with minimal required permissions
   - Create separate keys for different environments

## API Reference

### Functions

#### `load_webhook_config(config_path: str) -> Dict`

Load webhook configuration from JSON file.

**Parameters:**
- `config_path`: Path to config file (default: `"webhook_config.json"`)

**Returns:** Configuration dictionary

**Raises:**
- `FileNotFoundError`: If config file doesn't exist
- `ValueError`: If required fields are missing

---

#### `build_webhook_payload(set_data: Dict, access_key: str) -> Dict`

Build webhook payload from set data.

**Parameters:**
- `set_data`: Individual set from Phase 5 output
- `access_key`: Authentication key

**Returns:** Webhook payload dictionary

---

#### `send_set_to_webhook(set_data: Dict, config: Dict, attempt: int = 1) -> Dict`

Send a single set to webhook with retry logic.

**Parameters:**
- `set_data`: Individual set from Phase 5 output
- `config`: Webhook configuration
- `attempt`: Current attempt number (for recursion)

**Returns:** Result dictionary with `success`, `status_code`, `error`, `attempts`

---

#### `send_all_sets(phase5_output: Dict, config: Dict = None, verbose: bool = True) -> Dict`

Send all sets from Phase 5 output to webhook.

**Parameters:**
- `phase5_output`: Complete Phase 5 output
- `config`: Webhook config (loads from file if None)
- `verbose`: Print progress messages

**Returns:** Summary dictionary with `total_sets`, `succeeded`, `failed`, `results`

---

#### `send_phase5_file(phase5_file: str, config_file: str = "webhook_config.json", verbose: bool = True) -> Dict`

Load Phase 5 file and send all sets to webhook.

**Parameters:**
- `phase5_file`: Path to Phase 5 JSON file
- `config_file`: Path to config file
- `verbose`: Print progress messages

**Returns:** Summary dictionary from `send_all_sets()`

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review error messages in the output
3. Check webhook endpoint documentation
4. Run tests to verify integration: `pytest tests/phase5/test_webhook_sender.py`

---

**Last Updated:** 2025-10-17
**Version:** 1.0
**Module:** Phase 5 Webhook Integration
