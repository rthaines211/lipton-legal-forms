/**
 * Direct Python API Test
 *
 * This tests if the Python normalization API can actually generate documents
 */

const axios = require('axios');

async function testPythonAPI() {
    console.log('🔍 Testing Python Normalization API\n');
    console.log('='.repeat(60));

    // Create minimal test data
    const testData = {
        case_id: 'test-' + Date.now(),
        property: {
            address: '123 Test St',
            city: 'Test City',
            state: 'CA',
            zip: '12345',
            filing_location: 'Test Court'
        },
        plaintiffs: [
            {
                id: 1,
                first_name: 'Test',
                last_name: 'User',
                type: 'Individual',
                age: 'adult',
                head_of_household: true,
                unit: '',
                issues: {
                    vermin_issue: true,
                    vermin: ['Rats/Mice']
                }
            }
        ],
        defendants: [
            {
                id: 1,
                first_name: 'Test',
                last_name: 'Landlord',
                entity: 'Individual',
                role: 'owner'
            }
        ]
    };

    console.log(`\n📝 Test Case ID: ${testData.case_id}`);
    console.log('\n🚀 Calling /api/normalize...\n');

    try {
        const startTime = Date.now();

        // Call the normalize endpoint
        const response = await axios.post('http://localhost:8000/api/normalize', testData, {
            timeout: 60000 // 60 second timeout
        });

        const duration = Date.now() - startTime;

        console.log(`✅ Pipeline completed in ${duration}ms\n`);
        console.log('Response:', JSON.stringify(response.data, null, 2));

        // Check if webhooks were sent
        if (response.data.webhook_summary) {
            console.log('\n📊 Webhook Summary:');
            console.log(`   Total documents: ${response.data.webhook_summary.total_sets}`);
            console.log(`   Succeeded: ${response.data.webhook_summary.succeeded}`);
            console.log(`   Failed: ${response.data.webhook_summary.failed}`);
        }

    } catch (error) {
        console.error('\n❌ Pipeline failed!');
        console.error('Error:', error.message);
        if (error.response) {
            console.error('Response status:', error.response.status);
            console.error('Response data:', JSON.stringify(error.response.data, null, 2));
        }
    }

    console.log('\n' + '='.repeat(60));
}

testPythonAPI().catch(console.error);
