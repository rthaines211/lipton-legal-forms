"""
Integration Tests for API Endpoints

Tests cover the complete HTTP request/response cycle:
- Request validation
- Database operations
- Response structure
- Error handling
"""
import pytest
from fastapi.testclient import TestClient
from uuid import UUID
import json

from api.main import app


@pytest.mark.integration
class TestHealthEndpoints:
    """Test health check and status endpoints"""
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns API information"""
        # Arrange & Act
        response = client.get("/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"
        assert "endpoints" in data
    
    def test_health_check_endpoint(self, client: TestClient):
        """Test health check endpoint returns healthy status"""
        # Arrange & Act
        response = client.get("/health")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["database"] in ["connected", "disconnected"]
        assert "version" in data
        assert "timestamp" in data


@pytest.mark.integration
class TestFormSubmissionEndpoint:
    """Test form submission endpoint"""
    
    def test_submit_valid_form(self, client: TestClient, sample_form_data):
        """Test submitting a valid form returns success"""
        # Arrange
        # sample_form_data fixture provides valid form data
        
        # Act
        response = client.post("/api/form-submissions", json=sample_form_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        
        assert "case_id" in data
        assert UUID(data["case_id"])  # Validates it's a valid UUID
        assert data["plaintiff_count"] == 1
        assert data["defendant_count"] == 1
        assert data["issue_count"] >= 0
        assert "created_at" in data
        assert data["message"] == "Form submission processed successfully"
    
    def test_submit_form_without_plaintiffs(self, client: TestClient, sample_form_data):
        """Test submitting form without plaintiffs returns 400"""
        # Arrange
        form_data = sample_form_data.copy()
        form_data["PlaintiffDetails"] = []
        
        # Act
        response = client.post("/api/form-submissions", json=form_data)
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "plaintiff" in data["detail"].lower()
    
    def test_submit_form_without_defendants(self, client: TestClient, sample_form_data):
        """Test submitting form without defendants returns 400"""
        # Arrange
        form_data = sample_form_data.copy()
        form_data["DefendantDetails2"] = []
        
        # Act
        response = client.post("/api/form-submissions", json=form_data)
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "defendant" in data["detail"].lower()
    
    def test_submit_form_with_invalid_json(self, client: TestClient):
        """Test submitting malformed JSON returns 400"""
        # Arrange
        invalid_data = {"invalid": "structure"}
        
        # Act
        response = client.post("/api/form-submissions", json=invalid_data)
        
        # Assert
        assert response.status_code == 400  # Bad request (missing required fields)
    
    def test_submit_form_with_multiple_plaintiffs(self, client: TestClient, sample_form_data):
        """Test submitting form with multiple plaintiffs"""
        # Arrange
        form_data = sample_form_data.copy()
        
        # Add second plaintiff
        second_plaintiff = {
            "ItemNumber": 2,
            "PlaintiffItemNumberName": {
                "First": "Jane",
                "Last": "Plaintiff",
                "FirstAndLast": "Jane Plaintiff"
            },
            "PlaintiffItemNumberType": "Individual",
            "HeadOfHousehold": False,
            "PlaintiffItemNumberAgeCategory": ["adult"],
            "PlaintiffItemNumberDiscovery": {
                "VerminIssue": False,
                "Unit": "102"
            }
        }
        form_data["PlaintiffDetails"].append(second_plaintiff)
        
        # Act
        response = client.post("/api/form-submissions", json=form_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["plaintiff_count"] == 2
    
    def test_submit_form_stores_raw_payload(self, client: TestClient, sample_form_data, db_helper):
        """Test that form submission stores raw payload in database"""
        # Arrange & Act
        response = client.post("/api/form-submissions", json=sample_form_data)
        
        # Assert
        assert response.status_code == 201
        case_id = response.json()["case_id"]
        
        # Verify payload was stored
        case = db_helper.get_case_by_id(case_id)
        assert case is not None
        assert case["raw_payload"] is not None
        
        # PostgreSQL JSONB returns dict directly, not JSON string
        raw_payload = case["raw_payload"] if isinstance(case["raw_payload"], dict) else json.loads(case["raw_payload"])
        assert "PlaintiffDetails" in raw_payload
        assert "DefendantDetails2" in raw_payload


@pytest.mark.integration
class TestCaseRetrievalEndpoints:
    """Test case retrieval endpoints"""
    
    def test_get_cases_empty_database(self, client: TestClient):
        """Test getting cases when database is empty or test transaction"""
        # Arrange & Act
        response = client.get("/api/cases")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "cases" in data
        assert isinstance(data["cases"], list)
        assert "count" in data
        assert data["limit"] == 100  # Default limit
        assert data["offset"] == 0
    
    def test_get_cases_with_limit(self, client: TestClient):
        """Test getting cases with custom limit"""
        # Arrange & Act
        response = client.get("/api/cases?limit=10&offset=5")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert data["limit"] == 10
        assert data["offset"] == 5
    
    def test_get_case_by_id_not_found(self, client: TestClient):
        """Test getting non-existent case returns 404"""
        # Arrange
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        
        # Act
        response = client.get(f"/api/cases/{fake_uuid}")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_get_case_by_id_success(self, client: TestClient, sample_form_data):
        """Test getting case by ID returns complete details"""
        # Arrange - First create a case
        create_response = client.post("/api/form-submissions", json=sample_form_data)
        case_id = create_response.json()["case_id"]
        
        # Act
        response = client.get(f"/api/cases/{case_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "case" in data
        assert "parties" in data
        assert "issues" in data
        assert data["case"]["id"] == case_id
    
    def test_get_case_includes_plaintiff_count(self, client: TestClient, sample_form_data):
        """Test that case details include party counts"""
        # Arrange
        create_response = client.post("/api/form-submissions", json=sample_form_data)
        case_id = create_response.json()["case_id"]
        
        # Act
        response = client.get(f"/api/cases/{case_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "plaintiff_count" in data["case"]
        assert "defendant_count" in data["case"]
        assert data["case"]["plaintiff_count"] >= 1
        assert data["case"]["defendant_count"] >= 1


@pytest.mark.integration
class TestTaxonomyEndpoint:
    """Test taxonomy retrieval endpoint"""
    
    def test_get_taxonomy(self, client: TestClient):
        """Test getting complete taxonomy"""
        # Arrange & Act
        response = client.get("/api/taxonomy")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "categories" in data
        assert "total_categories" in data
        assert "timestamp" in data
        assert isinstance(data["categories"], list)
        assert data["total_categories"] > 0
    
    def test_taxonomy_structure(self, client: TestClient):
        """Test taxonomy has correct structure"""
        # Arrange & Act
        response = client.get("/api/taxonomy")
        
        # Assert
        assert response.status_code == 200
        categories = response.json()["categories"]
        
        if categories:
            first_category = categories[0]
            assert "category_id" in first_category
            assert "category_code" in first_category
            assert "category_name" in first_category
            assert "options" in first_category
            assert isinstance(first_category["options"], list)
    
    def test_taxonomy_options_have_required_fields(self, client: TestClient):
        """Test that taxonomy options include required fields"""
        # Arrange & Act
        response = client.get("/api/taxonomy")
        
        # Assert
        categories = response.json()["categories"]
        
        for category in categories:
            if category["options"]:
                option = category["options"][0]
                assert "id" in option
                assert "code" in option
                assert "name" in option
                assert "order" in option


@pytest.mark.integration
class TestPartyUpdateEndpoint:
    """Test party update endpoint"""
    
    def test_update_party_name(self, client: TestClient, sample_form_data):
        """Test updating party first and last name"""
        # Arrange - Create a case first
        create_response = client.post("/api/form-submissions", json=sample_form_data)
        case_id = create_response.json()["case_id"]
        
        # Get party ID
        case_response = client.get(f"/api/cases/{case_id}")
        parties = case_response.json()["parties"]
        party_id = parties[0]["id"]
        
        # Act
        update_data = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        response = client.patch(f"/api/parties/{party_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert data["party_id"] == party_id
        assert "first_name" in data["updated_fields"]
        assert "last_name" in data["updated_fields"]
        assert data["latest_payload_updated"] is True
    
    def test_update_party_not_found(self, client: TestClient):
        """Test updating non-existent party returns 404"""
        # Arrange
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        update_data = {"first_name": "Test"}
        
        # Act
        response = client.patch(f"/api/parties/{fake_uuid}", json=update_data)
        
        # Assert
        assert response.status_code == 404
    
    def test_update_party_no_fields(self, client: TestClient, sample_form_data):
        """Test updating party with no fields returns 400"""
        # Arrange
        create_response = client.post("/api/form-submissions", json=sample_form_data)
        case_id = create_response.json()["case_id"]
        
        case_response = client.get(f"/api/cases/{case_id}")
        party_id = case_response.json()["parties"][0]["id"]
        
        # Act
        response = client.patch(f"/api/parties/{party_id}", json={})
        
        # Assert
        assert response.status_code == 400


@pytest.mark.integration
class TestIssueManagementEndpoints:
    """Test issue add/remove endpoints"""
    
    def test_add_issue_to_plaintiff(self, client: TestClient, sample_form_data):
        """Test adding an issue to a plaintiff"""
        # Arrange - Create case and get plaintiff
        create_response = client.post("/api/form-submissions", json=sample_form_data)
        case_id = create_response.json()["case_id"]
        
        case_response = client.get(f"/api/cases/{case_id}")
        plaintiff = next(
            p for p in case_response.json()["parties"] if p["party_type"] == "plaintiff"
        )
        party_id = plaintiff["id"]
        
        # Get an issue option ID
        taxonomy_response = client.get("/api/taxonomy")
        categories = taxonomy_response.json()["categories"]
        option_id = categories[0]["options"][0]["id"]
        
        # Act
        response = client.post(f"/api/parties/{party_id}/issues/{option_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert data["party_id"] == party_id
        assert data["case_id"] == case_id
        assert data["issue_option_id"] == option_id
        assert data["latest_payload_updated"] is True
    
    def test_add_issue_to_defendant_fails(self, client: TestClient, sample_form_data):
        """Test that adding issue to defendant returns 400"""
        # Arrange
        create_response = client.post("/api/form-submissions", json=sample_form_data)
        case_id = create_response.json()["case_id"]
        
        case_response = client.get(f"/api/cases/{case_id}")
        defendant = next(
            p for p in case_response.json()["parties"] if p["party_type"] == "defendant"
        )
        party_id = defendant["id"]
        
        taxonomy_response = client.get("/api/taxonomy")
        option_id = taxonomy_response.json()["categories"][0]["options"][0]["id"]
        
        # Act
        response = client.post(f"/api/parties/{party_id}/issues/{option_id}")
        
        # Assert
        assert response.status_code == 400
        assert "plaintiff" in response.json()["detail"].lower()
    
    def test_remove_issue_from_plaintiff(self, client: TestClient, sample_form_data):
        """Test removing an issue from a plaintiff"""
        # Arrange - Create case, add issue, then remove it
        create_response = client.post("/api/form-submissions", json=sample_form_data)
        case_id = create_response.json()["case_id"]
        
        case_response = client.get(f"/api/cases/{case_id}")
        plaintiff = next(
            p for p in case_response.json()["parties"] if p["party_type"] == "plaintiff"
        )
        party_id = plaintiff["id"]
        
        # Get existing issue
        issues = case_response.json()["issues"]
        if issues:
            # Get option_id from existing issue
            taxonomy_response = client.get("/api/taxonomy")
            categories = taxonomy_response.json()["categories"]
            
            # Find matching option
            option_id = None
            for category in categories:
                for option in category["options"]:
                    if option["name"] == issues[0]["selected_issues"][0]:
                        option_id = option["id"]
                        break
                if option_id:
                    break
            
            # Act
            if option_id:
                response = client.delete(f"/api/parties/{party_id}/issues/{option_id}")
                
                # Assert
                assert response.status_code == 200
                data = response.json()
                assert data["latest_payload_updated"] is True


@pytest.mark.integration
class TestErrorHandling:
    """Test API error handling"""
    
    def test_invalid_uuid_format(self, client: TestClient):
        """Test that invalid UUID format returns appropriate error"""
        # Arrange & Act
        response = client.get("/api/cases/invalid-uuid")
        
        # Assert
        assert response.status_code == 500  # Database error for invalid UUID
    
    def test_method_not_allowed(self, client: TestClient):
        """Test that wrong HTTP method returns 405"""
        # Arrange & Act
        response = client.delete("/api/form-submissions")
        
        # Assert
        assert response.status_code == 405

