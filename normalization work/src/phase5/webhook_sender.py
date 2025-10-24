"""
Webhook Sender Module

Sends Phase 5 sets to Docmosis rendering webhook.
"""

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests

# Import Dropbox service for cloud backup
try:
    from utils import dropbox_service
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False
    print("⚠️  Dropbox service not available (utils.dropbox_service not found)")


def load_webhook_config(config_path: str = "webhook_config.json") -> Dict[str, Any]:
    """
    Load webhook configuration from JSON file.

    Args:
        config_path: Path to webhook configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(
            f"Webhook config not found: {config_path}\n"
            f"Please create webhook_config.json with webhook_url and access_key"
        )

    with open(config_file, 'r') as f:
        config = json.load(f)

    # Validate required fields
    required_fields = ['webhook_url', 'access_key']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required config field: {field}")

    return config


def build_webhook_payload(set_data: Dict[str, Any], access_key: str) -> Dict[str, Any]:
    """
    Build webhook payload from set data.

    Args:
        set_data: Individual set from Phase 5 output
        access_key: Webhook access key

    Returns:
        Webhook payload ready to send

    Example:
        >>> set_data = {
        ...     "Template": "SROGsMaster.docx",
        ...     "OutputName": "John Doe vs ABC Corp - SROGs Set 1 of 2",
        ...     "HasMold": True,
        ...     # ... other fields
        ... }
        >>> payload = build_webhook_payload(set_data, "key123")
        >>> payload['templateName']
        'SROGsMaster.docx'
    """
    return {
        "data": set_data,
        "accessKey": access_key,
        "templateName": set_data.get("Template", ""),
        "outputName": set_data.get("OutputName", "")
    }


def send_set_to_webhook(
    set_data: Dict[str, Any],
    config: Dict[str, Any],
    attempt: int = 1,
    dataset: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send a single set to the webhook.

    Args:
        set_data: Individual set from Phase 5 output
        config: Webhook configuration
        attempt: Current attempt number (for retry logic)
        dataset: Dataset metadata for the current set (used for output folders)

    Returns:
        Dictionary with:
        - success: Boolean indicating success/failure
        - status_code: HTTP status code (if request was made)
        - response: Response data (if successful)
        - saved_file: Path to saved document (if one was downloaded)
        - error: Error message (if failed)
        - attempts: Number of attempts made

    Example:
        >>> config = load_webhook_config()
        >>> set_data = {...}
        >>> result = send_set_to_webhook(set_data, config)
        >>> if result['success']:
        ...     print(f"Sent successfully: {result['status_code']}")
    """
    webhook_url = config['webhook_url']
    access_key = config['access_key']
    timeout = config.get('timeout_seconds', 30)
    max_attempts = config.get('retry_attempts', 3)
    retry_delay = config.get('retry_delay_seconds', 2)

    # Build payload
    payload = build_webhook_payload(set_data, access_key)

    def sanitize_path_text(text: str, default: str = "document") -> str:
        """Convert a label into a filesystem-safe string while preserving spaces."""
        if not text:
            return default
        safe = text.replace("_", " ")
        safe = re.sub(r"[^A-Za-z0-9.\- ]+", " ", safe)
        safe = re.sub(r"\s+", " ", safe).strip()
        return safe or default

    def determine_extension(content_type: str, template_name: str) -> str:
        """Pick a reasonable file extension based on content-type or template."""
        content_type_map = {
            "application/pdf": ".pdf",
            "application/msword": ".doc",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
            "text/plain": ".txt"
        }
        if content_type in content_type_map:
            return content_type_map[content_type]
        template_ext = Path(template_name).suffix if template_name else ""
        return template_ext or ".bin"

    def strip_unit(address: Optional[str]) -> Optional[str]:
        """Remove trailing unit designators (Unit, Apt, #, Suite) from address."""
        if not address:
            return address
        pattern = r"(?:,?\s+)?(?:Unit|Apt\.?|Apartment|Suite|Ste\.?|#)\s+[A-Za-z0-9-]+$"
        return re.sub(pattern, "", address, flags=re.IGNORECASE).strip()

    def document_type_folder(raw_type: Optional[str]) -> str:
        """Map dataset document type into configured folder names."""
        if not raw_type:
            return "unknown"
        normalized = raw_type.strip().lower()
        mapping = {
            "admissions": "ADMISSIONS",
            "pods": "PODS",
            "pod": "PODS",
            "srogs": "SROGs",
            "shrogs": "SROGs"
        }
        return mapping.get(normalized, sanitize_path_text(raw_type, "other"))

    def resolve_output_directory(base_dir: Path) -> Path:
        """Build nested directory path from dataset metadata if available."""
        if not dataset:
            return base_dir

        case_meta = dataset.get('case_metadata', {}) if dataset else {}
        address = (
            case_meta.get('property_address')
            or case_meta.get('property_address_with_unit')
            or set_data.get('Case', {}).get('FullAddress', '')
        )
        address = strip_unit(address)
        hoh = set_data.get('HeadOfHousehold') or dataset.get('metadata', {}).get('head_of_household', '')
        doc_folder = document_type_folder(dataset.get('doc_type'))

        address_segment = sanitize_path_text(address, "Unknown Address")
        hoh_segment = sanitize_path_text(hoh, "Unknown HoH")
        doc_segment = sanitize_path_text(doc_folder, "discovery")

        path_segments = [
            base_dir,
            Path(address_segment),
            Path(hoh_segment),
            Path("Discovery Propounded"),
            Path(doc_segment)
        ]

        output_path = Path(path_segments[0])
        for segment in path_segments[1:]:
            output_path = output_path / segment

        return output_path

    try:
        # Send POST request
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=timeout
        )

        # Check if successful
        if response.status_code == 200:
            # Try to parse JSON response, but don't fail if it's not JSON
            try:
                response_data = response.json() if response.content else None
            except (json.JSONDecodeError, ValueError):
                # Response is not JSON - this is okay for document generation APIs
                # The API might return binary data (docx file) or plain text
                response_data = {
                    'content_type': response.headers.get('Content-Type', 'unknown'),
                    'content_length': len(response.content) if response.content else 0,
                    'raw_text': response.text[:200] if response.text else None,  # First 200 chars
                    'note': 'Response was not JSON (likely binary document or plain text)'
                }

            saved_file = None
            if response.content:
                content_type = response.headers.get('Content-Type', '').split(';', 1)[0].strip().lower()
                save_documents = config.get('save_documents', True)
                save_plain_text = config.get('save_plain_text', False)
                is_json = content_type == "application/json"
                is_plain_text = content_type.startswith("text/")

                if save_documents and (not is_json) and (save_plain_text or not is_plain_text):
                    base_dir = Path(config.get('output_directory', 'webhook_documents'))
                    output_dir = resolve_output_directory(base_dir)
                    output_dir.mkdir(parents=True, exist_ok=True)

                    base_name = sanitize_path_text(set_data.get('OutputName', ''), "document")
                    extension = determine_extension(content_type, set_data.get('Template', ''))
                    candidate = output_dir / f"{base_name}{extension}"

                    counter = 1
                    while candidate.exists():
                        candidate = output_dir / f"{base_name}_{counter}{extension}"
                        counter += 1

                    with open(candidate, 'wb') as f:
                        f.write(response.content)

                    saved_file = str(candidate)

                    # Upload to Dropbox (non-blocking, errors logged but don't fail the request)
                    if DROPBOX_AVAILABLE and dropbox_service.is_enabled():
                        try:
                            dropbox_result = dropbox_service.upload_file(saved_file, response.content)
                            if dropbox_result['success']:
                                print(f"✅ Dropbox upload successful: {dropbox_result['dropbox_path']}")
                            else:
                                print(f"⚠️  Dropbox upload failed: {dropbox_result.get('error', 'Unknown error')}")
                        except Exception as dropbox_error:
                            print(f"❌ Dropbox upload error: {dropbox_error}")

            return {
                'success': True,
                'status_code': response.status_code,
                'response': response_data,
                'saved_file': saved_file,
                'attempts': attempt
            }
        else:
            # Non-200 status code
            error_msg = f"HTTP {response.status_code}: {response.text}"

            # Retry if we haven't exceeded max attempts
            if attempt < max_attempts:
                time.sleep(retry_delay * attempt)  # Exponential backoff
                return send_set_to_webhook(set_data, config, attempt + 1, dataset)

            return {
                'success': False,
                'status_code': response.status_code,
                'error': error_msg,
                'attempts': attempt
            }

    except requests.exceptions.Timeout:
        error_msg = f"Request timeout after {timeout} seconds"

        # Retry if we haven't exceeded max attempts
        if attempt < max_attempts:
            time.sleep(retry_delay * attempt)
            return send_set_to_webhook(set_data, config, attempt + 1, dataset)

        return {
            'success': False,
            'error': error_msg,
            'attempts': attempt
        }

    except requests.exceptions.RequestException as e:
        error_msg = f"Request error: {str(e)}"

        # Retry if we haven't exceeded max attempts
        if attempt < max_attempts:
            time.sleep(retry_delay * attempt)
            return send_set_to_webhook(set_data, config, attempt + 1, dataset)

        return {
            'success': False,
            'error': error_msg,
            'attempts': attempt
        }

    except Exception as e:
        # Unexpected error, don't retry
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}",
            'attempts': attempt
        }


