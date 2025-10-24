"""
Legal Forms ETL API - Main Application
FastAPI application for ingesting legal form submissions into PostgreSQL
"""
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import get_settings
from api.database import init_db_pool, close_db_pool, execute_query, get_db_connection
from api.models import (
    FormSubmission, CaseResponse, HealthCheckResponse, ErrorResponse,
    PartyUpdate, PartyUpdateResponse, IssueAddResponse, IssueDeleteResponse
)
from api.etl_service import FormETLService
from api.json_builder import JSONBuilderService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    logger.info("Starting Legal Forms ETL API...")
    init_db_pool()
    logger.info("Database pool initialized")

    yield

    # Shutdown
    logger.info("Shutting down Legal Forms ETL API...")
    close_db_pool()
    logger.info("Database pool closed")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="ETL API for ingesting legal form submissions into PostgreSQL",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
etl_service = FormETLService()
json_builder = JSONBuilderService()


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "endpoints": {
            "health": "/health",
            "submit_form": "POST /api/form-submissions",
            "get_cases": "GET /api/cases",
            "get_case": "GET /api/cases/{case_id}",
            "taxonomy": "GET /api/taxonomy"
        }
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        result = execute_query("SELECT 1 as status")
        db_status = "connected" if result else "disconnected"

        return HealthCheckResponse(
            status="healthy",
            database=db_status,
            version=settings.app_version,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )


@app.post("/api/form-submissions", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def submit_form(form_data: FormSubmission):
    """
    ETL Endpoint: Ingest form submission and store in database

    This endpoint:
    1. Validates the incoming JSON against the FormSubmission model
    2. Inserts a case record with address and filing information
    3. Inserts plaintiff and defendant party records
    4. Inserts plaintiff issue selections
    5. Stores the complete JSON in raw_payload and latest_payload

    All operations are atomic (single transaction).
    """
    try:
        logger.info("Received form submission")

        # Validate required data
        if not form_data.PlaintiffDetails:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one plaintiff is required"
            )

        if not form_data.DefendantDetails2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one defendant is required"
            )

        # Process via ETL service
        result = etl_service.ingest_form_submission(form_data)

        logger.info(f"Form submission processed successfully: {result['case_id']}")

        return CaseResponse(
            case_id=result["case_id"],
            created_at=result["created_at"],
            plaintiff_count=result["plaintiff_count"],
            defendant_count=result["defendant_count"],
            issue_count=result["issue_count"],
            message="Form submission processed successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Form submission failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process form submission: {str(e)}"
        )


@app.get("/api/cases")
async def get_cases(limit: int = 100, offset: int = 0):
    """
    Get list of cases

    Args:
        limit: Maximum number of cases to return (default 100)
        offset: Number of cases to skip (default 0)
    """
    try:
        query = """
            SELECT
                c.id,
                c.created_at,
                c.property_address,
                c.city,
                c.state,
                c.zip_code,
                c.filing_location,
                COUNT(DISTINCT CASE WHEN p.party_type = 'plaintiff' THEN p.id END) as plaintiff_count,
                COUNT(DISTINCT CASE WHEN p.party_type = 'defendant' THEN p.id END) as defendant_count
            FROM cases c
            LEFT JOIN parties p ON c.id = p.case_id
            GROUP BY c.id
            ORDER BY c.created_at DESC
            LIMIT %(limit)s OFFSET %(offset)s
        """

        cases = execute_query(query, {"limit": limit, "offset": offset})

        return {
            "cases": cases,
            "count": len(cases),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Failed to retrieve cases: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve cases: {str(e)}"
        )


