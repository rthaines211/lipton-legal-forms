"""
Unit Tests for Pydantic Models

Tests validate:
- Model validation rules
- Field defaults
- Serialization/deserialization
- Edge cases
"""
import pytest
from pydantic import ValidationError
from datetime import datetime
from uuid import UUID

from api.models import (
    PlaintiffName, DefendantName, PlaintiffDiscovery, FullAddress,
    PlaintiffDetail, DefendantDetail, FormSubmission,
    CaseResponse, HealthCheckResponse, ErrorResponse,
    PartyUpdate, PartyUpdateResponse,
    IssueAddResponse, IssueDeleteResponse
)


# ============================================================================
# Tests: Name Models
# ============================================================================

@pytest.mark.unit
class TestPlaintiffName:
    """Test PlaintiffName model validation"""
    
    def test_valid_plaintiff_name(self):
        """Test creating valid plaintiff name"""
        # Arrange & Act
        name = PlaintiffName(
            First="John",
            Last="Doe",
            FirstAndLast="John Doe"
        )
        
        # Assert
        assert name.First == "John"
        assert name.Last == "Doe"
        assert name.FirstAndLast == "John Doe"
    
    def test_plaintiff_name_with_middle(self):
        """Test plaintiff name with middle name"""
        # Arrange & Act
        name = PlaintiffName(
            First="John",
            Middle="Michael",
            Last="Doe",
            MiddleInitial="M"
        )
        
        # Assert
        assert name.Middle == "Michael"
        assert name.MiddleInitial == "M"
    
    def test_plaintiff_name_with_prefix_suffix(self):
        """Test plaintiff name with prefix and suffix"""
        # Arrange & Act
        name = PlaintiffName(
            First="John",
            Last="Doe",
            Prefix="Dr.",
            Suffix="Jr."
        )
        
        # Assert
        assert name.Prefix == "Dr."
        assert name.Suffix == "Jr."
    
    def test_plaintiff_name_optional_fields_default_none(self):
        """Test that optional fields default to None"""
        # Arrange & Act
        name = PlaintiffName(First="John", Last="Doe")
        
        # Assert
        assert name.Middle is None
        assert name.MiddleInitial is None
        assert name.Prefix is None
        assert name.Suffix is None


@pytest.mark.unit
class TestDefendantName:
    """Test DefendantName model validation"""
    
    def test_defendant_name_all_optional(self):
        """Test that all defendant name fields are optional"""
        # Arrange & Act
        name = DefendantName()
        
        # Assert
        assert name.First is None
        assert name.Last is None
        assert name.FirstAndLast is None
    
    def test_defendant_name_with_values(self):
        """Test defendant name with values"""
        # Arrange & Act
        name = DefendantName(
            First="Jane",
            Last="Smith",
            FirstAndLast="Jane Smith"
        )
        
        # Assert
        assert name.First == "Jane"
        assert name.Last == "Smith"


# ============================================================================
# Tests: Address Models
# ============================================================================

@pytest.mark.unit
class TestFullAddress:
    """Test FullAddress model validation"""
    
    def test_full_address_complete(self):
        """Test creating complete address"""
        # Arrange & Act
        address = FullAddress(
            StreetAddress="123 Main St",
            City="Los Angeles",
            State="CA",
            PostalCode="90001"
        )
        
        # Assert
        assert address.StreetAddress == "123 Main St"
        assert address.City == "Los Angeles"
        assert address.State == "CA"
        assert address.PostalCode == "90001"
    
    def test_address_defaults(self):
        """Test address default values"""
        # Arrange & Act
        address = FullAddress()
        
        # Assert
        assert address.Country == "United States"
        assert address.CountryCode == "US"
    
    def test_address_with_coordinates(self):
        """Test address with latitude/longitude"""
        # Arrange & Act
        address = FullAddress(
            StreetAddress="123 Main St",
            Latitude=34.0522,
            Longitude=-118.2437
        )
        
        # Assert
        assert address.Latitude == 34.0522
        assert address.Longitude == -118.2437


# ============================================================================
# Tests: Discovery Models
# ============================================================================

