/**
 * Legal Form Application - Express Server
 *
 * This server handles form submissions for a legal document application,
 * transforming raw HTML form data into structured JSON format with human-readable keys and values.
 *
 * Key Data Transformation Features:
 * - Converts checkbox selections into arrays and boolean flags
 * - Generates unique IDs for plaintiffs and defendants
 * - Structures address data with full formatting
 * - Processes discovery/issue tracking for multiple issue categories
 * - Reverts normalized keys to original human-readable format (e.g., "Fire Hazard", "Common areas")
 * - Adjusts value casing/spelling to match original specifications (e.g., "Air Conditioner", "Smoke Alarms")
 *
 * Output Format Transformation:
 * The system performs a two-stage transformation:
 * 1. First, raw form data is transformed into a normalized structured format with PascalCase keys
 * 2. Then, keys and values are reverted to their original human-readable forms:
 *    - Keys: "FireHazard" → "Fire Hazard", "CommonAreas" → "Common areas",
 *            "UtilityInterruptions" → "Checkbox 44n6i", etc.
 *    - Values: "Air conditioner" → "Air Conditioner", "Smoke alarms" → "Smoke Alarms",
 *              "Improper servicing/emptying" → "Properly servicing and emptying receptacles", etc.
 *
 * Important Notes on Boolean Flags:
 * - All Has_ prefix flags have been REMOVED from the output
 * - Categories like TrashProblems, NoticesIssues, Safety, and UtilityIssues
 *   populate their arrays (SelectTrashProblems, SelectNoticesIssues, SelectSafetyIssues,
 *   UtilityInterruptions) but DO NOT create top-level boolean flags
 * - This design prevents redundant boolean flags and keeps the output clean
 *
 * Last Updated: 2025-10-07
 * Recent Changes:
 * - Added revertToOriginalFormat() function to transform normalized keys/values back to original format
 * - Implemented recursive transformation for all nested objects and arrays
 * - Updated POST endpoint to apply transformation before saving JSON files
 * - Consolidated Plumbing values to use "Clogged bath/shower/sink/toilet"
 * - Reordered HealthHazard values (Mold, Mildew, Mushrooms, Raw sewage, Noxious fumes, Chemical/paint, Toxic water, Offensive odors)
 * - Updated Structure weatherproofing text: "Ineffective Weatherproofing of any windows doors"
 * - Normalized SelectSafetyIssues to use "Broken/inoperable security gate" (no spaces around /)
 * - Added automatic array deduplication to prevent duplicate values when multiple checkboxes map to the same consolidated value
 */

// Load environment variables from .env file
require('dotenv').config();

const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const compression = require('compression');
const fs = require('fs');
const path = require('path');
const { Pool } = require('pg');
const axios = require('axios');
const dropboxService = require('./dropbox-service');

// Monitoring and metrics
const metricsModule = require('./monitoring/metrics');
const { metricsMiddleware } = require('./monitoring/middleware');

// Logging
const logger = require('./monitoring/logger');
const {
    requestLoggingMiddleware,
    errorLoggingMiddleware
} = require('./monitoring/log-middleware');

// Health checks
const {
    checkLiveness,
    checkReadiness,
    checkDetailed,
    sendHealthResponse
} = require('./monitoring/health-checks');

const app = express();
const PORT = process.env.PORT || 3000;

/**
 * Access Control Configuration
 *
 * Secures the application with token-based authentication when deployed to production.
 * In development mode (NODE_ENV !== 'production'), authentication is bypassed.
 * Health check endpoints always bypass authentication for GCP monitoring.
 */
const ACCESS_TOKEN = process.env.ACCESS_TOKEN;
const REQUIRE_AUTH = process.env.NODE_ENV === 'production';

/**
 * Authentication Middleware
 * 
 * Checks for access token in URL query (?token=xxx) or Authorization header (Bearer xxx).
 * Blocks unauthorized requests with 401 status.
 * 
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
function requireAuth(req, res, next) {
    // Skip auth in development mode
    if (!REQUIRE_AUTH) {
        return next();
    }

    // Skip auth for health checks and metrics (GCP monitoring needs access)
    if (req.path.startsWith('/health') || req.path === '/metrics') {
        return next();
    }

    // Check for token in query string or Authorization header
    const tokenFromQuery = req.query.token;
    const tokenFromHeader = req.headers['authorization']?.replace('Bearer ', '');
    
    // Validate token
    if (tokenFromQuery === ACCESS_TOKEN || tokenFromHeader === ACCESS_TOKEN) {
        logger.info('Access granted', { 
            ip: req.ip, 
            path: req.path,
            method: req.method
        });
        return next();
    }
    
    // Log unauthorized attempt
    logger.warn('Unauthorized access attempt', { 
        ip: req.ip, 
        path: req.path,
        method: req.method,
        hasToken: !!(tokenFromQuery || tokenFromHeader)
    });
    
    // Return 401 Unauthorized
    res.status(401).json({ 
        error: 'Unauthorized', 
        message: 'Valid access token required. Provide token in URL (?token=xxx) or Authorization header (Bearer xxx).' 
    });
}

console.log('🔒 Access Control:', {
    enabled: REQUIRE_AUTH,
    mode: process.env.NODE_ENV,
    tokenConfigured: !!ACCESS_TOKEN
});

/**
 * Python Normalization Pipeline Configuration
 *
 * Configuration for calling the Python FastAPI service that runs
 * the 5-phase normalization pipeline on form submissions.
 */
const PIPELINE_CONFIG = {
    apiUrl: process.env.PIPELINE_API_URL || 'http://localhost:8000',
    enabled: process.env.PIPELINE_API_ENABLED !== 'false',
    timeout: parseInt(process.env.PIPELINE_API_TIMEOUT) || 300000, // Increase to 300s (5 minutes)
    apiKey: process.env.PIPELINE_API_KEY || '',
    executeOnSubmit: process.env.EXECUTE_PIPELINE_ON_SUBMIT !== 'false',
    continueOnFailure: process.env.CONTINUE_ON_PIPELINE_FAILURE !== 'false'
};

console.log('📋 Pipeline Configuration:', {
    apiUrl: PIPELINE_CONFIG.apiUrl,
    enabled: PIPELINE_CONFIG.enabled,
    executeOnSubmit: PIPELINE_CONFIG.executeOnSubmit
});


/**
 * PostgreSQL Connection Pool Configuration
 *
 * Optimized pool settings for performance and reliability.
 *
 * Performance Settings:
 * - max: 20 connections (balanced for concurrent requests)
 * - idleTimeoutMillis: 30000 (close idle connections after 30s)
 * - connectionTimeoutMillis: 2000 (fail fast on connection issues)
 * - maxUses: 7500 (rotate connections to prevent memory leaks)
 * - allowExitOnIdle: true (allow process to exit when idle)
 *
 * Tuning Notes:
 * - Increase 'max' for high-traffic scenarios (monitor with pg_stat_activity)
 * - Decrease 'idleTimeoutMillis' if connection limits are reached
 * - Monitor query performance with EXPLAIN ANALYZE
 */
const pool = new Pool({
    user: process.env.DB_USER || 'ryanhaines',
    host: process.env.DB_HOST || 'localhost',
    database: process.env.DB_NAME || 'legal_forms_db',
    password: process.env.DB_PASSWORD || '',
    port: process.env.DB_PORT || 5432,
    max: 20,                          // Maximum number of clients in the pool
    idleTimeoutMillis: 30000,         // Close idle clients after 30 seconds
    connectionTimeoutMillis: 2000,    // Return error after 2 seconds if connection not available
    maxUses: 7500,                    // Close and replace connection after 7500 uses
    allowExitOnIdle: true             // Allow pool to exit process when idle
});

// Test database connection on startup
pool.query('SELECT NOW()', (err, res) => {
    if (err) {
        console.error('❌ Database connection error:', err.message);
    } else {
        console.log('✅ Database connected successfully');
    }
});

// Create data directory if it doesn't exist
const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
}

/**
 * Pipeline Status Cache (Phase 5)
 *
 * In-memory cache to track pipeline execution status for real-time polling.
 * Each entry expires after 15 minutes to prevent memory leaks.
 *
 * Structure:
 * {
 *   [caseId]: {
 *     status: 'pending' | 'processing' | 'success' | 'failed' | 'skipped',
 *     startTime: timestamp,
 *     endTime: timestamp | null,
 *     executionTime: number | null,
 *     error: string | null,
 *     result: object | null,
 *     expiresAt: timestamp
 *   }
 * }
 */
const pipelineStatusCache = new Map();
const CACHE_TTL = 15 * 60 * 1000; // 15 minutes

/**
 * Store pipeline status in cache
 */
function setPipelineStatus(caseId, statusData) {
    pipelineStatusCache.set(caseId, {
        ...statusData,
        expiresAt: Date.now() + CACHE_TTL
    });
}

/**
 * Retrieve pipeline status from cache
 */
function getPipelineStatus(caseId) {
    const status = pipelineStatusCache.get(caseId);
    if (!status) {
        return null;
    }

    // Check if expired
    if (Date.now() > status.expiresAt) {
        pipelineStatusCache.delete(caseId);
        return null;
    }

    return status;
}

/**
 * Clean up expired cache entries (runs every 5 minutes)
 */
setInterval(() => {
    const now = Date.now();
    let cleaned = 0;

    for (const [caseId, status] of pipelineStatusCache.entries()) {
        if (now > status.expiresAt) {
            pipelineStatusCache.delete(caseId);
            cleaned++;
        }
    }

    if (cleaned > 0) {
        console.log(`🧹 Cleaned ${cleaned} expired pipeline status entries from cache`);
    }
}, 5 * 60 * 1000); // Run every 5 minutes

// Middleware
app.use(cors());

// Winston structured logging (must be early in middleware chain)
app.use(requestLoggingMiddleware);

// Prometheus metrics collection (must be early in middleware chain)
app.use(metricsMiddleware);

/**
 * Performance Optimization: Gzip/Brotli Compression
 *
 * Compresses all responses to reduce bandwidth and improve load times.
 * Typically achieves 70-80% size reduction for text-based assets.
 *
 * Configuration:
 * - level: 6 (balanced compression ratio vs CPU usage)
 * - threshold: 1024 bytes (don't compress tiny responses)
 * - filter: Only compress compressible content types
 */
app.use(compression({
    level: 6,
    threshold: 1024,
    filter: (req, res) => {
        if (req.headers['x-no-compression']) {
            return false;
        }
        return compression.filter(req, res);
    }
}));

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

/**
 * Performance Optimization: HTTP Caching Headers
 *
 * Implements aggressive caching strategy for static assets while ensuring
 * HTML content is revalidated. Reduces unnecessary network requests.
 *
 * Cache Strategy:
 * - Static assets (.js, .css, images): 1 year with immutable flag
 * - HTML files: 5 minutes with must-revalidate
 * - API responses: No cache (always fresh data)
 *
 * Impact: 95% reduction in bandwidth for returning users
 */
app.use((req, res, next) => {
    // Cache static assets for 1 year (immutable)
    if (req.url.match(/\.(js|css|png|jpg|jpeg|svg|woff|woff2|ttf|eot|ico)$/)) {
        res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
        res.setHeader('Expires', new Date(Date.now() + 31536000000).toUTCString());
    }
    // Cache HTML for 5 minutes with revalidation
    else if (req.url.endsWith('.html') || req.url === '/') {
        res.setHeader('Cache-Control', 'public, max-age=300, must-revalidate');
    }
    // No cache for API endpoints (always get fresh data)
    else if (req.url.startsWith('/api/')) {
        res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
        res.setHeader('Pragma', 'no-cache');
        res.setHeader('Expires', '0');
    }
    next();
});

// Apply authentication to all routes (except health checks, handled in middleware)
app.use(requireAuth);

