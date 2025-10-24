# Monitoring & Observability

This directory contains the monitoring and observability infrastructure for the Legal Form Application.

## Overview

The monitoring system is built on **Prometheus** for metrics collection and follows the **Four Golden Signals** framework:

1. **Latency** - How long it takes to serve requests
2. **Traffic** - How much demand is placed on the system
3. **Errors** - Rate of failed requests
4. **Saturation** - How "full" the system is

## Directory Structure

```
monitoring/
├── README.md                           # This file
├── metrics.js                          # Prometheus metrics definitions
├── middleware.js                       # Express instrumentation middleware
├── docker-compose.yml                  # (Phase 4) Local monitoring stack
├── prometheus/
│   ├── prometheus.yml                  # (Phase 4) Prometheus config
│   └── alerts/
│       └── application.yml             # (Phase 5) Alert rules
└── grafana/
    ├── provisioning/
    │   ├── datasources/
    │   │   └── prometheus.yml          # (Phase 4) Data source config
    │   └── dashboards/
    │       └── dashboards.yml          # (Phase 5) Dashboard provisioning
    └── dashboards/
        ├── application-overview.json   # (Phase 5) Application dashboard
        └── business-metrics.json       # (Phase 5) Business dashboard
```

## Files

### `metrics.js`
Core metrics collection module that defines all Prometheus metrics.

**Exports**:
- `register` - Prometheus registry for /metrics endpoint
- `metrics` - Object containing all metric instances
- Helper functions for recording metrics

**Metrics Categories**:
1. **Golden Signals**: HTTP request metrics (latency, traffic, errors)
2. **Business Metrics**: Form submissions, pipeline executions, Dropbox uploads
3. **Database Metrics**: Query performance, connection pool stats
4. **Application Metrics**: Uptime, version info, Node.js runtime

**Usage Example**:
```javascript
const { recordFormSubmission } = require('./monitoring/metrics');

// Record a successful form submission
recordFormSubmission(
  true,                    // success
  2,                       // plaintiffs
  1,                       // defendants
  0.245                    // processing time (seconds)
);
```

### `middleware.js`
Express middleware for automatic HTTP request instrumentation.

**Exports**:
- `metricsMiddleware` - Main middleware for request tracking
- `errorMetricsMiddleware` - Error tracking middleware
- `requestSizeMiddleware` - Request body size tracking

**Usage Example**:
```javascript
const { metricsMiddleware } = require('./monitoring/middleware');

app.use(metricsMiddleware);
```

**Features**:
- Automatic request duration tracking
- Response size measurement
- Route normalization (prevents high cardinality)
- Non-blocking metrics recording
- Error tracking

## Metrics Reference

### HTTP Metrics (Automatic)

#### `http_request_duration_seconds`
**Type**: Histogram
**Description**: Duration of HTTP requests in seconds
**Labels**: `method`, `route`, `status_code`
**Buckets**: 0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10

**Example Query**:
```promql
# 95th percentile latency
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)
```

#### `http_requests_total`
**Type**: Counter
**Description**: Total number of HTTP requests
**Labels**: `method`, `route`, `status_code`

**Example Query**:
```promql
# Request rate per second
rate(http_requests_total[5m])

# Error rate percentage
sum(rate(http_requests_total{status_code=~"5.."}[5m]))
/ sum(rate(http_requests_total[5m])) * 100
```

#### `http_response_size_bytes`
**Type**: Histogram
**Description**: Size of HTTP response bodies in bytes
**Labels**: `method`, `route`, `status_code`

### Form Submission Metrics

#### `form_submissions_total`
**Type**: Counter
**Description**: Total number of form submissions
**Labels**: `status` (success, error)

**Usage**:
```javascript
const { recordFormSubmission } = require('./monitoring/metrics');

recordFormSubmission(true, 2, 1, 0.5);  // success
recordFormSubmission(false, 0, 0, 0.1); // error
```

#### `form_processing_duration_seconds`
**Type**: Histogram
**Description**: Time taken to process form submissions
**Labels**: `status` (success, error)
**Buckets**: 0.1, 0.5, 1, 2, 5, 10, 30

#### `form_plaintiffs_count`
**Type**: Histogram
**Description**: Number of plaintiffs per form submission
**Buckets**: 1, 2, 3, 4, 5, 10, 20

