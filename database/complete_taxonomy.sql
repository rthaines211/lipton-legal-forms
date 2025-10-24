-- ============================================================================
-- Complete Issue Taxonomy for Legal Form Application
-- This file seeds all issue categories and options that match the actual form
-- ============================================================================

-- Clear existing data
TRUNCATE TABLE party_issue_selections CASCADE;
TRUNCATE TABLE issue_options CASCADE;
TRUNCATE TABLE issue_categories CASCADE;

-- Insert ALL Issue Categories
INSERT INTO issue_categories (category_code, category_name, display_order, is_multi_select) VALUES
    ('vermin', 'Vermin Issues', 1, true),
    ('insects', 'Insect Issues', 2, true),
    ('hvac', 'HVAC Issues', 3, true),
    ('electrical', 'Electrical Issues', 4, true),
    ('fire_hazard', 'Fire Hazard Issues', 5, true),
    ('government', 'Government Entity Contacted', 6, true),
    ('plumbing', 'Plumbing Issues', 7, true),
    ('structure', 'Structure Issues', 8, true),
    ('flooring', 'Flooring Issues', 9, true),
    ('cabinets', 'Cabinets Issues', 10, true),
    ('doors', 'Door Issues', 11, true),
    ('windows', 'Windows Issues', 12, true),
    ('common_areas', 'Common Areas Issues', 13, true),
    ('trash', 'Trash Problems', 14, true),
    ('nuisance', 'Nuisance Issues', 15, true),
    ('health_hazard', 'Health Hazard Issues', 16, true),
    ('appliances', 'Appliance Issues', 17, true),
    ('harassment', 'Harassment Issues', 18, true),
    ('notices', 'Notices Issues', 19, true),
    ('utility', 'Utility Issues', 20, true),
    ('safety', 'Safety Issues', 21, true),
    ('direct_yesno', 'Direct Yes/No Issues', 22, true)
ON CONFLICT (category_code) DO NOTHING;

-- Insert Vermin Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'RatsMice', 'Rats/Mice', 1 FROM issue_categories WHERE category_code = 'vermin'
UNION ALL SELECT id, 'Skunks', 'Skunks', 2 FROM issue_categories WHERE category_code = 'vermin'
UNION ALL SELECT id, 'Bats', 'Bats', 3 FROM issue_categories WHERE category_code = 'vermin'
UNION ALL SELECT id, 'Raccoons', 'Raccoons', 4 FROM issue_categories WHERE category_code = 'vermin'
UNION ALL SELECT id, 'Pigeons', 'Pigeons', 5 FROM issue_categories WHERE category_code = 'vermin'
UNION ALL SELECT id, 'Opossums', 'Opossums', 6 FROM issue_categories WHERE category_code = 'vermin';

-- Insert Insect Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'Ants', 'Ants', 1 FROM issue_categories WHERE category_code = 'insects'
UNION ALL SELECT id, 'Roaches', 'Roaches', 2 FROM issue_categories WHERE category_code = 'insects'
UNION ALL SELECT id, 'Flies', 'Flies', 3 FROM issue_categories WHERE category_code = 'insects'
UNION ALL SELECT id, 'Bedbugs', 'Bedbugs', 4 FROM issue_categories WHERE category_code = 'insects'
UNION ALL SELECT id, 'Wasps', 'Wasps', 5 FROM issue_categories WHERE category_code = 'insects'
UNION ALL SELECT id, 'Hornets', 'Hornets', 6 FROM issue_categories WHERE category_code = 'insects'
UNION ALL SELECT id, 'Spiders', 'Spiders', 7 FROM issue_categories WHERE category_code = 'insects'
UNION ALL SELECT id, 'Termites', 'Termites', 8 FROM issue_categories WHERE category_code = 'insects'
UNION ALL SELECT id, 'Mosquitos', 'Mosquitos', 9 FROM issue_categories WHERE category_code = 'insects'
UNION ALL SELECT id, 'Bees', 'Bees', 10 FROM issue_categories WHERE category_code = 'insects';

-- Insert HVAC Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'AirConditioner', 'Air conditioner', 1 FROM issue_categories WHERE category_code = 'hvac'
UNION ALL SELECT id, 'Heater', 'Heater', 2 FROM issue_categories WHERE category_code = 'hvac'
UNION ALL SELECT id, 'Ventilation', 'Ventilation', 3 FROM issue_categories WHERE category_code = 'hvac';

