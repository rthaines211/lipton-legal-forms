# Railway Deployment Fix - Summary

## Issue Resolved
**Problem:** Database insertion was failing with error:
```
column "submitter_name" of relation "cases" does not exist
```

## Root Cause
The Node.js server code ([server.js:1256-1259](server.js#L1256-L1259)) was trying to insert data into columns `submitter_name` and `submitter_email` that don't exist in the Railway PostgreSQL database schema.

**Why this happened:**
- The local development schema may have had these columns at some point
- When the Railway database was initialized using [database/schema.sql](database/schema.sql), these columns were not included
- The submitter information is actually stored in the `raw_payload` JSONB column, so separate columns were redundant

## What Was Fixed

### File: `server.js`

#### Before (Lines 1256-1276):
```javascript
const caseResult = await client.query(
    `INSERT INTO cases (
        property_address, city, state, zip_code, county, filing_location,
        internal_name, form_name, raw_payload, is_active, submitter_name, submitter_email
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
    RETURNING id`,
    [
        structuredData.Full_Address?.StreetAddress || structuredData.Full_Address?.Line1,
        structuredData.Full_Address?.City,
        structuredData.Full_Address?.State?.substring(0, 2)?.toUpperCase() || 'NC',
        structuredData.Full_Address?.PostalCode,
        structuredData.FilingCounty || structuredData['Filing county'],
        structuredData.FilingCity || structuredData['Filing city'],
        structuredData.Form?.InternalName,
        structuredData.Form?.Name,
        JSON.stringify(rawPayload),
        true,
        rawPayload.notificationName || 'Anonymous',  // ❌ Column doesn't exist
        rawPayload.notificationEmail || ''            // ❌ Column doesn't exist
    ]
);
```

#### After (Lines 1251-1274):
```javascript
const caseResult = await client.query(
    `INSERT INTO cases (
        property_address, city, state, zip_code, county, filing_location,
        internal_name, form_name, raw_payload, is_active
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    RETURNING id`,
    [
        structuredData.Full_Address?.StreetAddress || structuredData.Full_Address?.Line1,
        structuredData.Full_Address?.City,
        structuredData.Full_Address?.State?.substring(0, 2)?.toUpperCase() || 'NC',
        structuredData.Full_Address?.PostalCode,
        structuredData.FilingCounty || structuredData['Filing county'],
        structuredData.FilingCity || structuredData['Filing city'],
        structuredData.Form?.InternalName,
        structuredData.Form?.Name,
        JSON.stringify(rawPayload),
        true
        // Note: Submitter information (notificationName, notificationEmail) is stored in raw_payload JSON
    ]
);
```

**Changes Made:**
1. ✅ Removed `submitter_name` and `submitter_email` from column list
2. ✅ Removed corresponding values from parameters array
3. ✅ Updated comments to reflect actual schema
4. ✅ Changed placeholders from `$12` to `$10`

## Deployment Status

### What Was Working (Before Fix)
- ✅ Database connection successful
- ✅ Node.js backend running on port 3000
- ✅ Python pipeline service running on port 8000
- ✅ Both services can communicate
- ✅ Form submissions received and processed
- ✅ JSON files saved locally
- ✅ Python ETL pipeline successfully creates cases in database

### What Was Broken (Before Fix)
- ❌ Node.js backend could not save cases to database
- ❌ Database error on every form submission
- ❌ Users saw "Database save failed" warnings

### What Should Work Now (After Fix)
- ✅ Node.js backend can save cases to database
- ✅ No more schema mismatch errors
- ✅ Complete end-to-end form submission workflow
- ✅ Data saved in both JSON files and PostgreSQL

## How to Verify the Fix

### 1. Check Railway Deployment
1. Go to Railway Dashboard → **lipton-backend** service
2. Watch the **Deployments** tab
3. Wait for new deployment to complete (should auto-trigger from git push)
4. Check logs for: `✅ Database connected successfully`

### 2. Test Form Submission
1. Go to your Railway app URL (from Domains tab)
2. Submit a test form
3. Check logs for:
   - **Old error (should NOT see):** `column "submitter_name" of relation "cases" does not exist`
   - **New success (should see):** `📊 Created case with ID: <uuid>`

### 3. Verify Database Records
Using Railway CLI or database client:
```sql
-- Check that cases are being created
SELECT id, property_address, city, state, created_at
FROM cases
ORDER BY created_at DESC
LIMIT 5;

-- Verify submitter info is in raw_payload
SELECT
    id,
    raw_payload->>'notificationName' as submitter_name,
    raw_payload->>'notificationEmail' as submitter_email
FROM cases
ORDER BY created_at DESC
LIMIT 5;
```

## Additional Issues Found (Not Critical)

### Python Pipeline Warnings
The Python service logs show many warnings like:
```
WARNING - Issue option not found: vermin -> Skunks
WARNING - Issue option not found: insects -> Bedbugs
```

**Cause:** The `issue_options` table in the database needs to be populated with all the available issue options from your form.

**Impact:**
- Not critical - form submissions still work
- Only affects issue selection tracking
- Cases are created, but issue details are not fully saved

**Fix (Optional):**
Create a script to populate the `issue_options` table with all possible values from your form, or accept that only a subset of issues will be tracked.

## Database Schema Reference

### Current `cases` Table Columns:
```sql
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    internal_name VARCHAR(255),
    form_name VARCHAR(255),
    property_address TEXT NOT NULL,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(2) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    county VARCHAR(255),
    filing_location VARCHAR(255),
    raw_payload JSONB NOT NULL,        -- Contains ALL form data including submitter info
    latest_payload JSONB,
    is_active BOOLEAN DEFAULT true
);
```

**Note:** Submitter information is accessible via:
- `raw_payload->>'notificationName'`
- `raw_payload->>'notificationEmail'`
- `raw_payload->>'notificationEmailOptIn'`

## Next Steps

1. **Monitor Railway deployment** - Should complete in ~1 minute
2. **Test form submission** - Verify no database errors
3. **Check application logs** - Look for successful case creation
4. **(Optional) Populate issue_options table** - To eliminate warnings

## Files Modified
- [server.js](server.js) - Fixed database INSERT statement

## Related Documentation
- [RAILWAY_TROUBLESHOOTING.md](RAILWAY_TROUBLESHOOTING.md) - General Railway troubleshooting guide
- [database/schema.sql](database/schema.sql) - Complete database schema
- [railway.backend.toml](railway.backend.toml) - Backend service configuration

---

**Last Updated:** 2025-10-24
**Status:** ✅ Fix deployed and pushed to production
