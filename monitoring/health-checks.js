/**
 * Health Check Module
 *
 * Provides comprehensive health checks for the Legal Form Application.
 * Implements multiple health check endpoints suitable for different purposes:
 *
 * - Liveness Probe: Is the application running?
 * - Readiness Probe: Is the application ready to serve traffic?
 * - Detailed Health: Full diagnostic information
 *
 * Designed for:
 * - Kubernetes/Docker health checks
 * - GCP Load Balancer health probes
 * - Monitoring systems (Prometheus, Datadog, etc.)
 * - Developer debugging
 *
 * Usage:
 *   const { checkLiveness, checkReadiness, checkDetailed } = require('./monitoring/health-checks');
 *
 *   app.get('/health', async (req, res) => {
 *     const health = await checkLiveness();
 *     res.status(health.status === 'healthy' ? 200 : 503).json(health);
 *   });
 */

const logger = require('./logger');

// ============================================================================
// CONFIGURATION
// ============================================================================

const HEALTH_CHECK_TIMEOUT = 5000; // 5 seconds max for health checks

// ============================================================================
// LIVENESS PROBE
// ============================================================================

/**
 * Basic Liveness Check
 *
 * Answers: "Is the application process running?"
 * Use for: Kubernetes liveness probes, basic monitoring
 *
 * This check should ALWAYS return healthy if the process is running.
 * It does not check dependencies - only that the app is alive.
 *
 * Returns: { status: 'healthy', timestamp, uptime }
 */
async function checkLiveness() {
    return {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        service: process.env.SERVICE_NAME || 'legal-form-app',
        version: process.env.APP_VERSION || '1.0.0',
        environment: process.env.NODE_ENV || 'development'
    };
}

// ============================================================================
// READINESS PROBE
// ============================================================================

/**
 * Readiness Check
 *
 * Answers: "Is the application ready to serve traffic?"
 * Use for: Kubernetes readiness probes, load balancer health checks
 *
 * Checks critical dependencies:
 * - Database connection
 * - (Optional) External API availability
 *
 * Returns 'healthy' only if ALL critical dependencies are available.
 * Returns 'unhealthy' if any critical dependency is down.
 *
 * @param {Object} pool - PostgreSQL connection pool
 * @param {Object} options - Optional configuration
 * @returns {Promise<Object>} Health status
 */
async function checkReadiness(pool, options = {}) {
    const {
        checkExternalServices = false,
        pipelineApiUrl = null,
        dropboxEnabled = false
    } = options;

    const checks = {};
    let overallStatus = 'healthy';
    const errors = [];

    // Critical Check: Database
    try {
        const dbHealth = await checkDatabase(pool);
        checks.database = dbHealth;

        if (dbHealth.status !== 'healthy') {
            overallStatus = 'unhealthy';
            errors.push(`Database: ${dbHealth.error}`);
        }
    } catch (error) {
        checks.database = {
            status: 'unhealthy',
            error: error.message
        };
        overallStatus = 'unhealthy';
        errors.push(`Database: ${error.message}`);
    }

    // Optional Check: External Services
    if (checkExternalServices) {
        // Check Pipeline API (non-critical)
        if (pipelineApiUrl) {
            try {
                const pipelineHealth = await checkPipelineAPI(pipelineApiUrl);
                checks.pipeline = pipelineHealth;
                // Note: Pipeline is non-critical, so we don't fail readiness
            } catch (error) {
                checks.pipeline = {
                    status: 'unhealthy',
                    error: error.message
                };
            }
        }

        // Check Dropbox (non-critical)
        if (dropboxEnabled) {
            try {
                const dropboxHealth = await checkDropbox();
                checks.dropbox = dropboxHealth;
                // Note: Dropbox is non-critical, so we don't fail readiness
            } catch (error) {
                checks.dropbox = {
                    status: 'unhealthy',
                    error: error.message
                };
            }
        }
    }

    return {
        status: overallStatus,
        timestamp: new Date().toISOString(),
        checks,
        errors: errors.length > 0 ? errors : undefined
    };
}

// ============================================================================
// DETAILED HEALTH CHECK
// ============================================================================

/**
 * Detailed Health Check
 *
 * Answers: "What is the full health status of all components?"
 * Use for: Debugging, monitoring dashboards, diagnostics
 *
 * Checks ALL dependencies and provides detailed information:
 * - Application info (version, uptime, memory)
 * - Database (connection, pool stats, query performance)
 * - External services (Pipeline API, Dropbox)
 * - System resources (memory, CPU)
 *
 * @param {Object} pool - PostgreSQL connection pool
 * @param {Object} options - Configuration options
 * @returns {Promise<Object>} Detailed health information
 */
