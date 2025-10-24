#!/usr/bin/env node
/**
 * Phase 2 Integration Script
 *
 * This script applies Phase 2 changes to server.js:
 * - Adds dotenv and axios imports
 * - Adds pipeline configuration
 * - Adds callNormalizationPipeline function
 * - Updates POST endpoint to call pipeline
 * - Updates response to include pipeline results
 */

const fs = require('fs');
const path = require('path');

const serverPath = path.join(__dirname, 'server.js');
const backupPath = path.join(__dirname, 'server.js.backup');

console.log('🔧 Phase 2 Integration Script');
console.log('================================');
console.log('');

// Read server.js
let content = fs.readFileSync(serverPath, 'utf8');
console.log(`✅ Read server.js (${content.length} bytes)`);

// Backup
fs.writeFileSync(backupPath, content);
console.log(`✅ Created backup: server.js.backup`);

// 1. Add dotenv and axios after line 42
const importsLocation = content.indexOf("const express = require('express');");
if (importsLocation === -1) {
    console.error('❌ Could not find express import');
    process.exit(1);
}

// Add dotenv at the top (before express)
const dotenvImport = "// Load environment variables from .env file\nrequire('dotenv').config();\n\n";
content = content.substring(0, importsLocation) + dotenvImport + content.substring(importsLocation);
console.log('✅ Added dotenv import');

// Add axios after other requires
const axiosLocation = content.indexOf("const { Pool } = require('pg');");
if (axiosLocation === -1) {
    console.error('❌ Could not find pg import');
    process.exit(1);
}

const axiosImport = "\nconst axios = require('axios');";
const insertPoint = content.indexOf('\n', axiosLocation);
content = content.substring(0, insertPoint) + axiosImport + content.substring(insertPoint);
console.log('✅ Added axios import');

// 2. Add pipeline configuration after PORT definition
const portLocation = content.indexOf('const PORT = process.env.PORT || 3000;');
if (portLocation === -1) {
    console.error('❌ Could not find PORT definition');
    process.exit(1);
}

const pipelineConfig = `

/**
 * Python Normalization Pipeline Configuration
 *
 * Configuration for calling the Python FastAPI service that runs
 * the 5-phase normalization pipeline on form submissions.
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
    executeOnSubmit: PIPELINE_CONFIG.executeOnSubmit
});
`;

const portEndLine = content.indexOf('\n', portLocation);
content = content.substring(0, portEndLine) + pipelineConfig + content.substring(portEndLine);
console.log('✅ Added pipeline configuration');

// 3. Add callNormalizationPipeline function before saveToDatabase
const saveToDatabaseLocation = content.indexOf('async function saveToDatabase(structuredData, rawPayload) {');
if (saveToDatabaseLocation === -1) {
    console.error('❌ Could not find saveToDatabase function');
    process.exit(1);
}

const pipelineFunction = `
/**
 * Call the Python normalization pipeline API
 *
 * Sends the structured form data to the Python FastAPI service which executes
 * the complete 5-phase normalization pipeline.
 *
 * @param {Object} structuredData - The structured form data
 * @param {string} caseId - The database case ID for reference
 * @returns {Promise<Object>} Pipeline execution results
 */
async function callNormalizationPipeline(structuredData, caseId) {
    if (!PIPELINE_CONFIG.enabled || !PIPELINE_CONFIG.executeOnSubmit) {
        return { skipped: true, reason: 'Pipeline disabled in configuration' };
    }

    try {
        console.log(\`📋 Calling normalization pipeline (Case ID: \${caseId})...\`);
        const startTime = Date.now();

        const headers = { 'Content-Type': 'application/json' };
        if (PIPELINE_CONFIG.apiKey) {
            headers['X-API-Key'] = PIPELINE_CONFIG.apiKey;
        }

        const response = await axios.post(
            \`\${PIPELINE_CONFIG.apiUrl}/api/normalize\`,
            structuredData,
            {
                headers: headers,
                timeout: PIPELINE_CONFIG.timeout,
                validateStatus: (status) => status < 500
            }
        );

        const executionTime = Date.now() - startTime;

        if (response.data.success) {
            console.log(\`✅ Pipeline completed successfully in \${executionTime}ms\`);
            if (response.data.phase_results) {
                Object.entries(response.data.phase_results).forEach(([phase, results]) => {
                    console.log(\`   - \${phase}:\`, JSON.stringify(results));
                });
            }

            return {
                success: true,
                executionTime: executionTime,
                ...response.data
            };
        } else {
            const errorMessage = response.data.error || 'Unknown pipeline error';
            console.error(\`❌ Pipeline failed: \${errorMessage}\`);

            if (PIPELINE_CONFIG.continueOnFailure) {
                console.log('⚠️  Continuing despite pipeline failure');
                return {
                    success: false,
                    error: errorMessage,
                    continued: true
                };
            } else {
                throw new Error(\`Pipeline failed: \${errorMessage}\`);
            }
        }

    } catch (error) {
        const errorMessage = error.response?.data?.error || error.message;
        console.error('❌ Pipeline API call failed:', errorMessage);

        if (error.code === 'ECONNREFUSED') {
            console.error(\`   ⚠️  Connection refused - is the Python API running on \${PIPELINE_CONFIG.apiUrl}?\`);
        }

        if (PIPELINE_CONFIG.continueOnFailure) {
            console.log('⚠️  Continuing despite pipeline error');
            return {
                success: false,
                error: errorMessage,
                continued: true
            };
        } else {
            throw error;
        }
    }
}

`;

