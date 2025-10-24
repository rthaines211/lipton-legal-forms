# Legal Discovery Normalization API

FastAPI service for normalizing legal form data and generating discovery documents.

## Overview

This API service provides REST endpoints to execute the 5-phase normalization pipeline on legal form submissions. It transforms raw form data into structured discovery documents and can optionally send them to the Docmosis webhook for document generation.

## Features

- **RESTful API**: Clean HTTP endpoints for pipeline execution
- **Async Processing**: Fast, non-blocking request handling
- **Comprehensive Validation**: Pydantic models ensure data integrity
- **Auto-generated Documentation**: OpenAPI/Swagger docs at `/docs`
- **Health Monitoring**: Built-in health check endpoints
- **Configurable**: Environment-based configuration
- **Secure**: Optional API key authentication
- **CORS Support**: Configurable cross-origin resource sharing

## Quick Start

### Installation

1. Create and activate virtual environment:
```bash
cd "normalization work"
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Running Locally

Start the development server:
```bash
# Option 1: Using uvicorn directly
uvicorn api.main:app --reload --port 8000

# Option 2: Using Python module
python -m uvicorn api.main:app --reload --port 8000

# Option 3: Run the main file
python api/main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Health Check

**GET** `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "normalization-api"
}
```

### Service Status

**GET** `/api/status`

Get detailed service configuration and status.

**Response:**
```json
{
  "status": "running",
  "service": "normalization-api",
  "version": "1.0.0",
  "configuration": {
    "webhooks_enabled": true,
    "webhook_url": "https://docs.liptonlegal.com/api/render",
    "api_key_required": false,
    "debug_mode": false
  }
}
```

### Normalize Form Data

**POST** `/api/normalize`

Execute the complete normalization pipeline on form data.

**Headers:**
```
Content-Type: application/json
X-API-Key: your-api-key-here  (if API_KEY is configured)
```

**Request Body:**
```json
{
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
      "IsHeadOfHousehold": true,
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
```

**Success Response (200):**
```json
{
  "success": true,
  "case_id": "abc123",
  "execution_time_ms": 5420,
  "phase_results": {
    "phase1": {
      "plaintiffs": 2,
      "defendants": 1,
      "case_id": "abc123"
    },
    "phase2": {
      "datasets": 2,
      "hoh_count": 2,
      "defendant_count": 1
    },
    "phase3": {
      "datasets": 2,
      "flags_applied": 180,
      "sample_true_flags": 45
    },
    "phase4": {
      "profile_datasets": 6,
      "profiles_applied": 3
    },
    "phase5": {
      "split_datasets": 6,
      "total_sets": 8,
      "max_per_set": 120
    }
  },
  "webhook_summary": {
    "total_sets": 8,
    "succeeded": 8,
    "failed": 0
  }
}
```

**Error Response (500):**
```json
{
  "success": false,
  "error": "Phase 3 failed: Invalid flag configuration",
  "phase_failed": "phase3"
}
```

## Environment Configuration

Create a `.env` file with the following variables:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Webhook Configuration
WEBHOOK_URL=https://docs.liptonlegal.com/api/render
WEBHOOK_ACCESS_KEY=your-webhook-key-here
WEBHOOK_CONFIG_PATH=webhook_config.json
ENABLE_WEBHOOKS=true

# Security
API_KEY=your-secret-api-key-here
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Debug and Output
SAVE_DEBUG_FILES=false
OUTPUT_DIRECTORY=./debug_outputs
```

### Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server bind address | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `WEBHOOK_URL` | Docmosis webhook endpoint | None |
| `WEBHOOK_ACCESS_KEY` | Webhook authentication key | None |
| `ENABLE_WEBHOOKS` | Send results to webhook | `true` |
| `API_KEY` | API authentication key (optional) | None |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `http://localhost:3000` |
| `SAVE_DEBUG_FILES` | Save intermediate JSON files | `false` |

## Testing the API

### Using cURL

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

Test the normalize endpoint:
```bash
curl -X POST http://localhost:8000/api/normalize \
  -H "Content-Type: application/json" \
  -d @formtest.json
```

With API key:
```bash
curl -X POST http://localhost:8000/api/normalize \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key-here" \
  -d @formtest.json
```

### Using Python

```python
import requests

# Test health
response = requests.get("http://localhost:8000/health")
print(response.json())

# Normalize form data
with open("formtest.json") as f:
    form_data = json.load(f)

response = requests.post(
    "http://localhost:8000/api/normalize",
    json=form_data,
    headers={"X-API-Key": "your-key-here"}  # if API key is configured
)
print(response.json())
```

### Using the Interactive Docs

1. Open http://localhost:8000/docs in your browser
2. Click on the `/api/normalize` endpoint
3. Click "Try it out"
4. Paste your form JSON in the request body
5. Add API key if required
6. Click "Execute"

