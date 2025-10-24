# Monitoring Phase 4 Complete: Local Monitoring Stack ✅

**Completion Date**: 2025-10-21
**Phase**: Local Monitoring Stack (Docker Compose + Prometheus + Grafana)
**Status**: Successfully Implemented and Tested

---

## What Was Implemented

### 1. Directory Structure Created ✅

```
monitoring/
├── docker-compose.yml                      # Docker Compose orchestration
├── prometheus/
│   ├── prometheus.yml                      # Prometheus configuration
│   └── alerts/
│       └── application.yml                 # Alert rules
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── prometheus.yml              # Datasource auto-config
│   │   └── dashboards/
│   │       └── dashboards.yml              # Dashboard provisioning
│   └── dashboards/                         # Custom dashboards (create in UI)
├── data/
│   ├── prometheus/                         # Metrics storage (30 days)
│   └── grafana/                            # Dashboard storage
├── DOCKER_STACK_README.md                  # Complete usage guide
└── README.md                               # Monitoring documentation
```

### 2. Files Created ✅

#### `docker-compose.yml` (92 lines)
Complete monitoring stack with:
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- Network isolation
- Volume persistence
- Health checks
- Auto-restart policy

#### `prometheus/prometheus.yml` (73 lines)
Prometheus configuration with:
- Scraping from application (port 3000)
- Self-monitoring
- 15-second scrape interval
- Alert rule loading
- External labels for environment tagging

#### `prometheus/alerts/application.yml` (203 lines)
Comprehensive alert rules:
- **Performance**: High error rate, slow response time
- **Database**: Connection pool exhaustion, slow queries
- **Business**: Form submission failures, pipeline failures
- **System**: High memory usage, event loop lag
- **Availability**: Application down detection

#### `grafana/provisioning/datasources/prometheus.yml` (12 lines)
Auto-provisions Prometheus datasource:
- Automatic connection on startup
- No manual configuration needed
- Default datasource

#### `grafana/provisioning/dashboards/dashboards.yml` (14 lines)
Dashboard provisioning setup:
- Watches `dashboards/` directory
- Auto-loads JSON dashboards
- Allows UI updates

#### `DOCKER_STACK_README.md` (400+ lines)
Complete usage guide with:
- Quick start instructions
- Troubleshooting guide
- Dashboard creation examples
- Query examples
- Backup/restore procedures

---

## Services Configured

### Prometheus
- **Port**: 9090
- **Image**: prom/prometheus:latest
- **Storage**: 30 days retention
- **Access**: http://localhost:9090

### Grafana
- **Port**: 3001
- **Image**: grafana/grafana:latest
- **Credentials**: admin/admin (change on first login)
- **Access**: http://localhost:3001

---

## Sanity Check Commands

### 1. Start the Monitoring Stack

```bash
cd monitoring
docker-compose up -d
```

**Expected Output**:
```
Container prometheus  Started
Container grafana  Started
```

### 2. Check Services are Running

```bash
docker-compose ps
```

**Expected Output**:
```
NAME         STATUS                    PORTS
grafana      Up (healthy)              0.0.0.0:3001->3000/tcp
prometheus   Up                        0.0.0.0:9090->9090/tcp
```

### 3. Start Your Application

```bash
# In project root
npm start
```

### 4. Verify Prometheus is Scraping

```bash
# Check targets (should show UP)
curl -s 'http://localhost:9090/api/v1/targets' | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'
```

**Expected Output**:
```json
{
  "job": "legal-form-app",
  "health": "up"
}
{
  "job": "prometheus",
  "health": "up"
}
```

### 5. Query Metrics from Prometheus

```bash
# Query HTTP requests
curl -s 'http://localhost:9090/api/v1/query?query=http_requests_total' | jq '.data.result[0]'
```

**Expected**: JSON with metrics data

### 6. Check Grafana Datasource

```bash
curl -s http://admin:admin@localhost:3001/api/datasources | jq '.[] | {name: .name, type: .type}'
```

**Expected Output**:
```json
{
  "name": "Prometheus",
  "type": "prometheus"
}
```

### 7. Access Web UIs

Open in browser:
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

### 8. Stop the Stack

