/**
 * Phase 2 Integration Additions for server.js
 *
 * Add these sections to server.js to integrate with the Python normalization pipeline
 */

// ============================================================================
// 1. ADD AT TOP OF FILE (after existing require statements, around line 43)
// ============================================================================

// Load environment variables
require('dotenv').config();

// Import axios for HTTP requests to Python API
const axios = require('axios');

// ============================================================================
// 2. ADD AFTER const PORT = ... (around line 52)
// ============================================================================

/**
 * Python Normalization Pipeline Configuration
 *
 * Configuration for calling the Python FastAPI service that runs
 * the 5-phase normalization pipeline on form submissions.
 *
 * Environment Variables:
 * - PIPELINE_API_URL: Base URL of Python API (default: http://localhost:8000)
 * - PIPELINE_API_ENABLED: Enable/disable pipeline calls (default: true)
 * - PIPELINE_API_TIMEOUT: Request timeout in ms (default: 60000)
 * - PIPELINE_API_KEY: Optional API key for authentication
 * - EXECUTE_PIPELINE_ON_SUBMIT: Auto-execute on form submit (default: true)
 * - CONTINUE_ON_PIPELINE_FAILURE: Save form even if pipeline fails (default: true)
 */
const PIPELINE_CONFIG = {
    apiUrl: process.env.PIPELINE_API_URL || 'http://localhost:8000',
    enabled: process.env.PIPELINE_API_ENABLED !== 'false',
    timeout: parseInt(process.env.PIPELINE_API_TIMEOUT) || 60000,
    apiKey: process.env.PIPELINE_API_KEY || '',
    executeOnSubmit: process.env.EXECUTE_PIPELINE_ON_SUBMIT !== 'false',
    continueOnFailure: process.env.CONTINUE_ON_PIPELINE_FAILURE !== 'false'
};

console.log('📋 Pipeline Configuration:', {
    apiUrl: PIPELINE_CONFIG.apiUrl,
    enabled: PIPELINE_CONFIG.enabled,
    executeOnSubmit: PIPELINE_CONFIG.executeOnSubmit,
    timeout: `${PIPELINE_CONFIG.timeout}ms`
});

// ============================================================================
// 3. ADD NEW FUNCTION (before saveToDatabase function, around line 805)
// ============================================================================

/**
 * Call the Python normalization pipeline API
 *
 * Sends the structured form data to the Python FastAPI service which executes
 * the complete 5-phase normalization pipeline:
 * 1. Input Normalization
 * 2. Dataset Builder (HoH × Defendant Cartesian product)
 * 3. Flag Processors (180+ boolean flags)
 * 4. Document Profiles (SROGs, PODs, Admissions)
 * 5. Set Splitting (max 120 interrogatories per set)
 *
 * The pipeline also sends results to the Docmosis webhook for document generation
 * (if webhooks are enabled in the Python API configuration).
 *
 * @param {Object} structuredData - The structured form data (output of transformFormData)
 * @param {string} caseId - The database case ID for reference
 * @returns {Promise<Object>} Pipeline execution results with phase summaries
 * @throws {Error} If pipeline execution fails and CONTINUE_ON_PIPELINE_FAILURE is false
 */
async function callNormalizationPipeline(structuredData, caseId) {
    // Check if pipeline is enabled
    if (!PIPELINE_CONFIG.enabled) {
        console.log('📋 Pipeline disabled - skipping normalization');
        return { skipped: true, reason: 'Pipeline disabled in configuration' };
    }

    if (!PIPELINE_CONFIG.executeOnSubmit) {
        console.log('📋 Auto-execution disabled - skipping normalization');
        return { skipped: true, reason: 'Auto-execution disabled' };
    }

    try {
        console.log('📋 Calling normalization pipeline...');
        console.log(`   API URL: ${PIPELINE_CONFIG.apiUrl}/api/normalize`);
        console.log(`   Case ID: ${caseId}`);
        console.log(`   Timeout: ${PIPELINE_CONFIG.timeout}ms`);

        const startTime = Date.now();

        // Prepare request headers
        const headers = {
            'Content-Type': 'application/json'
        };

        // Add API key if configured
        if (PIPELINE_CONFIG.apiKey) {
            headers['X-API-Key'] = PIPELINE_CONFIG.apiKey;
        }

        // Call the Python API
        const response = await axios.post(
            `${PIPELINE_CONFIG.apiUrl}/api/normalize`,
            structuredData,
            {
                headers: headers,
                timeout: PIPELINE_CONFIG.timeout,
                validateStatus: (status) => status < 500 // Accept any status < 500
            }
        );

        const executionTime = Date.now() - startTime;

        // Check if pipeline succeeded
        if (response.data.success) {
            console.log(`✅ Pipeline completed successfully in ${executionTime}ms`);
            console.log(`   Case ID: ${response.data.case_id}`);
            console.log(`   Phases executed: ${Object.keys(response.data.phase_results || {}).length}`);

            // Log phase summaries
            if (response.data.phase_results) {
                console.log('   Phase Results:');
                Object.entries(response.data.phase_results).forEach(([phase, results]) => {
                    console.log(`     - ${phase}:`, JSON.stringify(results));
                });
            }

            // Log webhook summary if available
            if (response.data.webhook_summary) {
                const webhook = response.data.webhook_summary;
                console.log(`   Webhooks: ${webhook.succeeded}/${webhook.total_sets} succeeded`);
                if (webhook.failed > 0) {
                    console.warn(`   ⚠️  ${webhook.failed} webhook(s) failed`);
                }
            }

            return {
                success: true,
                executionTime: executionTime,
                ...response.data
            };

        } else {
            // Pipeline returned success: false
            const errorMessage = response.data.error || 'Unknown pipeline error';
            const phaseFailed = response.data.phase_failed || 'unknown';

            console.error(`❌ Pipeline failed at ${phaseFailed}: ${errorMessage}`);

            if (PIPELINE_CONFIG.continueOnFailure) {
                console.log('⚠️  Continuing despite pipeline failure (CONTINUE_ON_PIPELINE_FAILURE=true)');
                return {
                    success: false,
                    error: errorMessage,
                    phase_failed: phaseFailed,
                    continued: true
                };
            } else {
                throw new Error(`Pipeline failed at ${phaseFailed}: ${errorMessage}`);
            }
        }

    } catch (error) {
        const errorMessage = error.response?.data?.error || error.message;
        const statusCode = error.response?.status;

        console.error('❌ Pipeline API call failed:');
        console.error(`   Error: ${errorMessage}`);
        if (statusCode) {
            console.error(`   HTTP Status: ${statusCode}`);
        }
        if (error.code === 'ECONNREFUSED') {
            console.error(`   ⚠️  Connection refused - is the Python API running on ${PIPELINE_CONFIG.apiUrl}?`);
        }
        if (error.code === 'ETIMEDOUT' || error.code === 'ECONNABORTED') {
            console.error(`   ⚠️  Request timed out after ${PIPELINE_CONFIG.timeout}ms`);
        }

        if (PIPELINE_CONFIG.continueOnFailure) {
            console.log('⚠️  Continuing despite pipeline error (CONTINUE_ON_PIPELINE_FAILURE=true)');
            return {
                success: false,
                error: errorMessage,
                continued: true,
                errorCode: error.code
            };
        } else {
            throw error;
        }
    }
}