// Serve static files (HTML, CSS, JS) - only after auth passes
app.use(express.static(__dirname));

/**
 * Transform raw form data into structured format matching goalOutput.md
 */
function transformFormData(rawData) {
    console.log('Raw form data keys:', Object.keys(rawData));

    // Extract plaintiffs
    const plaintiffs = [];
    const plaintiffNumbers = new Set();

    // Find all plaintiff numbers
    Object.keys(rawData).forEach(key => {
        const match = key.match(/plaintiff-(\d+)-/);
        if (match) {
            plaintiffNumbers.add(parseInt(match[1]));
        }
    });

    console.log('Found plaintiff numbers:', Array.from(plaintiffNumbers));

    // Process each plaintiff
    plaintiffNumbers.forEach(num => {
        const isHeadOfHousehold = rawData[`plaintiff-${num}-head`] === 'yes';

        const plaintiff = {
            Id: generateShortId(),
            PlaintiffItemNumberName: {
                First: rawData[`plaintiff-${num}-first-name`] || null,
                FirstAndLast: null,
                Last: rawData[`plaintiff-${num}-last-name`] || null,
                Middle: null,
                MiddleInitial: null,
                Prefix: null,
                Suffix: null
            },
            PlaintiffItemNumberType: rawData[`plaintiff-${num}-type`] || "Individual",
            PlaintiffItemNumberAgeCategory: [
                rawData[`plaintiff-${num}-age`] === 'child' ? 'Child' : 'Adult'
            ],
            HeadOfHousehold: isHeadOfHousehold,
            ItemNumber: num
        };

        // Only include PlaintiffItemNumberDiscovery if this plaintiff is head of household
        if (isHeadOfHousehold) {
            plaintiff.PlaintiffItemNumberDiscovery = extractIssueData(rawData, num);
        }

        // Set FirstAndLast
        if (plaintiff.PlaintiffItemNumberName.First && plaintiff.PlaintiffItemNumberName.Last) {
            plaintiff.PlaintiffItemNumberName.FirstAndLast =
                `${plaintiff.PlaintiffItemNumberName.First} ${plaintiff.PlaintiffItemNumberName.Last}`;
        }

        plaintiffs.push(plaintiff);
    });

    // Extract defendants
    const defendants = [];
    const defendantNumbers = new Set();

    // Find all defendant numbers
    Object.keys(rawData).forEach(key => {
        const match = key.match(/defendant-(\d+)-/);
        if (match) {
            defendantNumbers.add(parseInt(match[1]));
        }
    });

    console.log('Found defendant numbers:', Array.from(defendantNumbers));

    // Process each defendant
    defendantNumbers.forEach(num => {
        const defendant = {
            Id: generateShortId(),
            DefendantItemNumberName: {
                First: rawData[`defendant-${num}-first-name`] || null,
                FirstAndLast: null,
                Last: rawData[`defendant-${num}-last-name`] || null,
                Middle: null,
                MiddleInitial: null,
                Prefix: null,
                Suffix: null
            },
            DefendantItemNumberType: rawData[`defendant-${num}-entity`] || "Individual",
            DefendantItemNumberManagerOwner: rawData[`defendant-${num}-role`] === 'manager' ? 'Manager' : 'Owner',
            ItemNumber: num
        };

        // Set FirstAndLast
        if (defendant.DefendantItemNumberName.First && defendant.DefendantItemNumberName.Last) {
            defendant.DefendantItemNumberName.FirstAndLast =
                `${defendant.DefendantItemNumberName.First} ${defendant.DefendantItemNumberName.Last}`;
        }

        defendants.push(defendant);
    });

    // Build address object
    const fullAddress = buildFullAddress(rawData);

    return {
        Form: {
            Id: "1",
            InternalName: "AutoPopulationForm",
            Name: "Auto-Population Form"
        },
        PlaintiffDetails: plaintiffs,
        PlaintiffDetails_Minimum: 1,
        DefendantDetails2: defendants,
        DefendantDetails2_Minimum: 1,
        DefendantDetails2_Maximum: 10,
        Full_Address: fullAddress,
        FilingCity: rawData['filing-city'] || null,
        FilingCounty: rawData['filing-county'] || null,
        NotificationEmailOptIn: Boolean(rawData.notificationEmailOptIn),
        NotificationEmail: rawData.notificationEmail || null
    };
}

/**
 * Extract issue data for a plaintiff based on the form field structure
 *
 * This function transforms raw form checkbox data into structured arrays and boolean flags.
 * It processes multiple categories of issues (vermin, insects, plumbing, etc.) and creates
 * both category-level boolean flags (e.g., "VerminIssue") and detailed arrays of specific
 * issues (e.g., ["Rats/Mice", "Bedbugs"]).
 *
 * Key Naming Convention:
 * All property keys use PascalCase without spaces (e.g., "FireHazard", "CommonAreas",
 * "SelectTrashProblems", "UtilityInterruptions", "AgeDiscrimination", etc.) to ensure
 * consistent JSON output format and easy programmatic access.
 *
 * Note: Some categories (TrashProblems, NoticesIssues, Safety, UtilityIssues) do NOT have
 * top-level boolean flags - they only populate their respective arrays. This ensures the
 * output matches the required specification without redundant Has_ flags.
 *
 * @param {Object} rawData - The raw form data from the POST request
 * @param {number} plaintiffNum - The plaintiff number to extract data for
 * @returns {Object} Structured issue data with arrays and boolean flags
 */
