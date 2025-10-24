"""
API routes for the normalization pipeline.

This module defines REST API endpoints for executing the discovery document
normalization pipeline and checking service status.

PERFORMANCE NOTE:
- The /api/normalize endpoint uses asyncio.to_thread() to run the synchronous
  pipeline in a background thread. This prevents blocking FastAPI's event loop,
  allowing /api/progress requests to be processed concurrently during document
  generation. Without this, progress requests would timeout waiting for the
  pipeline to complete.
"""

import os
import logging
import time
import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Header, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Import pipeline functions
from run_pipeline import (
    run_phase1,
    run_phase2,
    run_phase3,
    run_phase4,
    run_phase5
)
from src.phase5.webhook_sender import send_all_sets, send_all_sets_with_progress, load_webhook_config, get_progress

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


class NormalizeRequest(BaseModel):
    """
    Request model for form normalization.

    Attributes:
        Form: Form metadata (Id, InternalName, Name)
        PlaintiffDetails: List of plaintiff objects with discovery data
        DefendantDetails2: List of defendant objects
        Full_Address: Address information object
        case_id: Database case ID for progress tracking (optional)
    """
    Form: Dict[str, Any] = Field(..., description="Form metadata")
    PlaintiffDetails: list = Field(default=[], description="List of plaintiffs")
    DefendantDetails2: list = Field(default=[], description="List of defendants")
    Full_Address: Dict[str, Any] = Field(default={}, description="Property address")
    case_id: Optional[str] = Field(default=None, description="Database case ID for SSE progress tracking")

    class Config:
        json_schema_extra = {
            "example": {
                "Form": {
                    "Id": "1",
                    "InternalName": "AutoPopulationForm",
                    "Name": "Legal Discovery Form"
                },
                "PlaintiffDetails": [
                    {
                        "Id": "1",
                        "FirstName": "John",
                        "LastName": "Doe",
                        "IsHeadOfHousehold": True,
                        "Discovery": {
                            "Vermin": ["RatsMice", "Bedbugs"],
                            "Environmental": ["Mold", "LeadPaint"]
                        }
                    }
                ],
                "DefendantDetails2": [
                    {
                        "Id": "1",
                        "FirstName": "Jane",
                        "LastName": "Smith",
                        "EntityType": "LLC"
                    }
                ],
                "Full_Address": {
                    "Street": "123 Main St",
                    "City": "New York",
                    "State": "NY",
                    "PostalCode": "10001"
                }
            }
        }


class NormalizeResponse(BaseModel):
    """
    Response model for successful normalization.

    Attributes:
        success: Whether the pipeline completed successfully
        case_id: Unique case identifier
        execution_time_ms: Total execution time in milliseconds
        phase_results: Summary of results from each phase
        webhook_summary: Summary of webhook delivery (if enabled)
    """
    success: bool = Field(..., description="Pipeline execution success status")
    case_id: str = Field(..., description="Unique case identifier")
    execution_time_ms: int = Field(..., description="Total execution time in milliseconds")
    phase_results: Dict[str, Any] = Field(..., description="Results from each phase")
    webhook_summary: Optional[Dict[str, Any]] = Field(None, description="Webhook delivery summary")


class ErrorResponse(BaseModel):
    """
    Response model for errors.

    Attributes:
        success: Always False for errors
        error: Error message
        phase_failed: Which phase failed (if applicable)
        partial_results: Any results computed before failure
    """
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    phase_failed: Optional[str] = Field(None, description="Phase that failed")
    partial_results: Optional[Dict[str, Any]] = Field(None, description="Partial results before failure")


async def verify_api_key(x_api_key: str = Header(None)) -> Optional[str]:
    """
    Verify API key from request header.

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        The API key if valid

    Raises:
        HTTPException: If API key is invalid or missing
    """
    expected_key = os.getenv("API_KEY")

    # If no API key is configured, skip authentication
    if not expected_key:
        logger.warning("API_KEY not configured - authentication disabled")
        return None

    # Check if key is provided
    if not x_api_key:
        raise HTTPException(status_code=403, detail="Missing API key in X-API-Key header")

    # Verify key
    if x_api_key != expected_key:
        raise HTTPException(status_code=403, detail="Invalid API key")

    return x_api_key


