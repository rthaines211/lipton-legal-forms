/**
 * Winston Structured Logger
 *
 * Provides structured JSON logging with multiple transports and log levels.
 * Designed for both local development and production (GCP Cloud Logging ready).
 *
 * Features:
 * - Structured JSON format for machine parsing
 * - Human-readable console output in development
 * - Daily log rotation with size limits
 * - Multiple log levels (error, warn, info, http, debug)
 * - Request correlation tracking
 * - Error stack traces
 * - Metadata support
 *
 * Log Levels (priority):
 * - error: 0 - Critical errors requiring immediate attention
 * - warn: 1 - Warning messages about potential issues
 * - info: 2 - General informational messages
 * - http: 3 - HTTP request/response logs
 * - debug: 4 - Detailed debugging information
 *
 * Usage:
 *   const logger = require('./monitoring/logger');
 *   logger.info('Form submission received', { plaintiffs: 2, defendants: 1 });
 *   logger.error('Database connection failed', { error: err.message });
 */

const winston = require('winston');
const DailyRotateFile = require('winston-daily-rotate-file');
const path = require('path');
const fs = require('fs');

// ============================================================================
// CONFIGURATION
// ============================================================================

const LOG_DIR = process.env.LOG_DIR || path.join(process.cwd(), 'logs');
const LOG_LEVEL = process.env.LOG_LEVEL || 'info';
const NODE_ENV = process.env.NODE_ENV || 'development';
const SERVICE_NAME = process.env.SERVICE_NAME || 'legal-form-app';

// Create logs directory if it doesn't exist
if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR, { recursive: true });
}

// ============================================================================
// CUSTOM FORMATS
// ============================================================================

/**
 * JSON formatter for production/file logging
 * Creates structured JSON logs with ISO timestamps
 */
const jsonFormat = winston.format.combine(
    winston.format.timestamp({
        format: 'YYYY-MM-DDTHH:mm:ss.SSSZ' // ISO 8601 format
    }),
    winston.format.errors({ stack: true }), // Include stack traces for errors
    winston.format.metadata({
        fillWith: ['timestamp', 'service', 'environment']
    }),
    winston.format.json()
);

/**
 * Human-readable formatter for development console
 * Colorized output with aligned levels
 */
const consoleFormat = winston.format.combine(
    winston.format.timestamp({
        format: 'YYYY-MM-DD HH:mm:ss'
    }),
    winston.format.colorize(),
    winston.format.errors({ stack: true }),
    winston.format.printf(({ timestamp, level, message, requestId, ...metadata }) => {
        let msg = `${timestamp} [${level}]`;

        if (requestId) {
            msg += ` [${requestId}]`;
        }

        msg += `: ${message}`;

        // Add metadata if present
        const metaStr = Object.keys(metadata).length ? JSON.stringify(metadata, null, 2) : '';
        if (metaStr) {
            msg += `\n${metaStr}`;
        }

        return msg;
    })
);

/**
 * Production JSON formatter with service context
 * Adds service name, environment, and structured metadata
 */
const productionFormat = winston.format.combine(
    winston.format.timestamp({
        format: 'YYYY-MM-DDTHH:mm:ss.SSSZ'
    }),
    winston.format.errors({ stack: true }),
    winston.format((info) => {
        // Add service context to all logs
        info.service = SERVICE_NAME;
        info.environment = NODE_ENV;

        // Move correlation ID to top level for easier querying
        if (info.requestId) {
            info['@requestId'] = info.requestId;
        }

        return info;
    })(),
    winston.format.json()
);

// ============================================================================
// TRANSPORTS
// ============================================================================

/**
 * Console Transport
 * Used in development for real-time log viewing
 */
const consoleTransport = new winston.transports.Console({
    format: NODE_ENV === 'production' ? jsonFormat : consoleFormat,
    level: LOG_LEVEL
});

/**
 * File Transport - Combined Logs
 * All logs regardless of level
 */
const fileTransport = new winston.transports.File({
    filename: path.join(LOG_DIR, 'application.log'),
    format: productionFormat,
    maxsize: 10485760, // 10MB
    maxFiles: 5,
    tailable: true
});

/**
 * File Transport - Error Logs Only
 * Separate file for errors for easier debugging
 */
const errorFileTransport = new winston.transports.File({
    filename: path.join(LOG_DIR, 'error.log'),
    level: 'error',
    format: productionFormat,
    maxsize: 10485760, // 10MB
    maxFiles: 5,
    tailable: true
});

