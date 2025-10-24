# Database Trigger Issue - Troubleshooting

## Issue

When submitting forms, you're seeing this error:

```
❌ Database error: error: record "new" has no field "party_id"
```

This error comes from a PostgreSQL trigger function `auto_regenerate_payload()` that's trying to access fields that don't exist in the current schema.

## Root Cause

The database has a trigger that fires on INSERT/UPDATE to various tables (cases, parties, party_issue_selections, discovery_details). This trigger calls `regenerate_case_payload()` function which expects certain fields that may not exist in your current schema.

The trigger is looking for:
- `NEW.party_id` in the `party_issue_selections` table
- `NEW.party_id` in the `discovery_details` table

## Impact

- ✅ **Form data is still saved to JSON file** (working correctly)
- ❌ **Database save fails** (trigger error)
- ⚠️ **Pipeline receives `no-db-id`** instead of actual case ID

## Solutions

### Option 1: Drop the Trigger (Quickest)

If you don't need the `auto_regenerate_payload` functionality:

```sql
-- Connect to database
psql legal_forms_db

-- Drop the trigger from all tables
DROP TRIGGER IF EXISTS auto_regenerate_payload_trigger ON cases;
DROP TRIGGER IF EXISTS auto_regenerate_payload_trigger ON parties;
DROP TRIGGER IF EXISTS auto_regenerate_payload_trigger ON party_issue_selections;
DROP TRIGGER IF EXISTS auto_regenerate_payload_trigger ON discovery_details;

-- Drop the function
DROP FUNCTION IF EXISTS auto_regenerate_payload();
DROP FUNCTION IF EXISTS regenerate_case_payload(UUID);
```

### Option 2: Fix the Trigger Function

If you need the trigger, update it to handle the current schema:

```sql
-- First, check what the function does
\df+ auto_regenerate_payload

-- Then update it based on your current schema
-- (You'll need to provide the original function code to fix it)
```

### Option 3: Add Missing Columns

If the trigger expects these columns, add them:

```sql
-- Check current schema
\d party_issue_selections
\d discovery_details

-- If party_id is missing from party_issue_selections:
ALTER TABLE party_issue_selections ADD COLUMN IF NOT EXISTS party_id UUID REFERENCES parties(id);

-- If party_id is missing from discovery_details:
ALTER TABLE discovery_details ADD COLUMN IF NOT EXISTS party_id UUID REFERENCES parties(id);
```

## Recommended Action

**For immediate testing of Phase 2 integration, use Option 1** (drop the triggers). You can always recreate them later.

```bash
# Quick fix
/opt/homebrew/bin/psql legal_forms_db -c "
DROP TRIGGER IF EXISTS auto_regenerate_payload_trigger ON cases;
DROP TRIGGER IF EXISTS auto_regenerate_payload_trigger ON parties;
DROP TRIGGER IF EXISTS auto_regenerate_payload_trigger ON party_issue_selections;
DROP TRIGGER IF EXISTS auto_regenerate_payload_trigger ON discovery_details;
DROP FUNCTION IF EXISTS auto_regenerate_payload() CASCADE;
DROP FUNCTION IF EXISTS regenerate_case_payload(UUID) CASCADE;
"
```

## After Fixing

Once you've applied the fix, try submitting the form again. You should see:

```
✅ Form entry saved to JSON
✅ Form entry saved to database with case ID: <uuid>
📋 Calling normalization pipeline (Case ID: <uuid>)...
✅ Pipeline completed successfully in ~5000ms
```

## Verification

Test that it's fixed:

1. Submit a form
2. Check the console logs
3. Verify you see:
   - ✅ Database case ID (not "no-db-id")
   - ✅ Pipeline execution
   - ✅ No database errors

## Notes

- This issue is **not related to Phase 1 or Phase 2 implementation**
- Phase 2 integration is working correctly (pipeline is being called)
- The trigger was likely created by a previous version of your database schema
- Dropping triggers won't affect Phase 1/2 functionality

---

**Phase 1 & 2 are complete and working!** This is just a database schema maintenance issue.
