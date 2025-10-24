# Dropbox Integration Setup Guide

This guide explains how to configure and use the Dropbox integration for automatic document uploads.

## Overview

The application automatically uploads generated documents to Dropbox while preserving the local folder structure. This enables cloud storage and backup of all form submissions without relying on local disk storage.

## Features

- ✅ **Automatic Upload**: Form submissions automatically upload to Dropbox
- ✅ **Folder Preservation**: Maintains local folder structure in Dropbox
- ✅ **Configurable Base Path**: Set custom Dropbox folder location
- ✅ **Non-Blocking**: Uploads happen asynchronously without delaying responses
- ✅ **Error Resilient**: Application continues if Dropbox upload fails
- ✅ **Comprehensive Logging**: Tracks both local and Dropbox paths
- ✅ **Cloud-Ready**: Stateless design for deployment environments

---

## Setup Instructions

### Step 1: Create a Dropbox App

1. Go to [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. Click **"Create app"**
3. Choose:
   - **API**: Scoped access
   - **Type of access**: App folder OR Full Dropbox (recommended: App folder for security)
   - **Name**: Give your app a unique name (e.g., "LegalFormApp")
4. Click **"Create app"**

### Step 2: Configure App Permissions

1. In your app's settings, go to the **"Permissions"** tab
2. Enable the following permissions:
   - ✅ `files.metadata.write` - Create and modify file/folder metadata
   - ✅ `files.content.write` - Upload, download, and modify files
   - ✅ `files.content.read` - View content of files
3. Click **"Submit"** to save permissions

### Step 3: Generate Access Token

1. Go to the **"Settings"** tab in your app
2. Scroll down to **"OAuth 2"** section
3. Under **"Generated access token"**, click **"Generate"**
4. Copy the generated token (it will look like: `sl.xxxxxxxxxxxxxxxxxxxxx`)
5. **⚠️ IMPORTANT**: Store this token securely - it provides access to your Dropbox!

### Step 4: Configure Environment Variables

1. Open your `.env` file (create it if it doesn't exist)
2. Add the following configuration:

```env
# Dropbox Configuration
DROPBOX_ACCESS_TOKEN=sl.your_token_here
DROPBOX_ENABLED=true
DROPBOX_BASE_PATH=/Apps/LegalFormApp
LOCAL_OUTPUT_PATH=/output
CONTINUE_ON_DROPBOX_FAILURE=true
```

**Configuration Options:**

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DROPBOX_ACCESS_TOKEN` | Your Dropbox app access token | (none) | Yes |
| `DROPBOX_ENABLED` | Enable/disable Dropbox uploads | `false` | Yes |
| `DROPBOX_BASE_PATH` | Base folder path in Dropbox | `/Apps/LegalFormApp` | No |
| `LOCAL_OUTPUT_PATH` | Local output directory to mirror | `/output` | No |
| `CONTINUE_ON_DROPBOX_FAILURE` | Continue if upload fails | `true` | No |

### Step 5: Test the Integration

Run the test script to verify everything is configured correctly:

```bash
node test-dropbox-upload.js
```

**Expected output:**
```
✅ Connected to Dropbox account: Your Name
✅ Upload successful!
✅ Uploaded 3/3 files successfully
```

If you see errors, check:
- Access token is correct and not expired
- Permissions are properly configured
- `DROPBOX_ENABLED=true` is set in `.env`

---

## How It Works

### Path Mapping

The service automatically maps local file paths to Dropbox paths:

```
Local:   /output/Clients/SmithCase/SROGs/Set1.pdf
         ↓
Dropbox: /Apps/LegalFormApp/Clients/SmithCase/SROGs/Set1.pdf
```

**Path Transformation Logic:**
1. Remove local output path prefix (`/output`)
2. Combine with Dropbox base path (`/Apps/LegalFormApp`)
3. Preserve all sub-folder structure

### Automatic Folder Creation

The service automatically creates any missing folders in Dropbox before uploading files:

```
/Apps/LegalFormApp/              (created if needed)
  └── Clients/                   (created if needed)
      └── SmithCase/             (created if needed)
          └── SROGs/             (created if needed)
              └── Set1.pdf       (uploaded)
```

### File Overwriting

Files are uploaded with `overwrite` mode, meaning:
- ✅ If a file already exists, it will be replaced
- ✅ Previous versions are preserved in Dropbox version history
- ✅ No duplicate files or naming conflicts

---

## Integration Points

### 1. Form Submission Upload

When users submit forms, the JSON entry is automatically uploaded to Dropbox:

**Location in code:** `server.js:1378-1392`

```javascript
// Upload to Dropbox (non-blocking)
if (dropboxService.isEnabled()) {
    dropboxService.uploadFile(filepath)
        .then(result => {
            if (result.success) {
                console.log(`✅ Dropbox upload successful: ${result.dropboxPath}`);
            }
        })
        .catch(error => {
            console.error(`❌ Dropbox upload error: ${error.message}`);
        });
}
```

### 2. Manual Upload

You can manually upload files using the service:

```javascript
const dropboxService = require('./dropbox-service');

// Upload a single file
const result = await dropboxService.uploadFile('/path/to/file.json');

// Upload multiple files
const results = await dropboxService.uploadFiles([
    '/path/to/file1.json',
    '/path/to/file2.json'
]);
```

---

## Logging

The integration provides comprehensive logging:

```
☁️  Uploading to Dropbox: /output/Clients/Case1/file.json
📁 Created Dropbox folder: /Apps/LegalFormApp/Clients/Case1
✅ Uploaded to Dropbox: /output/Clients/Case1/file.json → /Apps/LegalFormApp/Clients/Case1/file.json
✅ Dropbox upload successful: /Apps/LegalFormApp/Clients/Case1/file.json
```

**Log Indicators:**
- `☁️` - Upload initiated
- `📁` - Folder created
- `✅` - Success
- `⚠️` - Warning (non-critical)
- `❌` - Error

---

## Troubleshooting

### Problem: "Dropbox is disabled"
**Solution:** Set `DROPBOX_ENABLED=true` in your `.env` file

### Problem: "Dropbox client not initialized"
**Solution:**
1. Check that `DROPBOX_ACCESS_TOKEN` is set in `.env`
2. Verify the token is valid (not expired)
3. Restart the server after changing `.env`

### Problem: "Failed to create Dropbox folder"
**Solution:**
1. Check app permissions include `files.metadata.write`
2. Verify base path doesn't have special characters
3. Check Dropbox account has available storage

### Problem: "Failed to upload file"
**Solution:**
1. Check file exists locally before upload
2. Verify file size is under Dropbox limits (350 GB)
3. Check network connectivity
4. Review Dropbox app permissions

### Problem: "Invalid access token"
**Solution:**
1. Regenerate access token in Dropbox App Console
2. Update `DROPBOX_ACCESS_TOKEN` in `.env`
3. If using OAuth, refresh tokens periodically

---

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use app folder access** instead of full Dropbox access when possible
3. **Rotate access tokens** periodically for enhanced security
4. **Limit token scope** to only required permissions
5. **Use environment variables** for production deployments
6. **Monitor uploads** through Dropbox activity logs

---

## Production Deployment

### Environment Variables

Ensure these environment variables are set in your production environment:

```bash
export DROPBOX_ACCESS_TOKEN="your_production_token"
export DROPBOX_ENABLED="true"
export DROPBOX_BASE_PATH="/Apps/LegalFormApp"
export LOCAL_OUTPUT_PATH="/output"
export CONTINUE_ON_DROPBOX_FAILURE="true"
```

### Docker Deployment

If using Docker, add to your `docker-compose.yml`:

```yaml
services:
  app:
    environment:
      - DROPBOX_ACCESS_TOKEN=${DROPBOX_ACCESS_TOKEN}
      - DROPBOX_ENABLED=true
      - DROPBOX_BASE_PATH=/Apps/LegalFormApp
```

### Kubernetes Deployment

Create a secret:

```bash
kubectl create secret generic dropbox-credentials \
  --from-literal=access-token=your_token_here
```

Reference in deployment:

```yaml
env:
  - name: DROPBOX_ACCESS_TOKEN
    valueFrom:
      secretKeyRef:
        name: dropbox-credentials
        key: access-token
  - name: DROPBOX_ENABLED
    value: "true"
```

---

## API Reference

See `dropbox-service.js` for full API documentation.

### Main Functions

#### `uploadFile(localFilePath, fileContent?)`
Uploads a single file to Dropbox.

**Parameters:**
- `localFilePath` (string): Absolute local file path
- `fileContent` (Buffer|string, optional): File content (reads from disk if not provided)

**Returns:** Promise<{ success, localPath, dropboxPath, error }>

#### `uploadFiles(localFilePaths)`
Uploads multiple files to Dropbox in parallel.

**Parameters:**
- `localFilePaths` (string[]): Array of absolute local file paths

**Returns:** Promise<Array<{ success, localPath, dropboxPath, error }>>

#### `mapLocalPathToDropbox(localPath)`
Maps a local path to its corresponding Dropbox path.

**Parameters:**
- `localPath` (string): Local file path

**Returns:** string (Dropbox path)

#### `isEnabled()`
Checks if Dropbox integration is enabled and configured.

**Returns:** boolean

---

## Python Pipeline Integration

The Dropbox integration is also available in the Python normalization pipeline for uploading generated legal documents.

### Python Configuration

Add to `/normalization work/.env`:

```env
DROPBOX_ACCESS_TOKEN=your-dropbox-access-token-here
DROPBOX_ENABLED=true
DROPBOX_BASE_PATH=/Current Clients
DROPBOX_LOCAL_OUTPUT_PATH=webhook_documents
DROPBOX_CONTINUE_ON_FAILURE=true
```

### How It Works

When the Python pipeline generates documents (SROGs, PODs, Admissions):

1. **Document Generated** - Webhook returns rendered document
2. **Saved Locally** - Saved to `webhook_documents/Address/HoH/Discovery/Type/doc.docx`
3. **Uploaded to Dropbox** - Automatically uploaded preserving structure
4. **Dropbox Path** - `/Current Clients/Address/HoH/Discovery/Type/doc.docx`

**Example Folder Structure:**

```
Dropbox: /Current Clients/
  ├── 123 Main St/
  │   ├── John Doe/
  │   │   └── Discovery Propounded/
  │   │       ├── SROGs/
  │   │       │   └── Set_1_SROGs.docx
  │   │       ├── PODS/
  │   │       │   └── Set_1_PODs.docx
  │   │       └── ADMISSIONS/
  │   │           └── Set_1_Admissions.docx
  │   └── Jane Smith/
  │       └── Discovery Propounded/
  │           └── SROGs/
  │               └── Set_1_SROGs.docx
  └── 456 Oak Ave/
      └── ...
```

### Testing Python Integration

```bash
cd "normalization work"
./venv/bin/python -c "
from dotenv import load_dotenv
load_dotenv()
from src.utils import dropbox_service
print(f'Dropbox enabled: {dropbox_service.is_enabled()}')
"
```

### Integration Points

**File:** `normalization work/src/phase5/webhook_sender.py:256-265`

After document is saved locally, Dropbox upload is triggered:

```python
# Upload to Dropbox (non-blocking, errors logged but don't fail the request)
if DROPBOX_AVAILABLE and dropbox_service.is_enabled():
    try:
        dropbox_result = dropbox_service.upload_file(saved_file, response.content)
        if dropbox_result['success']:
            print(f"✅ Dropbox upload successful: {dropbox_result['dropbox_path']}")
    except Exception as dropbox_error:
        print(f"❌ Dropbox upload error: {dropbox_error}")
```

---

## Support

For issues or questions:
1. Check the [Dropbox API documentation](https://www.dropbox.com/developers/documentation)
2. Review server logs for detailed error messages
3. **Node.js**: Run `node test-dropbox-upload.js` to diagnose issues
4. **Python**: Check FastAPI logs when pipeline executes
5. Verify `.env` configuration matches this guide

---

**Last Updated:** 2025-10-20
**Version:** 1.1.0 (Added Python Pipeline Integration)
