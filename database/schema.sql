-- ============================================================================
-- Legal Form Application - PostgreSQL Database Schema
-- ============================================================================
-- This schema supports the Lipton Legal AutoPopulationForm application
-- Stores habitability case data with multiple plaintiffs, defendants, and issues
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- CASES TABLE
-- Stores the main case/submission information
-- ============================================================================
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Case identifiers
    internal_name VARCHAR(255),
    form_name VARCHAR(255),

    -- Property information
    property_address TEXT NOT NULL,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(2) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    county VARCHAR(255),

    -- Filing location
    filing_location VARCHAR(255),

    -- JSON payload columns
    raw_payload JSONB NOT NULL, -- Original submission, immutable
    latest_payload JSONB, -- Regenerated from normalized data, editable view

    -- Metadata flags
    is_active BOOLEAN DEFAULT true,

    -- Indexes for common queries
    CONSTRAINT cases_state_check CHECK (LENGTH(state) = 2)
);

-- ============================================================================
-- PARTIES TABLE
-- Stores both plaintiffs and defendants
-- ============================================================================
CREATE TABLE parties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,

    -- Party identification
    party_type VARCHAR(20) NOT NULL CHECK (party_type IN ('plaintiff', 'defendant')),
    party_number INTEGER NOT NULL, -- Order in the form (plaintiff-1, plaintiff-2, etc.)

    -- Name information
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    full_name VARCHAR(511), -- Computed or stored

    -- Plaintiff-specific fields
    plaintiff_type VARCHAR(50), -- Individual, Organization, etc.
    age_category VARCHAR(50), -- Adult, Minor, etc.
    is_head_of_household BOOLEAN DEFAULT false,
    unit_number VARCHAR(50), -- For HoH constraint

    -- Defendant-specific fields
    entity_type VARCHAR(50), -- Individual, LLC, Corporation, etc.
    role VARCHAR(50), -- Manager/Owner

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT parties_case_party_number_unique UNIQUE (case_id, party_type, party_number),
    CONSTRAINT parties_names_check CHECK (
        (party_type = 'plaintiff' AND first_name IS NOT NULL AND last_name IS NOT NULL) OR
        (party_type = 'defendant' AND (first_name IS NOT NULL OR last_name IS NOT NULL))
    )
);

-- Partial unique index: Only one Head of Household per unit per case
CREATE UNIQUE INDEX idx_one_hoh_per_unit
ON parties (case_id, unit_number)
WHERE is_head_of_household = true AND unit_number IS NOT NULL;

-- ============================================================================
-- ISSUE_CATEGORIES TABLE
-- Stores the main issue categories (Vermin, Insects, Safety, etc.)
-- ============================================================================
CREATE TABLE issue_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Category identification
    category_code VARCHAR(50) NOT NULL UNIQUE, -- vermin, insects, environmental, etc.
    category_name VARCHAR(255) NOT NULL,
    display_order INTEGER,

    -- Category type
    is_multi_select BOOLEAN DEFAULT true, -- Can select multiple options

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- ============================================================================
-- ISSUE_OPTIONS TABLE
-- Stores individual issue options within categories
-- ============================================================================
CREATE TABLE issue_options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES issue_categories(id) ON DELETE CASCADE,

    -- Option identification
    option_code VARCHAR(50) NOT NULL, -- RatsMice, Bedbugs, etc.
    option_name VARCHAR(255) NOT NULL,
    display_order INTEGER,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,

    -- Ensure unique options within category
    CONSTRAINT issue_options_category_code_unique UNIQUE (category_id, option_code)
);

-- ============================================================================
-- PARTY_ISSUE_SELECTIONS TABLE
-- Links parties (plaintiffs) to their selected issues
-- ============================================================================
CREATE TABLE party_issue_selections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- References
    party_id UUID NOT NULL REFERENCES parties(id) ON DELETE CASCADE,
    issue_option_id UUID NOT NULL REFERENCES issue_options(id) ON DELETE CASCADE,

    -- Selection metadata
    selected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    notes TEXT, -- Optional notes about this specific issue

    -- Prevent duplicate selections
    CONSTRAINT party_issue_unique UNIQUE (party_id, issue_option_id)
);

