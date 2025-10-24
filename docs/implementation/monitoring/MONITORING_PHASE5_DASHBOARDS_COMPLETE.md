# Monitoring Phase 5 Complete: Grafana Dashboards ✅

**Completion Date**: 2025-10-21
**Phase**: Grafana Dashboards & Visualization
**Status**: Successfully Implemented and Tested

---

## What Was Implemented

### 3 Production-Ready Grafana Dashboards Created ✅

All dashboards automatically load on Grafana startup via provisioning.

#### 1. **Application Overview Dashboard** (`application-overview.json`)
**Size**: 22KB | **Panels**: 10

**Tracks HTTP and application performance metrics:**
- Request Rate (QPS) - Real-time queries per second
- Error Rate (5xx) - Percentage of server errors with thresholds
- P95 Latency - 95th percentile response time
- Application Status - UP/DOWN indicator
- HTTP Request Rate by Method (GET, POST, etc.)
- HTTP Response Status Codes (2xx, 3xx, 4xx, 5xx)
- HTTP Request Latency Percentiles (P50, P95, P99)
- P95 Latency by Route - Identify slow endpoints
- HTTP Traffic (Request/Response Size)
- Top Routes by Request Count

**Color-coded thresholds:**
- Green: Healthy (error rate <1%, latency <1s)
- Yellow: Warning (error rate 1-5%, latency 1-5s)
- Red: Critical (error rate >5%, latency >5s)

#### 2. **Business Metrics Dashboard** (`business-metrics.json`)
**Size**: 28KB | **Panels**: 12

**Tracks business-specific metrics:**
- Form Submissions (Last Hour) - Total count
- Form Submission Error Rate - Percentage with thresholds
- Pipeline Executions (Last Hour) - Document processing count
- Database P95 Query Time - Database performance
- Form Submissions Over Time - Success vs error breakdown
- Form Processing Time - P50, P95, P99 latencies
- Average Form Parties - Plaintiffs and defendants count
- Pipeline Executions - Success vs error over time
- Pipeline Execution Duration - P50, P95, P99 latencies
- Database Connection Pool - Active, idle, waiting connections
- Database Query Latency - P50, P95, P99 query times
- Database Operations - Query counts by operation type with error tracking

**Business insights:**
- Form submission success rates
- Processing time trends
- Database health and performance
- Pipeline execution patterns

#### 3. **System Resources Dashboard** (`system-resources.json`)
**Size**: 26KB | **Panels**: 12

**Tracks Node.js and system resources:**
- Memory Usage (RSS) - Resident set size with thresholds
- Heap Memory Used - JavaScript heap usage
- Event Loop Lag - Node.js responsiveness indicator
- Application Uptime - Time since last restart
- Node.js Memory Usage - RSS, heap total, heap used, external memory
- Event Loop Lag - Min, max, and current lag
- Heap Memory Breakdown - New space, old space, code, map, large objects
- Garbage Collection Rate - GC frequency
- CPU Usage - User and system CPU percentages
- Active Handles & Requests - Node.js internal counters
- Node.js Version Info - Runtime version details
- Open File Descriptors - OS resource tracking

**Health indicators:**
- Memory thresholds: Yellow >512MB, Red >1GB
- Event loop lag: Yellow >100ms, Red >500ms
- CPU and I/O patterns

---

## Files Created

| File | Purpose | Size | Panels |
|------|---------|------|--------|
| `grafana/dashboards/application-overview.json` | HTTP & application metrics | 22KB | 10 |
| `grafana/dashboards/business-metrics.json` | Business & database metrics | 28KB | 12 |
| `grafana/dashboards/system-resources.json` | Node.js & system resources | 26KB | 12 |

### Configuration Updated

- **`docker-compose.yml`** - Updated Grafana volume mounts to include dashboard directory
- **`grafana/provisioning/dashboards/dashboards.yml`** - Updated path to `/var/lib/grafana/dashboards`

---

