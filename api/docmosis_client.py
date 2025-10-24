"""
Docmosis Document Generation Client

Handles communication with Docmosis Tornado API for generating legal documents.
Sends form data to docs.liptonlegal.com/api/render and retrieves generated PDFs.
"""
import os
import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DocmosisClient:
    """Client for Docmosis Tornado API"""

    def __init__(self):
        """Initialize Docmosis client with configuration from environment"""
        self.api_url = os.getenv('DOCMOSIS_API_URL', 'https://docs.liptonlegal.com/api/render')
        self.access_key = os.getenv('DOCMOSIS_ACCESS_KEY')  # Optional
        self.timeout = int(os.getenv('DOCMOSIS_TIMEOUT', '60'))
        self.max_retries = int(os.getenv('DOCMOSIS_RETRY_ATTEMPTS', '3'))

        logger.info(f"Docmosis client initialized: {self.api_url}")
        if self.access_key:
            logger.info("Docmosis access key configured")
        else:
            logger.info("Docmosis access key not set (using open access)")

    async def generate_document(
        self,
        template_name: str,
        data: Dict[str, Any],
        output_filename: str,
        output_format: str = 'pdf'
    ) -> Dict[str, Any]:
        """
        Generate a document using Docmosis Tornado API

        Args:
            template_name: Name of Docmosis template (e.g., 'LegalForm.docx')
            data: Form data to merge into template
            output_filename: Desired output filename
            output_format: Output format (pdf, docx, etc.)

        Returns:
            Dict with:
                - success: bool
                - document: bytes (PDF content)
                - filename: str
                - size: int (bytes)
                - error: str (if failed)
        """
        result = {
            'success': False,
            'document': None,
            'filename': output_filename,
            'size': 0,
            'error': None,
            'template': template_name
        }

        try:
            logger.info(f"Generating document: {output_filename} using template {template_name}")

            # Prepare request payload for Docmosis
            payload = {
                'templateName': template_name,
                'outputName': output_filename,
                'outputFormat': output_format,
                'data': data
            }

            # Add access key only if configured (optional)
            if self.access_key:
                payload['accessKey'] = self.access_key
                logger.debug("Including access key in request")

            # Make request to Docmosis API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"Sending request to {self.api_url}")

                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/pdf'
                    }
                )

                # Check response
                if response.status_code == 200:
                    document_bytes = response.content
                    result['success'] = True
                    result['document'] = document_bytes
                    result['size'] = len(document_bytes)
                    logger.info(f"✅ Document generated successfully: {output_filename} ({result['size']} bytes)")
                else:
                    error_msg = f"Docmosis API returned {response.status_code}: {response.text}"
                    result['error'] = error_msg
                    logger.error(f"❌ Document generation failed: {error_msg}")

        except httpx.TimeoutException as e:
            result['error'] = f"Request timeout after {self.timeout}s: {str(e)}"
            logger.error(f"❌ Docmosis timeout: {result['error']}")

        except httpx.RequestError as e:
            result['error'] = f"Request error: {str(e)}"
            logger.error(f"❌ Docmosis request error: {result['error']}")

        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
            logger.exception(f"❌ Unexpected error generating document: {e}")

        return result

    async def generate_case_documents(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        templates: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate all documents for a legal case

        Args:
            case_id: UUID of the case
            case_data: Complete case data from database
            templates: List of template names (default: all case templates)

        Returns:
            Dict with:
                - total: int (number of documents attempted)
                - successful: int (number generated successfully)
                - failed: int (number that failed)
                - documents: List[Dict] (details for each document)
        """
        if templates is None:
            # Default templates for legal forms
            templates = [
                'ComplaintForm.docx',
                'DiscoveryRequest.docx',
                'SummonsForm.docx'
            ]

        results = {
            'total': len(templates),
            'successful': 0,
            'failed': 0,
            'documents': []
        }

        logger.info(f"Generating {len(templates)} documents for case {case_id}")

        for template in templates:
            # Generate output filename
            output_filename = f"{case_id}_{template.replace('.docx', '')}.pdf"

            # Generate document
            doc_result = await self.generate_document(
                template_name=template,
                data=case_data,
                output_filename=output_filename
            )

            if doc_result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1

            results['documents'].append(doc_result)

        logger.info(
            f"Document generation complete for case {case_id}: "
            f"{results['successful']}/{results['total']} successful"
        )

        return results

    def is_configured(self) -> bool:
        """Check if Docmosis client is properly configured"""
        # Docmosis is configured as long as we have the API URL
        # Access key is optional depending on Docmosis server setup
        return bool(self.api_url)


# Singleton instance
_docmosis_client = None

def get_docmosis_client() -> DocmosisClient:
    """Get singleton Docmosis client instance"""
    global _docmosis_client
    if _docmosis_client is None:
        _docmosis_client = DocmosisClient()
    return _docmosis_client
