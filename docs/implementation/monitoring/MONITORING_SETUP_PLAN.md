# Monitoring & Observability Setup Plan
## Legal Form Application - Phased Implementation

**Target Environment**: Local Development → Google Cloud Platform (GCP)
**Last Updated**: 2025-10-21
**Status**: Planning Phase

---

## Table of Contents
- [Overview](#overview)
- [Architecture Summary](#architecture-summary)
- [Prerequisites](#prerequisites)
- [Phase 1: Application Metrics](#phase-1-application-metrics)
- [Phase 2: Structured Logging](#phase-2-structured-logging)
- [Phase 3: Health Checks & Readiness Probes](#phase-3-health-checks--readiness-probes)
- [Phase 4: Local Monitoring Stack](#phase-4-local-monitoring-stack)
- [Phase 5: Dashboards & Alerts](#phase-5-dashboards--alerts)
- [GCP Migration Guide](#gcp-migration-guide)
- [Troubleshooting](#troubleshooting)

---

## Overview

This plan implements a comprehensive monitoring and observability solution for the Legal Form Application using the **three pillars of observability**:

1. **Metrics** - Prometheus for time-series data (request rates, latencies, errors)
2. **Logs** - Structured logging with Winston (application events, errors, debugging)
3. **Traces** - (Future: OpenTelemetry for distributed tracing)

### Key Objectives
- ✅ Monitor application performance (Golden Signals: Latency, Traffic, Errors, Saturation)
- ✅ Track business metrics (form submissions, pipeline executions, database operations)
- ✅ Enable debugging with structured logs
- ✅ Set up alerting for critical failures
- ✅ Prepare for GCP migration (Cloud Monitoring, Cloud Logging)

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│                  Legal Form Application                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Metrics    │  │    Logs      │  │    Health    │  │
│  │  (prom-      │  │  (winston)   │  │   Checks     │  │
│  │   client)    │  │              │  │              │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          │                  │                  │
    ┌─────▼─────┐      ┌────▼─────┐      ┌────▼─────┐
    │Prometheus │      │ File/    │      │ Load     │
    │  Server   │      │ Console  │      │ Balancer │
    │ (scrape)  │      │          │      │ (GCP)    │
    └─────┬─────┘      └──────────┘      └──────────┘
          │
    ┌─────▼─────┐
    │  Grafana  │
    │Dashboards │
    └───────────┘
```

**Local Development**: Docker Compose with Prometheus + Grafana
**GCP Production**: Google Cloud Monitoring + Cloud Logging (native integrations)

---

## Prerequisites

### Required Software
- Node.js v16+ (current: installed)
- Docker Desktop (for local monitoring stack)
- Docker Compose v2.0+
- PostgreSQL (current: running locally)

### Verification Commands
```bash
# Check Node.js version
node --version

# Check Docker
docker --version
docker-compose --version

# Check if Docker daemon is running
docker ps

# Check PostgreSQL
psql -U ryanhaines -d legal_forms_db -c "SELECT version();"
```

---

## Phase 1: Application Metrics

**Goal**: Instrument the Express application to expose Prometheus metrics

### What We'll Build
- Metrics collection module (`metrics.js`)
- Express middleware for automatic instrumentation
- Custom business metrics (form submissions, pipeline calls, DB queries)
- `/metrics` endpoint for Prometheus scraping

### Files to Create
1. `monitoring/metrics.js` - Prometheus metrics collector
2. `monitoring/middleware.js` - Express instrumentation middleware

### Metrics to Track

#### Golden Signals (Automatic)
- **Latency**: `http_request_duration_seconds` (histogram)
- **Traffic**: `http_requests_total` (counter)
- **Errors**: `http_requests_total{status_code="5xx"}` (counter)
- **Saturation**: `nodejs_eventloop_lag_seconds` (gauge)

#### Business Metrics (Custom)
- `form_submissions_total` - Total form submissions
- `form_submissions_errors_total` - Failed submissions
- `pipeline_executions_total` - Pipeline API calls
- `pipeline_execution_duration_seconds` - Pipeline latency
- `database_query_duration_seconds` - DB query performance
- `database_pool_connections_active` - Active DB connections
- `dropbox_uploads_total` - Dropbox upload operations
- `dropbox_upload_errors_total` - Failed Dropbox uploads

### Implementation Steps

#### Step 1.1: Install Dependencies
```bash
npm install --save prom-client response-time
```

**Sanity Check**:
```bash
# Verify installation
npm list prom-client response-time
```

#### Step 1.2: Create Metrics Module
Create `monitoring/metrics.js` with:
- Prometheus registry initialization
- Metric definitions (counters, histograms, gauges)
- Helper functions for incrementing metrics

#### Step 1.3: Add Metrics Middleware
Create `monitoring/middleware.js` with:
- HTTP request/response instrumentation
- Automatic path normalization (e.g., `/api/form-entries/:id` → `/api/form-entries/{id}`)
- Response time tracking

#### Step 1.4: Update server.js
- Import metrics module
- Add metrics middleware to Express
- Create `/metrics` endpoint
- Instrument existing endpoints with custom metrics

#### Step 1.5: Test Metrics Endpoint

**Sanity Check Commands**:
```bash
# Start the server
npm start

# In another terminal, make a test request
curl http://localhost:3000/api/health

# Check metrics endpoint
curl http://localhost:3000/metrics | grep http_request

# You should see output like:
# http_requests_total{method="GET",route="/api/health",status_code="200"} 1
# http_request_duration_seconds_bucket{le="0.005",method="GET",route="/api/health"} 1
```

**Expected Results**:
- ✅ `/metrics` endpoint returns Prometheus-formatted metrics
- ✅ Metrics include `http_requests_total` and `http_request_duration_seconds`
- ✅ No errors in server logs

---

## Phase 2: Structured Logging

**Goal**: Replace basic Morgan logging with structured JSON logging

### What We'll Build
- Winston logger with multiple transports (console, file, daily rotation)
- Structured log format with timestamps, request IDs, context
- Log levels (error, warn, info, debug)
- Correlation IDs for request tracing

### Files to Create
1. `monitoring/logger.js` - Winston logger configuration
2. `monitoring/log-middleware.js` - Request logging middleware

### Log Structure
```json
{
  "@timestamp": "2025-10-21T12:34:56.789Z",
  "level": "info",
  "message": "Form submission received",
  "service": "legal-form-app",
  "environment": "development",
  "requestId": "abc-123-def",
  "userId": "user-456",
  "method": "POST",
  "path": "/api/form-entries",
  "statusCode": 201,
  "duration": 245,
  "metadata": {
    "plaintiffs": 2,
    "defendants": 1,
    "pipelineEnabled": true
  }
}
```

### Implementation Steps

#### Step 2.1: Install Dependencies
```bash
npm install --save winston winston-daily-rotate-file
```

**Sanity Check**:
```bash
npm list winston winston-daily-rotate-file
```

#### Step 2.2: Create Logger Module
Create `monitoring/logger.js` with:
- Winston configuration
- Multiple transports (console, file, daily rotation)
- Custom JSON formatter
- Log level management (from env var)

#### Step 2.3: Create Logging Middleware
Create `monitoring/log-middleware.js` with:
- Request ID generation (UUID)
- Request/response logging
- Error logging with stack traces

#### Step 2.4: Update server.js
- Replace Morgan with Winston middleware
- Add structured logging to all endpoints
- Log critical events (form submissions, pipeline calls, DB errors)

#### Step 2.5: Test Logging

**Sanity Check Commands**:
```bash
# Start server
npm start

# Make test requests
curl -X POST http://localhost:3000/api/form-entries \
  -H "Content-Type: application/json" \
  -d '{"property": {"address": "123 Test St"}}'

# Check log files
ls -lh logs/

# View latest log entries
tail -f logs/application.log

# Search for specific log level
grep '"level":"error"' logs/application.log
```

**Expected Results**:
- ✅ Logs appear in `logs/application.log` as JSON
- ✅ Each log entry has timestamp, level, message, requestId
- ✅ Console shows human-readable logs (development mode)
- ✅ Files rotate daily (check `logs/` directory)

---

## Phase 3: Health Checks & Readiness Probes

**Goal**: Implement comprehensive health checks for monitoring and load balancing

### What We'll Build
- `/health` - Basic liveness probe (is app running?)
- `/health/ready` - Readiness probe (is app ready to serve traffic?)
- `/health/detailed` - Detailed health status (all dependencies)

### Health Check Components
1. **Application Health** - Server is running
2. **Database Health** - PostgreSQL connection pool
3. **External API Health** - Python pipeline (optional)
4. **Dropbox Health** - Dropbox API connection (optional)

### Files to Create
1. `monitoring/health-checks.js` - Health check implementations

### Implementation Steps

#### Step 3.1: Create Health Check Module
Create `monitoring/health-checks.js` with:
- Database connection check
- External API availability check
- Dropbox API check
- Aggregated health status

#### Step 3.2: Add Health Endpoints to server.js
- `GET /health` - Simple 200 OK (liveness)
- `GET /health/ready` - Check critical dependencies (readiness)
- `GET /health/detailed` - Full diagnostic info

#### Step 3.3: Test Health Checks

**Sanity Check Commands**:
```bash
# Start server
npm start

# Test liveness (should always return 200)
curl http://localhost:3000/health

# Test readiness
curl http://localhost:3000/health/ready

# Test detailed health (includes all dependencies)
curl http://localhost:3000/health/detailed | jq

# Expected JSON response:
# {
#   "status": "healthy",
#   "timestamp": "2025-10-21T12:34:56.789Z",
#   "uptime": 123.456,
#   "checks": {
#     "database": { "status": "healthy", "responseTime": 5 },
#     "pipeline": { "status": "healthy", "responseTime": 50 },
#     "dropbox": { "status": "healthy" }
#   }
# }

# Test with database down (stop PostgreSQL)
# Readiness should return 503
curl -i http://localhost:3000/health/ready
```

**Expected Results**:
- ✅ `/health` returns 200 OK
- ✅ `/health/ready` returns 200 when dependencies are healthy
- ✅ `/health/ready` returns 503 when database is down
- ✅ `/health/detailed` shows all dependency statuses

---

## Phase 4: Local Monitoring Stack

**Goal**: Run Prometheus and Grafana locally using Docker Compose

### What We'll Build
- Prometheus server to scrape application metrics
- Grafana for visualization
- Docker Compose orchestration
- Persistent storage for metrics and dashboards

### Files to Create
1. `monitoring/docker-compose.yml` - Monitoring stack definition
2. `monitoring/prometheus/prometheus.yml` - Prometheus configuration
3. `monitoring/prometheus/alerts.yml` - Alert rules
4. `monitoring/grafana/datasources.yml` - Grafana data sources
5. `monitoring/grafana/dashboards/` - Dashboard JSON files

### Directory Structure
```
monitoring/
├── docker-compose.yml
├── prometheus/
│   ├── prometheus.yml
│   └── alerts/
│       └── application.yml
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── prometheus.yml
│   │   └── dashboards/
│   │       └── dashboards.yml
│   └── dashboards/
│       ├── application-overview.json
│       └── database-performance.json
└── data/
    ├── prometheus/
    └── grafana/
```

### Implementation Steps

#### Step 4.1: Create Monitoring Directory
```bash
mkdir -p monitoring/prometheus/alerts
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p monitoring/grafana/provisioning/dashboards
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/data/prometheus
mkdir -p monitoring/data/grafana
```

#### Step 4.2: Create Prometheus Configuration
Create `monitoring/prometheus/prometheus.yml`

#### Step 4.3: Create Docker Compose File
Create `monitoring/docker-compose.yml` with:
- Prometheus service (port 9090)
- Grafana service (port 3001)
- Volume mounts for persistence
- Network configuration

#### Step 4.4: Configure Grafana Data Source
Create `monitoring/grafana/provisioning/datasources/prometheus.yml`

#### Step 4.5: Start Monitoring Stack

**Sanity Check Commands**:
```bash
# Navigate to monitoring directory
cd monitoring

# Start the stack
docker-compose up -d

# Check running containers
docker-compose ps

# Expected output:
# NAME                COMMAND             STATUS      PORTS
# prometheus          /bin/prometheus     Up          0.0.0.0:9090->9090/tcp
# grafana             /run.sh             Up          0.0.0.0:3001->3000/tcp

# View logs
docker-compose logs -f

# Test Prometheus
curl http://localhost:9090/-/healthy

# Test Grafana
curl http://localhost:3001/api/health
```

#### Step 4.6: Configure Prometheus Target

**Update `prometheus.yml` to scrape your application**:
```yaml
scrape_configs:
  - job_name: 'legal-form-app'
    scrape_interval: 15s
    static_configs:
      - targets: ['host.docker.internal:3000']  # Mac/Windows
        # For Linux: use your local IP instead
```

**Sanity Check Commands**:
```bash
# Restart Prometheus to load new config
docker-compose restart prometheus

# Open Prometheus UI
open http://localhost:9090

# Go to Status > Targets
# Verify 'legal-form-app' target shows as UP

# Query metrics in Prometheus
# Navigate to Graph tab and enter:
# http_requests_total

# You should see your application metrics
```

**Expected Results**:
- ✅ Prometheus UI accessible at http://localhost:9090
- ✅ Grafana UI accessible at http://localhost:3001 (admin/admin)
- ✅ Prometheus shows application target as UP
- ✅ Metrics visible in Prometheus query interface

---

## Phase 5: Dashboards & Alerts

**Goal**: Create Grafana dashboards and Prometheus alerts

### What We'll Build
1. **Application Overview Dashboard**
   - Request rate (QPS)
   - Error rate (%)
   - Response time (p50, p95, p99)
   - Active database connections

2. **Business Metrics Dashboard**
   - Form submissions over time
   - Pipeline execution success/failure
   - Database query performance
   - Dropbox upload statistics

3. **Alert Rules**
   - High error rate (>5% for 5 minutes)
   - Slow response time (p95 > 1s)
   - Database connection pool exhaustion
   - Pipeline failures

### Implementation Steps

#### Step 5.1: Create Application Dashboard
Create `monitoring/grafana/dashboards/application-overview.json` with panels for:
- Request rate (QPS)
- Error rate percentage
- Latency percentiles (p50, p95, p99)
- HTTP status code distribution

#### Step 5.2: Create Business Dashboard
Create `monitoring/grafana/dashboards/business-metrics.json` with panels for:
- Form submissions (counter)
- Pipeline execution rate
- Database performance
- Dropbox uploads

#### Step 5.3: Configure Dashboard Provisioning
Create `monitoring/grafana/provisioning/dashboards/dashboards.yml`

#### Step 5.4: Create Alert Rules
Create `monitoring/prometheus/alerts/application.yml` with:
- HighErrorRate
- SlowResponseTime
- DatabaseConnectionPoolHigh
- PipelineFailureRate

#### Step 5.5: Reload Monitoring Stack

**Sanity Check Commands**:
```bash
cd monitoring

# Restart to load dashboards
docker-compose restart grafana

# Reload Prometheus config
docker-compose exec prometheus kill -HUP 1

# Login to Grafana
open http://localhost:3001
# Username: admin
# Password: admin (change on first login)

# Verify dashboards
# Navigate to Dashboards > Browse
# You should see:
# - Application Overview
# - Business Metrics

# Verify alerts in Prometheus
open http://localhost:9090/alerts

# Generate traffic to see metrics
for i in {1..100}; do
  curl http://localhost:3000/api/health
done

# Check dashboard updates in Grafana
```

**Expected Results**:
- ✅ Grafana shows 2+ dashboards
- ✅ Dashboards display real-time metrics
- ✅ Prometheus shows alert rules (may be in "Pending" state)
- ✅ Metrics update as you generate traffic

---

## GCP Migration Guide

### Overview
This setup is designed for easy migration to Google Cloud Platform.

### GCP Services Mapping

| Local Component | GCP Service | Migration Path |
|----------------|-------------|----------------|
| Prometheus | Cloud Monitoring | Native integration via OpenTelemetry |
| Grafana | Cloud Monitoring Dashboards | Export JSON, recreate in GCP |
| Winston Logs | Cloud Logging | winston-gcp transport |
| Health Checks | Load Balancer Health Checks | Use existing endpoints |
| Docker Compose | Cloud Run / GKE | Container deployment |

### Phase 6: GCP Preparation (Future)

#### Step 6.1: Add GCP Dependencies
```bash
npm install --save @google-cloud/logging @google-cloud/monitoring
```

#### Step 6.2: Create GCP Logger Transport
```javascript
// monitoring/logger.js
const { LoggingWinston } = require('@google-cloud/logging-winston');

if (process.env.NODE_ENV === 'production') {
  logger.add(new LoggingWinston({
    projectId: process.env.GCP_PROJECT_ID,
    keyFilename: process.env.GCP_KEY_FILE
  }));
}
```

#### Step 6.3: Update Health Checks for GCP Load Balancer
```javascript
// Already compatible!
// GCP Load Balancer can use /health and /health/ready
```

#### Step 6.4: Deploy to Cloud Run (Container-based)
```bash
# Build Docker image
docker build -t gcr.io/[PROJECT_ID]/legal-form-app .

# Push to GCR
docker push gcr.io/[PROJECT_ID]/legal-form-app

# Deploy to Cloud Run
gcloud run deploy legal-form-app \
  --image gcr.io/[PROJECT_ID]/legal-form-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Note**: Detailed GCP migration steps will be documented after Phase 5 completion.

---

## Troubleshooting

### Issue: Prometheus shows target as DOWN

**Check**:
```bash
# Test metrics endpoint directly
curl http://localhost:3000/metrics

# Check Prometheus logs
docker-compose logs prometheus

# For Mac/Windows, ensure host.docker.internal resolves
ping host.docker.internal

# For Linux, use your machine's IP
ifconfig | grep "inet "
```

**Solution**: Update `prometheus.yml` with correct target address.

### Issue: No metrics appearing in Grafana

**Check**:
```bash
# Verify Prometheus is scraping
open http://localhost:9090/targets

# Query metrics directly in Prometheus
open http://localhost:9090/graph
# Enter: http_requests_total

# Check Grafana data source
# Grafana > Configuration > Data Sources > Prometheus
# Click "Test" button
```

**Solution**: Ensure Prometheus data source URL is correct: `http://prometheus:9090`

### Issue: Log files not created

**Check**:
```bash
# Verify logs directory exists and is writable
ls -ld logs/
mkdir -p logs/

# Check server startup logs
npm start

# Test logger directly
node -e "const logger = require('./monitoring/logger'); logger.info('test');"
```

### Issue: Database health check fails

**Check**:
```bash
# Test PostgreSQL connection
psql -U ryanhaines -d legal_forms_db -c "SELECT 1;"

# Check connection pool in code
# Verify DB credentials in .env file
cat .env | grep DB_
```

---

## Next Steps After Completion

1. **Load Testing**: Use tools like `artillery` or `k6` to generate realistic load
2. **Alerting Integration**: Connect Prometheus Alertmanager to Slack/PagerDuty
3. **Distributed Tracing**: Add OpenTelemetry for request tracing across services
4. **Log Analysis**: Set up log parsing and alerting on error patterns
5. **SLO Definition**: Define Service Level Objectives (e.g., 99.9% availability)

---

## Summary

### What You'll Have After All Phases

✅ **Metrics**: Prometheus collecting application and business metrics
✅ **Logs**: Structured JSON logs with rotation and correlation IDs
✅ **Health Checks**: Liveness and readiness probes for load balancers
✅ **Dashboards**: Grafana visualizations for monitoring
✅ **Alerts**: Automated alerts for critical issues
✅ **GCP Ready**: Architecture prepared for cloud migration

### Estimated Time
- Phase 1: 1-2 hours
- Phase 2: 1 hour
- Phase 3: 30 minutes
- Phase 4: 1 hour
- Phase 5: 1-2 hours
- **Total**: 4-6 hours

### Resources Required
- Disk Space: ~500MB (Docker images + log files)
- Memory: ~512MB (Prometheus + Grafana containers)
- CPU: Minimal impact on development machine

---

**Questions or Issues?**
Contact: [Your Contact Info]
Documentation: See individual component READMEs in `monitoring/` directory

---

*This monitoring setup follows industry best practices and is based on Google's SRE principles and the Four Golden Signals framework.*
