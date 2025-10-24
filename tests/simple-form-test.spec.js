/**
 * Simple Form Test - Basic functionality and structure verification
 *
 * This test focuses on the core form functionality without trying to
 * check every possible checkbox that may or may not exist in the form.
 */

import { test, expect } from '@playwright/test';

test.describe('Legal Form Basic Functionality', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('#main-form')).toBeVisible();
    await page.waitForTimeout(1000); // Wait for dynamic content to load
  });

  test('should load form correctly and have required elements', async ({ page }) => {
    // Check that main form sections are present
    await expect(page.locator('#property-address')).toBeVisible();
    await expect(page.locator('#city')).toBeVisible();
    await expect(page.locator('#state')).toBeVisible();
    await expect(page.locator('#zip-code')).toBeVisible();
    await expect(page.locator('#filing-city')).toBeVisible();
    await expect(page.locator('#filing-county')).toBeVisible();

    // Check that plaintiff and defendant sections exist
    await expect(page.locator('input[name="plaintiff-1-first-name"]')).toBeVisible();
    await expect(page.locator('input[name="plaintiff-1-last-name"]')).toBeVisible();
    await expect(page.locator('input[name="defendant-1-first-name"]')).toBeVisible();
    await expect(page.locator('input[name="defendant-1-last-name"]')).toBeVisible();

    // Check submit button exists
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should submit form and produce structured output', async ({ page, request }) => {
    // Fill out basic required information
    await page.fill('#property-address', '1331 Yorkshire Place NW');
    await page.fill('#city', 'Concord');
    await page.selectOption('#state', 'NC');
    await page.fill('#zip-code', '28027');
    await page.fill('#filing-city', 'Los Angeles');
    await page.fill('#filing-county', 'North Carolina');

    // Fill plaintiff information
    await page.fill('input[name="plaintiff-1-first-name"]', 'Clark');
    await page.fill('input[name="plaintiff-1-last-name"]', 'Kent');
    await page.fill('input[name="plaintiff-1-type"]', 'Individual');

    // Set as head of household to get unit field
    await page.check('input[name="plaintiff-1-head"][value="yes"]');
    await page.waitForTimeout(500); // Wait for unit field to appear
    await page.fill('input[name="plaintiff-1-unit"]', '1');

    // Fill defendant information
    await page.fill('input[name="defendant-1-first-name"]', 'Tony');
    await page.fill('input[name="defendant-1-last-name"]', 'Stark');
    await page.fill('input[name="defendant-1-entity"]', 'LLC');
    await page.check('input[name="defendant-1-role"][value="manager"]');

    // Skip checkbox testing for now - focus on core form functionality

    // Handle form submission dialogs
    const dialogMessages = [];
    page.on('dialog', async dialog => {
      dialogMessages.push(dialog.message());
      await dialog.accept();
    });

    // Submit form
    await page.click('button[type="submit"]');
    await page.waitForTimeout(3000); // Wait for submission to complete

    // Verify success dialog appeared
    expect(dialogMessages.some(msg => msg.includes('Form submitted successfully'))).toBe(true);

    // Extract entry ID from success message
    const successMessage = dialogMessages.find(msg => msg.includes('Entry ID:'));
    expect(successMessage).toBeTruthy();

    const entryId = successMessage.match(/Entry ID: ([\w-]+)/)?.[1];
    expect(entryId).toBeTruthy();

    // Wait for file to be written
    await page.waitForTimeout(1000);

    // Test API endpoint to verify structured data
    const apiResponse = await request.get(`/api/form-entries/${entryId}`);
    expect(apiResponse.ok()).toBeTruthy();

    const responseData = await apiResponse.json();
    expect(responseData.success).toBe(true);

    const structuredData = responseData.entry;

    // Verify basic structure matches goalOutput.md format
    expect(structuredData.Form).toBeDefined();
    expect(structuredData.Form.Id).toBe("1");
    expect(structuredData.Form.InternalName).toBe("AutoPopulationForm");
    expect(structuredData.Form.Name).toBe("Auto-Population Form");

    expect(structuredData.PlaintiffDetails).toBeDefined();
    expect(Array.isArray(structuredData.PlaintiffDetails)).toBe(true);
    expect(structuredData.PlaintiffDetails.length).toBeGreaterThan(0);

    expect(structuredData.DefendantDetails2).toBeDefined();
    expect(Array.isArray(structuredData.DefendantDetails2)).toBe(true);
    expect(structuredData.DefendantDetails2.length).toBeGreaterThan(0);

    expect(structuredData.Full_Address).toBeDefined();
    expect(structuredData.Full_Address.Country).toBe("United States");
    expect(structuredData.Full_Address.CountryCode).toBe("US");

    // Verify plaintiff data
    const plaintiff = structuredData.PlaintiffDetails[0];
    expect(plaintiff.PlaintiffItemNumberName.First).toBe("Clark");
    expect(plaintiff.PlaintiffItemNumberName.Last).toBe("Kent");
    expect(plaintiff.PlaintiffItemNumberName.FirstAndLast).toBe("Clark Kent");
    expect(plaintiff.PlaintiffItemNumberType).toBe("Individual");
    expect(plaintiff.HeadOfHousehold).toBe(true);
    expect(plaintiff.ItemNumber).toBe(1);

    // Verify discovery structure exists
    expect(plaintiff.PlaintiffItemNumberDiscovery).toBeDefined();
    const discovery = plaintiff.PlaintiffItemNumberDiscovery;

    // Check that all required discovery fields exist
    const requiredFields = [
      'VerminIssue', 'Vermin', 'InsectIssues', 'Insects', 'HVACIssues', 'HVAC',
      'ElectricalIssues', 'Electrical', 'FireHazardIssues', 'Fire Hazard',
      'GovernmentEntityContacted', 'Specific Government Entity Contacted',
      'AppliancesIssues', 'Appliances', 'PlumbingIssues', 'Plumbing',
      'CabinetsIssues', 'Cabinets', 'FlooringIssues', 'Flooring',
      'WindowsIssues', 'Windows', 'DoorIssues', 'Doors',
      'StructureIssues', 'Structure', 'CommonAreasIssues', 'Common areas',
      'TrashProblems', 'Select Trash Problems', 'NuisanceIssues', 'Nuisance',
      'HealthHazardIssues', 'Health hazard', 'HarassmentIssues', 'Harassment',
      'NoticesIssues', 'Select Notices Issues', 'UtilityIssues', 'Checkbox 44n6i',
      'Injury Issues', 'Nonresponsive landlord Issues', 'Unauthorized entries',
      'Stolen items', 'Damaged items', 'Age discrimination', 'Racial Discrimination',
      'Disability discrimination', 'Unit', 'Safety', 'Select Safety Issues', 'Security Deposit'
    ];

    requiredFields.forEach(field => {
      expect(discovery).toHaveProperty(field);
    });

    // Verify defendant data
    const defendant = structuredData.DefendantDetails2[0];
    expect(defendant.DefendantItemNumberName.First).toBe("Tony");
    expect(defendant.DefendantItemNumberName.Last).toBe("Stark");
    expect(defendant.DefendantItemNumberName.FirstAndLast).toBe("Tony Stark");
    expect(defendant.DefendantItemNumberType).toBe("LLC");
    expect(defendant.DefendantItemNumberManagerOwner).toBe("Manager");
    expect(defendant.ItemNumber).toBe(1);

    console.log('✅ Form submitted successfully and structure verified!');
    console.log('Entry ID:', entryId);
    console.log('Structured data preview:', JSON.stringify(structuredData, null, 2).substring(0, 500) + '...');
  });

  test('should add multiple plaintiffs and defendants', async ({ page }) => {
    // Fill basic info first
    await page.fill('#property-address', 'Test Address');
    await page.fill('#city', 'Test City');
    await page.selectOption('#state', 'CA');
    await page.fill('#zip-code', '90210');
    await page.fill('#filing-city', 'Test Filing City');
    await page.fill('#filing-county', 'Test County');

    // Fill first plaintiff
    await page.fill('input[name="plaintiff-1-first-name"]', 'Clark');
    await page.fill('input[name="plaintiff-1-last-name"]', 'Kent');

    // Add second plaintiff
    await page.click('button:has-text("Add Plaintiff")');
    await page.waitForTimeout(500);
    await page.fill('input[name="plaintiff-2-first-name"]', 'Lois');
    await page.fill('input[name="plaintiff-2-last-name"]', 'Lane');

    // Fill first defendant
    await page.fill('input[name="defendant-1-first-name"]', 'Tony');
    await page.fill('input[name="defendant-1-last-name"]', 'Stark');

    // Add second defendant
    await page.click('button:has-text("Add Defendant")');
    await page.waitForTimeout(500);
    await page.fill('input[name="defendant-2-first-name"]', 'Steve');
    await page.fill('input[name="defendant-2-last-name"]', 'Rogers');

    // Verify all fields are present
    await expect(page.locator('input[name="plaintiff-1-first-name"]')).toHaveValue('Clark');
    await expect(page.locator('input[name="plaintiff-2-first-name"]')).toHaveValue('Lois');
    await expect(page.locator('input[name="defendant-1-first-name"]')).toHaveValue('Tony');
    await expect(page.locator('input[name="defendant-2-first-name"]')).toHaveValue('Steve');

    console.log('✅ Multiple plaintiffs and defendants added successfully!');
  });
});