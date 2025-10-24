#!/usr/bin/env python3
"""
Standalone Webhook Sender Script

Send existing Phase 5 output JSON files to the Docmosis rendering webhook.

Usage:
    python3 send_to_webhook.py <phase5_output_file.json>
    python3 send_to_webhook.py output_phase5_20251017_145943.json
    python3 send_to_webhook.py output_phase5_20251017_145943.json --config custom_config.json
"""

import sys
import argparse
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.phase5.webhook_sender import send_phase5_file, load_webhook_config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Send Phase 5 output sets to Docmosis webhook',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send Phase 5 output to webhook
  python3 send_to_webhook.py output_phase5_20251017_145943.json

  # Use custom config file
  python3 send_to_webhook.py output_phase5_20251017_145943.json --config prod_config.json

  # Quiet mode (no progress messages)
  python3 send_to_webhook.py output_phase5_20251017_145943.json --quiet
        """
    )

    parser.add_argument(
        'phase5_file',
        help='Path to Phase 5 output JSON file'
    )

    parser.add_argument(
        '--config',
        default='webhook_config.json',
        help='Path to webhook configuration file (default: webhook_config.json)'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress messages'
    )

    args = parser.parse_args()

    # Validate input file exists
    phase5_path = Path(args.phase5_file)
    if not phase5_path.exists():
        print(f"❌ Error: File not found: {args.phase5_file}")
        return 1

    # Validate config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Error: Config file not found: {args.config}")
        print(f"   Please create {args.config} with webhook_url and access_key")
        return 1

    try:
        # Load and validate config
        config = load_webhook_config(args.config)

        if not args.quiet:
            print(f"\n{'='*70}")
            print(f"  WEBHOOK SENDER")
            print(f"{'='*70}")
            print(f"Phase 5 file: {args.phase5_file}")
            print(f"Config file:  {args.config}")
            print(f"Webhook URL:  {config['webhook_url']}")
            print(f"{'='*70}\n")

        # Send to webhook
        summary = send_phase5_file(
            str(phase5_path),
            str(config_path),
            verbose=not args.quiet
        )

        # Exit with appropriate code
        if summary['failed'] == 0:
            if not args.quiet:
                print(f"\n🎉 All sets sent successfully!")
            return 0
        else:
            if not args.quiet:
                print(f"\n⚠️  {summary['failed']} sets failed to send")
            return 1

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return 1

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
