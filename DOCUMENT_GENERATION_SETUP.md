# Document Generation Setup Guide

## Overview

The Python pipeline now includes **AUTOMATIC document generation workflow**:

1. **Form Submission** → Database ETL (existing)
2. **🆕 AUTOMATIC Document Generation** → Docmosis API at `docs.liptonlegal.com/api/render`
3. **🆕 AUTOMATIC Dropbox Upload** → Automatic backup to Dropbox

**NEW**: Documents are generated and uploaded **automatically** after every form submission - no manual triggering required!

---

## What Was Added

### New Python Modules

1. **[api/docmosis_client.py](api/docmosis_client.py)** - Docmosis API client
   - Calls `https://docs.liptonlegal.com/api/render`
   - Generates PDF documents from templates
   - Handles retries and timeouts

2. **[api/dropbox_client.py](api/dropbox_client.py)** - Dropbox upload client
   - Uploads generated PDFs to Dropbox
   - Organizes by case: `/Cases/{case_id}/document.pdf`
   - Supports batch uploads

3. **[api/document_service.py](api/document_service.py)** - Document generation orchestrator
   - Fetches case data from database
   - Generates documents via Docmosis
   - Uploads to Dropbox
   - Tracks progress and errors

### New API Endpoints

**Generate All Documents for a Case:**
```http
POST /api/cases/{case_id}/generate-documents
Content-Type: application/json

{
  "templates": ["ComplaintForm.docx", "DiscoveryRequest.docx"],  // optional
  "upload_to_dropbox": true  // optional, default: true
}
```

**Generate Single Document:**
```http
POST /api/cases/{case_id}/generate-document/ComplaintForm.docx?upload_to_dropbox=true
```

---

## Railway Environment Variables

### Required for Document Generation

Add these to **lipton-doc-pipeline** service in Railway:

```bash
# Docmosis Configuration (Required)
DOCMOSIS_API_URL=https://docs.liptonlegal.com/api/render

# Docmosis Configuration (Optional - only if your server requires it)
DOCMOSIS_ACCESS_KEY=<your-docmosis-access-key>
DOCMOSIS_TIMEOUT=60
DOCMOSIS_RETRY_ATTEMPTS=3

# Dropbox Configuration (Optional but recommended)
DROPBOX_ENABLED=true
DROPBOX_ACCESS_TOKEN=<your-dropbox-access-token>
DROPBOX_BASE_PATH=/Apps/LegalFormApp

# Python Environment
PYTHON_ENV=production
```

### How to Add in Railway

1. **Go to Railway Dashboard** → **lipton-doc-pipeline** service
2. **Click "Variables" tab**
3. **Click "+ New Variable"** for each variable above
4. **Enter Name and Value** (no quotes)
5. **Click "Add"**
6. **Deploy** to apply changes

---

## Document Generation Workflow

### Automatic Flow (After Form Submission) ✅

**Documents are now generated AUTOMATICALLY** after every form submission:

```mermaid
User submits form
   ↓
Node.js receives form
   ↓
Node.js calls Python /api/form-submissions
   ↓
Python saves to PostgreSQL ✅
   ↓
🆕 Python AUTOMATICALLY calls Docmosis API
   ↓
Docmosis generates PDFs
   ↓
Python uploads to Dropbox (if enabled)
   ↓
Documents saved! ✅
```

**No manual triggering required!** The `/api/form-submissions` endpoint now automatically:
1. Saves form data to database
2. Generates documents via Docmosis
3. Uploads to Dropbox (if configured)
4. Returns success to user

### Manual Trigger (Using API)

After a form is submitted and case is created:

```bash
# Get the case_id from form submission response
CASE_ID="<uuid-from-response>"

# Trigger document generation
curl -X POST "https://lipton-doc-pipeline.railway.app/api/cases/$CASE_ID/generate-documents" \
  -H "Content-Type: application/json" \
  -d '{
    "upload_to_dropbox": true
  }'
```

---

## Docmosis API Requirements

### Expected Request Format

The Docmosis client sends requests like this:

```json
{
  "templateName": "ComplaintForm.docx",
  "outputName": "case-123_ComplaintForm.pdf",
  "outputFormat": "pdf",
  "data": {
    // Complete case data from database
    "PlaintiffDetails": [...],
    "DefendantDetails2": [...],
    "Full_Address": {...},
    // ... all form fields
  },
  "accessKey": "<your-access-key>"
}
```

### Expected Response

**Success (200 OK):**
```
Content-Type: application/pdf
Body: <PDF binary data>
```

**Error (4xx/5xx):**
```json
{
  "error": "Error message from Docmosis"
}
```

---

## Dropbox Integration

### Folder Structure

Generated documents are organized in Dropbox:

```
/Apps/LegalFormApp/
├── Cases/
│   ├── {case-id-1}/
│   │   ├── case-id-1_ComplaintForm.pdf
│   │   ├── case-id-1_DiscoveryRequest.pdf
│   │   └── case-id-1_SummonsForm.pdf
│   └── {case-id-2}/
│       └── case-id-2_ComplaintForm.pdf
```

### Dropbox Access Token

To get a Dropbox access token:

1. Go to https://www.dropbox.com/developers/apps
2. Create an app or use existing app
3. Generate access token
4. Add to Railway as `DROPBOX_ACCESS_TOKEN`