-- Insert Electrical Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'Outlets', 'Outlets', 1 FROM issue_categories WHERE category_code = 'electrical'
UNION ALL SELECT id, 'Panel', 'Panel', 2 FROM issue_categories WHERE category_code = 'electrical'
UNION ALL SELECT id, 'WallSwitches', 'Wall switches', 3 FROM issue_categories WHERE category_code = 'electrical'
UNION ALL SELECT id, 'ExteriorLighting', 'Exterior lighting', 4 FROM issue_categories WHERE category_code = 'electrical'
UNION ALL SELECT id, 'InteriorLighting', 'Interior lighting', 5 FROM issue_categories WHERE category_code = 'electrical'
UNION ALL SELECT id, 'LightFixtures', 'Light fixtures', 6 FROM issue_categories WHERE category_code = 'electrical'
UNION ALL SELECT id, 'Fans', 'Fans', 7 FROM issue_categories WHERE category_code = 'electrical';

-- Insert Fire Hazard Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'SmokeAlarms', 'Smoke alarms', 1 FROM issue_categories WHERE category_code = 'fire_hazard'
UNION ALL SELECT id, 'FireExtinguisher', 'Fire extinguisher', 2 FROM issue_categories WHERE category_code = 'fire_hazard'
UNION ALL SELECT id, 'NonCompliantElectricity', 'Non-compliant electricity', 3 FROM issue_categories WHERE category_code = 'fire_hazard'
UNION ALL SELECT id, 'NonGFIOutlets', 'Non-GFI outlets near water', 4 FROM issue_categories WHERE category_code = 'fire_hazard'
UNION ALL SELECT id, 'CarbonMonoxideDetectors', 'Carbon monoxide detectors', 5 FROM issue_categories WHERE category_code = 'fire_hazard';

-- Insert Government Entity Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'HealthDepartment', 'Health department', 1 FROM issue_categories WHERE category_code = 'government'
UNION ALL SELECT id, 'HousingAuthority', 'Housing authority', 2 FROM issue_categories WHERE category_code = 'government'
UNION ALL SELECT id, 'CodeEnforcement', 'Code enforcement', 3 FROM issue_categories WHERE category_code = 'government'
UNION ALL SELECT id, 'FireDepartment', 'Fire department', 4 FROM issue_categories WHERE category_code = 'government'
UNION ALL SELECT id, 'PoliceDepartment', 'Police department', 5 FROM issue_categories WHERE category_code = 'government'
UNION ALL SELECT id, 'DeptEnvironmentalHealth', 'Department of environmental health', 6 FROM issue_categories WHERE category_code = 'government'
UNION ALL SELECT id, 'DeptHealthServices', 'Department of health services', 7 FROM issue_categories WHERE category_code = 'government';

-- Insert Plumbing Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'Toilet', 'Toilet', 1 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL SELECT id, 'InsufficientWaterPressure', 'Insufficient water pressure', 2 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL SELECT id, 'CloggedBath', 'Clogged bath', 3 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL SELECT id, 'CloggedShower', 'Clogged shower', 4 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL SELECT id, 'CloggedSinks', 'Clogged sinks', 5 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL SELECT id, 'CloggedToilets', 'Clogged toilets', 6 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL SELECT id, 'Bath', 'Bath', 7 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL SELECT id, 'Shower', 'Shower', 8 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL SELECT id, 'Fixtures', 'Fixtures', 9 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL SELECT id, 'Leaks', 'Leaks', 10 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL SELECT id, 'NoHotWater', 'No hot water', 11 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL SELECT id, 'NoColdWater', 'No cold water', 12 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL SELECT id, 'SewageComingOut', 'Sewage coming out', 13 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL SELECT id, 'NoCleanWaterSupply', 'No Clean Water Supply', 14 FROM issue_categories WHERE category_code = 'plumbing'
UNION ALL SELECT id, 'UnsanitaryWater', 'Unsanitary water', 15 FROM issue_categories WHERE category_code = 'plumbing';