def run_complete_pipeline(form_json: Dict[str, Any], send_webhooks: bool = True) -> Dict[str, Any]:
    """
    Execute the complete normalization pipeline (phases 1-5).

    This function runs all five phases of the pipeline:
    1. Input Normalization - Transform raw form data
    2. Dataset Builder - Create HoH × Defendant datasets
    3. Flag Processors - Apply 180+ boolean flags
    4. Document Profiles - Apply SROGs, PODs, Admissions profiles
    5. Set Splitting - Split into sets of max 120 interrogatories

    Args:
        form_json: Raw form data from the web application
        send_webhooks: Whether to send results to Docmosis webhook

    Returns:
        Dictionary containing:
            - success: bool
            - case_id: str
            - execution_time_ms: int
            - phase_results: dict with results from each phase
            - webhook_summary: dict (if webhooks enabled)

    Raises:
        Exception: If any phase fails
    """
    start_time = time.time()
    results = {}

    try:
        # Phase 1: Input Normalization
        logger.info("Starting Phase 1: Input Normalization")
        phase1_output = run_phase1(form_json)

        # Use the UUID case ID from the request instead of form ID
        # CRITICAL: This must be the database UUID, not the form's internal ID
        request_case_id = form_json.get('case_id')
        phase1_case_id = phase1_output.get('case_info', {}).get('case_id', 'unknown')
        case_id = request_case_id if request_case_id else phase1_case_id

        logger.info(f"🔍 Case ID determination:")
        logger.info(f"   Request case_id: {request_case_id}")
        logger.info(f"   Phase1 case_id: {phase1_case_id}")
        logger.info(f"   Using case_id: {case_id}")

        results['phase1'] = {
            'plaintiffs': len(phase1_output.get('plaintiffs', [])),
            'defendants': len(phase1_output.get('defendants', [])),
            'case_id': case_id
        }
        logger.info(f"Phase 1 complete: {results['phase1']}")

        # Phase 2: Dataset Builder
        logger.info("Starting Phase 2: Dataset Builder")
        phase2_output = run_phase2(phase1_output)
        results['phase2'] = {
            'datasets': phase2_output['metadata']['total_datasets'],
            'hoh_count': phase2_output['metadata']['hoh_count'],
            'defendant_count': phase2_output['metadata']['defendant_count']
        }
        logger.info(f"Phase 2 complete: {results['phase2']}")

        # Phase 3: Flag Processors
        logger.info("Starting Phase 3: Flag Processors")
        phase3_output = run_phase3(phase2_output)

        # Count flags in first dataset
        if phase3_output.get('datasets') and len(phase3_output['datasets']) > 0:
            first_dataset = phase3_output['datasets'][0]
            flag_count = len([k for k, v in first_dataset.get('flags', {}).items() if v is True])
            total_flags = len(first_dataset.get('flags', {}))
        else:
            flag_count = 0
            total_flags = 0

        results['phase3'] = {
            'datasets': phase3_output['metadata']['total_datasets'],
            'flags_applied': total_flags,
            'sample_true_flags': flag_count
        }
        logger.info(f"Phase 3 complete: {results['phase3']}")

        # Phase 4: Document Profiles
        logger.info("Starting Phase 4: Document Profiles")
        phase4_output = run_phase4(phase3_output)
        results['phase4'] = {
            'profile_datasets': phase4_output['metadata']['total_profile_datasets'],
            'profiles_applied': phase4_output['metadata']['profiles_applied']
        }
        logger.info(f"Phase 4 complete: {results['phase4']}")

        # Phase 5: Set Splitting
        logger.info("Starting Phase 5: Set Splitting")
        phase5_output = run_phase5(phase4_output)
        results['phase5'] = {
            'split_datasets': phase5_output['metadata']['total_split_datasets'],
            'total_sets': phase5_output['metadata']['total_sets'],
            'max_per_set': phase5_output['metadata']['max_interrogatories_per_set']
        }
        logger.info(f"Phase 5 complete: {results['phase5']}")

        # Optional: Send webhooks
        webhook_summary = None
        if send_webhooks:
            try:
                logger.info("Sending webhooks...")
                webhook_config_path = os.getenv("WEBHOOK_CONFIG_PATH", "webhook_config.json")
                webhook_config = load_webhook_config(webhook_config_path)

                # Override with environment variables if set
                if os.getenv("WEBHOOK_URL"):
                    webhook_config['webhook_url'] = os.getenv("WEBHOOK_URL")
                if os.getenv("WEBHOOK_ACCESS_KEY"):
                    webhook_config['access_key'] = os.getenv("WEBHOOK_ACCESS_KEY")

                # Send webhooks with progress tracking
                logger.info(f"Starting webhook sending with progress tracking for case: {case_id}")
                webhook_summary = send_all_sets_with_progress(phase5_output, webhook_config, case_id, verbose=True)
                logger.info(f"Webhooks sent: {webhook_summary}")

            except Exception as webhook_error:
                logger.error(f"Webhook sending failed: {webhook_error}", exc_info=True)
                # Don't fail the entire pipeline if webhooks fail
                webhook_summary = {
                    'total_sets': results['phase5']['total_sets'],
                    'succeeded': 0,
                    'failed': results['phase5']['total_sets'],
                    'error': str(webhook_error)
                }

        # Calculate execution time
        execution_time_ms = int((time.time() - start_time) * 1000)

        # Build response
        response = {
            'success': True,
            'case_id': case_id,
            'execution_time_ms': execution_time_ms,
            'phase_results': results
        }

        if webhook_summary:
            response['webhook_summary'] = webhook_summary

        logger.info(f"Pipeline complete in {execution_time_ms}ms")
        return response

    except Exception as e:
        # Determine which phase failed
        phase_failed = None
        if 'phase1' not in results:
            phase_failed = 'phase1'
        elif 'phase2' not in results:
            phase_failed = 'phase2'
        elif 'phase3' not in results:
            phase_failed = 'phase3'
        elif 'phase4' not in results:
            phase_failed = 'phase4'
        elif 'phase5' not in results:
            phase_failed = 'phase5'

        logger.error(f"Pipeline failed at {phase_failed}: {e}", exc_info=True)

        raise Exception(f"Pipeline failed at {phase_failed}: {str(e)}")


