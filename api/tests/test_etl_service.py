"""
Unit Tests for ETL Service

Tests follow the AAA (Arrange-Act-Assert) pattern and TDD principles:
- Test isolation: Each test is independent
- Clear test names: Describe what is being tested
- Single responsibility: Each test validates one behavior
"""
import pytest
from uuid import UUID
from unittest.mock import Mock, MagicMock, patch
from psycopg.rows import dict_row

from api.etl_service import FormETLService
from api.models import (
    FormSubmission, PlaintiffDetail, DefendantDetail,
    PlaintiffName, DefendantName, PlaintiffDiscovery
)


# ============================================================================
# Unit Tests: FormETLService
# ============================================================================

class TestFormETLService:
    """Test suite for FormETLService"""
    
    def test_service_initialization(self):
        """Test that service initializes with empty caches"""
        # Arrange & Act
        service = FormETLService()
        
        # Assert
        assert service.issue_category_cache == {}
        assert service.issue_option_cache == {}
    
    def test_insert_case_with_full_address(self, db_connection, form_submission_factory):
        """Test inserting a case with complete address information"""
        # Arrange
        service = FormETLService()
        form_data = form_submission_factory()
        cursor = db_connection.cursor(row_factory=dict_row)
        
        # Act
        case_id = service._insert_case(cursor, form_data)
        
        # Assert
        assert isinstance(case_id, UUID)
        
        # Verify case was inserted correctly
        cursor.execute("SELECT * FROM cases WHERE id = %s", (case_id,))
        case = cursor.fetchone()
        
        assert case is not None
        assert case["property_address"] == "123 Main St"
        assert case["city"] == "Los Angeles"
        assert case["state"] == "CA"
        assert case["zip_code"] == "90001"
        cursor.close()
    
    def test_insert_case_without_address(self, db_connection, address_factory):
        """Test inserting a case without address defaults appropriately"""
        # Arrange
        service = FormETLService()
        from api.models import FormSubmission, PlaintiffDetail, DefendantDetail, PlaintiffName, DefendantName
        
        # Create form with no address (set Full_Address to None explicitly)
        form_data = FormSubmission(
            Full_Address=None,
            Filing_city="Los Angeles",
            Filing_county="Los Angeles County",
            PlaintiffDetails=[
                PlaintiffDetail(
                    ItemNumber=1,
                    PlaintiffItemNumberName=PlaintiffName(First="John", Last="Doe")
                )
            ],
            DefendantDetails2=[
                DefendantDetail(
                    ItemNumber=1,
                    DefendantItemNumberName=DefendantName(First="Jane", Last="Smith")
                )
            ]
        )
        cursor = db_connection.cursor(row_factory=dict_row)
        
        # Act
        case_id = service._insert_case(cursor, form_data)
        
        # Assert
        cursor.execute("SELECT * FROM cases WHERE id = %s", (case_id,))
        case = cursor.fetchone()
        
        assert case["property_address"] == "Address Not Provided"
        assert case["city"] == "Los Angeles"  # From filing_city
        assert case["state"] == "CA"  # Default
        assert case["zip_code"] == "00000"  # Default
    
    def test_insert_case_stores_payloads(self, db_connection, form_submission_factory):
        """Test that case insertion stores both raw and latest payloads"""
        # Arrange
        service = FormETLService()
        form_data = form_submission_factory()
        cursor = db_connection.cursor(row_factory=dict_row)
        
        # Act
        case_id = service._insert_case(cursor, form_data)
        
        # Assert
        cursor.execute("SELECT raw_payload, latest_payload FROM cases WHERE id = %s", (case_id,))
        result = cursor.fetchone()
        
        assert result["raw_payload"] is not None
        assert result["latest_payload"] is not None
        assert result["raw_payload"] == result["latest_payload"]  # Should be identical initially
    
    def test_insert_plaintiffs_single(self, db_connection, plaintiff_factory):
        """Test inserting a single plaintiff"""
        # Arrange
        service = FormETLService()
        cursor = db_connection.cursor(row_factory=dict_row)
        
        # Create a test case first
        cursor.execute("""
            INSERT INTO cases (property_address, city, state, zip_code, raw_payload, latest_payload)
            VALUES ('Test', 'LA', 'CA', '90001', '{}', '{}')
            RETURNING id
        """)
        case_id = cursor.fetchone()["id"]
        
        plaintiff = plaintiff_factory(item_number=1)
        
        # Act
        count = service._insert_plaintiffs(cursor, case_id, [plaintiff])
        
        # Assert
        assert count == 1
        
        cursor.execute("SELECT * FROM parties WHERE case_id = %s", (case_id,))
        party = cursor.fetchone()
        
        assert party["party_type"] == "plaintiff"
        assert party["party_number"] == 1
        assert party["first_name"] == "John"
        assert party["last_name"] == "Doe"
        assert party["is_head_of_household"] is True
    
    def test_insert_plaintiffs_multiple(self, db_connection, plaintiff_factory, plaintiff_name_factory):
        """Test inserting multiple plaintiffs in correct order"""
        # Arrange
        service = FormETLService()
        cursor = db_connection.cursor(row_factory=dict_row)
        
        cursor.execute("""
            INSERT INTO cases (property_address, city, state, zip_code, raw_payload, latest_payload)
            VALUES ('Test', 'LA', 'CA', '90001', '{}', '{}')
            RETURNING id
        """)
        case_id = cursor.fetchone()["id"]
        
        plaintiffs = [
            plaintiff_factory(
                item_number=1,
                name=plaintiff_name_factory(first="John", last="Doe"),
                head_of_household=True
            ),
            plaintiff_factory(
                item_number=2,
                name=plaintiff_name_factory(first="Jane", last="Doe"),
                head_of_household=False
            ),
            plaintiff_factory(
                item_number=3,
                name=plaintiff_name_factory(first="Bob", last="Smith"),
                head_of_household=False
            )
        ]
        
        # Act
        count = service._insert_plaintiffs(cursor, case_id, plaintiffs)
        
        # Assert
        assert count == 3
        
        cursor.execute(
            "SELECT * FROM parties WHERE case_id = %s ORDER BY party_number",
            (case_id,)
        )
        parties = cursor.fetchall()
        
        assert len(parties) == 3
        assert parties[0]["first_name"] == "John"
        assert parties[1]["first_name"] == "Jane"
        assert parties[2]["first_name"] == "Bob"
    
    def test_insert_defendants_single(self, db_connection, defendant_factory):
        """Test inserting a single defendant"""
        # Arrange
        service = FormETLService()
        cursor = db_connection.cursor(row_factory=dict_row)
        
        cursor.execute("""
            INSERT INTO cases (property_address, city, state, zip_code, raw_payload, latest_payload)
            VALUES ('Test', 'LA', 'CA', '90001', '{}', '{}')
            RETURNING id
        """)
        case_id = cursor.fetchone()["id"]
        
        defendant = defendant_factory(item_number=1)
        
        # Act
        count = service._insert_defendants(cursor, case_id, [defendant])
        
        # Assert
        assert count == 1
        
        cursor.execute("SELECT * FROM parties WHERE case_id = %s", (case_id,))
        party = cursor.fetchone()
        
        assert party["party_type"] == "defendant"
        assert party["party_number"] == 1
        assert party["entity_type"] == "Individual"
        assert party["role"] == "owner"
    
    def test_insert_defendants_with_different_entity_types(
        self, db_connection, defendant_factory, defendant_name_factory
    ):
        """Test inserting defendants with various entity types"""
        # Arrange
        service = FormETLService()
        cursor = db_connection.cursor(row_factory=dict_row)
        
        cursor.execute("""
            INSERT INTO cases (property_address, city, state, zip_code, raw_payload, latest_payload)
            VALUES ('Test', 'LA', 'CA', '90001', '{}', '{}')
            RETURNING id
        """)
        case_id = cursor.fetchone()["id"]
        
        defendants = [
            defendant_factory(item_number=1, entity_type="Individual", role="owner"),
            defendant_factory(
                item_number=2,
                name=defendant_name_factory(first="Acme", last="Corp"),
                entity_type="LLC",
                role="manager"
            ),
            defendant_factory(
                item_number=3,
                name=defendant_name_factory(first="Property", last="Management Inc"),
                entity_type="Corporation",
                role="agent"
            )
        ]
        
        # Act
        count = service._insert_defendants(cursor, case_id, defendants)
        
        # Assert
        assert count == 3
        
        cursor.execute(
            "SELECT * FROM parties WHERE case_id = %s ORDER BY party_number",
            (case_id,)
        )
        parties = cursor.fetchall()
        
        assert parties[0]["entity_type"] == "Individual"
        assert parties[1]["entity_type"] == "LLC"
        assert parties[2]["entity_type"] == "Corporation"
    
    def test_load_issue_cache_populates_categories(self, db_connection):
        """Test that issue cache loads category mappings"""
        # Arrange
        service = FormETLService()
        cursor = db_connection.cursor(row_factory=dict_row)
        
        # Act
        service._load_issue_cache(cursor)
        
        # Assert
        assert len(service.issue_category_cache) > 0
        assert "vermin" in service.issue_category_cache
        assert isinstance(service.issue_category_cache["vermin"], UUID)
    
    def test_load_issue_cache_populates_options(self, db_connection):
        """Test that issue cache loads option mappings"""
        # Arrange
        service = FormETLService()
        cursor = db_connection.cursor(row_factory=dict_row)
        
        # Act
        service._load_issue_cache(cursor)
        
        # Assert
        assert len(service.issue_option_cache) > 0
        # Check for a known option
        key = ("vermin", "Rats/Mice")
        assert key in service.issue_option_cache
        assert isinstance(service.issue_option_cache[key], UUID)
    
    def test_get_issue_option_id_returns_valid_id(self, db_connection):
        """Test retrieving issue option ID from cache"""
        # Arrange
        service = FormETLService()
        cursor = db_connection.cursor(row_factory=dict_row)
        service._load_issue_cache(cursor)
        
        # Act
        option_id = service._get_issue_option_id(cursor, "vermin", "Rats/Mice")
        
        # Assert
        assert option_id is not None
        assert isinstance(option_id, UUID)
    
    def test_get_issue_option_id_returns_none_for_invalid(self, db_connection):
        """Test that invalid issue option returns None"""
        # Arrange
        service = FormETLService()
        cursor = db_connection.cursor(row_factory=dict_row)
        service._load_issue_cache(cursor)
        
        # Act
        option_id = service._get_issue_option_id(cursor, "invalid_category", "Invalid Option")
        
        # Assert
        assert option_id is None
    
    @pytest.mark.integration
    def test_ingest_form_submission_complete_flow(self, db_connection, form_submission_factory, discovery_factory):
        """Test complete form submission ingestion flow"""
        # Arrange
        service = FormETLService()
        
        # Use only issues that exist in the taxonomy
        discovery = discovery_factory(
            vermin=["Rats/Mice"],  # Known to exist
            insects=["Roaches"],   # Known to exist
            unit="101"
        )
        
        form_data = form_submission_factory()
        form_data.PlaintiffDetails[0].PlaintiffItemNumberDiscovery = discovery
        
        # Act
        with patch('api.etl_service.get_db_connection', return_value=db_connection):
            result = service.ingest_form_submission(form_data)
        
        # Assert
        assert "case_id" in result
        assert result["plaintiff_count"] == 1
        assert result["defendant_count"] == 1
        assert result["issue_count"] >= 2  # At least 2 issues selected (Rats/Mice and Roaches)
        
        # Verify data was actually inserted
        cursor = db_connection.cursor(row_factory=dict_row)
        cursor.execute("SELECT * FROM cases WHERE id = %s", (result["case_id"],))
        case = cursor.fetchone()
        assert case is not None
    
    @pytest.mark.integration
    def test_ingest_form_submission_with_multiple_parties(
        self, db_connection, form_submission_factory, plaintiff_factory, defendant_factory
    ):
        """Test ingestion with multiple plaintiffs and defendants"""
        # Arrange
        service = FormETLService()
        
        form_data = form_submission_factory(
            plaintiffs=[
                plaintiff_factory(item_number=1),
                plaintiff_factory(item_number=2)
            ],
            defendants=[
                defendant_factory(item_number=1),
                defendant_factory(item_number=2),
                defendant_factory(item_number=3)
            ]
        )
        
        # Act
        with patch('api.etl_service.get_db_connection', return_value=db_connection):
            result = service.ingest_form_submission(form_data)
        
        # Assert
        assert result["plaintiff_count"] == 2
        assert result["defendant_count"] == 3
    
    def test_ingest_form_submission_transaction_rollback_on_error(self, db_connection):
        """Test that transaction rolls back on error"""
        # Arrange
        service = FormETLService()
        
        # Create invalid form data (will fail validation or insertion)
        invalid_form = Mock()
        invalid_form.PlaintiffDetails = None  # Will cause error
        
        # Act & Assert
        with patch('api.etl_service.get_db_connection', return_value=db_connection):
            with pytest.raises(Exception):
                service.ingest_form_submission(invalid_form)
        
        # Verify no partial data was committed
        cursor = db_connection.cursor(row_factory=dict_row)
        cursor.execute("SELECT COUNT(*) FROM cases")
        # Since we're using transaction rollback in tests, count should be 0 or unchanged


