#!/usr/bin/env python3
"""
Complete Pipeline Runner for Phases 1-5

This script runs formtest.json through all 5 phases of the normalization pipeline
and outputs the JSON results from each phase to separate timestamped files.

This module can be used both as a standalone script and as an importable module
for the FastAPI service.

Usage as script:
    cd "normalization work"
    source venv/bin/activate
    python3 run_pipeline.py
    python3 run_pipeline.py --send-webhooks

Usage as module:
    from run_pipeline import run_phase1, run_phase2, run_phase3, run_phase4, run_phase5
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Phase 1: Input Normalization
from src.phase1.normalizer import normalize_form_data

# Phase 2: Dataset Builder
from src.phase2.dataset_builder import build_datasets

# Phase 3: Flag Processors
from src.phase3.flag_pipeline import FlagProcessorPipeline

# Phase 4: Document Profiles
from src.phase4 import ProfilePipeline

# Phase 5: Set Splitting
from src.phase5 import SplittingPipeline

# Webhook Sender (optional)
from src.phase5.webhook_sender import send_all_sets, load_webhook_config


def load_json_file(filepath: str) -> Dict[str, Any]:
    """
    Load JSON data from a file.

    Args:
        filepath: Path to the JSON file

    Returns:
        Parsed JSON data as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def save_json_file(data: Dict[str, Any], filepath: str) -> None:
    """
    Save data to a JSON file with pretty printing.

    Args:
        data: Dictionary to save
        filepath: Path to save the file
    """
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_success(text: str) -> None:
    """Print a success message."""
    print(f"✅ {text}")


def print_info(text: str) -> None:
    """Print an info message."""
    print(f"ℹ️  {text}")


def print_error(text: str) -> None:
    """Print an error message."""
    print(f"❌ {text}")


