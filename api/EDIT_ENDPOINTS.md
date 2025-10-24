# Edit Endpoints Documentation

## Overview

The Legal Forms ETL API provides endpoints for editing case data while preserving the original submission. All edits automatically rebuild the `latest_payload` JSONB field to reflect the current state of the data.

## Authentication

Currently, no authentication is required (development mode).

## Endpoints

### 1. Update Party Details

Updates party information (plaintiff or defendant) and automatically rebuilds the latest_payload.

**Endpoint:** `PATCH /api/parties/{party_id}`

**URL Parameters:**
- `party_id` (UUID, required) - The unique identifier of the party to update

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "full_name": "Jane Smith",
  "unit_number": "2A",
  "is_head_of_household": true
}
```

All fields are optional. Only include fields you want to update.

**Auto-Update Behavior:**
- If you update `first_name` or `last_name`, the `full_name` field is automatically updated to match (unless you explicitly provide a different `full_name`)

**Head of Household Constraint:**
- Only one party per unit can be marked as Head of Household
- If you attempt to set `is_head_of_household: true` for a unit that already has an HoH, you'll receive a 409 Conflict error

**Response (200 OK):**
```json
{
  "party_id": "e59b3254-bc6c-4111-a9bd-fe3252f95aa5",
  "case_id": "ee8d7009-cba4-4097-8a00-5d0f955f4b1b",
  "updated_fields": ["first_name", "last_name", "full_name"],
  "latest_payload_updated": true,
  "message": "Party updated successfully"
}
```

**Error Responses:**

404 Not Found - Party does not exist:
```json
{
  "detail": "Party {party_id} not found"
}
```

409 Conflict - HoH constraint violation:
```json
{
  "detail": "Unit 2A already has a Head of Household: Jane Smith. Only one Head of Household per unit is allowed."
}
```

**Example:**
```bash
curl -X PATCH http://localhost:8000/api/parties/e59b3254-bc6c-4111-a9bd-fe3252f95aa5 \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Jane", "last_name": "Smith"}'
```

---

### 2. Add Issue to Party

Adds a discovery issue to a plaintiff and rebuilds the latest_payload.

**Endpoint:** `POST /api/parties/{party_id}/issues/{option_id}`

**URL Parameters:**
- `party_id` (UUID, required) - The plaintiff's unique identifier
- `option_id` (UUID, required) - The issue option's unique identifier from the `issue_options` table

**Request Body:** None

**Response (200 OK):**
```json
{
  "party_id": "e59b3254-bc6c-4111-a9bd-fe3252f95aa5",
  "case_id": "ee8d7009-cba4-4097-8a00-5d0f955f4b1b",
  "issue_option_id": "85532f39-20a4-4905-b2de-62a55beb7e23",
  "category_name": "Windows",
  "option_name": "Broken",
  "latest_payload_updated": true,
  "message": "Issue added successfully"
}
```

If the issue already exists:
```json
{
  "party_id": "e59b3254-bc6c-4111-a9bd-fe3252f95aa5",
  "case_id": "ee8d7009-cba4-4097-8a00-5d0f955f4b1b",
  "issue_option_id": "9e2ca214-34f3-4844-ac44-443880e19d5f",
  "category_name": "Insects",
  "option_name": "Ants",
  "latest_payload_updated": true,
  "message": "Issue already exists (no change)"
}
```

**Error Responses:**

404 Not Found - Party does not exist:
```json
{
  "detail": "Party {party_id} not found"
}
```

404 Not Found - Issue option does not exist:
```json
{
  "detail": "Issue option {option_id} not found"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/parties/e59b3254-bc6c-4111-a9bd-fe3252f95aa5/issues/85532f39-20a4-4905-b2de-62a55beb7e23
```

---

### 3. Remove Issue from Party

Removes a discovery issue from a plaintiff and rebuilds the latest_payload.

**Endpoint:** `DELETE /api/parties/{party_id}/issues/{option_id}`

**URL Parameters:**
- `party_id` (UUID, required) - The plaintiff's unique identifier
- `option_id` (UUID, required) - The issue option's unique identifier

**Request Body:** None

**Response (200 OK):**
```json
{
  "party_id": "e59b3254-bc6c-4111-a9bd-fe3252f95aa5",
  "case_id": "ee8d7009-cba4-4097-8a00-5d0f955f4b1b",
  "issue_option_id": "9e2ca214-34f3-4844-ac44-443880e19d5f",
  "latest_payload_updated": true,
  "message": "Issue removed successfully"
}
```

If the issue doesn't exist (idempotent - no error):
```json
{
  "party_id": "e59b3254-bc6c-4111-a9bd-fe3252f95aa5",
  "case_id": "ee8d7009-cba4-4097-8a00-5d0f955f4b1b",
  "issue_option_id": "9e2ca214-34f3-4844-ac44-443880e19d5f",
  "latest_payload_updated": true,
  "message": "Issue removed successfully"
}
```

**Error Responses:**

404 Not Found - Party does not exist:
```json
{
  "detail": "Party {party_id} not found"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/parties/e59b3254-bc6c-4111-a9bd-fe3252f95aa5/issues/9e2ca214-34f3-4844-ac44-443880e19d5f
```

---

## Data Consistency Guarantees

1. **Atomic Transactions:** All edits are performed within a database transaction. If any part fails, the entire transaction is rolled back.

2. **Automatic Payload Rebuild:** Every successful edit triggers `build_json_from_db()` which reconstructs the `latest_payload` from the current normalized database records.

3. **Original Snapshot Preserved:** The `raw_payload` field always contains the original form submission and is never modified.

4. **Auto-Update Logic:** When updating `first_name` or `last_name`, `full_name` is automatically computed and updated.

---

## Getting Issue Option IDs

To find available issue options for adding to a party:

**Get Taxonomy:**
```bash
curl http://localhost:8000/api/taxonomy
```

This returns all categories and their options with IDs:
```json
{
  "categories": [
    {
      "id": "uuid-here",
      "category_name": "Windows",
      "options": [
        {
          "id": "85532f39-20a4-4905-b2de-62a55beb7e23",
          "option_name": "Broken"
        },
        {
          "id": "fc97b612-2940-453f-b7da-04225c506115",
          "option_name": "Screens"
        }
      ]
    }
  ]
}
```

---

## Testing the Endpoints

### Test Scenario 1: Update Party Name
```bash
# Update first and last name (full_name auto-updates)
curl -X PATCH http://localhost:8000/api/parties/{party_id} \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Jane", "last_name": "Doe"}'
```

### Test Scenario 2: Add Multiple Issues
```bash
# Add Broken Windows
curl -X POST http://localhost:8000/api/parties/{party_id}/issues/85532f39-20a4-4905-b2de-62a55beb7e23

# Add Ants
curl -X POST http://localhost:8000/api/parties/{party_id}/issues/9e2ca214-34f3-4844-ac44-443880e19d5f
```

### Test Scenario 3: HoH Constraint
```bash
# Set party 1 as HoH for unit 2A
curl -X PATCH http://localhost:8000/api/parties/{party1_id} \
  -H "Content-Type: application/json" \
  -d '{"unit_number": "2A", "is_head_of_household": true}'

# Try to set party 2 as HoH for same unit (should fail with 409)
curl -X PATCH http://localhost:8000/api/parties/{party2_id} \
  -H "Content-Type: application/json" \
  -d '{"unit_number": "2A", "is_head_of_household": true}'
```

### Test Scenario 4: Remove Issue
```bash
# Remove Ants issue
curl -X DELETE http://localhost:8000/api/parties/{party_id}/issues/9e2ca214-34f3-4844-ac44-443880e19d5f
```

---

## Implementation Details

### JSON Rebuilding

The `JSONBuilderService` (in `api/json_builder.py`) reconstructs the form JSON from normalized database records:

1. Fetches case details from `cases` table
2. Fetches all parties (plaintiffs and defendants) from `parties` table
3. For each plaintiff, fetches their issue selections from `party_issue_selections` table
4. Groups issues by category (multi-select arrays for Vermin, Insects, etc.)
5. Formats the output to match the original form structure

### Full Name Auto-Update

When updating `first_name` or `last_name`:
1. The endpoint fetches the current name values
2. Constructs `full_name = f"{first} {last}".strip()`
3. Adds `full_name` to the UPDATE statement
4. Includes it in the `updated_fields` response

### HoH Constraint Check

Before setting `is_head_of_household = true`:
1. Determine the target unit_number (from request or current value)
2. Query for existing HoH in that unit: `WHERE case_id = ? AND unit_number = ? AND is_head_of_household = true AND id != ?`
3. If found, raise HTTP 409 with descriptive error message
4. Otherwise, proceed with the update

---

## Future Enhancements

Potential improvements for production:

1. **Authentication & Authorization:** Add JWT or API key authentication
2. **Audit Trail:** Log all edits with timestamps and user IDs
3. **Validation Rules:** Add more business logic validation (e.g., date ranges, required fields)
4. **Bulk Operations:** Support updating multiple parties or issues in one request
5. **Partial Failures:** For bulk operations, return which succeeded/failed
6. **Webhooks:** Notify external systems when edits occur
7. **Version History:** Track all versions of latest_payload, not just raw and latest

---

**Last Updated:** 2025-10-08