-- Insert Structure Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'BumpsInCeiling', 'Bumps in ceiling', 1 FROM issue_categories WHERE category_code = 'structure'
UNION ALL SELECT id, 'HoleInCeiling', 'Hole in ceiling', 2 FROM issue_categories WHERE category_code = 'structure'
UNION ALL SELECT id, 'WaterStainsCeiling', 'Water stains on ceiling', 3 FROM issue_categories WHERE category_code = 'structure'
UNION ALL SELECT id, 'WaterStainsWall', 'Water stains on wall', 4 FROM issue_categories WHERE category_code = 'structure'
UNION ALL SELECT id, 'HoleInWall', 'Hole in wall', 5 FROM issue_categories WHERE category_code = 'structure'
UNION ALL SELECT id, 'Paint', 'Paint', 6 FROM issue_categories WHERE category_code = 'structure'
UNION ALL SELECT id, 'ExteriorDeckPorch', 'Exterior deck/porch', 7 FROM issue_categories WHERE category_code = 'structure'
UNION ALL SELECT id, 'WaterproofToilet', 'Waterproof toilet', 8 FROM issue_categories WHERE category_code = 'structure'
UNION ALL SELECT id, 'WaterproofTub', 'Waterproof tub', 9 FROM issue_categories WHERE category_code = 'structure'
UNION ALL SELECT id, 'Staircase', 'Staircase', 10 FROM issue_categories WHERE category_code = 'structure'
UNION ALL SELECT id, 'BasementFlood', 'Basement flood', 11 FROM issue_categories WHERE category_code = 'structure'
UNION ALL SELECT id, 'LeaksInGarage', 'Leaks in garage', 12 FROM issue_categories WHERE category_code = 'structure'
UNION ALL SELECT id, 'SoftSpotsLeaks', 'Soft spots due to leaks', 13 FROM issue_categories WHERE category_code = 'structure'
UNION ALL SELECT id, 'IneffectiveWaterproofing', 'Ineffective waterproofing of the tubs or toilet', 14 FROM issue_categories WHERE category_code = 'structure'
UNION ALL SELECT id, 'IneffectiveWeatherproofing', 'Ineffective Weatherproofing of any windows doors', 15 FROM issue_categories WHERE category_code = 'structure';

-- Insert Flooring Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'Uneven', 'Uneven', 1 FROM issue_categories WHERE category_code = 'flooring'
UNION ALL SELECT id, 'Carpet', 'Carpet', 2 FROM issue_categories WHERE category_code = 'flooring'
UNION ALL SELECT id, 'NailsStickingOut', 'Nails sticking out', 3 FROM issue_categories WHERE category_code = 'flooring'
UNION ALL SELECT id, 'Tiles', 'Tiles', 4 FROM issue_categories WHERE category_code = 'flooring';

-- Insert Cabinets Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'Broken', 'Broken', 1 FROM issue_categories WHERE category_code = 'cabinets'
UNION ALL SELECT id, 'Hinges', 'Hinges', 2 FROM issue_categories WHERE category_code = 'cabinets'
UNION ALL SELECT id, 'Alignment', 'Alignment', 3 FROM issue_categories WHERE category_code = 'cabinets';

-- Insert Door Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'Broken', 'Broken', 1 FROM issue_categories WHERE category_code = 'doors'
UNION ALL SELECT id, 'Knobs', 'Knobs', 2 FROM issue_categories WHERE category_code = 'doors'
UNION ALL SELECT id, 'Locks', 'Locks', 3 FROM issue_categories WHERE category_code = 'doors'
UNION ALL SELECT id, 'BrokenHinges', 'Broken hinges', 4 FROM issue_categories WHERE category_code = 'doors'
UNION ALL SELECT id, 'SlidingGlassDoors', 'Sliding glass doors', 5 FROM issue_categories WHERE category_code = 'doors'
UNION ALL SELECT id, 'IneffectiveWaterproofing', 'Ineffective waterproofing', 6 FROM issue_categories WHERE category_code = 'doors'
UNION ALL SELECT id, 'WaterIntrusionInsects', 'Water intrusion and/or insects', 7 FROM issue_categories WHERE category_code = 'doors'
UNION ALL SELECT id, 'DoNotCloseProperly', 'Do not close properly', 8 FROM issue_categories WHERE category_code = 'doors';

-- Insert Windows Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'Broken', 'Broken', 1 FROM issue_categories WHERE category_code = 'windows'
UNION ALL SELECT id, 'Screens', 'Screens', 2 FROM issue_categories WHERE category_code = 'windows'
UNION ALL SELECT id, 'Leaks', 'Leaks', 3 FROM issue_categories WHERE category_code = 'windows'
UNION ALL SELECT id, 'DoNotLock', 'Do not lock', 4 FROM issue_categories WHERE category_code = 'windows'
UNION ALL SELECT id, 'MissingWindows', 'Missing windows', 5 FROM issue_categories WHERE category_code = 'windows'
UNION ALL SELECT id, 'BrokenOrMissingScreens', 'Broken or missing screens', 6 FROM issue_categories WHERE category_code = 'windows';

