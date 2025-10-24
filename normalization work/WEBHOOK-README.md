# Webhook Integration - Quick Start Guide

## Overview

This directory now includes webhook integration to automatically send Phase 5 discovery sets to the Docmosis rendering API.

## Quick Start

### 1. Setup (One-time)

Ensure you have the `requests` library installed:

```bash
cd "normalization work"
source venv/bin/activate
pip install requests
```

The webhook configuration is already set up in [webhook_config.json](webhook_config.json).

### 2. Usage

**Run pipeline with webhook sending:**
```bash
python3 run_pipeline.py --send-webhooks
```

**Send existing Phase 5 output:**
```bash
python3 send_to_webhook.py output_phase5_20251017_145943.json
```

**Run pipeline without webhooks (default):**
```bash
python3 run_pipeline.py
```

## Files Added

| File | Purpose |
|------|---------|
| [webhook_config.json](webhook_config.json) | Webhook configuration (URL, access key, timeouts) |
| [src/phase5/webhook_sender.py](src/phase5/webhook_sender.py) | Webhook sender module with retry logic |
| [send_to_webhook.py](send_to_webhook.py) | Standalone script to send existing Phase 5 files |
| [tests/phase5/test_webhook_sender.py](tests/phase5/test_webhook_sender.py) | Comprehensive test suite (16 tests) |
| [WEBHOOK-INTEGRATION.md](WEBHOOK-INTEGRATION.md) | Complete documentation |
| [WEBHOOK-README.md](WEBHOOK-README.md) | This quick start guide |

## Files Modified

| File | Changes |
|------|---------|
| [run_pipeline.py](run_pipeline.py) | Added `--send-webhooks` and `--webhook-config` flags |

## Testing

Run the test suite:
```bash
pytest tests/phase5/test_webhook_sender.py -v
```

All 16 tests should pass:
- Configuration loading
- Payload construction
- HTTP request handling
- Retry logic
- Error handling

## Documentation

For complete documentation, see [WEBHOOK-INTEGRATION.md](WEBHOOK-INTEGRATION.md), which includes:

- Detailed configuration options
- Webhook payload structure
- Usage examples
- Error handling and troubleshooting
- Advanced usage patterns
- API reference

## Configuration

The [webhook_config.json](webhook_config.json) file contains:

```json
{
  "webhook_url": "https://docs.liptonlegal.com/api/render",
  "access_key": "YjcyM2Q0MzYtOTJiZi00NGI1LTlhMzQtYWIwZjFhNGYxNGE1OjMxMTY3MjM1Ng",
  "timeout_seconds": 30,
  "retry_attempts": 3,
  "retry_delay_seconds": 2
}
```

**Security Note:** Consider adding `webhook_config.json` to `.gitignore` if committing to version control.

## Example Output

When running with `--send-webhooks`:

```
======================================================================
  LEGAL DISCOVERY NORMALIZATION PIPELINE
  Phases 1-5: Complete Processing
  Webhook Sending: ENABLED
======================================================================

[... Phase 1-5 processing ...]

======================================================================
  WEBHOOK SENDING
======================================================================
ℹ️  Webhook URL: https://docs.liptonlegal.com/api/render
ℹ️  Config: webhook_config.json

🔄 Sending set 1: Clark Kent vs Tony Stark - Discovery Propounded SROGs Set 1 of 12.docx
   ✅ Success [200]
🔄 Sending set 2: Clark Kent vs Tony Stark - Discovery Propounded SROGs Set 2 of 12.docx
   ✅ Success [200]
[... 42 more sets ...]

======================================================================
✅ Webhook sending complete!
   - Total sets: 44
   - Succeeded: 44
   - Failed: 0
======================================================================
```

## Features

✅ **Automatic retry** with exponential backoff
✅ **Comprehensive error handling** for network, timeout, and HTTP errors
✅ **Detailed logging** with success/failure tracking
✅ **Optional integration** - can run pipeline without webhooks
✅ **Standalone script** - can send existing Phase 5 files
✅ **Fully tested** - 16 passing tests with mocked HTTP requests
✅ **Well documented** - complete API reference and troubleshooting guide

## Support

- **Documentation**: [WEBHOOK-INTEGRATION.md](WEBHOOK-INTEGRATION.md)
- **Troubleshooting**: See "Troubleshooting" section in WEBHOOK-INTEGRATION.md
- **Tests**: Run `pytest tests/phase5/test_webhook_sender.py -v`

---

**Version:** 1.0
**Last Updated:** 2025-10-17
**Status:** ✅ Ready for use