content = content.substring(0, saveToDatabaseLocation) + pipelineFunction + content.substring(saveToDatabaseLocation);
console.log('✅ Added callNormalizationPipeline function');

// 4. Add pipeline call in POST endpoint after database save
const dbSaveLocation = content.lastIndexOf('dbCaseId = await saveToDatabase(structuredData, formData);');
if (dbSaveLocation === -1) {
    console.error('❌ Could not find database save location');
    process.exit(1);
}

// Find the end of the try-catch block for database save
const dbSaveBlockEnd = content.indexOf('}', content.indexOf('// Continue - don\'t fail the request if database fails', dbSaveLocation));

const pipelineCall = `

        // Call Python normalization pipeline (Phase 2)
        let pipelineResult = null;
        try {
            pipelineResult = await callNormalizationPipeline(structuredData, dbCaseId || 'no-db-id');
            if (pipelineResult.success) {
                console.log('✅ Normalization pipeline completed successfully');
            } else if (pipelineResult.skipped) {
                console.log(\`📋 Pipeline skipped: \${pipelineResult.reason}\`);
            } else {
                console.warn('⚠️  Pipeline failed but form was saved');
            }
        } catch (pipelineError) {
            console.error('❌ Pipeline execution failed:', pipelineError.message);
        }
`;

content = content.substring(0, dbSaveBlockEnd + 1) + pipelineCall + content.substring(dbSaveBlockEnd + 1);
console.log('✅ Added pipeline call to POST endpoint');

// 5. Update response to include pipeline results
const responseLocation = content.lastIndexOf('success: true,\n            message: \'Form entry saved successfully\',');
if (responseLocation === -1) {
    console.error('❌ Could not find success response');
    process.exit(1);
}

// Find structuredData in response
const structuredDataInResponse = content.indexOf('structuredData: originalFormatData', responseLocation);
const responseEnd = content.indexOf('\n        });', structuredDataInResponse);

const pipelineResponseField = `,
            // Pipeline results (Phase 2)
            pipeline: pipelineResult ? {
                executed: !pipelineResult.skipped,
                success: pipelineResult.success,
                executionTime: pipelineResult.executionTime,
                case_id: pipelineResult.case_id,
                error: pipelineResult.error
            } : null`;

content = content.substring(0, responseEnd) + pipelineResponseField + content.substring(responseEnd);
console.log('✅ Updated response to include pipeline results');

// Write modified content
fs.writeFileSync(serverPath, content);
console.log('');
console.log('✅ Successfully applied Phase 2 integration!');
console.log('');
console.log('Next steps:');
console.log('1. Review the changes in server.js');
console.log('2. Start the Python API: cd "normalization work" && uvicorn api.main:app --port 8000');
console.log('3. Start the Node.js server: npm start');
console.log('4. Test form submission');
console.log('');
console.log('Backup saved to: server.js.backup');
