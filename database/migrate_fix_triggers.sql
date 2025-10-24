-- Migration: Fix auto_regenerate_payload trigger
-- Date: 2025-10-21
-- Purpose: Split shared trigger function into table-specific functions to fix field validation errors

-- Drop existing triggers first
DROP TRIGGER IF EXISTS regenerate_on_party_change ON parties;
DROP TRIGGER IF EXISTS regenerate_on_issue_change ON party_issue_selections;
DROP TRIGGER IF EXISTS regenerate_on_discovery_change ON discovery_details;

-- Drop the old shared function (CASCADE will drop any remaining triggers)
DROP FUNCTION IF EXISTS auto_regenerate_payload() CASCADE;

-- Create new table-specific trigger functions

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

-- Create new triggers using the table-specific functions
CREATE TRIGGER regenerate_on_party_change AFTER INSERT OR UPDATE ON parties
    FOR EACH ROW EXECUTE FUNCTION auto_regenerate_payload_parties();

CREATE TRIGGER regenerate_on_issue_change AFTER INSERT OR UPDATE OR DELETE ON party_issue_selections
    FOR EACH ROW EXECUTE FUNCTION auto_regenerate_payload_issues();

CREATE TRIGGER regenerate_on_discovery_change AFTER INSERT OR UPDATE ON discovery_details
    FOR EACH ROW EXECUTE FUNCTION auto_regenerate_payload_discovery();

-- Migration complete
-- Verify by running: SELECT tgname, tgrelid::regclass FROM pg_trigger WHERE tgname LIKE 'regenerate%';