-- Insert Common Areas Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'MailboxBroken', 'Mailbox broken', 1 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL SELECT id, 'ParkingAreaIssues', 'Parking area issues', 2 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL SELECT id, 'DamageToCars', 'Damage to cars', 3 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL SELECT id, 'Flooding', 'Flooding', 4 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL SELECT id, 'EntrancesBlocked', 'Entrances blocked', 5 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL SELECT id, 'SwimmingPool', 'Swimming pool', 6 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL SELECT id, 'Jacuzzi', 'Jacuzzi', 7 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL SELECT id, 'LaundryRoom', 'Laundry room', 8 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL SELECT id, 'RecreationRoom', 'Recreation room', 9 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL SELECT id, 'Gym', 'Gym', 10 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL SELECT id, 'Elevator', 'Elevator', 11 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL SELECT id, 'FilthRubbishGarbage', 'Filth/Rubbish/Garbage', 12 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL SELECT id, 'Vermin', 'Vermin', 13 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL SELECT id, 'Insects', 'Insects', 14 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL SELECT id, 'BrokenGate', 'Broken gate', 15 FROM issue_categories WHERE category_code = 'common_areas'
UNION ALL SELECT id, 'BlockedAreasDoors', 'Blocked areas/doors', 16 FROM issue_categories WHERE category_code = 'common_areas';

-- Insert Trash Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'InadequateReceptacles', 'Inadequate number of receptacles', 1 FROM issue_categories WHERE category_code = 'trash'
UNION ALL SELECT id, 'ImproperServicing', 'Improper servicing/emptying', 2 FROM issue_categories WHERE category_code = 'trash';

-- Insert Nuisance Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'Drugs', 'Drugs', 1 FROM issue_categories WHERE category_code = 'nuisance'
UNION ALL SELECT id, 'Smoking', 'Smoking', 2 FROM issue_categories WHERE category_code = 'nuisance'
UNION ALL SELECT id, 'NoisyNeighbors', 'Noisy neighbors', 3 FROM issue_categories WHERE category_code = 'nuisance'
UNION ALL SELECT id, 'Gangs', 'Gangs', 4 FROM issue_categories WHERE category_code = 'nuisance';

-- Insert Health Hazard Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'Mold', 'Mold', 1 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL SELECT id, 'Mildew', 'Mildew', 2 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL SELECT id, 'Mushrooms', 'Mushrooms', 3 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL SELECT id, 'RawSewageExterior', 'Raw sewage on exterior', 4 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL SELECT id, 'NoxiousFumes', 'Noxious fumes', 5 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL SELECT id, 'ChemicalPaint', 'Chemical/paint contamination', 6 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL SELECT id, 'ToxicWater', 'Toxic water pollution', 7 FROM issue_categories WHERE category_code = 'health_hazard'
UNION ALL SELECT id, 'OffensiveOdors', 'Offensive odors', 8 FROM issue_categories WHERE category_code = 'health_hazard';

-- Insert Appliance Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'Stove', 'Stove', 1 FROM issue_categories WHERE category_code = 'appliances'
UNION ALL SELECT id, 'Dishwasher', 'Dishwasher', 2 FROM issue_categories WHERE category_code = 'appliances'
UNION ALL SELECT id, 'WasherDryer', 'Washer/dryer', 3 FROM issue_categories WHERE category_code = 'appliances'
UNION ALL SELECT id, 'Oven', 'Oven', 4 FROM issue_categories WHERE category_code = 'appliances'
UNION ALL SELECT id, 'Microwave', 'Microwave', 5 FROM issue_categories WHERE category_code = 'appliances'
UNION ALL SELECT id, 'GarbageDisposal', 'Garbage disposal', 6 FROM issue_categories WHERE category_code = 'appliances'
UNION ALL SELECT id, 'Refrigerator', 'Refrigerator', 7 FROM issue_categories WHERE category_code = 'appliances';

-- Insert Harassment Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'UnlawfulDetainer', 'Unlawful detainer', 1 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL SELECT id, 'EvictionThreats', 'Eviction threats', 2 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL SELECT id, 'ByDefendant', 'By defendant', 3 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL SELECT id, 'ByMaintenance', 'By maintenance man/workers', 4 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL SELECT id, 'ByManager', 'By manager/building staff', 5 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL SELECT id, 'ByOwner', 'By owner', 6 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL SELECT id, 'OtherTenants', 'Other tenants', 7 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL SELECT id, 'IllegalNotices', 'Illegitimate notices', 8 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL SELECT id, 'RefusalRepairs', 'Refusal to make timely repairs', 9 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL SELECT id, 'WrittenThreats', 'Written threats', 10 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL SELECT id, 'AggressiveLanguage', 'Aggressive/inappropriate language', 11 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL SELECT id, 'PhysicalThreats', 'Physical threats or touching', 12 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL SELECT id, 'SingledOutNotices', 'Notices singling out one tenant, but not uniformly given to all tenants', 13 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL SELECT id, 'DuplicativeNotices', 'Duplicative notices', 14 FROM issue_categories WHERE category_code = 'harassment'
UNION ALL SELECT id, 'UntimelyResponse', 'Untimely response from landlord', 15 FROM issue_categories WHERE category_code = 'harassment';

