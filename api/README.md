# Legal Forms ETL API Documentation

## Overview

FastAPI-based ETL (Extract, Transform, Load) service for ingesting legal form submissions and storing them in a normalized PostgreSQL database structure.

### Features

- ✅ **Form Submission Ingestion**: Parse and validate incoming JSON payloads
- ✅ **Atomic Transactions**: All database operations wrapped in transactions
- ✅ **Normalized Storage**: Extract data into relational tables (cases, parties, issues)
- ✅ **Dual JSON Storage**: Store both raw and latest payloads
- ✅ **Issue Taxonomy**: Link plaintiff issues to standardized taxonomy
- ✅ **RESTful API**: Full CRUD operations for cases
- ✅ **Health Monitoring**: Database connection health checks

---

## Quick Start

### 1. Setup Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database connection details
```

### 3. Start the Server

```bash
# Development mode (auto-reload)
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Or using the script
python api/main.py
```

### 4. Verify Health

```bash
curl http://localhost:8000/health
```

---

## API Endpoints

### Root
```
GET /
```
Returns API information and available endpoints.

**Response:**
```json
{
  "name": "Legal Forms ETL API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "health": "/health",
    "submit_form": "POST /api/form-submissions",
    "get_cases": "GET /api/cases",
    "get_case": "GET /api/cases/{case_id}",
    "taxonomy": "GET /api/taxonomy"
  }
}
```

### Health Check
```
GET /health
```
Check API and database health status.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0",
  "timestamp": "2025-10-07T21:00:00.000000"
}
```

### Submit Form (ETL Endpoint)
```
POST /api/form-submissions
Content-Type: application/json
```

Main ETL endpoint to ingest form submissions.

**Request Body:**
```json
{
  "Full_Address": {
    "StreetAddress": "1331 Yorkshire Place NW",
    "City": "Concord",
    "State": "North Carolina",
    "PostalCode": "28027"
  },
  "Filing city": "Los Angeles",
  "Filing county": "North Carolina",
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
        "First": "Tony",
        "Last": "Stark",
        "FirstAndLast": "Tony Stark"
      },
      "DefendantItemNumberType": "LLC",
      "DefendantItemNumberManagerOwner": "Manager"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "case_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "created_at": "2025-10-07T21:00:00.000000",
  "plaintiff_count": 1,
  "defendant_count": 1,
  "issue_count": 4,
  "message": "Form submission processed successfully"
}
```

**What Happens:**
1. Validates incoming JSON structure
2. Inserts case record with address info
3. Inserts all plaintiffs with their details
4. Inserts all defendants
5. Links plaintiff issues to taxonomy options
6. Stores complete JSON in `raw_payload` and `latest_payload`
7. All operations in a single atomic transaction

### Get All Cases
```
GET /api/cases?limit=100&offset=0
```

Retrieve list of cases with pagination.

**Query Parameters:**
- `limit` (optional, default: 100): Maximum cases to return
- `offset` (optional, default: 0): Number of cases to skip

**Response:**
```json
{
  "cases": [
    {
      "id": "uuid",
      "created_at": "2025-10-07T21:00:00",
      "property_address": "1331 Yorkshire Place NW",
      "city": "Concord",
      "state": "NC",
      "zip_code": "28027",
      "filing_location": "Los Angeles",
      "plaintiff_count": 1,
      "defendant_count": 1
    }
  ],
  "count": 1,
  "limit": 100,
  "offset": 0
}
```

### Get Specific Case
```
GET /api/cases/{case_id}
```

Get detailed case information including parties and issues.

**Response:**
```json
{
  "case": {
    "id": "uuid",
    "created_at": "2025-10-07T21:00:00",
    "property_address": "1331 Yorkshire Place NW",
    "city": "Concord",
    "state": "NC",
    "raw_payload": { ... },
    "latest_payload": { ... }
  },
  "parties": [
    {
      "id": "uuid",
      "party_type": "plaintiff",
      "party_number": 1,
      "first_name": "Clark",
      "last_name": "Kent",
      "full_name": "Clark Kent",
      "is_head_of_household": true
    }
  ],
  "issues": [
    {
      "party_id": "uuid",
      "party_number": 1,
      "category_name": "Vermin",
      "selected_issues": ["Rats/Mice", "Bedbugs"]
    }
  ]
}
```

### Get Taxonomy
```
GET /api/taxonomy
```

Retrieve the complete issue taxonomy for form rendering.

**Response:**
```json
{
  "categories": [
    {
      "category_id": "uuid",
      "category_code": "vermin",
      "category_name": "Vermin",
      "category_order": 1,
      "is_multi_select": true,
      "options": [
        {
          "id": "uuid",
          "code": "rats_mice",
          "name": "Rats/Mice",
          "order": 1
        }
      ]
    }
  ],
  "total_categories": 19,
  "timestamp": "2025-10-07T21:00:00"
}
```

---

## ETL Data Flow

### 1. Form Submission → Database

```
Form JSON
    ↓
Validation (Pydantic)
    ↓
ETL Service
    ├── Insert Case
    ├── Insert Plaintiffs
    ├── Insert Defendants
    └── Insert Issue Selections
    ↓
PostgreSQL (Transaction)
```

### 2. Database Schema Mapping