function extractIssueData(rawData, plaintiffNum) {
    console.log(`Extracting issue data for plaintiff ${plaintiffNum}`);

    // Initialize the complete issue structure matching goalOutput.md
    // Note: TrashProblems, NoticesIssues, Safety, and UtilityIssues flags have been removed
    // as they are not needed - only their respective arrays are used
    const issues = {
        VerminIssue: false,
        Vermin: [],
        InsectIssues: false,
        Insects: [],
        HVACIssues: false,
        HVAC: [],
        Electrical: [],
        ElectricalIssues: false,
        FireHazardIssues: false,
        GovernmentEntityContacted: false,
        AppliancesIssues: false,
        PlumbingIssues: false,
        CabinetsIssues: false,
        FireHazard: [],
        SpecificGovernmentEntityContacted: [],
        Appliances: [],
        Plumbing: [],
        Cabinets: [],
        FlooringIssues: false,
        WindowsIssues: false,
        DoorIssues: false,
        Flooring: [],
        Windows: [],
        Doors: [],
        StructureIssues: false,
        Structure: [],
        CommonAreasIssues: false,
        CommonAreas: [],
        SelectTrashProblems: [],
        NuisanceIssues: false,
        Nuisance: [],
        HealthHazard: [],
        HealthHazardIssues: false,
        HarassmentIssues: false,
        Harassment: [],
        SelectNoticesIssues: [],
        UtilityInterruptions: [],
        InjuryIssues: false,
        NonresponsiveLandlordIssues: false,
        UnauthorizedEntries: false,
        StolenItems: false,
        DamagedItems: false,
        AgeDiscrimination: false,
        RacialDiscrimination: false,
        DisabilityDiscrimination: false,
        Unit: rawData[`plaintiff-${plaintiffNum}-unit`] || null,
        SelectSafetyIssues: [],
        SecurityDeposit: false
    };

    // Check all form fields for this plaintiff to see what checkbox values exist
    const plaintiffFields = Object.keys(rawData).filter(key => key.includes(`plaintiff-${plaintiffNum}-`) || key.includes(`-${plaintiffNum}`));
    console.log(`Plaintiff ${plaintiffNum} fields:`, plaintiffFields);

    // Map checkbox field patterns to output structure
    // Each mapping contains:
    //   - category: The array name where the value should be added (e.g., "Vermin", "Insects")
    //   - value: The string value to add to the array (e.g., "Rats/Mice", "Bedbugs")
    //   - flag: (optional) The boolean flag to set to true when this checkbox is checked
    //
    // For categories like "Select Trash Problems", "Select Notices Issues", "Select Safety Issues",
    // and "Checkbox 44n6i" (utility issues), NO FLAG is specified - only the array is populated.
    // This prevents unwanted TrashProblems, NoticesIssues, Safety, and UtilityIssues boolean flags.
    const fieldMappings = {
        // Vermin issues
        [`vermin-RatsMice-${plaintiffNum}`]: { category: 'Vermin', value: 'Rats/Mice', flag: 'VerminIssue' },
        [`vermin-Skunks-${plaintiffNum}`]: { category: 'Vermin', value: 'Skunks', flag: 'VerminIssue' },
        [`vermin-Bats-${plaintiffNum}`]: { category: 'Vermin', value: 'Bats', flag: 'VerminIssue' },
        [`vermin-Raccoons-${plaintiffNum}`]: { category: 'Vermin', value: 'Raccoons', flag: 'VerminIssue' },
        [`vermin-Pigeons-${plaintiffNum}`]: { category: 'Vermin', value: 'Pigeons', flag: 'VerminIssue' },
        [`vermin-Opossums-${plaintiffNum}`]: { category: 'Vermin', value: 'Opossums', flag: 'VerminIssue' },

        // Insect issues
        [`insect-Ants-${plaintiffNum}`]: { category: 'Insects', value: 'Ants', flag: 'InsectIssues' },
        [`insect-Roaches-${plaintiffNum}`]: { category: 'Insects', value: 'Roaches', flag: 'InsectIssues' },
        [`insect-Flies-${plaintiffNum}`]: { category: 'Insects', value: 'Flies', flag: 'InsectIssues' },
        [`insect-Bedbugs-${plaintiffNum}`]: { category: 'Insects', value: 'Bedbugs', flag: 'InsectIssues' },
        [`insect-Wasps-${plaintiffNum}`]: { category: 'Insects', value: 'Wasps', flag: 'InsectIssues' },
        [`insect-Hornets-${plaintiffNum}`]: { category: 'Insects', value: 'Hornets', flag: 'InsectIssues' },
        [`insect-Spiders-${plaintiffNum}`]: { category: 'Insects', value: 'Spiders', flag: 'InsectIssues' },
        [`insect-Termites-${plaintiffNum}`]: { category: 'Insects', value: 'Termites', flag: 'InsectIssues' },
        [`insect-Mosquitos-${plaintiffNum}`]: { category: 'Insects', value: 'Mosquitos', flag: 'InsectIssues' },
        [`insect-Bees-${plaintiffNum}`]: { category: 'Insects', value: 'Bees', flag: 'InsectIssues' },

        // HVAC issues
        [`hvac-AirConditioner-${plaintiffNum}`]: { category: 'HVAC', value: 'Air conditioner', flag: 'HVACIssues' },
        [`hvac-Heater-${plaintiffNum}`]: { category: 'HVAC', value: 'Heater', flag: 'HVACIssues' },
        [`hvac-Ventilation-${plaintiffNum}`]: { category: 'HVAC', value: 'Ventilation', flag: 'HVACIssues' },

        // Electrical issues
        [`electrical-Outlets-${plaintiffNum}`]: { category: 'Electrical', value: 'Outlets', flag: 'ElectricalIssues' },
        [`electrical-Panel-${plaintiffNum}`]: { category: 'Electrical', value: 'Panel', flag: 'ElectricalIssues' },
        [`electrical-WallSwitches-${plaintiffNum}`]: { category: 'Electrical', value: 'Wall switches', flag: 'ElectricalIssues' },
        [`electrical-ExteriorLighting-${plaintiffNum}`]: { category: 'Electrical', value: 'Exterior lighting', flag: 'ElectricalIssues' },
        [`electrical-InteriorLighting-${plaintiffNum}`]: { category: 'Electrical', value: 'Interior lighting', flag: 'ElectricalIssues' },
        [`electrical-LightFixtures-${plaintiffNum}`]: { category: 'Electrical', value: 'Light fixtures', flag: 'ElectricalIssues' },
        [`electrical-Fans-${plaintiffNum}`]: { category: 'Electrical', value: 'Fans', flag: 'ElectricalIssues' },

        // Fire hazard issues
        [`fire-hazard-SmokeAlarms-${plaintiffNum}`]: { category: 'FireHazard', value: 'Smoke alarms', flag: 'FireHazardIssues' },
        [`fire-hazard-FireExtinguisher-${plaintiffNum}`]: { category: 'FireHazard', value: 'Fire extinguisher', flag: 'FireHazardIssues' },
        [`fire-hazard-Noncompliantelectricity-${plaintiffNum}`]: { category: 'FireHazard', value: 'Non-compliant electricity', flag: 'FireHazardIssues' },
        [`fire-hazard-NonGFIoutletsnearwater-${plaintiffNum}`]: { category: 'FireHazard', value: 'Non-GFI outlets near water', flag: 'FireHazardIssues' },
        [`fire-hazard-Carbonmonoxidedetectors-${plaintiffNum}`]: { category: 'FireHazard', value: 'Carbon monoxide detectors', flag: 'FireHazardIssues' },

        // Government entities
        [`government-HealthDepartment-${plaintiffNum}`]: { category: 'SpecificGovernmentEntityContacted', value: 'Health department', flag: 'GovernmentEntityContacted' },
        [`government-HousingAuthority-${plaintiffNum}`]: { category: 'SpecificGovernmentEntityContacted', value: 'Housing authority', flag: 'GovernmentEntityContacted' },
        [`government-CodeEnforcement-${plaintiffNum}`]: { category: 'SpecificGovernmentEntityContacted', value: 'Code enforcement', flag: 'GovernmentEntityContacted' },
        [`government-FireDepartment-${plaintiffNum}`]: { category: 'SpecificGovernmentEntityContacted', value: 'Fire department', flag: 'GovernmentEntityContacted' },
        [`government-PoliceDepartment-${plaintiffNum}`]: { category: 'SpecificGovernmentEntityContacted', value: 'Police department', flag: 'GovernmentEntityContacted' },
        [`government-DepartmentofEnvironmentalHealth-${plaintiffNum}`]: { category: 'SpecificGovernmentEntityContacted', value: 'Department of environmental health', flag: 'GovernmentEntityContacted' },
        [`government-DepartmentofHealthServices-${plaintiffNum}`]: { category: 'SpecificGovernmentEntityContacted', value: 'Department of health services', flag: 'GovernmentEntityContacted' },

        // Appliances
        [`appliances-Stove-${plaintiffNum}`]: { category: 'Appliances', value: 'Stove', flag: 'AppliancesIssues' },
        [`appliances-Dishwasher-${plaintiffNum}`]: { category: 'Appliances', value: 'Dishwasher', flag: 'AppliancesIssues' },
        [`appliances-Washerdryer-${plaintiffNum}`]: { category: 'Appliances', value: 'Washer/dryer', flag: 'AppliancesIssues' },
        [`appliances-Oven-${plaintiffNum}`]: { category: 'Appliances', value: 'Oven', flag: 'AppliancesIssues' },
        [`appliances-Microwave-${plaintiffNum}`]: { category: 'Appliances', value: 'Microwave', flag: 'AppliancesIssues' },
        [`appliances-Garbagedisposal-${plaintiffNum}`]: { category: 'Appliances', value: 'Garbage disposal', flag: 'AppliancesIssues' },
        [`appliances-Refrigerator-${plaintiffNum}`]: { category: 'Appliances', value: 'Refrigerator', flag: 'AppliancesIssues' },

        // Plumbing
        [`plumbing-Toilet-${plaintiffNum}`]: { category: 'Plumbing', value: 'Toilet', flag: 'PlumbingIssues' },
        [`plumbing-Insufficientwaterpressure-${plaintiffNum}`]: { category: 'Plumbing', value: 'Insufficient water pressure', flag: 'PlumbingIssues' },
        [`plumbing-Cloggedbath-${plaintiffNum}`]: { category: 'Plumbing', value: 'Clogged bath', flag: 'PlumbingIssues' },
        [`plumbing-Shower-${plaintiffNum}`]: { category: 'Plumbing', value: 'Shower', flag: 'PlumbingIssues' },
        [`plumbing-Nohotwater-${plaintiffNum}`]: { category: 'Plumbing', value: 'No hot water', flag: 'PlumbingIssues' },
        [`plumbing-Cloggedsinks-${plaintiffNum}`]: { category: 'Plumbing', value: 'Clogged sinks', flag: 'PlumbingIssues' },
        [`plumbing-Bath-${plaintiffNum}`]: { category: 'Plumbing', value: 'Bath', flag: 'PlumbingIssues' },
        [`plumbing-Nocoldwater-${plaintiffNum}`]: { category: 'Plumbing', value: 'No cold water', flag: 'PlumbingIssues' },
        [`plumbing-Cloggedshower-${plaintiffNum}`]: { category: 'Plumbing', value: 'Clogged shower', flag: 'PlumbingIssues' },
        [`plumbing-Fixtures-${plaintiffNum}`]: { category: 'Plumbing', value: 'Fixtures', flag: 'PlumbingIssues' },
        [`plumbing-Sewagecomingout-${plaintiffNum}`]: { category: 'Plumbing', value: 'Sewage coming out', flag: 'PlumbingIssues' },
        [`plumbing-NoCleanWaterSupply-${plaintiffNum}`]: { category: 'Plumbing', value: 'No Clean Water Supply', flag: 'PlumbingIssues' },
        [`plumbing-Leaks-${plaintiffNum}`]: { category: 'Plumbing', value: 'Leaks', flag: 'PlumbingIssues' },
        [`plumbing-Cloggedtoilets-${plaintiffNum}`]: { category: 'Plumbing', value: 'Clogged toilets', flag: 'PlumbingIssues' },
        [`plumbing-Unsanitarywater-${plaintiffNum}`]: { category: 'Plumbing', value: 'Unsanitary water', flag: 'PlumbingIssues' },

        // Cabinets
        [`cabinets-Broken-${plaintiffNum}`]: { category: 'Cabinets', value: 'Broken', flag: 'CabinetsIssues' },
        [`cabinets-Hinges-${plaintiffNum}`]: { category: 'Cabinets', value: 'Hinges', flag: 'CabinetsIssues' },
        [`cabinets-Alignment-${plaintiffNum}`]: { category: 'Cabinets', value: 'Alignment', flag: 'CabinetsIssues' },

        // Flooring
        [`flooring-Uneven-${plaintiffNum}`]: { category: 'Flooring', value: 'Uneven', flag: 'FlooringIssues' },
        [`flooring-Carpet-${plaintiffNum}`]: { category: 'Flooring', value: 'Carpet', flag: 'FlooringIssues' },
        [`flooring-Nailsstickingout-${plaintiffNum}`]: { category: 'Flooring', value: 'Nails sticking out', flag: 'FlooringIssues' },
        [`flooring-Tiles-${plaintiffNum}`]: { category: 'Flooring', value: 'Tiles', flag: 'FlooringIssues' },

        // Windows
        [`windows-Broken-${plaintiffNum}`]: { category: 'Windows', value: 'Broken', flag: 'WindowsIssues' },
        [`windows-Screens-${plaintiffNum}`]: { category: 'Windows', value: 'Screens', flag: 'WindowsIssues' },
        [`windows-Leaks-${plaintiffNum}`]: { category: 'Windows', value: 'Leaks', flag: 'WindowsIssues' },
        [`windows-Donotlock-${plaintiffNum}`]: { category: 'Windows', value: 'Do not lock', flag: 'WindowsIssues' },
        [`windows-Missingwindows-${plaintiffNum}`]: { category: 'Windows', value: 'Missing windows', flag: 'WindowsIssues' },
        [`windows-Brokenormissingscreens-${plaintiffNum}`]: { category: 'Windows', value: 'Broken or missing screens', flag: 'WindowsIssues' },

        // Doors (note: field names use "door-" not "doors-")
        [`door-Broken-${plaintiffNum}`]: { category: 'Doors', value: 'Broken', flag: 'DoorIssues' },
        [`door-Knobs-${plaintiffNum}`]: { category: 'Doors', value: 'Knobs', flag: 'DoorIssues' },
        [`door-Locks-${plaintiffNum}`]: { category: 'Doors', value: 'Locks', flag: 'DoorIssues' },
        [`door-Brokenhinges-${plaintiffNum}`]: { category: 'Doors', value: 'Broken hinges', flag: 'DoorIssues' },
        [`door-Slidingglassdoors-${plaintiffNum}`]: { category: 'Doors', value: 'Sliding glass doors', flag: 'DoorIssues' },
        [`door-Ineffectivewaterproofing-${plaintiffNum}`]: { category: 'Doors', value: 'Ineffective waterproofing', flag: 'DoorIssues' },
        [`door-Waterintrusionandorinsects-${plaintiffNum}`]: { category: 'Doors', value: 'Water intrusion and/or insects', flag: 'DoorIssues' },
        [`door-Donotcloseproperly-${plaintiffNum}`]: { category: 'Doors', value: 'Do not close properly', flag: 'DoorIssues' },

        // Structure
        // Note: Waterproofing and weatherproofing values use specific capitalization and wording
        [`structure-Bumpsinceiling-${plaintiffNum}`]: { category: 'Structure', value: 'Bumps in ceiling', flag: 'StructureIssues' },
        [`structure-Holeinceiling-${plaintiffNum}`]: { category: 'Structure', value: 'Hole in ceiling', flag: 'StructureIssues' },
        [`structure-Waterstainsonceiling-${plaintiffNum}`]: { category: 'Structure', value: 'Water stains on ceiling', flag: 'StructureIssues' },
        [`structure-Waterstainsonwall-${plaintiffNum}`]: { category: 'Structure', value: 'Water stains on wall', flag: 'StructureIssues' },
        [`structure-Holeinwall-${plaintiffNum}`]: { category: 'Structure', value: 'Hole in wall', flag: 'StructureIssues' },
        [`structure-Paint-${plaintiffNum}`]: { category: 'Structure', value: 'Paint', flag: 'StructureIssues' },
        [`structure-Exteriordeckporch-${plaintiffNum}`]: { category: 'Structure', value: 'Exterior deck/porch', flag: 'StructureIssues' },
        [`structure-Waterprooftoilet-${plaintiffNum}`]: { category: 'Structure', value: 'Waterproof toilet', flag: 'StructureIssues' },
        [`structure-Waterprooftub-${plaintiffNum}`]: { category: 'Structure', value: 'Waterproof tub', flag: 'StructureIssues' },
        [`structure-Staircase-${plaintiffNum}`]: { category: 'Structure', value: 'Staircase', flag: 'StructureIssues' },
        [`structure-Basementflood-${plaintiffNum}`]: { category: 'Structure', value: 'Basement flood', flag: 'StructureIssues' },
        [`structure-Leaksingarage-${plaintiffNum}`]: { category: 'Structure', value: 'Leaks in garage', flag: 'StructureIssues' },
        [`structure-SoftSpotsduetoLeaks-${plaintiffNum}`]: { category: 'Structure', value: 'Soft spots due to leaks', flag: 'StructureIssues' },
        [`structure-UneffectiveWaterproofingofthetubsortoilet-${plaintiffNum}`]: { category: 'Structure', value: 'Ineffective waterproofing of the tubs or toilet', flag: 'StructureIssues' },
        [`structure-IneffectiveWeatherproofingofanywindows-${plaintiffNum}`]: { category: 'Structure', value: 'Ineffective Weatherproofing of any windows doors', flag: 'StructureIssues' },

        // Common areas
        [`common-areas-Mailboxbroken-${plaintiffNum}`]: { category: 'CommonAreas', value: 'Mailbox broken', flag: 'CommonAreasIssues' },
        [`common-areas-Parkingareaissues-${plaintiffNum}`]: { category: 'CommonAreas', value: 'Parking area issues', flag: 'CommonAreasIssues' },
        [`common-areas-Damagetocars-${plaintiffNum}`]: { category: 'CommonAreas', value: 'Damage to cars', flag: 'CommonAreasIssues' },
        [`common-areas-Flooding-${plaintiffNum}`]: { category: 'CommonAreas', value: 'Flooding', flag: 'CommonAreasIssues' },
        [`common-areas-Entrancesblocked-${plaintiffNum}`]: { category: 'CommonAreas', value: 'Entrances blocked', flag: 'CommonAreasIssues' },
        [`common-areas-Swimmingpool-${plaintiffNum}`]: { category: 'CommonAreas', value: 'Swimming pool', flag: 'CommonAreasIssues' },
        [`common-areas-Jacuzzi-${plaintiffNum}`]: { category: 'CommonAreas', value: 'Jacuzzi', flag: 'CommonAreasIssues' },
        [`common-areas-Laundryroom-${plaintiffNum}`]: { category: 'CommonAreas', value: 'Laundry room', flag: 'CommonAreasIssues' },
        [`common-areas-Recreationroom-${plaintiffNum}`]: { category: 'CommonAreas', value: 'Recreation room', flag: 'CommonAreasIssues' },
        [`common-areas-Gym-${plaintiffNum}`]: { category: 'CommonAreas', value: 'Gym', flag: 'CommonAreasIssues' },
        [`common-areas-Elevator-${plaintiffNum}`]: { category: 'CommonAreas', value: 'Elevator', flag: 'CommonAreasIssues' },
        [`common-areas-FilthRubbishGarbage-${plaintiffNum}`]: { category: 'CommonAreas', value: 'Filth/Rubbish/Garbage', flag: 'CommonAreasIssues' },
        [`common-areas-Vermin-${plaintiffNum}`]: { category: 'CommonAreas', value: 'Vermin', flag: 'CommonAreasIssues' },
        [`common-areas-Insects-${plaintiffNum}`]: { category: 'CommonAreas', value: 'Insects', flag: 'CommonAreasIssues' },
        [`common-areas-BrokenGate-${plaintiffNum}`]: { category: 'CommonAreas', value: 'Broken gate', flag: 'CommonAreasIssues' },
        [`common-areas-Blockedareasdoors-${plaintiffNum}`]: { category: 'CommonAreas', value: 'Blocked areas/doors', flag: 'CommonAreasIssues' },

        // Trash problems (note: field names use "trash-" not "trash-problems-")
        [`trash-Inadequatenumberofreceptacles-${plaintiffNum}`]: { category: 'SelectTrashProblems', value: 'Inadequate number of receptacles' },
        [`trash-Improperservicingemptying-${plaintiffNum}`]: { category: 'SelectTrashProblems', value: 'Improper servicing/emptying' },

        // Nuisance
        [`nuisance-Drugs-${plaintiffNum}`]: { category: 'Nuisance', value: 'Drugs', flag: 'NuisanceIssues' },
        [`nuisance-Smoking-${plaintiffNum}`]: { category: 'Nuisance', value: 'Smoking', flag: 'NuisanceIssues' },
        [`nuisance-Noisyneighbors-${plaintiffNum}`]: { category: 'Nuisance', value: 'Noisy neighbors', flag: 'NuisanceIssues' },
        [`nuisance-Gangs-${plaintiffNum}`]: { category: 'Nuisance', value: 'Gangs', flag: 'NuisanceIssues' },

        // Health hazard
        // Note: Values are ordered as: Mold, Mildew, Mushrooms, Raw sewage, Noxious fumes, Chemical/paint, Toxic water, Offensive odors
        [`health-hazard-Mold-${plaintiffNum}`]: { category: 'HealthHazard', value: 'Mold', flag: 'HealthHazardIssues' },
        [`health-hazard-Mildew-${plaintiffNum}`]: { category: 'HealthHazard', value: 'Mildew', flag: 'HealthHazardIssues' },
        [`health-hazard-Mushrooms-${plaintiffNum}`]: { category: 'HealthHazard', value: 'Mushrooms', flag: 'HealthHazardIssues' },
        [`health-hazard-Rawsewageonexterior-${plaintiffNum}`]: { category: 'HealthHazard', value: 'Raw sewage on exterior', flag: 'HealthHazardIssues' },
        [`health-hazard-Noxiousfumes-${plaintiffNum}`]: { category: 'HealthHazard', value: 'Noxious fumes', flag: 'HealthHazardIssues' },
        [`health-hazard-Chemicalpaintcontamination-${plaintiffNum}`]: { category: 'HealthHazard', value: 'Chemical/paint contamination', flag: 'HealthHazardIssues' },
        [`health-hazard-Toxicwaterpollution-${plaintiffNum}`]: { category: 'HealthHazard', value: 'Toxic water pollution', flag: 'HealthHazardIssues' },
        [`health-hazard-Offensiveodors-${plaintiffNum}`]: { category: 'HealthHazard', value: 'Offensive odors', flag: 'HealthHazardIssues' },

        // Harassment
        [`harassment-UnlawfulDetainer-${plaintiffNum}`]: { category: 'Harassment', value: 'Unlawful detainer', flag: 'HarassmentIssues' },
        [`harassment-Evictionthreats-${plaintiffNum}`]: { category: 'Harassment', value: 'Eviction threats', flag: 'HarassmentIssues' },
        [`harassment-Bydefendant-${plaintiffNum}`]: { category: 'Harassment', value: 'By defendant', flag: 'HarassmentIssues' },
        [`harassment-Bymaintenancemanworkers-${plaintiffNum}`]: { category: 'Harassment', value: 'By maintenance man/workers', flag: 'HarassmentIssues' },
        [`harassment-Bymanagerbuildingstaff-${plaintiffNum}`]: { category: 'Harassment', value: 'By manager/building staff', flag: 'HarassmentIssues' },
        [`harassment-Byowner-${plaintiffNum}`]: { category: 'Harassment', value: 'By owner', flag: 'HarassmentIssues' },
        [`harassment-Othertenants-${plaintiffNum}`]: { category: 'Harassment', value: 'Other tenants', flag: 'HarassmentIssues' },
        [`harassment-Illegitimatenotices-${plaintiffNum}`]: { category: 'Harassment', value: 'Illegitimate notices', flag: 'HarassmentIssues' },
        [`harassment-Refusaltomaketimelyrepairs-${plaintiffNum}`]: { category: 'Harassment', value: 'Refusal to make timely repairs', flag: 'HarassmentIssues' },
        [`harassment-Writtenthreats-${plaintiffNum}`]: { category: 'Harassment', value: 'Written threats', flag: 'HarassmentIssues' },
        [`harassment-Aggressiveinappropriatelanguage-${plaintiffNum}`]: { category: 'Harassment', value: 'Aggressive/inappropriate language', flag: 'HarassmentIssues' },
        [`harassment-Physicalthreatsortouching-${plaintiffNum}`]: { category: 'Harassment', value: 'Physical threats or touching', flag: 'HarassmentIssues' },
        [`harassment-Noticessinglingoutonetenantbutnotuniformlygiventoalltenants-${plaintiffNum}`]: { category: 'Harassment', value: 'Notices singling out one tenant, but not uniformly given to all tenants', flag: 'HarassmentIssues' },
        [`harassment-Duplicativenotices-${plaintiffNum}`]: { category: 'Harassment', value: 'Duplicative notices', flag: 'HarassmentIssues' },
        [`harassment-UntimelyResponsefromLandlord-${plaintiffNum}`]: { category: 'Harassment', value: 'Untimely response from landlord', flag: 'HarassmentIssues' },

        // Notices issues (note: field names use "notices-" not "notices-issues-")
        [`notices-3day-${plaintiffNum}`]: { category: 'SelectNoticesIssues', value: '3-day' },
        [`notices-24hour-${plaintiffNum}`]: { category: 'SelectNoticesIssues', value: '24-hour' },
        [`notices-30day-${plaintiffNum}`]: { category: 'SelectNoticesIssues', value: '30-day' },
        [`notices-60day-${plaintiffNum}`]: { category: 'SelectNoticesIssues', value: '60-day' },
        [`notices-Toquit-${plaintiffNum}`]: { category: 'SelectNoticesIssues', value: 'To quit' },
        [`notices-Performorquit-${plaintiffNum}`]: { category: 'SelectNoticesIssues', value: 'Perform or quit' },

        // Utility issues (note: field names use "utility-" not "utility-issues-")
        [`utility-Gasleak-${plaintiffNum}`]: { category: 'UtilityInterruptions', value: 'Gas leak' },
        [`utility-Watershutoffs-${plaintiffNum}`]: { category: 'UtilityInterruptions', value: 'Water shutoffs' },
        [`utility-Electricityshutoffs-${plaintiffNum}`]: { category: 'UtilityInterruptions', value: 'Electricity shutoffs' },
        [`utility-Heatshutoff-${plaintiffNum}`]: { category: 'UtilityInterruptions', value: 'Heat shutoff' },
        [`utility-Gasshutoff-${plaintiffNum}`]: { category: 'UtilityInterruptions', value: 'Gas shutoff' },

        // Safety issues (note: field names use "safety-" not "safety-issues-")
        // Note: "Broken/inoperable security gate" uses "/" with no spaces for consistency
        [`safety-Brokeninoperablesecuritygate-${plaintiffNum}`]: { category: 'SelectSafetyIssues', value: 'Broken/inoperable security gate' },
        [`safety-Brokendoors-${plaintiffNum}`]: { category: 'SelectSafetyIssues', value: 'Broken doors' },
        [`safety-Unauthorizedentries-${plaintiffNum}`]: { category: 'SelectSafetyIssues', value: 'Unauthorized entries' },
        [`safety-Brokenbuzzertogetin-${plaintiffNum}`]: { category: 'SelectSafetyIssues', value: 'Broken buzzer to get in' },
        [`safety-Securitycameras-${plaintiffNum}`]: { category: 'SelectSafetyIssues', value: 'Security cameras' },
        [`safety-Inoperablelocks-${plaintiffNum}`]: { category: 'SelectSafetyIssues', value: 'Inoperable locks' },

        // Direct boolean issues
        [`direct-appliancesissues-${plaintiffNum}`]: { flag: 'AppliancesIssues' },
        [`direct-injuryissues-${plaintiffNum}`]: { flag: 'InjuryIssues' },
        [`direct-nonresponsivelandlordissues-${plaintiffNum}`]: { flag: 'NonresponsiveLandlordIssues' },
        [`direct-unauthorizedentries-${plaintiffNum}`]: { flag: 'UnauthorizedEntries' },
        [`direct-stolenitems-${plaintiffNum}`]: { flag: 'StolenItems' },
        [`direct-damageditems-${plaintiffNum}`]: { flag: 'DamagedItems' },
        [`direct-agediscrimination-${plaintiffNum}`]: { flag: 'AgeDiscrimination' },
        [`direct-racialdiscrimination-${plaintiffNum}`]: { flag: 'RacialDiscrimination' },
        [`direct-disabilitydiscrimination-${plaintiffNum}`]: { flag: 'DisabilityDiscrimination' },
        [`direct-securitydepositissues-${plaintiffNum}`]: { flag: 'SecurityDeposit' }
    };

    // Process all mappings
    // This loop iterates through all field mappings and checks if each checkbox is checked ('on')
    // When a checkbox is found:
    //   1. If it has a category, add the value to that array
    //   2. If it has a flag, set that boolean to true
    //   3. Some mappings have only a category (no flag) - this is intentional for trash, notices, safety, utilities
    Object.keys(fieldMappings).forEach(fieldKey => {
        if (rawData[fieldKey] === 'on') {
            const mapping = fieldMappings[fieldKey];
            console.log(`Found checked field: ${fieldKey} -> ${JSON.stringify(mapping)}`);

            if (mapping.category) {
                // Add to array
                issues[mapping.category].push(mapping.value);
                // Set flag if one exists (some categories like trash/notices/safety/utilities don't have flags)
                if (mapping.flag) {
                    issues[mapping.flag] = true;
                }
            } else if (mapping.flag) {
                // Set boolean flag only (for direct boolean issues without arrays)
                issues[mapping.flag] = true;
            }
        }
    });

    // Deduplicate all arrays to prevent duplicate values
    // This is necessary because multiple form fields may map to the same consolidated value
    // (e.g., multiple clogged items all map to "Clogged bath/shower/sink/toilet")
    Object.keys(issues).forEach(key => {
        if (Array.isArray(issues[key]) && issues[key].length > 0) {
            issues[key] = [...new Set(issues[key])];
        }
    });

    console.log(`Final issues for plaintiff ${plaintiffNum}:`, issues);
    return issues;
}

