# Legal Form Application - Database Schema Documentation

## Overview

This PostgreSQL schema provides normalized storage for the Lipton Legal AutoPopulationForm application, supporting multiple plaintiffs, defendants, and detailed habitability issue tracking.

## Quick Start

### 1. Initialize the Database

```bash
# Create database
createdb legal_forms

# Run the schema
psql legal_forms < database/schema.sql
```

### 2. Verify Installation

```sql
-- Check that all tables are created
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Should show:
-- cases
-- discovery_details
-- issue_categories
-- issue_options
-- parties
-- party_issue_selections
```

## Schema Architecture

### Core Tables

#### 1. **cases** - Main Case Information
Stores the primary case data including property address and filing information.

**Key Fields:**
- `id` (UUID) - Primary key
- `property_address`, `city`, `state`, `zip_code` - Property location
- `raw_payload` (JSONB) - Original immutable submission
- `latest_payload` (JSONB) - Auto-regenerated from normalized data

#### 2. **parties** - Plaintiffs and Defendants
Stores all parties involved in the case.

**Key Fields:**
- `party_type` - Either 'plaintiff' or 'defendant'
- `party_number` - Order in the form (1, 2, 3...)
- `is_head_of_household` - Boolean (only one HoH per unit enforced)
- `unit_number` - For multi-unit properties

**Important Constraint:**
- Only ONE Head of Household per unit per case (enforced by `idx_one_hoh_per_unit`)

#### 3. **issue_categories** - Issue Type Groups
Pre-seeded categories: Vermin, Insects, Environmental, Housing, Safety, Legal

#### 4. **issue_options** - Specific Issues
Pre-seeded options like "Rats/Mice", "Bedbugs", "Mold", etc.

#### 5. **party_issue_selections** - Plaintiff Issues
Many-to-many relationship between plaintiffs and their selected issues.

#### 6. **discovery_details** - Additional Discovery Data
Stores notice dates, complaint information, and documentation details per plaintiff.

## Key Features

### 1. **Dual JSON Storage**

- **raw_payload**: Immutable original submission
- **latest_payload**: Auto-regenerated from normalized data whenever data changes

This enables:
- Audit trail of original submission
- Editable normalized data
- Automatic JSON regeneration on any update

### 2. **Head of Household Constraint**

The partial unique index enforces that only one plaintiff can be marked as Head of Household per unit:

```sql
CREATE UNIQUE INDEX idx_one_hoh_per_unit
ON parties (case_id, unit_number)
WHERE is_head_of_household = true AND unit_number IS NOT NULL;
```

### 3. **Automatic Payload Regeneration**

Any update to normalized data automatically regenerates `latest_payload`:

```sql
-- This function is called automatically via triggers
SELECT regenerate_case_payload('case-uuid-here');
```

## Usage Examples

### Insert a New Case

```sql
-- 1. Insert the case
INSERT INTO cases (
    property_address,
    city,
    state,
    zip_code,
    filing_location,
    internal_name,
    form_name,
    raw_payload
) VALUES (
    '123 Main St, Apt 4B',
    'Boston',
    'MA',
    '02101',
    'Suffolk County District Court',
    'smith-v-jones-2025',
    'Smith v. Jones Habitability Case',
    '{"original": "submission", "data": "here"}'::jsonb
) RETURNING id;

-- Let's say this returns: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
```

### Add Plaintiffs

```sql
-- Insert first plaintiff (Head of Household)
INSERT INTO parties (
    case_id,
    party_type,
    party_number,
    first_name,
    last_name,
    full_name,
    plaintiff_type,
    age_category,
    is_head_of_household,
    unit_number
) VALUES (
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'plaintiff',
    1,
    'John',
    'Smith',
    'John Smith',
    'Individual',
    'Adult',
    true,
    '4B'
) RETURNING id;

-- Insert second plaintiff (same unit, NOT HoH)
INSERT INTO parties (
    case_id,
    party_type,
    party_number,
    first_name,
    last_name,
    full_name,
    plaintiff_type,
    age_category,
    is_head_of_household,
    unit_number
) VALUES (
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'plaintiff',
    2,
    'Jane',
    'Smith',
    'Jane Smith',
    'Individual',
    'Adult',
    false,  -- Cannot be HoH, John is already HoH for unit 4B
    '4B'
) RETURNING id;
```

### Add Defendants

```sql
INSERT INTO parties (
    case_id,
    party_type,
    party_number,
    first_name,
    last_name,
    full_name,
    entity_type,
    role
) VALUES (
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'defendant',
    1,
    'Robert',
    'Jones',
    'Robert Jones',
    'LLC',
    'Manager/Owner'
);
```

### Add Issues to Plaintiff

