/**
 * Audit Test: All Checkboxes Checked
 *
 * This test fills out the form with all checkboxes checked to audit
 * the visual appearance of the review/submission page.
 */

const { test, expect } = require('@playwright/test');

test('audit form submission with all checkboxes checked', async ({ page }) => {
    // Navigate to the form
    await page.goto('http://localhost:3000');

    // Wait for form to load
    await expect(page.locator('h1')).toContainText('Legal Form');

    // Fill property information
    await page.fill('#property-address', '123 Test Street');
    await page.fill('#apartment-unit', 'Apt 4B');
    await page.fill('#city', 'Boston');
    await page.fill('#state', 'MA');
    await page.fill('#zip-code', '02101');
    await page.fill('#filing-city', 'Boston');
    await page.fill('#filing-county', 'Suffolk County');

    // Fill plaintiff 1 information
    await page.fill('#plaintiff-1-first-name', 'John');
    await page.fill('#plaintiff-1-last-name', 'Doe');
    await page.selectOption('#plaintiff-1-type', 'Individual');
    await page.selectOption('#plaintiff-1-age', 'Adult');
    await page.selectOption('#plaintiff-1-head', 'Yes');
    await page.fill('#plaintiff-1-unit', '4B');

    // Check ALL issue checkboxes for plaintiff 1
    // We'll use a more robust approach - find all checkboxes and check them
    const allCheckboxes = await page.locator('input[type="checkbox"]').all();

    console.log(`Found ${allCheckboxes.length} checkboxes total`);

    // Check each checkbox
    for (const checkbox of allCheckboxes) {
        const isVisible = await checkbox.isVisible();
        const isEnabled = await checkbox.isEnabled();

        if (isVisible && isEnabled) {
            await checkbox.check();
        }
    }

    // Fill defendant 1 information
    await page.fill('#defendant-1-first-name', 'Jane');
    await page.fill('#defendant-1-last-name', 'Smith');
    await page.selectOption('#defendant-1-entity', 'Individual');
    await page.selectOption('#defendant-1-role', 'Owner');

    // Click Review button
    await page.click('button:has-text("Review Form")');

    // Wait for navigation to review page
    await page.waitForURL('**/review.html');

    // Take a screenshot of the entire review page
    await page.screenshot({
        path: 'test-results/review-all-checked-full.png',
        fullPage: true
    });

    // Verify we're on review page
    await expect(page.locator('h1')).toContainText('Review Your Submission');

    // Check that property info is displayed
    await expect(page.locator('#property-data')).toContainText('123 Test Street');

    // Check that plaintiff info is displayed
    await expect(page.locator('#plaintiffs-data')).toContainText('John');
    await expect(page.locator('#plaintiffs-data')).toContainText('Doe');

    // Check that defendant info is displayed
    await expect(page.locator('#defendants-data')).toContainText('Jane');
    await expect(page.locator('#defendants-data')).toContainText('Smith');

    // Take screenshot of just the plaintiffs section to see issues clearly
    const plaintiffsSection = page.locator('.section').filter({ hasText: 'Plaintiff Information' });
    await plaintiffsSection.screenshot({
        path: 'test-results/plaintiffs-section-all-checked.png'
    });

    // Log the number of issue categories displayed
    const issueCategories = await page.locator('.issues-category').count();
    console.log(`Number of issue categories displayed: ${issueCategories}`);

    // Log the total number of individual issues displayed
    const issueItems = await page.locator('.issue-list li').count();
    console.log(`Total individual issues displayed: ${issueItems}`);

    // Get all category titles to see what's displayed
    const categoryTitles = await page.locator('.category-title').allTextContents();
    console.log('Category titles:', categoryTitles);

    // Wait a moment for visual inspection
    await page.waitForTimeout(1000);

    console.log('✓ Review page loaded successfully with all checkboxes checked');
    console.log('✓ Screenshots saved to test-results/ directory');
});