-- ============================================================================
-- DISCOVERY_DETAILS TABLE
-- Stores additional discovery information per plaintiff
-- ============================================================================
CREATE TABLE discovery_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    party_id UUID NOT NULL REFERENCES parties(id) ON DELETE CASCADE,

    -- Discovery fields (from form)
    has_received_notice BOOLEAN DEFAULT false,
    notice_date DATE,
    notice_type VARCHAR(255),

    has_filed_complaint BOOLEAN DEFAULT false,
    complaint_date DATE,
    complaint_agency VARCHAR(255),

    has_repair_request BOOLEAN DEFAULT false,
    repair_request_date DATE,

    has_documentation BOOLEAN DEFAULT false,
    documentation_types TEXT[], -- Array of document types

    additional_notes TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- One discovery record per plaintiff
    CONSTRAINT discovery_party_unique UNIQUE (party_id)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Cases indexes
CREATE INDEX idx_cases_created_at ON cases(created_at DESC);
CREATE INDEX idx_cases_property_address ON cases(property_address);
CREATE INDEX idx_cases_city_state ON cases(city, state);
CREATE INDEX idx_cases_active ON cases(is_active) WHERE is_active = true;

-- Parties indexes
CREATE INDEX idx_parties_case_id ON parties(case_id);
CREATE INDEX idx_parties_type ON parties(party_type);
CREATE INDEX idx_parties_full_name ON parties(full_name);
CREATE INDEX idx_parties_hoh ON parties(is_head_of_household) WHERE is_head_of_household = true;

-- Issue selections indexes
CREATE INDEX idx_party_issues_party ON party_issue_selections(party_id);
CREATE INDEX idx_party_issues_option ON party_issue_selections(issue_option_id);

