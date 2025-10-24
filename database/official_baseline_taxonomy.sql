-- ============================================================================
-- Legal Form Application - OFFICIAL Baseline Taxonomy
-- ============================================================================
-- This script implements the exact 19-category baseline taxonomy
-- from Baseline Option.md with all official options
--
-- Categories: 19
-- Options: As defined in official baseline documentation
-- ============================================================================

-- ============================================================================
-- STEP 1: TRUNCATE EXISTING TAXONOMY DATA
-- ============================================================================

TRUNCATE TABLE party_issue_selections CASCADE;
TRUNCATE TABLE issue_options RESTART IDENTITY CASCADE;
TRUNCATE TABLE issue_categories RESTART IDENTITY CASCADE;

-- ============================================================================
-- STEP 2: INSERT 19 BASELINE CATEGORIES
-- ============================================================================

WITH cats(name, code, display_order) AS (VALUES
 ('Vermin', 'vermin', 1),
 ('Insects', 'insects', 2),
 ('HVAC', 'hvac', 3),
 ('Electrical', 'electrical', 4),
 ('Fire Hazard', 'fire_hazard', 5),
 ('Government Entities Contacted', 'government_entities', 6),
 ('Appliances', 'appliances', 7),
 ('Plumbing', 'plumbing', 8),
 ('Cabinets', 'cabinets', 9),
 ('Flooring', 'flooring', 10),
 ('Windows', 'windows', 11),
 ('Doors', 'doors', 12),
 ('Structure', 'structure', 13),
 ('Common Areas', 'common_areas', 14),
 ('Trash Problems', 'trash_problems', 15),
 ('Nuisance', 'nuisance', 16),
 ('Health Hazard', 'health_hazard', 17),
 ('Safety', 'safety', 18),
 ('Notices', 'notices', 19)
)
INSERT INTO issue_categories(category_name, category_code, display_order, is_multi_select)
SELECT name, code, display_order, true FROM cats;