@pytest.mark.unit
class TestPlaintiffDiscovery:
    """Test PlaintiffDiscovery model validation"""
    
    def test_discovery_defaults_to_false_and_empty(self):
        """Test that boolean flags default to False and arrays to empty"""
        # Arrange & Act
        discovery = PlaintiffDiscovery()
        
        # Assert
        assert discovery.VerminIssue is False
        assert discovery.InsectIssues is False
        assert discovery.Vermin == []
        assert discovery.Insects == []
    
    def test_discovery_with_vermin_issues(self):
        """Test discovery with vermin issues"""
        # Arrange & Act
        discovery = PlaintiffDiscovery(
            VerminIssue=True,
            Vermin=["Rats/Mice", "Bedbugs"]
        )
        
        # Assert
        assert discovery.VerminIssue is True
        assert len(discovery.Vermin) == 2
        assert "Rats/Mice" in discovery.Vermin
    
    def test_discovery_field_aliases(self):
        """Test that field aliases work correctly"""
        # Arrange & Act
        data = {
            "Fire Hazard": ["Fire Escape"],
            "Health hazard": ["Mold"]
        }
        discovery = PlaintiffDiscovery(**data)
        
        # Assert
        assert discovery.FireHazard == ["Fire Escape"]
        assert discovery.HealthHazard == ["Mold"]
    
    def test_discovery_with_unit(self):
        """Test discovery with unit number"""
        # Arrange & Act
        discovery = PlaintiffDiscovery(Unit="101")
        
        # Assert
        assert discovery.Unit == "101"


# ============================================================================
# Tests: Party Detail Models
# ============================================================================

@pytest.mark.unit
class TestPlaintiffDetail:
    """Test PlaintiffDetail model validation"""
    
    def test_plaintiff_detail_required_fields(self):
        """Test that required fields are validated"""
        # Arrange & Act
        plaintiff = PlaintiffDetail(
            ItemNumber=1,
            PlaintiffItemNumberName=PlaintiffName(First="John", Last="Doe")
        )
        
        # Assert
        assert plaintiff.ItemNumber == 1
        assert plaintiff.PlaintiffItemNumberName.First == "John"
    
    def test_plaintiff_detail_defaults(self):
        """Test plaintiff detail default values"""
        # Arrange & Act
        plaintiff = PlaintiffDetail(
            ItemNumber=1,
            PlaintiffItemNumberName=PlaintiffName(First="John", Last="Doe")
        )
        
        # Assert
        assert plaintiff.HeadOfHousehold is False
        assert plaintiff.PlaintiffItemNumberAgeCategory == []
    
    def test_plaintiff_detail_complete(self):
        """Test complete plaintiff detail"""
        # Arrange & Act
        plaintiff = PlaintiffDetail(
            ItemNumber=1,
            PlaintiffItemNumberName=PlaintiffName(First="John", Last="Doe"),
            PlaintiffItemNumberType="Individual",
            PlaintiffItemNumberAgeCategory=["adult"],
            HeadOfHousehold=True,
            PlaintiffItemNumberDiscovery=PlaintiffDiscovery(
                VerminIssue=True,
                Vermin=["Rats/Mice"]
            )
        )
        
        # Assert
        assert plaintiff.PlaintiffItemNumberType == "Individual"
        assert plaintiff.HeadOfHousehold is True
        assert plaintiff.PlaintiffItemNumberAgeCategory == ["adult"]
        assert plaintiff.PlaintiffItemNumberDiscovery.VerminIssue is True


@pytest.mark.unit
class TestDefendantDetail:
    """Test DefendantDetail model validation"""
    
    def test_defendant_detail_required_fields(self):
        """Test defendant with required fields only"""
        # Arrange & Act
        defendant = DefendantDetail(
            ItemNumber=1,
            DefendantItemNumberName=DefendantName(First="Jane", Last="Smith")
        )
        
        # Assert
        assert defendant.ItemNumber == 1
        assert defendant.DefendantItemNumberName.First == "Jane"
    
    def test_defendant_detail_with_entity_type(self):
        """Test defendant with entity type"""
        # Arrange & Act
        defendant = DefendantDetail(
            ItemNumber=1,
            DefendantItemNumberName=DefendantName(First="Acme", Last="Corp"),
            DefendantItemNumberType="LLC",
            DefendantItemNumberManagerOwner="manager"
        )
        
        # Assert
        assert defendant.DefendantItemNumberType == "LLC"
        assert defendant.DefendantItemNumberManagerOwner == "manager"


# ============================================================================
# Tests: Form Submission Model
# ============================================================================

