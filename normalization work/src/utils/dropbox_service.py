"""
Dropbox Service Module

Handles all Dropbox API operations for uploading generated legal documents.
Preserves local folder structure when uploading to Dropbox.

Configuration (via environment variables):
- DROPBOX_ACCESS_TOKEN: OAuth token for Dropbox API authentication
- DROPBOX_ENABLED: Enable/disable Dropbox uploads (default: false)
- DROPBOX_BASE_PATH: Base folder path in Dropbox (default: /Current Clients)
- DROPBOX_LOCAL_OUTPUT_PATH: Local output directory to mirror (default: webhook_documents)
- DROPBOX_CONTINUE_ON_FAILURE: Continue on upload failure (default: true)

Features:
- Automatic folder creation in Dropbox
- File overwriting (preserves version history in Dropbox)
- Path mapping from local to Dropbox structure
- Comprehensive error handling and logging

Example Usage:
    from utils.dropbox_service import upload_file, is_enabled

    if is_enabled():
        result = upload_file('/path/to/document.docx')
        if result['success']:
            print(f"Uploaded to: {result['dropbox_path']}")

Last Updated: 2025-10-20
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

# Configure logging
logger = logging.getLogger(__name__)

# Dropbox Configuration from environment variables
DROPBOX_CONFIG = {
    'access_token': os.getenv('DROPBOX_ACCESS_TOKEN', ''),
    'enabled': os.getenv('DROPBOX_ENABLED', 'false').lower() == 'true',
    'base_path': os.getenv('DROPBOX_BASE_PATH', '/Current Clients'),
    'local_output_path': os.getenv('DROPBOX_LOCAL_OUTPUT_PATH', 'webhook_documents'),
    'continue_on_failure': os.getenv('DROPBOX_CONTINUE_ON_FAILURE', 'true').lower() == 'true'
}

# Initialize Dropbox client if enabled and token provided
_dbx_client = None
if DROPBOX_CONFIG['enabled'] and DROPBOX_CONFIG['access_token']:
    try:
        _dbx_client = dropbox.Dropbox(DROPBOX_CONFIG['access_token'])
        # Test connection
        _dbx_client.users_get_current_account()
        logger.info(f"✅ Dropbox service initialized")
        logger.info(f"   Base path: {DROPBOX_CONFIG['base_path']}")
    except AuthError as e:
        logger.error(f"❌ Dropbox authentication failed: {e}")
        _dbx_client = None
    except Exception as e:
        logger.error(f"❌ Dropbox initialization failed: {e}")
        _dbx_client = None
elif DROPBOX_CONFIG['enabled'] and not DROPBOX_CONFIG['access_token']:
    logger.warning("⚠️  Dropbox enabled but no access token provided. Uploads will be skipped.")
else:
    logger.info("ℹ️  Dropbox service disabled")


def is_enabled() -> bool:
    """
    Check if Dropbox integration is enabled and configured.

    Returns:
        True if Dropbox client is initialized, False otherwise
    """
    return _dbx_client is not None


def map_local_path_to_dropbox(local_path: str) -> str:
    """
    Maps a local file path to its corresponding Dropbox path.

    Args:
        local_path: Local file path (e.g., webhook_documents/Address/HoH/Discovery/SROGs/file.docx)

    Returns:
        Dropbox path (e.g., /Current Clients/Address/HoH/Discovery/SROGs/file.docx)

    Example:
        >>> map_local_path_to_dropbox('webhook_documents/123 Main St/John Doe/Discovery/SROGs/doc.docx')
        '/Current Clients/123 Main St/John Doe/Discovery/SROGs/doc.docx'
    """
    # Convert to Path object and normalize
    local_path_obj = Path(local_path)
    local_output_path = Path(DROPBOX_CONFIG['local_output_path'])

    # Get relative path from local output directory
    try:
        relative_path = local_path_obj.relative_to(local_output_path)
    except ValueError:
        # Path is not relative to local_output_path, try to find it
        # Convert to string and look for the local output path
        local_str = str(local_path_obj)
        output_str = str(local_output_path)

        if output_str in local_str:
            # Found it, extract the part after the output path
            idx = local_str.index(output_str)
            relative_str = local_str[idx + len(output_str):].lstrip('/')
            relative_path = Path(relative_str)
        else:
            # Can't find local output path, use the filename only
            logger.warning(f"⚠️  Could not find '{output_str}' in '{local_str}', using filename only")
            relative_path = Path(local_path_obj.name)

    # Combine base path with relative path
    dropbox_path = f"{DROPBOX_CONFIG['base_path']}/{relative_path}".replace('\\', '/')

    # Ensure no double slashes
    while '//' in dropbox_path:
        dropbox_path = dropbox_path.replace('//', '/')

    return dropbox_path


def ensure_folder_exists(folder_path: str) -> bool:
    """
    Creates a folder in Dropbox if it doesn't exist.

    Args:
        folder_path: Dropbox folder path to create

    Returns:
        True if folder exists or was created successfully, False otherwise
    """
    if not _dbx_client:
        return False

    try:
        # Check if folder exists
        _dbx_client.files_get_metadata(folder_path)
        return True
    except ApiError as e:
        error = e.error
        if hasattr(error, 'is_path') and error.is_path():
            # Folder doesn't exist, create it
            try:
                _dbx_client.files_create_folder_v2(folder_path)
                logger.info(f"📁 Created Dropbox folder: {folder_path}")
                return True
            except ApiError as create_error:
                logger.error(f"❌ Failed to create Dropbox folder {folder_path}: {create_error}")
                return False
        else:
            logger.error(f"❌ Error checking Dropbox folder {folder_path}: {e}")
            return False


def ensure_parent_folders_exist(dropbox_path: str) -> bool:
    """
    Recursively creates all parent folders for a given Dropbox path.

    Args:
        dropbox_path: Full Dropbox file path

    Returns:
        True if all folders exist or were created successfully

    Example:
        >>> ensure_parent_folders_exist('/Current Clients/Address/HoH/Discovery/SROGs/file.docx')
        # Creates: /Current Clients, /Current Clients/Address,
        #          /Current Clients/Address/HoH, etc.
    """
    if not _dbx_client:
        return False

    # Split path and build folders incrementally
    parts = [p for p in dropbox_path.split('/') if p]

    current_path = ''
    for i, part in enumerate(parts[:-1]):  # Exclude filename
        current_path += '/' + part

        # Skip base path if it's just the first level
        if i == 0 and current_path == DROPBOX_CONFIG['base_path']:
            continue

        success = ensure_folder_exists(current_path)
        if not success and not DROPBOX_CONFIG['continue_on_failure']:
            return False

    return True


def upload_file(local_file_path: str, file_content: Optional[bytes] = None) -> Dict[str, Any]:
    """
    Uploads a file to Dropbox, preserving the folder structure.

    Args:
        local_file_path: Absolute local file path
        file_content: File content (optional, will read from disk if not provided)

    Returns:
        Dictionary with upload result:
        {
            'success': bool,
            'local_path': str,
            'dropbox_path': str (if successful),
            'error': str (if failed)
        }

    Example:
        >>> result = upload_file('/path/to/document.docx')
        >>> if result['success']:
        ...     print(f"Uploaded to: {result['dropbox_path']}")
    """
    result = {
        'success': False,
        'local_path': local_file_path,
        'dropbox_path': None,
        'error': None
    }

    # Check if Dropbox is enabled
    if not DROPBOX_CONFIG['enabled']:
        result['error'] = 'Dropbox is disabled'
        return result

    if not _dbx_client:
        result['error'] = 'Dropbox client not initialized'
        return result

    try:
        # Map local path to Dropbox path
        dropbox_path = map_local_path_to_dropbox(local_file_path)
        result['dropbox_path'] = dropbox_path

        # Ensure parent folders exist
        folders_created = ensure_parent_folders_exist(dropbox_path)
        if not folders_created and not DROPBOX_CONFIG['continue_on_failure']:
            result['error'] = 'Failed to create parent folders'
            return result

        # Read file content if not provided
        if file_content is None:
            with open(local_file_path, 'rb') as f:
                file_content = f.read()

        # Upload file to Dropbox (overwrite if exists)
        _dbx_client.files_upload(
            file_content,
            dropbox_path,
            mode=WriteMode('overwrite'),
            autorename=False,
            mute=False
        )

        result['success'] = True
        logger.info(f"☁️  Uploaded to Dropbox: {local_file_path} → {dropbox_path}")

        return result

    except FileNotFoundError:
        result['error'] = f'Local file not found: {local_file_path}'
        logger.error(f"❌ {result['error']}")
        if not DROPBOX_CONFIG['continue_on_failure']:
            raise
        return result

    except ApiError as e:
        result['error'] = f'Dropbox API error: {e}'
        logger.error(f"❌ Dropbox upload failed for {local_file_path}: {e}")
        if not DROPBOX_CONFIG['continue_on_failure']:
            raise
        return result

    except Exception as e:
        result['error'] = f'Upload error: {e}'
        logger.error(f"❌ Dropbox upload error for {local_file_path}: {e}")
        if not DROPBOX_CONFIG['continue_on_failure']:
            raise
        return result


def upload_files(local_file_paths: list) -> list:
    """
    Uploads multiple files to Dropbox.

    Args:
        local_file_paths: List of absolute local file paths

    Returns:
        List of upload results (one dict per file)

    Example:
        >>> results = upload_files(['/path/file1.docx', '/path/file2.docx'])
        >>> success_count = sum(1 for r in results if r['success'])
        >>> print(f"Uploaded {success_count}/{len(results)} files")
    """
    if not DROPBOX_CONFIG['enabled'] or not _dbx_client:
        logger.info('ℹ️  Dropbox disabled, skipping batch upload')
        return [
            {
                'success': False,
                'local_path': path,
                'dropbox_path': None,
                'error': 'Dropbox is disabled'
            }
            for path in local_file_paths
        ]

    logger.info(f"📤 Uploading {len(local_file_paths)} files to Dropbox...")

    results = []
    for file_path in local_file_paths:
        result = upload_file(file_path)
        results.append(result)

    success_count = sum(1 for r in results if r['success'])
    logger.info(f"✅ Successfully uploaded {success_count}/{len(local_file_paths)} files to Dropbox")

    return results


def create_shared_link(folder_path: str) -> Optional[str]:
    """
    Create a shareable link for a Dropbox folder.
    If a shared link already exists, returns the existing link.

    Args:
        folder_path: Dropbox folder path (e.g., '/Current Clients/123 Main St')

    Returns:
        Shareable URL string, or None if failed

    Example:
        >>> link = create_shared_link('/Current Clients/123 Main St')
        >>> if link:
        ...     print(f"Share this link: {link}")
    """
    if not _dbx_client:
        logger.warning("⚠️  Cannot create shared link: Dropbox client not initialized")
        return None

    try:
        # Try to create a new shared link
        shared_link_metadata = _dbx_client.sharing_create_shared_link_with_settings(folder_path)
        link_url = shared_link_metadata.url
        logger.info(f"✅ Created Dropbox shared link for: {folder_path}")
        return link_url

    except ApiError as e:
        error = e.error
        # Check if error is because a shared link already exists
        if hasattr(error, 'is_shared_link_already_exists') and error.is_shared_link_already_exists():
            # Get existing shared links for this folder
            try:
                links = _dbx_client.sharing_list_shared_links(path=folder_path, direct_only=True)
                if links.links:
                    link_url = links.links[0].url
                    logger.info(f"✅ Retrieved existing Dropbox shared link for: {folder_path}")
                    return link_url
                else:
                    logger.warning(f"⚠️  Shared link exists but couldn't retrieve it for: {folder_path}")
                    return None
            except Exception as retrieve_error:
                logger.error(f"❌ Failed to retrieve existing shared link for {folder_path}: {retrieve_error}")
                return None
        else:
            logger.error(f"❌ Failed to create shared link for {folder_path}: {e}")
            return None

    except Exception as e:
        logger.error(f"❌ Unexpected error creating shared link for {folder_path}: {e}")
        return None


def get_config() -> Dict[str, Any]:
    """
    Get current Dropbox configuration.

    Returns:
        Configuration dictionary (access token is masked)
    """
    config_copy = DROPBOX_CONFIG.copy()
    if config_copy['access_token']:
        config_copy['access_token'] = '***' + config_copy['access_token'][-10:]
    return config_copy


# Export main functions
__all__ = [
    'is_enabled',
    'upload_file',
    'upload_files',
    'map_local_path_to_dropbox',
    'create_shared_link',
    'get_config'
]
