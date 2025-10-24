<!-- 2e4a6725-399b-4232-aad5-4f688eef45bf 4e42d45c-17c0-4d9f-89f7-f8032cf47291 -->
# Implement Access Token Authentication for GCP Deployment

## Goal

Secure the webserver with URL-based token authentication so it can only be accessed with a secret token in the query string (`?token=xxx`) or Authorization header.

## Implementation Steps

### 1. Update Environment Configuration

**File**: `.env` (already exists in project root)

Add access control section to existing .env file:

```env
# ==========================================
# Access Control & Security
# ==========================================
ACCESS_TOKEN=your-secret-token-here-change-this
# NODE_ENV already configured (currently: development)
# Set to production when deploying to GCP
```

**Note**: The file already has `NODE_ENV=development` configured. When deploying to GCP, this will be set to `production` via GCP environment variables.

### 2. Add Authentication Middleware

**File**: `server.js`

**Location**: After line 75 (after `const PORT = process.env.PORT || 3000;`)

Add three components:

- Access token configuration from environment
- `requireAuth()` middleware function that:
- Skips auth in development mode
- Allows health checks/metrics (for GCP monitoring)
- Checks for token in `req.query.token` OR `Authorization` header
- Returns 401 if unauthorized
- Logs access attempts

### 3. Apply Middleware to Routes

**File**: `server.js`

**Location**: Line 281 (after `app.use(express.static(__dirname));`)

Add `app.use(requireAuth);` to protect all routes except health checks.

### 4. Update .gitignore Protection

**File**: `.gitignore`

Verify `.env` is already excluded (it is, confirmed in Phase 1).

### 5. Test Authentication

- Test without token → expect 401
- Test with correct token in URL → expect access
- Test with correct token in header → expect access  
- Test health checks work without token → expect 200

### 6. Prepare GCP Deployment

Document deployment commands for:

- **Cloud Run**: `gcloud run deploy` with `--set-env-vars`
- **App Engine**: Update `app.yaml` with env_variables
- **Compute Engine**: Set via instance metadata

## Key Files

- `.env` (new)
- `server.js` (modify)
- `docs/setup/GCP_DEPLOYMENT.md` (new, optional)

## Security Notes

- Token should be cryptographically random (min 32 chars)
- Never commit `.env` to git
- Use HTTPS in production (GCP provides this)
- Health endpoints bypass auth for GCP monitoring

### To-dos

- [ ] Create .env file with ACCESS_TOKEN and NODE_ENV configuration
- [ ] Add authentication middleware code to server.js after PORT configuration
- [ ] Apply requireAuth middleware to protect all routes in server.js
- [ ] Test authentication with/without token and verify health checks work
- [ ] Create GCP deployment documentation with environment variable setup