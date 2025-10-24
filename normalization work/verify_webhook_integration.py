#!/usr/bin/env python3
"""
Webhook Integration Verification Script

This script verifies that the webhook integration is properly set up and configured.
It performs several checks without actually sending data to the webhook.

Usage:
    python3 verify_webhook_integration.py
"""

import json
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.phase5.webhook_sender import (
        load_webhook_config,
        build_webhook_payload
    )
except ImportError as e:
    print(f"❌ Error importing webhook sender module: {e}")
    sys.exit(1)


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def check_config_file():
    """Check if webhook config file exists and is valid."""
    print_header("1. Checking Webhook Configuration")

    config_file = Path("webhook_config.json")

    if not config_file.exists():
        print("❌ webhook_config.json not found")
        return False

    print("✅ webhook_config.json exists")

    try:
        config = load_webhook_config("webhook_config.json")
        print("✅ Configuration is valid JSON")

        # Check required fields
        if 'webhook_url' in config:
            print(f"✅ webhook_url: {config['webhook_url']}")
        else:
            print("❌ Missing webhook_url")
            return False

        if 'access_key' in config:
            masked_key = config['access_key'][:10] + "..." if len(config['access_key']) > 10 else "***"
            print(f"✅ access_key: {masked_key}")
        else:
            print("❌ Missing access_key")
            return False

        # Check optional fields
        print(f"✅ timeout_seconds: {config.get('timeout_seconds', 'default')}")
        print(f"✅ retry_attempts: {config.get('retry_attempts', 'default')}")
        print(f"✅ retry_delay_seconds: {config.get('retry_delay_seconds', 'default')}")

        return True

    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False


def check_phase5_output():
    """Check if Phase 5 output files exist."""
    print_header("2. Checking Phase 5 Output Files")

    phase5_files = list(Path(".").glob("output_phase5_*.json"))

    if not phase5_files:
        print("⚠️  No Phase 5 output files found")
        print("   Run 'python3 run_pipeline.py' to generate Phase 5 output")
        return False

    print(f"✅ Found {len(phase5_files)} Phase 5 output file(s):")
    for file in phase5_files[:5]:  # Show max 5
        print(f"   - {file.name}")

    if len(phase5_files) > 5:
        print(f"   ... and {len(phase5_files) - 5} more")

    # Load and verify structure of most recent file
    latest_file = max(phase5_files, key=lambda p: p.stat().st_mtime)
    print(f"\n📄 Verifying latest file: {latest_file.name}")

    try:
        with open(latest_file, 'r') as f:
            phase5_output = json.load(f)

        if 'datasets' not in phase5_output:
            print("❌ Invalid structure: missing 'datasets' key")
            return False

        datasets = phase5_output['datasets']
        print(f"✅ Contains {len(datasets)} dataset(s)")

        total_sets = sum(len(d.get('sets', [])) for d in datasets)
        print(f"✅ Contains {total_sets} total set(s)")

        if total_sets > 0:
            # Check first set structure
            first_set = datasets[0]['sets'][0]
            required_fields = ['Template', 'OutputName', 'SetNumber']

            missing_fields = [f for f in required_fields if f not in first_set]
            if missing_fields:
                print(f"❌ First set missing required fields: {missing_fields}")
                return False

            print(f"✅ First set has all required webhook fields")

        return True

    except Exception as e:
        print(f"❌ Error loading Phase 5 output: {e}")
        return False


def check_webhook_payload():
    """Verify webhook payload construction."""
    print_header("3. Checking Webhook Payload Construction")

    # Load Phase 5 output
    phase5_files = list(Path(".").glob("output_phase5_*.json"))
    if not phase5_files:
        print("⚠️  Skipping (no Phase 5 output files)")
        return False

    latest_file = max(phase5_files, key=lambda p: p.stat().st_mtime)

    try:
        with open(latest_file, 'r') as f:
            phase5_output = json.load(f)

        if not phase5_output.get('datasets'):
            print("❌ No datasets found")
            return False

        first_set = phase5_output['datasets'][0]['sets'][0]

        # Build payload
        payload = build_webhook_payload(first_set, "test-key-123")

        # Verify structure
        required_keys = ['data', 'accessKey', 'templateName', 'outputName']
        missing_keys = [k for k in required_keys if k not in payload]

        if missing_keys:
            print(f"❌ Payload missing keys: {missing_keys}")
            return False

        print("✅ Payload has correct structure:")
        print(f"   - data: {len(payload['data'])} fields")
        print(f"   - accessKey: {payload['accessKey'][:10]}...")
        print(f"   - templateName: {payload['templateName']}")
        print(f"   - outputName: {payload['outputName'][:50]}...")

        return True

    except Exception as e:
        print(f"❌ Error constructing payload: {e}")
        return False


def check_dependencies():
    """Check if required Python packages are installed."""
    print_header("4. Checking Python Dependencies")

    try:
        import requests
        print(f"✅ requests library installed (v{requests.__version__})")
    except ImportError:
        print("❌ requests library not installed")
        print("   Run: pip install requests")
        return False

    try:
        import pytest
        print(f"✅ pytest installed (v{pytest.__version__})")
    except ImportError:
        print("⚠️  pytest not installed (optional, needed for tests)")

    return True


def check_test_files():
    """Check if test files exist."""
    print_header("5. Checking Test Files")

    test_file = Path("tests/phase5/test_webhook_sender.py")

    if not test_file.exists():
        print("❌ Test file not found: tests/phase5/test_webhook_sender.py")
        return False

    print("✅ Test file exists: tests/phase5/test_webhook_sender.py")
    print("\n   To run tests:")
    print("   pytest tests/phase5/test_webhook_sender.py -v")

    return True


def main():
    """Main verification function."""
    print("\n" + "=" * 70)
    print("  WEBHOOK INTEGRATION VERIFICATION")
    print("=" * 70)

    checks = [
        ("Configuration File", check_config_file),
        ("Phase 5 Output", check_phase5_output),
        ("Payload Construction", check_webhook_payload),
        ("Python Dependencies", check_dependencies),
        ("Test Files", check_test_files)
    ]

    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))

    # Print summary
    print_header("VERIFICATION SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print("\n" + "=" * 70)

    if passed == total:
        print("🎉 All checks passed! Webhook integration is ready to use.")
        print("\nNext steps:")
        print("1. Run pipeline with webhooks:")
        print("   python3 run_pipeline.py --send-webhooks")
        print("\n2. Or send existing Phase 5 output:")
        print("   python3 send_to_webhook.py output_phase5_*.json")
        return 0
    else:
        print(f"⚠️  {total - passed} check(s) failed. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