# Global progress tracking
_progress_cache = {}
_sse_consumers = {}  # Track active SSE connections

def update_progress(case_id: str, completed: int, total: int, current_doc: str = ""):
    """Update progress for a case with enhanced tracking for SSE"""
    _progress_cache[case_id] = {
        'completed': completed,
        'total': total,
        'current_doc': current_doc,
        'timestamp': time.time(),
        'status': 'in_progress'
    }
    
    # Log progress for debugging
    if total > 0:
        percent = int((completed / total) * 100)
        print(f"📊 Progress update for {case_id}: {completed}/{total} ({percent}%) - {current_doc}")

def update_progress_complete(case_id: str, total: int, output_url: str = ""):
    """Mark progress as complete with output URL"""
    _progress_cache[case_id] = {
        'completed': total,
        'total': total,
        'current_doc': '',
        'timestamp': time.time(),
        'status': 'complete',
        'output_url': output_url
    }
    print(f"✅ Job completed for {case_id}: {total} documents, URL: {output_url}")

def update_progress_error(case_id: str, error_code: str, error_message: str):
    """Mark progress as failed with error details"""
    _progress_cache[case_id] = {
        'completed': _progress_cache.get(case_id, {}).get('completed', 0),
        'total': _progress_cache.get(case_id, {}).get('total', 0),
        'current_doc': '',
        'timestamp': time.time(),
        'status': 'error',
        'error': error_message,
        'error_code': error_code
    }
    print(f"❌ Job failed for {case_id}: {error_code} - {error_message}")

