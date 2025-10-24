# GCP Deployment Guide - Lipton Webserver

## Overview

This guide covers deploying the Lipton Legal Discovery Document Generation Form application to Google Cloud Platform (GCP) with access token authentication enabled.

## Access Token Authentication

The application is configured with token-based authentication that:
- **Activates in production** when `NODE_ENV=production`
- **Remains disabled in development** (NODE_ENV=development)
- **Allows health checks** without authentication for GCP monitoring
- **Accepts tokens** via URL query string or Authorization header

### Access Token
```
a0ae8df2d793c8c4dcaebe22095479aa7241605f06b057a3e057919ab5b95ed4
```

### Usage Examples
- **URL**: `https://your-app.gcp.com/?token=a0ae8df2d793c8c4dcaebe22095479aa7241605f06b057a3e057919ab5b95ed4`
- **Header**: `Authorization: Bearer a0ae8df2d793c8c4dcaebe22095479aa7241605f06b057a3e057919ab5b95ed4`

---

## Deployment Options

### Option 1: Cloud Run (Recommended)

Cloud Run is ideal for containerized applications with automatic scaling.

#### Prerequisites
```bash
# Install Google Cloud SDK if not already installed
brew install google-cloud-sdk  # macOS
# or download from https://cloud.google.com/sdk/docs/install

# Login and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### Deploy Steps

1. **Create Dockerfile** (if not exists):
```dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application files
COPY . .

# Expose port
EXPOSE 3000

# Start server
CMD ["node", "server.js"]
```

2. **Deploy to Cloud Run**:
```bash
# Build and deploy in one command
gcloud run deploy lipton-webserver \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars NODE_ENV=production \
  --set-env-vars ACCESS_TOKEN=a0ae8df2d793c8c4dcaebe22095479aa7241605f06b057a3e057919ab5b95ed4 \
  --set-env-vars PIPELINE_API_URL=http://localhost:8000 \
  --set-env-vars PIPELINE_API_ENABLED=true \
  --set-env-vars DB_HOST=YOUR_DB_HOST \
  --set-env-vars DB_NAME=legal_forms_db \
  --set-env-vars DB_USER=YOUR_DB_USER \
  --set-env-vars DB_PASSWORD=YOUR_DB_PASSWORD \
  --set-env-vars DROPBOX_ENABLED=false \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300
```

3. **Access your application**:
```
https://lipton-webserver-XXXX-uc.a.run.app/?token=a0ae8df2d793c8c4dcaebe22095479aa7241605f06b057a3e057919ab5b95ed4
```

#### Update Environment Variables
```bash
gcloud run services update lipton-webserver \
  --region us-central1 \
  --set-env-vars ACCESS_TOKEN=NEW_TOKEN_HERE
```

---

### Option 2: App Engine

App Engine provides a fully managed platform with built-in scaling.

#### Deploy Steps

1. **Create `app.yaml`**:
```yaml
runtime: nodejs20
instance_class: F2

env_variables:
  NODE_ENV: "production"
  ACCESS_TOKEN: "a0ae8df2d793c8c4dcaebe22095479aa7241605f06b057a3e057919ab5b95ed4"
  PORT: "8080"
  PIPELINE_API_URL: "http://localhost:8000"
  PIPELINE_API_ENABLED: "true"
  DB_HOST: "YOUR_DB_HOST"
  DB_NAME: "legal_forms_db"
  DB_USER: "YOUR_DB_USER"
  DB_PASSWORD: "YOUR_DB_PASSWORD"
  DROPBOX_ENABLED: "false"

automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.65

handlers:
  - url: /.*
    script: auto
    secure: always
```

2. **Deploy**:
```bash
gcloud app deploy

# View logs
gcloud app logs tail -s default
```

3. **Access your application**:
```
https://YOUR_PROJECT_ID.appspot.com/?token=a0ae8df2d793c8c4dcaebe22095479aa7241605f06b057a3e057919ab5b95ed4
```

---

### Option 3: Compute Engine

Traditional VM-based deployment with full control.

#### Deploy Steps

1. **Create VM Instance**:
```bash
gcloud compute instances create lipton-webserver \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --boot-disk-size=20GB \
  --tags=http-server,https-server
```

2. **SSH into instance**:
```bash
gcloud compute ssh lipton-webserver --zone=us-central1-a
```

3. **Install Node.js and dependencies**:
```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PostgreSQL client (if needed)
sudo apt-get install -y postgresql-client

# Clone your repository or upload files
git clone YOUR_REPO_URL
cd Lipton\ Webserver

# Install dependencies
npm install

# Create .env file
cat > .env << 'EOF'
NODE_ENV=production
PORT=3000
ACCESS_TOKEN=a0ae8df2d793c8c4dcaebe22095479aa7241605f06b057a3e057919ab5b95ed4
# ... add other variables
EOF
```

4. **Setup PM2 for process management**:
```bash
sudo npm install -g pm2
pm2 start server.js --name lipton-webserver
pm2 startup
pm2 save
```

5. **Configure firewall**:
```bash
gcloud compute firewall-rules create allow-lipton-webserver \
  --allow tcp:3000 \
  --source-ranges 0.0.0.0/0 \
  --target-tags http-server
