# Railway Deployment Troubleshooting Guide

## Current Issue
**lipton-backend** service builds successfully (5 seconds) but fails to deploy or takes 45+ minutes.

## Root Cause Analysis

### Why Build Succeeds But Deploy Fails
- **Build phase**: Compiles code, installs dependencies ✅ (working)
- **Deploy phase**: Runs container, connects to database ❌ (failing)
- **Most likely cause**: Environment variables not properly set or Railway configuration conflict

---

## Immediate Action Items

### 1. Verify Environment Variables in Railway UI

Go to **Railway Dashboard** → **lipton-backend** service → **Variables** tab

**Check that these EXACT variables exist:**

```bash
# Database Connection (CRITICAL - must match exactly)
DB_USER=postgres
DB_HOST=postgres.railway.internal
DB_NAME=railway
DB_PASSWORD=EkstcClojPAPJGcnOuwyuIJEagbsqnKx
DB_PORT=5432

# Application Configuration
NODE_ENV=production
PIPELINE_API_URL=http://lipton-doc-pipeline:8000
PIPELINE_ENABLED=true

# Railway will auto-set these (verify they exist):
PORT=(should be set automatically by Railway)
```

**IMPORTANT NOTES:**
- Do NOT add quotes around variable values in Railway UI
- Railway automatically provides PORT variable - you don't need to set it
- DB_PASSWORD should match the one from lipton-database service

### 2. Check Railway Service Settings

**In lipton-backend service Settings:**

1. **Builder**: Should be "Dockerfile"
2. **Dockerfile Path**: Should be "Dockerfile.node"
3. **Root Directory**: Should be "/" or empty (not set)
4. **Watch Paths**: Should be "/" or empty

**To Change Builder:**
- Go to Settings → Deploy
- Change "Builder" to "Dockerfile"
- Set "Dockerfile Path" to "Dockerfile.node"
- Click Save

### 3. Check Service Deployment Logs

**In Railway Dashboard** → **lipton-backend** → **Deployments** → Click latest deployment

You should see **THREE sections** of logs:

#### A. Build Logs (Should be successful ✅)
```
#1 [internal] load build definition from Dockerfile.node
...
✅ Build completed in 5.23 seconds
```

#### B. Deploy Logs (This is where the problem is ⚠️)
Look for these specific messages:

**If you see:**
```
Error: connect ECONNREFUSED
```
→ **Database variables not set correctly**

**If you see:**
```
✅ Database connected successfully
Server running on port 3000
```
→ **Container is working! Health check might be the issue**

**If you see nothing or logs stop:**
→ **Container is crashing on startup**

#### C. Application Logs
These show actual app output once running.

### 4. Test Health Check Manually

Once deployed, get your Railway service URL:
- Go to **lipton-backend** service → **Settings** → **Domains**
- Your URL will be something like: `https://lipton-backend-production.up.railway.app`

**Test the health endpoint:**
```bash
curl https://your-service-url.railway.app/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-24T...",
  "uptime": 123.456,
  "service": "legal-form-app",
  "version": "1.0.0",
  "environment": "production"
}
```

---

## Common Issues & Solutions

### Issue 1: "Environment variables not taking effect"

**Symptom:** Added variables in Railway but still getting connection errors