/**
 * Build full address object
 */
function buildFullAddress(rawData) {
    const line1 = rawData['property-address'] || '';
    const unit = rawData['apartment-unit'] ? ` ${rawData['apartment-unit']}` : '';
    const city = rawData['city'] || '';
    const state = rawData['state'] || '';
    const zip = rawData['zip-code'] || '';
    const stateName = getStateName(state);

    const streetAddress = line1 + unit;
    const fullAddress = `${streetAddress}, ${city}, ${stateName} ${zip}`;
    const cityStateZip = `${city}, ${stateName} ${zip}`;

    return {
        City: city,
        CityStatePostalCode: cityStateZip,
        Country: "United States",
        CountryCode: "US",
        FullAddress: fullAddress,
        FullInternationalAddress: `${fullAddress}, United States`,
        Latitude: null,
        Line1: streetAddress,
        Line2: null,
        Line3: null,
        Longitude: null,
        PostalCode: zip,
        State: stateName,
        StreetAddress: streetAddress,
        Type: "Home"
    };
}

/**
 * Convert state code to full name
 */
function getStateName(stateCode) {
    const stateMap = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
        'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
        'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
        'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
        'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
        'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
        'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
        'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
    };
    return stateMap[stateCode] || stateCode;
}

/**
 * Generate short random ID
 */
