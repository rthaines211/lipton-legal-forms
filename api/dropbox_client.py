"""
Dropbox Upload Client for Python Pipeline

Handles uploading generated documents to Dropbox for cloud storage and backup.
"""
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


class DropboxClient:
    """Client for uploading documents to Dropbox"""

    def __init__(self):
        """Initialize Dropbox client with configuration from environment"""
        self.access_token = os.getenv('DROPBOX_ACCESS_TOKEN')
        self.base_path = os.getenv('DROPBOX_BASE_PATH', '/Apps/LegalFormApp')
        self.enabled = os.getenv('DROPBOX_ENABLED', 'false').lower() == 'true'
        self.upload_url = 'https://content.dropboxapi.com/2/files/upload'

        if self.enabled and not self.access_token:
            logger.warning("Dropbox enabled but DROPBOX_ACCESS_TOKEN not set - uploads will fail")

        if self.enabled:
            logger.info(f"Dropbox client initialized: {self.base_path}")
        else:
            logger.info("Dropbox client disabled")

    async def upload_document(
        self,
        document_bytes: bytes,
        dropbox_path: str,
        overwrite: bool = True
    ) -> Dict[str, Any]:
        """
        Upload a document to Dropbox

        Args:
            document_bytes: Binary content of the document
            dropbox_path: Path in Dropbox (e.g., '/Cases/case-123/document.pdf')
            overwrite: Whether to overwrite existing file

        Returns:
            Dict with:
                - success: bool
                - dropbox_path: str (full path in Dropbox)
                - size: int (bytes uploaded)
                - error: str (if failed)
        """
        result = {
            'success': False,
            'dropbox_path': None,
            'size': 0,
            'error': None
        }

        if not self.enabled:
            result['error'] = 'Dropbox upload disabled'
            return result

        if not self.access_token:
            result['error'] = 'Dropbox access token not configured'
            logger.error("❌ Cannot upload - no access token")
            return result

        try:
            # Build full Dropbox path
            full_path = f"{self.base_path}/{dropbox_path}".replace('//', '/')

            logger.info(f"📤 Uploading to Dropbox: {full_path} ({len(document_bytes)} bytes)")

            # Prepare Dropbox API headers
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/octet-stream',
                'Dropbox-API-Arg': f'{{"path": "{full_path}", "mode": "{{".\tag": "{"overwrite" if overwrite else "add"}"}}"}}'
            }

            # Upload to Dropbox
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.upload_url,
                    headers=headers,
                    content=document_bytes
                )

                if response.status_code == 200:
                    result['success'] = True
                    result['dropbox_path'] = full_path
                    result['size'] = len(document_bytes)
                    logger.info(f"✅ Dropbox upload successful: {full_path}")
                else:
                    error_msg = f"Dropbox API returned {response.status_code}: {response.text}"
                    result['error'] = error_msg
                    logger.error(f"❌ Dropbox upload failed: {error_msg}")

        except httpx.TimeoutException as e:
            result['error'] = f"Upload timeout: {str(e)}"
            logger.error(f"❌ Dropbox timeout: {result['error']}")

        except httpx.RequestError as e:
            result['error'] = f"Request error: {str(e)}"
            logger.error(f"❌ Dropbox request error: {result['error']}")

        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
            logger.exception(f"❌ Unexpected error uploading to Dropbox: {e}")

        return result

    async def upload_case_documents(
        self,
        case_id: str,
        documents: list
    ) -> Dict[str, Any]:
        """
        Upload all documents for a case to Dropbox

        Args:
            case_id: UUID of the case
            documents: List of document dicts with 'filename' and 'document' (bytes)

        Returns:
            Dict with:
                - total: int
                - successful: int
                - failed: int
                - uploads: List[Dict] (details for each upload)
        """
        results = {
            'total': len(documents),
            'successful': 0,
            'failed': 0,
            'uploads': []
        }

        if not self.enabled:
            logger.info("Dropbox disabled, skipping uploads")
            return results

        logger.info(f"Uploading {len(documents)} documents for case {case_id}")

        for doc in documents:
            if not doc.get('success') or not doc.get('document'):
                logger.warning(f"Skipping upload for failed document: {doc.get('filename')}")
                results['failed'] += 1
                results['uploads'].append({
                    'filename': doc.get('filename'),
                    'success': False,
                    'error': 'Document generation failed'
                })
                continue

            # Create Dropbox path: /Cases/{case_id}/{filename}
            dropbox_path = f"Cases/{case_id}/{doc['filename']}"

            # Upload document
            upload_result = await self.upload_document(
                document_bytes=doc['document'],
                dropbox_path=dropbox_path
            )

            if upload_result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1

            results['uploads'].append({
                'filename': doc['filename'],
                **upload_result
            })

        logger.info(
            f"Dropbox uploads complete for case {case_id}: "
            f"{results['successful']}/{results['total']} successful"
        )

        return results

    def is_enabled(self) -> bool:
        """Check if Dropbox uploads are enabled and configured"""
        return self.enabled and bool(self.access_token)


# Singleton instance
_dropbox_client = None

def get_dropbox_client() -> DropboxClient:
    """Get singleton Dropbox client instance"""
    global _dropbox_client
    if _dropbox_client is None:
        _dropbox_client = DropboxClient()
    return _dropbox_client