| Form Field | Database Table | Column |
|------------|----------------|--------|
| `Full_Address.StreetAddress` | `cases` | `property_address` |
| `Full_Address.City` | `cases` | `city` |
| `Filing city` | `cases` | `filing_location` |
| `PlaintiffDetails[].PlaintiffItemNumberName` | `parties` | `first_name`, `last_name` |
| `PlaintiffDetails[].HeadOfHousehold` | `parties` | `is_head_of_household` |
| `PlaintiffDetails[].PlaintiffItemNumberDiscovery.Vermin[]` | `party_issue_selections` | Links to `issue_options` |
| Entire JSON | `cases` | `raw_payload`, `latest_payload` |

### 3. Issue Mapping

The ETL service maps form issue arrays to database taxonomy:

```
Form:
"Discovery": {
  "Vermin": ["Rats/Mice", "Bedbugs"],
  "Insects": ["Roaches"]
}

Database:
party_issue_selections:
  - party_id → plaintiff UUID
  - issue_option_id → "Rats/Mice" option UUID
  - issue_option_id → "Bedbugs" option UUID
  - issue_option_id → "Roaches" option UUID
```

---

## Architecture

### Components

```
api/
├── __init__.py         # Package init
├── config.py           # Configuration (env variables)
├── database.py         # Database connection management
├── models.py           # Pydantic models (validation)
├── etl_service.py      # ETL transformation logic
└── main.py             # FastAPI application
```

### Dependencies

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **Psycopg 3**: PostgreSQL driver
- **python-dotenv**: Environment management

### Database Connection

Uses Psycopg 3 with connection pooling:
- Min connections: 2
- Max connections: 10
- Auto-commit: False (manual transaction control)
- Row factory: dict_row (results as dictionaries)

---

## Error Handling

### Validation Errors (400)

```json
{
  "detail": [
    {
      "loc": ["body", "PlaintiffDetails"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Server Errors (500)

```json
{
  "error": "Internal Server Error",
  "detail": "Failed to process form submission: ...",
  "timestamp": "2025-10-07T21:00:00"
}
```

### Transaction Rollback

All ETL operations are wrapped in transactions. If any step fails:
1. Transaction is automatically rolled back
2. No partial data is saved
3. Error is returned to client
4. Database remains consistent

---

## Testing

### Manual API Testing

```bash
# Test health
curl http://localhost:8000/health

# Test taxonomy
curl http://localhost:8000/api/taxonomy

# Submit form (with sample data from goalOutput.md)
curl -X POST http://localhost:8000/api/form-submissions \
  -H "Content-Type: application/json" \
  -d @sample_form_submission.json

# Get cases
curl http://localhost:8000/api/cases

# Get specific case
curl http://localhost:8000/api/cases/{case-uuid}
```

### Using httpie (cleaner output)

```bash
# Install httpie
pip install httpie

# Test endpoints
http GET localhost:8000/health
http GET localhost:8000/api/taxonomy
http POST localhost:8000/api/form-submissions < sample_form_submission.json
```

---

## Logging

The API logs all important operations:

```
INFO - Starting Legal Forms ETL API...
INFO - Database pool initialized
INFO - Received form submission
INFO - Created case: uuid
INFO - Inserted 1 plaintiffs
INFO - Inserted 1 defendants
INFO - Inserted 4 issue selections
INFO - Form submission processed successfully
```

---

## Development

### Running in Development

```bash
# Activate virtual environment
source venv/bin/activate

# Start with auto-reload
python -m uvicorn api.main:app --reload

# Or run main directly
python api/main.py
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://ryanhaines@localhost:5432/legal_forms` | PostgreSQL connection string |
| `DATABASE_POOL_MIN_SIZE` | `2` | Minimum pool connections |
| `DATABASE_POOL_MAX_SIZE` | `10` | Maximum pool connections |
| `API_HOST` | `0.0.0.0` | API host |
| `API_PORT` | `8000` | API port |
| `API_RELOAD` | `true` | Auto-reload on code changes |

---

## Production Deployment

### Recommended Setup

1. **Use environment variables** for sensitive configuration
2. **Set appropriate CORS origins** (not `*`)
3. **Enable HTTPS** with reverse proxy (nginx/traefik)
4. **Increase connection pool** based on load
5. **Add rate limiting** to prevent abuse
6. **Enable authentication** if needed

### Example with Gunicorn

```bash
pip install gunicorn

gunicorn api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

---

## Troubleshooting

### Database Connection Failed

```
ERROR - Database connection failed
```

**Fix:**
1. Verify PostgreSQL is running: `psql legal_forms -c "SELECT 1"`
2. Check `DATABASE_URL` in `.env`
3. Ensure database exists: `createdb legal_forms`
4. Run schema: `psql legal_forms < database/official_baseline_taxonomy.sql`

### Issue Option Not Found

```
WARNING - Issue option not found: vermin -> Squirrels
```

**Fix:**
- Option doesn't exist in database taxonomy
- Either add to taxonomy or use an existing option
- Check spelling/capitalization matches exactly

### Transaction Failed

```
ERROR - ETL transaction failed: ...
```

**Fix:**
- Check logs for specific error
- Verify data format matches Pydantic models
- Ensure required fields are present
- Check for constraint violations (e.g., duplicate HoH per unit)

---

## API Documentation

Interactive API documentation available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## License

Internal use only - Lipton Legal

---

**Version:** 1.0.0
**Last Updated:** 2025-10-07
