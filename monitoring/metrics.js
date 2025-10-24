/**
 * Prometheus Metrics Collector
 *
 * This module provides comprehensive metrics collection for the Legal Form Application.
 * It tracks both infrastructure metrics (Golden Signals) and business metrics.
 *
 * Metrics Categories:
 * 1. Golden Signals - HTTP requests, latency, errors, saturation
 * 2. Business Metrics - Form submissions, pipeline executions, Dropbox uploads
 * 3. Infrastructure - Database connections, Node.js runtime
 *
 * Usage:
 *   const metrics = require('./monitoring/metrics');
 *   metrics.httpRequestTotal.inc({ method: 'GET', route: '/api/health', status_code: 200 });
 */

const client = require('prom-client');

// Create a Registry which registers the metrics
const register = new client.Registry();

// Add default metrics (CPU, memory, event loop lag, etc.)
client.collectDefaultMetrics({
  register,
  prefix: 'nodejs_',
  gcDurationBuckets: [0.001, 0.01, 0.1, 1, 2, 5]
});

// ============================================================================
// GOLDEN SIGNALS - Infrastructure Metrics
// ============================================================================

/**
 * HTTP Request Duration (Histogram)
 * Tracks the duration of HTTP requests in seconds
 * Labels: method, route, status_code
 * Buckets optimized for web application response times
 */
const httpRequestDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
  registers: [register]
});

/**
 * HTTP Requests Total (Counter)
 * Total count of HTTP requests
 * Labels: method, route, status_code
 */
const httpRequestTotal = new client.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code'],
  registers: [register]
});

/**
 * HTTP Response Size (Histogram)
 * Size of HTTP response bodies in bytes
 * Labels: method, route, status_code
 */
const httpResponseSize = new client.Histogram({
  name: 'http_response_size_bytes',
  help: 'Size of HTTP response bodies in bytes',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [100, 1000, 5000, 10000, 50000, 100000, 500000, 1000000],
  registers: [register]
});

// ============================================================================
// BUSINESS METRICS - Form Submissions
// ============================================================================

/**
 * Form Submissions Total (Counter)
 * Total number of form submissions
 * Labels: status (success, error)
 */
const formSubmissionsTotal = new client.Counter({
  name: 'form_submissions_total',
  help: 'Total number of form submissions',
  labelNames: ['status'],
  registers: [register]
});

/**
 * Form Processing Duration (Histogram)
 * Time taken to process and save form submissions
 * Labels: status (success, error)
 */
const formProcessingDuration = new client.Histogram({
  name: 'form_processing_duration_seconds',
  help: 'Duration of form processing in seconds',
  labelNames: ['status'],
  buckets: [0.1, 0.5, 1, 2, 5, 10, 30],
  registers: [register]
});

/**
 * Form Plaintiffs Count (Histogram)
 * Number of plaintiffs per form submission
 */
const formPlaintiffsCount = new client.Histogram({
  name: 'form_plaintiffs_count',
  help: 'Number of plaintiffs per form submission',
  buckets: [1, 2, 3, 4, 5, 10, 20],
  registers: [register]
});

/**
 * Form Defendants Count (Histogram)
 * Number of defendants per form submission
 */
const formDefendantsCount = new client.Histogram({
  name: 'form_defendants_count',
  help: 'Number of defendants per form submission',
  buckets: [1, 2, 3, 4, 5, 10, 20],
  registers: [register]
});

// ============================================================================
// BUSINESS METRICS - Python Pipeline Integration
// ============================================================================

/**
 * Pipeline Executions Total (Counter)
 * Total number of pipeline API calls
 * Labels: status (success, error, skipped)
 */
const pipelineExecutionsTotal = new client.Counter({
  name: 'pipeline_executions_total',
  help: 'Total number of pipeline executions',
  labelNames: ['status'],
  registers: [register]
});

/**
 * Pipeline Execution Duration (Histogram)
 * Time taken for pipeline to complete
 * Labels: status (success, error)
 */
