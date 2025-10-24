-- ============================================================================
-- Legal Form Application - Complete Discovery Taxonomy Seed Data
-- ============================================================================
-- This file contains the complete standardized taxonomy of discovery issues
-- All categories unified into a single structure including Notices and
-- Government Entities for consistent issue tracking across the application
-- ============================================================================

-- ============================================================================
-- CLEAR EXISTING DATA (optional - use with caution in production)
-- ============================================================================
-- TRUNCATE TABLE party_issue_selections CASCADE;
-- DELETE FROM issue_options;
-- DELETE FROM issue_categories;

-- ============================================================================
-- INSERT ISSUE CATEGORIES
-- ============================================================================
-- Using ON CONFLICT to make this script idempotent (safe to run multiple times)

INSERT INTO issue_categories (category_code, category_name, display_order, is_multi_select) VALUES
    ('vermin', 'Vermin', 1, true),
    ('insects', 'Insects', 2, true),
    ('hvac', 'HVAC', 3, true),
    ('electrical', 'Electrical', 4, true),
    ('fire_hazard', 'Fire Hazard', 5, true),
    ('appliances', 'Appliances', 6, true),
    ('plumbing', 'Plumbing', 7, true),
    ('cabinets', 'Cabinets', 8, true),
    ('flooring', 'Flooring', 9, true),
    ('windows', 'Windows', 10, true),
    ('doors', 'Doors', 11, true),
    ('structure', 'Structure', 12, true),
    ('common_areas', 'Common Areas', 13, true),
    ('trash_problems', 'Trash Problems', 14, true),
    ('nuisance', 'Nuisance', 15, true),
    ('health_hazard', 'Health Hazard', 16, true),
    ('safety', 'Safety', 17, true),
    ('notices', 'Notices', 18, true),
    ('government_entities', 'Government Entities', 19, true)
ON CONFLICT (category_code) DO UPDATE SET
    category_name = EXCLUDED.category_name,
    display_order = EXCLUDED.display_order,
    is_multi_select = EXCLUDED.is_multi_select;