#### `form_defendants_count`
**Type**: Histogram
**Description**: Number of defendants per form submission
**Buckets**: 1, 2, 3, 4, 5, 10, 20

### Pipeline Metrics

#### `pipeline_executions_total`
**Type**: Counter
**Description**: Total number of pipeline executions
**Labels**: `status` (success, error, skipped)

**Usage**:
```javascript
const { recordPipelineExecution } = require('./monitoring/metrics');

recordPipelineExecution('success', 45.3);  // 45.3 seconds
recordPipelineExecution('error', 2.1);
recordPipelineExecution('skipped', undefined);
```

#### `pipeline_execution_duration_seconds`
**Type**: Histogram
**Description**: Time taken for pipeline to complete
**Labels**: `status` (success, error)
**Buckets**: 1, 5, 10, 30, 60, 120, 300

### Dropbox Metrics

#### `dropbox_uploads_total`
**Type**: Counter
**Description**: Total number of Dropbox upload attempts
**Labels**: `status` (success, error, skipped)

**Usage**:
```javascript
const { recordDropboxUpload } = require('./monitoring/metrics');

recordDropboxUpload('success', 1.2, 50000);  // 1.2s, 50KB
recordDropboxUpload('error', 0.5, undefined);
```

#### `dropbox_upload_duration_seconds`
**Type**: Histogram
**Description**: Time taken to upload files to Dropbox
**Labels**: `status` (success, error)
**Buckets**: 0.1, 0.5, 1, 2, 5, 10, 30

#### `dropbox_upload_file_size_bytes`
**Type**: Histogram
**Description**: Size of files uploaded to Dropbox
**Buckets**: 1000, 10000, 50000, 100000, 500000, 1000000, 5000000

### Database Metrics

#### `database_query_duration_seconds`
**Type**: Histogram
**Description**: Time taken to execute database queries
**Labels**: `operation` (select, insert, update, delete), `table`
**Buckets**: 0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2

**Usage**:
```javascript
const { recordDatabaseQuery } = require('./monitoring/metrics');

recordDatabaseQuery('insert', 'cases', 'success', 0.025);
recordDatabaseQuery('select', 'parties', 'success', 0.005);
```

#### `database_queries_total`
**Type**: Counter
**Description**: Total number of database queries
**Labels**: `operation`, `table`, `status` (success, error)

#### `database_pool_connections_active`
**Type**: Gauge
**Description**: Number of active database connections

**Usage**:
```javascript
const { updateDatabasePoolMetrics } = require('./monitoring/metrics');

updateDatabasePoolMetrics(5, 15, 0);  // 5 active, 15 idle, 0 waiting
```

#### `database_pool_connections_idle`
**Type**: Gauge
**Description**: Number of idle database connections

#### `database_pool_connections_waiting`
**Type**: Gauge
**Description**: Number of queries waiting for a connection

### Application Metrics

#### `application_info`
**Type**: Gauge
**Description**: Application version and environment information
**Labels**: `version`, `environment`, `node_version`

#### `application_uptime_seconds`
**Type**: Gauge
**Description**: Application uptime in seconds

### Node.js Runtime Metrics (Default)

These metrics are automatically collected by `prom-client`:

- `nodejs_process_cpu_user_seconds_total` - User CPU time
- `nodejs_process_cpu_system_seconds_total` - System CPU time
- `nodejs_process_resident_memory_bytes` - Resident memory
- `nodejs_process_heap_bytes` - Heap size
- `nodejs_eventloop_lag_seconds` - Event loop lag
- `nodejs_gc_duration_seconds` - Garbage collection duration
- And many more...

## Integration Guide

### Step 1: Import the Modules

```javascript
const metricsModule = require('./monitoring/metrics');
const { metricsMiddleware } = require('./monitoring/middleware');
```

### Step 2: Add Middleware

```javascript
// Early in middleware chain (before routes)
app.use(metricsMiddleware);
```

### Step 3: Create /metrics Endpoint

```javascript
app.get('/metrics', async (req, res) => {
  try {
    res.set('Content-Type', metricsModule.register.contentType);
    const metrics = await metricsModule.register.metrics();
    res.end(metrics);
  } catch (error) {
    console.error('Error generating metrics:', error);
    res.status(500).end('Error generating metrics');
  }
});
```

