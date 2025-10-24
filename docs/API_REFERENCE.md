# API Reference Documentation

## Table of Contents
- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Endpoints](#endpoints)
  - [Form Entries](#form-entries)
  - [Pipeline Management](#pipeline-management)
  - [Health & Monitoring](#health--monitoring)
  - [Static Pages](#static-pages)
- [Code Examples](#code-examples)

## Overview

The Legal Form Application API is a RESTful API for managing legal form submissions with comprehensive data transformation, dual storage (JSON + PostgreSQL), and optional cloud backup.

**API Version:** 1.0.0
**Content-Type:** application/json
**Character Encoding:** UTF-8

## Authentication

### Production Mode
When `NODE_ENV=production`, all API endpoints (except health checks and metrics) require authentication.

#### Method 1: Query Parameter
```
GET /api/form-entries?token=YOUR_ACCESS_TOKEN
```

#### Method 2: Authorization Header
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Development Mode
When `NODE_ENV` is not set to `production`, authentication is **disabled** for easier local development.

### Endpoints That Bypass Authentication
The following endpoints are always accessible without authentication:
- `/health`
- `/api/health`
- `/health/ready`
- `/health/detailed`
- `/metrics`

## Base URL

### Development
```
http://localhost:3000
```

### Production
```
https://your-production-domain.com
```

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... }
}
```

### Error Response
```json
{
  "error": "Error Type",
  "message": "Human-readable error description",
  "details": {
    "field": "Additional error context"
  }
}
```

## Error Handling

### HTTP Status Codes

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid authentication token |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server-side error occurred |
| 503 | Service Unavailable | Dependent service (DB, Pipeline) unavailable |

### Common Error Responses

#### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Valid access token required. Provide token in URL (?token=xxx) or Authorization header (Bearer xxx)."
}
```

#### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Form entry with ID '123456' not found"
}
```

#### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "Failed to save form entry",
  "details": {
    "timestamp": "2025-10-21T12:00:00.000Z"
  }
}
```

## Rate Limiting

**Current Status:** Not implemented

**Recommended for Production:**
- 100 requests per minute per IP
- Burst limit: 200 requests
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Endpoints

---

## Form Entries

### Create Form Entry

Submit a new legal form entry with plaintiff, defendant, and issue tracking data.

**Endpoint:** `POST /api/form-entries`

**Authentication:** Required (production only)

**Request Body:**
```json
{
  "Form": {
    "Id": "1",
    "InternalName": "AutoPopulationForm",
    "Name": "Auto-Population Form"
  },
  "Full_Address": {
    "StreetAddress": "1331 Yorkshire Place NW",
    "City": "Concord",
    "State": "North Carolina",
    "PostalCode": "28027",
    "Country": "United States",
    "CountryCode": "US"
  },
  "Filing city": "Los Angeles",
  "Filing county": "Los Angeles County",
  "submitter_name": "John Doe",
  "submitter_email": "john.doe@example.com",
  "PlaintiffDetails": [
    {
      "ItemNumber": 1,
      "PlaintiffItemNumberName": {
        "First": "Clark",
        "Last": "Kent",
        "FirstAndLast": "Clark Kent"
      },
      "PlaintiffItemNumberType": "Individual",
      "PlaintiffItemNumberAgeCategory": ["Adult"],
      "HeadOfHousehold": true,
      "PlaintiffItemNumberDiscovery": {
        "VerminIssue": true,
        "Vermin": ["Rats/Mice", "Bedbugs"],
        "InsectIssues": true,
        "Insects": ["Roaches", "Ants"],
        "Unit": "1"
      }
    }
  ],
  "DefendantDetails2": [
    {
      "ItemNumber": 1,
      "DefendantItemNumberName": {
        "First": "Jane",
        "Last": "Smith",
        "FirstAndLast": "Jane Smith"
      },
      "DefendantItemNumberType": "LLC",
      "DefendantItemNumberManagerOwner": "Manager"
    }
  ]
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Form submission successful",
  "entry": {
    "id": "1729539600000-abc123",
    "timestamp": 1729539600000,
    "filename": "form-entry-1729539600000-abc123.json"
  },
  "database": {
    "case_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "plaintiff_count": 1,
    "defendant_count": 1
  },
  "dropbox": {
    "uploaded": true,
    "path": "/Apps/LegalFormApp/data/form-entry-1729539600000-abc123.json"
  },
  "pipeline": {
    "triggered": true,
    "status": "processing"
  }
}
```

**Workflow:**
1. Validates incoming JSON structure
2. Transforms data to internal format
3. Generates unique timestamp-based ID
4. **Parallel operations:**
   - Saves JSON file to `data/` directory
   - Inserts records into PostgreSQL database
   - Uploads to Dropbox (if enabled)
5. Triggers normalization pipeline (if enabled)
6. Returns success response with all operation results

---

### List All Form Entries

Retrieve all form submissions stored in the system.

**Endpoint:** `GET /api/form-entries`

**Authentication:** Required (production only)

**Query Parameters:** None

**Response:** `200 OK`
```json
{
  "entries": [
    {
      "id": "1729539600000-abc123",
      "timestamp": 1729539600000,
      "filename": "form-entry-1729539600000-abc123.json",
      "Form": { ... },
      "Full_Address": { ... },
      "PlaintiffDetails": [ ... ],
      "DefendantDetails2": [ ... ]
    }
  ],
  "count": 1
}
```

**Notes:**
- Returns all JSON files from the `data/` directory
- Files are sorted by timestamp (newest first)
- No pagination implemented (consider adding for large datasets)

---

### Get Form Entry by ID

Retrieve a specific form submission by its unique ID.

**Endpoint:** `GET /api/form-entries/:id`

**Authentication:** Required (production only)

**Path Parameters:**
- `id` (string, required) - Form entry ID
  - Example: `1729539600000-abc123`

**Response:** `200 OK`
```json
{
  "id": "1729539600000-abc123",
  "timestamp": 1729539600000,
  "filename": "form-entry-1729539600000-abc123.json",
  "Form": {
    "Id": "1",
    "InternalName": "AutoPopulationForm",
    "Name": "Auto-Population Form"
  },
  "Full_Address": {
    "StreetAddress": "1331 Yorkshire Place NW",
    "City": "Concord",
    "State": "North Carolina",
    "PostalCode": "28027"
  },
  "PlaintiffDetails": [ ... ],
  "DefendantDetails2": [ ... ]
}
```

**Error Response:** `404 Not Found`
```json
{
  "error": "Not Found",
  "message": "Form entry with ID '1729539600000-abc123' not found"
}
```

---

### Update Form Entry

Update an existing form submission.

**Endpoint:** `PUT /api/form-entries/:id`

**Authentication:** Required (production only)

**Path Parameters:**
- `id` (string, required) - Form entry ID

**Request Body:**
```json
{
  "Full_Address": {
    "StreetAddress": "Updated Address",
    "City": "Updated City",
    "State": "California",
    "PostalCode": "90001"
  },
  "PlaintiffDetails": [ ... ],
  "DefendantDetails2": [ ... ]
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Form entry updated successfully",
  "entry": {
    "id": "1729539600000-abc123",
    "filename": "form-entry-1729539600000-abc123.json"
  }
}
```

**Notes:**
- Replaces the entire form entry with new data
- Updates both JSON file and database record
- Triggers Dropbox sync if enabled

---

### Delete Form Entry

Delete a specific form submission.

**Endpoint:** `DELETE /api/form-entries/:id`

**Authentication:** Required (production only)

**Path Parameters:**
- `id` (string, required) - Form entry ID

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Form entry deleted successfully",
  "deletedId": "1729539600000-abc123"
}
```

**Error Response:** `404 Not Found`
```json
{
  "error": "Not Found",
  "message": "Form entry with ID '1729539600000-abc123' not found"
}
```

**Notes:**
- Deletes JSON file from `data/` directory
- Does NOT delete database record (database operations are separate)
- Cannot be undone

---

### Delete All Form Entries

**⚠️ DANGER:** Delete all form submissions from the system.

**Endpoint:** `DELETE /api/form-entries/clear-all`

**Authentication:** Required (production only)

**Request Body:** None

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "All form entries deleted successfully",
  "deletedCount": 42
}
```

**Warning:**
- This operation **cannot be undone**
- Deletes all JSON files in `data/` directory
- Does NOT delete database records
- Use with extreme caution in production

---

## Pipeline Management

### Get Pipeline Status

Retrieve the current status of the normalization pipeline for a specific case.

**Endpoint:** `GET /api/pipeline-status/:caseId`

**Authentication:** Required (production only)

**Path Parameters:**
- `caseId` (UUID, required) - Case UUID from database

**Response:** `200 OK`
```json
{
  "case_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "pipeline_status": "completed",
  "last_run": "2025-10-21T12:00:00.000Z",
  "error_message": null,
  "phases_completed": [
    "extraction",
    "normalization",
    "validation",
    "enrichment",
    "persistence"
  ],
  "processing_time_ms": 2450
}
```

**Pipeline Status Values:**
- `pending` - Pipeline not yet run
- `processing` - Currently running
- `completed` - Successfully completed
- `failed` - Encountered error

**Error Response:** `404 Not Found`
```json
{
  "error": "Not Found",
  "message": "Case with ID 'a1b2c3d4-...' not found"
}
```

---

### Retry Pipeline Processing

Manually trigger the normalization pipeline for a specific case.

**Endpoint:** `POST /api/pipeline-retry/:caseId`

**Authentication:** Required (production only)

**Path Parameters:**
- `caseId` (UUID, required) - Case UUID from database

**Request Body:** None

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Pipeline processing initiated",
  "case_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "pipeline_status": "processing"
}
```

**Use Cases:**
- Retry failed pipeline runs
- Re-process after data corrections
- Trigger normalization for old cases

**Error Response:** `503 Service Unavailable`
```json
{
  "error": "Service Unavailable",
  "message": "Pipeline service is not available",
  "details": {
    "pipeline_url": "http://localhost:8000",
    "error": "ECONNREFUSED"
  }
}
```

---

## Health & Monitoring

### Basic Health Check

Check if the application is running and healthy.

**Endpoint:** `GET /health` or `GET /api/health`

**Authentication:** Not required

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2025-10-21T12:00:00.000Z",
  "uptime": 3600.5,
  "database": "connected"
}
```

**Response:** `503 Service Unavailable`
```json
{
  "status": "unhealthy",
  "timestamp": "2025-10-21T12:00:00.000Z",
  "uptime": 3600.5,
  "database": "disconnected",
  "error": "Database connection failed"
}
```

---

### Readiness Probe

Kubernetes-style readiness check to determine if the service can handle traffic.

**Endpoint:** `GET /health/ready`

**Authentication:** Not required

**Response:** `200 OK`
```json
{
  "status": "ready",
  "timestamp": "2025-10-21T12:00:00.000Z",
  "checks": {
    "database": "pass",
    "filesystem": "pass"
  }
}
```

**Response:** `503 Service Unavailable`
```json
{
  "status": "not ready",
  "timestamp": "2025-10-21T12:00:00.000Z",
  "checks": {
    "database": "fail",
    "filesystem": "pass"
  },
  "errors": [
    "Database connection pool exhausted"
  ]
}
```

---

### Detailed Health Check

Comprehensive health information including all dependencies.

**Endpoint:** `GET /health/detailed`

**Authentication:** Not required

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2025-10-21T12:00:00.000Z",
  "uptime": 3600.5,
  "version": "1.0.0",
  "environment": "production",
  "checks": {
    "database": {
      "status": "healthy",
      "latency_ms": 5.2,
      "pool_total": 20,
      "pool_idle": 15,
      "pool_waiting": 0
    },
    "filesystem": {
      "status": "healthy",
      "writable": true,
      "data_directory": "/app/data",
      "available_space_mb": 15000
    },
    "dropbox": {
      "enabled": true,
      "status": "healthy",
      "last_upload": "2025-10-21T11:55:00.000Z"
    },
    "pipeline": {
      "enabled": true,
      "url": "http://localhost:8000",
      "reachable": true,
      "version": "1.0.0"
    }
  },
  "metrics": {
    "total_submissions": 1250,
    "submissions_today": 42,
    "avg_response_time_ms": 85.3
  }
}
```

---

### Prometheus Metrics

Expose application metrics in Prometheus format.

**Endpoint:** `GET /metrics`

**Authentication:** Not required

**Response:** `200 OK` (text/plain)
```
# HELP http_request_duration_seconds HTTP request duration in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1",method="GET",route="/api/form-entries",status_code="200"} 45
http_request_duration_seconds_bucket{le="0.5",method="GET",route="/api/form-entries",status_code="200"} 50
http_request_duration_seconds_sum{method="GET",route="/api/form-entries",status_code="200"} 12.5
http_request_duration_seconds_count{method="GET",route="/api/form-entries",status_code="200"} 50

# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",route="/api/form-entries",status_code="200"} 50
http_requests_total{method="POST",route="/api/form-entries",status_code="200"} 42

# HELP database_connections_active Active database connections
# TYPE database_connections_active gauge
database_connections_active 5
```

**Available Metrics:**
- `http_request_duration_seconds` - Request duration histogram
- `http_requests_total` - Total request counter
- `database_connections_active` - Active DB connections
- `database_query_duration_seconds` - Database query latency
- `form_submissions_total` - Total form submissions
- `pipeline_processing_duration_seconds` - Pipeline processing time

---

## Static Pages

### Main Form Page

**Endpoint:** `GET /`

**Authentication:** Required (production only)

**Response:** HTML form page

**Description:** Serves the main legal form interface where users can:
- Enter property information
- Add multiple plaintiffs with issue tracking
- Add multiple defendants
- Review submission before finalizing
- Submit form data

---

### Review Page

**Endpoint:** `GET /review.html`

**Authentication:** Required (production only)

**Response:** HTML review page

**Description:** Displays a preview of the form submission allowing users to review and make changes before final submission.

---

### Success Page

**Endpoint:** `GET /success`

**Authentication:** Required (production only)

**Response:** HTML success page

**Description:** Displays confirmation message after successful form submission with the entry ID.

---

## Code Examples

### JavaScript (Fetch API)

#### Submit Form Entry
```javascript
const formData = {
  "Full_Address": {
    "StreetAddress": "123 Main St",
    "City": "Los Angeles",
    "State": "California",
    "PostalCode": "90001"
  },
  "PlaintiffDetails": [
    {
      "ItemNumber": 1,
      "PlaintiffItemNumberName": {
        "First": "John",
        "Last": "Doe",
        "FirstAndLast": "John Doe"
      },
      "PlaintiffItemNumberType": "Individual",
      "HeadOfHousehold": true
    }
  ],
  "DefendantDetails2": [
    {
      "ItemNumber": 1,
      "DefendantItemNumberName": {
        "First": "ABC",
        "Last": "Properties",
        "FirstAndLast": "ABC Properties"
      },
      "DefendantItemNumberType": "LLC"
    }
  ]
};