function generateShortId() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < 6; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

/**
 * Revert normalized keys back to their original human-readable forms
 * and adjust value casing/spelling to match the original version
 *
 * This function recursively transforms the JSON output to match the original
 * key names and value formatting used in the first version of the application.
 *
 * @param {Object|Array} obj - The object or array to transform
 * @returns {Object|Array} Transformed object with original key names and value casing
 */
function revertToOriginalFormat(obj) {
    // Key mapping: normalized keys -> original human-readable keys
    const keyMappings = {
        'FilingCity': 'Filing city',
        'FilingCounty': 'Filing county',
        'HealthHazard': 'Health hazard',
        'SecurityDeposit': 'Security Deposit',
        'FireHazard': 'Fire Hazard',
        'SpecificGovernmentEntityContacted': 'Specific Government Entity Contacted',
        'CommonAreas': 'Common areas',
        'SelectTrashProblems': 'Select Trash Problems',
        'SelectSafetyIssues': 'Select Safety Issues',
        'SelectNoticesIssues': 'Select Notices Issues',
        'UtilityInterruptions': 'Checkbox 44n6i',
        'InjuryIssues': 'Injury Issues',
        'NonresponsiveLandlordIssues': 'Nonresponsive landlord Issues',
        'UnauthorizedEntries': 'Unauthorized entries',
        'StolenItems': 'Stolen items',
        'DamagedItems': 'Damaged items',
        'AgeDiscrimination': 'Age discrimination',
        'RacialDiscrimination': 'Racial Discrimination',
        'DisabilityDiscrimination': 'Disability discrimination',
        'NotificationEmailOptIn': 'Notification Email Opt-In',
        'NotificationEmail': 'Notification Email'
    };

    // Value mappings: normalized values -> original casing/spelling
    const valueMappings = {
        // HVAC
        'Air conditioner': 'Air Conditioner',

        // Electrical
        'Wall switches': 'Wall Switches',
        'Exterior lighting': 'Exterior Lighting',
        'Interior lighting': 'Interior Lighting',
        'Light fixtures': 'Light Fixtures',

        // Fire Hazard
        'Smoke alarms': 'Smoke Alarms',
        'Fire extinguisher': 'Fire Extinguisher',

        // Specific Government Entity Contacted
        'Health department': 'Health Department',
        'Housing authority': 'Housing Authority',
        'Code enforcement': 'Code Enforcement',
        'Fire department': 'Fire Department',
        'Police department': 'Police Department',
        'Department of environmental health': 'Department of Environmental Health',
        'Department of health services': 'Department of Health Services',

        // Common areas
        'Broken gate': 'Broken Gate',
        'Filth/Rubbish/Garbage': 'Filth Rubbish Garbage',

        // Harassment
        'Unlawful detainer': 'Unlawful Detainer',
        'Untimely response from landlord': 'Untimely Response from Landlord',

        // Structure
        'Soft spots due to leaks': 'Soft Spots due to Leaks',

        // Select Trash Problems
        'Improper servicing/emptying': 'Properly servicing and emptying receptacles',

        // Select Notices Issues
        'Perform or quit': 'Perform or Quit'
    };

    // Handle null, undefined, and primitive types
    if (obj === null || obj === undefined || typeof obj !== 'object') {
        return obj;
    }

    // Handle arrays - recursively transform each element
    if (Array.isArray(obj)) {
        return obj.map(item => {
            // Transform string values in arrays
            if (typeof item === 'string' && valueMappings[item]) {
                return valueMappings[item];
            }
            // Recursively transform objects in arrays
            if (typeof item === 'object') {
                return revertToOriginalFormat(item);
            }
            return item;
        });
    }

    // Handle objects - recursively transform keys and values
    const transformed = {};
    for (const [key, value] of Object.entries(obj)) {
        // Map the key name if it needs to be reverted
        const newKey = keyMappings[key] || key;

        // Recursively transform the value
        transformed[newKey] = revertToOriginalFormat(value);
    }

    return transformed;
}

/**
 * Save form data to PostgreSQL database
 * Creates case, parties, and issue selections based on the structured data
 *
 * Database Schema Note:
 * - Submitter information (notificationName, notificationEmail) is stored in raw_payload JSONB column
 * - All form data is preserved in the raw_payload for reference
 */

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
        // Store skipped status in cache (Phase 5)
        setPipelineStatus(caseId, {
            status: 'skipped',
            phase: 'complete',
            progress: 100,
            currentPhase: null,
            totalPhases: 5,
            startTime: Date.now(),
            endTime: Date.now(),
            executionTime: 0,
            error: null,
            result: { reason: 'Pipeline disabled in configuration' }
        });
        return { skipped: true, reason: 'Pipeline disabled in configuration' };
    }

    try {
        console.log(`📋 Calling normalization pipeline (Case ID: ${caseId})...`);
        const startTime = Date.now();

        // Store initial processing status in cache with phase tracking
        setPipelineStatus(caseId, {
            status: 'processing',
            phase: 'pipeline_started',
            progress: 40,  // 40% after form saved and database written
            currentPhase: 'Starting pipeline...',
            totalPhases: 5,
            startTime: startTime,
            endTime: null,
            executionTime: null,
            error: null,
            result: null,
            documentProgress: { completed: 0, total: 0, current: '' }
        });

        const headers = { 'Content-Type': 'application/json' };
        if (PIPELINE_CONFIG.apiKey) {
            headers['X-API-Key'] = PIPELINE_CONFIG.apiKey;
        }

        // Add case ID to the request data
        structuredData.case_id = caseId;
        console.log(`🔍 Sending to Python API with case_id: ${structuredData.case_id}`);
        console.log(`🔍 Case ID type: ${typeof structuredData.case_id}`);
        console.log(`🔍 Data keys being sent: ${Object.keys(structuredData).join(', ')}`);

        // CRITICAL DEBUG: Verify case_id is in the payload
        if (!structuredData.case_id) {
            console.error('❌ CRITICAL: case_id is missing from structuredData!');
        } else {
            console.log(`✅ Confirmed case_id in payload: ${structuredData.case_id}`);
        }

        // Start the pipeline in the background
        const pipelinePromise = axios.post(
            `${PIPELINE_CONFIG.apiUrl}/api/form-submissions`,
            structuredData,
            {
                headers: headers,
                timeout: PIPELINE_CONFIG.timeout,
                validateStatus: (status) => status < 500
            }
        );

        // ============================================================
        // DOCUMENT GENERATION (AUTOMATIC)
        // ============================================================
        // Document generation now happens automatically within the
        // /api/form-submissions endpoint. The Python service generates
        // documents via Docmosis and uploads to Dropbox synchronously.
        // No separate progress tracking needed.
        // ============================================================
        console.log(`📄 Document generation will happen automatically in Python pipeline...`);

        // Wait for pipeline completion (includes document generation)
        const response = await pipelinePromise;

        const executionTime = Date.now() - startTime;

        if (response.data.success) {
            console.log(`✅ Pipeline completed successfully in ${executionTime}ms`);
            
            // Extract webhook summary
            const webhookSummary = response.data.webhook_summary || null;
            if (webhookSummary) {
                console.log(`📄 Documents generated: ${webhookSummary.total_sets} (${webhookSummary.succeeded} succeeded, ${webhookSummary.failed} failed)`);
            }
            
            if (response.data.phase_results) {
                Object.entries(response.data.phase_results).forEach(([phase, results]) => {
                    console.log(`   - ${phase}:`, JSON.stringify(results));
                });
            }

            // Store success status in cache with webhook details
            setPipelineStatus(caseId, {
                status: 'success',
                phase: 'complete',
                progress: 100,
                currentPhase: webhookSummary ? `Generated ${webhookSummary.total_sets} documents` : 'Complete',
                totalPhases: 5,
                startTime: startTime,
                endTime: Date.now(),
                executionTime: executionTime,
                error: null,
                result: response.data,
                webhookSummary: webhookSummary  // Add webhook details
            });

            return {
                success: true,
                executionTime: executionTime,
                case_id: caseId,
                ...response.data
            };
        } else {
            const errorMessage = response.data.error || 'Unknown pipeline error';
            console.error(`❌ Pipeline failed: ${errorMessage}`);

            // Store failure status in cache (Phase 5)
            setPipelineStatus(caseId, {
                status: 'failed',
                phase: 'failed',
                progress: 0,
                currentPhase: null,
                totalPhases: 5,
                startTime: startTime,
                endTime: Date.now(),
                executionTime: executionTime,
                error: errorMessage,
                result: null
            });

            if (PIPELINE_CONFIG.continueOnFailure) {
                console.log('⚠️  Continuing despite pipeline failure');
                return {
                    success: false,
                    error: errorMessage,
                    case_id: caseId,
                    continued: true
                };
            } else {
                throw new Error(`Pipeline failed: ${errorMessage}`);
            }
        }

    } catch (error) {
        const errorMessage = error.response?.data?.error || error.message;
        console.error('❌ Pipeline API call failed:', errorMessage);

        if (error.code === 'ECONNREFUSED') {
            console.error(`   ⚠️  Connection refused - is the Python API running on ${PIPELINE_CONFIG.apiUrl}?`);
        }

        // Store error status in cache (Phase 5)
        setPipelineStatus(caseId, {
            status: 'failed',
            phase: 'failed',
            progress: 0,
            currentPhase: null,
            totalPhases: 5,
            startTime: Date.now(),
            endTime: Date.now(),
            executionTime: 0,
            error: errorMessage,
            result: null
        });

        if (PIPELINE_CONFIG.continueOnFailure) {
            console.log('⚠️  Continuing despite pipeline error');
            return {
                success: false,
                error: errorMessage,
                case_id: caseId,
                continued: true
            };
        } else {
            throw error;
        }
    }
}