```sql
-- First, get the plaintiff and issue option IDs
WITH plaintiff AS (
    SELECT id FROM parties
    WHERE case_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    AND party_type = 'plaintiff'
    AND party_number = 1
),
vermin_issues AS (
    SELECT io.id, io.option_code
    FROM issue_options io
    JOIN issue_categories ic ON io.category_id = ic.id
    WHERE ic.category_code = 'vermin'
    AND io.option_code IN ('RatsMice', 'Bedbugs')
)
-- Insert issue selections
INSERT INTO party_issue_selections (party_id, issue_option_id)
SELECT p.id, v.id
FROM plaintiff p
CROSS JOIN vermin_issues v;
```

### Add Discovery Details

```sql
INSERT INTO discovery_details (
    party_id,
    has_received_notice,
    notice_date,
    notice_type,
    has_filed_complaint,
    complaint_date,
    complaint_agency,
    has_documentation,
    documentation_types
) VALUES (
    (SELECT id FROM parties
     WHERE case_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
     AND party_type = 'plaintiff'
     AND party_number = 1),
    true,
    '2025-01-15',
    'Written Notice to Landlord',
    true,
    '2025-02-01',
    'City Housing Inspection',
    true,
    ARRAY['Photos', 'Emails', 'Inspection Report']
);
```

### Query Examples

#### Get All Cases with Counts

```sql
SELECT * FROM v_cases_complete;
```

#### Get Complete Case Data

```sql
SELECT
    c.id,
    c.property_address,
    c.latest_payload
FROM cases c
WHERE c.id = 'case-uuid-here';
```

#### Get All Plaintiffs for a Case with Their Issues

```sql
SELECT
    p.full_name,
    p.is_head_of_household,
    array_agg(DISTINCT ic.category_name || ': ' || io.option_name) as issues
FROM parties p
LEFT JOIN party_issue_selections pis ON p.id = pis.party_id
LEFT JOIN issue_options io ON pis.issue_option_id = io.id
LEFT JOIN issue_categories ic ON io.category_id = ic.id
WHERE p.case_id = 'case-uuid-here'
AND p.party_type = 'plaintiff'
GROUP BY p.id, p.full_name, p.is_head_of_household, p.party_number
ORDER BY p.party_number;
```

#### Get Plaintiff Discovery Summary

```sql
SELECT
    p.full_name,
    dd.has_received_notice,
    dd.notice_date,
    dd.has_filed_complaint,
    dd.complaint_agency,
    dd.documentation_types
FROM parties p
LEFT JOIN discovery_details dd ON p.id = dd.party_id
WHERE p.case_id = 'case-uuid-here'
AND p.party_type = 'plaintiff'
ORDER BY p.party_number;
```

#### Find All Cases with Specific Issue

```sql
SELECT DISTINCT
    c.id,
    c.property_address,
    c.city,
    c.state
FROM cases c
JOIN parties p ON c.id = p.case_id
JOIN party_issue_selections pis ON p.id = pis.party_id
JOIN issue_options io ON pis.issue_option_id = io.id
WHERE io.option_code = 'Mold'
ORDER BY c.created_at DESC;
```

#### Get Latest Payload (Regenerated JSON)

```sql
SELECT latest_payload
FROM cases
WHERE id = 'case-uuid-here';
```

## Data Migration from Current System

### Convert Existing JSON Files to Database