@router.post("/api/normalize", response_model=NormalizeResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad request or validation error"},
    403: {"model": ErrorResponse, "description": "Invalid API key"},
    500: {"model": ErrorResponse, "description": "Pipeline execution error"}
})
async def normalize_form(
    request: NormalizeRequest,
    api_key: Optional[str] = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Execute the normalization pipeline on form data.

    This endpoint accepts form data from the web application, runs it through
    all 5 phases of the normalization pipeline, and optionally sends the results
    to the Docmosis webhook for document generation.

    **Authentication**: Requires X-API-Key header if API_KEY is configured.

    **Request Body**: Form data matching the legal discovery form structure.

    **Response**: Execution results including case ID, phase summaries, and webhook status.

    **Error Handling**: If the pipeline fails, the response will include which phase
    failed and any partial results computed before the failure.

    Args:
        request: Form data to normalize
        api_key: API key from header (validated by dependency)

    Returns:
        Normalization results with phase summaries

    Raises:
        HTTPException: If pipeline execution fails
    """
    try:
        # Convert request to dict
        form_json = request.dict()

        # CRITICAL DEBUG: Check if case_id is in the request
        logger.info(f"📦 Received request keys: {', '.join(form_json.keys())}")
        if 'case_id' in form_json:
            logger.info(f"✅ case_id found in request: {form_json['case_id']}")
        else:
            logger.warning(f"❌ case_id NOT found in request!")

        # Check if webhooks should be sent
        send_webhooks = os.getenv("ENABLE_WEBHOOKS", "true").lower() == "true"

        # Run pipeline in background thread to avoid blocking the event loop
        # This allows /api/progress requests to be processed while documents generate
        logger.info(f"Starting pipeline for form: {form_json.get('Form', {}).get('Id', 'unknown')}")
        logger.info("🔄 Running pipeline in background thread to allow concurrent progress requests...")
        result = await asyncio.to_thread(run_complete_pipeline, form_json, send_webhooks)
        logger.info("✅ Pipeline completed in background thread")

        return result

    except Exception as e:
        logger.error(f"Pipeline execution error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "phase_failed": "unknown"
            }
        )


@router.get("/api/progress/{case_id}")
async def get_progress_status(case_id: str) -> Dict[str, Any]:
    """
    Get real-time progress for document generation.
    
    Args:
        case_id: Case ID to get progress for
        
    Returns:
        Progress information including completed/total documents
    """
    progress = get_progress(case_id)
    logger.info(f"Progress requested for case {case_id}: {progress}")
    return {
        'case_id': case_id,
        'completed': progress.get('completed', 0),
        'total': progress.get('total', 0),
        'current_doc': progress.get('current_doc', ''),
        'progress_percent': int((progress.get('completed', 0) / max(progress.get('total', 1), 1)) * 100)
    }

@router.get("/api/status")
async def get_status() -> Dict[str, Any]:
    """
    Get API service status and configuration.

    Returns information about the service configuration, including
    whether webhooks are enabled and basic health information.

    Returns:
        Service status information
    """
    return {
        "status": "running",
        "service": "normalization-api",
        "version": "1.0.0",
        "configuration": {
            "webhooks_enabled": os.getenv("ENABLE_WEBHOOKS", "true").lower() == "true",
            "webhook_url": os.getenv("WEBHOOK_URL", "not configured"),
            "api_key_required": bool(os.getenv("API_KEY")),
            "debug_mode": os.getenv("SAVE_DEBUG_FILES", "false").lower() == "true"
        }
    }


@router.get("/api/jobs/{job_id}/stream")
async def stream_job_progress(job_id: str):
    """
    Stream real-time progress updates for document generation via Server-Sent Events.
    
    This endpoint provides a persistent connection that streams progress events
    as documents are generated. Events include progress updates, completion
    notifications, and error messages.
    
    Args:
        job_id: Case ID to track progress for
        
    Returns:
        StreamingResponse with text/event-stream content type
        
    Events:
        - progress: Current progress update with completed/total counts
        - complete: Job completed successfully with output URL
        - error: Job failed with error code and message
    """
    async def event_generator():
        """Generate SSE events for job progress"""
        last_heartbeat = time.time()
        heartbeat_interval = 20  # Send heartbeat every 20 seconds
        last_progress = None
        
        try:
            while True:
                # Get current progress for this job
                progress = get_progress(job_id)
                
                # Check if we have new progress data
                current_progress = {
                    'completed': progress.get('completed', 0),
                    'total': progress.get('total', 0),
                    'current_doc': progress.get('current_doc', ''),
                    'timestamp': progress.get('timestamp', 0)
                }
                
                # Send progress event if we have new data
                # Note: We send events even when total=0 to show "initializing" state
                if current_progress != last_progress:
                    progress_event = {
                        "jobId": job_id,
                        "current": current_progress['completed'],
                        "total": current_progress['total'],
                        "message": f"Generating {current_progress['current_doc']}" if current_progress['current_doc'] else "Processing documents..."
                    }

                    yield f"event: progress\n"
                    yield f"data: {json.dumps(progress_event)}\n\n"

                    last_progress = current_progress

                    # Check if job is complete (only when we have a valid total)
                    if current_progress['total'] > 0 and current_progress['completed'] >= current_progress['total']:
                        # Send completion event
                        complete_event = {
                            "jobId": job_id,
                            "total": current_progress['total'],
                            "outputUrl": progress.get('output_url', '')
                        }
                        
                        yield f"event: complete\n"
                        yield f"data: {json.dumps(complete_event)}\n\n"
                        
                        # End the stream after completion
                        break
                
                # Send heartbeat to keep connection alive
                current_time = time.time()
                if current_time - last_heartbeat >= heartbeat_interval:
                    yield f": heartbeat {int(current_time)}\n\n"
                    last_heartbeat = current_time
                
                # Check for errors in progress data
                if progress.get('error'):
                    error_event = {
                        "jobId": job_id,
                        "code": progress.get('error_code', 'UNEXPECTED'),
                        "message": progress.get('error', 'Unknown error occurred')
                    }
                    
                    yield f"event: error\n"
                    yield f"data: {json.dumps(error_event)}\n\n"
                    break
                
                # Sleep before next check
                await asyncio.sleep(2)
                
        except asyncio.CancelledError:
            # Client disconnected
            logger.info(f"SSE stream cancelled for job {job_id}")
            raise
        except Exception as e:
            logger.error(f"Error in SSE stream for job {job_id}: {e}")
            # Send error event
            error_event = {
                "jobId": job_id,
                "code": "STREAM_DISCONNECTED",
                "message": f"Stream error: {str(e)}"
            }
            yield f"event: error\n"
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )
