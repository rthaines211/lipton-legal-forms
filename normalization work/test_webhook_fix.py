#!/usr/bin/env python3
"""
Test script to demonstrate the webhook sender fix for non-JSON responses.

This script simulates what happens when the Docmosis API returns a non-JSON
response (like a binary Word document) instead of JSON data.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.phase5.webhook_sender import send_set_to_webhook, load_webhook_config


def simulate_non_json_response():
    """Simulate the webhook returning a non-JSON response."""
    print("=" * 70)
    print("SIMULATING NON-JSON RESPONSE FROM WEBHOOK")
    print("=" * 70)
    print()

    # Load config
    config = load_webhook_config()

    # Create a sample set
    sample_set = {
        'Template': 'SROGsMaster.docx',
        'OutputName': 'John Doe vs ABC Corp - SROGs Set 1 of 2.docx',
        'SetNumber': 1,
        'HasMold': True
    }

    print("📄 Sample Set:")
    print(f"   Template: {sample_set['Template']}")
    print(f"   OutputName: {sample_set['OutputName']}")
    print()

    # Mock the HTTP response to return non-JSON content (like a Word document)
    with patch('src.phase5.webhook_sender.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'PK\x03\x04...'  # Binary content (like .docx file)
        mock_response.text = 'Binary document content'
        mock_response.headers = {
            'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }

        # Simulate JSON parsing error
        import json
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_post.return_value = mock_response

        print("🌐 Simulated Response:")
        print(f"   Status Code: {mock_response.status_code}")
        print(f"   Content-Type: {mock_response.headers['Content-Type']}")
        print(f"   Content: Binary data (Word document)")
        print()

        # Send to webhook
        print("📤 Sending to webhook...")
        result = send_set_to_webhook(sample_set, config)
        print()

        # Display result
        print("=" * 70)
        print("RESULT")
        print("=" * 70)

        if result['success']:
            print("✅ SUCCESS - Webhook call succeeded despite non-JSON response!")
            print()
            print("Response Details:")
            print(f"   Status Code: {result['status_code']}")
            print(f"   Attempts: {result['attempts']}")

            if result.get('response'):
                print()
                print("   Response Metadata:")
                for key, value in result['response'].items():
                    if key == 'raw_text':
                        print(f"      {key}: {value[:50]}..." if value else f"      {key}: None")
                    else:
                        print(f"      {key}: {value}")
        else:
            print("❌ FAILED")
            print(f"   Error: {result.get('error')}")

        print()
        print("=" * 70)


def demonstrate_original_error():
    """Show what the original error looked like."""
    print()
    print("=" * 70)
    print("ORIGINAL ERROR (BEFORE FIX)")
    print("=" * 70)
    print()
    print("When the webhook returned non-JSON content, you would see:")
    print()
    print("   ❌ Failed: Request error: Expecting value: line 1 column 1 (char 0)")
    print()
    print("This happened because the code tried to parse the response as JSON,")
    print("but the API returned a binary Word document instead.")
    print()


def demonstrate_fix():
    """Show how the fix works."""
    print()
    print("=" * 70)
    print("THE FIX")
    print("=" * 70)
    print()
    print("The webhook sender now:")
    print()
    print("1. ✅ Tries to parse JSON if available")
    print("2. ✅ If JSON parsing fails, treats it as success anyway (status 200)")
    print("3. ✅ Stores response metadata instead:")
    print("      - Content-Type (e.g., 'application/vnd...document.wordprocessingml')")
    print("      - Content-Length (size of binary data)")
    print("      - Raw text preview (first 200 characters)")
    print("4. ✅ Still marks the webhook call as successful")
    print()
    print("This allows the Docmosis API to return:")
    print("   • Binary Word documents (.docx files)")
    print("   • Plain text messages")
    print("   • HTML pages")
    print("   • Or JSON (if that's what the API returns)")
    print()


def main():
    """Main function."""
    demonstrate_original_error()
    demonstrate_fix()
    simulate_non_json_response()

    print()
    print("🎉 The webhook sender now handles non-JSON responses gracefully!")
    print()
    print("You can now send your Phase 5 output to the webhook:")
    print("   python3 send_to_webhook.py output_phase5_20251017_152408.json")
    print()


if __name__ == "__main__":
    main()