async function checkDetailed(pool, options = {}) {
    const {
        pipelineApiUrl = null,
        dropboxEnabled = false
    } = options;

    const checks = {};
    let overallStatus = 'healthy';
    const warnings = [];
    const errors = [];

    // Application Info
    checks.application = {
        status: 'healthy',
        name: process.env.SERVICE_NAME || 'legal-form-app',
        version: process.env.APP_VERSION || '1.0.0',
        environment: process.env.NODE_ENV || 'development',
        uptime: process.uptime(),
        nodeVersion: process.version,
        platform: process.platform,
        pid: process.pid
    };

    // System Resources
    const memUsage = process.memoryUsage();
    checks.system = {
        status: 'healthy',
        memory: {
            heapUsed: Math.round(memUsage.heapUsed / 1024 / 1024) + ' MB',
            heapTotal: Math.round(memUsage.heapTotal / 1024 / 1024) + ' MB',
            external: Math.round(memUsage.external / 1024 / 1024) + ' MB',
            rss: Math.round(memUsage.rss / 1024 / 1024) + ' MB'
        },
        cpuUsage: process.cpuUsage()
    };

    // Warn on high memory usage (>500MB heap)
    if (memUsage.heapUsed > 500 * 1024 * 1024) {
        checks.system.status = 'warning';
        warnings.push('High memory usage detected');
    }

    // Database Check (Critical)
    try {
        const dbHealth = await checkDatabase(pool);
        checks.database = dbHealth;

        if (dbHealth.status === 'unhealthy') {
            overallStatus = 'unhealthy';
            errors.push(`Database: ${dbHealth.error}`);
        } else if (dbHealth.status === 'warning') {
            if (overallStatus === 'healthy') {
                overallStatus = 'warning';
            }
            warnings.push(`Database: ${dbHealth.warning}`);
        }

        // Get pool stats if available
        if (pool.totalCount !== undefined) {
            checks.database.pool = {
                total: pool.totalCount,
                idle: pool.idleCount,
                waiting: pool.waitingCount
            };

            // Warn if pool is exhausted
            if (pool.waitingCount > 0) {
                checks.database.status = 'warning';
                checks.database.warning = 'Connection pool has waiting queries';
                if (overallStatus === 'healthy') {
                    overallStatus = 'warning';
                }
                warnings.push('Database connection pool under pressure');
            }
        }
    } catch (error) {
        checks.database = {
            status: 'unhealthy',
            error: error.message
        };
        overallStatus = 'unhealthy';
        errors.push(`Database: ${error.message}`);
    }

    // Pipeline API Check (Non-Critical)
    if (pipelineApiUrl) {
        try {
            const pipelineHealth = await checkPipelineAPI(pipelineApiUrl);
            checks.pipeline = pipelineHealth;

            if (pipelineHealth.status === 'unhealthy') {
                warnings.push(`Pipeline API: ${pipelineHealth.error}`);
            }
        } catch (error) {
            checks.pipeline = {
                status: 'unhealthy',
                error: error.message
            };
            warnings.push(`Pipeline API: ${error.message}`);
        }
    }

    // Dropbox Check (Non-Critical)
    if (dropboxEnabled) {
        try {
            const dropboxHealth = await checkDropbox();
            checks.dropbox = dropboxHealth;

            if (dropboxHealth.status === 'unhealthy') {
                warnings.push(`Dropbox: ${dropboxHealth.error}`);
            }
        } catch (error) {
            checks.dropbox = {
                status: 'unhealthy',
                error: error.message
            };
            warnings.push(`Dropbox: ${error.message}`);
        }
    }

    return {
        status: overallStatus,
        timestamp: new Date().toISOString(),
        checks,
        warnings: warnings.length > 0 ? warnings : undefined,
        errors: errors.length > 0 ? errors : undefined
    };
}

// ============================================================================
// INDIVIDUAL HEALTH CHECKS
// ============================================================================

/**
 * Check Database Health
 *
 * Tests PostgreSQL connection by executing a simple query.
 * Measures response time and checks for errors.
 *
 * @param {Object} pool - PostgreSQL connection pool
 * @returns {Promise<Object>} Database health status
 */
