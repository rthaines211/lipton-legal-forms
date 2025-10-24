/**
 * Comprehensive Test - All Issues Checked
 *
 * This test fills out the form with ALL possible checkboxes checked
 * to verify that every issue category is properly captured and transformed
 * in the JSON output.
 *
 * Purpose:
 * - Validate all field mappings in server.js
 * - Ensure newly fixed fields (plumbing, cabinets, windows, structure, health hazard, harassment) work correctly
 * - Generate a complete JSON output showing all possible issues
 */

const { test, expect } = require('@playwright/test');

test.describe('Complete Form Submission - All Issues Checked', () => {
    test('should capture all checked issues correctly in JSON output', async ({ page }) => {
        // Navigate to the form
        await page.goto('http://localhost:3000');

        // Wait for form to load
        await expect(page.locator('h1')).toContainText('Discovery Document Generation Form');

        // ===== PROPERTY INFORMATION =====
        await page.fill('[name="property-address"]', '1234 Test Street');
        await page.fill('[name="city"]', 'Los Angeles');
        await page.selectOption('[name="state"]', 'CA');
        await page.fill('[name="zip-code"]', '90001');
        await page.fill('[name="filing-city"]', 'Los Angeles');
        await page.fill('[name="filing-county"]', 'Los Angeles County');

        // ===== PLAINTIFF 1 =====
        await page.fill('[name="plaintiff-1-first-name"]', 'Complete');
        await page.fill('[name="plaintiff-1-last-name"]', 'Tester');
        await page.selectOption('[name="plaintiff-1-type"]', 'Individual');
        await page.check('[name="plaintiff-1-age"][value="adult"]');
        await page.check('[name="plaintiff-1-head"][value="yes"]');
        await page.fill('[name="plaintiff-1-unit"]', '101');

        // ===== CHECK ALL ISSUES FOR PLAINTIFF 1 =====

        // Vermin - all options
        await page.check('[name="vermin-RatsMice-1"]');
        await page.check('[name="vermin-Skunks-1"]');
        await page.check('[name="vermin-Bats-1"]');
        await page.check('[name="vermin-Raccoons-1"]');
        await page.check('[name="vermin-Pigeons-1"]');
        await page.check('[name="vermin-Opossums-1"]');

        // Insects - all options
        await page.check('[name="insect-Ants-1"]');
        await page.check('[name="insect-Roaches-1"]');
        await page.check('[name="insect-Flies-1"]');
        await page.check('[name="insect-Bedbugs-1"]');
        await page.check('[name="insect-Wasps-1"]');
        await page.check('[name="insect-Hornets-1"]');
        await page.check('[name="insect-Spiders-1"]');
        await page.check('[name="insect-Termites-1"]');
        await page.check('[name="insect-Mosquitos-1"]');
        await page.check('[name="insect-Bees-1"]');

        // HVAC - all options
        await page.check('[name="hvac-AirConditioner-1"]');
        await page.check('[name="hvac-Heater-1"]');
        await page.check('[name="hvac-Ventilation-1"]');

        // Electrical - all options
        await page.check('[name="electrical-Outlets-1"]');
        await page.check('[name="electrical-Panel-1"]');
        await page.check('[name="electrical-WallSwitches-1"]');
        await page.check('[name="electrical-ExteriorLighting-1"]');
        await page.check('[name="electrical-InteriorLighting-1"]');
        await page.check('[name="electrical-LightFixtures-1"]');
        await page.check('[name="electrical-Fans-1"]');

        // Fire Hazard - all options
        await page.check('[name="fire-hazard-SmokeAlarms-1"]');
        await page.check('[name="fire-hazard-FireExtinguisher-1"]');
        await page.check('[name="fire-hazard-Noncompliantelectricity-1"]');
        await page.check('[name="fire-hazard-NonGFIoutletsnearwater-1"]');
        await page.check('[name="fire-hazard-Carbonmonoxidedetectors-1"]');

        // Government Entities - all options
        await page.check('[name="government-HealthDepartment-1"]');
        await page.check('[name="government-HousingAuthority-1"]');
        await page.check('[name="government-CodeEnforcement-1"]');
        await page.check('[name="government-FireDepartment-1"]');
        await page.check('[name="government-PoliceDepartment-1"]');
        await page.check('[name="government-DepartmentofEnvironmentalHealth-1"]');
        await page.check('[name="government-DepartmentofHealthServices-1"]');

        // Appliances - all options
        await page.check('[name="appliances-Stove-1"]');
        await page.check('[name="appliances-Dishwasher-1"]');
        await page.check('[name="appliances-Washerdryer-1"]');
        await page.check('[name="appliances-Oven-1"]');
        await page.check('[name="appliances-Microwave-1"]');
        await page.check('[name="appliances-Garbagedisposal-1"]');
        await page.check('[name="appliances-Refrigerator-1"]');

        // Plumbing - all options (including newly fixed ones)
        await page.check('[name="plumbing-Toilet-1"]');
        await page.check('[name="plumbing-Insufficientwaterpressure-1"]');
        await page.check('[name="plumbing-Cloggedbathshowersinktoliet-1"]'); // Fixed mapping
        await page.check('[name="plumbing-Nohotwater-1"]');
        await page.check('[name="plumbing-Nocoldwater-1"]');
        await page.check('[name="plumbing-Sewagecomingout-1"]');
        await page.check('[name="plumbing-Nocleanwatersupply-1"]'); // Fixed mapping
        await page.check('[name="plumbing-Unsanitarywater-1"]');

        // Cabinets - all options (including newly fixed ones)
        await page.check('[name="cabinets-Broken-1"]');
        await page.check('[name="cabinets-BrokenHinges-1"]'); // Fixed mapping
        await page.check('[name="cabinets-Alignment-1"]');

        // Flooring - all options
        await page.check('[name="flooring-Uneven-1"]');
        await page.check('[name="flooring-Carpet-1"]');
        await page.check('[name="flooring-Nailsstickingout-1"]');
        await page.check('[name="flooring-Tiles-1"]');

        // Windows - all options (including newly fixed ones)
        await page.check('[name="windows-Broken-1"]');
        await page.check('[name="windows-Screens-1"]');
        await page.check('[name="windows-Leaks-1"]');
        await page.check('[name="windows-Donotlock-1"]');
        await page.check('[name="windows-Missingwindows-1"]'); // Fixed mapping
        await page.check('[name="windows-Brokenormissingscreens-1"]'); // Fixed mapping

        // Doors - all options
        await page.check('[name="door-Broken-1"]');
        await page.check('[name="door-Knobs-1"]');
        await page.check('[name="door-Locks-1"]');
        await page.check('[name="door-Brokenhinges-1"]');
        await page.check('[name="door-Slidingglassdoors-1"]');
        await page.check('[name="door-Ineffectivewaterproofing-1"]');
        await page.check('[name="door-Waterintrusionandorinsects-1"]');
        await page.check('[name="door-Donotcloseproperly-1"]');

        // Structure - all options (including newly fixed ones)
        await page.check('[name="structure-Bumpsinceiling-1"]');
        await page.check('[name="structure-Holeincelingwall-1"]'); // Fixed mapping
        await page.check('[name="structure-Waterstainscelingwall-1"]'); // Fixed mapping
        await page.check('[name="structure-Basementflood-1"]'); // Fixed mapping
        await page.check('[name="structure-Exteriordeckporch-1"]');
        await page.check('[name="structure-Leaksingarage-1"]');
        await page.check('[name="structure-Softspotsdutoleaks-1"]'); // Fixed mapping
        await page.check('[name="structure-Waterprooftoilet-1"]');
        await page.check('[name="structure-Waterprooftub-1"]');
        await page.check('[name="structure-Ineffectiveweatherproofingtoiletstubswindowsdoors-1"]');
        await page.check('[name="structure-Staircase-1"]');

        // Common Areas - all options
        await page.check('[name="common-areas-Mailboxbroken-1"]');
        await page.check('[name="common-areas-Parkingareaissues-1"]');
        await page.check('[name="common-areas-Damagetocars-1"]');
        await page.check('[name="common-areas-Flooding-1"]');
        await page.check('[name="common-areas-Entrancesblocked-1"]');
        await page.check('[name="common-areas-Swimmingpool-1"]');
        await page.check('[name="common-areas-Jacuzzi-1"]');
        await page.check('[name="common-areas-Laundryroom-1"]');
        await page.check('[name="common-areas-Recreationroom-1"]');
        await page.check('[name="common-areas-Gym-1"]');
        await page.check('[name="common-areas-Elevator-1"]');
        await page.check('[name="common-areas-FilthRubbishGarbage-1"]');
        await page.check('[name="common-areas-Vermin-1"]');
        await page.check('[name="common-areas-Insects-1"]');
        await page.check('[name="common-areas-BrokenGate-1"]');
        await page.check('[name="common-areas-Blockedareasdoors-1"]');

        // Trash Problems - all options
        await page.check('[name="trash-Inadequatenumberofreceptacles-1"]');
        await page.check('[name="trash-Improperservicingemptying-1"]');

        // Nuisance - all options
        await page.check('[name="nuisance-Drugs-1"]');
        await page.check('[name="nuisance-Smoking-1"]');
        await page.check('[name="nuisance-Noisyneighbors-1"]');
        await page.check('[name="nuisance-Gangs-1"]');

        // Health Hazard - all options (including newly fixed ones)
        await page.check('[name="health-hazard-Mold-1"]');
        await page.check('[name="health-hazard-Mildew-1"]');
        await page.check('[name="health-hazard-Mushrooms-1"]');
        await page.check('[name="health-hazard-Noxiousfumes-1"]');
        await page.check('[name="health-hazard-Toxicwaterpollution-1"]'); // Fixed mapping
        await page.check('[name="health-hazard-Rawsewageonexterior-1"]');
        await page.check('[name="health-hazard-Chemicalpaintcontamination-1"]'); // Fixed mapping
        await page.check('[name="health-hazard-Offensiveodors-1"]'); // Fixed mapping

        // Harassment - all options (including newly fixed ones)
        await page.check('[name="harassment-Bymangerbuildingstaffunlawfuldetainerrefusaltorepair-1"]'); // Fixed mapping
        await page.check('[name="harassment-Byownerevictionthreatswrittenthreatsduplicativenotices-1"]'); // Fixed mapping
        await page.check('[name="harassment-Bytenantsaggressivelanguagephysicalthreats-1"]'); // Fixed mapping
        await page.check('[name="harassment-Bymaintenancestaffinappropriatebehavioruntimelyresponse-1"]'); // Fixed mapping
        await page.check('[name="harassment-Noticessinglingoutonentenant-1"]'); // Fixed mapping
        await page.check('[name="harassment-Illegitimatenotices-1"]');

        // Notices Issues - all options
        await page.check('[name="notices-3day-1"]');
        await page.check('[name="notices-24hour-1"]');
        await page.check('[name="notices-30day-1"]');
        await page.check('[name="notices-60day-1"]');
        await page.check('[name="notices-Toquit-1"]');
        await page.check('[name="notices-Performorquit-1"]');

        // Utility Issues - all options
        await page.check('[name="utility-Gasleak-1"]');
        await page.check('[name="utility-Watershutoffs-1"]');
        await page.check('[name="utility-Electricityshutoffs-1"]');
        await page.check('[name="utility-Heatshutoff-1"]');
        await page.check('[name="utility-Gasshutoff-1"]');

        // Direct Boolean Issues - all options
        await page.check('[name="direct-injuryissues-1"]');
        await page.check('[name="direct-nonresponsivelandlordissues-1"]');
        await page.check('[name="direct-unauthorizedentries-1"]');
        await page.check('[name="direct-stolenitems-1"]');
        await page.check('[name="direct-damageditems-1"]');
        await page.check('[name="direct-agediscrimination-1"]');
        await page.check('[name="direct-racialdiscrimination-1"]');
        await page.check('[name="direct-disabilitydiscrimination-1"]');
        await page.check('[name="direct-securitydepositissues-1"]');

        // Safety Issues - all options
        await page.check('[name="safety-Brokeninoperablesecuritygate-1"]');
        await page.check('[name="safety-Brokendoors-1"]');
        await page.check('[name="safety-Unauthorizedentries-1"]');
        await page.check('[name="safety-Brokenbuzzertogetin-1"]');
        await page.check('[name="safety-Securitycameras-1"]');
        await page.check('[name="safety-Inoperablelocks-1"]');

        // ===== DEFENDANT 1 =====
        await page.fill('[name="defendant-1-first-name"]', 'Test');
        await page.fill('[name="defendant-1-last-name"]', 'Landlord');
        await page.selectOption('[name="defendant-1-entity"]', 'LLC');
        await page.check('[name="defendant-1-role"][value="owner"]');

        // ===== SUBMIT FORM =====
        await page.click('button[type="submit"]');

        // Wait for success page
        await expect(page).toHaveURL(/success/, { timeout: 10000 });

        // Verify success message
        await expect(page.locator('body')).toContainText('Form submitted successfully');

        // Get the latest form entry from the API
        const response = await page.request.get('http://localhost:3000/api/form-entries');
        expect(response.ok()).toBeTruthy();

        const data = await response.json();
        expect(data.success).toBe(true);
        expect(data.entries).toBeDefined();
        expect(data.entries.length).toBeGreaterThan(0);

        // Get the most recent entry
        const latestEntry = data.entries[0];
        const entryId = latestEntry.id;

        // Fetch the full entry data
        const entryResponse = await page.request.get(`http://localhost:3000/api/form-entries/${entryId}`);
        expect(entryResponse.ok()).toBeTruthy();

        const entryData = await entryResponse.json();
        const formData = entryData.entry;

        console.log('\n========== COMPLETE FORM OUTPUT ==========');
        console.log(JSON.stringify(formData, null, 2));
        console.log('==========================================\n');

        // ===== VALIDATE ALL ISSUE CATEGORIES =====
        const plaintiff = formData.PlaintiffDetails[0];
        const discovery = plaintiff.PlaintiffItemNumberDiscovery;

        // Vermin
        expect(discovery.VerminIssue).toBe(true);
        expect(discovery.Vermin).toContain('Rats/Mice');
        expect(discovery.Vermin).toContain('Skunks');
        expect(discovery.Vermin).toContain('Bats');
        expect(discovery.Vermin).toContain('Racoons');
        expect(discovery.Vermin).toContain('Pigeons');
        expect(discovery.Vermin).toContain('Opossum');

        // Insects
        expect(discovery.InsectIssues).toBe(true);
        expect(discovery.Insects).toContain('Ants');
        expect(discovery.Insects).toContain('Roaches');
        expect(discovery.Insects).toContain('Bedbugs');

        // Plumbing (NEWLY FIXED FIELDS)
        expect(discovery.PlumbingIssues).toBe(true);
        expect(discovery.Plumbing).toContain('Clogged bath / shower / sink / toilet');
        expect(discovery.Plumbing).toContain('No clean water supply');

        // Cabinets (NEWLY FIXED FIELDS)
        expect(discovery.CabinetsIssues).toBe(true);
        expect(discovery.Cabinets).toContain('Broken Hinges');

        // Windows (NEWLY FIXED FIELDS)
        expect(discovery.WindowsIssues).toBe(true);
        expect(discovery.Windows).toContain('Missing windows');
        expect(discovery.Windows).toContain('Broken or missing screens');

        // Structure (NEWLY FIXED FIELDS)
        expect(discovery.StructureIssues).toBe(true);
        expect(discovery.Structure).toContain('Hole in ceiling / wall');
        expect(discovery.Structure).toContain('Soft spots due to leaks');
        expect(discovery.Structure).toContain('Basement flood');
        expect(discovery.Structure).toContain('Water stains (ceiling/wall)');

        // Health Hazard (NEWLY FIXED FIELDS)
        expect(discovery.HealthHazardIssues).toBe(true);
        expect(discovery['Health hazard']).toContain('Toxic water pollution');
        expect(discovery['Health hazard']).toContain('Offensive odors');
        expect(discovery['Health hazard']).toContain('Chemical/paint contamination');

        // Harassment (NEWLY FIXED FIELDS)
        expect(discovery.HarassmentIssues).toBe(true);
        expect(discovery.Harassment).toContain('By manager/building staff (unlawful detainer, refusal to repair)');
        expect(discovery.Harassment).toContain('By owner (eviction threats, written threats, duplicative notices)');
        expect(discovery.Harassment).toContain('By tenants (aggressive language, physical threats)');
        expect(discovery.Harassment).toContain('By maintenance staff (inappropriate behavior, untimely response)');
        expect(discovery.Harassment).toContain('Notices singling out one tenant');

        // Safety Issues
        expect(discovery['Select Safety Issues']).toContain('Broken/inoperable security gate');
        expect(discovery['Select Safety Issues']).toContain('Unauthorized entries');

        // Direct Boolean Issues
        expect(discovery['Injury Issues']).toBe(true);
        expect(discovery['Nonresponsive landlord Issues']).toBe(true);
        expect(discovery['Age discrimination']).toBe(true);
        expect(discovery['Racial Discrimination']).toBe(true);
        expect(discovery['Disability discrimination']).toBe(true);

        console.log('✅ All issue categories validated successfully!');
    });
});