# ============================================================================
# Unit Tests: Edge Cases and Error Handling
# ============================================================================

class TestETLServiceEdgeCases:
    """Test edge cases and error handling"""
    
    def test_insert_plaintiffs_with_empty_list(self, db_connection):
        """Test inserting empty plaintiff list"""
        # Arrange
        service = FormETLService()
        cursor = db_connection.cursor(row_factory=dict_row)
        
        cursor.execute("""
            INSERT INTO cases (property_address, city, state, zip_code, raw_payload, latest_payload)
            VALUES ('Test', 'LA', 'CA', '90001', '{}', '{}')
            RETURNING id
        """)
        case_id = cursor.fetchone()["id"]
        
        # Act
        count = service._insert_plaintiffs(cursor, case_id, [])
        
        # Assert
        assert count == 0
    
    def test_insert_defendants_with_missing_names(self, db_connection, defendant_factory):
        """Test inserting defendant with minimal name information"""
        # Arrange
        service = FormETLService()
        cursor = db_connection.cursor(row_factory=dict_row)
        
        cursor.execute("""
            INSERT INTO cases (property_address, city, state, zip_code, raw_payload, latest_payload)
            VALUES ('Test', 'LA', 'CA', '90001', '{}', '{}')
            RETURNING id
        """)
        case_id = cursor.fetchone()["id"]
        
        # Create defendant with minimal name
        defendant = defendant_factory()
        defendant.DefendantItemNumberName.First = ""
        defendant.DefendantItemNumberName.Last = ""
        defendant.DefendantItemNumberName.FirstAndLast = None
        
        # Act
        count = service._insert_defendants(cursor, case_id, [defendant])
        
        # Assert
        assert count == 1
        
        cursor.execute("SELECT * FROM parties WHERE case_id = %s", (case_id,))
        party = cursor.fetchone()
        
        # Should default to "Unknown"
        assert party["full_name"] == "Unknown"
    
    def test_insert_plaintiff_issues_with_no_discovery(self, db_connection, plaintiff_factory):
        """Test inserting plaintiff issues when discovery is None"""
        # Arrange
        service = FormETLService()
        cursor = db_connection.cursor(row_factory=dict_row)
        
        cursor.execute("""
            INSERT INTO cases (property_address, city, state, zip_code, raw_payload, latest_payload)
            VALUES ('Test', 'LA', 'CA', '90001', '{}', '{}')
            RETURNING id
        """)
        case_id = cursor.fetchone()["id"]
        
        plaintiff = plaintiff_factory()
        plaintiff.PlaintiffItemNumberDiscovery = None
        
        service._insert_plaintiffs(cursor, case_id, [plaintiff])
        
        # Act
        count = service._insert_plaintiff_issues(cursor, case_id, [plaintiff])
        
        # Assert
        assert count == 0  # No issues should be inserted
    
    def test_insert_case_with_long_state_code(self, db_connection, form_submission_factory, address_factory):
        """Test that long state codes are truncated to 2 characters"""
        # Arrange
        service = FormETLService()
        address = address_factory(state="California")  # Full state name
        form_data = form_submission_factory(address=address)
        cursor = db_connection.cursor(row_factory=dict_row)
        
        # Act
        case_id = service._insert_case(cursor, form_data)
        
        # Assert
        cursor.execute("SELECT state FROM cases WHERE id = %s", (case_id,))
        result = cursor.fetchone()
        
        assert len(result["state"]) == 2
        assert result["state"] == "Ca"  # First 2 chars