**Solution:**
1. Click "Add Variable" button in Railway (don't use RAW editor for DB variables)
2. Add each variable individually:
   - Variable: `DB_USER`
   - Value: `postgres`
3. After adding ALL variables, click "Deploy" or trigger a new deployment
4. Variables only apply to NEW deployments, not existing ones

### Issue 2: "postgres.railway.internal not found"

**Symptom:** `Error: getaddrinfo ENOTFOUND postgres.railway.internal`

**Solution:**
1. Make sure **lipton-database** service is deployed and healthy
2. Check that services are in the SAME Railway project
3. Try using Railway's private network variable:
   ```
   DB_HOST=${{lipton-database.RAILWAY_PRIVATE_DOMAIN}}
   ```

### Issue 3: "Health check timeout"

**Symptom:** Deployment stuck at "Waiting for health check..."

**Solution 1 - Increase Timeout:**
Add to railway.backend.toml:
```toml
[deploy]
healthcheckTimeout = 300
healthcheckPath = "/health"
```

**Solution 2 - Check if app is actually running:**
```bash
# In Railway, go to service → Logs
# Look for: "Server running on port X"
```

**Solution 3 - Test health endpoint:**
Railway might be checking wrong path. Our app responds to:
- `/health`
- `/api/health`

### Issue 4: "Railway using wrong Dockerfile"

**Symptom:** Seeing "pip: command not found" in Node.js service logs

**Solution:**
1. Delete the multi-stage Dockerfile if it exists
2. Use service-specific Dockerfiles:
   - **lipton-backend**: Use `Dockerfile.node`
   - **lipton-doc-pipeline**: Use `Dockerfile.python`
3. Set Dockerfile path in Railway service settings
4. Ensure `railway.backend.toml` exists with correct config

---

## Step-by-Step Deployment Process

### Start Fresh (if nothing works)

1. **Delete the failing deployment:**
   - Railway Dashboard → lipton-backend → Deployments
   - Click three dots on latest deployment → "Delete"

2. **Verify configuration files exist locally:**
   ```bash
   ls -la Dockerfile.node
   ls -la railway.backend.toml
   ```

3. **Commit and push if you made changes:**
   ```bash
   git add .
   git commit -m "Fix Railway backend configuration"
   git push origin main
   ```

4. **In Railway UI, manually trigger deployment:**
   - Go to lipton-backend service
   - Click "Deploy" button (top right)
   - Select "Deploy latest commit"

5. **Watch logs in real-time:**
   - Keep Deployments tab open
   - Monitor Build → Deploy → Application logs
   - Look for specific error messages

---

## Expected Successful Deployment Logs

```
==================== Build Logs ====================
#1 [internal] load build definition from Dockerfile.node
...
✅ Build completed in 5 seconds

==================== Deploy Logs ====================
🚀 Starting container...
✅ Database connected successfully
📡 Pipeline API configured: http://lipton-doc-pipeline:8000
🚀 Server running on port 3000

   📋 Legal Form Submission API
   ===========================
   Available endpoints:
   - POST   /api/form-submission
   - GET    /api/form-entries
   - GET    /health
   ...

==================== Application Logs ====================
[2025-10-24 12:00:00] INFO: Application started
[2025-10-24 12:00:01] INFO: Health check passed
```

---

## Database Connection Verification

### Test from Node.js service container

**Option 1: Use Railway CLI**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Run command in lipton-backend container
railway run --service lipton-backend node -e "
const { Pool } = require('pg');
const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT
});
pool.query('SELECT NOW()', (err, res) => {
  console.log(err ? 'ERROR: ' + err.message : 'SUCCESS: ' + res.rows[0].now);
  process.exit(err ? 1 : 0);
});
"
```

**Option 2: Add debug endpoint**
Add to server.js temporarily:
```javascript
app.get('/debug/db', async (req, res) => {
    try {
        const result = await pool.query('SELECT NOW() as time');
        res.json({
            success: true,
            time: result.rows[0].time,
            config: {
                user: process.env.DB_USER,
                host: process.env.DB_HOST,
                database: process.env.DB_NAME,
                port: process.env.DB_PORT,
                password: process.env.DB_PASSWORD ? '****' : 'NOT SET'
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message,
            config: {
                user: process.env.DB_USER,
                host: process.env.DB_HOST,
                database: process.env.DB_NAME,
                port: process.env.DB_PORT,
                password: process.env.DB_PASSWORD ? '****' : 'NOT SET'
            }
        });
    }
});
```

Then access: `https://your-service.railway.app/debug/db`

---

## What to Share for Further Help

If issues persist, gather these:

1. **Screenshot of Variables tab** (blur password)
2. **Full Deploy Logs** (the section between Build and Application logs)
3. **Service Settings screenshot** showing:
   - Builder type
   - Dockerfile path
   - Root directory
4. **Output of health check test:**
   ```bash
   curl https://your-service.railway.app/health
   ```
5. **Database service status** from Railway dashboard

---

## Contact Support

If you've tried everything:

1. Railway Discord: https://discord.gg/railway
2. Railway Community: https://help.railway.app/
3. Create GitHub issue with deployment logs

---

## Quick Reference: Variable Checker

Copy/paste this checklist and check off each one in Railway UI:

- [ ] DB_USER exists and = `postgres`
- [ ] DB_HOST exists and = `postgres.railway.internal`
- [ ] DB_NAME exists and = `railway`
- [ ] DB_PASSWORD exists and matches database service
- [ ] DB_PORT exists and = `5432`
- [ ] NODE_ENV exists and = `production`
- [ ] PIPELINE_API_URL exists and = `http://lipton-doc-pipeline:8000`
- [ ] PIPELINE_ENABLED exists and = `true`
- [ ] PORT is auto-set by Railway (should see it in list)
- [ ] No variables have quotes around values
- [ ] Variables were added using "Add Variable" button, not RAW editor
- [ ] Deployment was triggered AFTER adding variables