## Dashboard Features

### Auto-Refresh
All dashboards refresh every **10 seconds** for real-time monitoring.

### Time Range
Default view: **Last 1 hour** (adjustable in Grafana UI)

### Folder Organization
All dashboards are organized under **"Legal Form Application"** folder in Grafana.

### Interactive Features
- **Tooltips**: Hover over graphs for detailed values
- **Legend Tables**: Show mean, max, and sum calculations
- **Time Range Selection**: Click and drag to zoom into specific time periods
- **Panel Links**: Click panel titles to expand/edit
- **Auto-scaling**: Y-axes adjust automatically to data ranges

---

## Accessing the Dashboards

### Open Grafana
1. Navigate to: http://localhost:3001
2. Login with your credentials (default: admin/admin if not changed)

### Find the Dashboards

**Option 1: Via Folder**
1. Click **Dashboards** in the left sidebar
2. Open the **"Legal Form Application"** folder
3. You'll see all 3 dashboards:
   - Legal Form App - Application Overview
   - Legal Form App - Business Metrics
   - Legal Form App - System Resources

**Option 2: Via Search**
1. Click the **Search** icon (magnifying glass) in the left sidebar
2. Type "Legal Form App"
3. Select the dashboard you want to view

---

## Sanity Check Commands

### 1. Verify Dashboard Files Exist

```bash
ls -lh monitoring/grafana/dashboards/
```

**Expected Output**:
```
application-overview.json    22KB
business-metrics.json        28KB
system-resources.json        26KB
```

### 2. Check Grafana Logs for Dashboard Provisioning

```bash
cd monitoring
docker-compose logs grafana | grep -i "provision.*dashboard"
```

**Expected Output**:
```
logger=provisioning.dashboard msg="starting to provision dashboards"
logger=provisioning.dashboard msg="finished to provision dashboards"
```

### 3. Restart Grafana (if dashboards don't appear)

```bash
cd monitoring
docker-compose restart grafana
```

Wait 10-15 seconds for Grafana to fully start, then refresh your browser.

### 4. Check Grafana is Healthy

```bash
cd monitoring
docker-compose ps grafana
```

**Expected Output**:
```
NAME      STATUS
grafana   Up (healthy)
```

---

## Testing the Dashboards

### Test 1: Application Overview Dashboard

1. Open **Legal Form App - Application Overview**
2. **Check panels populate with data:**
   - Request Rate should show >0 if app is receiving traffic
   - Application Status should show "UP" in green
   - Error Rate should be low or 0%
   - Latency graphs should show response times

3. **Generate test traffic:**
   ```bash
   # Open your app in browser
   curl http://localhost:3000/
   curl http://localhost:3000/health
   curl http://localhost:3000/metrics
   ```

4. **Verify metrics update** (within 10 seconds):
   - Request Rate increases
   - Graphs show new data points
   - Status codes show in breakdown

### Test 2: Business Metrics Dashboard

1. Open **Legal Form App - Business Metrics**
2. **Check database metrics:**
   - Database P95 Query Time shows values
   - Database Connection Pool shows active connections
   - Database Operations panel shows query counts

3. **Submit a test form** (if app is running):
   - Navigate to http://localhost:3000
   - Fill out and submit a form
   - Return to dashboard

4. **Verify business metrics update:**
   - Form Submissions (Last Hour) increments
   - Form Submissions Over Time shows new data point
   - Form Processing Time updates

### Test 3: System Resources Dashboard

1. Open **Legal Form App - System Resources**
2. **Check system metrics populate:**
   - Memory Usage shows current RSS
   - Heap Memory Used shows values
   - Event Loop Lag shows latency
   - Application Uptime shows time running

3. **Verify graphs show trends:**
   - Memory usage graphs show patterns
   - CPU usage shows activity
   - GC rate shows garbage collection

4. **Node.js Version Info panel** should show:
   - Node.js version
   - V8 version

---

## Dashboard Customization

