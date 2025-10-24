"""
Pytest Configuration and Shared Fixtures

This module provides:
- Database test fixtures
- Test client setup
- Mock data factories
- Reusable test utilities
"""
import os
import pytest
from typing import Generator, Dict, Any
from datetime import datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from psycopg import Connection
from psycopg.rows import dict_row

from api.main import app
from api.database import get_db_connection, init_db_pool, close_db_pool
from api.models import (
    FormSubmission, PlaintiffDetail, DefendantDetail,
    PlaintiffName, DefendantName, PlaintiffDiscovery, FullAddress
)


# ============================================================================
# Session-Level Fixtures
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables"""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "INFO"
    yield
    # Cleanup after all tests


@pytest.fixture(scope="session")
def db_pool():
    """Initialize database pool for tests"""
    init_db_pool()
    yield
    close_db_pool()


# ============================================================================
# Function-Level Fixtures
# ============================================================================

@pytest.fixture
def db_connection(db_pool) -> Generator[Connection, None, None]:
    """
    Provide a database connection for a test with automatic rollback
    
    Each test gets a fresh transaction that's rolled back after the test,
    ensuring test isolation without affecting the actual database.
    """
    with get_db_connection() as conn:
        conn.autocommit = False
        
        # Start a transaction
        with conn.cursor() as cursor:
            cursor.execute("BEGIN")
        
        yield conn
        
        # Rollback the transaction (test changes are discarded)
        with conn.cursor() as cursor:
            cursor.execute("ROLLBACK")


@pytest.fixture
def client() -> TestClient:
    """Provide a FastAPI test client"""
    return TestClient(app)


# ============================================================================
# Test Data Factories
# ============================================================================

@pytest.fixture
def plaintiff_name_factory():
    """Factory for creating PlaintiffName instances"""
    def create(
        first: str = "John",
        last: str = "Doe",
        middle: str = None,
        **kwargs
    ) -> PlaintiffName:
        return PlaintiffName(
            First=first,
            Last=last,
            FirstAndLast=f"{first} {last}",
            Middle=middle,
            **kwargs
        )
    return create


@pytest.fixture
def defendant_name_factory():
    """Factory for creating DefendantName instances"""
    def create(
        first: str = "Jane",
        last: str = "Smith",
        **kwargs
    ) -> DefendantName:
        return DefendantName(
            First=first,
            Last=last,
            FirstAndLast=f"{first} {last}",
            **kwargs
        )
    return create


@pytest.fixture
def discovery_factory():
    """Factory for creating PlaintiffDiscovery instances"""
    def create(
        vermin: list = None,
        insects: list = None,
        unit: str = None,
        **kwargs
    ) -> PlaintiffDiscovery:
        return PlaintiffDiscovery(
            VerminIssue=bool(vermin),
            InsectIssues=bool(insects),
            Vermin=vermin or [],
            Insects=insects or [],
            Unit=unit,
            **kwargs
        )
    return create


@pytest.fixture
def plaintiff_factory(plaintiff_name_factory, discovery_factory):
    """Factory for creating PlaintiffDetail instances"""
    def create(
        item_number: int = 1,
        name: PlaintiffName = None,
        discovery: PlaintiffDiscovery = None,
        plaintiff_type: str = "Individual",
        head_of_household: bool = True,
        **kwargs
    ) -> PlaintiffDetail:
        return PlaintiffDetail(
            ItemNumber=item_number,
            PlaintiffItemNumberName=name or plaintiff_name_factory(),
            PlaintiffItemNumberDiscovery=discovery or discovery_factory(),
            PlaintiffItemNumberType=plaintiff_type,
            HeadOfHousehold=head_of_household,
            **kwargs
        )
    return create


@pytest.fixture
def defendant_factory(defendant_name_factory):
    """Factory for creating DefendantDetail instances"""
    def create(
        item_number: int = 1,
        name: DefendantName = None,
        entity_type: str = "Individual",
        role: str = "owner",
        **kwargs
    ) -> DefendantDetail:
        return DefendantDetail(
            ItemNumber=item_number,
            DefendantItemNumberName=name or defendant_name_factory(),
            DefendantItemNumberType=entity_type,
            DefendantItemNumberManagerOwner=role,
            **kwargs
        )
    return create


@pytest.fixture
def address_factory():
    """Factory for creating FullAddress instances"""
    def create(
        street: str = "123 Main St",
        city: str = "Los Angeles",
        state: str = "CA",
        postal_code: str = "90001",
        **kwargs
    ) -> FullAddress:
        return FullAddress(
            StreetAddress=street,
            City=city,
            State=state,
            PostalCode=postal_code,
            Country="United States",
            CountryCode="US",
            **kwargs
        )
    return create


@pytest.fixture
def form_submission_factory(plaintiff_factory, defendant_factory, address_factory):
    """Factory for creating complete FormSubmission instances"""
    def create(
        plaintiffs: list[PlaintiffDetail] = None,
        defendants: list[DefendantDetail] = None,
        address: FullAddress = None,
        filing_city: str = "Los Angeles",
        filing_county: str = "Los Angeles County",
        **kwargs
    ) -> FormSubmission:
        return FormSubmission(
            Full_Address=address or address_factory(),
            Filing_city=filing_city,
            Filing_county=filing_county,
            PlaintiffDetails=plaintiffs or [plaintiff_factory()],
            DefendantDetails2=defendants or [defendant_factory()],
            Form={"Name": "Test Form", "InternalName": "test-form"},
            **kwargs
        )
    return create


# ============================================================================
# Database Helper Fixtures
# ============================================================================

@pytest.fixture
def db_helper(db_connection):
    """Helper functions for database operations in tests"""
    class DBHelper:
        def __init__(self, conn: Connection):
            self.conn = conn
        
        def get_case_by_id(self, case_id: str) -> Dict[str, Any] | None:
            """Get case by ID"""
            cur = self.conn.cursor(row_factory=dict_row)
            cur.execute("SELECT * FROM cases WHERE id = %s", (case_id,))
            result = cur.fetchone()
            cur.close()
            return result
        
        def get_parties_by_case(self, case_id: str) -> list[Dict[str, Any]]:
            """Get all parties for a case"""
            cur = self.conn.cursor(row_factory=dict_row)
            cur.execute(
                "SELECT * FROM parties WHERE case_id = %s ORDER BY party_number",
                (case_id,)
            )
            results = cur.fetchall()
            cur.close()
            return results
        
        def get_issue_selections_by_party(self, party_id: str) -> list[Dict[str, Any]]:
            """Get all issue selections for a party"""
            cur = self.conn.cursor(row_factory=dict_row)
            cur.execute(
                """
                SELECT pis.*, io.option_name, ic.category_name
                FROM party_issue_selections pis
                JOIN issue_options io ON pis.issue_option_id = io.id
                JOIN issue_categories ic ON io.category_id = ic.id
                WHERE pis.party_id = %s
                ORDER BY ic.display_order, io.display_order
                """,
                (party_id,)
            )
            results = cur.fetchall()
            cur.close()
            return results
        
        def count_parties_by_type(self, case_id: str, party_type: str) -> int:
            """Count parties by type"""
            cur = self.conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM parties WHERE case_id = %s AND party_type = %s",
                (case_id, party_type)
            )
            count = cur.fetchone()[0]
            cur.close()
            return count
        
        def cleanup_case(self, case_id: str):
            """Delete a case and all related data"""
            cur = self.conn.cursor()
            # Cascade delete will handle related records
            cur.execute("DELETE FROM cases WHERE id = %s", (case_id,))
            cur.close()
    
    return DBHelper(db_connection)


# ============================================================================
# Mock Data Fixtures
# ============================================================================

@pytest.fixture
def sample_form_data() -> Dict[str, Any]:
    """Sample form data as raw dictionary"""
    return {
        "Full_Address": {
            "StreetAddress": "123 Test Street",
            "City": "Los Angeles",
            "State": "CA",
            "PostalCode": "90001"
        },
        "Filing city": "Los Angeles",
        "Filing county": "Los Angeles County",
        "PlaintiffDetails": [
            {
                "ItemNumber": 1,
                "PlaintiffItemNumberName": {
                    "First": "Test",
                    "Last": "Plaintiff",
                    "FirstAndLast": "Test Plaintiff"
                },
                "PlaintiffItemNumberType": "Individual",
                "HeadOfHousehold": True,
                "PlaintiffItemNumberAgeCategory": ["adult"],
                "PlaintiffItemNumberDiscovery": {
                    "VerminIssue": True,
                    "Vermin": ["Rats/Mice", "Bedbugs"],
                    "Unit": "101"
                }
            }
        ],
        "DefendantDetails2": [
            {
                "ItemNumber": 1,
                "DefendantItemNumberName": {
                    "First": "Test",
                    "Last": "Defendant",
                    "FirstAndLast": "Test Defendant"
                },
                "DefendantItemNumberType": "LLC",
                "DefendantItemNumberManagerOwner": "owner"
            }
        ],
        "Form": {
            "Name": "Legal Form",
            "InternalName": "legal-form-v1"
        }
    }