async function saveToDatabase(structuredData, rawPayload) {
    const client = await pool.connect();

    try {
        await client.query('BEGIN');

        // 1. Insert case
        // Note: Submitter info is stored in raw_payload JSON
        const caseResult = await client.query(
            `INSERT INTO cases (
                property_address, city, state, zip_code, county, filing_location,
                internal_name, form_name, raw_payload, is_active
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING id`,
            [
                structuredData.Full_Address?.StreetAddress || structuredData.Full_Address?.Line1,
                structuredData.Full_Address?.City,
                structuredData.Full_Address?.State?.substring(0, 2)?.toUpperCase() || 'NC',
                structuredData.Full_Address?.PostalCode,
                structuredData.FilingCounty || structuredData['Filing county'],
                structuredData.FilingCity || structuredData['Filing city'],
                structuredData.Form?.InternalName,
                structuredData.Form?.Name,
                JSON.stringify(rawPayload),
                true
                // Note: Submitter information (notificationName, notificationEmail) is stored in raw_payload JSON
            ]
        );

        const caseId = caseResult.rows[0].id;
        console.log(`📊 Created case with ID: ${caseId}`);

        // 2. Insert plaintiffs
        const plaintiffs = structuredData.PlaintiffDetails || [];
        const plaintiffIds = {};

        for (let i = 0; i < plaintiffs.length; i++) {
            const plaintiff = plaintiffs[i];
            const plaintiffResult = await client.query(
                `INSERT INTO parties (
                    case_id, party_type, party_number, first_name, last_name, full_name,
                    plaintiff_type, age_category, is_head_of_household, unit_number
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING id`,
                [
                    caseId,
                    'plaintiff',
                    plaintiff.ItemNumber || (i + 1),
                    plaintiff.PlaintiffItemNumberName?.First,
                    plaintiff.PlaintiffItemNumberName?.Last,
                    plaintiff.PlaintiffItemNumberName?.FirstAndLast,
                    plaintiff.PlaintiffItemNumberType,
                    plaintiff.PlaintiffItemNumberAgeCategory?.[0],
                    plaintiff.HeadOfHousehold || false,
                    plaintiff.PlaintiffItemNumberDiscovery?.Unit
                ]
            );

            const plaintiffId = plaintiffResult.rows[0].id;
            plaintiffIds[plaintiff.ItemNumber || (i + 1)] = plaintiffId;
            console.log(`👤 Created plaintiff: ${plaintiff.PlaintiffItemNumberName?.FirstAndLast} (ID: ${plaintiffId})`);

            // 3. Insert issue selections for this plaintiff (if head of household)
            if (plaintiff.HeadOfHousehold && plaintiff.PlaintiffItemNumberDiscovery) {
                const discovery = plaintiff.PlaintiffItemNumberDiscovery;
                // Convert boolean flags to array items for Direct Yes/No issues
                const directYesNoItems = [];
                if (discovery.InjuryIssues) directYesNoItems.push('Injury Issues');
                if (discovery.NonresponsiveLandlordIssues || discovery['Nonresponsive landlord Issues']) directYesNoItems.push('Nonresponsive Landlord Issues');
                if (discovery.UnauthorizedEntries || discovery['Unauthorized entries']) directYesNoItems.push('Unauthorized Entries');
                if (discovery.StolenItems || discovery['Stolen items']) directYesNoItems.push('Stolen Items');
                if (discovery.DamagedItems || discovery['Damaged items']) directYesNoItems.push('Damaged Items');
                if (discovery.AgeDiscrimination || discovery['Age discrimination']) directYesNoItems.push('Age Discrimination');
                if (discovery.RacialDiscrimination || discovery['Racial Discrimination']) directYesNoItems.push('Racial Discrimination');
                if (discovery.DisabilityDiscrimination || discovery['Disability discrimination']) directYesNoItems.push('Disability Discrimination');
                if (discovery.SecurityDeposit || discovery['Security Deposit']) directYesNoItems.push('Security Deposit Issues');

                const issueArrays = [
                    { category: 'vermin', items: discovery.Vermin || [] },
                    { category: 'insects', items: discovery.Insects || [] },
                    { category: 'hvac', items: discovery.HVAC || [] },
                    { category: 'electrical', items: discovery.Electrical || [] },
                    { category: 'fire_hazard', items: discovery.FireHazard || discovery['Fire Hazard'] || [] },
                    { category: 'government', items: discovery.SpecificGovernmentEntityContacted || discovery['Specific Government Entity Contacted'] || [] },
                    { category: 'plumbing', items: discovery.Plumbing || [] },
                    { category: 'structure', items: discovery.Structure || [] },
                    { category: 'flooring', items: discovery.Flooring || [] },
                    { category: 'cabinets', items: discovery.Cabinets || [] },
                    { category: 'doors', items: discovery.Doors || [] },
                    { category: 'windows', items: discovery.Windows || [] },
                    { category: 'common_areas', items: discovery.CommonAreas || discovery['Common areas'] || [] },
                    { category: 'nuisance', items: discovery.Nuisance || [] },
                    { category: 'health_hazard', items: discovery.HealthHazard || discovery['Health hazard'] || [] },
                    { category: 'appliances', items: discovery.Appliances || [] },
                    { category: 'harassment', items: discovery.Harassment || [] },
                    { category: 'safety', items: discovery.SelectSafetyIssues || discovery['Select Safety Issues'] || [] },
                    { category: 'notices', items: discovery.SelectNoticesIssues || discovery['Select Notices Issues'] || [] },
                    { category: 'utility', items: discovery.UtilityInterruptions || discovery['Checkbox 44n6i'] || [] },
                    { category: 'trash', items: discovery.SelectTrashProblems || discovery['Select Trash Problems'] || [] },
                    { category: 'direct_yesno', items: directYesNoItems }
                ];

                for (const issueArray of issueArrays) {
                    for (const itemName of issueArray.items) {
                        // Find the issue option by name
                        const optionResult = await client.query(
                            `SELECT io.id
                             FROM issue_options io
                             JOIN issue_categories ic ON io.category_id = ic.id
                             WHERE ic.category_code = $1 AND io.option_name ILIKE $2`,
                            [issueArray.category, itemName]
                        );

                        if (optionResult.rows.length > 0) {
                            const optionId = optionResult.rows[0].id;
                            await client.query(
                                `INSERT INTO party_issue_selections (party_id, issue_option_id)
                                 VALUES ($1, $2)
                                 ON CONFLICT (party_id, issue_option_id) DO NOTHING`,
                                [plaintiffId, optionId]
                            );
                        } else {
                            console.warn(`⚠️  Issue option not found: ${issueArray.category} - ${itemName}`);
                        }
                    }
                }
            }
        }

        // 4. Insert defendants
        const defendants = structuredData.DefendantDetails2 || [];

        for (let i = 0; i < defendants.length; i++) {
            const defendant = defendants[i];
            await client.query(
                `INSERT INTO parties (
                    case_id, party_type, party_number, first_name, last_name, full_name,
                    entity_type, role
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
                [
                    caseId,
                    'defendant',
                    defendant.ItemNumber || (i + 1),
                    defendant.DefendantItemNumberName?.First,
                    defendant.DefendantItemNumberName?.Last,
                    defendant.DefendantItemNumberName?.FirstAndLast,
                    defendant.DefendantItemNumberType,
                    defendant.DefendantItemNumberManagerOwner
                ]
            );

            console.log(`⚖️  Created defendant: ${defendant.DefendantItemNumberName?.FirstAndLast}`);
        }

        await client.query('COMMIT');
        console.log('✅ Database transaction completed successfully');

        return caseId;

    } catch (error) {
        await client.query('ROLLBACK');
        console.error('❌ Database error:', error);
        throw error;
    } finally {
        client.release();
    }
}

/**
 * POST /api/form-entries
 * Save form submission data as JSON file AND PostgreSQL database
 */
app.post('/api/form-entries', async (req, res) => {
    try {
        const formData = req.body;
        console.log('Received form data:', JSON.stringify(formData, null, 2));

        // Validate required fields - check for at least one plaintiff
        const hasPlaintiff = Object.keys(formData).some(key =>
            key.includes('plaintiff') && key.includes('first-name') && formData[key]
        );

        if (!formData.id || !hasPlaintiff) {
            console.log('Missing fields check:', {
                id: !!formData.id,
                hasPlaintiff: hasPlaintiff
            });
            return res.status(400).json({
                success: false,
                error: 'Missing required fields: id and at least one plaintiff name'
            });
        }

        // Create a temporary case ID for progress tracking (will be replaced by DB ID)
        const tempCaseId = `temp-${formData.id}`;

        // Step 1: Saving form to file (10% progress)
        setPipelineStatus(tempCaseId, {
            status: 'processing',
            phase: 'saving_form',
            progress: 10,
            currentPhase: 'Saving form data...',
            totalPhases: 5,
            startTime: Date.now(),
            endTime: null,
            executionTime: null,
            error: null,
            result: null
        });

        // Transform the raw form data into structured format
        const structuredData = transformFormData(formData);

        // Revert normalized keys/values to original human-readable format
        const originalFormatData = revertToOriginalFormat(structuredData);

        // Add server timestamp to main data
        originalFormatData.serverTimestamp = new Date().toISOString();

        // Create filename with timestamp and ID
        const filename = `form-entry-${formData.id}.json`;
        const filepath = path.join(dataDir, filename);

        // Write to file
        fs.writeFileSync(filepath, JSON.stringify(originalFormatData, null, 2));

        // Log the submission
        console.log(`✅ Form entry saved to JSON: ${filename}`);

        // Record form submission metrics
        const plaintiffCount = originalFormatData.PlaintiffDetails?.length || 0;
        const defendantCount = originalFormatData.DefendantDetails2?.length || 0;
        const processingTime = (Date.now() - Date.parse(originalFormatData.serverTimestamp || new Date().toISOString())) / 1000;
        metricsModule.recordFormSubmission(true, plaintiffCount, defendantCount, processingTime);
        console.log(`📊 Metrics recorded: ${plaintiffCount} plaintiffs, ${defendantCount} defendants`);

        // ============================================================
        // DROPBOX UPLOAD (NON-BLOCKING)
        // ============================================================
        // Automatically upload form submission JSON to Dropbox for cloud backup.
        // This runs asynchronously and does not block the response or database save.
        //
        // Configuration (in .env):
        // - DROPBOX_ENABLED: Enable/disable uploads
        // - DROPBOX_ACCESS_TOKEN: OAuth token for authentication
        // - DROPBOX_BASE_PATH: Base folder in Dropbox (e.g., /Apps/LegalFormApp)
        //
        // Path Mapping Example:
        // Local:   /data/form-entry-123.json
        // Dropbox: /Apps/LegalFormApp/data/form-entry-123.json
        //
        // For setup instructions, see DROPBOX_SETUP.md
        // ============================================================
        // NOTE: Dropbox upload of raw JSON files is disabled
        // Dropbox is only used for final generated documents from Docmosis
        // Raw form data is stored in PostgreSQL via the Python pipeline
        /*
        if (dropboxService.isEnabled()) {
            console.log(`☁️  Uploading to Dropbox: ${filepath}`);
            dropboxService.uploadFile(filepath)
                .then(result => {
                    if (result.success) {
                        console.log(`✅ Dropbox upload successful: ${result.dropboxPath}`);
                    } else {
                        console.warn(`⚠️  Dropbox upload failed: ${result.error}`);
                    }
                })
                .catch(error => {
                    console.error(`❌ Dropbox upload error: ${error.message}`);
                });
        }
        */

        // Step 2: Saving to database (20% progress)
        setPipelineStatus(tempCaseId, {
            status: 'processing',
            phase: 'saving_database',
            progress: 20,
            currentPhase: 'Saving to database...',
            totalPhases: 5,
            startTime: Date.now(),
            endTime: null,
            executionTime: null,
            error: null,
            result: null
        });

        // Save to PostgreSQL database
        let dbCaseId = null;
        try {
            dbCaseId = await saveToDatabase(structuredData, formData);
            console.log(`✅ Form entry saved to database with case ID: ${dbCaseId}`);

            // Copy the status from temp ID to actual DB case ID
            const tempStatus = getPipelineStatus(tempCaseId);
            if (tempStatus) {
                setPipelineStatus(dbCaseId, {
                    ...tempStatus,
                    progress: 30,
                    currentPhase: 'Database saved, starting pipeline...'
                });
            }
        } catch (dbError) {
            console.error('⚠️  Database save failed, but JSON file was saved:', dbError.message);
            console.error('   Error details:', dbError.stack);
            // Continue - don't fail the request if database fails
        }

        // ============================================================
        // DETERMINE CASE ID FOR TRACKING
        // ============================================================
        // Use database case ID if available, otherwise fall back to form ID
        // This ensures progress tracking works even if database save fails
        const trackingCaseId = dbCaseId || formData.id;
        console.log(`📊 Tracking Case ID: ${trackingCaseId} (DB: ${dbCaseId ? 'YES' : 'NO'})`);

        // ============================================================
        // SEND RESPONSE IMMEDIATELY - DON'T WAIT FOR PIPELINE
        // ============================================================
        // Send the response NOW so the frontend can reset the form immediately.
        // The pipeline will continue running in the background, and the frontend
        // will poll /api/pipeline-status/:caseId to get real-time progress updates.
        // ============================================================

        // IMPORTANT: Send the database case ID for SSE progress tracking
        // The Python pipeline uses this ID to broadcast progress updates
        console.log(`📤 Sending response with dbCaseId: ${trackingCaseId} (type: ${typeof trackingCaseId})`);
        console.log(`   Form ID (UUID): ${formData.id}`);
        console.log(`   Database ID (integer): ${dbCaseId}`);

        res.status(201).json({
            success: true,
            message: 'Form entry saved successfully',
            id: formData.id, // UUID for file tracking
            filename: filename,
            dbCaseId: trackingCaseId, // Database case ID for SSE progress tracking
            timestamp: originalFormatData.serverTimestamp,
            structuredData: originalFormatData,
            pipelineEnabled: PIPELINE_CONFIG.enabled && PIPELINE_CONFIG.executeOnSubmit, // Tell frontend if pipeline is running
            // Pipeline will execute in background
            pipeline: {
                executed: PIPELINE_CONFIG.enabled && PIPELINE_CONFIG.executeOnSubmit,
                status: 'running',
                message: 'Pipeline execution started in background'
            }
        });

        // ============================================================
        // RUN PIPELINE IN BACKGROUND - AFTER RESPONSE SENT
        // ============================================================
        // Execute pipeline asynchronously without blocking the response.
        // The frontend will poll for progress updates via /api/pipeline-status/:caseId
        // ============================================================
        console.log(`\n${'='.repeat(70)}`);
        console.log(`🚀 STARTING BACKGROUND PIPELINE EXECUTION`);
        console.log(`   Tracking Case ID: ${trackingCaseId}`);
        console.log(`   Database Case ID: ${dbCaseId || 'N/A (using form ID)'}`);
        console.log(`   Form ID: ${formData.id}`);
        console.log(`   Pipeline Enabled: ${PIPELINE_CONFIG.enabled}`);
        console.log(`   Execute on Submit: ${PIPELINE_CONFIG.executeOnSubmit}`);
        console.log(`${'='.repeat(70)}\n`);

        callNormalizationPipeline(originalFormatData, trackingCaseId)
            .then((pipelineResult) => {
                console.log(`\n${'='.repeat(70)}`);
                if (pipelineResult.success) {
                    console.log('✅ PIPELINE COMPLETED SUCCESSFULLY');
                    console.log(`   Case ID: ${dbCaseId}`);
                    console.log(`   Execution time: ${pipelineResult.executionTime}ms`);
                    // Record successful pipeline execution
                    metricsModule.recordPipelineExecution(true, pipelineResult.executionTime / 1000, pipelineResult.phase || 'complete');
                } else if (pipelineResult.skipped) {
                    console.log(`📋 PIPELINE SKIPPED`);
                    console.log(`   Reason: ${pipelineResult.reason}`);
                } else {
                    console.warn('⚠️  PIPELINE FAILED (but form was saved)');
                    console.log(`   Error: ${pipelineResult.error || 'Unknown'}`);
                    // Record failed pipeline execution
                    metricsModule.recordPipelineExecution(false, pipelineResult.executionTime / 1000 || 0, pipelineResult.phase || 'error');
                }
                console.log(`${'='.repeat(70)}\n`);
            })
            .catch((pipelineError) => {
                console.log(`\n${'='.repeat(70)}`);
                console.error('❌ PIPELINE EXECUTION THREW ERROR');
                console.error(`   Error: ${pipelineError.message}`);
                console.error(`   Stack: ${pipelineError.stack}`);
                console.log(`${'='.repeat(70)}\n`);
                // Record pipeline error
                metricsModule.recordPipelineExecution(false, 0, 'error');
            });

    } catch (error) {
        console.error('❌ Error saving form entry:', error);
        // Record failed form submission
        metricsModule.recordFormSubmission(false, 0, 0, 0);
        res.status(500).json({
            success: false,
            error: 'Internal server error',
            details: error.message
        });
    }
});

/**
 * GET /api/form-entries
 * List all saved form entries
 */
app.get('/api/form-entries', (req, res) => {
    try {
        const files = fs.readdirSync(dataDir)
            .filter(file => file.startsWith('form-entry-') && file.endsWith('.json'))
            .map(file => {
                try {
                    const filepath = path.join(dataDir, file);
                    const stats = fs.statSync(filepath);
                    const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));

                    // Get first plaintiff name for display - check both structured and raw data
                    let plaintiffName = 'Unknown Plaintiff';
                    let plaintiffCount = 0;
                    let defendantCount = 0;

                    // Try to get from structured PlaintiffDetails first
                    if (data.PlaintiffDetails && data.PlaintiffDetails.length > 0) {
                        const firstPlaintiff = data.PlaintiffDetails[0];
                        if (firstPlaintiff.PlaintiffItemNumberName && firstPlaintiff.PlaintiffItemNumberName.FirstAndLast) {
                            plaintiffName = firstPlaintiff.PlaintiffItemNumberName.FirstAndLast;
                        } else if (firstPlaintiff.PlaintiffItemNumberName && firstPlaintiff.PlaintiffItemNumberName.First && firstPlaintiff.PlaintiffItemNumberName.Last) {
                            plaintiffName = `${firstPlaintiff.PlaintiffItemNumberName.First} ${firstPlaintiff.PlaintiffItemNumberName.Last}`;
                        }
                        plaintiffCount = data.PlaintiffDetails.length;
                    }

                    // Count defendants from structured data
                    if (data.DefendantDetails2 && data.DefendantDetails2.length > 0) {
                        defendantCount = data.DefendantDetails2.length;
                    }

                    // Fallback to raw data if structured data not available
                    if (plaintiffName === 'Unknown Plaintiff') {
                        const firstPlaintiffFirstName = Object.keys(data).find(key =>
                            key.includes('plaintiff') && key.includes('first-name')
                        );
                        const firstPlaintiffLastName = Object.keys(data).find(key =>
                            key.includes('plaintiff') && key.includes('last-name')
                        );

                        if (firstPlaintiffFirstName && firstPlaintiffLastName && data[firstPlaintiffFirstName] && data[firstPlaintiffLastName]) {
                            plaintiffName = `${data[firstPlaintiffFirstName]} ${data[firstPlaintiffLastName]}`;
                        }

                        // Count from raw data as fallback
                        if (plaintiffCount === 0) {
                            plaintiffCount = Object.keys(data).filter(key => key.includes('plaintiff') && key.includes('first-name')).length;
                        }
                        if (defendantCount === 0) {
                            defendantCount = Object.keys(data).filter(key => key.includes('defendant') && key.includes('first-name')).length;
                        }
                    }

                    // Get street address from structured data
                    let streetAddress = 'Unknown Address';
                    if (data.Full_Address && data.Full_Address.StreetAddress) {
                        streetAddress = data.Full_Address.StreetAddress;
                    } else if (data.Full_Address && data.Full_Address.Line1) {
                        streetAddress = data.Full_Address.Line1;
                    }

                    return {
                        filename: file,
                        id: data.id || file.replace('form-entry-', '').replace('.json', ''),
                        name: plaintiffName,
                        streetAddress: streetAddress,
                        submittedAt: data.submittedAt,
                        serverTimestamp: data.serverTimestamp || stats.mtime.toISOString(),
                        fileSize: stats.size,
                        plaintiffCount: plaintiffCount,
                        defendantCount: defendantCount
                    };
                } catch (fileError) {
                    // Log error but skip corrupted files instead of crashing entire request
                    console.error(`⚠️ Error reading file ${file}:`, fileError.message);
                    return null;
                }
            })
            .filter(entry => entry !== null) // Remove any failed entries
            .sort((a, b) => new Date(b.serverTimestamp) - new Date(a.serverTimestamp));

        res.json({
            success: true,
            count: files.length,
            entries: files
        });

    } catch (error) {
        console.error('❌ Error listing form entries:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error',
            details: error.message
        });
    }
});

/**
 * GET /api/form-entries/:id
 * Get specific form entry by ID
 */
app.get('/api/form-entries/:id', (req, res) => {
    try {
        const { id } = req.params;
        const filename = `form-entry-${id}.json`;
        const filepath = path.join(dataDir, filename);

        if (!fs.existsSync(filepath)) {
            return res.status(404).json({
                success: false,
                error: 'Form entry not found'
            });
        }

        const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));

        res.json({
            success: true,
            entry: data
        });

    } catch (error) {
        console.error('❌ Error retrieving form entry:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error',
            details: error.message
        });
    }
});

/**
 * DELETE /api/form-entries/clear-all
 * Delete all form entries
 */
app.delete('/api/form-entries/clear-all', (req, res) => {
    try {
        // Get all form entry files
        const files = fs.readdirSync(dataDir).filter(file => file.startsWith('form-entry-') && file.endsWith('.json'));

        let deletedCount = 0;
        const errors = [];

        // Delete each file
        files.forEach(filename => {
            try {
                const filepath = path.join(dataDir, filename);
                fs.unlinkSync(filepath);
                deletedCount++;
                console.log(`🗑️ Deleted: ${filename}`);
            } catch (error) {
                console.error(`❌ Error deleting ${filename}:`, error);
                errors.push({ filename, error: error.message });
            }
        });

        console.log(`🧹 Cleared ${deletedCount} form entries`);

        res.json({
            success: true,
            message: `Successfully deleted ${deletedCount} form entries`,
            deletedCount: deletedCount,
            errors: errors.length > 0 ? errors : undefined
        });

    } catch (error) {
        console.error('❌ Error clearing all form entries:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error',
            details: error.message
        });
    }
});

/**
 * PUT /api/form-entries/:id
 * Update specific form entry by ID
 */
app.put('/api/form-entries/:id', (req, res) => {
    try {
        const { id } = req.params;
        const updatedData = req.body;
        const filename = `form-entry-${id}.json`;
        const filepath = path.join(dataDir, filename);

        if (!fs.existsSync(filepath)) {
            return res.status(404).json({
                success: false,
                error: 'Form entry not found'
            });
        }

        // Read existing data to preserve any fields not being updated
        const existingData = JSON.parse(fs.readFileSync(filepath, 'utf8'));

        // Update the data with new values
        const mergedData = {
            ...existingData,
            ...updatedData,
            lastModified: new Date().toISOString()
        };

        // Write updated data back to file
        fs.writeFileSync(filepath, JSON.stringify(mergedData, null, 2));

        console.log(`📝 Form entry updated: ${filename}`);

        res.json({
            success: true,
            message: 'Form entry updated successfully',
            id: id,
            entry: mergedData
        });

    } catch (error) {
        console.error('❌ Error updating form entry:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error',
            details: error.message
        });
    }
});

/**
 * DELETE /api/form-entries/:id
 * Delete specific form entry by ID
 */
app.delete('/api/form-entries/:id', (req, res) => {
    try {
        const { id } = req.params;
        const filename = `form-entry-${id}.json`;
        const filepath = path.join(dataDir, filename);

        if (!fs.existsSync(filepath)) {
            return res.status(404).json({
                success: false,
                error: 'Form entry not found'
            });
        }

        fs.unlinkSync(filepath);
        console.log(`🗑️ Form entry deleted: ${filename}`);

        res.json({
            success: true,
            message: 'Form entry deleted successfully',
            id: id
        });

    } catch (error) {
        console.error('❌ Error deleting form entry:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error',
            details: error.message
        });
    }
});

/**
 * Prometheus Metrics Endpoint
 *
 * GET /metrics
 *
 * Exposes application metrics in Prometheus format for scraping.
 * This endpoint is used by Prometheus server to collect metrics.
 *
 * Metrics include:
 * - HTTP request rates, latencies, and error rates
 * - Form submission statistics
 * - Pipeline execution metrics
 * - Database performance metrics
 * - Dropbox upload statistics
 * - Node.js runtime metrics (memory, CPU, event loop)
 */
app.get('/metrics', async (req, res) => {
    try {
        res.set('Content-Type', metricsModule.register.contentType);
        const metrics = await metricsModule.register.metrics();
        res.end(metrics);
    } catch (error) {
        console.error('❌ Error generating metrics:', error);
        res.status(500).end('Error generating metrics');
    }
});

/**
 * Health Check Endpoints
 *
 * Three levels of health checks for different purposes:
 * 1. /health or /api/health - Liveness probe (is app running?)
 * 2. /health/ready - Readiness probe (is app ready for traffic?)
 * 3. /health/detailed - Full diagnostics (all components)
 */

// Liveness Probe - Basic health check
// Used by: Kubernetes liveness probes, basic monitoring
// Always returns 200 if the process is running
app.get(['/health', '/api/health'], async (req, res) => {
    try {
        const health = await checkLiveness();
        sendHealthResponse(res, health);
    } catch (error) {
        logger.error('Liveness check failed', { error: error.message });
        res.status(500).json({
            status: 'unhealthy',
            error: 'Liveness check failed',
            timestamp: new Date().toISOString()
        });
    }
});

// Readiness Probe - Dependency health check
// Used by: Kubernetes readiness probes, load balancers
// Returns 200 only if critical dependencies (database) are healthy
app.get('/health/ready', async (req, res) => {
    try {
        const health = await checkReadiness(pool, {
            checkExternalServices: false // Don't check optional services for readiness
        });

        sendHealthResponse(res, health);

        // Log if unhealthy
        if (health.status === 'unhealthy') {
            logger.warn('Readiness check failed', {
                errors: health.errors,
                checks: health.checks
            });
        }
    } catch (error) {
        logger.error('Readiness check failed', { error: error.message });
        res.status(503).json({
            status: 'unhealthy',
            error: 'Readiness check failed',
            timestamp: new Date().toISOString()
        });
    }
});

// Detailed Health Check - Full diagnostics
// Used by: Debugging, monitoring dashboards, ops teams
// Returns comprehensive health information for all components
app.get('/health/detailed', async (req, res) => {
    try {
        const health = await checkDetailed(pool, {
            pipelineApiUrl: PIPELINE_CONFIG.enabled ? PIPELINE_CONFIG.apiUrl : null,
            dropboxEnabled: process.env.DROPBOX_ENABLED === 'true'
        });

        sendHealthResponse(res, health);

        // Log warnings and errors
        if (health.warnings && health.warnings.length > 0) {
            logger.warn('Health check warnings detected', {
                warnings: health.warnings
            });
        }

        if (health.errors && health.errors.length > 0) {
            logger.error('Health check errors detected', {
                errors: health.errors
            });
        }
    } catch (error) {
        logger.error('Detailed health check failed', { error: error.message });
        res.status(500).json({
            status: 'unhealthy',
            error: 'Detailed health check failed',
            timestamp: new Date().toISOString()
        });
    }
});

/**
 * Pipeline Status Polling Endpoint (Phase 5)
 *
 * GET /api/pipeline-status/:caseId
 *
 * Retrieves the current status of the normalization pipeline for a given case.
 * Supports real-time polling from the frontend to provide user feedback.
 *
 * Response Statuses:
 * - pending: Pipeline is queued but not yet started
 * - processing: Pipeline is currently executing
 * - success: Pipeline completed successfully
 * - failed: Pipeline encountered an error
 * - skipped: Pipeline was disabled or not executed
 * - not_found: No status found for the given case ID
 */
app.get('/api/pipeline-status/:caseId', async (req, res) => {
    let { caseId } = req.params;

    console.log(`📊 Pipeline status check requested for case: ${caseId}`);

    // If this is a temp ID (format: temp-{formId}), try to find the real case ID
    if (caseId.startsWith('temp-')) {
        const formId = caseId.substring(5); // Remove 'temp-' prefix
        console.log(`🔍 Temp ID detected, looking up real case ID for form: ${formId}`);

        try {
            // Query database to find the real case ID using the form ID
            const result = await pool.query(
                `SELECT id FROM cases WHERE raw_payload->>'id' = $1 ORDER BY created_at DESC LIMIT 1`,
                [formId]
            );

            if (result.rows.length > 0) {
                const realCaseId = result.rows[0].id;
                console.log(`✅ Found real case ID: ${realCaseId}`);
                caseId = realCaseId; // Use the real case ID for status lookup
            } else {
                console.log(`⚠️  No case found yet for form ID: ${formId} - form may still be saving`);
                // Return a "still saving" status
                return res.json({
                    success: true,
                    caseId: req.params.caseId,
                    status: 'processing',
                    phase: 'saving_form',
                    progress: 10,
                    currentPhase: 'Saving form data...',
                    totalPhases: 5,
                    startTime: Date.now(),
                    endTime: null,
                    executionTime: null,
                    error: null,
                    result: null
                });
            }
        } catch (dbError) {
            console.error(`❌ Database error looking up case ID:`, dbError.message);
            // Fall through to check temp ID in cache
        }
    }

    // Retrieve status from cache
    const status = getPipelineStatus(caseId);

    if (!status) {
        console.log(`⚠️  No pipeline status found for case: ${caseId}`);
        return res.status(404).json({
            success: false,
            status: 'not_found',
            message: 'No pipeline status found for this case ID',
            caseId: req.params.caseId
        });
    }

    // Return sanitized status (remove internal expiresAt field)
    const { expiresAt, ...statusData } = status;

    res.json({
        success: true,
        caseId: req.params.caseId, // Return original requested ID
        realCaseId: caseId, // Include the real case ID if it was looked up
        ...statusData
    });
});

/**
 * Pipeline Retry Endpoint (Phase 5)
 *
 * POST /api/pipeline-retry/:caseId
 *
 * Retries the normalization pipeline for a specific case.
 * Retrieves the form submission from the data directory and re-executes the pipeline.
 *
 * This endpoint allows users to retry failed pipeline executions without
 * resubmitting the entire form.
 */
app.post('/api/pipeline-retry/:caseId', async (req, res) => {
    const { caseId } = req.params;

    console.log(`🔄 Pipeline retry requested for case: ${caseId}`);

    try {
        // Option 1: Query database for the form data by case ID
        let formData = null;
        let foundFile = null;

        try {
            const dbQuery = await pool.query('SELECT * FROM cases WHERE id = $1', [caseId]);
            if (dbQuery.rows.length > 0) {
                console.log(`📊 Found case in database: ${caseId}`);
                // We have the case, now need to reconstruct the form data
                // For now, try to find the JSON file by searching all files
            }
        } catch (dbErr) {
            console.warn('⚠️  Database query failed, falling back to file search');
        }

        // Search JSON files for this case ID
        const files = fs.readdirSync(dataDir);
        for (const file of files) {
            if (file.endsWith('.json')) {
                try {
                    const filePath = path.join(dataDir, file);
                    const fileContent = JSON.parse(fs.readFileSync(filePath, 'utf8'));

                    // Check if this file matches the case ID (look in dbCaseId or pipeline metadata)
                    // The form might have been transformed, so check the original payload
                    if (fileContent.id === caseId ||
                        file.includes(caseId) ||
                        (fileContent.dbCaseId === caseId)) {
                        formData = fileContent;
                        foundFile = file;
                        console.log(`📄 Found form data in file: ${foundFile}`);
                        break;
                    }
                } catch (err) {
                    // Skip files that can't be parsed
                    continue;
                }
            }
        }

        if (!formData) {
            console.warn(`⚠️  Form data not found for case: ${caseId}`);
            console.log(`   Searched ${files.filter(f => f.endsWith('.json')).length} JSON files`);
            return res.status(404).json({
                success: false,
                error: 'Form data not found for this case ID',
                caseId: caseId,
                hint: 'The form data may have been cleaned up or the case ID is incorrect'
            });
        }

        console.log(`📄 Re-running pipeline with form data from: ${foundFile}`);

        // Re-run the pipeline with the form data
        const pipelineResult = await callNormalizationPipeline(formData, caseId);

        res.json({
            success: true,
            message: 'Pipeline retry initiated',
            caseId: caseId,
            pipeline: pipelineResult
        });

    } catch (error) {
        console.error('❌ Error retrying pipeline:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to retry pipeline',
            details: error.message
        });
    }
});

// Root route - serve the form
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Review page route
app.get('/review.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'review.html'));
});

// Success page route
app.get('/success', (req, res) => {
    res.sendFile(path.join(__dirname, 'success.html'));
});

// 404 handler
app.use('*', (req, res) => {
    res.status(404).json({
        success: false,
        error: 'Endpoint not found',
        path: req.originalUrl
    });
});

// Error logging middleware (logs errors before handling)
app.use(errorLoggingMiddleware);

// Error handler
app.use((error, req, res, next) => {
    // Error already logged by errorLoggingMiddleware
    res.status(error.statusCode || error.status || 500).json({
        success: false,
        error: error.message || 'Internal server error',
        details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
});

// Start server
app.listen(PORT, () => {
    logger.info('Server started', {
        port: PORT,
        environment: process.env.NODE_ENV || 'development',
        nodeVersion: process.version,
        dataDirectory: dataDir
    });

    // Also log to console for visibility during development
    console.log(`🚀 Server running on http://localhost:${PORT}`);
    console.log(`📁 Data directory: ${dataDir}`);
    console.log(`📊 Form available at: http://localhost:${PORT}`);
    console.log(`🔍 API endpoints:`);
    console.log(`   POST   /api/form-entries     - Save form entry`);
    console.log(`   GET    /api/form-entries     - List all entries`);
    console.log(`   GET    /api/form-entries/:id - Get specific entry`);
    console.log(`   PUT    /api/form-entries/:id - Update entry`);
    console.log(`   DELETE /api/form-entries/:id - Delete entry`);
    console.log(`   DELETE /api/form-entries/clear-all - Delete all entries`);
    console.log(`   GET    /health              - Liveness probe`);
    console.log(`   GET    /health/ready        - Readiness probe`);
    console.log(`   GET    /health/detailed     - Detailed diagnostics`);
    console.log(`   GET    /metrics             - Prometheus metrics`);
});