const pipelineExecutionDuration = new client.Histogram({
  name: 'pipeline_execution_duration_seconds',
  help: 'Duration of pipeline execution in seconds',
  labelNames: ['status'],
  buckets: [1, 5, 10, 30, 60, 120, 300],
  registers: [register]
});

// ============================================================================
// BUSINESS METRICS - Dropbox Integration
// ============================================================================

/**
 * Dropbox Uploads Total (Counter)
 * Total number of Dropbox upload attempts
 * Labels: status (success, error, skipped)
 */
const dropboxUploadsTotal = new client.Counter({
  name: 'dropbox_uploads_total',
  help: 'Total number of Dropbox upload attempts',
  labelNames: ['status'],
  registers: [register]
});

/**
 * Dropbox Upload Duration (Histogram)
 * Time taken to upload files to Dropbox
 * Labels: status (success, error)
 */
const dropboxUploadDuration = new client.Histogram({
  name: 'dropbox_upload_duration_seconds',
  help: 'Duration of Dropbox uploads in seconds',
  labelNames: ['status'],
  buckets: [0.1, 0.5, 1, 2, 5, 10, 30],
  registers: [register]
});

/**
 * Dropbox Upload File Size (Histogram)
 * Size of files uploaded to Dropbox in bytes
 */
const dropboxUploadFileSize = new client.Histogram({
  name: 'dropbox_upload_file_size_bytes',
  help: 'Size of files uploaded to Dropbox in bytes',
  buckets: [1000, 10000, 50000, 100000, 500000, 1000000, 5000000],
  registers: [register]
});

// ============================================================================
// DATABASE METRICS
// ============================================================================

/**
 * Database Query Duration (Histogram)
 * Time taken to execute database queries
 * Labels: operation (select, insert, update, delete), table
 */
const databaseQueryDuration = new client.Histogram({
  name: 'database_query_duration_seconds',
  help: 'Duration of database queries in seconds',
  labelNames: ['operation', 'table'],
  buckets: [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2],
  registers: [register]
});

/**
 * Database Queries Total (Counter)
 * Total number of database queries
 * Labels: operation (select, insert, update, delete), table, status (success, error)
 */
const databaseQueriesTotal = new client.Counter({
  name: 'database_queries_total',
  help: 'Total number of database queries',
  labelNames: ['operation', 'table', 'status'],
  registers: [register]
});

/**
 * Database Connection Pool Active (Gauge)
 * Number of active database connections in the pool
 */
const databasePoolActive = new client.Gauge({
  name: 'database_pool_connections_active',
  help: 'Number of active database connections',
  registers: [register]
});

/**
 * Database Connection Pool Idle (Gauge)
 * Number of idle database connections in the pool
 */
const databasePoolIdle = new client.Gauge({
  name: 'database_pool_connections_idle',
  help: 'Number of idle database connections',
  registers: [register]
});

/**
 * Database Connection Pool Waiting (Gauge)
 * Number of queries waiting for a database connection
 */
const databasePoolWaiting = new client.Gauge({
  name: 'database_pool_connections_waiting',
  help: 'Number of queries waiting for a connection',
  registers: [register]
});

// ============================================================================
// APPLICATION HEALTH METRICS
// ============================================================================

/**
 * Application Info (Gauge)
 * Application information and version
 * Labels: version, environment, node_version
 */
const applicationInfo = new client.Gauge({
  name: 'application_info',
  help: 'Application information',
  labelNames: ['version', 'environment', 'node_version'],
  registers: [register]
});

// Set application info on startup
applicationInfo.set({
  version: process.env.APP_VERSION || '1.0.0',
  environment: process.env.NODE_ENV || 'development',
  node_version: process.version
}, 1);

/**
 * Application Uptime (Gauge)
 * Application uptime in seconds
 */
