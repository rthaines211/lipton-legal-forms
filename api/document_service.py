"""
Document Generation Service

Orchestrates document generation workflow:
1. Fetch case data from database
2. Generate documents via Docmosis
3. Upload documents to Dropbox
4. Track progress and status
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from api.docmosis_client import get_docmosis_client
from api.dropbox_client import get_dropbox_client
from api.database import execute_query, get_db_connection
from api.json_builder import JSONBuilderService

logger = logging.getLogger(__name__)


class DocumentGenerationService:
    """Service for generating and uploading case documents"""

    def __init__(self):
        """Initialize document generation service"""
        self.docmosis = get_docmosis_client()
        self.dropbox = get_dropbox_client()
        self.json_builder = JSONBuilderService()
        logger.info("Document generation service initialized")

    async def fetch_case_data(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch complete case data from database for document generation

        Args:
            case_id: UUID of the case

        Returns:
            Dict with all case data formatted for Docmosis templates
        """
        try:
            logger.info(f"Fetching case data for document generation: {case_id}")

            # Use JSON builder to get normalized case data
            case_json = await self.json_builder.build_case_json(case_id)

            if not case_json:
                logger.error(f"Case not found: {case_id}")
                return None

            logger.debug(f"Case data fetched successfully for {case_id}")
            return case_json

        except Exception as e:
            logger.exception(f"Error fetching case data: {e}")
            return None

    async def generate_documents_for_case(
        self,
        case_id: str,
        templates: list = None,
        upload_to_dropbox: bool = True
    ) -> Dict[str, Any]:
        """
        Generate all documents for a case

        Args:
            case_id: UUID of the case
            templates: List of template names (None = use defaults)
            upload_to_dropbox: Whether to upload generated docs to Dropbox

        Returns:
            Dict with:
                - case_id: str
                - success: bool
                - documents_generated: int
                - documents_uploaded: int (if Dropbox enabled)
                - documents: List[Dict] (details for each document)
                - dropbox_uploads: List[Dict] (upload results)
                - error: str (if failed)
        """
        result = {
            'case_id': case_id,
            'success': False,
            'documents_generated': 0,
            'documents_uploaded': 0,
            'documents': [],
            'dropbox_uploads': [],
            'error': None,
            'timestamp': datetime.utcnow().isoformat()
        }

        try:
            logger.info(f"Starting document generation for case {case_id}")

            # Step 1: Fetch case data
            case_data = await self.fetch_case_data(case_id)
            if not case_data:
                result['error'] = f"Case not found: {case_id}"
                logger.error(result['error'])
                return result

            # Step 2: Generate documents via Docmosis
            logger.info(f"Calling Docmosis to generate documents...")
            doc_results = await self.docmosis.generate_case_documents(
                case_id=case_id,
                case_data=case_data,
                templates=templates
            )

            result['documents'] = doc_results['documents']
            result['documents_generated'] = doc_results['successful']

            if doc_results['successful'] == 0:
                result['error'] = "No documents generated successfully"
                logger.error(result['error'])
                return result

            logger.info(
                f"✅ Generated {doc_results['successful']}/{doc_results['total']} documents"
            )

            # Step 3: Upload to Dropbox (if enabled)
            if upload_to_dropbox and self.dropbox.is_enabled():
                logger.info("Uploading documents to Dropbox...")
                upload_results = await self.dropbox.upload_case_documents(
                    case_id=case_id,
                    documents=doc_results['documents']
                )

                result['dropbox_uploads'] = upload_results['uploads']
                result['documents_uploaded'] = upload_results['successful']

                logger.info(
                    f"✅ Uploaded {upload_results['successful']}/{upload_results['total']} documents to Dropbox"
                )
            else:
                logger.info("Dropbox upload skipped (disabled or not configured)")

            # Mark as successful
            result['success'] = True

            logger.info(
                f"✅ Document generation complete for case {case_id}: "
                f"{result['documents_generated']} generated, "
                f"{result['documents_uploaded']} uploaded"
            )

        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
            logger.exception(f"❌ Document generation failed for case {case_id}: {e}")

        return result

    async def generate_single_document(
        self,
        case_id: str,
        template_name: str,
        upload_to_dropbox: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a single document for a case

        Args:
            case_id: UUID of the case
            template_name: Name of Docmosis template
            upload_to_dropbox: Whether to upload to Dropbox

        Returns:
            Dict with document generation result
        """
        try:
            logger.info(f"Generating single document for case {case_id}: {template_name}")

            # Fetch case data
            case_data = await self.fetch_case_data(case_id)
            if not case_data:
                return {
                    'success': False,
                    'error': f"Case not found: {case_id}"
                }

            # Generate output filename
            output_filename = f"{case_id}_{template_name.replace('.docx', '')}.pdf"

            # Generate document
            doc_result = await self.docmosis.generate_document(
                template_name=template_name,
                data=case_data,
                output_filename=output_filename
            )

            # Upload to Dropbox if successful and enabled
            if doc_result['success'] and upload_to_dropbox and self.dropbox.is_enabled():
                dropbox_path = f"Cases/{case_id}/{output_filename}"
                upload_result = await self.dropbox.upload_document(
                    document_bytes=doc_result['document'],
                    dropbox_path=dropbox_path
                )
                doc_result['dropbox_upload'] = upload_result

            return doc_result

        except Exception as e:
            logger.exception(f"Error generating single document: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def is_configured(self) -> bool:
        """Check if document generation is properly configured"""
        return self.docmosis.is_configured()


# Singleton instance
_document_service = None

def get_document_service() -> DocumentGenerationService:
    """Get singleton document generation service instance"""
    global _document_service
    if _document_service is None:
        _document_service = DocumentGenerationService()
    return _document_service
