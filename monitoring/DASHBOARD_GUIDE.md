# Grafana Dashboard Guide 📊

**Complete guide to understanding your monitoring dashboards**

---

## Table of Contents

1. [Dashboard 1: Application Overview](#dashboard-1-application-overview)
2. [Dashboard 2: Business Metrics](#dashboard-2-business-metrics)
3. [Dashboard 3: System Resources](#dashboard-3-system-resources)
4. [Understanding the Numbers](#understanding-the-numbers)
5. [Alert Thresholds](#alert-thresholds)

---

# Dashboard 1: Application Overview

**Purpose**: Monitor HTTP traffic, application performance, and response times

**When to use**:
- Checking if your app is responding normally
- Investigating slow response times
- Identifying error spikes
- Monitoring traffic patterns

---

## Panel: Request Rate (QPS)

**What it shows**: Queries (requests) per second hitting your application

**Metric**: `sum(rate(http_requests_total[5m]))`

**What it means**:
- Shows how busy your application is
- Rate is calculated over 5-minute windows
- Includes all HTTP requests (GET, POST, etc.)

**What to watch for**:
- ✅ **Normal**: Steady rate matching your expected traffic
- ⚠️ **Concern**: Sudden drops (might indicate app crashed or network issues)
- ⚠️ **Concern**: Unexpected spikes (could be traffic surge or attack)

**Example values**:
- Development: 0.1 - 5 req/sec
- Low traffic: 5 - 50 req/sec
- Medium traffic: 50 - 500 req/sec
- High traffic: 500+ req/sec

---

## Panel: Error Rate (5xx)

**What it shows**: Percentage of requests returning server errors (500-599 status codes)

**Metric**: `sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100`

**What it means**:
- 5xx errors = something broke on the server
- Common 5xx errors:
  - 500 Internal Server Error
  - 502 Bad Gateway
  - 503 Service Unavailable

**What to watch for**:
- ✅ **Healthy**: 0% (no errors)
- ✅ **Good**: < 0.1% (less than 1 error per 1000 requests)
- ⚠️ **Warning**: 1-5% (investigate, something might be wrong)
- 🚨 **Critical**: > 5% (serious issue, users are experiencing errors)

**Color indicators**:
- Green: 0-1%
- Yellow: 1-5%
- Red: >5%

---

## Panel: P95 Latency

**What it shows**: 95th percentile response time (in seconds)

**Metric**: `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))`

**What it means**:
- P95 = 95% of requests are faster than this time
- Only 5% of requests are slower
- Better indicator than average because it shows worst-case performance

**What to watch for**:
- ✅ **Excellent**: < 0.1s (100ms)
- ✅ **Good**: 0.1-0.5s (100-500ms)
- ⚠️ **Slow**: 0.5-2s (500ms-2s) - users will notice
- 🚨 **Critical**: > 2s - investigate immediately

**Color indicators**:
- Green: < 1s
- Yellow: 1-5s
- Red: > 5s

---

## Panel: Application Status

**What it shows**: Whether your application is up and responding

**Metric**: `up{job="legal-form-app"}`

**What it means**:
- 1 = Application is UP and responding to Prometheus
- 0 = Application is DOWN or unreachable

**What to watch for**:
- ✅ **UP**: Shows green with "UP" text
- 🚨 **DOWN**: Shows red with "DOWN" text - app crashed or network issue

---

## Panel: HTTP Request Rate by Method

**What it shows**: Requests per second broken down by HTTP method (GET, POST, etc.)

**Metric**: `sum(rate(http_requests_total[5m])) by (method)`

**What it means**:
- GET: Read operations (loading pages, fetching data)
- POST: Write operations (form submissions, creating data)
- PUT: Update operations
- DELETE: Delete operations

**What to watch for**:
- ✅ **Normal**: GET requests typically highest (users browsing)
- ⚠️ **Unusual**: Very high POST rate might indicate automation or attack
- Pattern changes: Sudden method distribution changes

---

## Panel: HTTP Response Status Codes

**What it shows**: Stacked graph of response status codes over time

**Metric**: `sum(rate(http_requests_total[5m])) by (status_code)`

**What it means**:
- **2xx (Green)**: Success - request completed successfully
  - 200 OK
  - 201 Created
- **3xx (Blue)**: Redirection - request redirected elsewhere
  - 301 Moved Permanently
  - 302 Found
- **4xx (Yellow)**: Client errors - user/client made mistake
  - 400 Bad Request
  - 404 Not Found
  - 403 Forbidden
- **5xx (Red)**: Server errors - your application failed
  - 500 Internal Server Error
  - 503 Service Unavailable

**What to watch for**:
- ✅ **Healthy**: Mostly 2xx (green at bottom)
- ⚠️ **4xx spike**: Check for broken links or bad client requests
- 🚨 **5xx present**: Fix server errors immediately

---

## Panel: HTTP Request Latency Percentiles

**What it shows**: Response time distribution (P50, P95, P99)

**Metrics**:
- P50: `histogram_quantile(0.50, ...)` - median (50% faster, 50% slower)
- P95: `histogram_quantile(0.95, ...)` - 95% of requests faster
- P99: `histogram_quantile(0.99, ...)` - 99% of requests faster

**What it means**:
- **P50 (median)**: Typical user experience
- **P95**: What slower requests experience
- **P99**: Worst-case scenarios (only 1% slower)

**What to watch for**:
- ✅ **Good spread**: P50 << P95 << P99 (most requests fast, few slow)
- ⚠️ **Large gap**: P50=0.1s, P99=5s → some users having terrible experience
- 🚨 **All high**: All percentiles >1s → systemic performance issue

**Example healthy values**:
- P50: 50ms
- P95: 200ms
- P99: 500ms

---

## Panel: P95 Latency by Route

**What it shows**: Which API endpoints/pages are slowest

**Metric**: `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, route))`

**What it means**:
- Shows P95 latency for each route separately
- Helps identify specific slow endpoints

**What to watch for**:
- Routes consistently slower than others
- Routes that suddenly become slow
- Routes exceeding acceptable latency thresholds

**Common patterns**:
- `/` homepage: Should be fast (< 100ms)
- `/api/form-entries` POST: May be slower (form processing)
- Database-heavy routes: Expected to be slower

---

## Panel: HTTP Traffic (Request/Response Size)

**What it shows**: Bandwidth usage (bytes per second)

**Metrics**:
- Request: `sum(rate(http_request_size_bytes_sum[5m]))`
- Response: `sum(rate(http_response_size_bytes_sum[5m]))`

**What it means**:
- How much data is flowing in (request) and out (response)
- Measured in bytes/sec

**What to watch for**:
- Response typically larger than request
- Sudden spikes might indicate large file downloads or data dumps
- Sustained high throughput might need bandwidth optimization

---

## Panel: Top Routes by Request Count

**What it shows**: Which endpoints receive the most traffic

**Metric**: `sum(increase(http_requests_total[1m])) by (route)`

**What it means**:
- Bar chart showing request counts per route
- Identifies your most-used endpoints

**What to watch for**:
- Expected routes at the top (homepage, popular pages)
- Unexpected high traffic to obscure routes
- Changes in route popularity patterns

---

# Dashboard 2: Business Metrics

**Purpose**: Monitor business-specific metrics (forms, pipeline, database)

**When to use**:
- Tracking form submission success rates
- Monitoring document generation pipeline
- Database performance issues
- Business intelligence and reporting

---

## Panel: Form Submissions (Last Hour)

**What it shows**: Total number of forms submitted in the last hour

**Metric**: `sum(increase(form_submissions_total[1h]))`

**What it means**:
- Counts successful form submissions
- Rolling 1-hour window

**What to watch for**:
- ✅ **Expected**: Matches your typical form submission rate
- ⚠️ **Zero**: No forms submitted recently (normal off-hours, or issue?)
- ⚠️ **Very high**: Could indicate automated testing or issues

**Note about decimals**:
- You might see "1.02" instead of "1"
- This is normal - Prometheus extrapolates over time windows
- Treat as "approximately 1"

---

## Panel: Form Submission Error Rate

**What it shows**: Percentage of form submissions that failed

**Metric**: `sum(rate(form_submissions_total{status="error"}[5m])) / sum(rate(form_submissions_total[5m])) * 100`

**What it means**:
- Error = form failed to save or process
- Could be validation errors, database issues, or server crashes

**What to watch for**:
- ✅ **Perfect**: 0% (no errors)
- ⚠️ **Warning**: 10-20% (investigate common failure reasons)
- 🚨 **Critical**: > 20% (serious issue preventing form submissions)

**Color indicators**:
- Green: < 10%
- Yellow: 10-20%
- Red: > 20%

---

## Panel: Pipeline Executions (Last Hour)

**What it shows**: Number of document generation pipeline runs in the last hour

**Metric**: `sum(increase(pipeline_executions_total[1h]))`

**What it means**:
- Each form submission triggers a pipeline execution
- Pipeline generates legal documents from form data

**What to watch for**:
- Should roughly match "Form Submissions (Last Hour)"
- ⚠️ **Lower than forms**: Some forms not triggering pipeline
- **Zero**: Pipeline disabled or failing to start

---

## Panel: Database P95 Query Time

**What it shows**: 95th percentile database query duration (milliseconds)

**Metric**: `histogram_quantile(0.95, sum(rate(database_query_duration_seconds_bucket[5m])) by (le)) * 1000`

**What it means**:
- How long database queries take
- P95 = 95% of queries complete faster than this

**What to watch for**:
- ✅ **Excellent**: < 10ms
- ✅ **Good**: 10-50ms
- ⚠️ **Slow**: 50-100ms (consider optimization)
- 🚨 **Critical**: > 100ms (serious performance issue)

**Color indicators**:
- Green: < 50ms
- Yellow: 50-100ms
- Red: > 100ms

---

## Panel: Form Submissions Over Time

**What it shows**: Success vs error submissions as a stacked graph

**Metric**: `sum(increase(form_submissions_total[5m])) by (status)`

**What it means**:
- Green area: Successful submissions
- Red area: Failed submissions
- Shows trends over time

**What to watch for**:
- ✅ **Healthy**: Mostly/all green
- ⚠️ **Red appearing**: Errors occurring, investigate logs
- Patterns: Errors at specific times might indicate scheduled job conflicts

---

## Panel: Form Processing Time

**What it shows**: How long it takes to process and save a form (P50, P95, P99)

**Metrics**:
- P50: `histogram_quantile(0.50, sum(rate(form_processing_duration_seconds_bucket[5m])) by (le))`
- P95: `histogram_quantile(0.95, ...)`
- P99: `histogram_quantile(0.99, ...)`

**What it means**:
- Time from form submission to save completion
- Includes data transformation, file write, database insert

**What to watch for**:
- ✅ **Fast**: P95 < 0.5s
- ⚠️ **Acceptable**: P95 0.5-2s
- 🚨 **Slow**: P95 > 2s (users will notice delay)

**Causes of slowness**:
- Database bottleneck
- Slow file I/O
- Complex data transformations

---

## Panel: Average Form Parties (Plaintiffs/Defendants)

**What it shows**: Average number of plaintiffs and defendants per form

**Metrics**:
- Plaintiffs: `avg(form_plaintiffs_count)`
- Defendants: `avg(form_defendants_count)`

**What it means**:
- Shows typical case complexity
- More parties = more complex cases

**What to watch for**:
- Track trends over time
- Unusually high party counts might indicate data issues
- Business intelligence: case complexity patterns

---

## Panel: Pipeline Executions (Over Time)

**What it shows**: Pipeline success vs failure rate

**Metric**: `sum(increase(pipeline_executions_total[5m])) by (status)`

**What it means**:
- Green: Successful document generations
- Red: Failed pipeline runs

**What to watch for**:
- ✅ **Healthy**: All green (100% success)
- ⚠️ **Some red**: Pipeline failures, check logs
- 🚨 **Mostly red**: Pipeline broken, immediate attention needed

**Pipeline failures might indicate**:
- Python API down
- Document template errors
- File system issues
- Network timeouts

---

## Panel: Pipeline Execution Duration

**What it shows**: How long the document generation pipeline takes (P50, P95, P99)

**Metrics**: Same pattern as form processing time

**What it means**:
- Time to generate all legal documents
- Typically several seconds (involves AI/ML processing)

**What to watch for**:
- ✅ **Normal**: P95 5-15 seconds
- ⚠️ **Slow**: P95 15-30 seconds
- 🚨 **Very slow**: P95 > 30 seconds

**Note**: This is background processing, so doesn't block user response

---

## Panel: Database Connection Pool

**What it shows**: Active, idle, and waiting database connections

**Metrics**:
- Active: `database_pool_connections_active`
- Idle: `database_pool_connections_idle`
- Waiting: `database_pool_connections_waiting`

**What it means**:
- **Active**: Currently executing queries
- **Idle**: Available for use
- **Waiting**: Requests waiting for a connection

**What to watch for**:
- ✅ **Healthy**: Mostly idle, some active
- ⚠️ **Busy**: All active, few idle (increase pool size?)
- 🚨 **Waiting > 0**: Pool exhausted, queries being delayed

**Pool configuration**:
- Default: 20 max connections
- Adjust in `.env`: `DB_POOL_MAX=30`

---

## Panel: Database Query Latency

**What it shows**: Database query response times (P50, P95, P99) in milliseconds

**What it means**:
- How fast the database responds to queries
- Same concept as HTTP latency but for database

**What to watch for**:
- ✅ **Excellent**: P95 < 10ms
- ✅ **Good**: P95 10-50ms
- ⚠️ **Slow**: P95 50-200ms
- 🚨 **Critical**: P95 > 200ms

**Causes of slow queries**:
- Missing database indexes
- Complex joins
- Large result sets
- Database under heavy load

---

## Panel: Database Operations

**What it shows**: Query counts by operation type, plus errors

**Metric**: `sum(increase(database_queries_total[5m])) by (operation)`

**What it means**:
- Shows distribution of database operations
- Operations: SELECT, INSERT, UPDATE, DELETE
- Errors shown in red

**What to watch for**:
- ✅ **Normal**: Mostly SELECTs (reads), some INSERTs/UPDATEs (writes)
- ⚠️ **Errors**: Any red line means database errors occurring
- Pattern changes: Sudden increase in DELETEs might be suspicious

---

# Dashboard 3: System Resources

**Purpose**: Monitor Node.js process health and system resource usage

**When to use**:
- Investigating memory leaks
- CPU usage spikes
- Event loop lag (responsiveness issues)
- Garbage collection problems

---

## Panel: Memory Usage (RSS)

**What it shows**: Resident Set Size - total RAM used by Node.js process

**Metric**: `nodejs_process_resident_memory_bytes / (1024 * 1024)` (in MB)

**What it means**:
- RSS = total memory the process is using
- Includes heap, code, stack, etc.

**What to watch for**:
- ✅ **Normal**: Steady or slowly increasing
- ⚠️ **Warning**: > 512 MB (might want to investigate)
- 🚨 **Critical**: > 1 GB or continuously growing (memory leak)

**Color indicators**:
- Green: < 512 MB
- Yellow: 512 MB - 1 GB
- Red: > 1 GB

**Memory leak indicators**:
- Continuously increasing over hours/days
- Never stabilizes
- Eventually crashes with "out of memory"

---

## Panel: Heap Memory Used

**What it shows**: JavaScript heap memory usage (where objects live)

**Metric**: `nodejs_heap_size_used_bytes / (1024 * 1024)` (in MB)

**What it means**:
- Heap = memory for JavaScript objects
- Smaller than RSS (RSS includes everything)

**What to watch for**:
- ✅ **Normal**: 50-256 MB for typical apps
- ⚠️ **Warning**: > 256 MB
- 🚨 **Critical**: > 512 MB or continuously growing

**Color indicators**:
- Green: < 256 MB
- Yellow: 256-512 MB
- Red: > 512 MB

---

## Panel: Event Loop Lag

**What it shows**: Event loop delay in milliseconds

**Metric**: `nodejs_eventloop_lag_seconds * 1000`

**What it means**:
- Event loop = heart of Node.js, processes async operations
- Lag = how long tasks wait before being processed
- **Critical metric for responsiveness**

**What to watch for**:
- ✅ **Excellent**: < 10 ms
- ✅ **Good**: 10-50 ms
- ⚠️ **Warning**: 50-100 ms (users might notice slight delays)
- 🚨 **Critical**: > 100 ms (app feels sluggish)

**Color indicators**:
- Green: < 100 ms
- Yellow: 100-500 ms
- Red: > 500 ms

**Causes of high lag**:
- CPU-intensive synchronous operations
- Blocking I/O
- Inefficient algorithms
- Too many concurrent operations

---

## Panel: Application Uptime

**What it shows**: How long the process has been running (seconds)

**Metric**: `process_uptime_seconds`

**What it means**:
- Time since the process started
- Resets to 0 when app restarts

**What to watch for**:
- Steady increase = stable
- Frequent drops to 0 = app crashing/restarting
- Track uptime for reliability metrics (e.g., "5 9s" = 99.999% uptime)

---

## Panel: Node.js Memory Usage (Detailed)

**What it shows**: Memory breakdown by type

**Metrics**:
- RSS: Total memory
- Heap Total: Allocated heap
- Heap Used: Actually used heap
- External: C++ objects memory

**What it means**:
- Shows memory distribution
- Helps identify what's consuming memory

**What to watch for**:
- **Heap Used approaching Heap Total**: Frequent garbage collection
- **External growing**: Native addon memory usage
- Patterns over time

---

## Panel: Event Loop Lag (Detailed)

**What it shows**: Min, max, and current event loop lag

**Metrics**:
- Current: `nodejs_eventloop_lag_seconds * 1000`
- Min: `nodejs_eventloop_lag_min_seconds * 1000`
- Max: `nodejs_eventloop_lag_max_seconds * 1000`

**What it means**:
- Min: Best case
- Max: Worst case spikes
- Current: Right now

**What to watch for**:
- Max spikes indicate periodic slowness
- Consistently high current value indicates systemic issue

---

## Panel: Heap Memory Breakdown by Space

**What it shows**: V8 heap memory by space type (stacked)

**Spaces**:
- **New Space**: Newly allocated objects (short-lived)
- **Old Space**: Long-lived objects
- **Code Space**: Compiled JavaScript code
- **Map Space**: Hidden classes and maps
- **Large Object Space**: Objects > 1 MB

**What it means**:
- Shows internal V8 memory organization
- Advanced debugging

**What to watch for**:
- Old Space continuously growing = potential leak
- Large Object Space spike = big data structures

---

## Panel: Garbage Collection Rate

**What it shows**: How often garbage collection runs

**Metric**: `rate(nodejs_gc_duration_seconds_count[5m])`

**What it means**:
- GC = cleaning up unused memory
- Higher rate = more memory churn

**What to watch for**:
- ✅ **Normal**: Occasional GC (few times per minute)
- ⚠️ **High**: Very frequent GC (many times per second)
- High GC + high memory = app struggling with memory

**Performance impact**:
- GC pauses JavaScript execution
- Frequent GC = reduced throughput

---

## Panel: CPU Usage

**What it shows**: CPU time used by the process (user + system)

**Metrics**:
- User CPU: `rate(process_cpu_user_seconds_total[5m]) * 100`
- System CPU: `rate(process_cpu_system_seconds_total[5m]) * 100`

**What it means**:
- **User CPU**: Time executing JavaScript code
- **System CPU**: Time in OS kernel (I/O, system calls)
- Percentage of one CPU core

**What to watch for**:
- ✅ **Normal**: 5-30% (varies with traffic)
- ⚠️ **High**: 50-80% (might need optimization)
- 🚨 **Critical**: > 80% sustained (CPU bound, need scaling)

**Note**: 100% = 1 CPU core fully used. Multi-core: can exceed 100%

---

## Panel: Active Handles & Requests

**What it shows**: Node.js internal counters

**Metrics**:
- Active Handles: `nodejs_active_handles_total`
- Active Requests: `nodejs_active_requests_total`

**What it means**:
- **Handles**: Open files, sockets, timers
- **Requests**: Pending async operations

**What to watch for**:
- Steady state or slight fluctuation = normal
- Continuously growing = resource leak
  - File handles not closed
  - Timers not cleared
  - Database connections not released

---

## Panel: Node.js Version Info

**What it shows**: Runtime version information

**What it means**:
- Node.js version
- V8 engine version
- Useful for tracking upgrades

---

## Panel: Open File Descriptors

**What it shows**: Number of open files/sockets

**Metric**: `process_open_fds`

**What it means**:
- Files, network sockets, etc.
- OS has limits (typically 1024-4096)

**What to watch for**:
- ✅ **Normal**: 10-100
- ⚠️ **High**: Approaching OS limit
- 🚨 **At limit**: "Too many open files" errors

---

# Understanding the Numbers

## Why Do I See Decimals (1.02 instead of 1)?

**Reason**: Prometheus interpolates data over time windows

When you see:
- `form_submissions_total = 1.02`
- `increase(form_submissions_total[5m]) = 0.87`

This is **normal and expected**:
- Prometheus scrapes every 10 seconds
- Counters increment at irregular times
- Prometheus extrapolates to fill gaps
- Result: slight fractional values

**Treat as**: "approximately 1" or "close to 1"

---

## Why Does increase() Show 0?

`increase(metric[5m])` calculates the **change** over 5 minutes.

If counter is sitting at 5 for the full 5 minutes:
- Start: 5
- End: 5
- Increase: 0 ✓ (correct!)

**This is working as designed.** Generate new activity to see increases.

---

## What are Rates vs Counters?

**Counter**: Always increases (resets on restart)
- Example: `http_requests_total = 1523`
- Meaning: 1523 total requests since startup

**Rate**: Change per second
- Example: `rate(http_requests_total[5m]) = 5.2`
- Meaning: 5.2 requests per second (averaged over 5 minutes)

**Increase**: Total change over time
- Example: `increase(http_requests_total[1h]) = 18720`
- Meaning: 18,720 requests in the last hour

---

# Alert Thresholds

## Critical Alerts 🚨

**Immediate attention required:**

| Metric | Threshold | Action |
|--------|-----------|---------|
| Error Rate | > 5% | Check logs, investigate errors |
| Application Down | UP = 0 | Restart application |
| Event Loop Lag | > 500ms | Find blocking operations |
| Memory RSS | > 1GB | Check for memory leaks |
| Database Pool Waiting | > 0 | Increase pool size or optimize queries |
| CPU Usage | > 80% sustained | Optimize code or scale horizontally |

---

## Warning Alerts ⚠️

**Investigate soon:**

| Metric | Threshold | Action |
|--------|-----------|---------|
| Error Rate | 1-5% | Review error logs |
| P95 Latency | > 1s | Profile slow endpoints |
| Database Query Time | > 100ms | Add indexes, optimize queries |
| Form Error Rate | > 10% | Check validation logic |
| Memory RSS | > 512MB | Monitor for leaks |
| GC Rate | Very high | Reduce object allocation |

---

## Good Values ✅

**Target ranges:**

| Metric | Healthy Range |
|--------|---------------|
| Error Rate | 0% - 0.1% |
| P95 Latency | < 500ms |
| Database Queries | < 50ms P95 |
| Event Loop Lag | < 50ms |
| Memory RSS | < 512MB stable |
| CPU Usage | 10-40% |
| Form Success Rate | > 99% |
| Pipeline Success Rate | > 95% |

---

# Quick Reference

## Dashboard Health Check (60 seconds)

**Application Overview:**
1. ✅ Application Status = UP (green)
2. ✅ Error Rate < 1% (green)
3. ✅ P95 Latency < 1s (green)

**Business Metrics:**
4. ✅ Form submissions happening (if expected)
5. ✅ Form Error Rate < 10% (green/yellow)
6. ✅ Database Query Time < 100ms (green/yellow)

**System Resources:**
7. ✅ Event Loop Lag < 100ms (green)
8. ✅ Memory RSS stable and < 512MB (green)
9. ✅ No growing trends (memory leaks)

**All green = System healthy! 🎉**

---

## Common Investigation Patterns

### "My app is slow"
1. Check: **P95 Latency** (Application Overview)
2. Check: **P95 Latency by Route** - which endpoints?
3. Check: **Event Loop Lag** (System Resources)
4. Check: **Database Query Time** (Business Metrics)

### "Users seeing errors"
1. Check: **Error Rate** (Application Overview)
2. Check: **HTTP Response Status Codes** - what codes?
3. Check: **Form Submission Error Rate** (Business Metrics)
4. Check application logs for error details

### "Is my database slow?"
1. Check: **Database P95 Query Time** (Business Metrics)
2. Check: **Database Connection Pool** - any waiting?
3. Check: **Database Operations** - any errors?
4. Check: **Database Query Latency** - trends

### "Memory issues?"
1. Check: **Memory RSS** (System Resources) - growing?
2. Check: **Heap Memory Used** - growing?
3. Check: **GC Rate** - very high?
4. Check: **Active Handles & Requests** - growing?

---

## Pro Tips 💡

1. **Set time range to "Last 15 minutes"** when troubleshooting active issues
2. **Use "Last 24 hours"** to see daily patterns and trends
3. **Enable auto-refresh (10s)** for live monitoring
4. **Bookmark your favorite dashboard** for quick access
5. **Compare current vs historical** - is this behavior new?
6. **Check multiple panels together** - issues often show in multiple places
7. **Use Prometheus UI** for custom queries and testing
8. **Export dashboard screenshots** for incident reports

---

**This guide should help you understand and act on your monitoring data! 📈**

*Last updated: 2025-10-21*
