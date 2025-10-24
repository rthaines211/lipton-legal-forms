/**
 * Progress Tracking Diagnostic Script
 *
 * This script tests the document generation progress tracking to identify
 * why the frontend isn't seeing incremental progress updates.
 */

const axios = require('axios');

async function testProgressTracking() {
    console.log('🔍 Testing Progress Tracking System\n');
    console.log('=' .repeat(60));

    // Test 1: Check if Python API is running
    console.log('\n1️⃣  Testing Python API health...');
    try {
        const health = await axios.get('http://localhost:8000/health');
        console.log('✅ Python API is running:', health.data);
    } catch (error) {
        console.error('❌ Python API is NOT running!');
        console.error('   Start it with: cd "normalization work" && source venv/bin/activate && uvicorn api.main:app --host 0.0.0.0 --port 8000');
        return;
    }

    // Test 2: Check Node.js server
    console.log('\n2️⃣  Testing Node.js server...');
    try {
        const health = await axios.get('http://localhost:3000/api/health');
        console.log('✅ Node.js server is running:', health.data);
    } catch (error) {
        console.error('❌ Node.js server is NOT running!');
        return;
    }

    // Test 3: Test progress endpoint with dummy data
    console.log('\n3️⃣  Testing progress endpoint...');
    try {
        const progress = await axios.get('http://localhost:8000/api/progress/test-case-123');
        console.log('✅ Progress endpoint responds:', progress.data);
        console.log('   Note: Shows 0/0 because no documents are being generated for this test case');
    } catch (error) {
        console.error('❌ Progress endpoint failed:', error.message);
    }

    // Test 4: Check if there's a recent case with progress
    console.log('\n4️⃣  Looking for recent submissions...');
    try {
        const entries = await axios.get('http://localhost:3000/api/form-entries');
        if (entries.data && entries.data.entries && entries.data.entries.length > 0) {
            const latest = entries.data.entries[0];
            console.log(`✅ Found ${entries.data.entries.length} submissions`);
            console.log(`   Latest submission ID: ${latest.id}`);
            console.log(`   Latest case ID: ${latest.dbCaseId || 'No DB ID'}`);

            if (latest.dbCaseId) {
                console.log(`\n   Checking progress for latest case...`);
                const progress = await axios.get(`http://localhost:8000/api/progress/${latest.dbCaseId}`);
                console.log(`   Progress data:`, progress.data);

                const pipelineStatus = await axios.get(`http://localhost:3000/api/pipeline-status/${latest.dbCaseId}`);
                console.log(`   Pipeline status:`, pipelineStatus.data);
            }
        } else {
            console.log('⚠️  No submissions found');
        }
    } catch (error) {
        console.error('❌ Failed to check submissions:', error.message);
    }

    console.log('\n' + '='.repeat(60));
    console.log('\n📋 DIAGNOSIS:');
    console.log('   If you see progress as 0/0, it means:');
    console.log('   - Progress data has already expired (it only lasts during generation)');
    console.log('   - OR the case_id is not being passed correctly to Python');
    console.log('\n💡 TO TEST LIVE:');
    console.log('   1. Open http://localhost:3000 in your browser');
    console.log('   2. Open browser DevTools console (F12)');
    console.log('   3. Open terminal where Node.js server is running');
    console.log('   4. Submit a form');
    console.log('   5. Watch BOTH consoles for these logs:');
    console.log('      - Server: "🚀 Starting document progress polling..."');
    console.log('      - Server: "🔄 Polling document progress..."');
    console.log('      - Server: "📊 Document progress: 1/32..."');
    console.log('      - Browser: "📄 Document generation progress: 1/32"');
    console.log('\n');
}

testProgressTracking().catch(console.error);