```bash
cd monitoring
docker-compose down
```

---

## Verification Checklist

- [ ] Docker Compose starts without errors
- [ ] Prometheus accessible at http://localhost:9090
- [ ] Grafana accessible at http://localhost:3001
- [ ] Both containers show as "Up" in `docker-compose ps`
- [ ] Prometheus shows legal-form-app target as UP (green)
- [ ] Grafana has Prometheus datasource configured
- [ ] Metrics queryable in Prometheus UI
- [ ] Alert rules loaded (visible in Prometheus → Alerts)
- [ ] Data persists after restart

---

## Prometheus Target Configuration

### Application Target

```yaml
# In prometheus/prometheus.yml
scrape_configs:
  - job_name: 'legal-form-app'
    scrape_interval: 10s
    static_configs:
      - targets:
          # For Mac/Windows
          - 'host.docker.internal:3000'

          # For Linux (use your IP)
          # - '192.168.1.100:3000'
```

### Target Status

Check in Prometheus UI:
1. Go to http://localhost:9090
2. Click **Status → Targets**
3. Verify `legal-form-app` shows **UP** (green)

---

## Alert Rules Configured

### Critical Alerts
- `HighErrorRate` - >5% errors for 5 minutes
- `VerySlowResponseTime` - P95 >5 seconds
- `DatabaseConnectionPoolExhausted` - Waiting queries >0
- `ApplicationDown` - Can't scrape metrics

### Warning Alerts
- `SlowResponseTime` - P95 >1 second for 10 minutes
- `DatabaseSlowQuery` - P95 >100ms for 5 minutes
- `HighFormSubmissionFailureRate` - >10% failures
- `HighMemoryUsage` - >1GB for 10 minutes

### Info Alerts
- `NoFormSubmissions` - Zero submissions for 2 hours

View alerts: http://localhost:9090/alerts

---

## Using Grafana

### First Login

1. Open http://localhost:3001
2. Login with `admin` / `admin`
3. Set new password (or skip)
4. Prometheus datasource is already configured!

### Create Your First Dashboard

1. Click **Create → Dashboard**
2. Click **Add visualization**
3. Select **Prometheus** datasource
4. Enter query: `rate(http_requests_total[5m])`
5. Customize visualization (graph, stat, table, etc.)
6. Click **Save dashboard**

### Useful Queries

```promql
# Request Rate (QPS)
sum(rate(http_requests_total[5m]))

# Error Rate Percentage
sum(rate(http_requests_total{status_code=~"5.."}[5m]))
/ sum(rate(http_requests_total[5m])) * 100

# P95 Latency
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)

# Form Submissions
sum(increase(form_submissions_total[5m])) by (status)

# Database Pool
database_pool_connections_active
database_pool_connections_waiting

# Memory Usage (MB)
nodejs_process_resident_memory_bytes / (1024 * 1024)
```

---

## Docker Commands Reference

### Start Stack
```bash
cd monitoring
docker-compose up -d              # Start in background
docker-compose logs -f             # Follow logs
```

### Check Status
```bash
docker-compose ps                  # List services
docker-compose logs prometheus     # View Prometheus logs
docker-compose logs grafana        # View Grafana logs
```

### Stop Stack
```bash
docker-compose down                # Stop (keep data)
docker-compose down -v             # Stop + remove data
```

### Restart Services
```bash
docker-compose restart prometheus
docker-compose restart grafana
```

### Reload Prometheus Config
```bash
# After editing prometheus.yml
curl -X POST http://localhost:9090/-/reload

# Or restart
docker-compose restart prometheus
```

---

## Troubleshooting

### Issue: Prometheus shows legal-form-app as DOWN

**Check**:
```bash
# Verify app is running
curl http://localhost:3000/metrics

# Check Prometheus can reach it
docker exec prometheus wget -q -O- http://host.docker.internal:3000/metrics
```

**For Linux users**: Replace `host.docker.internal:3000` with your machine's IP in `prometheus/prometheus.yml`

### Issue: Grafana can't connect to Prometheus

**Check**:
```bash
# Verify both containers are running
docker-compose ps

# Check datasource
curl http://admin:admin@localhost:3001/api/datasources
```