def run_phase1(form_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run Phase 1: Input Normalization.

    Transforms raw form JSON into normalized structure with:
    - Case information extracted
    - Plaintiffs normalized with discovery data flattened
    - Defendants normalized

    Args:
        form_json: Raw form data from formtest.json

    Returns:
        Normalized data structure
    """
    print_header("PHASE 1: INPUT NORMALIZATION")
    print_info("Normalizing form data...")

    normalized = normalize_form_data(form_json)

    print_success("Phase 1 complete!")
    print(f"   - Plaintiffs: {len(normalized.get('plaintiffs', []))}")
    print(f"   - Defendants: {len(normalized.get('defendants', []))}")
    print(f"   - Case ID: {normalized.get('case_info', {}).get('case_id', 'N/A')}")

    return normalized


def run_phase2(normalized_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run Phase 2: Dataset Builder.

    Creates Cartesian product of Head of Household plaintiffs × Defendants.

    Args:
        normalized_data: Output from Phase 1

    Returns:
        Collection of datasets with metadata
    """
    print_header("PHASE 2: DATASET BUILDER")
    print_info("Building HoH × Defendant datasets...")

    result = build_datasets(normalized_data)

    print_success("Phase 2 complete!")
    print(f"   - Total datasets: {result['metadata']['total_datasets']}")
    print(f"   - HoH plaintiffs: {result['metadata']['hoh_count']}")
    print(f"   - Defendants: {result['metadata']['defendant_count']}")
    print(f"   - Non-HoH plaintiffs: {result['metadata']['non_hoh_plaintiffs']}")

    return result


def run_phase3(phase2_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run Phase 3: Flag Processors.

    Processes each dataset through 25+ flag processors to generate 180+ boolean flags.

    Args:
        phase2_output: Output from Phase 2

    Returns:
        Collection of enriched datasets with flags
    """
    print_header("PHASE 3: FLAG PROCESSORS")
    print_info("Processing datasets through flag processors...")

    pipeline = FlagProcessorPipeline()
    result = pipeline.process_all_datasets(phase2_output)

    # Count total flags in first dataset as sample
    if result.get('datasets') and len(result['datasets']) > 0:
        first_dataset = result['datasets'][0]
        flag_count = len([k for k, v in first_dataset.get('flags', {}).items() if v is True])
        total_flags = len(first_dataset.get('flags', {}))
    else:
        flag_count = 0
        total_flags = 0

    print_success("Phase 3 complete!")
    print(f"   - Enriched datasets: {result['metadata']['total_datasets']}")
    print(f"   - Sample true flags (first dataset): {flag_count}/{total_flags}")

    return result


def run_phase4(phase3_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run Phase 4: Document Profiles.

    Applies three document profiles (SROGs, PODs, Admissions) to each dataset.

    Args:
        phase3_output: Output from Phase 3

    Returns:
        Collection with profile datasets
    """
    print_header("PHASE 4: DOCUMENT PROFILES")
    print_info("Applying document profiles (SROGs, PODs, Admissions)...")

    pipeline = ProfilePipeline()
    result = pipeline.apply_profiles_to_collection(phase3_output)

    print_success("Phase 4 complete!")
    print(f"   - Original datasets: {len(phase3_output.get('datasets', []))}")
    print(f"   - Profile datasets: {result['metadata']['total_profile_datasets']}")
    print(f"   - Profiles applied: {result['metadata']['profiles_applied']} (SROGs, PODs, Admissions)")

    return result


def run_phase5(phase4_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run Phase 5: Set Splitting.

    Splits profile datasets into sets with max 120 interrogatories per set.

    Args:
        phase4_output: Output from Phase 4

    Returns:
        Collection with split sets and filenames
    """
    print_header("PHASE 5: SET SPLITTING")
    print_info("Splitting profile datasets into sets (max 120 interrogatories)...")

    pipeline = SplittingPipeline(max_interrogatories_per_set=120)
    all_split_datasets = pipeline.split_all_datasets(phase4_output)

    # Count total sets across all datasets
    total_sets = 0
    for dataset in all_split_datasets:
        if 'metadata' in dataset:
            total_sets += dataset['metadata'].get('total_sets', 0)

    print_success("Phase 5 complete!")
    print(f"   - Profile datasets processed: {len(all_split_datasets)}")
    print(f"   - Total sets created: {total_sets}")

    # Wrap in a structure for consistency
    result = {
        'datasets': all_split_datasets,
        'metadata': {
            'total_split_datasets': len(all_split_datasets),
            'total_sets': total_sets,
            'max_interrogatories_per_set': 120
        }
    }

    return result


def main():
    """Main pipeline execution function."""

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Run legal discovery normalization pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--send-webhooks',
        action='store_true',
        help='Send Phase 5 sets to webhook after processing'
    )
    parser.add_argument(
        '--webhook-config',
        default='webhook_config.json',
        help='Path to webhook configuration file (default: webhook_config.json)'
    )
    args = parser.parse_args()

    # Print banner
    print("\n" + "=" * 70)
    print("  LEGAL DISCOVERY NORMALIZATION PIPELINE")
    print("  Phases 1-5: Complete Processing")
    if args.send_webhooks:
        print("  Webhook Sending: ENABLED")
    print("=" * 70)

    # Generate timestamp for output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        # Load input file
        print_header("LOADING INPUT FILE")
        input_file = "formtest.json"
        print_info(f"Loading {input_file}...")
        form_json = load_json_file(input_file)
        print_success(f"Loaded {input_file}")

        # Phase 1: Input Normalization
        phase1_output = run_phase1(form_json)
        phase1_file = f"output_phase1_{timestamp}.json"
        save_json_file(phase1_output, phase1_file)
        print_info(f"Saved to: {phase1_file}")

        # Phase 2: Dataset Builder
        phase2_output = run_phase2(phase1_output)
        phase2_file = f"output_phase2_{timestamp}.json"
        save_json_file(phase2_output, phase2_file)
        print_info(f"Saved to: {phase2_file}")

        # Phase 3: Flag Processors
        phase3_output = run_phase3(phase2_output)
        phase3_file = f"output_phase3_{timestamp}.json"
        save_json_file(phase3_output, phase3_file)
        print_info(f"Saved to: {phase3_file}")

        # Phase 4: Document Profiles
        phase4_output = run_phase4(phase3_output)
        phase4_file = f"output_phase4_{timestamp}.json"
        save_json_file(phase4_output, phase4_file)
        print_info(f"Saved to: {phase4_file}")

        # Phase 5: Set Splitting
        phase5_output = run_phase5(phase4_output)
        phase5_file = f"output_phase5_{timestamp}.json"
        save_json_file(phase5_output, phase5_file)
        print_info(f"Saved to: {phase5_file}")

        # Optional: Send to webhook
        webhook_summary = None
        if args.send_webhooks:
            print_header("WEBHOOK SENDING")
            try:
                # Load webhook config
                webhook_config = load_webhook_config(args.webhook_config)
                print_info(f"Webhook URL: {webhook_config['webhook_url']}")
                print_info(f"Config: {args.webhook_config}")
                print()

                # Send all sets
                webhook_summary = send_all_sets(phase5_output, webhook_config, verbose=True)

            except FileNotFoundError as e:
                print_error(f"Webhook config not found: {e}")
                print_info("Continuing without webhook sending...")
            except Exception as e:
                print_error(f"Webhook sending error: {e}")
                print_info("Continuing...")

        # Print final summary
        print_header("PIPELINE COMPLETE")
        print_success("All phases completed successfully!")
        print("\nOutput files:")
        print(f"  1. {phase1_file} - Normalized form data")
        print(f"  2. {phase2_file} - HoH × Defendant datasets")
        print(f"  3. {phase3_file} - Enriched datasets with 180+ flags")
        print(f"  4. {phase4_file} - Profiled datasets (SROGs, PODs, Admissions)")
        print(f"  5. {phase5_file} - Split sets with max 120 interrogatories")

        if webhook_summary:
            print("\nWebhook Summary:")
            print(f"  - Total sets: {webhook_summary['total_sets']}")
            print(f"  - Succeeded: {webhook_summary['succeeded']}")
            print(f"  - Failed: {webhook_summary['failed']}")

        print("\n" + "=" * 70)

        # Exit with error if webhook sending failed
        if webhook_summary and webhook_summary['failed'] > 0:
            return 1

        return 0

    except FileNotFoundError as e:
        print_error(f"File not found: {e}")
        print_info("Make sure formtest.json exists in the current directory")
        return 1

    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON: {e}")
        return 1

    except Exception as e:
        print_error(f"Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