-- Discovery indexes
CREATE INDEX idx_discovery_party ON discovery_details(party_id);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to relevant tables
CREATE TRIGGER update_cases_updated_at BEFORE UPDATE ON cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_parties_updated_at BEFORE UPDATE ON parties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_discovery_updated_at BEFORE UPDATE ON discovery_details
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to regenerate latest_payload from normalized data
CREATE OR REPLACE FUNCTION regenerate_case_payload(case_uuid UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    case_record RECORD;
    plaintiffs JSONB;
    defendants JSONB;
BEGIN
    -- Get case information
    SELECT * INTO case_record FROM cases WHERE id = case_uuid;

    -- Build plaintiffs array with discovery data
    SELECT jsonb_agg(
        jsonb_build_object(
            'id', p.id,
            'Name', jsonb_build_object(
                'First', p.first_name,
                'Last', p.last_name,
                'FirstAndLast', p.full_name
            ),
            'Type', p.plaintiff_type,
            'AgeCategory', p.age_category,
            'HeadOfHousehold', p.is_head_of_household,
            'UnitNumber', p.unit_number,
            'Discovery', (
                SELECT jsonb_build_object(
                    'Vermin', COALESCE((
                        SELECT jsonb_agg(io.option_code)
                        FROM party_issue_selections pis
                        JOIN issue_options io ON pis.issue_option_id = io.id
                        JOIN issue_categories ic ON io.category_id = ic.id
                        WHERE pis.party_id = p.id AND ic.category_code = 'vermin'
                    ), '[]'::jsonb),
                    'Insects', COALESCE((
                        SELECT jsonb_agg(io.option_code)
                        FROM party_issue_selections pis
                        JOIN issue_options io ON pis.issue_option_id = io.id
                        JOIN issue_categories ic ON io.category_id = ic.id
                        WHERE pis.party_id = p.id AND ic.category_code = 'insects'
                    ), '[]'::jsonb),
                    'Environmental', COALESCE((
                        SELECT jsonb_agg(io.option_code)
                        FROM party_issue_selections pis
                        JOIN issue_options io ON pis.issue_option_id = io.id
                        JOIN issue_categories ic ON io.category_id = ic.id
                        WHERE pis.party_id = p.id AND ic.category_code = 'environmental'
                    ), '[]'::jsonb),
                    'HasReceivedNotice', COALESCE(dd.has_received_notice, false),
                    'HasFiledComplaint', COALESCE(dd.has_filed_complaint, false)
                )
                FROM discovery_details dd
                WHERE dd.party_id = p.id
            )
        ) ORDER BY p.party_number
    ) INTO plaintiffs
    FROM parties p
    WHERE p.case_id = case_uuid AND p.party_type = 'plaintiff';

    -- Build defendants array
    SELECT jsonb_agg(
        jsonb_build_object(
            'id', d.id,
            'Name', jsonb_build_object(
                'First', d.first_name,
                'Last', d.last_name,
                'FirstAndLast', d.full_name
            ),
            'EntityType', d.entity_type,
            'Role', d.role
        ) ORDER BY d.party_number
    ) INTO defendants
    FROM parties d
    WHERE d.case_id = case_uuid AND d.party_type = 'defendant';

    -- Build complete result
    result := jsonb_build_object(
        'Id', case_record.id,
        'InternalName', case_record.internal_name,
        'Name', case_record.form_name,
        'PlaintiffDetails', COALESCE(plaintiffs, '[]'::jsonb),
        'DefendantDetails2', COALESCE(defendants, '[]'::jsonb),
        'Full_Address', jsonb_build_object(
            'Country', 'US',
            'State_Province', jsonb_build_object(
                'Name', case_record.state,
                'City', jsonb_build_object(
                    'Name', case_record.city,
                    'PostalCode', jsonb_build_object(
                        'Name', case_record.zip_code
                    )
                )
            ),
            'StreetAddress', case_record.property_address
        ),
        'FilingLocation', case_record.filing_location
    );

    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Trigger functions to auto-regenerate latest_payload on data changes
-- Split into table-specific functions to avoid field validation errors

-- Trigger function for parties table
CREATE OR REPLACE FUNCTION auto_regenerate_payload_parties()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE cases
    SET latest_payload = regenerate_case_payload(NEW.case_id)
    WHERE id = NEW.case_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger function for party_issue_selections table
CREATE OR REPLACE FUNCTION auto_regenerate_payload_issues()
RETURNS TRIGGER AS $$
DECLARE
    target_case_id UUID;
BEGIN
    -- Handle both INSERT/UPDATE (NEW) and DELETE (OLD)
    IF TG_OP = 'DELETE' THEN
        SELECT case_id INTO target_case_id FROM parties WHERE id = OLD.party_id;
    ELSE
        SELECT case_id INTO target_case_id FROM parties WHERE id = NEW.party_id;
    END IF;
    
    UPDATE cases
    SET latest_payload = regenerate_case_payload(target_case_id)
    WHERE id = target_case_id;
    
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Trigger function for discovery_details table
CREATE OR REPLACE FUNCTION auto_regenerate_payload_discovery()
RETURNS TRIGGER AS $$
DECLARE
    target_case_id UUID;
BEGIN
    SELECT case_id INTO target_case_id FROM parties WHERE id = NEW.party_id;
    
    UPDATE cases
    SET latest_payload = regenerate_case_payload(target_case_id)
    WHERE id = target_case_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers using the table-specific functions
CREATE TRIGGER regenerate_on_party_change AFTER INSERT OR UPDATE ON parties
    FOR EACH ROW EXECUTE FUNCTION auto_regenerate_payload_parties();

CREATE TRIGGER regenerate_on_issue_change AFTER INSERT OR UPDATE OR DELETE ON party_issue_selections
    FOR EACH ROW EXECUTE FUNCTION auto_regenerate_payload_issues();

CREATE TRIGGER regenerate_on_discovery_change AFTER INSERT OR UPDATE ON discovery_details
    FOR EACH ROW EXECUTE FUNCTION auto_regenerate_payload_discovery();

-- ============================================================================
-- SEED DATA - Issue Categories and Options
-- ============================================================================

-- Insert Issue Categories
INSERT INTO issue_categories (category_code, category_name, display_order, is_multi_select) VALUES
    ('vermin', 'Vermin Issues', 1, true),
    ('insects', 'Insect Issues', 2, true),
    ('environmental', 'Environmental Hazards', 3, true),
    ('housing', 'Housing Conditions', 4, true),
    ('safety', 'Safety Issues', 5, true),
    ('legal', 'Legal Issues', 6, true)
ON CONFLICT (category_code) DO NOTHING;

-- Insert Vermin Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'RatsMice', 'Rats/Mice', 1 FROM issue_categories WHERE category_code = 'vermin'
UNION ALL
SELECT id, 'Bedbugs', 'Bedbugs', 2 FROM issue_categories WHERE category_code = 'vermin'
UNION ALL
SELECT id, 'OtherVermin', 'Other Vermin', 3 FROM issue_categories WHERE category_code = 'vermin';

-- Insert Insect Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'Roaches', 'Roaches', 1 FROM issue_categories WHERE category_code = 'insects'
UNION ALL
SELECT id, 'Ants', 'Ants', 2 FROM issue_categories WHERE category_code = 'insects'
UNION ALL
SELECT id, 'Flies', 'Flies', 3 FROM issue_categories WHERE category_code = 'insects'
UNION ALL
SELECT id, 'OtherInsects', 'Other Insects', 4 FROM issue_categories WHERE category_code = 'insects';

-- Insert Environmental Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'Mold', 'Mold', 1 FROM issue_categories WHERE category_code = 'environmental'
UNION ALL
SELECT id, 'LeadPaint', 'Lead Paint', 2 FROM issue_categories WHERE category_code = 'environmental'
UNION ALL
SELECT id, 'Asbestos', 'Asbestos', 3 FROM issue_categories WHERE category_code = 'environmental'
UNION ALL
SELECT id, 'WaterDamage', 'Water Damage', 4 FROM issue_categories WHERE category_code = 'environmental';

-- Insert Housing Condition Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'HeatAC', 'Heat/AC Issues', 1 FROM issue_categories WHERE category_code = 'housing'
UNION ALL
SELECT id, 'Plumbing', 'Plumbing Issues', 2 FROM issue_categories WHERE category_code = 'housing'
UNION ALL
SELECT id, 'Electrical', 'Electrical Issues', 3 FROM issue_categories WHERE category_code = 'housing'
UNION ALL
SELECT id, 'StructuralDamage', 'Structural Damage', 4 FROM issue_categories WHERE category_code = 'housing';

-- Insert Safety Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'Locks', 'Lock Issues', 1 FROM issue_categories WHERE category_code = 'safety'
UNION ALL
SELECT id, 'SmokeDetectors', 'Smoke Detector Issues', 2 FROM issue_categories WHERE category_code = 'safety'
UNION ALL
SELECT id, 'CarbonMonoxide', 'Carbon Monoxide Detector Issues', 3 FROM issue_categories WHERE category_code = 'safety'
UNION ALL
SELECT id, 'FireHazards', 'Fire Hazards', 4 FROM issue_categories WHERE category_code = 'safety';

-- Insert Legal Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'Retaliation', 'Retaliation', 1 FROM issue_categories WHERE category_code = 'legal'
UNION ALL
SELECT id, 'Discrimination', 'Discrimination', 2 FROM issue_categories WHERE category_code = 'legal'
UNION ALL
SELECT id, 'Harassment', 'Harassment', 3 FROM issue_categories WHERE category_code = 'legal'
UNION ALL
SELECT id, 'IllegalEviction', 'Illegal Eviction', 4 FROM issue_categories WHERE category_code = 'legal';

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Complete case data with all relationships
CREATE OR REPLACE VIEW v_cases_complete AS
SELECT
    c.id as case_id,
    c.created_at,
    c.property_address,
    c.city,
    c.state,
    c.zip_code,
    c.filing_location,
    COUNT(DISTINCT CASE WHEN p.party_type = 'plaintiff' THEN p.id END) as plaintiff_count,
    COUNT(DISTINCT CASE WHEN p.party_type = 'defendant' THEN p.id END) as defendant_count,
    c.latest_payload
FROM cases c
LEFT JOIN parties p ON c.id = p.case_id
GROUP BY c.id;

-- View: Plaintiff issues summary
CREATE OR REPLACE VIEW v_plaintiff_issues AS
SELECT
    p.id as party_id,
    p.case_id,
    p.full_name as plaintiff_name,
    ic.category_name,
    io.option_name as issue,
    pis.selected_at
FROM parties p
JOIN party_issue_selections pis ON p.id = pis.party_id
JOIN issue_options io ON pis.issue_option_id = io.id
JOIN issue_categories ic ON io.category_id = ic.id
WHERE p.party_type = 'plaintiff'
ORDER BY p.case_id, p.party_number, ic.display_order, io.display_order;

-- ============================================================================
-- GRANTS AND PERMISSIONS (uncomment and adjust as needed)
-- ============================================================================

-- Example: Grant permissions to application role
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO app_user;

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE cases IS 'Stores main case/submission information from the legal form application';
COMMENT ON TABLE parties IS 'Stores both plaintiffs and defendants for each case';
COMMENT ON TABLE issue_categories IS 'Stores the main issue categories (Vermin, Insects, Safety, etc.)';
COMMENT ON TABLE issue_options IS 'Stores individual issue options within categories';
COMMENT ON TABLE party_issue_selections IS 'Links parties (plaintiffs) to their selected issues';
COMMENT ON TABLE discovery_details IS 'Stores additional discovery information per plaintiff';

COMMENT ON COLUMN cases.raw_payload IS 'Original form submission JSON, immutable record';
COMMENT ON COLUMN cases.latest_payload IS 'Regenerated JSON from normalized data, represents current editable state';
COMMENT ON COLUMN parties.party_number IS 'Order in the form (plaintiff-1, plaintiff-2, etc.)';
COMMENT ON COLUMN parties.is_head_of_household IS 'Only one HoH allowed per unit per case (enforced by partial unique index)';

COMMENT ON FUNCTION regenerate_case_payload IS 'Regenerates the latest_payload JSONB from normalized relational data';
COMMENT ON INDEX idx_one_hoh_per_unit IS 'Enforces business rule: only one Head of Household per unit per case';
