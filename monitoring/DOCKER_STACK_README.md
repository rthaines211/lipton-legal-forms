# Local Monitoring Stack - Docker Compose

This directory contains a complete monitoring stack for the Legal Form Application using Docker Compose.

## What's Included

- **Prometheus** - Metrics collection and storage
- **Grafana** - Metrics visualization and dashboards

## Quick Start

### 1. Prerequisites

```bash
# Check Docker is installed and running
docker --version
docker ps

# Check Docker Compose is installed
docker-compose --version
```

### 2. Start the Monitoring Stack

```bash
# Navigate to monitoring directory
cd monitoring

# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Access the Services

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
  - Username: `admin`
  - Password: `admin` (you'll be prompted to change on first login)

### 4. Start Your Application

```bash
# In another terminal, from project root
npm start
```

Your application will be running on http://localhost:3000 and exposing metrics at http://localhost:3000/metrics

## Verify Everything is Working

### Check Prometheus is Scraping Metrics

1. Open http://localhost:9090
2. Go to **Status → Targets**
3. Verify `legal-form-app` target shows as **UP** (green)

### Check Grafana Connection

1. Open http://localhost:3001
2. Login with admin/admin
3. Go to **Configuration → Data Sources**
4. Verify Prometheus datasource shows a green checkmark

### Query Some Metrics

In Prometheus (http://localhost:9090):

```promql
# Total HTTP requests
http_requests_total

# Request rate per second
rate(http_requests_total[5m])

# P95 latency
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# Form submissions
form_submissions_total
```

## Managing the Stack

### View Service Status

```bash
docker-compose ps
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f prometheus
docker-compose logs -f grafana
```

### Stop the Stack

```bash
# Stop but keep data
docker-compose down

# Stop and remove all data
docker-compose down -v
```

### Restart a Service

```bash
docker-compose restart prometheus
docker-compose restart grafana
```

### Update Configuration

If you modify `prometheus.yml` or alert rules:

```bash
# Reload Prometheus configuration (no restart needed)
curl -X POST http://localhost:9090/-/reload

# Or restart the service
docker-compose restart prometheus
```

## Troubleshooting

### Prometheus Shows "legal-form-app" Target as DOWN

**Possible Causes**:
1. Application not running on port 3000
2. Network connectivity issue between Docker and host

**Solutions**:
```bash
# Check app is running
curl http://localhost:3000/metrics

# For Linux users: Update prometheus.yml
# Replace 'host.docker.internal:3000' with your machine's IP (e.g., '192.168.1.100:3000')

# Restart Prometheus
docker-compose restart prometheus
```

### Grafana Can't Connect to Prometheus

**Solution**:
```bash
# Check both services are running
docker-compose ps

# Restart Grafana
docker-compose restart grafana

# Check Grafana logs
docker-compose logs grafana
```

### Port Conflicts

If ports 9090 or 3001 are already in use:

```yaml
# Edit docker-compose.yml and change ports:
services:
  prometheus:
    ports:
      - "9091:9090"  # Use port 9091 instead
  grafana:
    ports:
      - "3002:3000"  # Use port 3002 instead
```

### Can't Access from Docker Container (Linux)

On Linux, `host.docker.internal` doesn't work by default.

**Solution**: Edit `prometheus/prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'legal-form-app'
    static_configs:
      - targets:
          # Replace with your machine's IP
          - '192.168.1.100:3000'  # Change this to your IP
```

Find your IP:
```bash
ip addr show | grep "inet " | grep -v 127.0.0.1
```

## Creating Dashboards in Grafana

### Option 1: Use the Grafana UI

1. Open Grafana (http://localhost:3001)
2. Click **Create → Dashboard**
3. Click **Add visualization**
4. Select **Prometheus** datasource
5. Enter a query (e.g., `rate(http_requests_total[5m])`)
6. Customize visualization
7. Click **Save dashboard**

### Option 2: Import Pre-built Dashboards

Grafana has a library of community dashboards:

1. Go to **Dashboards → Import**
2. Enter dashboard ID or upload JSON
3. Select Prometheus datasource
4. Click **Import**

**Recommended Dashboards**:
- **1860** - Node Exporter Full (if you add node-exporter)
- **3662** - Prometheus 2.0 Overview

### Useful Queries for Your Dashboards

```promql
# Request Rate (QPS)
sum(rate(http_requests_total[5m]))

# Error Rate Percentage
sum(rate(http_requests_total{status_code=~"5.."}[5m]))
/ sum(rate(http_requests_total[5m])) * 100

# P50, P95, P99 Latency
histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# Form Submissions Over Time
sum(increase(form_submissions_total[5m])) by (status)

# Database Connection Pool Usage
database_pool_connections_active
database_pool_connections_idle
database_pool_connections_waiting

# Memory Usage
nodejs_process_resident_memory_bytes / (1024 * 1024)
```

## Data Retention

### Prometheus

- **Default**: 30 days (configured in docker-compose.yml)
- **Location**: `./data/prometheus/`
- **Size**: Depends on metrics volume (~100MB-1GB for typical usage)

To change retention:
```yaml
# In docker-compose.yml
command:
  - '--storage.tsdb.retention.time=90d'  # Keep for 90 days
```

### Grafana

- **Dashboards**: Stored in `./data/grafana/`
- **Settings**: Persisted across restarts

## Backup and Restore

### Backup

```bash
# Stop services
docker-compose down

# Backup data directories
tar -czf monitoring-backup-$(date +%Y%m%d).tar.gz data/

# Restart services
docker-compose up -d
```

### Restore

```bash
# Stop services
docker-compose down

# Restore data
tar -xzf monitoring-backup-YYYYMMDD.tar.gz

# Restart services
docker-compose up -d
```

## Scaling and Performance

### Resource Limits

To limit resource usage:

```yaml
# In docker-compose.yml, add to each service:
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M
```

### Scrape Interval

Default is 15 seconds. For less frequent scraping:

```yaml
# In prometheus/prometheus.yml
global:
  scrape_interval: 30s  # or 60s
```

## Next Steps

1. **Create Custom Dashboards** in Grafana for your specific metrics
2. **Set Up Alerting** by configuring Alertmanager (separate service)
3. **Add More Exporters**:
   - PostgreSQL Exporter for database metrics
   - Node Exporter for system metrics
   - Blackbox Exporter for external endpoint monitoring

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)

---

*For questions or issues, check the main project README or monitoring documentation.*
