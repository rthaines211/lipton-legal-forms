-- ============================================================================
-- Legal Form Application - Taxonomy Cleanup Script
-- ============================================================================
-- This script removes duplicates and options not correlated to the form output
-- Based on audit of goalOutput.md structure
-- ============================================================================

-- ============================================================================
-- STEP 1: Remove duplicate options (keep new comprehensive taxonomy)
-- ============================================================================

-- Remove old duplicates from Environmental Hazards category
-- (These are duplicated in Structure category with better naming)
DELETE FROM issue_options
WHERE category_id = (SELECT id FROM issue_categories WHERE category_code = 'environmental')
AND option_code IN ('Asbestos', 'LeadPaint', 'Mold', 'WaterDamage');

-- Remove old duplicates from Legal category
-- (These don't appear in the form output structure)
DELETE FROM issue_options
WHERE category_id = (SELECT id FROM issue_categories WHERE category_code = 'legal');

-- Remove old duplicates from Housing Conditions category
-- (These don't appear in the form output structure)
DELETE FROM issue_options
WHERE category_id = (SELECT id FROM issue_categories WHERE category_code = 'housing');

-- Remove old capitalized duplicates in Vermin category
DELETE FROM issue_options
WHERE category_id = (SELECT id FROM issue_categories WHERE category_code = 'vermin')
AND option_code IN ('RatsMice', 'Bedbugs', 'OtherVermin');

-- Remove old capitalized duplicates in Insects category
DELETE FROM issue_options
WHERE category_id = (SELECT id FROM issue_categories WHERE category_code = 'insects')
AND option_code IN ('Roaches', 'Ants', 'Flies', 'OtherInsects');

-- ============================================================================
-- STEP 2: Remove categories not in form output
-- ============================================================================

-- These categories don't exist in the goalOutput.md Discovery structure:
-- - environmental (merged into structure, health_hazard)
-- - housing (merged into hvac, plumbing, electrical)
-- - legal (appears as harassment/notices/discrimination flags)

DELETE FROM issue_categories WHERE category_code = 'environmental';
DELETE FROM issue_categories WHERE category_code = 'housing';
DELETE FROM issue_categories WHERE category_code = 'legal';

-- ============================================================================
-- STEP 3: Add missing options from form output
-- ============================================================================

-- Add missing Vermin options from goalOutput.md
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'skunks', 'Skunks', 8 FROM issue_categories WHERE category_code = 'vermin'
UNION ALL
SELECT id, 'pigeons', 'Pigeons', 9 FROM issue_categories WHERE category_code = 'vermin'
ON CONFLICT (category_id, option_code) DO NOTHING;

-- Fix "Racoons" to "Raccoons" spelling consistency
UPDATE issue_options SET option_name = 'Raccoons'
WHERE option_code = 'raccoons' AND category_id = (SELECT id FROM issue_categories WHERE category_code = 'vermin');

-- Add missing Insect options from goalOutput.md
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'hornets', 'Hornets', 10 FROM issue_categories WHERE category_code = 'insects'
UNION ALL
SELECT id, 'bees', 'Bees', 11 FROM issue_categories WHERE category_code = 'insects'
ON CONFLICT (category_id, option_code) DO NOTHING;

-- Fix "Wasps/Bees" since form has them separate - update to just "Wasps"
UPDATE issue_options SET option_name = 'Wasps'
WHERE option_code = 'wasps_bees' AND category_id = (SELECT id FROM issue_categories WHERE category_code = 'insects');

-- ============================================================================
-- STEP 4: Add new categories from form that are missing
-- ============================================================================

-- Add Harassment category (appears in form output)
INSERT INTO issue_categories (category_code, category_name, display_order, is_multi_select)
VALUES ('harassment', 'Harassment', 20, true)
ON CONFLICT (category_code) DO NOTHING;

-- Add Harassment options from goalOutput.md
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'unlawful_detainer', 'Unlawful Detainer', 1 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL
SELECT id, 'eviction_threats', 'Eviction threats', 2 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL
SELECT id, 'by_defendant', 'By defendant', 3 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL
SELECT id, 'by_maintenance', 'By maintenance man/workers', 4 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL
SELECT id, 'by_manager', 'By manager/building staff', 5 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL
SELECT id, 'by_owner', 'By owner', 6 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL
SELECT id, 'other_tenants', 'Other tenants', 7 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL
SELECT id, 'illegitimate_notices', 'Illegitimate notices', 8 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL
SELECT id, 'refusal_repairs', 'Refusal to make timely repairs', 9 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL
SELECT id, 'written_threats', 'Written threats', 10 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL
SELECT id, 'aggressive_language', 'Aggressive/inappropriate language', 11 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL
SELECT id, 'physical_threats', 'Physical threats or touching', 12 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL
SELECT id, 'selective_notices', 'Notices singling out one tenant, but not uniformly given to all tenants', 13 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL
SELECT id, 'duplicative_notices', 'Duplicative notices', 14 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL
SELECT id, 'untimely_response', 'Untimely Response from Landlord', 15 FROM issue_categories WHERE category_code = 'harassment'
ON CONFLICT (category_id, option_code) DO NOTHING;

-- Add Utilities category (appears as "Checkbox 44n6i" in form)
INSERT INTO issue_categories (category_code, category_name, display_order, is_multi_select)
VALUES ('utilities', 'Utilities', 21, true)
ON CONFLICT (category_code) DO NOTHING;

-- Add Utility options from goalOutput.md
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'gas_leak', 'Gas leak', 1 FROM issue_categories WHERE category_code = 'utilities'
UNION ALL
SELECT id, 'water_shutoffs', 'Water shutoffs', 2 FROM issue_categories WHERE category_code = 'utilities'
UNION ALL
SELECT id, 'electricity_shutoffs', 'Electricity shutoffs', 3 FROM issue_categories WHERE category_code = 'utilities'
UNION ALL
SELECT id, 'heat_shutoff', 'Heat Shutoff', 4 FROM issue_categories WHERE category_code = 'utilities'
UNION ALL
SELECT id, 'gas_shutoff', 'Gas Shutoff', 5 FROM issue_categories WHERE category_code = 'utilities'
ON CONFLICT (category_id, option_code) DO NOTHING;

-- Add Discrimination category (appears as boolean flags in form)
INSERT INTO issue_categories (category_code, category_name, display_order, is_multi_select)
VALUES ('discrimination', 'Discrimination', 22, true)
ON CONFLICT (category_code) DO NOTHING;

-- Add Discrimination options from goalOutput.md
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'age_discrimination', 'Age discrimination', 1 FROM issue_categories WHERE category_code = 'discrimination'
UNION ALL
SELECT id, 'racial_discrimination', 'Racial Discrimination', 2 FROM issue_categories WHERE category_code = 'discrimination'
UNION ALL
SELECT id, 'disability_discrimination', 'Disability discrimination', 3 FROM issue_categories WHERE category_code = 'discrimination'
ON CONFLICT (category_id, option_code) DO NOTHING;

-- ============================================================================
-- STEP 5: Update display_order for remaining categories
-- ============================================================================

UPDATE issue_categories SET display_order = 1 WHERE category_code = 'vermin';
UPDATE issue_categories SET display_order = 2 WHERE category_code = 'insects';
UPDATE issue_categories SET display_order = 3 WHERE category_code = 'hvac';
UPDATE issue_categories SET display_order = 4 WHERE category_code = 'electrical';
UPDATE issue_categories SET display_order = 5 WHERE category_code = 'fire_hazard';
UPDATE issue_categories SET display_order = 6 WHERE category_code = 'appliances';
UPDATE issue_categories SET display_order = 7 WHERE category_code = 'plumbing';
UPDATE issue_categories SET display_order = 8 WHERE category_code = 'cabinets';
UPDATE issue_categories SET display_order = 9 WHERE category_code = 'flooring';
UPDATE issue_categories SET display_order = 10 WHERE category_code = 'windows';
UPDATE issue_categories SET display_order = 11 WHERE category_code = 'doors';
UPDATE issue_categories SET display_order = 12 WHERE category_code = 'structure';
UPDATE issue_categories SET display_order = 13 WHERE category_code = 'common_areas';
UPDATE issue_categories SET display_order = 14 WHERE category_code = 'trash_problems';
UPDATE issue_categories SET display_order = 15 WHERE category_code = 'nuisance';
UPDATE issue_categories SET display_order = 16 WHERE category_code = 'health_hazard';
UPDATE issue_categories SET display_order = 17 WHERE category_code = 'safety';
UPDATE issue_categories SET display_order = 18 WHERE category_code = 'harassment';
UPDATE issue_categories SET display_order = 19 WHERE category_code = 'notices';
UPDATE issue_categories SET display_order = 20 WHERE category_code = 'utilities';
UPDATE issue_categories SET display_order = 21 WHERE category_code = 'discrimination';
UPDATE issue_categories SET display_order = 22 WHERE category_code = 'government_entities';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Check for remaining duplicates
DO $$
DECLARE
    duplicate_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO duplicate_count
    FROM (
        SELECT option_name
        FROM issue_options
        GROUP BY option_name
        HAVING COUNT(*) > 1
    ) dupes;

    IF duplicate_count > 0 THEN
        RAISE NOTICE '⚠️  Warning: % duplicate option names still exist', duplicate_count;
    ELSE
        RAISE NOTICE '✅ No duplicate option names found';
    END IF;
END $$;

-- Show final category count
DO $$
DECLARE
    category_count INTEGER;
    option_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO category_count FROM issue_categories WHERE is_active = true;
    SELECT COUNT(*) INTO option_count FROM issue_options WHERE is_active = true;

    RAISE NOTICE '✅ Cleanup complete';
    RAISE NOTICE '📊 Active categories: %', category_count;
    RAISE NOTICE '📋 Active options: %', option_count;
END $$;

-- Display summary
SELECT
    ic.category_name,
    ic.display_order,
    COUNT(io.id) as option_count
FROM issue_categories ic
LEFT JOIN issue_options io ON ic.id = io.category_id
WHERE ic.is_active = true
GROUP BY ic.id, ic.category_name, ic.display_order
ORDER BY ic.display_order;
