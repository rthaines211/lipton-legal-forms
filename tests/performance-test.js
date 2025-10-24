/**
 * Performance Load Testing Script
 *
 * This k6 script tests the application under various load conditions.
 * It simulates realistic user behavior including form submissions and API calls.
 *
 * Performance Thresholds:
 * - 95% of requests should complete within 500ms
 * - 99% of requests should complete within 1000ms
 * - Error rate should be below 1%
 * - Throughput should handle 50+ concurrent users
 *
 * Usage:
 *   # Install k6 first
 *   brew install k6
 *
 *   # Run basic load test
 *   k6 run performance-test.js
 *
 *   # Run stress test
 *   k6 run --vus 100 --duration 5m performance-test.js
 *
 *   # Run with custom thresholds
 *   k6 run --vus 50 --duration 2m performance-test.js
 *
 * Reports:
 *   - Console output shows real-time metrics
 *   - HTML report: k6 run --out json=results.json performance-test.js
 *
 * @module PerformanceTest
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

/**
 * Custom Metrics
 */
const errorRate = new Rate('errors');
const pageLoadTime = new Trend('page_load_time');
const apiResponseTime = new Trend('api_response_time');
const formSubmissions = new Counter('form_submissions');

/**
 * Test Configuration
 *
 * Simulates realistic traffic patterns:
 * - Stage 1: Ramp up to 10 users over 30 seconds (warmup)
 * - Stage 2: Maintain 50 users for 2 minutes (steady state)
 * - Stage 3: Spike to 100 users for 1 minute (stress test)
 * - Stage 4: Ramp down to 0 over 30 seconds (cooldown)
 */