@app.get("/api/cases/{case_id}")
async def get_case(case_id: str):
    """
    Get detailed case information including all parties and issues

    Args:
        case_id: UUID of the case
    """
    try:
        # Get case details
        case_query = """
            SELECT
                c.*,
                COUNT(DISTINCT CASE WHEN p.party_type = 'plaintiff' THEN p.id END) as plaintiff_count,
                COUNT(DISTINCT CASE WHEN p.party_type = 'defendant' THEN p.id END) as defendant_count
            FROM cases c
            LEFT JOIN parties p ON c.id = p.case_id
            WHERE c.id = %(case_id)s
            GROUP BY c.id
        """

        case = execute_query(case_query, {"case_id": case_id})

        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found"
            )

        # Get parties
        parties_query = """
            SELECT * FROM parties
            WHERE case_id = %(case_id)s
            ORDER BY party_type, party_number
        """
        parties = execute_query(parties_query, {"case_id": case_id})

        # Get issues for each plaintiff
        issues_query = """
            SELECT
                p.id as party_id,
                p.party_number,
                ic.category_name,
                array_agg(io.option_name ORDER BY io.display_order) as selected_issues
            FROM parties p
            JOIN party_issue_selections pis ON p.id = pis.party_id
            JOIN issue_options io ON pis.issue_option_id = io.id
            JOIN issue_categories ic ON io.category_id = ic.id
            WHERE p.case_id = %(case_id)s AND p.party_type = 'plaintiff'
            GROUP BY p.id, p.party_number, ic.id, ic.category_name
            ORDER BY p.party_number, ic.display_order
        """
        issues = execute_query(issues_query, {"case_id": case_id})

        return {
            "case": case[0],
            "parties": parties,
            "issues": issues
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve case {case_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve case: {str(e)}"
        )


@app.get("/api/taxonomy")
async def get_taxonomy():
    """
    Get complete issue taxonomy (categories and options)

    Returns all issue categories with their options for form rendering
    """
    try:
        query = """
            SELECT
                ic.id as category_id,
                ic.category_code,
                ic.category_name,
                ic.display_order as category_order,
                ic.is_multi_select,
                json_agg(
                    json_build_object(
                        'id', io.id,
                        'code', io.option_code,
                        'name', io.option_name,
                        'order', io.display_order
                    ) ORDER BY io.display_order
                ) as options
            FROM issue_categories ic
            LEFT JOIN issue_options io ON ic.id = io.category_id
            WHERE ic.is_active = true
            GROUP BY ic.id, ic.category_code, ic.category_name, ic.display_order, ic.is_multi_select
            ORDER BY ic.display_order
        """

        categories = execute_query(query)

        return {
            "categories": categories,
            "total_categories": len(categories),
            "timestamp": datetime.now()
        }

    except Exception as e:
        logger.error(f"Failed to retrieve taxonomy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve taxonomy: {str(e)}"
        )


# ============================================================================
# Edit Endpoints
# ============================================================================

@app.patch("/api/parties/{party_id}", response_model=PartyUpdateResponse)
async def update_party(party_id: str, party_update: PartyUpdate):
    """
    Update party details and rebuild latest_payload

    Allowed fields:
    - first_name
    - last_name
    - full_name
    - unit_number
    - is_head_of_household

    Enforces one Head of Household per unit constraint.
    Returns 409 Conflict if HoH constraint would be violated.

    Args:
        party_id: UUID of the party to update
        party_update: Fields to update
    """
    try:
        # Validate at least one field provided
        update_data = party_update.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one field must be provided for update"
            )

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Get current party and case_id
                cur.execute(
                    "SELECT id, case_id, party_type, unit_number FROM parties WHERE id = %s",
                    (party_id,)
                )
                party = cur.fetchone()

                if not party:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Party {party_id} not found"
                    )

                case_id = party["case_id"]

                # Check HoH constraint if being updated
                if "is_head_of_household" in update_data and update_data["is_head_of_household"]:
                    # Get unit number (use new if provided, else current)
                    unit_number = update_data.get("unit_number", party["unit_number"])

                    if unit_number:
                        # Check if another party is already HoH for this unit
                        cur.execute(
                            """
                            SELECT id, full_name FROM parties
                            WHERE case_id = %s
                              AND unit_number = %s
                              AND is_head_of_household = true
                              AND id != %s
                            """,
                            (case_id, unit_number, party_id)
                        )
                        existing_hoh = cur.fetchone()

                        if existing_hoh:
                            raise HTTPException(
                                status_code=status.HTTP_409_CONFLICT,
                                detail=f"Unit {unit_number} already has a Head of Household: {existing_hoh['full_name']}. "
                                       f"Only one Head of Household per unit is allowed."
                            )

                # Build UPDATE query dynamically
                set_clauses = []
                params = {}

                for field, value in update_data.items():
                    set_clauses.append(f"{field} = %({field})s")
                    params[field] = value

                # Auto-update full_name if first_name or last_name changed
                if "first_name" in update_data or "last_name" in update_data:
                    # Get current values
                    cur.execute(
                        "SELECT first_name, last_name FROM parties WHERE id = %s",
                        (party_id,)
                    )
                    current = cur.fetchone()

                    first = update_data.get("first_name", current["first_name"])
                    last = update_data.get("last_name", current["last_name"])
                    full = f"{first} {last}".strip()

                    if "full_name" not in update_data:
                        set_clauses.append("full_name = %(full_name)s")
                        params["full_name"] = full
                        update_data["full_name"] = full  # Track for response

                params["party_id"] = party_id

                update_query = f"""
                    UPDATE parties
                    SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %(party_id)s
                    RETURNING id, case_id
                """

                cur.execute(update_query, params)
                updated = cur.fetchone()

                if not updated:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to update party"
                    )

                # Rebuild latest_payload
                json_builder.update_latest_payload(cur, case_id)

                logger.info(f"Updated party {party_id}, rebuilt latest_payload for case {case_id}")

                return PartyUpdateResponse(
                    party_id=updated["id"],
                    case_id=updated["case_id"],
                    updated_fields=list(update_data.keys()),
                    latest_payload_updated=True,
                    message="Party updated successfully"
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update party {party_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update party: {str(e)}"
        )


@app.post("/api/parties/{party_id}/issues/{option_id}", response_model=IssueAddResponse)
async def add_party_issue(party_id: str, option_id: str):
    """
    Add an issue selection to a party and rebuild latest_payload

    Args:
        party_id: UUID of the party (plaintiff)
        option_id: UUID of the issue option to add
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Verify party exists and get case_id
                cur.execute(
                    "SELECT id, case_id, party_type, full_name FROM parties WHERE id = %s",
                    (party_id,)
                )
                party = cur.fetchone()

                if not party:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Party {party_id} not found"
                    )

                if party["party_type"] != "plaintiff":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Issues can only be added to plaintiffs"
                    )

                case_id = party["case_id"]

                # Verify issue option exists
                cur.execute(
                    """
                    SELECT io.id, io.option_name, ic.category_name
                    FROM issue_options io
                    JOIN issue_categories ic ON io.category_id = ic.id
                    WHERE io.id = %s
                    """,
                    (option_id,)
                )
                issue_option = cur.fetchone()

                if not issue_option:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Issue option {option_id} not found"
                    )

                # Insert issue selection (ON CONFLICT DO NOTHING handles duplicates)
                cur.execute(
                    """
                    INSERT INTO party_issue_selections (party_id, issue_option_id)
                    VALUES (%s, %s)
                    ON CONFLICT (party_id, issue_option_id) DO NOTHING
                    RETURNING id
                    """,
                    (party_id, option_id)
                )
                result = cur.fetchone()

                # Rebuild latest_payload
                json_builder.update_latest_payload(cur, case_id)

                logger.info(f"Added issue {issue_option['option_name']} to party {party_id}")

                return IssueAddResponse(
                    party_id=party["id"],
                    case_id=case_id,
                    issue_option_id=issue_option["id"],
                    category_name=issue_option["category_name"],
                    option_name=issue_option["option_name"],
                    latest_payload_updated=True,
                    message="Issue added successfully" if result else "Issue already exists (no change)"
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add issue to party {party_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add issue: {str(e)}"
        )


@app.delete("/api/parties/{party_id}/issues/{option_id}", response_model=IssueDeleteResponse)
async def remove_party_issue(party_id: str, option_id: str):
    """
    Remove an issue selection from a party and rebuild latest_payload

    Args:
        party_id: UUID of the party (plaintiff)
        option_id: UUID of the issue option to remove
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Verify party exists and get case_id
                cur.execute(
                    "SELECT id, case_id, party_type FROM parties WHERE id = %s",
                    (party_id,)
                )
                party = cur.fetchone()

                if not party:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Party {party_id} not found"
                    )

                case_id = party["case_id"]

                # Delete issue selection
                cur.execute(
                    """
                    DELETE FROM party_issue_selections
                    WHERE party_id = %s AND issue_option_id = %s
                    RETURNING id
                    """,
                    (party_id, option_id)
                )
                deleted = cur.fetchone()

                if not deleted:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Issue selection not found for party {party_id} and option {option_id}"
                    )

                # Rebuild latest_payload
                json_builder.update_latest_payload(cur, case_id)

                logger.info(f"Removed issue {option_id} from party {party_id}")

                return IssueDeleteResponse(
                    party_id=party["id"],
                    case_id=case_id,
                    issue_option_id=option_id,
                    latest_payload_updated=True,
                    message="Issue removed successfully"
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove issue from party {party_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove issue: {str(e)}"
        )


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc),
            timestamp=datetime.now()
        ).model_dump()
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level="info"
    )
