"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


# ============================================================================
# Request Models (Form Submission)
# ============================================================================

class PlaintiffDiscovery(BaseModel):
    """Discovery/Issue details for a plaintiff"""
    # Boolean flags for issue categories
    VerminIssue: Optional[bool] = False
    InsectIssues: Optional[bool] = False
    HVACIssues: Optional[bool] = False
    ElectricalIssues: Optional[bool] = False
    FireHazardIssues: Optional[bool] = False
    GovernmentEntityContacted: Optional[bool] = False
    AppliancesIssues: Optional[bool] = False
    PlumbingIssues: Optional[bool] = False
    CabinetsIssues: Optional[bool] = False
    FlooringIssues: Optional[bool] = False
    WindowsIssues: Optional[bool] = False
    DoorIssues: Optional[bool] = False
    StructureIssues: Optional[bool] = False
    CommonAreasIssues: Optional[bool] = False
    TrashProblems: Optional[bool] = False
    NuisanceIssues: Optional[bool] = False
    HealthHazardIssues: Optional[bool] = False
    SafetyIssues: Optional[bool] = False
    NoticesIssues: Optional[bool] = False

    # Issue arrays
    Vermin: Optional[List[str]] = []
    Insects: Optional[List[str]] = []
    HVAC: Optional[List[str]] = []
    Electrical: Optional[List[str]] = []
    FireHazard: Optional[List[str]] = Field(default=[], alias="Fire Hazard")
    GovernmentEntities: Optional[List[str]] = Field(default=[], alias="Specific Government Entity Contacted")
    Appliances: Optional[List[str]] = []
    Plumbing: Optional[List[str]] = []
    Cabinets: Optional[List[str]] = []
    Flooring: Optional[List[str]] = []
    Windows: Optional[List[str]] = []
    Doors: Optional[List[str]] = []
    Structure: Optional[List[str]] = []
    CommonAreas: Optional[List[str]] = Field(default=[], alias="Common areas")
    TrashProblemsSelect: Optional[List[str]] = Field(default=[], alias="Select Trash Problems")
    Nuisance: Optional[List[str]] = []
    HealthHazard: Optional[List[str]] = Field(default=[], alias="Health hazard")
    Safety: Optional[List[str]] = Field(default=[], alias="Select Safety Issues")
    Notices: Optional[List[str]] = Field(default=[], alias="Select Notices Issues")

    # Unit and other fields
    Unit: Optional[str] = None

    class Config:
        populate_by_name = True


class PlaintiffName(BaseModel):
    """Plaintiff name structure"""
    First: str
    Last: str
    FirstAndLast: Optional[str] = None
    Middle: Optional[str] = None
    MiddleInitial: Optional[str] = None
    Prefix: Optional[str] = None
    Suffix: Optional[str] = None


class PlaintiffDetail(BaseModel):
    """Plaintiff details from form submission"""
    Id: Optional[str] = None
    PlaintiffItemNumberName: PlaintiffName
    PlaintiffItemNumberType: Optional[str] = None
    PlaintiffItemNumberAgeCategory: Optional[List[str]] = []
    PlaintiffItemNumberDiscovery: Optional[PlaintiffDiscovery] = None
    HeadOfHousehold: Optional[bool] = False
    ItemNumber: int


class DefendantName(BaseModel):
    """Defendant name structure"""
    First: Optional[str] = None
    Last: Optional[str] = None
    FirstAndLast: Optional[str] = None
    Middle: Optional[str] = None
    MiddleInitial: Optional[str] = None
    Prefix: Optional[str] = None
    Suffix: Optional[str] = None


class DefendantDetail(BaseModel):
    """Defendant details from form submission"""
    Id: Optional[str] = None
    DefendantItemNumberName: DefendantName
    DefendantItemNumberType: Optional[str] = None
    DefendantItemNumberManagerOwner: Optional[str] = None
    ItemNumber: int


class FullAddress(BaseModel):
    """Full address structure (optional, may not be present in all submissions)"""
    StreetAddress: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    PostalCode: Optional[str] = None
    Country: Optional[str] = "United States"
    CountryCode: Optional[str] = "US"
    FullAddress: Optional[str] = None
    FullInternationalAddress: Optional[str] = None
    CityStatePostalCode: Optional[str] = None
    Line1: Optional[str] = None
    Line2: Optional[str] = None
    Line3: Optional[str] = None
    Latitude: Optional[float] = None
    Longitude: Optional[float] = None
    Type: Optional[str] = None


class FormSubmission(BaseModel):
    """Complete form submission payload"""
    # Property information
    Full_Address: Optional[FullAddress] = None
    Filing_city: Optional[str] = Field(None, alias="Filing city")
    Filing_county: Optional[str] = Field(None, alias="Filing county")

    # Parties
    PlaintiffDetails: List[PlaintiffDetail] = []
    DefendantDetails2: List[DefendantDetail] = []

    # Form metadata (optional)
    Form: Optional[dict] = None

    class Config:
        populate_by_name = True


# ============================================================================
# Response Models
# ============================================================================

class CaseResponse(BaseModel):
    """Response after creating a case"""
    case_id: UUID
    created_at: datetime
    plaintiff_count: int
    defendant_count: int
    issue_count: int
    message: str = "Case created successfully"


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    version: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime


# ============================================================================
# Edit/Update Models
# ============================================================================

class PartyUpdate(BaseModel):
    """Model for updating party details"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    unit_number: Optional[str] = None
    is_head_of_household: Optional[bool] = None

    class Config:
        # At least one field must be provided
        validate_assignment = True


class PartyUpdateResponse(BaseModel):
    """Response after updating a party"""
    party_id: UUID
    case_id: UUID
    updated_fields: List[str]
    latest_payload_updated: bool
    message: str = "Party updated successfully"


class IssueAddResponse(BaseModel):
    """Response after adding an issue to a party"""
    party_id: UUID
    case_id: UUID
    issue_option_id: UUID
    category_name: str
    option_name: str
    latest_payload_updated: bool
    message: str = "Issue added successfully"


class IssueDeleteResponse(BaseModel):
    """Response after removing an issue from a party"""
    party_id: UUID
    case_id: UUID
    issue_option_id: UUID
    latest_payload_updated: bool
    message: str = "Issue removed successfully"