```

---

## Database Setup

### Cloud SQL (PostgreSQL)

1. **Create Cloud SQL instance**:
```bash
gcloud sql instances create lipton-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1
```

2. **Create database**:
```bash
gcloud sql databases create legal_forms_db \
  --instance=lipton-db
```

3. **Create user**:
```bash
gcloud sql users create lipton_user \
  --instance=lipton-db \
  --password=SECURE_PASSWORD_HERE
```

4. **Get connection name**:
```bash
gcloud sql instances describe lipton-db --format="value(connectionName)"
```

5. **Import schema**:
```bash
gcloud sql import sql lipton-db \
  gs://YOUR_BUCKET/database/schema.sql \
  --database=legal_forms_db
```

---

## Monitoring & Health Checks

### Health Check Endpoints

The application provides health check endpoints that **bypass authentication**:

- `/health` - Basic liveness check
- `/health/ready` - Readiness check (includes DB connectivity)
- `/health/detailed` - Detailed system status
- `/metrics` - Prometheus metrics

### Configure Cloud Run Health Checks

```bash
gcloud run services update lipton-webserver \
  --region us-central1 \
  --no-cpu-throttling \
  --max-instances 10 \
  --min-instances 1 \
  --health-check-path /health/ready \
  --health-check-interval 30s \
  --health-check-timeout 5s
```

### Cloud Monitoring

The application exports Prometheus metrics at `/metrics`. To integrate with Cloud Monitoring:

1. Follow the [Prometheus Integration Guide](../implementation/monitoring/MONITORING_COMPLETE.md)
2. Configure the monitoring stack in `monitoring/docker-compose.yml`

---

## Security Best Practices

### 1. Rotate Access Token Regularly

Generate a new token:
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

Update in GCP:
```bash
# Cloud Run
gcloud run services update lipton-webserver \
  --set-env-vars ACCESS_TOKEN=NEW_TOKEN

# App Engine - update app.yaml and redeploy
```

### 2. Use HTTPS Only

All GCP options provide HTTPS by default. Ensure `secure: always` in app.yaml.

### 3. Restrict by IP (Optional)

Add IP allowlist using Cloud Armor or VPC:
```bash
gcloud compute security-policies create lipton-policy \
  --description "IP allowlist for Lipton webserver"

gcloud compute security-policies rules create 1000 \
  --security-policy lipton-policy \
  --src-ip-ranges "YOUR_OFFICE_IP/32" \
  --action "allow"
```

### 4. Environment Variables Security

**Never commit** `.env` to version control. Use GCP Secret Manager for sensitive values:

```bash
# Store secret
echo -n "a0ae8df2d793c8c4dcaebe22095479aa7241605f06b057a3e057919ab5b95ed4" | \
  gcloud secrets create access-token --data-file=-

# Grant access to Cloud Run
gcloud secrets add-iam-policy-binding access-token \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"

# Reference in Cloud Run
gcloud run services update lipton-webserver \
  --update-secrets ACCESS_TOKEN=access-token:latest
```

---

## Troubleshooting

### 401 Unauthorized Errors

**Problem**: Getting 401 even with correct token.

**Solutions**:
1. Verify `NODE_ENV=production` is set
2. Check token matches exactly (no extra spaces)
3. URL encode token if it contains special characters
4. Check application logs:
   ```bash
   gcloud run logs read --service lipton-webserver --limit 50
   ```

### Health Checks Failing

**Problem**: GCP marks service as unhealthy.

**Solutions**:
1. Verify `/health` endpoint returns 200:
   ```bash
   curl -I https://your-app.gcp.com/health
   ```
2. Check database connectivity (readiness check)
3. Review health check configuration timeout/interval

### Application Not Starting

**Problem**: Service crashes on startup.

**Solutions**:
1. Check logs for errors:
   ```bash
   gcloud run logs read --service lipton-webserver --limit 100
   ```
2. Verify all required environment variables are set
3. Check database credentials
4. Ensure PostgreSQL database is accessible

---

## Cost Optimization

### Cloud Run
- Use `--min-instances 0` for development (cold starts)
- Use `--min-instances 1` for production (always ready)
- Set `--cpu-throttling` to reduce costs when idle
- Use `--concurrency 80` to maximize instance usage

### Database
- Start with `db-f1-micro` for testing
- Enable automatic storage increase
- Configure automated backups
- Use connection pooling (already configured in app)

---

## Support & Documentation

- **Application Docs**: See `/docs` directory
- **GCP Documentation**: https://cloud.google.com/docs
- **Cloud Run**: https://cloud.google.com/run/docs
- **App Engine**: https://cloud.google.com/appengine/docs

---

## Quick Reference

### Current Configuration
- **Access Token**: `a0ae8df2d793c8c4dcaebe22095479aa7241605f06b057a3e057919ab5b95ed4`
- **Auth Mode**: Production only (`NODE_ENV=production`)
- **Health Checks**: Bypass authentication
- **Token Methods**: URL query string OR Authorization header

### Common Commands
```bash
# View Cloud Run logs
gcloud run logs tail --service lipton-webserver

# Update environment variable
gcloud run services update lipton-webserver --set-env-vars KEY=VALUE

# Scale instances
gcloud run services update lipton-webserver --min-instances 1 --max-instances 10

# Get service URL
gcloud run services describe lipton-webserver --format 'value(status.url)'
```