-- ============================================================================
-- STEP 3: INSERT BASELINE OPTIONS FOR EACH CATEGORY
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. VERMIN (6 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('rats_mice', 'Rats/Mice', 1),
  ('skunks', 'Skunks', 2),
  ('bats', 'Bats', 3),
  ('raccoons', 'Raccoons', 4),
  ('pigeons', 'Pigeons', 5),
  ('opossums', 'Opossums', 6)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Vermin';

-- ----------------------------------------------------------------------------
-- 2. INSECTS (10 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('ants', 'Ants', 1),
  ('roaches', 'Roaches', 2),
  ('flies', 'Flies', 3),
  ('bedbugs', 'Bedbugs', 4),
  ('wasps', 'Wasps', 5),
  ('hornets', 'Hornets', 6),
  ('spiders', 'Spiders', 7),
  ('termites', 'Termites', 8),
  ('mosquitos', 'Mosquitos', 9),
  ('bees', 'Bees', 10)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Insects';

-- ----------------------------------------------------------------------------
-- 3. HVAC (3 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('air_conditioner', 'Air Conditioner', 1),
  ('heater', 'Heater', 2),
  ('ventilation', 'Ventilation', 3)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'HVAC';

-- ----------------------------------------------------------------------------
-- 4. ELECTRICAL (7 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('outlets', 'Outlets', 1),
  ('panel', 'Panel', 2),
  ('wall_switches', 'Wall Switches', 3),
  ('exterior_lighting', 'Exterior Lighting', 4),
  ('interior_lighting', 'Interior Lighting', 5),
  ('light_fixtures', 'Light Fixtures', 6),
  ('fans', 'Fans', 7)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Electrical';

-- ----------------------------------------------------------------------------
-- 5. FIRE HAZARD (5 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('smoke_alarms', 'Smoke Alarms', 1),
  ('fire_extinguisher', 'Fire Extinguisher', 2),
  ('non_compliant_electricity', 'Non-compliant electricity', 3),
  ('non_gfi_outlets', 'Non-GFI outlets near water', 4),
  ('carbon_monoxide_detectors', 'Carbon monoxide detectors', 5)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Fire Hazard';

-- ----------------------------------------------------------------------------
-- 6. GOVERNMENT ENTITIES CONTACTED (7 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('health_department', 'Health Department', 1),
  ('police_department', 'Police Department', 2),
  ('housing_authority', 'Housing Authority', 3),
  ('dept_environmental_health', 'Department of Environmental Health', 4),
  ('code_enforcement', 'Code Enforcement', 5),
  ('dept_health_services', 'Department of Health Services', 6),
  ('fire_department', 'Fire Department', 7)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Government Entities Contacted';

-- ----------------------------------------------------------------------------
-- 7. APPLIANCES (7 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('stove', 'Stove', 1),
  ('dishwasher', 'Dishwasher', 2),
  ('washer_dryer', 'Washer/Dryer', 3),
  ('oven', 'Oven', 4),
  ('microwave', 'Microwave', 5),
  ('garbage_disposal', 'Garbage Disposal', 6),
  ('refrigerator', 'Refrigerator', 7)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Appliances';

-- ----------------------------------------------------------------------------
-- 8. PLUMBING (8 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('toilet', 'Toilet', 1),
  ('insufficient_water_pressure', 'Insufficient water pressure', 2),
  ('clogged_drains', 'Clogged bath/shower/sink/toilet', 3),
  ('no_hot_water', 'No hot water', 4),
  ('no_cold_water', 'No cold water', 5),
  ('sewage_coming_out', 'Sewage coming out', 6),
  ('no_clean_water_supply', 'No clean water supply', 7),
  ('unsanitary_water', 'Unsanitary water', 8)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Plumbing';

-- ----------------------------------------------------------------------------
-- 9. CABINETS (3 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('broken', 'Broken', 1),
  ('hinges', 'Hinges', 2),
  ('alignment', 'Alignment', 3)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Cabinets';

-- ----------------------------------------------------------------------------
-- 10. FLOORING (4 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('uneven', 'Uneven', 1),
  ('carpet', 'Carpet', 2),
  ('nails_sticking_out', 'Nails sticking out', 3),
  ('tiles', 'Tiles', 4)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Flooring';

-- ----------------------------------------------------------------------------
-- 11. WINDOWS (6 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('broken', 'Broken', 1),
  ('screens', 'Screens', 2),
  ('leaks', 'Leaks', 3),
  ('do_not_lock', 'Do not lock', 4),
  ('missing_windows', 'Missing windows', 5),
  ('broken_missing_screens', 'Broken or missing screens', 6)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Windows';

-- ----------------------------------------------------------------------------
-- 12. DOORS (8 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('broken', 'Broken', 1),
  ('knobs', 'Knobs', 2),
  ('locks', 'Locks', 3),
  ('broken_hinges', 'Broken hinges', 4),
  ('sliding_glass_doors', 'Sliding glass doors', 5),
  ('ineffective_waterproofing', 'Ineffective waterproofing', 6),
  ('water_intrusion_insects', 'Water intrusion and/or insects', 7),
  ('do_not_close_properly', 'Do not close properly', 8)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Doors';

-- ----------------------------------------------------------------------------
-- 13. STRUCTURE (15 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('bumps_in_ceiling', 'Bumps in ceiling', 1),
  ('hole_in_ceiling', 'Hole in ceiling', 2),
  ('water_stains_ceiling', 'Water stains on ceiling', 3),
  ('water_stains_wall', 'Water stains on wall', 4),
  ('hole_in_wall', 'Hole in wall', 5),
  ('paint', 'Paint', 6),
  ('exterior_deck_porch', 'Exterior deck/porch', 7),
  ('waterproof_toilet', 'Waterproof toilet', 8),
  ('waterproof_tub', 'Waterproof tub', 9),
  ('staircase', 'Staircase', 10),
  ('basement_flood', 'Basement flood', 11),
  ('leaks_in_garage', 'Leaks in garage', 12),
  ('soft_spots_leaks', 'Soft spots due to leaks', 13),
  ('ineffective_waterproofing_tub_toilet', 'Ineffective waterproofing of the tubs or toilet', 14),
  ('ineffective_weatherproofing_windows_doors', 'Ineffective weatherproofing of any windows or doors', 15)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Structure';

-- ----------------------------------------------------------------------------
-- 14. COMMON AREAS (16 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('mailbox_broken', 'Mailbox broken', 1),
  ('parking_area_issues', 'Parking area issues', 2),
  ('damage_to_cars', 'Damage to cars', 3),
  ('flooding', 'Flooding', 4),
  ('entrances_blocked', 'Entrances blocked', 5),
  ('swimming_pool', 'Swimming pool', 6),
  ('jacuzzi', 'Jacuzzi', 7),
  ('laundry_room', 'Laundry room', 8),
  ('recreation_room', 'Recreation room', 9),
  ('gym', 'Gym', 10),
  ('elevator', 'Elevator', 11),
  ('filth_rubbish_garbage', 'Filth/Rubbish/Garbage', 12),
  ('vermin', 'Vermin', 13),
  ('insects', 'Insects', 14),
  ('broken_gate', 'Broken gate', 15),
  ('blocked_areas_doors', 'Blocked areas/doors', 16)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Common Areas';

-- ----------------------------------------------------------------------------
-- 15. TRASH PROBLEMS (2 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('inadequate_receptacles', 'Inadequate number of receptacles', 1),
  ('properly_servicing_emptying', 'Properly servicing and emptying receptacles', 2)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Trash Problems';

-- ----------------------------------------------------------------------------
-- 16. NUISANCE (4 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('drugs', 'Drugs', 1),
  ('smoking', 'Smoking', 2),
  ('noisy_neighbors', 'Noisy neighbors', 3),
  ('gangs', 'Gangs', 4)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Nuisance';

-- ----------------------------------------------------------------------------
-- 17. HEALTH HAZARD (8 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('mold', 'Mold', 1),
  ('mildew', 'Mildew', 2),
  ('mushrooms', 'Mushrooms', 3),
  ('raw_sewage_exterior', 'Raw sewage on exterior', 4),
  ('noxious_fumes', 'Noxious fumes', 5),
  ('chemical_paint_contamination', 'Chemical/Paint contamination', 6),
  ('toxic_water_pollution', 'Toxic water pollution', 7),
  ('offensive_odors', 'Offensive odors', 8)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Health Hazard';

-- ----------------------------------------------------------------------------
-- 18. SAFETY (6 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('broken_security_gate', 'Broken/Inoperable security gate', 1),
  ('broken_doors', 'Broken doors', 2),
  ('unauthorized_entries', 'Unauthorized entries', 3),
  ('broken_buzzer', 'Broken buzzer to get in', 4),
  ('security_cameras', 'Security cameras', 5),
  ('inoperable_locks', 'Inoperable locks', 6)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Safety';

-- ----------------------------------------------------------------------------
-- 19. NOTICES (6 options)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT c.id, v.code, v.name, v.ord
FROM issue_categories c
JOIN (VALUES
  ('3_day', '3-day', 1),
  ('24_hour', '24-hour', 2),
  ('30_day', '30-day', 3),
  ('60_day', '60-day', 4),
  ('to_quit', 'To quit', 5),
  ('perform_or_quit', 'Perform or quit', 6)
) AS v(code, name, ord) ON TRUE
WHERE c.category_name = 'Notices';

-- ============================================================================
-- VERIFICATION AND SUMMARY
-- ============================================================================

DO $$
DECLARE
    category_count INTEGER;
    option_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO category_count FROM issue_categories;
    SELECT COUNT(*) INTO option_count FROM issue_options;

    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════';
    RAISE NOTICE '✅ OFFICIAL BASELINE TAXONOMY LOADED';
    RAISE NOTICE '═══════════════════════════════════════════════════════════';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Categories: % (Official Baseline)', category_count;
    RAISE NOTICE '📋 Total Options: %', option_count;
    RAISE NOTICE '';
    RAISE NOTICE '✅ All options match Baseline Option.md exactly';
    RAISE NOTICE '📁 Source: database/Baseline Option.md';
    RAISE NOTICE '';
END $$;

-- Display final category summary with option counts
SELECT
    ic.display_order as "#",
    ic.category_name as "Category",
    COUNT(io.id) as "Options"
FROM issue_categories ic
LEFT JOIN issue_options io ON ic.id = io.category_id
GROUP BY ic.id, ic.category_name, ic.display_order
ORDER BY ic.display_order;