// ============================================================================
// 4. MODIFY THE POST /api/form-entries ENDPOINT (around line 1036-1041)
// ============================================================================

// Find this section in the POST endpoint:
//
//         // Save to PostgreSQL database
//         let dbCaseId = null;
//         try {
//             dbCaseId = await saveToDatabase(structuredData, formData);
//             console.log(`✅ Form entry saved to database with case ID: ${dbCaseId}`);
//         } catch (dbError) {
//             console.error('⚠️  Database save failed, but JSON file was saved:', dbError.message);
//             // Continue - don't fail the request if database fails
//         }
//
// REPLACE WITH:
//
//         // Save to PostgreSQL database
//         let dbCaseId = null;
//         try {
//             dbCaseId = await saveToDatabase(structuredData, formData);
//             console.log(`✅ Form entry saved to database with case ID: ${dbCaseId}`);
//         } catch (dbError) {
//             console.error('⚠️  Database save failed, but JSON file was saved:', dbError.message);
//             // Continue - don't fail the request if database fails
//         }
//
//         // Call Python normalization pipeline (Phase 2)
//         let pipelineResult = null;
//         try {
//             pipelineResult = await callNormalizationPipeline(structuredData, dbCaseId || 'no-db-id');
//             if (pipelineResult.success) {
//                 console.log('✅ Normalization pipeline completed successfully');
//             } else if (pipelineResult.skipped) {
//                 console.log(`📋 Pipeline skipped: ${pipelineResult.reason}`);
//             } else {
//                 console.warn('⚠️  Pipeline failed but form was saved');
//             }
//         } catch (pipelineError) {
//             console.error('❌ Pipeline execution failed:', pipelineError.message);
//             // Error already logged in callNormalizationPipeline
//             // If we're here and continueOnFailure=false, this error will propagate
//         }

// ============================================================================
// 5. UPDATE THE RESPONSE (around line 1044-1052)
// ============================================================================

// Find the success response:
//
//         // Success response
//         res.status(201).json({
//             success: true,
//             message: 'Form entry saved successfully',
//             id: formData.id,
//             filename: filename,
//             dbCaseId: dbCaseId,
//             timestamp: originalFormatData.serverTimestamp,
//             structuredData: originalFormatData
//         });
//
// REPLACE WITH:
//
//         // Success response
//         res.status(201).json({
//             success: true,
//             message: 'Form entry saved successfully',
//             id: formData.id,
//             filename: filename,
//             dbCaseId: dbCaseId,
//             timestamp: originalFormatData.serverTimestamp,
//             structuredData: originalFormatData,
//             // Pipeline results (if executed)
//             pipeline: pipelineResult ? {
//                 executed: !pipelineResult.skipped,
//                 success: pipelineResult.success,
//                 executionTime: pipelineResult.executionTime,
//                 case_id: pipelineResult.case_id,
//                 error: pipelineResult.error,
//                 phase_results: pipelineResult.phase_results,
//                 webhook_summary: pipelineResult.webhook_summary
//             } : null
//         });

// ============================================================================
// END OF PATCH
// ============================================================================

console.log('✅ This is a patch file - apply changes to server.js manually');
console.log('   See comments above for exact locations and changes');