const response = await fetch('http://localhost:3000/api/form-entries', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
  },
  body: JSON.stringify(formData)
});

const result = await response.json();
console.log('Form submitted:', result.entry.id);
```

#### Get All Entries
```javascript
const response = await fetch('http://localhost:3000/api/form-entries?token=YOUR_ACCESS_TOKEN');
const data = await response.json();

console.log(`Found ${data.count} entries`);
data.entries.forEach(entry => {
  console.log(`- ${entry.id}: ${entry.Full_Address.StreetAddress}`);
});
```

#### Check Health
```javascript
const response = await fetch('http://localhost:3000/health');
const health = await response.json();

if (health.status === 'healthy') {
  console.log('✓ Application is healthy');
  console.log(`✓ Database: ${health.database}`);
} else {
  console.error('✗ Application is unhealthy');
}
```

---

### Python (Requests)

#### Submit Form Entry
```python
import requests

form_data = {
    "Full_Address": {
        "StreetAddress": "123 Main St",
        "City": "Los Angeles",
        "State": "California",
        "PostalCode": "90001"
    },
    "PlaintiffDetails": [{
        "ItemNumber": 1,
        "PlaintiffItemNumberName": {
            "First": "John",
            "Last": "Doe",
            "FirstAndLast": "John Doe"
        },
        "PlaintiffItemNumberType": "Individual",
        "HeadOfHousehold": True
    }],
    "DefendantDetails2": [{
        "ItemNumber": 1,
        "DefendantItemNumberName": {
            "First": "ABC",
            "Last": "Properties",
            "FirstAndLast": "ABC Properties"
        },
        "DefendantItemNumberType": "LLC"
    }]
}