### Editing Dashboards

1. Open any dashboard
2. Click the **gear icon** (⚙️) in the top right
3. Select **Settings**
4. Make changes (panels, queries, thresholds, etc.)
5. Click **Save dashboard**

**Note**: Dashboard JSON files will NOT be overwritten. Your changes persist in Grafana's database.

### Adding New Panels

1. Open a dashboard
2. Click **Add** → **Visualization**
3. Select **Prometheus** datasource
4. Enter a PromQL query
5. Configure visualization type (graph, stat, gauge, etc.)
6. Click **Apply**

### Creating New Dashboards

1. Click **Dashboards** → **New** → **New Dashboard**
2. Add panels with Prometheus queries
3. Save to "Legal Form Application" folder
4. Export JSON and save to `monitoring/grafana/dashboards/` (optional)

---

## Useful PromQL Queries

These queries can be used to create custom panels:

### HTTP Metrics
```promql
# Request rate
sum(rate(http_requests_total[5m]))

# Error percentage
sum(rate(http_requests_total{status_code=~"5.."}[5m]))
/ sum(rate(http_requests_total[5m])) * 100

# P95 latency
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)

# Requests by endpoint
sum(rate(http_requests_total[5m])) by (route)
```

### Business Metrics
```promql
# Form submissions per minute
sum(increase(form_submissions_total[1m])) by (status)

# Pipeline success rate
sum(rate(pipeline_executions_total{status="success"}[5m]))
/ sum(rate(pipeline_executions_total[5m])) * 100

# Average plaintiffs per form
avg(form_plaintiffs_count)

# Database pool saturation
database_pool_connections_active
/ (database_pool_connections_active + database_pool_connections_idle) * 100
```

### System Metrics
```promql
# Memory usage in MB
nodejs_process_resident_memory_bytes / (1024 * 1024)

# Heap utilization percentage
nodejs_heap_size_used_bytes / nodejs_heap_size_total_bytes * 100

# Event loop lag in ms
nodejs_eventloop_lag_seconds * 1000

# CPU usage percentage
rate(process_cpu_user_seconds_total[5m]) * 100
```

---

## Alerting (Future Enhancement)

While dashboards provide visualization, you can also set up Grafana alerts:

1. **Open a panel** → **Edit**
2. Go to **Alert** tab
3. **Create alert rule** with conditions
4. **Configure notifications** (email, Slack, etc.)

**Current Setup**: Alert rules are defined in Prometheus (`prometheus/alerts/application.yml`). View active alerts in Prometheus UI at http://localhost:9090/alerts

---

## Troubleshooting

### Issue: Dashboards Not Appearing

**Solution 1**: Restart Grafana
```bash
cd monitoring
docker-compose restart grafana
```

**Solution 2**: Check logs for errors
```bash
docker-compose logs grafana | tail -50
```

**Solution 3**: Verify provisioning config
```bash
cat grafana/provisioning/dashboards/dashboards.yml
```

### Issue: No Data in Panels

**Possible Causes**:
1. Application not running → Start with `npm start`
2. Prometheus not scraping → Check http://localhost:9090/targets
3. Wrong time range → Adjust time picker in top-right
4. No traffic generated → Access app at http://localhost:3000

**Solution**: Generate test traffic
```bash
for i in {1..10}; do curl -s http://localhost:3000/health > /dev/null; sleep 1; done
```

### Issue: Panel Shows "No Data"

**Check**:
1. Verify metric exists in Prometheus: http://localhost:9090
2. Try the query in Prometheus UI first
3. Check metric name spelling in panel query
4. Verify time range includes data

### Issue: Graphs Not Updating

**Solution**: Check auto-refresh
- Look for refresh interval in top-right (should say "10s")
- Click the dropdown to enable/change refresh rate
- Or manually click the **Refresh** icon

---

## GCP Migration Notes

These Grafana dashboards use standard Prometheus queries that will work with **Google Cloud Monitoring** (formerly Stackdriver):

