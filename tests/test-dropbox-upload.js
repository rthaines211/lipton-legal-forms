/**
 * Dropbox Upload Test Script
 *
 * Tests the Dropbox service by creating a sample file and uploading it.
 * This verifies that the Dropbox integration is working correctly.
 *
 * Prerequisites:
 * 1. Create a Dropbox app at https://www.dropbox.com/developers/apps
 * 2. Generate an access token
 * 3. Add DROPBOX_ACCESS_TOKEN to your .env file
 * 4. Set DROPBOX_ENABLED=true in your .env file
 *
 * Usage:
 *   node test-dropbox-upload.js
 */

require('dotenv').config();
const fs = require('fs').promises;
const path = require('path');
const dropboxService = require('./dropbox-service');

async function runTests() {
    console.log('='.repeat(70));
    console.log('🧪 Dropbox Upload Test Suite');
    console.log('='.repeat(70));
    console.log('');

    // Test 1: Check if Dropbox is enabled
    console.log('Test 1: Checking Dropbox service status...');
    const isEnabled = dropboxService.isEnabled();
    console.log(`   Dropbox enabled: ${isEnabled}`);
    console.log(`   Config:`, JSON.stringify(dropboxService.config, null, 2));
    console.log('');

    if (!isEnabled) {
        console.error('❌ Dropbox is not enabled. Please set DROPBOX_ENABLED=true and DROPBOX_ACCESS_TOKEN in your .env file.');
        console.log('');
        console.log('To enable Dropbox:');
        console.log('1. Go to https://www.dropbox.com/developers/apps');
        console.log('2. Create a new app or select an existing one');
        console.log('3. Generate an access token');
        console.log('4. Add to .env file:');
        console.log('   DROPBOX_ACCESS_TOKEN=your_token_here');
        console.log('   DROPBOX_ENABLED=true');
        return;
    }

    // Test 2: Get account info
    console.log('Test 2: Testing Dropbox connection...');
    try {
        const accountInfo = await dropboxService.getAccountInfo();
        console.log(`   ✅ Connected to Dropbox account: ${accountInfo.name.display_name}`);
        console.log(`   Email: ${accountInfo.email}`);
    } catch (error) {
        console.error(`   ❌ Failed to connect to Dropbox: ${error.message}`);
        return;
    }
    console.log('');

    // Test 3: Create test directory and file
    console.log('Test 3: Creating test file...');
    const testDir = path.join(__dirname, 'data', 'test-dropbox');
    const testFilePath = path.join(testDir, 'test-upload.json');

    try {
        await fs.mkdir(testDir, { recursive: true });
        const testData = {
            test: true,
            message: 'This is a test file for Dropbox upload',
            timestamp: new Date().toISOString(),
            randomId: Math.random().toString(36).substring(7)
        };
        await fs.writeFile(testFilePath, JSON.stringify(testData, null, 2));
        console.log(`   ✅ Created test file: ${testFilePath}`);
    } catch (error) {
        console.error(`   ❌ Failed to create test file: ${error.message}`);
        return;
    }
    console.log('');

    // Test 4: Test path mapping
    console.log('Test 4: Testing path mapping...');
    const dropboxPath = dropboxService.mapLocalPathToDropbox(testFilePath);
    console.log(`   Local path:   ${testFilePath}`);
    console.log(`   Dropbox path: ${dropboxPath}`);
    console.log('');

    // Test 5: Upload file to Dropbox
    console.log('Test 5: Uploading file to Dropbox...');
    try {
        const result = await dropboxService.uploadFile(testFilePath);
        if (result.success) {
            console.log(`   ✅ Upload successful!`);
            console.log(`   Local path:   ${result.localPath}`);
            console.log(`   Dropbox path: ${result.dropboxPath}`);
        } else {
            console.error(`   ❌ Upload failed: ${result.error}`);
        }
    } catch (error) {
        console.error(`   ❌ Upload error: ${error.message}`);
    }
    console.log('');

    // Test 6: Upload multiple files
    console.log('Test 6: Testing batch upload...');
    const testFiles = [];
    for (let i = 1; i <= 3; i++) {
        const filePath = path.join(testDir, `test-batch-${i}.json`);
        testFiles.push(filePath);
        await fs.writeFile(filePath, JSON.stringify({ batch: i, timestamp: new Date().toISOString() }, null, 2));
    }
    console.log(`   Created ${testFiles.length} test files`);

    try {
        const results = await dropboxService.uploadFiles(testFiles);
        const successCount = results.filter(r => r.success).length;
        console.log(`   ✅ Uploaded ${successCount}/${testFiles.length} files successfully`);
        results.forEach((r, i) => {
            if (r.success) {
                console.log(`      ${i + 1}. ✅ ${path.basename(r.localPath)} → ${r.dropboxPath}`);
            } else {
                console.log(`      ${i + 1}. ❌ ${path.basename(r.localPath)} - ${r.error}`);
            }
        });
    } catch (error) {
        console.error(`   ❌ Batch upload error: ${error.message}`);
    }
    console.log('');

    // Cleanup
    console.log('Cleanup: Removing test files...');
    try {
        await fs.rm(testDir, { recursive: true, force: true });
        console.log('   ✅ Test files removed');
    } catch (error) {
        console.warn(`   ⚠️  Failed to remove test files: ${error.message}`);
    }

    console.log('');
    console.log('='.repeat(70));
    console.log('✅ Test suite completed!');
    console.log('='.repeat(70));
}

// Run tests
runTests().catch(error => {
    console.error('❌ Test suite failed:', error);
    process.exit(1);
});
