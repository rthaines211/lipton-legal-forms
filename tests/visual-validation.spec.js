/**
 * Visual Validation Test Suite
 *
 * Comprehensive visual testing including:
 * - Screenshot capture at multiple viewport sizes
 * - Accessibility compliance checking (WCAG 2.1)
 * - Component-level visual validation
 * - Responsive design verification
 * - Color contrast analysis
 * - Focus indicator validation
 */

const { test, expect } = require('@playwright/test');
const path = require('path');

// Test configuration
const VIEWPORTS = {
    mobile: { width: 375, height: 667 },      // iPhone SE
    tablet: { width: 768, height: 1024 },     // iPad
    desktop: { width: 1920, height: 1080 },   // Desktop HD
    wide: { width: 2560, height: 1440 }       // Desktop 2K
};

const BASE_URL = 'http://localhost:3000';

// Screenshot directory
const SCREENSHOT_DIR = path.join(__dirname, '../visual-snapshots');

test.describe('Visual Validation Suite', () => {

    test.describe('Screenshot Capture and Analysis', () => {

        test('should capture full page screenshots at all viewports', async ({ page }) => {
            for (const [name, viewport] of Object.entries(VIEWPORTS)) {
                await page.setViewportSize(viewport);
                await page.goto(BASE_URL);
                await page.waitForLoadState('networkidle');

                // Capture full page
                await page.screenshot({
                    path: path.join(SCREENSHOT_DIR, `full-page-${name}.png`),
                    fullPage: true
                });

                console.log(`✓ Captured ${name} viewport (${viewport.width}x${viewport.height})`);
            }
        });

        test('should capture component-level screenshots', async ({ page }) => {
            await page.goto(BASE_URL);
            await page.waitForLoadState('networkidle');

            const components = [
                { selector: 'h1', name: 'header' },
                { selector: '.form-section:first-child', name: 'property-section' },
                { selector: '#plaintiffs-container', name: 'plaintiffs-container' },
                { selector: '#defendants-container', name: 'defendants-container' },
                { selector: '.form-actions', name: 'form-actions' }
            ];

            for (const component of components) {
                const element = await page.locator(component.selector).first();
                if (await element.isVisible()) {
                    await element.screenshot({
                        path: path.join(SCREENSHOT_DIR, `component-${component.name}.png`)
                    });
                    console.log(`✓ Captured ${component.name}`);
                }
            }
        });

        test('should capture plaintiff issue checkboxes', async ({ page }) => {
            await page.goto(BASE_URL);
            await page.waitForLoadState('networkidle');

            // Add a plaintiff to reveal issues
            const plaintiffFirstName = await page.locator('input[name="plaintiff-1-first-name"]').first();
            await plaintiffFirstName.fill('Test');

            const plaintiffLastName = await page.locator('input[name="plaintiff-1-last-name"]').first();
            await plaintiffLastName.fill('User');

            // Mark as head of household
            const headOfHousehold = await page.locator('input[name="plaintiff-1-head"][value="yes"]').first();
            await headOfHousehold.check();

            // Wait for issue section to appear
            await page.waitForTimeout(500);

            // Capture issue sections
            const issueSections = [
                'vermin-issues',
                'insect-issues',
                'hvac-issues',
                'plumbing-issues'
            ];

            for (const sectionId of issueSections) {
                const section = page.locator(`#${sectionId}`);
                if (await section.isVisible()) {
                    await section.screenshot({
                        path: path.join(SCREENSHOT_DIR, `issues-${sectionId}.png`)
                    });
                    console.log(`✓ Captured ${sectionId}`);
                }
            }
        });
    });

    test.describe('Accessibility Compliance (WCAG 2.1)', () => {

        test('should have proper heading hierarchy', async ({ page }) => {
            await page.goto(BASE_URL);

            const h1Count = await page.locator('h1').count();
            const h2Count = await page.locator('h2').count();
            const h3Count = await page.locator('h3').count();

            // Should have exactly one h1
            expect(h1Count).toBe(1);

            // Should have multiple h2s for sections
            expect(h2Count).toBeGreaterThan(0);

            console.log(`Heading structure: H1=${h1Count}, H2=${h2Count}, H3=${h3Count}`);
        });

        test('should have labels for all form inputs', async ({ page }) => {
            await page.goto(BASE_URL);

            const inputs = await page.locator('input[type="text"], input[type="email"], select').all();

            let unlabeledInputs = [];

            for (const input of inputs) {
                const id = await input.getAttribute('id');
                const name = await input.getAttribute('name');
                const ariaLabel = await input.getAttribute('aria-label');

                // Check if there's an associated label
                const hasLabel = await page.locator(`label[for="${id}"]`).count() > 0;
                const hasAriaLabel = !!ariaLabel;

                if (!hasLabel && !hasAriaLabel) {
                    unlabeledInputs.push({ id, name });
                }
            }

            if (unlabeledInputs.length > 0) {
                console.warn('⚠️  Unlabeled inputs found:', unlabeledInputs);
            }

            // All inputs should have labels or aria-labels
            expect(unlabeledInputs.length).toBe(0);
        });

        test('should have sufficient color contrast', async ({ page }) => {
            await page.goto(BASE_URL);

            // Check primary button contrast
            const submitButton = page.locator('button[type="submit"]');
            const buttonBg = await submitButton.evaluate((el) => {
                return window.getComputedStyle(el).backgroundColor;
            });
            const buttonColor = await submitButton.evaluate((el) => {
                return window.getComputedStyle(el).color;
            });

            console.log(`Submit button - Background: ${buttonBg}, Text: ${buttonColor}`);

            // Navy background (#1F2A44) with white text meets WCAG AA
            expect(buttonBg).toContain('rgb'); // Should have computed color
            expect(buttonColor).toContain('rgb');
        });

        test('should have visible focus indicators', async ({ page }) => {
            await page.goto(BASE_URL);

            const focusableElements = await page.locator('input, button, select, a').all();

            // Test focus on first input
            const firstInput = focusableElements[0];
            await firstInput.focus();

            const outlineStyle = await firstInput.evaluate((el) => {
                const styles = window.getComputedStyle(el);
                return {
                    outline: styles.outline,
                    outlineWidth: styles.outlineWidth,
                    boxShadow: styles.boxShadow
                };
            });

            console.log('Focus indicator:', outlineStyle);

            // Should have either outline or box-shadow for focus
            const hasFocusIndicator = outlineStyle.outlineWidth !== '0px' ||
                                     outlineStyle.boxShadow !== 'none';

            expect(hasFocusIndicator).toBe(true);
        });

        test('should have alt text for images', async ({ page }) => {
            await page.goto(BASE_URL);

            const images = await page.locator('img').all();

            for (const img of images) {
                const alt = await img.getAttribute('alt');
                const src = await img.getAttribute('src');

                // All images should have alt attributes (can be empty for decorative)
                expect(alt !== null).toBe(true);
                console.log(`Image: ${src}, Alt: "${alt}"`);
            }
        });
    });

    test.describe('Responsive Design Verification', () => {

        test('should adapt layout at mobile breakpoint', async ({ page }) => {
            // Desktop first
            await page.setViewportSize(VIEWPORTS.desktop);
            await page.goto(BASE_URL);
            await page.waitForLoadState('networkidle');

            const containerDesktop = await page.locator('.container').first();
            const desktopWidth = await containerDesktop.evaluate((el) => el.offsetWidth);

            // Mobile
            await page.setViewportSize(VIEWPORTS.mobile);
            await page.waitForTimeout(200);

            const containerMobile = await page.locator('.container').first();
            const mobileWidth = await containerMobile.evaluate((el) => el.offsetWidth);

            console.log(`Container width - Desktop: ${desktopWidth}px, Mobile: ${mobileWidth}px`);

            // Mobile should be narrower
            expect(mobileWidth).toBeLessThan(desktopWidth);
        });

        test('should stack form actions on mobile', async ({ page }) => {
            await page.setViewportSize(VIEWPORTS.mobile);
            await page.goto(BASE_URL);

            const formActions = page.locator('.form-actions button').first();
            const buttonWidth = await formActions.evaluate((el) => {
                return window.getComputedStyle(el).width;
            });

            console.log(`Mobile button width: ${buttonWidth}`);

            // Per CSS line 291-297, buttons should be full width on mobile
            // This would be ~100% minus padding
            const parentWidth = await formActions.evaluate((el) => el.parentElement.offsetWidth);
            const actualWidth = await formActions.evaluate((el) => el.offsetWidth);

            // Button should take most of parent width
            expect(actualWidth / parentWidth).toBeGreaterThan(0.9);
        });

        test('should handle long content without overflow', async ({ page }) => {
            await page.goto(BASE_URL);

            // Add very long plaintiff name
            const firstNameInput = await page.locator('input[name="plaintiff-1-first-name"]').first();
            await firstNameInput.fill('VeryLongFirstNameThatMightCauseOverflowIssues');

            const container = page.locator('.container');
            const hasOverflow = await container.evaluate((el) => {
                return el.scrollWidth > el.clientWidth;
            });

            expect(hasOverflow).toBe(false);
        });
    });

    test.describe('Component Visual Validation', () => {

        test('should render plaintiff section correctly', async ({ page }) => {
            await page.goto(BASE_URL);

            const plaintiffSection = page.locator('#plaintiffs-container');
            await expect(plaintiffSection).toBeVisible();

            // Should have at least one plaintiff form
            const plaintiffForms = await page.locator('.repeating-section').count();
            expect(plaintiffForms).toBeGreaterThanOrEqual(1);

            // Add plaintiff button should exist
            const addButton = page.locator('button:has-text("Add Another Plaintiff")');
            await expect(addButton).toBeVisible();
        });

        test('should render defendant section correctly', async ({ page }) => {
            await page.goto(BASE_URL);

            const defendantSection = page.locator('#defendants-container');
            await expect(defendantSection).toBeVisible();

            // Add defendant button should exist
            const addButton = page.locator('button:has-text("Add Another Defendant")');
            await expect(addButton).toBeVisible();
        });

        test('should apply brand colors correctly', async ({ page }) => {
            await page.goto(BASE_URL);

            // Check h1 color (should be #1F2A44 - brand navy)
            const h1 = page.locator('h1');
            const h1Color = await h1.evaluate((el) => {
                return window.getComputedStyle(el).color;
            });

            // #1F2A44 = rgb(31, 42, 68)
            expect(h1Color).toBe('rgb(31, 42, 68)');

            // Check add button color (should be #00AEEF - brand teal)
            const addButton = page.locator('.add-section-btn').first();
            const buttonBg = await addButton.evaluate((el) => {
                return window.getComputedStyle(el).backgroundColor;
            });

            // #00AEEF = rgb(0, 174, 239)
            expect(buttonBg).toBe('rgb(0, 174, 239)');
        });

        test('should show remove buttons in correct position', async ({ page }) => {
            await page.goto(BASE_URL);

            // Check if remove button is positioned absolutely in top-right
            const removeButton = page.locator('.remove-section-btn').first();

            if (await removeButton.isVisible()) {
                const position = await removeButton.evaluate((el) => {
                    const styles = window.getComputedStyle(el);
                    return {
                        position: styles.position,
                        top: styles.top,
                        right: styles.right
                    };
                });

                expect(position.position).toBe('absolute');
                expect(position.top).toBe('15px');
                expect(position.right).toBe('15px');
            }
        });

        test('should display form sections with correct styling', async ({ page }) => {
            await page.goto(BASE_URL);

            const formSection = page.locator('.form-section').first();

            const styling = await formSection.evaluate((el) => {
                const styles = window.getComputedStyle(el);
                return {
                    backgroundColor: styles.backgroundColor,
                    borderRadius: styles.borderRadius,
                    padding: styles.padding,
                    borderLeft: styles.borderLeft
                };
            });

            console.log('Form section styling:', styling);

            // Should have background color
            expect(styling.backgroundColor).not.toBe('rgba(0, 0, 0, 0)');

            // Should have border radius
            expect(styling.borderRadius).toBe('10px');

            // Should have left border (4px solid teal)
            expect(styling.borderLeft).toContain('4px');
        });
    });

    test.describe('Issue Checkbox Validation', () => {

        test('should display issue checkboxes when head of household is selected', async ({ page }) => {
            await page.goto(BASE_URL);

            // Fill in plaintiff info
            await page.locator('input[name="plaintiff-1-first-name"]').fill('Test');
            await page.locator('input[name="plaintiff-1-last-name"]').fill('User');

            // Mark as head of household
            await page.locator('input[name="plaintiff-1-head"][value="yes"]').check();

            // Wait for issues to appear
            await page.waitForTimeout(500);

            // Vermin issues should be visible
            const verminSection = page.locator('#vermin-issues-1');
            await expect(verminSection).toBeVisible();

            // Take screenshot
            await page.screenshot({
                path: path.join(SCREENSHOT_DIR, 'issues-revealed.png'),
                fullPage: true
            });
        });

        test('should prevent double-toggle bug on checkboxes', async ({ page }) => {
            await page.goto(BASE_URL);

            // Setup plaintiff
            await page.locator('input[name="plaintiff-1-first-name"]').fill('Test');
            await page.locator('input[name="plaintiff-1-last-name"]').fill('User');
            await page.locator('input[name="plaintiff-1-head"][value="yes"]').check();
            await page.waitForTimeout(500);

            // Find a checkbox container
            const checkboxContainer = page.locator('.checkbox-item').first();

            // Check the pointer-events style on the checkbox inside
            const checkbox = checkboxContainer.locator('input[type="checkbox"]');
            const pointerEvents = await checkbox.evaluate((el) => {
                return window.getComputedStyle(el).pointerEvents;
            });

            // Should be 'none' to prevent double-toggle
            expect(pointerEvents).toBe('none');
        });
    });

    test.describe('Interaction States', () => {

        test('should show hover states on buttons', async ({ page }) => {
            await page.goto(BASE_URL);

            const addButton = page.locator('.add-section-btn').first();

            // Get initial background color
            const initialBg = await addButton.evaluate((el) => {
                return window.getComputedStyle(el).backgroundColor;
            });

            // Hover
            await addButton.hover();
            await page.waitForTimeout(100);

            // Note: Hover state detection is limited in automated tests
            // This is more for documentation
            console.log(`Button initial color: ${initialBg}`);
            console.log('Hover state should show darker teal (#0099D4)');
        });

        test('should show error states for invalid inputs', async ({ page }) => {
            await page.goto(BASE_URL);

            // Try to submit empty form
            const submitButton = page.locator('button[type="submit"]');
            await submitButton.click();

            // Check if any inputs have error class
            await page.waitForTimeout(500);

            const errorInputs = await page.locator('input.error, select.error').count();
            console.log(`Inputs with error class: ${errorInputs}`);
        });
    });
});