-- ============================================================================
-- INSERT ISSUE OPTIONS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- VERMIN
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'rats_mice', 'Rats/Mice', 1 FROM issue_categories WHERE category_code = 'vermin'
UNION ALL
SELECT id, 'bedbugs', 'Bedbugs', 2 FROM issue_categories WHERE category_code = 'vermin'
UNION ALL
SELECT id, 'squirrels', 'Squirrels', 3 FROM issue_categories WHERE category_code = 'vermin'
UNION ALL
SELECT id, 'raccoons', 'Raccoons', 4 FROM issue_categories WHERE category_code = 'vermin'
UNION ALL
SELECT id, 'opossums', 'Opossums', 5 FROM issue_categories WHERE category_code = 'vermin'
UNION ALL
SELECT id, 'bats', 'Bats', 6 FROM issue_categories WHERE category_code = 'vermin'
UNION ALL
SELECT id, 'other_vermin', 'Other Vermin', 7 FROM issue_categories WHERE category_code = 'vermin'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- INSECTS
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'roaches', 'Roaches', 1 FROM issue_categories WHERE category_code = 'insects'
UNION ALL
SELECT id, 'ants', 'Ants', 2 FROM issue_categories WHERE category_code = 'insects'
UNION ALL
SELECT id, 'flies', 'Flies', 3 FROM issue_categories WHERE category_code = 'insects'
UNION ALL
SELECT id, 'mosquitoes', 'Mosquitoes', 4 FROM issue_categories WHERE category_code = 'insects'
UNION ALL
SELECT id, 'termites', 'Termites', 5 FROM issue_categories WHERE category_code = 'insects'
UNION ALL
SELECT id, 'wasps_bees', 'Wasps/Bees', 6 FROM issue_categories WHERE category_code = 'insects'
UNION ALL
SELECT id, 'fleas', 'Fleas', 7 FROM issue_categories WHERE category_code = 'insects'
UNION ALL
SELECT id, 'spiders', 'Spiders', 8 FROM issue_categories WHERE category_code = 'insects'
UNION ALL
SELECT id, 'other_insects', 'Other Insects', 9 FROM issue_categories WHERE category_code = 'insects'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- HVAC
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'no_heat', 'No Heat', 1 FROM issue_categories WHERE category_code = 'hvac'
UNION ALL
SELECT id, 'inadequate_heat', 'Inadequate Heat', 2 FROM issue_categories WHERE category_code = 'hvac'
UNION ALL
SELECT id, 'no_ac', 'No Air Conditioning', 3 FROM issue_categories WHERE category_code = 'hvac'
UNION ALL
SELECT id, 'inadequate_ac', 'Inadequate Air Conditioning', 4 FROM issue_categories WHERE category_code = 'hvac'
UNION ALL
SELECT id, 'broken_thermostat', 'Broken Thermostat', 5 FROM issue_categories WHERE category_code = 'hvac'
UNION ALL
SELECT id, 'poor_ventilation', 'Poor Ventilation', 6 FROM issue_categories WHERE category_code = 'hvac'
UNION ALL
SELECT id, 'hvac_noise', 'HVAC System Noise', 7 FROM issue_categories WHERE category_code = 'hvac'
UNION ALL
SELECT id, 'dirty_filters', 'Dirty/Unmaintained Filters', 8 FROM issue_categories WHERE category_code = 'hvac'
UNION ALL
SELECT id, 'other_hvac', 'Other HVAC Issues', 9 FROM issue_categories WHERE category_code = 'hvac'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- ELECTRICAL
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'no_power', 'No Power', 1 FROM issue_categories WHERE category_code = 'electrical'
UNION ALL
SELECT id, 'frequent_outages', 'Frequent Power Outages', 2 FROM issue_categories WHERE category_code = 'electrical'
UNION ALL
SELECT id, 'broken_outlets', 'Broken Outlets', 3 FROM issue_categories WHERE category_code = 'electrical'
UNION ALL
SELECT id, 'broken_switches', 'Broken Light Switches', 4 FROM issue_categories WHERE category_code = 'electrical'
UNION ALL
SELECT id, 'exposed_wiring', 'Exposed Wiring', 5 FROM issue_categories WHERE category_code = 'electrical'
UNION ALL
SELECT id, 'sparking_outlets', 'Sparking Outlets/Switches', 6 FROM issue_categories WHERE category_code = 'electrical'
UNION ALL
SELECT id, 'insufficient_outlets', 'Insufficient Outlets', 7 FROM issue_categories WHERE category_code = 'electrical'
UNION ALL
SELECT id, 'flickering_lights', 'Flickering Lights', 8 FROM issue_categories WHERE category_code = 'electrical'
UNION ALL
SELECT id, 'tripping_breakers', 'Frequently Tripping Breakers', 9 FROM issue_categories WHERE category_code = 'electrical'
UNION ALL
SELECT id, 'other_electrical', 'Other Electrical Issues', 10 FROM issue_categories WHERE category_code = 'electrical'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- FIRE HAZARD
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'no_smoke_detector', 'No Smoke Detector', 1 FROM issue_categories WHERE category_code = 'fire_hazard'
UNION ALL
SELECT id, 'broken_smoke_detector', 'Broken Smoke Detector', 2 FROM issue_categories WHERE category_code = 'fire_hazard'
UNION ALL
SELECT id, 'no_co_detector', 'No Carbon Monoxide Detector', 3 FROM issue_categories WHERE category_code = 'fire_hazard'
UNION ALL
SELECT id, 'broken_co_detector', 'Broken Carbon Monoxide Detector', 4 FROM issue_categories WHERE category_code = 'fire_hazard'
UNION ALL
SELECT id, 'no_fire_extinguisher', 'No Fire Extinguisher', 5 FROM issue_categories WHERE category_code = 'fire_hazard'
UNION ALL
SELECT id, 'blocked_fire_exits', 'Blocked Fire Exits', 6 FROM issue_categories WHERE category_code = 'fire_hazard'
UNION ALL
SELECT id, 'faulty_sprinklers', 'Faulty Sprinkler System', 7 FROM issue_categories WHERE category_code = 'fire_hazard'
UNION ALL
SELECT id, 'combustible_materials', 'Improper Storage of Combustible Materials', 8 FROM issue_categories WHERE category_code = 'fire_hazard'
UNION ALL
SELECT id, 'other_fire_hazard', 'Other Fire Hazards', 9 FROM issue_categories WHERE category_code = 'fire_hazard'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- APPLIANCES
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'broken_stove', 'Broken Stove/Oven', 1 FROM issue_categories WHERE category_code = 'appliances'
UNION ALL
SELECT id, 'broken_refrigerator', 'Broken Refrigerator', 2 FROM issue_categories WHERE category_code = 'appliances'
UNION ALL
SELECT id, 'broken_dishwasher', 'Broken Dishwasher', 3 FROM issue_categories WHERE category_code = 'appliances'
UNION ALL
SELECT id, 'broken_microwave', 'Broken Microwave', 4 FROM issue_categories WHERE category_code = 'appliances'
UNION ALL
SELECT id, 'broken_washer', 'Broken Washing Machine', 5 FROM issue_categories WHERE category_code = 'appliances'
UNION ALL
SELECT id, 'broken_dryer', 'Broken Dryer', 6 FROM issue_categories WHERE category_code = 'appliances'
UNION ALL
SELECT id, 'broken_water_heater', 'Broken Water Heater', 7 FROM issue_categories WHERE category_code = 'appliances'
UNION ALL
SELECT id, 'broken_garbage_disposal', 'Broken Garbage Disposal', 8 FROM issue_categories WHERE category_code = 'appliances'
UNION ALL
SELECT id, 'other_appliance', 'Other Appliance Issues', 9 FROM issue_categories WHERE category_code = 'appliances'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- PLUMBING
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'no_hot_water', 'No Hot Water', 1 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL
SELECT id, 'no_running_water', 'No Running Water', 2 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL
SELECT id, 'low_water_pressure', 'Low Water Pressure', 3 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL
SELECT id, 'leaking_pipes', 'Leaking Pipes', 4 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL
SELECT id, 'clogged_drains', 'Clogged Drains', 5 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL
SELECT id, 'toilet_not_working', 'Toilet Not Working', 6 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL
SELECT id, 'toilet_constantly_running', 'Toilet Constantly Running', 7 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL
SELECT id, 'leaking_faucets', 'Leaking Faucets', 8 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL
SELECT id, 'sewage_backup', 'Sewage Backup', 9 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL
SELECT id, 'rusty_water', 'Rusty/Discolored Water', 10 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL
SELECT id, 'frozen_pipes', 'Frozen Pipes', 11 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL
SELECT id, 'other_plumbing', 'Other Plumbing Issues', 12 FROM issue_categories WHERE category_code = 'plumbing'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- CABINETS
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'broken_cabinet_doors', 'Broken Cabinet Doors', 1 FROM issue_categories WHERE category_code = 'cabinets'
UNION ALL
SELECT id, 'missing_cabinet_doors', 'Missing Cabinet Doors', 2 FROM issue_categories WHERE category_code = 'cabinets'
UNION ALL
SELECT id, 'broken_hinges', 'Broken Hinges', 3 FROM issue_categories WHERE category_code = 'cabinets'
UNION ALL
SELECT id, 'broken_handles', 'Broken Handles/Knobs', 4 FROM issue_categories WHERE category_code = 'cabinets'
UNION ALL
SELECT id, 'damaged_shelving', 'Damaged Shelving', 5 FROM issue_categories WHERE category_code = 'cabinets'
UNION ALL
SELECT id, 'water_damaged_cabinets', 'Water Damaged Cabinets', 6 FROM issue_categories WHERE category_code = 'cabinets'
UNION ALL
SELECT id, 'pest_damage_cabinets', 'Pest Damage to Cabinets', 7 FROM issue_categories WHERE category_code = 'cabinets'
UNION ALL
SELECT id, 'other_cabinet', 'Other Cabinet Issues', 8 FROM issue_categories WHERE category_code = 'cabinets'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- FLOORING
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'damaged_flooring', 'Damaged Flooring', 1 FROM issue_categories WHERE category_code = 'flooring'
UNION ALL
SELECT id, 'loose_flooring', 'Loose Flooring', 2 FROM issue_categories WHERE category_code = 'flooring'
UNION ALL
SELECT id, 'uneven_floors', 'Uneven Floors', 3 FROM issue_categories WHERE category_code = 'flooring'
UNION ALL
SELECT id, 'holes_in_floor', 'Holes in Floor', 4 FROM issue_categories WHERE category_code = 'flooring'
UNION ALL
SELECT id, 'water_damaged_floor', 'Water Damaged Flooring', 5 FROM issue_categories WHERE category_code = 'flooring'
UNION ALL
SELECT id, 'carpet_stains', 'Severe Carpet Stains/Damage', 6 FROM issue_categories WHERE category_code = 'flooring'
UNION ALL
SELECT id, 'missing_tiles', 'Missing Tiles', 7 FROM issue_categories WHERE category_code = 'flooring'
UNION ALL
SELECT id, 'cracked_tiles', 'Cracked Tiles', 8 FROM issue_categories WHERE category_code = 'flooring'
UNION ALL
SELECT id, 'other_flooring', 'Other Flooring Issues', 9 FROM issue_categories WHERE category_code = 'flooring'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- WINDOWS
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'broken_windows', 'Broken Windows', 1 FROM issue_categories WHERE category_code = 'windows'
UNION ALL
SELECT id, 'cracked_windows', 'Cracked Windows', 2 FROM issue_categories WHERE category_code = 'windows'
UNION ALL
SELECT id, 'windows_wont_open', 'Windows Won''t Open', 3 FROM issue_categories WHERE category_code = 'windows'
UNION ALL
SELECT id, 'windows_wont_close', 'Windows Won''t Close/Lock', 4 FROM issue_categories WHERE category_code = 'windows'
UNION ALL
SELECT id, 'drafty_windows', 'Drafty Windows', 5 FROM issue_categories WHERE category_code = 'windows'
UNION ALL
SELECT id, 'missing_screens', 'Missing Window Screens', 6 FROM issue_categories WHERE category_code = 'windows'
UNION ALL
SELECT id, 'broken_window_locks', 'Broken Window Locks', 7 FROM issue_categories WHERE category_code = 'windows'
UNION ALL
SELECT id, 'water_leaks_windows', 'Water Leaks Around Windows', 8 FROM issue_categories WHERE category_code = 'windows'
UNION ALL
SELECT id, 'other_window', 'Other Window Issues', 9 FROM issue_categories WHERE category_code = 'windows'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- DOORS
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'broken_entry_door', 'Broken Entry Door', 1 FROM issue_categories WHERE category_code = 'doors'
UNION ALL
SELECT id, 'door_wont_lock', 'Door Won''t Lock', 2 FROM issue_categories WHERE category_code = 'doors'
UNION ALL
SELECT id, 'broken_door_lock', 'Broken Door Lock', 3 FROM issue_categories WHERE category_code = 'doors'
UNION ALL
SELECT id, 'missing_keys', 'Missing Keys', 4 FROM issue_categories WHERE category_code = 'doors'
UNION ALL
SELECT id, 'door_wont_close', 'Door Won''t Close Properly', 5 FROM issue_categories WHERE category_code = 'doors'
UNION ALL
SELECT id, 'broken_hinges_door', 'Broken Door Hinges', 6 FROM issue_categories WHERE category_code = 'doors'
UNION ALL
SELECT id, 'damaged_door_frame', 'Damaged Door Frame', 7 FROM issue_categories WHERE category_code = 'doors'
UNION ALL
SELECT id, 'drafty_doors', 'Drafty Doors', 8 FROM issue_categories WHERE category_code = 'doors'
UNION ALL
SELECT id, 'security_concerns_door', 'Security Concerns with Door', 9 FROM issue_categories WHERE category_code = 'doors'
UNION ALL
SELECT id, 'other_door', 'Other Door Issues', 10 FROM issue_categories WHERE category_code = 'doors'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- STRUCTURE
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'roof_leaks', 'Roof Leaks', 1 FROM issue_categories WHERE category_code = 'structure'
UNION ALL
SELECT id, 'ceiling_damage', 'Ceiling Damage', 2 FROM issue_categories WHERE category_code = 'structure'
UNION ALL
SELECT id, 'wall_damage', 'Wall Damage', 3 FROM issue_categories WHERE category_code = 'structure'
UNION ALL
SELECT id, 'holes_in_walls', 'Holes in Walls', 4 FROM issue_categories WHERE category_code = 'structure'
UNION ALL
SELECT id, 'cracks_in_walls', 'Cracks in Walls', 5 FROM issue_categories WHERE category_code = 'structure'
UNION ALL
SELECT id, 'foundation_issues', 'Foundation Issues', 6 FROM issue_categories WHERE category_code = 'structure'
UNION ALL
SELECT id, 'water_damage_structure', 'Water Damage (Structural)', 7 FROM issue_categories WHERE category_code = 'structure'
UNION ALL
SELECT id, 'mold_growth', 'Mold Growth', 8 FROM issue_categories WHERE category_code = 'structure'
UNION ALL
SELECT id, 'peeling_paint', 'Peeling/Chipping Paint', 9 FROM issue_categories WHERE category_code = 'structure'
UNION ALL
SELECT id, 'lead_paint', 'Lead Paint', 10 FROM issue_categories WHERE category_code = 'structure'
UNION ALL
SELECT id, 'asbestos', 'Asbestos', 11 FROM issue_categories WHERE category_code = 'structure'
UNION ALL
SELECT id, 'sagging_ceiling', 'Sagging Ceiling', 12 FROM issue_categories WHERE category_code = 'structure'
UNION ALL
SELECT id, 'structural_instability', 'Structural Instability', 13 FROM issue_categories WHERE category_code = 'structure'
UNION ALL
SELECT id, 'other_structural', 'Other Structural Issues', 14 FROM issue_categories WHERE category_code = 'structure'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- COMMON AREAS
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'broken_stairs', 'Broken/Unsafe Stairs', 1 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL
SELECT id, 'broken_railings', 'Broken Railings', 2 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL
SELECT id, 'poor_lighting_common', 'Poor Lighting', 3 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL
SELECT id, 'dirty_common_areas', 'Dirty/Unmaintained Common Areas', 4 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL
SELECT id, 'broken_elevator', 'Broken Elevator', 5 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL
SELECT id, 'broken_intercom', 'Broken Intercom/Buzzer System', 6 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL
SELECT id, 'broken_mailboxes', 'Broken Mailboxes', 7 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL
SELECT id, 'laundry_issues', 'Laundry Room Issues', 8 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL
SELECT id, 'parking_issues', 'Parking Issues', 9 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL
SELECT id, 'security_common_areas', 'Security Issues in Common Areas', 10 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL
SELECT id, 'other_common_area', 'Other Common Area Issues', 11 FROM issue_categories WHERE category_code = 'common_areas'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- TRASH PROBLEMS
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'overflowing_trash', 'Overflowing Trash', 1 FROM issue_categories WHERE category_code = 'trash_problems'
UNION ALL
SELECT id, 'no_trash_service', 'No Trash Service', 2 FROM issue_categories WHERE category_code = 'trash_problems'
UNION ALL
SELECT id, 'insufficient_bins', 'Insufficient Trash Bins', 3 FROM issue_categories WHERE category_code = 'trash_problems'
UNION ALL
SELECT id, 'trash_attracts_pests', 'Trash Attracting Pests', 4 FROM issue_categories WHERE category_code = 'trash_problems'
UNION ALL
SELECT id, 'illegal_dumping', 'Illegal Dumping on Property', 5 FROM issue_categories WHERE category_code = 'trash_problems'
UNION ALL
SELECT id, 'recycling_issues', 'Recycling Issues', 6 FROM issue_categories WHERE category_code = 'trash_problems'
UNION ALL
SELECT id, 'other_trash', 'Other Trash Issues', 7 FROM issue_categories WHERE category_code = 'trash_problems'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- NUISANCE
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'noise_disturbances', 'Noise Disturbances', 1 FROM issue_categories WHERE category_code = 'nuisance'
UNION ALL
SELECT id, 'neighbor_harassment', 'Neighbor Harassment', 2 FROM issue_categories WHERE category_code = 'nuisance'
UNION ALL
SELECT id, 'landlord_harassment', 'Landlord Harassment', 3 FROM issue_categories WHERE category_code = 'nuisance'
UNION ALL
SELECT id, 'illegal_entry', 'Illegal Entry by Landlord', 4 FROM issue_categories WHERE category_code = 'nuisance'
UNION ALL
SELECT id, 'privacy_violations', 'Privacy Violations', 5 FROM issue_categories WHERE category_code = 'nuisance'
UNION ALL
SELECT id, 'drug_activity', 'Drug Activity on Property', 6 FROM issue_categories WHERE category_code = 'nuisance'
UNION ALL
SELECT id, 'criminal_activity', 'Criminal Activity on Property', 7 FROM issue_categories WHERE category_code = 'nuisance'
UNION ALL
SELECT id, 'excessive_odors', 'Excessive Odors', 8 FROM issue_categories WHERE category_code = 'nuisance'
UNION ALL
SELECT id, 'other_nuisance', 'Other Nuisance Issues', 9 FROM issue_categories WHERE category_code = 'nuisance'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- HEALTH HAZARD
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'mold_health', 'Mold (Health Hazard)', 1 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL
SELECT id, 'lead_exposure', 'Lead Exposure', 2 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL
SELECT id, 'asbestos_exposure', 'Asbestos Exposure', 3 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL
SELECT id, 'radon', 'Radon', 4 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL
SELECT id, 'carbon_monoxide_leak', 'Carbon Monoxide Leak', 5 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL
SELECT id, 'gas_leak', 'Gas Leak', 6 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL
SELECT id, 'sewage_exposure', 'Sewage Exposure', 7 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL
SELECT id, 'contaminated_water', 'Contaminated Water', 8 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL
SELECT id, 'pest_infestation_health', 'Pest Infestation (Health Risk)', 9 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL
SELECT id, 'unsanitary_conditions', 'Unsanitary Conditions', 10 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL
SELECT id, 'allergen_exposure', 'Excessive Allergen Exposure', 11 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL
SELECT id, 'other_health_hazard', 'Other Health Hazards', 12 FROM issue_categories WHERE category_code = 'health_hazard'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- SAFETY
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'inadequate_locks', 'Inadequate Locks', 1 FROM issue_categories WHERE category_code = 'safety'
UNION ALL
SELECT id, 'no_deadbolt', 'No Deadbolt', 2 FROM issue_categories WHERE category_code = 'safety'
UNION ALL
SELECT id, 'broken_security_system', 'Broken Security System', 3 FROM issue_categories WHERE category_code = 'safety'
UNION ALL
SELECT id, 'inadequate_lighting', 'Inadequate Lighting', 4 FROM issue_categories WHERE category_code = 'safety'
UNION ALL
SELECT id, 'unsafe_stairs', 'Unsafe Stairs/Steps', 5 FROM issue_categories WHERE category_code = 'safety'
UNION ALL
SELECT id, 'trip_hazards', 'Trip Hazards', 6 FROM issue_categories WHERE category_code = 'safety'
UNION ALL
SELECT id, 'exposed_hazards', 'Exposed Hazardous Materials', 7 FROM issue_categories WHERE category_code = 'safety'
UNION ALL
SELECT id, 'broken_security_gates', 'Broken Security Gates/Doors', 8 FROM issue_categories WHERE category_code = 'safety'
UNION ALL
SELECT id, 'inadequate_fire_escape', 'Inadequate Fire Escape', 9 FROM issue_categories WHERE category_code = 'safety'
UNION ALL
SELECT id, 'dangerous_construction', 'Dangerous Construction/Repairs', 10 FROM issue_categories WHERE category_code = 'safety'
UNION ALL
SELECT id, 'other_safety', 'Other Safety Issues', 11 FROM issue_categories WHERE category_code = 'safety'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- NOTICES (Unified into taxonomy)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'verbal_notice', 'Verbal Notice to Landlord', 1 FROM issue_categories WHERE category_code = 'notices'
UNION ALL
SELECT id, 'written_notice', 'Written Notice to Landlord', 2 FROM issue_categories WHERE category_code = 'notices'
UNION ALL
SELECT id, 'email_notice', 'Email Notice to Landlord', 3 FROM issue_categories WHERE category_code = 'notices'
UNION ALL
SELECT id, 'certified_mail_notice', 'Certified Mail Notice', 4 FROM issue_categories WHERE category_code = 'notices'
UNION ALL
SELECT id, 'text_message_notice', 'Text Message Notice', 5 FROM issue_categories WHERE category_code = 'notices'
UNION ALL
SELECT id, 'portal_request', 'Online Portal Maintenance Request', 6 FROM issue_categories WHERE category_code = 'notices'
UNION ALL
SELECT id, 'emergency_notice', 'Emergency Notice', 7 FROM issue_categories WHERE category_code = 'notices'
UNION ALL
SELECT id, 'no_response_to_notice', 'No Response to Notice', 8 FROM issue_categories WHERE category_code = 'notices'
UNION ALL
SELECT id, 'landlord_aware_no_repair', 'Landlord Aware But No Repair', 9 FROM issue_categories WHERE category_code = 'notices'
UNION ALL
SELECT id, 'other_notice', 'Other Notice Type', 10 FROM issue_categories WHERE category_code = 'notices'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ----------------------------------------------------------------------------
-- GOVERNMENT ENTITIES (Unified into taxonomy)
-- ----------------------------------------------------------------------------
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'local_housing_authority', 'Local Housing Authority', 1 FROM issue_categories WHERE category_code = 'government_entities'
UNION ALL
SELECT id, 'housing_inspection_dept', 'Housing Inspection Department', 2 FROM issue_categories WHERE category_code = 'government_entities'
UNION ALL
SELECT id, 'code_enforcement', 'Code Enforcement', 3 FROM issue_categories WHERE category_code = 'government_entities'
UNION ALL
SELECT id, 'health_department', 'Health Department', 4 FROM issue_categories WHERE category_code = 'government_entities'
UNION ALL
SELECT id, 'building_dept', 'Building Department', 5 FROM issue_categories WHERE category_code = 'government_entities'
UNION ALL
SELECT id, 'fire_department', 'Fire Department', 6 FROM issue_categories WHERE category_code = 'government_entities'
UNION ALL
SELECT id, 'police_department', 'Police Department', 7 FROM issue_categories WHERE category_code = 'government_entities'
UNION ALL
SELECT id, 'legal_aid_services', 'Legal Aid Services', 8 FROM issue_categories WHERE category_code = 'government_entities'
UNION ALL
SELECT id, 'tenant_rights_org', 'Tenant Rights Organization', 9 FROM issue_categories WHERE category_code = 'government_entities'
UNION ALL
SELECT id, 'fair_housing_agency', 'Fair Housing Agency', 10 FROM issue_categories WHERE category_code = 'government_entities'
UNION ALL
SELECT id, 'housing_court', 'Housing Court', 11 FROM issue_categories WHERE category_code = 'government_entities'
UNION ALL
SELECT id, 'attorney_general', 'Attorney General Office', 12 FROM issue_categories WHERE category_code = 'government_entities'
UNION ALL
SELECT id, 'hud', 'HUD (Housing and Urban Development)', 13 FROM issue_categories WHERE category_code = 'government_entities'
UNION ALL
SELECT id, 'rent_board', 'Rent Board/Commission', 14 FROM issue_categories WHERE category_code = 'government_entities'
UNION ALL
SELECT id, 'other_government', 'Other Government Entity', 15 FROM issue_categories WHERE category_code = 'government_entities'
ON CONFLICT (category_id, option_code) DO UPDATE SET
    option_name = EXCLUDED.option_name,
    display_order = EXCLUDED.display_order;

-- ============================================================================
-- VERIFICATION QUERY
-- ============================================================================
-- Run this to verify all data loaded correctly:
/*
SELECT
    ic.category_name,
    ic.display_order,
    COUNT(io.id) as option_count
FROM issue_categories ic
LEFT JOIN issue_options io ON ic.id = io.category_id
GROUP BY ic.id, ic.category_name, ic.display_order
ORDER BY ic.display_order;
*/

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '✅ Discovery taxonomy seed data loaded successfully';
    RAISE NOTICE '📊 Categories: 19';
    RAISE NOTICE '📋 Total options: %', (SELECT COUNT(*) FROM issue_options);
END $$;