response = requests.post(
    'http://localhost:3000/api/form-entries',
    json=form_data,
    headers={'Authorization': 'Bearer YOUR_ACCESS_TOKEN'}
)

result = response.json()
print(f"Form submitted: {result['entry']['id']}")
```

#### Get Pipeline Status
```python
import requests

case_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

response = requests.get(
    f'http://localhost:3000/api/pipeline-status/{case_id}',
    headers={'Authorization': 'Bearer YOUR_ACCESS_TOKEN'}
)

status = response.json()
print(f"Pipeline status: {status['pipeline_status']}")
print(f"Last run: {status['last_run']}")
```

---

### cURL

#### Submit Form Entry
```bash
curl -X POST http://localhost:3000/api/form-entries \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "Full_Address": {
      "StreetAddress": "123 Main St",
      "City": "Los Angeles",
      "State": "California",
      "PostalCode": "90001"
    },
    "PlaintiffDetails": [],
    "DefendantDetails2": []
  }'
```

#### Get All Entries
```bash
curl http://localhost:3000/api/form-entries?token=YOUR_ACCESS_TOKEN
```

#### Delete Entry
```bash
curl -X DELETE http://localhost:3000/api/form-entries/1729539600000-abc123?token=YOUR_ACCESS_TOKEN
```

#### Health Check
```bash
curl http://localhost:3000/health
```

#### Prometheus Metrics
```bash
curl http://localhost:3000/metrics
```

---

## Webhooks & Events

**Current Status:** Not implemented

**Future Enhancement:** Server-Sent Events (SSE) for real-time pipeline updates.

```javascript
// Future SSE implementation
const eventSource = new EventSource('/api/events?token=YOUR_TOKEN');

eventSource.addEventListener('pipeline-update', (event) => {
  const data = JSON.parse(event.data);
  console.log(`Pipeline ${data.phase}: ${data.status}`);
});
```

---

## Versioning

**Current Version:** 1.0.0

**Versioning Strategy:** Semantic Versioning (SemVer)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

**Future:** API versioning via URL path (`/api/v2/form-entries`)

---

## Support & Feedback

- **Documentation:** `/docs` directory
- **Issues:** GitHub Issues (if applicable)
- **Interactive API Docs:** `http://localhost:8000/docs` (Python API)

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-21
**Maintained By:** Development Team