### Migration Path

| Local Setup | GCP Equivalent |
|------------|----------------|
| Grafana Dashboards | Cloud Monitoring Dashboards |
| Prometheus Queries (PromQL) | MQL (Monitoring Query Language) |
| Auto-provisioning | Terraform / gcloud CLI |
| Dashboard JSON | Dashboard JSON (compatible format) |

### Export for GCP

To export dashboards for GCP migration:

1. Open dashboard in Grafana
2. Click **Share** (icon in top-right)
3. Go to **Export** tab
4. Click **Save to file**
5. Store JSON for later migration

**Note**: PromQL queries may need conversion to MQL for Cloud Monitoring.

---

## Dashboard Summary

### Dashboards Created: 3

1. **Application Overview** - HTTP performance, latency, errors
2. **Business Metrics** - Forms, pipeline, database performance
3. **System Resources** - Memory, CPU, Node.js internals

### Total Panels: 34
- 10 panels (Application Overview)
- 12 panels (Business Metrics)
- 12 panels (System Resources)

### Metrics Visualized: 40+
- HTTP requests, latency, status codes, traffic
- Form submissions, processing time, party counts
- Pipeline executions, duration, success rates
- Database queries, pool, latency, operations
- Memory (RSS, heap, spaces, GC)
- CPU, event loop, handles, file descriptors

### Refresh Rate: 10 seconds
All dashboards auto-refresh every 10 seconds for real-time monitoring.

---

## Phase 5 Completion Checklist

- [x] Create Application Overview Dashboard (10 panels)
- [x] Create Business Metrics Dashboard (12 panels)
- [x] Create System Resources Dashboard (12 panels)
- [x] Configure dashboard provisioning in Grafana
- [x] Update docker-compose.yml with dashboard volume mounts
- [x] Restart Grafana to load dashboards
- [x] Verify dashboards appear in Grafana UI
- [x] Test panels display metrics correctly
- [x] Document dashboard usage and queries
- [x] Create completion documentation

---

## All Monitoring Phases Complete! 🎉

✅ **Phase 1**: Application Metrics (Prometheus client)
✅ **Phase 2**: Structured Logging (Winston)
✅ **Phase 3**: Health Checks & Readiness Probes
✅ **Phase 4**: Local Monitoring Stack (Docker Compose)
✅ **Phase 5**: Grafana Dashboards ← JUST COMPLETED

**Total Monitoring Implementation**:
- **Lines of Code**: ~4,100 lines (including dashboards)
- **Configuration Files**: 12 files
- **Dashboards**: 3 production-ready dashboards
- **Panels**: 34 visualization panels
- **Metrics**: 40+ metrics tracked
- **Alerts**: 14 alert rules configured

---

## Next Steps (Optional Enhancements)

### Immediate Improvements
1. **Customize thresholds** - Adjust warning/critical levels based on your app's baseline
2. **Add more panels** - Create panels for specific business metrics you care about
3. **Set up Grafana alerts** - Configure email/Slack notifications for dashboard panels

### Advanced Monitoring
1. **Add PostgreSQL Exporter** - Detailed database metrics (connections, queries, cache hit rates)
2. **Add Node Exporter** - System-level metrics (CPU, disk, network)
3. **Distributed Tracing** - Implement Jaeger for request flow visualization
4. **Log Aggregation** - Ship logs to Loki or Elasticsearch
5. **Alertmanager** - Route Prometheus alerts to multiple channels (email, Slack, PagerDuty)

### Production Readiness
1. **Secure Grafana** - Change default password, enable HTTPS
2. **Backup dashboards** - Export and version control dashboard JSON
3. **SLO/SLI tracking** - Define and monitor Service Level Objectives
4. **Synthetic monitoring** - Add uptime checks with Blackbox Exporter

---

*Phase 5 implementation completed successfully. Full observability stack with metrics, logs, health checks, and dashboards is now operational!*