## Pipeline Phases

The normalization pipeline consists of 5 phases:

1. **Phase 1: Input Normalization**
   - Transforms raw form data into normalized structure
   - Extracts case information
   - Flattens plaintiff discovery data
   - Normalizes defendants

2. **Phase 2: Dataset Builder**
   - Creates Cartesian product of Head of Household plaintiffs × Defendants
   - Generates all necessary plaintiff-defendant combinations

3. **Phase 3: Flag Processors**
   - Applies 25+ flag processors to each dataset
   - Generates 180+ boolean flags based on discovery issues
   - Enriches datasets with computed flags

4. **Phase 4: Document Profiles**
   - Applies three document profiles: SROGs, PODs, Admissions
   - Creates specialized datasets for each document type
   - Multiplies datasets by profile types

5. **Phase 5: Set Splitting**
   - Splits profile datasets into sets
   - Ensures max 120 interrogatories per set
   - Generates filenames for document generation
   - Optionally sends to Docmosis webhook

## Production Deployment

### Docker

Build the Docker image:
```bash
docker build -t normalization-api .
```

Run the container:
```bash
docker run -p 8000:8000 \
  -e WEBHOOK_URL=https://docs.liptonlegal.com/api/render \
  -e WEBHOOK_ACCESS_KEY=your-key \
  -e API_KEY=your-api-key \
  normalization-api
```

### Google Cloud Run

Deploy to Cloud Run:
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/normalization-api

# Deploy
gcloud run deploy normalization-api \
  --image gcr.io/PROJECT_ID/normalization-api \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --max-instances 10 \
  --set-env-vars WEBHOOK_URL=$WEBHOOK_URL \
  --set-secrets WEBHOOK_ACCESS_KEY=webhook-key:latest,API_KEY=api-key:latest
```

## Performance

Typical performance metrics:

- **Phase 1**: ~200-500ms
- **Phase 2**: ~100-300ms
- **Phase 3**: ~1-2s (depends on dataset size)
- **Phase 4**: ~500ms-1s
- **Phase 5**: ~500ms-1s
- **Webhook Sending**: ~2-5s (depends on network)

**Total**: ~5-10 seconds for typical form with 2 plaintiffs and 1 defendant

## Error Handling

The API implements comprehensive error handling:

1. **Validation Errors**: Pydantic validates all input data
2. **Phase Failures**: Each phase failure is caught and reported
3. **Webhook Failures**: Pipeline completes even if webhooks fail
4. **Timeout Handling**: Configurable timeouts for webhook calls
5. **Graceful Degradation**: Partial results returned when possible

## Security

### API Key Authentication

When `API_KEY` is configured, all requests to `/api/normalize` require the `X-API-Key` header.

### CORS Configuration

Configure allowed origins using the `ALLOWED_ORIGINS` environment variable.

### Secrets Management

For production:
- Use Google Secret Manager for sensitive values
- Never commit `.env` files to version control
- Rotate API keys regularly

## Logging

The API uses Python's standard logging module with structured logs:

```
2025-10-17 12:34:56 - api.routes - INFO - Starting pipeline for form: 1
2025-10-17 12:34:56 - api.routes - INFO - Phase 1 complete: {'plaintiffs': 2, 'defendants': 1}
2025-10-17 12:34:57 - api.routes - INFO - Phase 2 complete: {'datasets': 2}
...
2025-10-17 12:35:02 - api.routes - INFO - Pipeline complete in 5420ms
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -ti :8000

# Kill the process
lsof -ti :8000 | xargs kill -9
```

### Module Import Errors

Ensure you're in the correct directory:
```bash
cd "normalization work"
python -m uvicorn api.main:app
```

### Webhook Failures

Check webhook configuration:
- Verify `WEBHOOK_URL` is correct
- Verify `WEBHOOK_ACCESS_KEY` is valid
- Check network connectivity to webhook endpoint

## Development

### Code Structure

```
normalization work/
├── api/
│   ├── __init__.py       # Package initialization
│   ├── main.py           # FastAPI app and config
│   ├── routes.py         # API endpoints
│   └── README.md         # This file
├── src/                  # Pipeline phases
│   ├── phase1/
│   ├── phase2/
│   ├── phase3/
│   ├── phase4/
│   └── phase5/
├── run_pipeline.py       # Standalone pipeline runner
├── requirements.txt      # Python dependencies
└── .env                  # Environment configuration
```

### Adding New Endpoints

1. Add route function to `api/routes.py`
2. Use appropriate HTTP method decorator
3. Add Pydantic models for request/response validation
4. Update this README with endpoint documentation

### Running Tests

```bash
pytest tests/api/
```

## License

Internal use only - Lipton Legal

## Support

For issues or questions, contact the development team.