export let options = {
    stages: [
        { duration: '30s', target: 10 },   // Warmup
        { duration: '2m', target: 50 },    // Steady state
        { duration: '1m', target: 100 },   // Stress test
        { duration: '30s', target: 0 },    // Cooldown
    ],
    thresholds: {
        // 95% of requests should complete within 500ms
        'http_req_duration': ['p(95)<500'],
        // 99% of requests should complete within 1000ms
        'http_req_duration{name:page_load}': ['p(99)<1000'],
        // Error rate should be below 1%
        'errors': ['rate<0.01'],
        // API calls should respond within 300ms for 90% of requests
        'http_req_duration{name:api_call}': ['p(90)<300'],
    },
    // HTTP connection reuse for realistic browser behavior
    noConnectionReuse: false,
    // User agent
    userAgent: 'k6-performance-test/1.0',
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';

/**
 * Generate random form data for testing
 */
function generateFormData() {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(7);

    return {
        id: `${timestamp}-${random}`,
        submittedAt: new Date().toISOString(),

        // Property information
        'property-address': `${Math.floor(Math.random() * 9999)} Test St`,
        'apartment-unit': `Apt ${Math.floor(Math.random() * 100)}`,
        'city': 'Los Angeles',
        'state': 'CA',
        'zip-code': '90001',
        'filing-city': 'Los Angeles',
        'filing-county': 'Los Angeles County',

        // Plaintiff 1 (required)
        'plaintiff-1-first-name': `John${random}`,
        'plaintiff-1-last-name': `Doe${random}`,
        'plaintiff-1-type': 'Individual',
        'plaintiff-1-age': 'adult',
        'plaintiff-1-head': 'yes',
        'plaintiff-1-unit': 'Apt 101',

        // Add some issues for variety
        'vermin-RatsMice-1': 'on',
        'insect-Roaches-1': 'on',
        'hvac-AirConditioner-1': 'on',
        'plumbing-Toilet-1': 'on',

        // Defendant 1 (required)
        'defendant-1-first-name': `Jane${random}`,
        'defendant-1-last-name': `Smith${random}`,
        'defendant-1-entity': 'Individual',
        'defendant-1-role': 'owner',

        // Email notification
        notificationEmail: null,
        notificationEmailOptIn: false,
        notificationName: null
    };
}

/**
 * Test: Load Homepage
 */
function testPageLoad() {
    const startTime = Date.now();

    const res = http.get(BASE_URL, {
        tags: { name: 'page_load' }
    });

    const duration = Date.now() - startTime;
    pageLoadTime.add(duration);

    const checkResult = check(res, {
        'homepage loaded': (r) => r.status === 200,
        'page size < 300KB': (r) => r.body.length < 300000,
        'contains form element': (r) => r.body.includes('legal-form'),
    });

    errorRate.add(!checkResult);

    return res.status === 200;
}

/**
 * Test: Submit Form
 */
function testFormSubmission() {
    const formData = generateFormData();
    const startTime = Date.now();

    const res = http.post(
        `${BASE_URL}/api/form-entries`,
        JSON.stringify(formData),
        {
            headers: { 'Content-Type': 'application/json' },
            tags: { name: 'api_call' }
        }
    );

    const duration = Date.now() - startTime;
    apiResponseTime.add(duration);

    const checkResult = check(res, {
        'submission successful': (r) => r.status === 201,
        'response contains id': (r) => {
            try {
                const body = JSON.parse(r.body);
                return body.id !== undefined;
            } catch (e) {
                return false;
            }
        },
        'response time < 1s': (r) => r.timings.duration < 1000,
    });

    if (res.status === 201) {
        formSubmissions.add(1);
    }

    errorRate.add(!checkResult);

    return res.status === 201;
}

/**
 * Test: List Form Entries (GET API)
 */
function testListEntries() {
    const startTime = Date.now();

    const res = http.get(`${BASE_URL}/api/form-entries`, {
        tags: { name: 'api_call' }
    });

    const duration = Date.now() - startTime;
    apiResponseTime.add(duration);

    const checkResult = check(res, {
        'list entries successful': (r) => r.status === 200,
        'response is JSON': (r) => {
            try {
                JSON.parse(r.body);
                return true;
            } catch (e) {
                return false;
            }
        },
        'response time < 500ms': (r) => r.timings.duration < 500,
    });

    errorRate.add(!checkResult);

    return res.status === 200;
}

/**
 * Test: Health Check
 */
function testHealthCheck() {
    const res = http.get(`${BASE_URL}/api/health`, {
        tags: { name: 'api_call' }
    });

    const checkResult = check(res, {
        'health check passed': (r) => r.status === 200,
        'status is OK': (r) => {
            try {
                const body = JSON.parse(r.body);
                return body.status === 'OK';
            } catch (e) {
                return false;
            }
        },
        'response time < 100ms': (r) => r.timings.duration < 100,
    });

    errorRate.add(!checkResult);
}

/**
 * Main Test Scenario
 *
 * Simulates realistic user behavior:
 * 1. Load homepage
 * 2. Fill out form (simulated by wait time)
 * 3. Submit form
 * 4. View submissions list
 * 5. Random think time between actions
 */
export default function () {
    // Scenario 1: New user visits and submits form (70% of traffic)
    if (Math.random() < 0.7) {
        group('User Journey: Submit Form', () => {
            // Load homepage
            const pageLoaded = testPageLoad();
            sleep(Math.random() * 2 + 1); // Think time: 1-3 seconds

            if (pageLoaded) {
                // Simulate filling out form
                sleep(Math.random() * 5 + 5); // Fill form: 5-10 seconds

                // Submit form
                testFormSubmission();
                sleep(Math.random() * 2 + 1);
            }
        });
    }
    // Scenario 2: Admin views submissions (20% of traffic)
    else if (Math.random() < 0.9) {
        group('User Journey: View Submissions', () => {
            testListEntries();
            sleep(Math.random() * 3 + 2);
        });
    }
    // Scenario 3: Health check monitoring (10% of traffic)
    else {
        group('System: Health Check', () => {
            testHealthCheck();
            sleep(1);
        });
    }

    // Random think time between iterations
    sleep(Math.random() * 2 + 1);
}

/**
 * Setup function - runs once before all iterations
 */
export function setup() {
    console.log(`🚀 Starting performance test against ${BASE_URL}`);
    console.log('📊 Simulating realistic user traffic patterns...\n');

    // Verify server is running
    const res = http.get(`${BASE_URL}/api/health`);
    if (res.status !== 200) {
        throw new Error(`Server not available at ${BASE_URL}. Please start the server first.`);
    }

    return { startTime: Date.now() };
}

/**
 * Teardown function - runs once after all iterations
 */
export function teardown(data) {
    const duration = (Date.now() - data.startTime) / 1000;
    console.log(`\n✅ Performance test completed in ${duration.toFixed(2)} seconds`);
}

/**
 * Handle summary - custom summary output
 */
export function handleSummary(data) {
    console.log('\n📈 Performance Summary:');
    console.log('='.repeat(60));

    const metrics = data.metrics;

    // HTTP metrics
    if (metrics.http_req_duration) {
        console.log('\n⏱️  Response Times:');
        console.log(`   Average:     ${metrics.http_req_duration.values.avg.toFixed(2)}ms`);
        console.log(`   Median:      ${metrics.http_req_duration.values.med.toFixed(2)}ms`);
        console.log(`   95th %ile:   ${metrics.http_req_duration.values['p(95)'].toFixed(2)}ms`);
        console.log(`   99th %ile:   ${metrics.http_req_duration.values['p(99)'].toFixed(2)}ms`);
        console.log(`   Max:         ${metrics.http_req_duration.values.max.toFixed(2)}ms`);
    }

    // Request stats
    if (metrics.http_reqs) {
        console.log('\n📡 Request Statistics:');
        console.log(`   Total Requests:  ${metrics.http_reqs.values.count}`);
        console.log(`   Requests/sec:    ${metrics.http_reqs.values.rate.toFixed(2)}`);
    }

    // Error rate
    if (metrics.errors) {
        const errorPct = (metrics.errors.values.rate * 100).toFixed(2);
        console.log(`\n❌ Error Rate:      ${errorPct}%`);
    }

    // Form submissions
    if (metrics.form_submissions) {
        console.log(`\n✉️  Form Submissions: ${metrics.form_submissions.values.count}`);
    }

    console.log('\n' + '='.repeat(60) + '\n');

    return {
        'summary.json': JSON.stringify(data, null, 2),
    };
}