-- Insert Notices Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, '3Day', '3-day', 1 FROM issue_categories WHERE category_code = 'notices'
UNION ALL SELECT id, '24Hour', '24-hour', 2 FROM issue_categories WHERE category_code = 'notices'
UNION ALL SELECT id, '30Day', '30-day', 3 FROM issue_categories WHERE category_code = 'notices'
UNION ALL SELECT id, '60Day', '60-day', 4 FROM issue_categories WHERE category_code = 'notices'
UNION ALL SELECT id, 'ToQuit', 'To quit', 5 FROM issue_categories WHERE category_code = 'notices'
UNION ALL SELECT id, 'PerformOrQuit', 'Perform or quit', 6 FROM issue_categories WHERE category_code = 'notices';

-- Insert Utility Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'GasLeak', 'Gas leak', 1 FROM issue_categories WHERE category_code = 'utility'
UNION ALL SELECT id, 'WaterShutoffs', 'Water shutoffs', 2 FROM issue_categories WHERE category_code = 'utility'
UNION ALL SELECT id, 'ElectricityShutoffs', 'Electricity shutoffs', 3 FROM issue_categories WHERE category_code = 'utility'
UNION ALL SELECT id, 'HeatShutoff', 'Heat shutoff', 4 FROM issue_categories WHERE category_code = 'utility'
UNION ALL SELECT id, 'GasShutoff', 'Gas shutoff', 5 FROM issue_categories WHERE category_code = 'utility';

-- Insert Safety Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'BrokenSecurityGate', 'Broken/inoperable security gate', 1 FROM issue_categories WHERE category_code = 'safety'
UNION ALL SELECT id, 'BrokenDoors', 'Broken doors', 2 FROM issue_categories WHERE category_code = 'safety'
UNION ALL SELECT id, 'UnauthorizedEntries', 'Unauthorized entries', 3 FROM issue_categories WHERE category_code = 'safety'
UNION ALL SELECT id, 'BrokenBuzzer', 'Broken buzzer to get in', 4 FROM issue_categories WHERE category_code = 'safety'
UNION ALL SELECT id, 'SecurityCameras', 'Security cameras', 5 FROM issue_categories WHERE category_code = 'safety'
UNION ALL SELECT id, 'InoperableLocks', 'Inoperable locks', 6 FROM issue_categories WHERE category_code = 'safety';

-- Insert Direct Yes/No Options
INSERT INTO issue_options (category_id, option_code, option_name, display_order)
SELECT id, 'InjuryIssues', 'Injury Issues', 1 FROM issue_categories WHERE category_code = 'direct_yesno'
UNION ALL SELECT id, 'NonresponsiveLandlord', 'Nonresponsive Landlord Issues', 2 FROM issue_categories WHERE category_code = 'direct_yesno'
UNION ALL SELECT id, 'UnauthorizedEntries', 'Unauthorized Entries', 3 FROM issue_categories WHERE category_code = 'direct_yesno'
UNION ALL SELECT id, 'StolenItems', 'Stolen Items', 4 FROM issue_categories WHERE category_code = 'direct_yesno'
UNION ALL SELECT id, 'DamagedItems', 'Damaged Items', 5 FROM issue_categories WHERE category_code = 'direct_yesno'
UNION ALL SELECT id, 'AgeDiscrimination', 'Age Discrimination', 6 FROM issue_categories WHERE category_code = 'direct_yesno'
UNION ALL SELECT id, 'RacialDiscrimination', 'Racial Discrimination', 7 FROM issue_categories WHERE category_code = 'direct_yesno'
UNION ALL SELECT id, 'DisabilityDiscrimination', 'Disability Discrimination', 8 FROM issue_categories WHERE category_code = 'direct_yesno'
UNION ALL SELECT id, 'SecurityDepositIssues', 'Security Deposit Issues', 9 FROM issue_categories WHERE category_code = 'direct_yesno';

-- Show results
SELECT
    ic.category_name,
    COUNT(io.id) as option_count
FROM issue_categories ic
LEFT JOIN issue_options io ON ic.id = io.category_id
GROUP BY ic.category_name, ic.display_order
ORDER BY ic.display_order;