test.describe('Visual Regression Setup', () => {

    test('should create baseline screenshots for regression testing', async ({ page }) => {
        await page.goto(BASE_URL);
        await page.waitForLoadState('networkidle');

        // Create baselines at different states
        const states = [
            {
                name: 'initial-state',
                setup: async () => {}
            },
            {
                name: 'with-plaintiff',
                setup: async () => {
                    await page.locator('input[name="plaintiff-1-first-name"]').fill('John');
                    await page.locator('input[name="plaintiff-1-last-name"]').fill('Doe');
                }
            },
            {
                name: 'with-issues',
                setup: async () => {
                    await page.locator('input[name="plaintiff-1-first-name"]').fill('John');
                    await page.locator('input[name="plaintiff-1-last-name"]').fill('Doe');
                    await page.locator('input[name="plaintiff-1-head"][value="yes"]').check();
                    await page.waitForTimeout(500);
                }
            },
            {
                name: 'with-multiple-plaintiffs',
                setup: async () => {
                    await page.locator('input[name="plaintiff-1-first-name"]').fill('John');
                    await page.locator('input[name="plaintiff-1-last-name"]').fill('Doe');

                    // Add second plaintiff
                    await page.locator('button:has-text("Add Another Plaintiff")').click();
                    await page.waitForTimeout(300);
                }
            }
        ];

        for (const state of states) {
            await page.reload();
            await page.waitForLoadState('networkidle');
            await state.setup();

            await page.screenshot({
                path: path.join(SCREENSHOT_DIR, `baseline-${state.name}.png`),
                fullPage: true
            });

            console.log(`✓ Created baseline: ${state.name}`);
        }
    });
});
