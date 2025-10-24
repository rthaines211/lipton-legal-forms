/**
 * Form Completion E2E Tests
 *
 * These tests verify that the legal form can be filled out completely
 * and produces output that matches the expected goalOutput.md structure.
 */

import { test, expect } from '@playwright/test';

test.describe('Legal Form Completion', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to the form
    await page.goto('/');

    // Wait for the form to be fully loaded
    await expect(page.locator('#main-form')).toBeVisible();
  });

  test('should fill out complete form matching goalOutput.md structure', async ({ page }) => {
    // Fill out property information
    await page.fill('#property-address', '1331 Yorkshire Place NW');
    await page.fill('#apartment-unit', '');
    await page.fill('#city', 'Concord');
    await page.selectOption('#state', 'NC');
    await page.fill('#zip-code', '28027');
    await page.fill('#filing-city', 'Los Angeles');
    await page.fill('#filing-county', 'North Carolina');

    // Fill out first plaintiff (Clark Kent)
    await page.fill('input[name="plaintiff-1-first-name"]', 'Clark');
    await page.fill('input[name="plaintiff-1-last-name"]', 'Kent');
    await page.fill('input[name="plaintiff-1-type"]', 'Individual');
    await page.check('input[name="plaintiff-1-age"][value="adult"]');
    await page.check('input[name="plaintiff-1-head"][value="yes"]');

    // Wait for unit field to appear
    await expect(page.locator('input[name="plaintiff-1-unit"]')).toBeVisible();
    await page.fill('input[name="plaintiff-1-unit"]', '1');

    // Fill out plaintiff 1 issues - comprehensive selection matching goalOutput.md
    // Vermin issues
    await page.check('#vermin-RatsMice-1');
    await page.check('#vermin-Skunks-1');
    await page.check('#vermin-Bats-1');
    await page.check('#vermin-Raccoons-1');
    await page.check('#vermin-Pigeons-1');
    await page.check('#vermin-Opossums-1');

    // Insect issues
    await page.check('#insect-Ants-1');
    await page.check('#insect-Roaches-1');
    await page.check('#insect-Flies-1');
    await page.check('#insect-Bedbugs-1');
    await page.check('#insect-Wasps-1');
    await page.check('#insect-Hornets-1');
    await page.check('#insect-Spiders-1');
    await page.check('#insect-Termites-1');
    await page.check('#insect-Mosquitos-1');
    await page.check('#insect-Bees-1');

    // HVAC issues
    await page.check('#hvac-AirConditioner-1');
    await page.check('#hvac-Heater-1');
    await page.check('#hvac-Ventilation-1');

    // Electrical issues
    await page.check('#electrical-Outlets-1');
    await page.check('#electrical-Panel-1');
    await page.check('#electrical-WallSwitches-1');
    await page.check('#electrical-ExteriorLighting-1');
    await page.check('#electrical-InteriorLighting-1');
    await page.check('#electrical-LightFixtures-1');
    await page.check('#electrical-Fans-1');

    // Fire hazard issues
    await page.check('#fire-hazard-SmokeAlarms-1');
    await page.check('#fire-hazard-FireExtinguisher-1');
    await page.check('#fire-hazard-Noncompliantelectricity-1');
    await page.check('#fire-hazard-NonGFIoutletsnearwater-1');
    await page.check('#fire-hazard-Carbonmonoxidedetectors-1');

    // Government entities contacted
    await page.check('#government-HealthDepartment-1');
    await page.check('#government-HousingAuthority-1');
    await page.check('#government-CodeEnforcement-1');
    await page.check('#government-FireDepartment-1');
    await page.check('#government-PoliceDepartment-1');
    await page.check('#government-DepartmentofEnvironmentalHealth-1');
    await page.check('#government-DepartmentofHealthServices-1');

    // Appliances
    await page.check('#appliances-Stove-1');
    await page.check('#appliances-Dishwasher-1');
    await page.check('#appliances-Washerdryer-1');
    await page.check('#appliances-Oven-1');
    await page.check('#appliances-Microwave-1');
    await page.check('#appliances-Garbagedisposal-1');
    await page.check('#appliances-Refrigerator-1');

    // Plumbing
    await page.check('#plumbing-Toilet-1');
    await page.check('#plumbing-Shower-1');
    await page.check('#plumbing-Bath-1');
    await page.check('#plumbing-Fixtures-1');
    await page.check('#plumbing-Leaks-1');
    await page.check('#plumbing-Insufficientwaterpressure-1');
    await page.check('#plumbing-Nohotwater-1');
    await page.check('#plumbing-Nocoldwater-1');
    await page.check('#plumbing-Sewagecomingout-1');
    await page.check('#plumbing-Cloggedtoilets-1');
    await page.check('#plumbing-Cloggedbath-1');
    await page.check('#plumbing-Cloggedsinks-1');
    await page.check('#plumbing-Cloggedshower-1');
    await page.check('#plumbing-NoCleanWaterSupply-1');
    await page.check('#plumbing-Unsanitarywater-1');

    // Cabinets
    await page.check('#cabinets-Broken-1');
    await page.check('#cabinets-Hinges-1');
    await page.check('#cabinets-Alignment-1');

    // Flooring
    await page.check('#flooring-Uneven-1');
    await page.check('#flooring-Carpet-1');
    await page.check('#flooring-Nailsstickingout-1');
    await page.check('#flooring-Tiles-1');

    // Windows
    await page.check('#windows-Broken-1');
    await page.check('#windows-Screens-1');
    await page.check('#windows-Leaks-1');
    await page.check('#windows-Donotlock-1');
    await page.check('#windows-MissingWindows-1');
    await page.check('#windows-BrokenorMissingscreens-1');

    // Doors
    await page.check('#doors-Broken-1');
    await page.check('#doors-Knobs-1');
    await page.check('#doors-Locks-1');
    await page.check('#doors-Brokenhinges-1');
    await page.check('#doors-Slidingglassdoors-1');
    await page.check('#doors-Ineffectivewaterproofing-1');
    await page.check('#doors-Waterintrusionandorinsects-1');
    await page.check('#doors-DoNotCloseProperly-1');

    // Structure
    await page.check('#structure-Bumpsinceiling-1');
    await page.check('#structure-Holeinceiling-1');
    await page.check('#structure-Waterstainsonceiling-1');
    await page.check('#structure-Waterstainsonwall-1');
    await page.check('#structure-Holeinwall-1');
    await page.check('#structure-Paint-1');
    await page.check('#structure-Exteriordeckporch-1');
    await page.check('#structure-Waterprooftoilet-1');
    await page.check('#structure-Waterprooftub-1');
    await page.check('#structure-Staircase-1');
    await page.check('#structure-Basementflood-1');
    await page.check('#structure-Leaksingarage-1');
    await page.check('#structure-SoftSpotsduetoLeaks-1');
    await page.check('#structure-UneffectiveWaterproofingofthetubsortoilet-1');
    await page.check('#structure-IneffectiveWeatherproofingofanywindowsdoors-1');

    // Common areas
    await page.check('#common-areas-Mailboxbroken-1');
    await page.check('#common-areas-Parkingareaissues-1');
    await page.check('#common-areas-Damagetocars-1');
    await page.check('#common-areas-Flooding-1');
    await page.check('#common-areas-Entrancesblocked-1');
    await page.check('#common-areas-Swimmingpool-1');
    await page.check('#common-areas-Jacuzzi-1');
    await page.check('#common-areas-Laundryroom-1');
    await page.check('#common-areas-Recreationroom-1');
    await page.check('#common-areas-Gym-1');
    await page.check('#common-areas-Elevator-1');
    await page.check('#common-areas-FilthRubbishGarbage-1');
    await page.check('#common-areas-Vermin-1');
    await page.check('#common-areas-Insects-1');
    await page.check('#common-areas-BrokenGate-1');
    await page.check('#common-areas-Blockedareasdoors-1');

    // Trash problems
    await page.check('#trash-problems-Inadequatenumberofreceptacles-1');
    await page.check('#trash-problems-Properlyservicingandemmptyingreceptacles-1');

    // Nuisance
    await page.check('#nuisance-Drugs-1');
    await page.check('#nuisance-Smoking-1');
    await page.check('#nuisance-Noisyneighbors-1');
    await page.check('#nuisance-Gangs-1');

    // Health hazard
    await page.check('#health-hazard-Mold-1');
    await page.check('#health-hazard-Mildew-1');
    await page.check('#health-hazard-Mushrooms-1');
    await page.check('#health-hazard-Rawsewageonexterior-1');
    await page.check('#health-hazard-Noxiousfumes-1');
    await page.check('#health-hazard-Chemicalspaintcontamination-1');
    await page.check('#health-hazard-ToxicWaterPollution-1');
    await page.check('#health-hazard-OffensiveOdors-1');

    // Harassment
    await page.check('#harassment-UnlawfulDetainer-1');
    await page.check('#harassment-Evictionthreats-1');
    await page.check('#harassment-Bydefendant-1');
    await page.check('#harassment-Bymaintenancemanworkers-1');
    await page.check('#harassment-Bymanagerbuildingstaff-1');
    await page.check('#harassment-Byowner-1');
    await page.check('#harassment-Othertenants-1');
    await page.check('#harassment-Illegitimatenotices-1');
    await page.check('#harassment-Refusaltomakeimtelyrepairs-1');
    await page.check('#harassment-Writtenthreats-1');
    await page.check('#harassment-Aggressiveinappropriatelanguage-1');
    await page.check('#harassment-Physicalthreatsortouching-1');
    await page.check('#harassment-Noticessinglingoutonetenantbutnotuniformlygiventoalltenants-1');
    await page.check('#harassment-Duplicativenotices-1');
    await page.check('#harassment-UntimelyResponsefromLandlord-1');

    // Notices issues
    await page.check('#notices-issues-3day-1');
    await page.check('#notices-issues-24hour-1');
    await page.check('#notices-issues-30day-1');
    await page.check('#notices-issues-60day-1');
    await page.check('#notices-issues-Toquit-1');
    await page.check('#notices-issues-PerformorQuit-1');

    // Utility issues
    await page.check('#utility-issues-Gasleak-1');
    await page.check('#utility-issues-Watershutoffs-1');
    await page.check('#utility-issues-Electricityshutoffs-1');
    await page.check('#utility-issues-HeatShutoff-1');
    await page.check('#utility-issues-GasShutoff-1');

    // Direct boolean issues
    await page.check('#direct-injuryissues-1');
    await page.check('#direct-nonresponsivelandlordissues-1');
    await page.check('#direct-unauthorizedentries-1');
    await page.check('#direct-stolenitems-1');
    await page.check('#direct-damageditems-1');
    await page.check('#direct-agediscrimination-1');
    await page.check('#direct-racialdiscrimination-1');
    await page.check('#direct-disabilitydiscrimination-1');

    // Safety issues
    await page.check('#safety-issues-Brokeninoperablesecuritygate-1');
    await page.check('#safety-issues-Brokendoors-1');
    await page.check('#safety-issues-Unauthorizedentries-1');
    await page.check('#safety-issues-Brokenbuzzertogetin-1');
    await page.check('#safety-issues-Securitycameras-1');
    await page.check('#safety-issues-Inoperablelocks-1');

    // Security deposit
    await page.check('#direct-securitydepositissues-1');

    // Add second plaintiff (Lois Lane)
    await page.click('button[data-section="plaintiff"]');
    await page.fill('input[name="plaintiff-2-first-name"]', 'Lois');
    await page.fill('input[name="plaintiff-2-last-name"]', 'Lane');
    await page.fill('input[name="plaintiff-2-type"]', 'Guadrian');
    await page.check('input[name="plaintiff-2-age"][value="adult"]');
    await page.check('input[name="plaintiff-2-head"][value="yes"]');

    // Wait for unit field to appear
    await expect(page.locator('input[name="plaintiff-2-unit"]')).toBeVisible();
    await page.fill('input[name="plaintiff-2-unit"]', '2');

    // Fill out limited issues for plaintiff 2 (matching goalOutput.md)
    await page.check('#vermin-Skunks-2');
    await page.check('#vermin-Raccoons-2');
    await page.check('#insect-Flies-2');
    await page.check('#insect-Hornets-2');
    await page.check('#trash-problems-Inadequatenumberofreceptacles-2');

    // Add third plaintiff (Bruce Wayne)
    await page.click('button[data-section="plaintiff"]');
    await page.fill('input[name="plaintiff-3-first-name"]', 'Bruce');
    await page.fill('input[name="plaintiff-3-last-name"]', 'Wayne');
    await page.fill('input[name="plaintiff-3-type"]', 'Individual');
    await page.check('input[name="plaintiff-3-age"][value="adult"]');
    await page.check('input[name="plaintiff-3-head"][value="no"]');
    // No unit field appears since not head of household
    // No issues checked for plaintiff 3 (matching goalOutput.md)

    // Add first defendant (Tony Stark)
    await page.fill('input[name="defendant-1-first-name"]', 'Tony');
    await page.fill('input[name="defendant-1-last-name"]', 'Stark');
    await page.fill('input[name="defendant-1-entity"]', 'LLC');
    await page.check('input[name="defendant-1-role"][value="manager"]');

    // Add second defendant (Steve Rogers)
    await page.click('button[data-section="defendant"]');
    await page.fill('input[name="defendant-2-first-name"]', 'Steve');
    await page.fill('input[name="defendant-2-last-name"]', 'Rogers');
    await page.fill('input[name="defendant-2-entity"]', 'LLC');
    await page.check('input[name="defendant-2-role"][value="owner"]');

    // Submit the form
    await page.click('button[type="submit"]');

    // Wait for redirect to success page
    await expect(page).toHaveURL(/.*success.*/);

    // Get the entry ID from URL
    const url = page.url();
    const urlParams = new URLSearchParams(url.split('?')[1]);
    const entryId = urlParams.get('id');

    expect(entryId).toBeTruthy();

    // Wait a moment for the file to be written
    await page.waitForTimeout(1000);
  });

  test('should verify API returns structured data matching goalOutput.md', async ({ page, request }) => {
    // First, submit a simple form to get an entry ID
    await page.goto('/');

    await page.fill('#property-address', '1331 Yorkshire Place NW');
    await page.fill('#city', 'Concord');
    await page.selectOption('#state', 'NC');
    await page.fill('#zip-code', '28027');
    await page.fill('#filing-city', 'Los Angeles');
    await page.fill('#filing-county', 'North Carolina');

    await page.fill('input[name="plaintiff-1-first-name"]', 'Test');
    await page.fill('input[name="plaintiff-1-last-name"]', 'User');
    await page.fill('input[name="defendant-1-first-name"]', 'Test');
    await page.fill('input[name="defendant-1-last-name"]', 'Defendant');

    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*success.*/);

    const url = page.url();
    const urlParams = new URLSearchParams(url.split('?')[1]);
    const entryId = urlParams.get('id');

    // Wait for file to be written
    await page.waitForTimeout(1000);

    // Now test the API to verify structured data
    const apiResponse = await request.get(`/api/form-entries/${entryId}`);
    expect(apiResponse.ok()).toBeTruthy();

    const responseData = await apiResponse.json();
    expect(responseData.success).toBe(true);

    const structuredData = responseData.entry;

    // Verify the structure matches goalOutput.md format
    expect(structuredData.Form).toBeDefined();
    expect(structuredData.Form.Id).toBe("1");
    expect(structuredData.Form.InternalName).toBe("AutoPopulationForm");
    expect(structuredData.Form.Name).toBe("Auto-Population Form");

    expect(structuredData.PlaintiffDetails).toBeDefined();
    expect(Array.isArray(structuredData.PlaintiffDetails)).toBe(true);
    expect(structuredData.PlaintiffDetails_Minimum).toBe(1);

    expect(structuredData.DefendantDetails2).toBeDefined();
    expect(Array.isArray(structuredData.DefendantDetails2)).toBe(true);
    expect(structuredData.DefendantDetails2_Minimum).toBe(1);
    expect(structuredData.DefendantDetails2_Maximum).toBe(10);

    expect(structuredData.Full_Address).toBeDefined();
    expect(structuredData.Full_Address.Country).toBe("United States");
    expect(structuredData.Full_Address.CountryCode).toBe("US");
    expect(structuredData.Full_Address.Type).toBe("Home");

    // Verify plaintiff structure
    const firstPlaintiff = structuredData.PlaintiffDetails[0];
    expect(firstPlaintiff.Id).toBeDefined();
    expect(firstPlaintiff.PlaintiffItemNumberName).toBeDefined();
    expect(firstPlaintiff.PlaintiffItemNumberName.First).toBe("Test");
    expect(firstPlaintiff.PlaintiffItemNumberName.Last).toBe("User");
    expect(firstPlaintiff.PlaintiffItemNumberName.FirstAndLast).toBe("Test User");
    expect(firstPlaintiff.PlaintiffItemNumberType).toBeDefined();
    expect(firstPlaintiff.PlaintiffItemNumberAgeCategory).toBeDefined();
    expect(Array.isArray(firstPlaintiff.PlaintiffItemNumberAgeCategory)).toBe(true);
    expect(firstPlaintiff.PlaintiffItemNumberDiscovery).toBeDefined();
    expect(firstPlaintiff.HeadOfHousehold).toBeDefined();
    expect(firstPlaintiff.ItemNumber).toBe(1);

    // Verify discovery structure has all required fields
    const discovery = firstPlaintiff.PlaintiffItemNumberDiscovery;
    const requiredFields = [
      'VerminIssue', 'Vermin', 'InsectIssues', 'Insects', 'HVACIssues', 'HVAC',
      'Electrical', 'ElectricalIssues', 'FireHazardIssues', 'GovernmentEntityContacted',
      'AppliancesIssues', 'PlumbingIssues', 'CabinetsIssues', 'Fire Hazard',
      'Specific Government Entity Contacted', 'Appliances', 'Plumbing', 'Cabinets',
      'FlooringIssues', 'WindowsIssues', 'DoorIssues', 'Flooring', 'Windows', 'Doors',
      'StructureIssues', 'Structure', 'CommonAreasIssues', 'Common areas',
      'TrashProblems', 'Select Trash Problems', 'NuisanceIssues', 'Nuisance',
      'Health hazard', 'HealthHazardIssues', 'HarassmentIssues', 'Harassment',
      'NoticesIssues', 'Select Notices Issues', 'UtilityIssues', 'Checkbox 44n6i',
      'Injury Issues', 'Nonresponsive landlord Issues', 'Unauthorized entries',
      'Stolen items', 'Damaged items', 'Age discrimination', 'Racial Discrimination',
      'Disability discrimination', 'Unit', 'Safety', 'Select Safety Issues', 'Security Deposit'
    ];

    requiredFields.forEach(field => {
      expect(discovery).toHaveProperty(field);
    });

    // Verify defendant structure
    const firstDefendant = structuredData.DefendantDetails2[0];
    expect(firstDefendant.Id).toBeDefined();
    expect(firstDefendant.DefendantItemNumberName).toBeDefined();
    expect(firstDefendant.DefendantItemNumberName.First).toBe("Test");
    expect(firstDefendant.DefendantItemNumberName.Last).toBe("Defendant");
    expect(firstDefendant.DefendantItemNumberName.FirstAndLast).toBe("Test Defendant");
    expect(firstDefendant.DefendantItemNumberType).toBeDefined();
    expect(firstDefendant.DefendantItemNumberManagerOwner).toBeDefined();
    expect(firstDefendant.ItemNumber).toBe(1);
  });

  test('should handle form validation properly', async ({ page }) => {
    await page.goto('/');

    // Wait for form to initialize with default plaintiff and defendant
    await page.waitForTimeout(1000);

    // Try to submit form with empty required fields - HTML5 validation should prevent submission
    const submitButton = page.locator('button[type="submit"]');
    await submitButton.click();

    // The page should stay on the same URL due to HTML5 validation
    await page.waitForTimeout(500);
    expect(page.url()).toContain('localhost:3000');

    // Fill required fields
    await page.fill('#property-address', 'Test Address');
    await page.fill('#city', 'Test City');
    await page.selectOption('#state', 'CA');
    await page.fill('#zip-code', '90210');
    await page.fill('#filing-city', 'Test Filing City');
    await page.fill('#filing-county', 'Test County');

    await page.fill('input[name="plaintiff-1-first-name"]', 'John');
    await page.fill('input[name="plaintiff-1-last-name"]', 'Doe');

    await page.fill('input[name="defendant-1-first-name"]', 'Jane');
    await page.fill('input[name="defendant-1-last-name"]', 'Smith');

    // Now form should submit successfully (will show alert and reset form)
    // Handle the alert that appears after successful submission
    page.on('dialog', async dialog => {
      expect(dialog.message()).toContain('Form submitted successfully');
      await dialog.accept();
    });

    // Handle the confirmation dialog about resetting form
    page.on('dialog', async dialog => {
      if (dialog.message().includes('reset the form')) {
        await dialog.accept(); // Accept to reset form
      }
    });

    await submitButton.click();

    // Wait for submission to complete
    await page.waitForTimeout(2000);

    // Verify form was reset (should have empty required fields)
    const addressValue = await page.inputValue('#property-address');
    expect(addressValue).toBe('');
  });
});