async function checkDatabase(pool) {
    const start = Date.now();

    try {
        // Simple query to test connection
        const result = await Promise.race([
            pool.query('SELECT NOW() as now, version() as version'),
            new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Database query timeout')), HEALTH_CHECK_TIMEOUT)
            )
        ]);

        const responseTime = Date.now() - start;

        // Warn if query is slow (>100ms for a simple query is concerning)
        const status = responseTime > 100 ? 'warning' : 'healthy';
        const warning = responseTime > 100 ? 'Slow database response time' : undefined;

        return {
            status,
            responseTime: `${responseTime}ms`,
            connected: true,
            timestamp: result.rows[0].now,
            warning
        };
    } catch (error) {
        const responseTime = Date.now() - start;

        logger.error('Database health check failed', {
            error: error.message,
            responseTime: `${responseTime}ms`
        });

        return {
            status: 'unhealthy',
            responseTime: `${responseTime}ms`,
            connected: false,
            error: error.message
        };
    }
}

/**
 * Check Pipeline API Health
 *
 * Tests connectivity to the Python normalization pipeline API.
 * Attempts to call the health endpoint if available.
 *
 * @param {string} apiUrl - Pipeline API base URL
 * @returns {Promise<Object>} Pipeline API health status
 */
async function checkPipelineAPI(apiUrl) {
    const start = Date.now();

    try {
        const axios = require('axios');

        // Try to call the health endpoint
        const response = await Promise.race([
            axios.get(`${apiUrl}/health`, { timeout: HEALTH_CHECK_TIMEOUT }),
            new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Pipeline API timeout')), HEALTH_CHECK_TIMEOUT)
            )
        ]);

        const responseTime = Date.now() - start;

        return {
            status: 'healthy',
            responseTime: `${responseTime}ms`,
            available: true,
            url: apiUrl,
            version: response.data?.version || 'unknown'
        };
    } catch (error) {
        const responseTime = Date.now() - start;

        // Pipeline API being down is not critical (it's optional)
        return {
            status: 'unhealthy',
            responseTime: `${responseTime}ms`,
            available: false,
            url: apiUrl,
            error: error.code === 'ECONNREFUSED' ?
                'Connection refused - API may not be running' :
                error.message
        };
    }
}

/**
 * Check Dropbox Health
 *
 * Tests Dropbox API connectivity.
 * Note: This is a lightweight check - full auth check would be expensive.
 *
 * @returns {Promise<Object>} Dropbox health status
 */
async function checkDropbox() {
    try {
        // Check if Dropbox is configured
        const dropboxEnabled = process.env.DROPBOX_ENABLED === 'true';
        const dropboxToken = process.env.DROPBOX_ACCESS_TOKEN;

        if (!dropboxEnabled) {
            return {
                status: 'disabled',
                message: 'Dropbox integration is disabled'
            };
        }

        if (!dropboxToken) {
            return {
                status: 'unhealthy',
                error: 'Dropbox access token not configured'
            };
        }

        // If we have a token, assume healthy
        // Full API check would be too expensive for health checks
        return {
            status: 'healthy',
            configured: true,
            message: 'Dropbox configured (token present)'
        };
    } catch (error) {
        return {
            status: 'unhealthy',
            error: error.message
        };
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get HTTP Status Code from Health Status
 *
 * Maps health status to appropriate HTTP status codes:
 * - healthy: 200 OK
 * - warning: 200 OK (still serving traffic)
 * - unhealthy: 503 Service Unavailable
 *
 * @param {string} status - Health status string
 * @returns {number} HTTP status code
 */
function getHttpStatusCode(status) {
    switch (status) {
        case 'healthy':
            return 200;
        case 'warning':
            return 200; // Still operational, just warning
        case 'unhealthy':
            return 503;
        default:
            return 500;
    }
}

/**
 * Format Health Check Response
 *
 * Adds standard headers and formatting to health check responses.
 * Makes responses consistent and easy to parse.
 *
 * @param {Object} health - Health check result
 * @param {Object} res - Express response object
 */
function sendHealthResponse(res, health) {
    const statusCode = getHttpStatusCode(health.status);

    res.status(statusCode)
        .set('Cache-Control', 'no-cache, no-store, must-revalidate')
        .set('Pragma', 'no-cache')
        .set('Expires', '0')
        .json(health);
}

// ============================================================================
// EXPORTS
// ============================================================================

module.exports = {
    // Main health check functions
    checkLiveness,
    checkReadiness,
    checkDetailed,

    // Individual check functions (for custom use)
    checkDatabase,
    checkPipelineAPI,
    checkDropbox,

    // Utility functions
    getHttpStatusCode,
    sendHealthResponse
};