```sql
-- Example function to import from existing JSON structure
CREATE OR REPLACE FUNCTION import_json_submission(json_data JSONB)
RETURNS UUID AS $$
DECLARE
    new_case_id UUID;
    plaintiff_data JSONB;
    defendant_data JSONB;
    new_party_id UUID;
BEGIN
    -- Insert case
    INSERT INTO cases (
        property_address,
        city,
        state,
        zip_code,
        filing_location,
        internal_name,
        form_name,
        raw_payload
    ) VALUES (
        json_data->'Full_Address'->>'StreetAddress',
        json_data->'Full_Address'->'State_Province'->'City'->>'Name',
        json_data->'Full_Address'->'State_Province'->>'Name',
        json_data->'Full_Address'->'State_Province'->'City'->'PostalCode'->>'Name',
        json_data->>'FilingLocation',
        json_data->>'InternalName',
        json_data->>'Name',
        json_data
    ) RETURNING id INTO new_case_id;

    -- Insert plaintiffs
    FOR plaintiff_data IN SELECT * FROM jsonb_array_elements(json_data->'PlaintiffDetails')
    LOOP
        INSERT INTO parties (
            case_id,
            party_type,
            party_number,
            first_name,
            last_name,
            full_name,
            plaintiff_type,
            age_category,
            is_head_of_household
        ) VALUES (
            new_case_id,
            'plaintiff',
            (SELECT COUNT(*) + 1 FROM parties WHERE case_id = new_case_id AND party_type = 'plaintiff'),
            plaintiff_data->'Name'->>'First',
            plaintiff_data->'Name'->>'Last',
            plaintiff_data->'Name'->>'FirstAndLast',
            plaintiff_data->>'Type',
            plaintiff_data->>'AgeCategory',
            (plaintiff_data->>'HeadOfHousehold')::boolean
        ) RETURNING id INTO new_party_id;

        -- Import issues for this plaintiff
        -- (You would need to parse the Discovery object and map to issue_options)
    END LOOP;

    -- Insert defendants
    FOR defendant_data IN SELECT * FROM jsonb_array_elements(json_data->'DefendantDetails2')
    LOOP
        INSERT INTO parties (
            case_id,
            party_type,
            party_number,
            first_name,
            last_name,
            full_name,
            entity_type,
            role
        ) VALUES (
            new_case_id,
            'defendant',
            (SELECT COUNT(*) + 1 FROM parties WHERE case_id = new_case_id AND party_type = 'defendant'),
            defendant_data->'Name'->>'First',
            defendant_data->'Name'->>'Last',
            defendant_data->'Name'->>'FirstAndLast',
            defendant_data->>'EntityType',
            defendant_data->>'Role'
        );
    END LOOP;

    RETURN new_case_id;
END;
$$ LANGUAGE plpgsql;
```

## Maintenance

### Update Issue Categories

```sql
-- Add a new issue category
INSERT INTO issue_categories (category_code, category_name, display_order)
VALUES ('utilities', 'Utility Issues', 7);

-- Add options to the new category
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'NoHotWater', 'No Hot Water', 1
FROM issue_categories
WHERE category_code = 'utilities';
```

### Regenerate Payload Manually

```sql
-- If you need to manually regenerate a case's latest_payload
UPDATE cases
SET latest_payload = regenerate_case_payload(id)
WHERE id = 'case-uuid-here';
```

### Find Constraint Violations

```sql
-- Find cases with multiple HoH in same unit (shouldn't exist due to constraint)
SELECT
    case_id,
    unit_number,
    COUNT(*) as hoh_count
FROM parties
WHERE is_head_of_household = true
AND unit_number IS NOT NULL
GROUP BY case_id, unit_number
HAVING COUNT(*) > 1;
```

## Performance Considerations

1. **Indexes**: All common query paths are indexed (case lookups, party queries, issue selections)
2. **JSONB**: Use JSONB operators for efficient querying of payload columns
3. **Triggers**: Payload regeneration happens automatically but can be disabled if bulk importing
4. **Partitioning**: Consider partitioning `cases` by created_at for very large datasets

## Backup and Recovery

```bash
# Backup entire database
pg_dump legal_forms > backup_$(date +%Y%m%d).sql

# Backup schema only
pg_dump --schema-only legal_forms > schema_backup.sql

# Restore
psql legal_forms < backup_20250107.sql
```

## Security Recommendations

1. **Row-Level Security**: Consider enabling RLS for multi-tenant scenarios
2. **Audit Logging**: Enable PostgreSQL audit logging for compliance
3. **Encryption**: Use pgcrypto for sensitive fields if needed
4. **Permissions**: Grant minimal necessary permissions to application users

## API Integration Points

The schema is designed to work with your existing Express.js API:

- **POST /api/form-entries**: Insert into `cases`, `parties`, `party_issue_selections`, `discovery_details`
- **GET /api/form-entries/:id**: Query `cases.latest_payload` or join all tables
- **PUT /api/form-entries/:id**: Update normalized tables, auto-regenerates JSON
- **DELETE /api/form-entries/:id**: Cascade deletes handle all related records

## Troubleshooting

### Issue: Cannot add second HoH to same unit

**Error**: `duplicate key value violates unique constraint "idx_one_hoh_per_unit"`

**Solution**: This is by design. Only one plaintiff per unit can be Head of Household. Either:
1. Change the existing HoH to `is_head_of_household = false`
2. Assign the new plaintiff to a different unit
3. Mark the new plaintiff as non-HoH

### Issue: Payload not regenerating

**Check**: Verify triggers are enabled:

```sql
SELECT tgname, tgenabled
FROM pg_trigger
WHERE tgname LIKE 'regenerate%';
```

**Fix**: Re-create triggers if needed:

```sql
-- Re-run the trigger creation section from schema.sql
```

## Contributing

When modifying the schema:

1. Always create migration scripts (don't modify schema.sql directly in production)
2. Test with realistic data volumes
3. Update this README with new features
4. Document any new constraints or business rules

## License

Internal use only - Lipton Legal