/**
 * Daily Rotate Transport - HTTP Logs
 * HTTP requests logged separately with daily rotation
 */
const httpRotateTransport = new DailyRotateFile({
    filename: path.join(LOG_DIR, 'http-%DATE%.log'),
    datePattern: 'YYYY-MM-DD',
    level: 'http',
    format: productionFormat,
    maxSize: '20m',
    maxFiles: '14d', // Keep logs for 14 days
    zippedArchive: true
});

/**
 * Daily Rotate Transport - Application Logs
 * All application logs with daily rotation
 */
const appRotateTransport = new DailyRotateFile({
    filename: path.join(LOG_DIR, 'app-%DATE%.log'),
    datePattern: 'YYYY-MM-DD',
    format: productionFormat,
    maxSize: '20m',
    maxFiles: '30d', // Keep logs for 30 days
    zippedArchive: true
});

// ============================================================================
// LOGGER INSTANCE
// ============================================================================

/**
 * Main Winston Logger Instance
 */
const logger = winston.createLogger({
    level: LOG_LEVEL,
    defaultMeta: {
        service: SERVICE_NAME,
        environment: NODE_ENV
    },
    transports: [
        consoleTransport,
        fileTransport,
        errorFileTransport,
        httpRotateTransport,
        appRotateTransport
    ],
    exitOnError: false // Don't exit on unhandled errors
});

// ============================================================================
// HELPER METHODS
// ============================================================================

/**
 * Log HTTP request
 * Convenience method for logging HTTP requests
 */
logger.logRequest = function(req, res, duration) {
    this.http('HTTP Request', {
        requestId: req.requestId,
        method: req.method,
        path: req.path,
        statusCode: res.statusCode,
        duration: duration,
        userAgent: req.get('user-agent'),
        ip: req.ip || req.connection.remoteAddress
    });
};

/**
 * Log form submission
 * Convenience method for logging form submissions
 */
logger.logFormSubmission = function(success, metadata = {}) {
    const level = success ? 'info' : 'error';
    this[level]('Form submission', {
        success,
        ...metadata
    });
};

/**
 * Log pipeline execution
 * Convenience method for logging pipeline runs
 */
logger.logPipeline = function(status, metadata = {}) {
    const level = status === 'success' ? 'info' : status === 'error' ? 'error' : 'warn';
    this[level]('Pipeline execution', {
        status,
        ...metadata
    });
};

/**
 * Log database operation
 * Convenience method for logging database queries
 */
logger.logDatabase = function(operation, metadata = {}) {
    this.debug('Database operation', {
        operation,
        ...metadata
    });
};

/**
 * Log Dropbox operation
 * Convenience method for logging Dropbox uploads
 */
logger.logDropbox = function(success, metadata = {}) {
    const level = success ? 'info' : 'error';
    this[level]('Dropbox operation', {
        success,
        ...metadata
    });
};

/**
 * Log with correlation ID
 * Adds request ID to log metadata
 */
logger.withRequestId = function(requestId) {
    return {
        info: (message, meta = {}) => this.info(message, { requestId, ...meta }),
        error: (message, meta = {}) => this.error(message, { requestId, ...meta }),
        warn: (message, meta = {}) => this.warn(message, { requestId, ...meta }),
        debug: (message, meta = {}) => this.debug(message, { requestId, ...meta }),
        http: (message, meta = {}) => this.http(message, { requestId, ...meta })
    };
};

// ============================================================================
// EVENT HANDLERS
// ============================================================================

/**
 * Log rotation events
 */
httpRotateTransport.on('rotate', (oldFilename, newFilename) => {
    logger.info('HTTP log rotated', {
        oldFilename: path.basename(oldFilename),
        newFilename: path.basename(newFilename)
    });
});

appRotateTransport.on('rotate', (oldFilename, newFilename) => {
    logger.info('Application log rotated', {
        oldFilename: path.basename(oldFilename),
        newFilename: path.basename(newFilename)
    });
});

/**
 * Log transport errors
 */
logger.on('error', (error) => {
    console.error('Logger error:', error);
});

// ============================================================================
// STARTUP LOG
// ============================================================================

logger.info('Logger initialized', {
    logLevel: LOG_LEVEL,
    logDirectory: LOG_DIR,
    environment: NODE_ENV,
    service: SERVICE_NAME
});

// ============================================================================
// EXPORTS
// ============================================================================

module.exports = logger;