@pytest.mark.unit
class TestFormSubmission:
    """Test FormSubmission model validation"""
    
    def test_form_submission_minimal(self, plaintiff_factory, defendant_factory):
        """Test minimal valid form submission"""
        # Arrange & Act
        form = FormSubmission(
            PlaintiffDetails=[plaintiff_factory()],
            DefendantDetails2=[defendant_factory()]
        )
        
        # Assert
        assert len(form.PlaintiffDetails) == 1
        assert len(form.DefendantDetails2) == 1
    
    def test_form_submission_complete(
        self, plaintiff_factory, defendant_factory, address_factory
    ):
        """Test complete form submission"""
        # Arrange & Act
        form = FormSubmission(
            Full_Address=address_factory(),
            Filing_city="Los Angeles",
            Filing_county="Los Angeles County",
            PlaintiffDetails=[plaintiff_factory()],
            DefendantDetails2=[defendant_factory()],
            Form={"Name": "Test Form", "InternalName": "test-form"}
        )
        
        # Assert
        assert form.Full_Address is not None
        assert form.Filing_city == "Los Angeles"
        assert form.Form["Name"] == "Test Form"
    
    def test_form_submission_field_aliases(self):
        """Test that field aliases work in form submission"""
        # Arrange
        data = {
            "Filing city": "Los Angeles",
            "Filing county": "LA County",
            "PlaintiffDetails": [{
                "ItemNumber": 1,
                "PlaintiffItemNumberName": {"First": "John", "Last": "Doe"}
            }],
            "DefendantDetails2": [{
                "ItemNumber": 1,
                "DefendantItemNumberName": {"First": "Jane", "Last": "Smith"}
            }]
        }
        
        # Act
        form = FormSubmission(**data)
        
        # Assert
        assert form.Filing_city == "Los Angeles"
        assert form.Filing_county == "LA County"


# ============================================================================
# Tests: Response Models
# ============================================================================

@pytest.mark.unit
class TestCaseResponse:
    """Test CaseResponse model"""
    
    def test_case_response_creation(self):
        """Test creating case response"""
        # Arrange
        case_id = UUID("12345678-1234-5678-1234-567812345678")
        
        # Act
        response = CaseResponse(
            case_id=case_id,
            created_at=datetime.now(),
            plaintiff_count=2,
            defendant_count=3,
            issue_count=5
        )
        
        # Assert
        assert response.case_id == case_id
        assert response.plaintiff_count == 2
        assert response.defendant_count == 3
        assert response.issue_count == 5
        assert response.message == "Case created successfully"


@pytest.mark.unit
class TestHealthCheckResponse:
    """Test HealthCheckResponse model"""
    
    def test_health_check_response(self):
        """Test health check response structure"""
        # Arrange & Act
        response = HealthCheckResponse(
            status="healthy",
            database="connected",
            version="1.0.0",
            timestamp=datetime.now()
        )
        
        # Assert
        assert response.status == "healthy"
        assert response.database == "connected"
        assert response.version == "1.0.0"


@pytest.mark.unit
class TestErrorResponse:
    """Test ErrorResponse model"""
    
    def test_error_response_with_detail(self):
        """Test error response with detail"""
        # Arrange & Act
        response = ErrorResponse(
            error="Bad Request",
            detail="Missing required field",
            timestamp=datetime.now()
        )
        
        # Assert
        assert response.error == "Bad Request"
        assert response.detail == "Missing required field"
    
    def test_error_response_without_detail(self):
        """Test error response without detail"""
        # Arrange & Act
        response = ErrorResponse(
            error="Internal Server Error",
            timestamp=datetime.now()
        )
        
        # Assert
        assert response.error == "Internal Server Error"
        assert response.detail is None


# ============================================================================
# Tests: Update Models
# ============================================================================

@pytest.mark.unit
class TestPartyUpdate:
    """Test PartyUpdate model"""
    
    def test_party_update_single_field(self):
        """Test updating single field"""
        # Arrange & Act
        update = PartyUpdate(first_name="Updated")
        
        # Assert
        assert update.first_name == "Updated"
        assert update.last_name is None
    
    def test_party_update_multiple_fields(self):
        """Test updating multiple fields"""
        # Arrange & Act
        update = PartyUpdate(
            first_name="John",
            last_name="Doe",
            unit_number="101",
            is_head_of_household=True
        )
        
        # Assert
        assert update.first_name == "John"
        assert update.last_name == "Doe"
        assert update.unit_number == "101"
        assert update.is_head_of_household is True
    
    def test_party_update_model_dump_excludes_none(self):
        """Test that model dump excludes None values"""
        # Arrange
        update = PartyUpdate(first_name="John")
        
        # Act
        data = update.model_dump(exclude_none=True)
        
        # Assert
        assert "first_name" in data
        assert "last_name" not in data
        assert "unit_number" not in data


@pytest.mark.unit
class TestPartyUpdateResponse:
    """Test PartyUpdateResponse model"""
    
    def test_party_update_response(self):
        """Test party update response structure"""
        # Arrange
        party_id = UUID("12345678-1234-5678-1234-567812345678")
        case_id = UUID("87654321-4321-8765-4321-876543218765")
        
        # Act
        response = PartyUpdateResponse(
            party_id=party_id,
            case_id=case_id,
            updated_fields=["first_name", "last_name"],
            latest_payload_updated=True
        )
        
        # Assert
        assert response.party_id == party_id
        assert response.case_id == case_id
        assert len(response.updated_fields) == 2
        assert response.latest_payload_updated is True

