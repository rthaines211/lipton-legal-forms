/**
 * Prometheus Metrics Middleware
 *
 * Express middleware for automatic HTTP request instrumentation.
 * This middleware captures request/response metrics for all routes.
 *
 * Features:
 * - Automatic request duration tracking
 * - Response size measurement
 * - Route normalization (prevents high cardinality)
 * - Error tracking
 * - Non-blocking metrics recording
 *
 * Usage:
 *   const { metricsMiddleware } = require('./monitoring/middleware');
 *   app.use(metricsMiddleware);
 */

const responseTime = require('response-time');
const { recordHttpRequest, normalizeRoute } = require('./metrics');

/**
 * Metrics Middleware Factory
 *
 * Creates Express middleware that automatically records metrics
 * for all HTTP requests passing through the application.
 *
 * This middleware:
 * 1. Captures request start time
 * 2. Waits for response to finish
 * 3. Calculates duration
 * 4. Records metrics (non-blocking)
 * 5. Normalizes routes to prevent cardinality explosion
 */
function createMetricsMiddleware() {
  return responseTime((req, res, time) => {
    // Skip metrics endpoint itself to avoid recursion
    if (req.path === '/metrics') {
      return;
    }

    try {
      const method = req.method;
      const route = getRoutePath(req);
      const statusCode = res.statusCode;
      const duration = time / 1000; // Convert ms to seconds
      const responseSize = res.get('Content-Length') || 0;

      // Record metrics (async, non-blocking)
      setImmediate(() => {
        recordHttpRequest(method, route, statusCode, duration, parseInt(responseSize));
      });
    } catch (error) {
      // Silently fail - don't break the request
      console.error('Error recording metrics:', error.message);
    }
  });
}

/**
 * Extract route path from Express request
 *
 * Tries to get the most specific route path:
 * 1. Express route path (e.g., /api/form-entries/:id)
 * 2. Base URL (for mounted routers)
 * 3. Original URL as fallback
 */
function getRoutePath(req) {
  // For Express routes with defined paths
  if (req.route && req.route.path) {
    const baseUrl = req.baseUrl || '';
    return baseUrl + req.route.path;
  }

  // For mounted routers
  if (req.baseUrl) {
    return req.baseUrl;
  }

  // Fallback to original URL (will be normalized later)
  return req.originalUrl || req.url || 'unknown';
}

/**
 * Error Tracking Middleware
 *
 * Catches errors and records error metrics.
 * Should be added after all routes but before final error handler.
 *
 * Usage:
 *   app.use(errorMetricsMiddleware);
 *   app.use((err, req, res, next) => { ... }); // Your error handler
 */
function errorMetricsMiddleware(err, req, res, next) {
  // The error will be handled by Express's error handler
  // We just want to ensure metrics are recorded for errors

  // If status code not set, default to 500
  if (!res.statusCode || res.statusCode === 200) {
    res.statusCode = 500;
  }

  // Continue to next error handler
  next(err);
}

/**
 * Request Size Tracking Middleware (Optional)
 *
 * Tracks the size of incoming request bodies.
 * Useful for monitoring form submission sizes.
 */
function requestSizeMiddleware(req, res, next) {
  const contentLength = req.get('Content-Length');

  if (contentLength) {
    req.requestSize = parseInt(contentLength);
  }

  next();
}

// ============================================================================
// EXPORTS
// ============================================================================

module.exports = {
  metricsMiddleware: createMetricsMiddleware(),
  errorMetricsMiddleware,
  requestSizeMiddleware,
  getRoutePath
};