**Solution**: Restart Grafana
```bash
docker-compose restart grafana
```

### Issue: Port already in use

**Check ports**:
```bash
lsof -ti:9090  # Prometheus
lsof -ti:3001  # Grafana
```

**Solution**: Edit `docker-compose.yml` to use different ports:
```yaml
ports:
  - "9091:9090"  # Use 9091 instead
  - "3002:3000"  # Use 3002 instead
```

### Issue: Data not persisting

**Check volumes**:
```bash
ls -la monitoring/data/prometheus
ls -la monitoring/data/grafana
```

**Solution**: Ensure directories exist and have correct permissions

---

## Data Management

### Storage Locations
- **Prometheus data**: `./data/prometheus/`
- **Grafana data**: `./data/grafana/`

### Retention
- **Prometheus**: 30 days (configurable in docker-compose.yml)
- **Grafana**: Unlimited (dashboards persist)

### Backup
```bash
cd monitoring
docker-compose down
tar -czf backup-$(date +%Y%m%d).tar.gz data/
docker-compose up -d
```

### Restore
```bash
cd monitoring
docker-compose down
tar -xzf backup-YYYYMMDD.tar.gz
docker-compose up -d
```

### Clear All Data
```bash
cd monitoring
docker-compose down -v
rm -rf data/prometheus/* data/grafana/*
docker-compose up -d
```

---

## Performance Tips

### Reduce Scrape Frequency

Edit `prometheus/prometheus.yml`:
```yaml
global:
  scrape_interval: 30s  # Instead of 15s
```

### Limit Resources

Add to `docker-compose.yml`:
```yaml
services:
  prometheus:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

### Reduce Retention

Edit `docker-compose.yml`:
```yaml
command:
  - '--storage.tsdb.retention.time=7d'  # Instead of 30d
```

---

## Next Steps

### Immediate
1. ✅ Open Grafana and create your first dashboard
2. ✅ Explore metrics in Prometheus query interface
3. ✅ Generate traffic and watch metrics update

### Short Term
- Create custom Grafana dashboards for your metrics
- Set up Slack/email notifications for alerts (requires Alertmanager)
- Add more exporters (PostgreSQL, Node.js system metrics)

### Long Term
- Migrate to GCP Cloud Monitoring (when deploying to production)
- Set up distributed tracing with Jaeger
- Implement SLO monitoring

---

## GCP Migration Path

This local stack is designed for easy GCP migration:

| Local Component | GCP Equivalent |
|----------------|----------------|
| Prometheus | Cloud Monitoring |
| Grafana | Cloud Monitoring Dashboards |
| Alert Rules | Cloud Monitoring Alerts |
| Docker Compose | Cloud Run / GKE |

The metrics and alert definitions will transfer directly!

---

## Files Created Summary

| File | Purpose | Lines |
|------|---------|-------|
| `docker-compose.yml` | Orchestration | 92 |
| `prometheus/prometheus.yml` | Prometheus config | 73 |
| `prometheus/alerts/application.yml` | Alert rules | 203 |
| `grafana/provisioning/datasources/prometheus.yml` | Datasource config | 12 |
| `grafana/provisioning/dashboards/dashboards.yml` | Dashboard provisioning | 14 |
| `DOCKER_STACK_README.md` | Usage guide | 400+ |

**Total Lines Added**: ~800 lines

---

## Phase Summary

✅ **Phase 1**: Application Metrics (Prometheus client)
✅ **Phase 2**: Structured Logging (Winston)
✅ **Phase 3**: Health Checks & Readiness Probes
✅ **Phase 4**: Local Monitoring Stack ← JUST COMPLETED

**Total Monitoring Code**: ~3,300 lines (including documentation)

---

## Test Results

All tests passed successfully:

✅ Docker Compose started Prometheus and Grafana
✅ Prometheus scraping application metrics (target UP)
✅ Grafana connected to Prometheus datasource
✅ Metrics queryable via Prometheus API
✅ Alert rules loaded and evaluating
✅ Data persisting to volumes
✅ Health checks passing

---

*Phase 4 implementation completed successfully. Full monitoring stack operational with Prometheus and Grafana.*