def get_progress(case_id: str) -> Dict[str, Any]:
    """Get current progress for a case"""
    return _progress_cache.get(case_id, {
        'completed': 0, 
        'total': 0, 
        'current_doc': '', 
        'status': 'pending',
        'timestamp': time.time()
    })

def send_all_sets_with_progress(
    phase5_output: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
    case_id: str = "",
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Send all sets from Phase 5 output to webhook with progress tracking.

    After successful generation, creates a shareable Dropbox link to the
    address-level folder (e.g., /Current Clients/1331 Yorkshire Place NW)
    and includes it in the completion notification.

    Args:
        phase5_output: Complete Phase 5 output with datasets and sets
        config: Webhook configuration (loads from file if None)
        case_id: Case ID for progress tracking
        verbose: Whether to print progress messages

    Returns:
        Summary dictionary with webhook results

    Dropbox Integration:
        - Extracts address from first uploaded document's Dropbox path
        - Creates shareable link for address-level folder
        - Link is passed to frontend via progress completion notification
        - Frontend displays clickable link in success toast
    """
    # Load config if not provided
    if config is None:
        config = load_webhook_config()
    
    results = []
    succeeded = 0
    failed = 0
    total_sets = 0
    
    # Count total sets first
    for dataset in phase5_output.get('datasets', []):
        total_sets += len(dataset.get('sets', []))
    
    # Initialize progress
    if case_id:
        update_progress(case_id, 0, total_sets, "Starting document generation...")
    
    # Iterate through all datasets
    for dataset in phase5_output.get('datasets', []):
        # Iterate through all sets in this dataset
        for set_data in dataset.get('sets', []):
            # Get set information for logging
            output_name = set_data.get('OutputName', f'Set {len(results) + 1}')
            
            if verbose:
                print(f"Sending {output_name}...")
            
            # Update progress
            if case_id:
                update_progress(case_id, len(results), total_sets, f"Generating {output_name}...")
            
            # Send the set
            result = send_set_to_webhook(set_data, config, dataset=dataset)
            results.append(result)
            
            if result['success']:
                succeeded += 1
                if verbose:
                    print(f"✅ {output_name} sent successfully")
            else:
                failed += 1
                if verbose:
                    print(f"❌ {output_name} failed: {result.get('error', 'Unknown error')}")
    
    # Final progress update with completion status
    if case_id:
        if failed == 0:
            # All succeeded - mark as complete
            # Try to create Dropbox shared link to address-level folder
            dropbox_link = ""
            if DROPBOX_AVAILABLE and dropbox_service.is_enabled():
                try:
                    # Extract address-level folder from first successful result
                    for result in results:
                        if result.get('success') and result.get('saved_file'):
                            local_path = result['saved_file']
                            dropbox_path = dropbox_service.map_local_path_to_dropbox(local_path)

                            # Extract address-level folder (e.g., /Current Clients/1331 Yorkshire Place NW)
                            # Dropbox path format: /Current Clients/{address}/{hoh}/Discovery Propounded/{doc_type}/file.docx
                            parts = dropbox_path.split('/')
                            if len(parts) >= 3:
                                # Reconstruct address-level folder path
                                base_path = dropbox_service.DROPBOX_CONFIG['base_path']
                                address = parts[2] if len(parts) > 2 else None

                                if address:
                                    address_folder = f"{base_path}/{address}"
                                    print(f"📁 Creating Dropbox shared link for: {address_folder}")
                                    dropbox_link = dropbox_service.create_shared_link(address_folder)
                                    if dropbox_link:
                                        print(f"✅ Dropbox link created: {dropbox_link}")
                                    else:
                                        print("⚠️  Could not create Dropbox shared link")
                            break
                except Exception as link_error:
                    print(f"⚠️  Error creating Dropbox link: {link_error}")

            update_progress_complete(case_id, total_sets, dropbox_link)
        else:
            # Some failed - mark as error
            update_progress_error(case_id, "STORAGE_WRITE_FAIL", f"{failed} out of {total_sets} documents failed to generate")
    
    return {
        'total_sets': total_sets,
        'succeeded': succeeded,
        'failed': failed,
        'results': results
    }

def send_all_sets(
    phase5_output: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Send all sets from Phase 5 output to webhook.

    Args:
        phase5_output: Complete Phase 5 output with datasets and sets
        config: Webhook configuration (loads from file if None)
        verbose: Whether to print progress messages

    Returns:
        Summary dictionary with:
        - total_sets: Total number of sets processed
        - succeeded: Number of sets successfully sent
        - failed: Number of sets that failed
        - results: List of individual results for each set

    Example:
        >>> phase5_output = json.load(open('output_phase5_20251017_145943.json'))
        >>> summary = send_all_sets(phase5_output)
        >>> print(f"Sent {summary['succeeded']}/{summary['total_sets']} sets")
    """
    # Load config if not provided
    if config is None:
        config = load_webhook_config()

    results = []
    succeeded = 0
    failed = 0
    total_sets = 0

    # Iterate through all datasets
    for dataset in phase5_output.get('datasets', []):
        # Iterate through all sets in this dataset
        for set_data in dataset.get('sets', []):
            total_sets += 1

            # Get set information for logging
            output_name = set_data.get('OutputName', f'Set {total_sets}')

            if verbose:
                print(f"🔄 Sending set {total_sets}: {output_name}")

            # Send to webhook
            result = send_set_to_webhook(set_data, config, dataset=dataset)
            result['set_name'] = output_name
            results.append(result)

            # Track success/failure
            if result['success']:
                succeeded += 1
                if verbose:
                    status = result.get('status_code', 200)
                    attempts = result.get('attempts', 1)
                    retry_msg = f" (after {attempts} attempts)" if attempts > 1 else ""
                    print(f"   ✅ Success [{status}]{retry_msg}")
            else:
                failed += 1
                if verbose:
                    error = result.get('error', 'Unknown error')
                    print(f"   ❌ Failed: {error}")

    # Build summary
    summary = {
        'total_sets': total_sets,
        'succeeded': succeeded,
        'failed': failed,
        'results': results
    }

    if verbose:
        print(f"\n{'='*70}")
        print(f"✅ Webhook sending complete!")
        print(f"   - Total sets: {total_sets}")
        print(f"   - Succeeded: {succeeded}")
        print(f"   - Failed: {failed}")
        if failed > 0:
            print(f"\n❌ Failed sets:")
            for result in results:
                if not result['success']:
                    print(f"   - {result['set_name']}: {result['error']}")

    return summary


# Module-level convenience function
def send_phase5_file(
    phase5_file: str,
    config_file: str = "webhook_config.json",
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Load Phase 5 output file and send all sets to webhook.

    Args:
        phase5_file: Path to Phase 5 output JSON file
        config_file: Path to webhook configuration file
        verbose: Whether to print progress messages

    Returns:
        Summary dictionary from send_all_sets()

    Example:
        >>> summary = send_phase5_file('output_phase5_20251017_145943.json')
    """
    # Load Phase 5 output
    with open(phase5_file, 'r') as f:
        phase5_output = json.load(f)

    # Load config
    config = load_webhook_config(config_file)

    if verbose:
        print(f"{'='*70}")
        print(f"  WEBHOOK SENDING")
        print(f"  File: {phase5_file}")
        print(f"  Webhook: {config['webhook_url']}")
        print(f"{'='*70}\n")

    # Send all sets
    return send_all_sets(phase5_output, config, verbose)