---

## Testing Document Generation

### 1. Submit a Test Form

```bash
# Submit form to create a case
curl -X POST "https://lipton-backend.railway.app/api/form-entries" \
  -H "Content-Type: application/json" \
  -d @test-form.json
```

Response will include `dbCaseId`.

### 2. Trigger Document Generation

```bash
# Use the case_id from step 1
curl -X POST "https://lipton-doc-pipeline.railway.app/api/cases/{case_id}/generate-documents"
```

### 3. Check Logs

**Python Service Logs (Railway):**
```
✅ Document generated successfully: case-123_ComplaintForm.pdf (45230 bytes)
✅ Dropbox upload successful: /Apps/LegalFormApp/Cases/case-123/case-123_ComplaintForm.pdf
✅ Document generation complete for case case-123: 3 generated, 3 uploaded
```

### 4. Verify in Dropbox

Check your Dropbox app folder:
```
/Apps/LegalFormApp/Cases/case-123/
```

---

## Troubleshooting

### "Document generation is not configured"

**Problem:** `DOCMOSIS_API_URL` not set

**Solution:**
```bash
# Add to Railway variables
DOCMOSIS_API_URL=https://docs.liptonlegal.com/api/render
```

### "Docmosis API returned 401"

**Problem:** Invalid or missing access key

**Solution:**
- Verify access key is correct
- Check Docmosis account is active
- Ensure `docs.liptonlegal.com` is configured properly

### "Docmosis timeout"

**Problem:** Docmosis taking too long (>60s default)

**Solution:**
```bash
# Increase timeout
DOCMOSIS_TIMEOUT=120
```

### "Dropbox upload failed: 401"

**Problem:** Invalid Dropbox access token

**Solution:**
- Regenerate Dropbox access token
- Update `DROPBOX_ACCESS_TOKEN` in Railway
- Redeploy service

### "Template not found"

**Problem:** Docmosis doesn't have the specified template

**Solution:**
- Upload template to Docmosis server
- Verify template name matches exactly (case-sensitive)
- Default templates: `ComplaintForm.docx`, `DiscoveryRequest.docx`, `SummonsForm.docx`

---

## Default Templates

The system uses these default templates if none are specified:

1. **ComplaintForm.docx** - Main legal complaint
2. **DiscoveryRequest.docx** - Discovery requests
3. **SummonsForm.docx** - Summons document

To use custom templates:

```bash
curl -X POST "/api/cases/{case_id}/generate-documents" \
  -H "Content-Type: application/json" \
  -d '{
    "templates": ["CustomTemplate.docx", "AnotherTemplate.docx"]
  }'
```

---

## Environment Variable Summary

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DOCMOSIS_API_URL` | **YES** | `https://docs.liptonlegal.com/api/render` | Docmosis API endpoint |
| `DOCMOSIS_ACCESS_KEY` | No* | None | Docmosis API access key (*only if server requires authentication) |
| `DOCMOSIS_TIMEOUT` | No | `60` | Request timeout in seconds |
| `DOCMOSIS_RETRY_ATTEMPTS` | No | `3` | Number of retry attempts |
| `DROPBOX_ENABLED` | No | `false` | Enable Dropbox uploads |
| `DROPBOX_ACCESS_TOKEN` | No** | None | Dropbox OAuth token (**required if enabled) |
| `DROPBOX_BASE_PATH` | No | `/Apps/LegalFormApp` | Base folder in Dropbox |

---

## Next Steps

1. ✅ Add environment variables to Railway
2. ✅ Deploy updated Python service
3. ✅ Test document generation with a sample case
4. ✅ Verify documents appear in Dropbox
5. ✅ Update Docmosis templates if needed
6. ✅ Monitor logs for errors

---

## API Documentation

### Generate Documents Endpoint

**URL:** `POST /api/cases/{case_id}/generate-documents`

**Request Body:**
```json
{
  "templates": ["string"],  // optional
  "upload_to_dropbox": true  // optional
}
```

**Response (Success):**
```json
{
  "success": true,
  "case_id": "uuid",
  "documents_generated": 3,
  "documents_uploaded": 3,
  "documents": [
    {
      "success": true,
      "filename": "case-123_ComplaintForm.pdf",
      "size": 45230,
      "template": "ComplaintForm.docx"
    }
  ],
  "dropbox_uploads": [
    {
      "success": true,
      "dropbox_path": "/Apps/LegalFormApp/Cases/case-123/case-123_ComplaintForm.pdf",
      "size": 45230
    }
  ],
  "message": "Generated 3 documents successfully"
}
```

**Response (Error):**
```json
{
  "detail": "Document generation failed: <error message>"
}
```

### Health Check

The health endpoint (`/health`) now includes document generation status:

```bash
curl https://lipton-doc-pipeline.railway.app/health
```

```json
{
  "status": "healthy",
  "database": "connected",
  "docmosis_configured": true,  // NEW
  "dropbox_enabled": true,      // NEW
  "version": "1.0.0"
}
```

---

## Contact & Support

If you encounter issues:

1. Check Railway logs for detailed error messages
2. Verify all environment variables are set correctly
3. Test Docmosis API directly to isolate issues
4. Check Dropbox app permissions

---

**Last Updated:** 2025-10-24
**Status:** ✅ Ready for deployment
