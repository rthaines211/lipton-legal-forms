/**
 * Winston Logging Middleware
 *
 * Express middleware for structured request/response logging.
 * Provides request correlation tracking and automatic logging.
 *
 * Features:
 * - Generates unique request IDs (UUID v4)
 * - Logs all HTTP requests and responses
 * - Tracks request duration
 * - Attaches logger to request object
 * - Captures response status codes
 * - Non-blocking log writes
 *
 * Usage:
 *   const { requestLoggingMiddleware } = require('./monitoring/log-middleware');
 *   app.use(requestLoggingMiddleware);
 *
 * Access logger in routes:
 *   app.get('/route', (req, res) => {
 *     req.logger.info('Processing request', { someData: 'value' });
 *   });
 */

const logger = require('./logger');
const { v4: uuidv4 } = require('crypto').randomUUID ?
    { v4: () => require('crypto').randomUUID() } :
    require('uuid');

// ============================================================================
// REQUEST ID GENERATION
// ============================================================================

/**
 * Generates a unique request ID
 * Uses crypto.randomUUID() if available (Node 16.7+), falls back to uuid package
 */
function generateRequestId() {
    try {
        // Use built-in crypto.randomUUID if available (Node 16.7+)
        if (require('crypto').randomUUID) {
            return require('crypto').randomUUID();
        }
    } catch (error) {
        // Fall back to generating a simple UUID
    }

    // Simple UUID v4 implementation (fallback)
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// ============================================================================
// REQUEST LOGGING MIDDLEWARE
// ============================================================================

/**
 * Request Logging Middleware Factory
 *
 * Creates Express middleware that:
 * 1. Generates unique request ID
 * 2. Logs incoming request
 * 3. Attaches scoped logger to request
 * 4. Logs response with duration
 */
function createRequestLoggingMiddleware(options = {}) {
    const {
        // Skip logging for certain paths
        skipPaths = ['/health', '/metrics'],
        // Log level for requests
        logLevel = 'http',
        // Include request body in logs (be careful with sensitive data)
        includeBody = false,
        // Include query parameters
        includeQuery = true,
        // Include request headers
        includeHeaders = false
    } = options;

    return function requestLoggingMiddleware(req, res, next) {
        // Generate request ID
        req.requestId = generateRequestId();

        // Attach scoped logger to request
        req.logger = logger.withRequestId(req.requestId);

        // Record start time
        const startTime = Date.now();

        // Skip logging for certain paths
        const shouldSkip = skipPaths.some(path => req.path.startsWith(path));

        if (!shouldSkip) {
            // Log incoming request
            const requestLog = {
                requestId: req.requestId,
                method: req.method,
                path: req.path,
                originalUrl: req.originalUrl,
                ip: req.ip || req.connection.remoteAddress,
                userAgent: req.get('user-agent')
            };

            if (includeQuery && Object.keys(req.query).length > 0) {
                requestLog.query = req.query;
            }

            if (includeBody && req.body && Object.keys(req.body).length > 0) {
                // Be careful with sensitive data!
                requestLog.bodySize = JSON.stringify(req.body).length;
            }

            if (includeHeaders) {
                requestLog.headers = {
                    contentType: req.get('content-type'),
                    contentLength: req.get('content-length'),
                    accept: req.get('accept')
                };
            }

            logger[logLevel]('Incoming request', requestLog);
        }

        // Capture response
        const originalSend = res.send;
        const originalJson = res.json;

        // Override res.send to capture response
        res.send = function(data) {
            res.send = originalSend;
            logResponse(req, res, startTime, data, shouldSkip);
            return originalSend.call(this, data);
        };

        // Override res.json to capture response
        res.json = function(data) {
            res.json = originalJson;
            logResponse(req, res, startTime, data, shouldSkip);
            return originalJson.call(this, data);
        };

        // Also log when response finishes (catches cases where send/json aren't called)
        res.on('finish', () => {
            if (!res.logged) {
                logResponse(req, res, startTime, null, shouldSkip);
            }
        });

        next();
    };
}

/**
 * Log response details
 */
function logResponse(req, res, startTime, data, shouldSkip) {
    // Prevent double logging
    if (res.logged) return;
    res.logged = true;

    if (shouldSkip) return;

    const duration = Date.now() - startTime;
    const statusCode = res.statusCode;

    const responseLog = {
        requestId: req.requestId,
        method: req.method,
        path: req.path,
        statusCode: statusCode,
        duration: duration,
        contentLength: res.get('content-length') || (data ? JSON.stringify(data).length : 0)
    };

    // Determine log level based on status code
    let level = 'http';
    if (statusCode >= 500) {
        level = 'error';
    } else if (statusCode >= 400) {
        level = 'warn';
    }

    logger[level]('Request completed', responseLog);

    // Also log slow requests as warnings
    if (duration > 1000) { // Slower than 1 second
        logger.warn('Slow request detected', {
            requestId: req.requestId,
            path: req.path,
            duration: duration,
            threshold: 1000
        });
    }
}

// ============================================================================
// ERROR LOGGING MIDDLEWARE
// ============================================================================

/**
 * Error Logging Middleware
 *
 * Logs uncaught errors with full stack traces.
 * Should be added after all routes but before final error handler.
 *
 * Usage:
 *   app.use(errorLoggingMiddleware);
 *   app.use((err, req, res, next) => { ... }); // Your error handler
 */
function errorLoggingMiddleware(err, req, res, next) {
    const errorLog = {
        requestId: req.requestId,
        method: req.method,
        path: req.path,
        error: {
            message: err.message,
            stack: err.stack,
            code: err.code,
            statusCode: err.statusCode || err.status
        }
    };

    // Log error with full stack trace
    logger.error('Request error', errorLog);

    // Continue to next error handler
    next(err);
}

// ============================================================================
// CORRELATION ID EXTRACTOR
// ============================================================================

/**
 * Extract or Generate Correlation ID Middleware
 *
 * Checks for existing correlation ID in headers (from upstream services)
 * or generates a new one. Useful in microservices architectures.
 *
 * Headers checked (in order):
 * - x-request-id
 * - x-correlation-id
 * - x-trace-id
 */
function correlationIdMiddleware(req, res, next) {
    // Check for existing correlation ID in headers
    req.requestId =
        req.get('x-request-id') ||
        req.get('x-correlation-id') ||
        req.get('x-trace-id') ||
        generateRequestId();

    // Add correlation ID to response headers for client tracking
    res.setHeader('x-request-id', req.requestId);

    next();
}

// ============================================================================
// REQUEST CONTEXT LOGGER
// ============================================================================

/**
 * Creates a child logger with request context
 *
 * Useful for logging in async operations that don't have access to req object
 */
function createContextLogger(context = {}) {
    return {
        info: (message, meta = {}) => logger.info(message, { ...context, ...meta }),
        error: (message, meta = {}) => logger.error(message, { ...context, ...meta }),
        warn: (message, meta = {}) => logger.warn(message, { ...context, ...meta }),
        debug: (message, meta = {}) => logger.debug(message, { ...context, ...meta }),
        http: (message, meta = {}) => logger.http(message, { ...context, ...meta })
    };
}

// ============================================================================
// EXPORTS
// ============================================================================

module.exports = {
    // Main middleware
    requestLoggingMiddleware: createRequestLoggingMiddleware(),

    // Configurable middleware factory
    createRequestLoggingMiddleware,

    // Error logging
    errorLoggingMiddleware,

    // Correlation ID
    correlationIdMiddleware,

    // Utilities
    generateRequestId,
    createContextLogger
};
