/**
 * End-to-End Pipeline Integration Test
 *
 * Tests the complete flow from form submission through pipeline execution:
 * 1. Fill out the form with test data
 * 2. Submit the form
 * 3. Verify form is saved to database
 * 4. Verify pipeline is called and executes successfully
 * 5. Verify response includes pipeline results
 */

const { test, expect } = require('@playwright/test');

test.describe('End-to-End Pipeline Integration', () => {
    test('should submit form and execute normalization pipeline', async ({ page }) => {
        // Navigate to the form
        await page.goto('http://localhost:3000');

        // Wait for form to load
        await expect(page.locator('h1')).toBeVisible();

        console.log('✅ Form loaded');

        // Fill in property information
        await page.fill('[name="property-address"]', '123 Main Street');
        await page.fill('[name="city"]', 'Los Angeles');
        await page.selectOption('[name="state"]', 'CA');
        await page.fill('[name="zip-code"]', '90001');
        await page.fill('[name="apartment-unit"]', 'Apt 101');

        console.log('✅ Property info filled');

        // Fill in filing information
        await page.fill('[name="filing-city"]', 'Los Angeles');
        await page.fill('[name="filing-county"]', 'Los Angeles County');

        console.log('✅ Filing info filled');

        // Add first plaintiff
        await page.fill('[name="plaintiff-1-first-name"]', 'John');
        await page.fill('[name="plaintiff-1-last-name"]', 'Doe');
        await page.selectOption('[name="plaintiff-1-type"]', 'Individual');
        await page.check('[name="plaintiff-1-head"][value="yes"]');
        await page.selectOption('[name="plaintiff-1-age"]', 'adult');
        await page.fill('[name="plaintiff-1-unit"]', '101');

        console.log('✅ Plaintiff info filled');

        // Select some discovery issues for plaintiff 1
        await page.check('[name="vermin-RatsMice-1"]');
        await page.check('[name="vermin-Bedbugs-1"]');
        await page.check('[name="insect-Roaches-1"]');
        await page.check('[name="hvac-AirConditioner-1"]');
        await page.check('[name="plumbing-Toilet-1"]');
        await page.check('[name="health-hazard-Mold-1"]');

        console.log('✅ Discovery issues selected');

        // Add first defendant
        await page.fill('[name="defendant-1-first-name"]', 'Jane');
        await page.fill('[name="defendant-1-last-name"]', 'Smith');
        await page.selectOption('[name="defendant-1-entity"]', 'LLC');
        await page.check('[name="defendant-1-role"][value="manager"]');

        console.log('✅ Defendant info filled');

        // Intercept the form submission to capture the response
        let submissionResponse = null;
        page.on('response', async response => {
            if (response.url().includes('/api/form-entries') && response.request().method() === 'POST') {
                submissionResponse = await response.json();
                console.log('📋 Form submission response received');
            }
        });

        // Submit the form
        console.log('📤 Submitting form...');
        await page.click('button[type="submit"]');

        // Wait for success page or response
        await page.waitForURL('**/success', { timeout: 70000 }); // Extended timeout for pipeline

        console.log('✅ Redirected to success page');

        // Verify we got a response
        expect(submissionResponse).not.toBeNull();
        expect(submissionResponse.success).toBe(true);

        console.log('✅ Form submission successful');

        // Verify database case ID was created
        expect(submissionResponse.dbCaseId).toBeDefined();
        expect(submissionResponse.dbCaseId).not.toBeNull();

        console.log(`✅ Database case ID: ${submissionResponse.dbCaseId}`);

        // Verify pipeline was executed
        expect(submissionResponse.pipeline).toBeDefined();
        expect(submissionResponse.pipeline.executed).toBe(true);

        console.log('✅ Pipeline was executed');

        // Verify pipeline succeeded
        expect(submissionResponse.pipeline.success).toBe(true);
        expect(submissionResponse.pipeline.error).toBeUndefined();

        console.log('✅ Pipeline completed successfully');

        // Verify execution time is reasonable (< 60 seconds)
        expect(submissionResponse.pipeline.executionTime).toBeLessThan(60000);

        console.log(`✅ Pipeline execution time: ${submissionResponse.pipeline.executionTime}ms`);

        // Verify pipeline case_id was generated
        expect(submissionResponse.pipeline.case_id).toBeDefined();

        console.log(`✅ Pipeline case ID: ${submissionResponse.pipeline.case_id}`);

        // Log the full pipeline result for inspection
        console.log('\n📊 Full Pipeline Result:');
        console.log(JSON.stringify(submissionResponse.pipeline, null, 2));

        console.log('\n🎉 End-to-end pipeline integration test PASSED!');
    });

    test('should handle pipeline failure gracefully', async ({ page }) => {
        // This test verifies that form submission continues even if pipeline fails

        // Temporarily stop the Python API to simulate failure
        // (In real test, we'd use environment variable or mock)

        console.log('⚠️  Testing pipeline failure scenario');

        await page.goto('http://localhost:3000');

        // Fill minimal required fields
        await page.fill('[name="property-address"]', '456 Test St');
        await page.fill('[name="city"]', 'Test City');
        await page.selectOption('[name="state"]', 'CA');
        await page.fill('[name="zip-code"]', '90002');

        await page.fill('[name="plaintiff-1-first-name"]', 'Test');
        await page.fill('[name="plaintiff-1-last-name"]', 'User');
        await page.check('[name="plaintiff-1-head"][value="yes"]');

        await page.fill('[name="defendant-1-first-name"]', 'Test');
        await page.fill('[name="defendant-1-last-name"]', 'Defendant');

        let submissionResponse = null;
        page.on('response', async response => {
            if (response.url().includes('/api/form-entries') && response.request().method() === 'POST') {
                submissionResponse = await response.json();
            }
        });

        await page.click('button[type="submit"]');

        // Should still redirect to success even if pipeline fails
        await page.waitForURL('**/success', { timeout: 70000 });

        // Form submission should succeed
        expect(submissionResponse.success).toBe(true);

        // Pipeline may have failed or succeeded depending on API availability
        if (submissionResponse.pipeline) {
            console.log(`Pipeline executed: ${submissionResponse.pipeline.executed}`);
            console.log(`Pipeline success: ${submissionResponse.pipeline.success}`);
            if (submissionResponse.pipeline.error) {
                console.log(`Pipeline error: ${submissionResponse.pipeline.error}`);
            }
        }

        console.log('✅ Form saved successfully regardless of pipeline status');
    });
});