const applicationUptime = new client.Gauge({
  name: 'application_uptime_seconds',
  help: 'Application uptime in seconds',
  registers: [register],
  collect() {
    this.set(process.uptime());
  }
});

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Normalizes HTTP route paths to prevent high cardinality
 * Converts dynamic segments to template variables
 *
 * Examples:
 *   /api/form-entries/123 -> /api/form-entries/{id}
 *   /api/form-entries/abc-def-456 -> /api/form-entries/{id}
 */
function normalizeRoute(path) {
  if (!path) return 'unknown';

  // Replace UUIDs and numeric IDs with {id}
  let normalized = path.replace(/\/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi, '/{id}');
  normalized = normalized.replace(/\/\d+/g, '/{id}');

  return normalized;
}

/**
 * Records an HTTP request with all relevant metrics
 * This is the main function called by the middleware
 */
function recordHttpRequest(method, route, statusCode, duration, responseSize) {
  const normalizedRoute = normalizeRoute(route);
  const labels = {
    method: method,
    route: normalizedRoute,
    status_code: statusCode.toString()
  };

  httpRequestTotal.inc(labels);
  httpRequestDuration.observe(labels, duration);

  if (responseSize) {
    httpResponseSize.observe(labels, responseSize);
  }
}

/**
 * Records a form submission event
 */
function recordFormSubmission(success, plaintiffs, defendants, processingTime) {
  const status = success ? 'success' : 'error';

  formSubmissionsTotal.inc({ status });
  formProcessingDuration.observe({ status }, processingTime);

  if (success && plaintiffs !== undefined) {
    formPlaintiffsCount.observe(plaintiffs);
  }

  if (success && defendants !== undefined) {
    formDefendantsCount.observe(defendants);
  }
}

/**
 * Records a pipeline execution event
 */
function recordPipelineExecution(status, duration) {
  pipelineExecutionsTotal.inc({ status });

  if (duration !== undefined) {
    pipelineExecutionDuration.observe({ status }, duration);
  }
}

/**
 * Records a Dropbox upload event
 */
function recordDropboxUpload(status, duration, fileSize) {
  dropboxUploadsTotal.inc({ status });

  if (duration !== undefined) {
    dropboxUploadDuration.observe({ status }, duration);
  }

  if (fileSize !== undefined) {
    dropboxUploadFileSize.observe(fileSize);
  }
}

/**
 * Records a database query event
 */
function recordDatabaseQuery(operation, table, status, duration) {
  databaseQueriesTotal.inc({ operation, table, status });

  if (duration !== undefined) {
    databaseQueryDuration.observe({ operation, table }, duration);
  }
}

/**
 * Updates database connection pool metrics
 */
function updateDatabasePoolMetrics(active, idle, waiting) {
  if (active !== undefined) databasePoolActive.set(active);
  if (idle !== undefined) databasePoolIdle.set(idle);
  if (waiting !== undefined) databasePoolWaiting.set(waiting);
}

// ============================================================================
// EXPORTS
// ============================================================================

module.exports = {
  // Registry for /metrics endpoint
  register,

  // Metric objects (for direct manipulation if needed)
  metrics: {
    httpRequestDuration,
    httpRequestTotal,
    httpResponseSize,
    formSubmissionsTotal,
    formProcessingDuration,
    formPlaintiffsCount,
    formDefendantsCount,
    pipelineExecutionsTotal,
    pipelineExecutionDuration,
    dropboxUploadsTotal,
    dropboxUploadDuration,
    dropboxUploadFileSize,
    databaseQueryDuration,
    databaseQueriesTotal,
    databasePoolActive,
    databasePoolIdle,
    databasePoolWaiting,
    applicationInfo,
    applicationUptime
  },

  // Helper functions
  normalizeRoute,
  recordHttpRequest,
  recordFormSubmission,
  recordPipelineExecution,
  recordDropboxUpload,
  recordDatabaseQuery,
  updateDatabasePoolMetrics
};