### Step 4: Record Business Metrics

```javascript
const {
  recordFormSubmission,
  recordPipelineExecution,
  recordDropboxUpload,
  recordDatabaseQuery
} = require('./monitoring/metrics');

// In your form submission handler
const startTime = Date.now();
try {
  // ... save form ...
  const processingTime = (Date.now() - startTime) / 1000;

  recordFormSubmission(
    true,                                    // success
    transformedData.PlaintiffDetails.length, // plaintiff count
    transformedData.DefendantDetails2.length, // defendant count
    processingTime                           // duration
  );
} catch (error) {
  recordFormSubmission(false, 0, 0, 0);
}

// In your pipeline handler
const pipelineStart = Date.now();
try {
  const result = await callPipeline(data);
  const duration = (Date.now() - pipelineStart) / 1000;
  recordPipelineExecution('success', duration);
} catch (error) {
  const duration = (Date.now() - pipelineStart) / 1000;
  recordPipelineExecution('error', duration);
}
```

## Testing Metrics

### 1. Start the Application
```bash
npm start
```

### 2. Generate Traffic
```bash
# Test health endpoint
curl http://localhost:3000/api/health

# Generate load
for i in {1..100}; do
  curl -s http://localhost:3000/api/health > /dev/null
done
```

### 3. View Metrics
```bash
# View all metrics
curl http://localhost:3000/metrics

# Filter specific metrics
curl http://localhost:3000/metrics | grep http_request
curl http://localhost:3000/metrics | grep form_
curl http://localhost:3000/metrics | grep nodejs_
```

### 4. Query Specific Metrics
```bash
# Request rate
curl -s http://localhost:3000/metrics | grep "http_requests_total"

# Latency
curl -s http://localhost:3000/metrics | grep "http_request_duration"

# Application info
curl -s http://localhost:3000/metrics | grep "application_info"
```

## Prometheus Queries

### Request Rate (QPS)
```promql
# Requests per second (all endpoints)
sum(rate(http_requests_total[5m]))

# Requests per second (by endpoint)
sum(rate(http_requests_total[5m])) by (route)
```

### Error Rate
```promql
# Error rate percentage
sum(rate(http_requests_total{status_code=~"5.."}[5m]))
/ sum(rate(http_requests_total[5m])) * 100

# Error count by route
sum(rate(http_requests_total{status_code=~"5.."}[5m])) by (route)
```

### Latency Percentiles
```promql
# p50 latency
histogram_quantile(0.50,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)

# p95 latency
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)

# p99 latency
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)
```

### Business Metrics
```promql
# Form submission rate
rate(form_submissions_total[5m])

# Form submission success rate
sum(rate(form_submissions_total{status="success"}[5m]))
/ sum(rate(form_submissions_total[5m]))

# Average processing time
rate(form_processing_duration_seconds_sum[5m])
/ rate(form_processing_duration_seconds_count[5m])
```

## Best Practices

### 1. Label Cardinality
- ✅ Use labels with low cardinality (method, status_code, route)
- ❌ Avoid labels with high cardinality (user_id, request_id, timestamp)

### 2. Metric Naming
- Use `_total` suffix for counters
- Use `_seconds` suffix for durations
- Use `_bytes` suffix for sizes
- Use snake_case for metric names

### 3. Recording Metrics
- Record metrics asynchronously when possible
- Use `setImmediate()` to avoid blocking requests
- Handle errors gracefully in metric recording

### 4. Testing
- Always verify metrics appear in `/metrics` endpoint
- Check that counters increment correctly
- Validate histogram buckets match your use case

## Troubleshooting

### Metrics not appearing
1. Check server logs for errors
2. Verify middleware is loaded early
3. Generate traffic to trigger metrics
4. Check `/metrics` endpoint directly

### High memory usage
1. Check for high cardinality labels
2. Verify metric cleanup is working
3. Monitor `nodejs_process_heap_bytes`

### Incorrect values
1. Verify metric type (counter vs gauge vs histogram)
2. Check label values are correct
3. Ensure units are consistent (seconds, not ms)

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Node.js Client Documentation](https://github.com/simmonds/prom-client)
- [Four Golden Signals](https://sre.google/sre-book/monitoring-distributed-systems/)

---

*Monitoring infrastructure implemented as part of Phase 1: Application Metrics*
