# Railway Deployment Plan: Legal Forms Application

## Document Overview

This comprehensive guide covers deploying a hybrid Node.js + Python application to Railway, a modern Platform-as-a-Service (PaaS) designed for developers. The application consists of:

- **Node.js Express Service** (Port 3000): Main web server handling form submissions
- **Python FastAPI Service** (Port 8000): Data normalization pipeline
- **PostgreSQL Database**: Shared data store for both services

**Last Updated:** October 24, 2025
**Application Version:** 1.0.0
**Target Environment:** Production on Railway

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Service Architecture](#service-architecture)
4. [Railway Configuration Files](#railway-configuration-files)
5. [Database Setup](#database-setup)
6. [Environment Variables](#environment-variables)
7. [Build and Start Commands](#build-and-start-commands)
8. [Deployment Steps](#deployment-steps)
9. [Networking and Domains](#networking-and-domains)
10. [Monitoring and Logging](#monitoring-and-logging)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)
13. [Post-Deployment Checklist](#post-deployment-checklist)

---

## Architecture Overview

### Application Structure

```
Legal Forms Application
├── Node.js Service (Primary)
│   ├── Express Server (Port 3000)
│   ├── PostgreSQL Client
│   ├── Dropbox Integration
│   └── Form Handling & API
├── Python Service (Data Pipeline)
│   ├── FastAPI Server (Port 8000)
│   ├── 5-Phase Normalization Pipeline
│   ├── Database Connection Pool
│   └── ETL Processing
└── PostgreSQL Database
    ├── Cases Table
    ├── Parties Table
    └── Party Issue Selections Table
```

### Service Communication Flow

```
User Browser (HTTPS)
    ↓
Railway Public URL
    ↓
Node.js Service (Port 3000) ← Public
    ↓
Python Service (Port 8000) ← Internal Only
    ↓
PostgreSQL Database ← Shared
```

### Deployment Architecture

```
Railway Project
├── Service 1: Node.js Backend
│   ├── Source: Root directory
│   ├── Build: npm install + npm run build:prod
│   ├── Start: npm start
│   └── Port: 3000 (exposed publicly)
├── Service 2: Python API
│   ├── Source: api/ directory
│   ├── Build: pip install -r requirements.txt
│   ├── Start: uvicorn main:app --host 0.0.0.0 --port 8000
│   └── Port: 8000 (internal only)
└── Database: PostgreSQL
    ├── Provisioned by Railway
    ├── Auto-configured connection string
    └── Shared by both services
```

---

## Prerequisites

### Before You Start

- **Railway Account**: Sign up at https://railway.app
- **GitHub Account**: Required for source code repository (Railway recommends Git-based deployments)
- **Local Git Repository**: Initialize git in your project
- **Railway CLI**: Install locally for advanced management
- **Database Backups**: Backup your current PostgreSQL database
- **Environment Variables**: Have all `.env` values documented

### Required Tools

```bash
# Install Railway CLI (macOS/Linux)
npm install -g @railway/cli

# Or using Homebrew (macOS)
brew install railway

# Verify installation
railway --version
```

### Account Preparation Checklist

- [ ] Create Railway account at https://railway.app
- [ ] Connect GitHub account to Railway
- [ ] Install Railway CLI locally
- [ ] Verify git is initialized in project: `git init`
- [ ] Create `.railwayignore` file (optional, similar to `.gitignore`)
- [ ] Document all environment variables needed
- [ ] Backup existing PostgreSQL database
- [ ] Prepare custom domain name (if applicable)

---

## Service Architecture

### Single Repository with Multiple Services

This project uses a **monorepo approach** with two services in the same repository:

#### Directory Structure

```
legal-forms-app/
├── package.json                 # Node.js dependencies
├── package-lock.json
├── server.js                    # Node.js Express server (entry point)
├── build.js                     # Build script (assets minification)
├── dropbox-service.js           # Dropbox integration module
├── requirements.txt             # Python dependencies
├── .env.example                 # Template for environment variables
├── .env                         # Actual environment (DO NOT commit)
├── .gitignore
├── .railwayignore              # Railway-specific ignore file
├── api/                         # Python FastAPI application
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Configuration and settings
│   ├── database.py             # Database connection management
│   ├── models.py               # Pydantic data models
│   ├── etl_service.py          # ETL processing logic
│   ├── json_builder.py         # JSON output generation
│   ├── tests/                  # Python tests
│   └── README.md
├── js/                          # Frontend JavaScript (minified in dist/)
├── css/                         # Stylesheets
├── html/                        # HTML templates
├── dist/                        # Production-optimized assets (generated by build.js)
├── node_modules/               # Node.js dependencies
├── logs/                        # Application logs (local development)
└── README.md
```

### Service Deployment Options

#### Option A: Monorepo (Recommended for This Project)

Deploy both services from a single repository with separate start commands:

**Advantages:**
- Easier coordination of code changes
- Shared configuration and environment variables
- Simplified database schema management
- Single repository to maintain

**Implementation:**
- Node.js service detects Python service URL from environment
- Both services use same PostgreSQL connection string
- Deployment: One Railway project with two services

#### Option B: Separate Repositories

Split into two repositories (advanced):

**Advantages:**
- Independent scaling and versioning
- Separate CI/CD pipelines
- Clearer service boundaries

**Disadvantages:**
- More complex to manage
- Duplicate configuration files
- Harder to coordinate breaking changes

**Recommendation:** Use Option A (monorepo) for initial deployment.

### Service Naming Convention

For clarity in Railway, use these service names:

- **Service 1 (Node.js):** `legal-forms-api` or `backend`
  - Identifier: `backend`, `nodejs`, or `express`

- **Service 2 (Python):** `legal-forms-pipeline` or `normalization-api`
  - Identifier: `pipeline`, `fastapi`, or `python`

- **Database:** `legal-forms-postgres` or `database`
  - Railway auto-assigns connection string variable

---

## Railway Configuration Files

### 1. Nixpacks Configuration (Optional but Recommended)

Create `nixpacks.toml` in the root directory for explicit build configuration:

```toml
# Nixpacks configuration for the Node.js and Python hybrid application
# This file helps Railway understand how to build and run your services

[build]
# Node.js will be detected automatically from package.json
# Python will be detected from requirements.txt

[env]
# Environment variables for the build process
NODE_ENV = "production"
PYTHONUNBUFFERED = "1"

[start]
# Start commands are defined in railway.json (per-service)
# This is for reference only
cmd = "npm start"  # This will be overridden per service
```

**Explanation:**
- Nixpacks is Railway's build system that automatically detects dependencies
- Specifying `NODE_ENV=production` optimizes Node.js builds
- `PYTHONUNBUFFERED=1` ensures Python logs appear immediately
- Each service gets its own start command in railway.json

### 2. Railway Configuration (railway.json)

Create `railway.json` in the root directory for service-specific configuration:

```json
{
  "$schema": "https://railway.app/schema.json",
  "build": {
    "builder": "nix"
  },
  "services": {
    "backend": {
      "sourceRepo": ".",
      "buildCommand": "npm install && npm run build:prod",
      "startCommand": "npm start",
      "variables": {
        "NODE_ENV": "production",
        "PORT": "3000"
      },
      "routing": {
        "publicPort": 3000
      }
    },
    "pipeline": {
      "sourceRepo": ".",
      "buildCommand": "pip install -r requirements.txt",
      "startCommand": "uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4",
      "variables": {
        "PYTHONUNBUFFERED": "1",
        "PORT": "8000"
      },
      "routing": {
        "publicPort": null
      }
    }
  },
  "plugins": []
}
```

**Service Configuration Breakdown:**

| Field | Node.js Service | Python Service | Purpose |
|-------|---|---|---|
| sourceRepo | "." | "." | Both use same repository |
| buildCommand | npm install + build | pip install | Production asset optimization |
| startCommand | npm start | uvicorn with 4 workers | Service startup |
| PORT variable | 3000 | 8000 | Express and FastAPI ports |
| publicPort | 3000 | null | Only Node.js exposed publicly |

### 3. Alternative: Procfile Configuration

If using Procfile instead of railway.json (Railway still supports it):

```
# Procfile
web: npm start
pipeline: uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Note:** Railway.json is preferred for better control. If using Procfile, you'll need to define services via web console.

### 4. .railwayignore File

Create `.railwayignore` to exclude files from deployment:

```
# Development and testing files
node_modules/
.pytest_cache/
.venv/
__pycache__/
*.pyc
.DS_Store

# Local files (not production)
.env
.env.local
.env.*.local

# Development dependencies
devDependencies (handled via package.json)
playwright-report/
test-results/

# Large data files (if applicable)
Processed Test/
backups/
logs/

# Git
.git/
.gitignore

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
Thumbs.db
.DS_Store

# Build artifacts that will be regenerated
dist/  # Will be rebuilt on each deploy
```

**Explanation:**
- Reduces deployment artifact size
- Prevents stale files from affecting production
- Keeps `.env` from accidentally being deployed
- Excludes test data and development tools

### 5. Build Optimization: .npmrc

Create `.npmrc` for optimized npm builds:

```
# Optimize Node.js build on Railway
production=true
legacy-peer-deps=true
fetch-timeout=120000
fetch-retry-mintimeout=10000
fetch-retry-maxtimeout=120000
prefer-offline=false
```

**Settings Explanation:**
- `production=true`: Skip dev dependencies during Railway build
- `legacy-peer-deps=true`: Handle peer dependency conflicts
- Increased timeout: Reliable builds on slower connections

---

## Database Setup

### PostgreSQL Provisioning on Railway

#### Step 1: Create PostgreSQL Service in Railway

1. **Via Web Console:**
   - Go to Railway Dashboard → New Project → Database → PostgreSQL
   - Railway auto-configures with secure credentials
   - Default: 1 GB storage, auto-backups enabled

2. **Via Railway CLI:**
   ```bash
   railway login
   railway init
   railway add --service postgresql
   ```

3. **Configuration:**
   - Railway creates a `DATABASE_URL` environment variable
   - Format: `postgresql://user:password@host:port/database`
   - Connection pooling: Built-in via psycopg-pool (Python)

#### Step 2: Connection String Configuration

Railway automatically provides these variables to your services:

```
# Auto-generated by Railway
DATABASE_URL=postgresql://postgres:randompass@localhost:5432/railway

# Node.js uses these specific variables
DB_USER=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=railway
DB_PASSWORD=randompass
```

**Important:** You can rename the database after creation, but update environment variables accordingly.

#### Step 3: Database Schema Initialization

Railway PostgreSQL instances start empty. You must initialize the schema.

**Option A: Manual SQL Execution (Recommended for Initial Setup)**

1. Get database credentials from Railway Dashboard
2. Connect from local machine:
   ```bash
   psql postgresql://postgres:password@host:5432/railway
   ```

3. Run schema creation SQL:
   ```sql
   -- Create cases table
   CREATE TABLE cases (
       id SERIAL PRIMARY KEY,
       case_name VARCHAR(255) NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   -- Create parties table
   CREATE TABLE parties (
       id SERIAL PRIMARY KEY,
       case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
       party_name VARCHAR(255) NOT NULL,
       party_type VARCHAR(50),
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   -- Create party issue selections table
   CREATE TABLE party_issue_selections (
       id SERIAL PRIMARY KEY,
       party_id INTEGER NOT NULL REFERENCES parties(id) ON DELETE CASCADE,
       issue VARCHAR(255) NOT NULL,
       selected BOOLEAN DEFAULT TRUE,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   -- Create indexes for performance
   CREATE INDEX idx_cases_created_at ON cases(created_at);
   CREATE INDEX idx_parties_case_id ON parties(case_id);
   CREATE INDEX idx_party_issues_party_id ON party_issue_selections(party_id);
   ```

4. Verify schema creation:
   ```sql
   \dt  -- List all tables
   \d cases  -- Describe cases table structure
   ```

**Option B: Automated Migration Script (Advanced)**

Create `scripts/init-database.js` for automatic schema setup:

```javascript
#!/usr/bin/env node
/**
 * Database initialization script
 * Runs on first deployment or manually
 * Use: node scripts/init-database.js
 */

const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

const pool = new Pool({
    connectionString: process.env.DATABASE_URL ||
        `postgresql://${process.env.DB_USER}:${process.env.DB_PASSWORD}@${process.env.DB_HOST}:${process.env.DB_PORT}/${process.env.DB_NAME}`
});

const initSql = `
    CREATE TABLE IF NOT EXISTS cases (
        id SERIAL PRIMARY KEY,
        case_name VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS parties (
        id SERIAL PRIMARY KEY,
        case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
        party_name VARCHAR(255) NOT NULL,
        party_type VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS party_issue_selections (
        id SERIAL PRIMARY KEY,
        party_id INTEGER NOT NULL REFERENCES parties(id) ON DELETE CASCADE,
        issue VARCHAR(255) NOT NULL,
        selected BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_cases_created_at ON cases(created_at);
    CREATE INDEX IF NOT EXISTS idx_parties_case_id ON parties(case_id);
    CREATE INDEX IF NOT EXISTS idx_party_issues_party_id ON party_issue_selections(party_id);
`;

async function initializeDatabase() {
    const client = await pool.connect();
    try {
        console.log('Initializing database schema...');
        await client.query(initSql);
        console.log('Database schema initialized successfully');
    } catch (err) {
        console.error('Error initializing database:', err);
        process.exit(1);
    } finally {
        await client.end();
        await pool.end();
    }
}

initializeDatabase();
```

Add to package.json:
```json
{
  "scripts": {
    "init:db": "node scripts/init-database.js"
  }
}
```

#### Step 4: Connect Both Services to Database

**Node.js Service (server.js):**
```javascript
const { Pool } = require('pg');

// Configuration from environment
const pool = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT,
    max: 20,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
});

// Or use DATABASE_URL directly
const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    max: 20
});

pool.on('error', (err) => {
    console.error('Unexpected error on idle client', err);
});
```

**Python Service (api/config.py):**
```python
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Use DATABASE_URL from Railway or construct from components
    database_url: str = os.getenv(
        "DATABASE_URL",
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

    # Connection pooling settings
    database_pool_min_size: int = 2
    database_pool_max_size: int = 10
```

#### Step 5: Database Backup Strategy

Railway provides automatic daily backups. For production:

1. **Enable Automated Backups:** Done by default on Railway
2. **Access Backups:** Via Railway Dashboard → Database → Backups
3. **Manual Backup Before Deployment:**
   ```bash
   # Export current database before deploying
   pg_dump postgresql://user:pass@host:port/dbname > backup_$(date +%Y%m%d).sql
   ```

4. **Restore from Backup:**
   ```bash
   # If needed after deployment
   psql postgresql://user:pass@host:port/dbname < backup_20251024.sql
   ```

#### Step 6: Production Database Optimization

Add to your PostgreSQL parameters for production workloads:

```sql
-- Connection optimization
-- (Applied via Railway dashboard if supported, or SQL commands)

-- Enable query monitoring
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1 second

-- Performance tuning
ALTER SYSTEM SET effective_cache_size = '256MB';
ALTER SYSTEM SET shared_buffers = '64MB';
ALTER SYSTEM SET work_mem = '16MB';

-- Select appropriate database size on Railway
-- Small: 1GB - Development/Testing
-- Standard: 10GB - Production
-- Enterprise: 100GB+ - High-volume production
```

---

## Environment Variables

### Complete Environment Variable Reference

#### Node.js Service Variables

```bash
# Server Configuration
PORT=3000
NODE_ENV=production

# Database Connection
DB_USER=postgres
DB_HOST=<railway-db-host>
DB_NAME=railway
DB_PASSWORD=<generated-by-railway>
DB_PORT=5432

# Or use combined connection string
DATABASE_URL=postgresql://postgres:password@host:5432/railway

# Python Service Integration
PIPELINE_API_URL=http://legal-forms-pipeline:8000
PIPELINE_API_ENABLED=true
PIPELINE_API_TIMEOUT=60000
PIPELINE_API_KEY=<optional-api-key>

# Pipeline Execution
EXECUTE_PIPELINE_ON_SUBMIT=true
CONTINUE_ON_PIPELINE_FAILURE=true

# Dropbox Integration (Optional)
DROPBOX_ENABLED=false
DROPBOX_ACCESS_TOKEN=<your-dropbox-token>
DROPBOX_BASE_PATH=/Apps/LegalFormApp
LOCAL_OUTPUT_PATH=/tmp/output
CONTINUE_ON_DROPBOX_FAILURE=true

# Logging (Optional)
LOG_LEVEL=info
LOG_FILE=/tmp/logs/app.log
LOG_MAX_SIZE=10m
LOG_MAX_FILES=5
```

#### Python Service Variables

```bash
# API Server
PORT=8000
PYTHONUNBUFFERED=1

# Database Connection (reuse from Node.js)
DATABASE_URL=postgresql://postgres:password@host:5432/railway

# Or use components
DB_USER=postgres
DB_HOST=<railway-db-host>
DB_NAME=railway
DB_PASSWORD=<generated-by-railway>
DB_PORT=5432

# Application Settings
APP_NAME=Legal Forms ETL API
APP_VERSION=1.0.0
API_RELOAD=false  # false for production, true for development
```

### Railway-Specific Environment Variables

Railway automatically injects these system variables:

```bash
# Available in both services automatically:

# Railway project information
RAILWAY_ENVIRONMENT_ID=<environment-id>
RAILWAY_ENVIRONMENT_NAME=production|staging
RAILWAY_PROJECT_ID=<project-id>
RAILWAY_PROJECT_NAME=legal-forms-app
RAILWAY_SERVICE_ID=<service-id>
RAILWAY_SERVICE_NAME=backend|pipeline
RAILWAY_DEPLOYMENT_ID=<deployment-id>

# Database service (if using Railway PostgreSQL)
DATABASE_URL=postgresql://postgres:password@db.railway.internal:5432/railway
PGUSER=postgres
PGPASSWORD=<password>
PGHOST=db.railway.internal
PGPORT=5432
PGDATABASE=railway

# These are useful for:
# - Logging which environment is running
# - Conditional configuration (dev vs prod)
# - Health check endpoints
# - Metrics and monitoring
```

### Environment Variable Configuration in Railway

#### Method 1: Web Console (Easiest)

1. Go to Railway Dashboard → Project → Service → Variables
2. Add variables manually or import from file
3. Use "Show All" to reveal sensitive values
4. Changes apply on next deployment

#### Method 2: Import from .env File

1. Prepare `.env.production` file:
   ```bash
   NODE_ENV=production
   DB_USER=postgres
   DB_HOST=...
   # All variables listed
   ```

2. In Railway Console:
   - Click "Add Variable" → "Import from File"
   - Paste contents of `.env.production`
   - Review and confirm

#### Method 3: Railway CLI

```bash
railway login
railway link  # Link to your project
railway variables set NODE_ENV=production
railway variables set DB_USER=postgres
railway variables set DB_HOST=your-host
# ... etc
```

#### Method 4: GitHub Secrets Integration

For GitHub-sourced deployments:

1. Add secrets to GitHub:
   - Go to Settings → Secrets and variables → Actions
   - Add each variable as a secret

2. Railway can read from GitHub:
   - In Railway settings, enable GitHub integration
   - Variables automatically synced from repo secrets

### Sensitive Variable Best Practices

**DO NOT:**
- Commit `.env` file to git
- Store tokens in version control
- Use test/development credentials in production
- Share environment variable values in code

**DO:**
- Use Railway's secure variable storage
- Rotate API keys quarterly
- Use different credentials per environment
- Document required variables in `.env.example`

**Example .env.example** (commit this):
```bash
# Database (use Railway's generated values)
DB_USER=postgres
DB_HOST=localhost
DB_NAME=legal_forms_db
DB_PASSWORD=change_me
DB_PORT=5432

# Python API Communication
PIPELINE_API_URL=http://localhost:8000
PIPELINE_API_ENABLED=true
PIPELINE_API_TIMEOUT=60000
PIPELINE_API_KEY=

# Dropbox (optional)
DROPBOX_ENABLED=false
DROPBOX_ACCESS_TOKEN=
DROPBOX_BASE_PATH=/Apps/LegalFormApp
```

### Service-to-Service Communication Setup

In Railway, services on the same project communicate using service names:

```javascript
// Node.js server.js
const PIPELINE_API_URL = process.env.PIPELINE_API_URL ||
    'http://legal-forms-pipeline:8000';

// Inside same Railway project, can use:
// http://legal-forms-pipeline:8000  (recommended)
// Not: http://localhost:8000

axios.post(`${PIPELINE_API_URL}/api/form-submissions`, formData)
    .catch(err => {
        logger.error('Pipeline API error:', err.message);
        if (!process.env.CONTINUE_ON_PIPELINE_FAILURE) {
            throw err;
        }
    });
```

**Important:**
- Services within Railway can communicate via service name (not localhost)
- Use service name as hostname (e.g., `legal-forms-pipeline`)
- Port is the internal port (8000 for Python, 3000 for Node.js)
- External (public) traffic uses generated Railway domain

---

## Build and Start Commands

### Node.js Service Build Process

**Build Command (runs once during deployment):**

```bash
npm install && npm run build:prod
```

**Breakdown:**
1. `npm install`: Installs dependencies from package-lock.json
   - Uses exact versions for reproducible builds
   - Takes ~30-60 seconds
   - Caches node_modules between deployments

2. `npm run build:prod`: Executes build.js with production environment
   - Minifies JavaScript files with Terser
   - Minifies CSS with clean-css
   - Minifies HTML with html-minifier-terser
   - Generates source maps for debugging
   - Creates `/dist` directory with optimized assets
   - Time: ~5-10 seconds
   - Output: 70-85% smaller assets (with gzip)

**Start Command (runs after build, persists for deployment):**

```bash
npm start
```

**What it does:**
- Executes `node server.js` (from package.json scripts)
- Starts Express server on PORT environment variable (default 3000)
- Loads .env configuration for database and API settings
- Initializes Dropbox service if DROPBOX_ENABLED=true
- Sets up Prometheus metrics endpoint at /metrics
- Starts Morgan request logging
- Handles graceful shutdown on SIGTERM

**Optional: Advanced Build with Health Checks**

```bash
# In railway.json, startCommand
npm start & while ! curl -f http://localhost:3000/health; do sleep 1; done
```

This ensures server is healthy before marking deployment successful.

### Python Service Build Process

**Build Command:**

```bash
pip install -r requirements.txt
```

**Breakdown:**
1. Installs Python dependencies from requirements.txt
   - Fixed versions for reproducibility
   - Binary wheels for psycopg (pre-compiled)
   - Takes ~30-90 seconds depending on dependencies
   - Caches pip packages between deployments

**Start Command:**

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4 --loop uvloop
```

**Parameters Explained:**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| api.main:app | Module path | Loads FastAPI app from api/main.py |
| --host 0.0.0.0 | Bind all interfaces | Makes service accessible on all network interfaces |
| --port 8000 | Port number | Match PYTHON PORT environment variable |
| --workers 4 | Worker count | Handle concurrent requests (adjust based on memory) |
| --loop uvloop | Event loop | Faster async I/O (optional, requires uvloop in requirements) |

**Alternative Start Commands:**

```bash
# Single worker (less resource usage, for testing)
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Auto-scaling workers (based on CPU)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers auto

# With reload for development (use only with api_reload=true in config)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Build Optimization for Faster Deployments

**Node.js Optimization:**

Update `.npmrc`:
```
production=true
prefer-offline=true
```

Update package.json build script:
```json
{
  "scripts": {
    "build:prod": "NODE_ENV=production node build.js",
    "build:fast": "node build.js --skip-html"  // Skip HTML minification if not needed
  }
}
```

**Python Optimization:**

Create `requirements-prod.txt` (without dev dependencies):
```
# requirements-prod.txt (production only)
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.10.0
pydantic-settings==2.6.0
psycopg[binary]==3.2.3
psycopg-pool==3.2.1
python-multipart==0.0.6
python-dotenv==1.0.0
uvloop==0.20.0  # Optional: faster event loop
```

Update railway.json:
```json
{
  "pipeline": {
    "buildCommand": "pip install -r requirements-prod.txt"
  }
}
```

### Dockerfile Alternative (Advanced)

For more control, create Dockerfile for each service:

**Dockerfile.node** (Node.js):
```dockerfile
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY . .

# Build assets
RUN npm run build:prod

# Start server
EXPOSE 3000
CMD ["npm", "start"]
```

**Dockerfile.python** (Python):
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Start server
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Then in railway.json:
```json
{
  "build": {
    "dockerfile": "Dockerfile.node"  // or Dockerfile.python per service
  }
}
```

---

## Deployment Steps

### Pre-Deployment Checklist

Before deploying to Railway, verify:

- [ ] Git repository initialized: `git init`
- [ ] All code committed: `git status` shows clean tree
- [ ] .env file added to .gitignore (not in repo)
- [ ] .railwayignore created (excludes node_modules, __pycache__, etc.)
- [ ] Railway account created and verified
- [ ] GitHub account connected to Railway
- [ ] All required dependencies in package.json and requirements.txt
- [ ] Build script tested locally: `npm run build:prod`
- [ ] Python service starts locally: `uvicorn api.main:app --reload`
- [ ] Database schema documented (SQL for PostgreSQL creation)
- [ ] All environment variables documented in .env.example
- [ ] Backup of current database (if migrating from existing database)
- [ ] .env.production created with actual values (keep locally, not in git)

### Step 1: Initialize Git Repository

```bash
cd "/Users/ryanhaines/Desktop/Lipton Webserver - Local"

# Initialize git if not already done
git init

# Configure git user (one time)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Stage all files
git add .

# Commit initial version
git commit -m "Initial commit: Legal forms application with Node.js + Python services"

# Verify repository status
git log --oneline -1  # Should show your commit
git status  # Should show clean working tree
```

### Step 2: Prepare Environment Files

```bash
# Create production environment file (NOT committed to git)
cat > .env.production << EOF
# Node.js Server
PORT=3000
NODE_ENV=production

# Database (will be provided by Railway)
DB_USER=postgres
DB_HOST=\${RAILWAY_DB_HOST}
DB_NAME=railway
DB_PASSWORD=\${RAILWAY_DB_PASSWORD}
DB_PORT=5432

# Python Service
PIPELINE_API_URL=http://legal-forms-pipeline:8000
PIPELINE_API_ENABLED=true
PIPELINE_API_TIMEOUT=60000

# Pipeline Execution
EXECUTE_PIPELINE_ON_SUBMIT=true
CONTINUE_ON_PIPELINE_FAILURE=true

# Dropbox (optional)
DROPBOX_ENABLED=false
DROPBOX_BASE_PATH=/Apps/LegalFormApp

EOF

# Make note of the credentials Railway will generate
echo "Secure this file and don't commit to git:"
cat .env.production
```

### Step 3: Create Railroad Configuration Files

**Create railway.json:**

```bash
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/schema.json",
  "build": {
    "builder": "nix"
  },
  "services": {
    "backend": {
      "sourceRepo": ".",
      "buildCommand": "npm install && npm run build:prod",
      "startCommand": "npm start",
      "variables": {
        "NODE_ENV": "production",
        "PORT": "3000"
      },
      "routing": {
        "publicPort": 3000,
        "protocol": "http"
      }
    },
    "pipeline": {
      "sourceRepo": ".",
      "buildCommand": "pip install -r requirements.txt",
      "startCommand": "uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4",
      "variables": {
        "PYTHONUNBUFFERED": "1",
        "PORT": "8000"
      },
      "routing": {
        "publicPort": null
      }
    }
  },
  "plugins": []
}
EOF

git add railway.json
git commit -m "Add Railway configuration for dual services"
```

**Create .railwayignore:**

```bash
cat > .railwayignore << 'EOF'
# Node.js
node_modules/
.npm
npm-debug.log

# Python
__pycache__/
*.pyc
.pytest_cache/
.venv/
venv/

# Development
.env
.env.local
.env.*.local
.vscode/
.idea/
*.swp
*.swo

# Data
Processed Test/
backups/
logs/

# Build artifacts (will be regenerated)
dist/

# OS
.DS_Store
Thumbs.db

# Git
.git/
EOF

git add .railwayignore
git commit -m "Add Railway-specific ignore rules"
```

**Create nixpacks.toml (optional but recommended):**

```bash
cat > nixpacks.toml << 'EOF'
[build]
# Node.js detected from package.json
# Python detected from requirements.txt

[env]
NODE_ENV = "production"
PYTHONUNBUFFERED = "1"
EOF

git add nixpacks.toml
git commit -m "Add Nixpacks build configuration"
```

### Step 4: Install Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Or with Homebrew (macOS)
brew install railway

# Verify installation
railway --version  # Should show version number

# Authenticate with Railway
railway login
# Opens browser for GitHub authentication, follow prompts
```

### Step 5: Create Railway Project

#### Option A: Via Web Console (Recommended for First Time)

1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "GitHub" and authorize connection
4. Choose "Deploy from GitHub repo"
5. Select your repository containing the code
6. Railway auto-detects Node.js and Python
7. Configure as needed
8. Deploy

#### Option B: Via Railway CLI

```bash
# Initialize Railway project
railway init

# Follow prompts:
# - Enter project name: legal-forms-app
# - Select environment: production
# - Region: Choose closest to users (e.g., us-west for US West Coast)

# Link to existing Railway project
railway link

# Verify link
railway service list  # Should show services
```

### Step 6: Add Services to Railway Project

#### Via Web Console:

1. **Backend Service (Node.js):**
   - Dashboard → Project → New Service → GitHub
   - Select repository and branch (main)
   - Service name: `backend`
   - Build command: `npm install && npm run build:prod`
   - Start command: `npm start`
   - Port: 3000

2. **Pipeline Service (Python):**
   - Dashboard → Project → New Service → GitHub
   - Same repository
   - Service name: `pipeline`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4`
   - Port: 8000
   - **Important:** Set "Expose Publicly" to OFF (internal only)

3. **Database:**
   - Dashboard → Project → New Service → Database → PostgreSQL
   - Railway auto-configures
   - Connection string automatically available

#### Via Railway CLI:

```bash
# Create services from railway.json
railway deploy

# Or add services manually
railway service create backend
railway service create pipeline
railway service create database --type postgres
```

### Step 7: Configure Environment Variables

```bash
# Using Railway CLI

# Backend service variables
railway env BACKEND
railway variables set NODE_ENV=production
railway variables set PORT=3000
railway variables set PIPELINE_API_URL=http://pipeline:8000
railway variables set PIPELINE_API_ENABLED=true
railway variables set EXECUTE_PIPELINE_ON_SUBMIT=true
railway variables set CONTINUE_ON_PIPELINE_FAILURE=true
railway variables set DROPBOX_ENABLED=false

# Switch to pipeline service
railway env PIPELINE
railway variables set PYTHONUNBUFFERED=1
railway variables set PORT=8000

# Verify variables
railway variables list
```

Or manually in Web Console:
1. Select service
2. Settings → Variables
3. Add each variable
4. "Deploy" to apply

### Step 8: Initialize PostgreSQL Database

```bash
# Get database connection details from Railway
railway env DATABASE  # Switch to database service
railway variables list  # Get DATABASE_URL

# From your local machine, connect to Railway PostgreSQL
psql "postgresql://postgres:PASSWORD@HOST:5432/railway"

# Run schema initialization SQL
psql "postgresql://postgres:PASSWORD@HOST:5432/railway" < schema.sql

# Or manually paste SQL commands from Section: Database Setup → Schema Creation
```

**Get Exact Connection String:**
```bash
railway variables list | grep DATABASE_URL
# Copy the full connection string
```

### Step 9: Deploy Application

```bash
# Option 1: Deploy via CLI
railway up

# Option 2: Deploy specific service
railway up --service backend
railway up --service pipeline

# Option 3: Via Web Console
# Push to main branch, Railway auto-deploys:
git push origin main
```

**Deployment Process:**
1. Railway fetches latest code from GitHub
2. Builds Node.js service: npm install + npm run build:prod
3. Builds Python service: pip install -r requirements.txt
4. Starts both services on assigned ports
5. Configures routing (Node.js public, Python internal)
6. Makes service available at Railway domain

**Monitor Deployment:**
```bash
# Watch deployment status
railway logs --service backend
railway logs --service pipeline

# Get deployment details
railway status
```

### Step 10: Verify Deployment

```bash
# Get public URL
railway open  # Opens deployed application in browser

# Or via CLI
railway domain  # Shows assigned Railway domain

# Test API endpoints
curl https://legal-forms-app-prod-xxxx.railway.app/
curl https://legal-forms-app-prod-xxxx.railway.app/health

# Check logs for errors
railway logs --service backend --follow
railway logs --service pipeline --follow
```

**Expected Responses:**

Node.js server responds on:
```
https://legal-forms-app-prod-xxxx.railway.app/
HTTPS only (Railway auto-redirects HTTP → HTTPS)
```

Python service only accessible internally (not via public URL).

### Step 11: Configure Custom Domain (Optional)

```bash
# In Railway Web Console:
# 1. Go to Project Settings → Domains
# 2. Click "Add Custom Domain"
# 3. Enter your domain (e.g., api.example.com)
# 4. Add provided CNAME record to DNS:
#    api.example.com CNAME legal-forms-app-prod-xxxx.railway.app
# 5. Verify DNS propagation (may take 10-30 minutes)
# 6. Railway auto-provisions HTTPS certificate (Let's Encrypt)

# Verify custom domain
curl https://api.example.com/
```

---

## Networking and Domains

### Public vs Internal Services

#### Public Service (Node.js Backend)

**Exposed to Internet:**
- Users access via https://your-domain.railway.app
- Auto-configured HTTPS/SSL with Railway certificate
- Load balancer automatically handles traffic

**Railway Configuration:**
```json
{
  "routing": {
    "publicPort": 3000,
    "protocol": "http"
  }
}
```

**Environment Variable for Clients:**
```javascript
// Clients use public Railway URL
const API_URL = 'https://legal-forms-app-prod-xxxx.railway.app';

// Or custom domain
const API_URL = 'https://api.example.com';
```

#### Internal Service (Python Pipeline)

**Not Exposed to Internet:**
- Only accessible from other services in same Railway project
- Uses internal service name as hostname
- No public URL generated
- Safer for internal-only APIs

**Railway Configuration:**
```json
{
  "routing": {
    "publicPort": null
  }
}
```

**Environment Variable for Service-to-Service Communication:**
```javascript
// Node.js server.js calls Python service
const PIPELINE_API_URL = process.env.PIPELINE_API_URL ||
    'http://legal-forms-pipeline:8000';

// Inside Railway, service name "legal-forms-pipeline" resolves to:
// http://legal-forms-pipeline:8000
// Port 8000 is internal port from Python service
```

### Railway Internal Networking

```
Service Discovery (DNS):
  [Service Name] → Internal IP Address

Example:
  legal-forms-pipeline → 10.0.x.x (Railway internal network)

Connection:
  Node.js → http://legal-forms-pipeline:8000 → Python FastAPI

Security:
  - Internal services not exposed to internet
  - Communication within Railway's network only
  - No port forwarding needed
```

### Custom Domain Setup

**Step 1: Prepare Domain**

Prerequisites:
- Domain registered and active
- DNS provider accessible (GoDaddy, Namecheap, etc.)
- You have permissions to modify DNS

**Step 2: Add Domain to Railway**

1. Go to Railway Dashboard → Project → Settings
2. Scroll to "Domains" section
3. Click "Add Domain"
4. Enter domain: `api.example.com` or `forms.example.com`
5. Select "Add" (don't deploy yet)

**Step 3: Configure DNS**

Railway provides CNAME record to add:

```
Name:   api
Type:   CNAME
Value:  legal-forms-app-prod-xxxx.railway.app
TTL:    3600 (1 hour)
```

Add to your DNS provider (example for GoDaddy):
1. Log in to DNS provider
2. Find "Add Record" or "DNS Records"
3. Add CNAME record with values above
4. Save changes

**Step 4: Verify DNS Propagation**

```bash
# Check DNS propagation (may take up to 30 minutes)
dig api.example.com

# Should show:
# api.example.com. 3600 IN CNAME legal-forms-app-prod-xxxx.railway.app

# Test HTTPS (Railway auto-provisions certificate)
curl https://api.example.com/
```

**Step 5: Automatic HTTPS/SSL**

Railway automatically:
- Provisions Let's Encrypt certificate
- Enables HTTPS/TLS 1.2+
- Auto-renews certificate (valid 90 days)
- Redirects HTTP → HTTPS

No manual certificate management needed!

### Network Architecture Diagram

```
Internet
    ↓
HTTPS Load Balancer (Railway)
    ↓
├─→ [Public Domain] api.example.com
│   ↓
│   [Node.js Service Port 3000]
│   ├─ Express Server
│   ├─ Form Handlers
│   ├─ API Endpoints
│   └─ Static Assets
│
└─→ [Internal Only] legal-forms-pipeline:8000
    (Not accessible from internet)
    ↓
    [Python Service Port 8000]
    ├─ FastAPI Application
    ├─ ETL Pipeline
    ├─ Data Processing
    └─ Normalization

    ↓ (Both services)

    [PostgreSQL Database]
    (Railway-managed, internal)
    ├─ Cases Table
    ├─ Parties Table
    └─ Issues Table
```

### Environment Variables for URLs

**Node.js Service:**
```javascript
// Set in environment or code
const PIPELINE_API_URL = process.env.PIPELINE_API_URL ||
    'http://legal-forms-pipeline:8000';

// Use for internal API calls
const response = await axios.post(
    `${PIPELINE_API_URL}/api/form-submissions`,
    formData
);
```

**Frontend/Client JavaScript:**
```javascript
// In browser, use public domain
const API_BASE_URL = process.env.REACT_APP_API_URL ||
    window.location.origin;  // Same origin as current page

fetch(`${API_BASE_URL}/api/submit-form`, {
    method: 'POST',
    body: JSON.stringify(formData)
});
```

---

## Monitoring and Logging

### Railway Built-in Monitoring

#### View Logs

**Web Console:**
1. Go to Project → Service
2. Click "Logs" tab
3. View real-time logs
4. Filter by log level: error, warning, info

**Railway CLI:**
```bash
# Real-time logs for all services
railway logs

# Logs for specific service
railway logs --service backend
railway logs --service pipeline

# Follow logs (like tail -f)
railway logs --follow

# Filter by service and level
railway logs --service backend --level error
```

**Log Access Examples:**

```bash
# Node.js service logs
railway logs --service backend --follow

# Expected output:
# 2025-10-24T12:34:56.789Z [server.js] Server running on port 3000
# 2025-10-24T12:34:57.123Z [morgan] GET /health 200 - 2ms
# 2025-10-24T12:35:00.456Z [database] Connected to PostgreSQL

# Python service logs
railway logs --service pipeline --follow

# Expected output:
# 2025-10-24T12:34:56.123 INFO: Uvicorn running on 0.0.0.0:8000
# 2025-10-24T12:35:01.234 INFO: Database pool initialized
# 2025-10-24T12:35:02.345 POST /api/form-submissions 200 OK
```

#### Metrics Dashboard

Railway provides resource monitoring:

1. **Web Console:**
   - Project → Service → Metrics
   - CPU Usage
   - Memory Usage
   - Network I/O
   - Deployment History

2. **Key Metrics to Monitor:**

| Metric | Node.js | Python | Database |
|--------|---------|--------|----------|
| CPU % | Ideally < 50% | Ideally < 30% | < 60% |
| Memory | Warn > 256MB | Warn > 200MB | < 256MB |
| Network | Monitor for spikes | Normal < 1MB/min | Depends on volume |
| Request Latency | < 500ms avg | < 200ms avg | < 100ms |

### Application-Level Monitoring

#### Node.js Health Check Endpoint

Server.js should expose health status:

```javascript
// In server.js
const express = require('express');
const { Pool } = require('pg');

const pool = new Pool({
    connectionString: process.env.DATABASE_URL
});

app.get('/health', async (req, res) => {
    try {
        // Check database connectivity
        const result = await pool.query('SELECT NOW()');

        // Check Python service (optional)
        let pipelineStatus = 'unknown';
        try {
            const response = await axios.get(
                `${process.env.PIPELINE_API_URL}/health`,
                { timeout: 5000 }
            );
            pipelineStatus = response.data.status || 'unknown';
        } catch (err) {
            pipelineStatus = 'unreachable';
        }

        res.status(200).json({
            status: 'healthy',
            timestamp: new Date().toISOString(),
            database: 'connected',
            pipeline: pipelineStatus,
            uptime: process.uptime(),
            environment: process.env.NODE_ENV
        });
    } catch (err) {
        res.status(503).json({
            status: 'unhealthy',
            error: err.message,
            database: 'disconnected'
        });
    }
});

// Metrics endpoint
app.get('/metrics', (req, res) => {
    // Prometheus metrics format
    res.type('text/plain');
    res.send(promClient.register.metrics());
});
```

#### Python Health Check Endpoint

FastAPI auto-generates OpenAPI docs at `/docs`:

```python
# In api/main.py
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        result = execute_query("SELECT 1 as status")
        db_status = "connected" if result else "disconnected"

        return HealthCheckResponse(
            status="healthy",
            database=db_status,
            timestamp=datetime.now().isoformat(),
            version=settings.app_version
        )
    except Exception as err:
        return HealthCheckResponse(
            status="unhealthy",
            database="disconnected",
            error=str(err)
        )
```

#### Test Health Endpoints

```bash
# Node.js health check
curl https://api.example.com/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-10-24T12:34:56.123Z",
  "database": "connected",
  "pipeline": "connected",
  "uptime": 3456.789,
  "environment": "production"
}

# Python health check (from Node.js only, not public)
curl http://legal-forms-pipeline:8000/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-10-24T12:34:56.123456",
  "version": "1.0.0"
}
```

### Logging Best Practices

#### Node.js Logging

Use Winston for structured logging (already in your package.json):

```javascript
const winston = require('winston');
const DailyRotateFile = require('winston-daily-rotate-file');

const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: winston.format.combine(
        winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
        winston.format.errors({ stack: true }),
        winston.format.json()
    ),
    transports: [
        // Console output (Railway captures stdout/stderr)
        new winston.transports.Console({
            format: winston.format.simple()
        }),

        // Daily rotating file (if filesystem available)
        new DailyRotateFile({
            filename: '/tmp/logs/app-%DATE%.log',
            datePattern: 'YYYY-MM-DD',
            maxSize: '20m',
            maxFiles: '10d'
        })
    ]
});

// Usage
logger.info('Application started', {
    environment: process.env.NODE_ENV,
    port: process.env.PORT
});

logger.error('Database error', {
    error: err.message,
    stack: err.stack,
    query: sql
});
```

#### Python Logging

Use Python logging module (already configured in api/main.py):

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Usage
logger.info("Application started", extra={
    "environment": settings.environment,
    "port": settings.api_port
})

logger.error("Database error", extra={
    "error": str(err),
    "query": query_string
})
```

#### Accessing Logs

```bash
# Real-time streaming
railway logs --follow

# Filter by time (last 1 hour)
railway logs --tail 3600

# Export logs for analysis
railway logs > app-logs-$(date +%Y%m%d).txt

# Search logs for errors
railway logs | grep ERROR

# Monitor specific service
watch -n 1 'railway logs --service backend --tail 50'
```

### Setting up Log Aggregation

For production logging, consider integrating external services:

**Option 1: Datadog**
```javascript
const StatsD = require('node-dogstatsd').StatsD;
const dogstatsd = new StatsD();

app.use((req, res, next) => {
    dogstatsd.increment('http.requests');
    dogstatsd.histogram('http.request_size', req.headers['content-length']);
    next();
});
```

**Option 2: Papertrail**
```bash
# Add to requirements.txt
python-syslog==1.2.2

# In Python app
import syslog
logger = logging.getLogger()
syslog_handler = logging.handlers.SysLogHandler(...)
logger.addHandler(syslog_handler)
```

**Option 3: Google Cloud Logging**
```javascript
const {Logging} = require('@google-cloud/logging');
const logging = new Logging();
const projectLog = logging.log('legal-forms-app');
const metadata = { resource: { type: 'global' } };
projectLog.write(projectLog.entry(metadata, logMessage));
```

---

## Best Practices

### Production Deployment Checklist

Before deploying to production:

- [ ] **Code Quality**
  - [ ] Code reviewed and approved
  - [ ] All tests passing locally: `npm test`, `pytest`
  - [ ] No console.log/print debugging statements
  - [ ] Error handling implemented for all async operations
  - [ ] Security vulnerabilities checked: `npm audit`

- [ ] **Configuration**
  - [ ] All environment variables configured in Railway
  - [ ] Sensitive values NOT in code or .env file
  - [ ] Database credentials secure (use Railway auto-generated)
  - [ ] CORS properly configured (restrict origins if needed)
  - [ ] API keys rotated and scoped appropriately

- [ ] **Database**
  - [ ] Schema created in production database
  - [ ] Backups enabled (Railway default)
  - [ ] Connection pooling configured (min 2, max 10)
  - [ ] Indexes created on frequently queried columns
  - [ ] Database size adequate for projected load

- [ ] **Monitoring**
  - [ ] Health check endpoints implemented and tested
  - [ ] Logging configured (Winston, Python logging)
  - [ ] Metrics endpoint available (/metrics for Prometheus)
  - [ ] Error tracking set up (Sentry, Datadog, etc.)
  - [ ] Alert thresholds defined (CPU, memory, errors)

- [ ] **Security**
  - [ ] HTTPS enforced (Railway default)
  - [ ] CORS headers configured restrictively
  - [ ] SQL injection prevention (parameterized queries)
  - [ ] Input validation on all endpoints
  - [ ] Rate limiting considered for public endpoints
  - [ ] Sensitive data encrypted in database if needed

- [ ] **Performance**
  - [ ] Assets minified (build.js for Node.js)
  - [ ] Database queries optimized (use EXPLAIN ANALYZE)
  - [ ] Connection pooling enabled
  - [ ] Caching headers set appropriately
  - [ ] Load testing performed locally

- [ ] **Documentation**
  - [ ] Deployment steps documented
  - [ ] Environment variables documented
  - [ ] Troubleshooting guide created
  - [ ] Architecture diagram available
  - [ ] Runbook for common issues

### Security Best Practices

#### Application Security

**Node.js:**
```javascript
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

// Security headers
app.use(helmet());

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000,  // 15 minutes
    max: 100,  // limit each IP to 100 requests per windowMs
    message: 'Too many requests from this IP'
});

app.use('/api/', limiter);

// Input validation
const { body, validationResult } = require('express-validator');

app.post('/api/submit-form', [
    body('caseId').isInt().toInt(),
    body('partyName').trim().isLength({ min: 1, max: 255 }),
], (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
    }
    // Process form...
});
```

**Python:**
```python
from fastapi.security import HTTPBearer, HTTPAuthCredential
from pydantic import validator

security = HTTPBearer()

@app.post("/api/form-submissions")
async def submit_form(
    form: FormSubmission,
    credentials: HTTPAuthCredential = Depends(security)
):
    # Validate API key
    if credentials.credentials != os.getenv('PIPELINE_API_KEY'):
        raise HTTPException(status_code=403, detail="Invalid API key")

    # Pydantic auto-validates input models
    return await etl_service.process(form)
```

#### Database Security

```javascript
// Always use parameterized queries
const result = await pool.query(
    'SELECT * FROM cases WHERE id = $1',
    [caseId]  // Parameter, not string interpolation
);

// Never do this:
// const result = await pool.query(`SELECT * FROM cases WHERE id = ${caseId}`);
```

#### Environment Variable Security

```bash
# Store sensitive values ONLY in Railway environment, not in code

# Good: Reference environment variables
const apiKey = process.env.PIPELINE_API_KEY;
const dbPassword = process.env.DB_PASSWORD;

# Bad: Hardcoded values
const apiKey = 'sk-12345...';
const dbPassword = 'MyPassword123';

# Never log sensitive values
logger.info('API call made');  // OK
logger.info(`Using API key: ${apiKey}`);  // BAD!
```

### Performance Optimization

#### Node.js Optimization

```javascript
// Enable gzip compression
const compression = require('compression');
app.use(compression());

// Set proper cache headers
app.use(express.static('dist', {
    maxAge: 31536000000,  // 1 year for production assets
    etag: false
}));

// Use connection pooling (already configured in Pool)
const pool = new Pool({
    max: 20,  // Maximum connections
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
});

// Monitor pool status
setInterval(() => {
    console.log('Pool status:', {
        total: pool.totalCount,
        idle: pool.idleCount,
        waiting: pool.waitingCount
    });
}, 60000);  // Every minute
```

#### Python Optimization

```python
# Use connection pooling (auto-configured in psycopg-pool)
pool = ConnectionPool(
    conninfo=settings.database_url,
    min_size=2,  # Minimum connections
    max_size=10,  # Maximum connections
)

# Enable async processing for concurrent requests
# (FastAPI with uvicorn workers already handles this)

# Cache database queries if appropriate
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

@app.get("/api/cases")
@cached(namespace="cases", expire=3600)  # Cache for 1 hour
async def get_cases():
    return await etl_service.get_all_cases()
```

#### Database Performance

```sql
-- Create indexes on frequently queried columns
CREATE INDEX idx_cases_created_at ON cases(created_at);
CREATE INDEX idx_parties_case_id ON parties(case_id);
CREATE INDEX idx_party_issues_party_id ON party_issue_selections(party_id);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM cases WHERE created_at > NOW() - INTERVAL '30 days';

-- Monitor slow queries
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1 second
```

### Cost Optimization

#### Railway Pricing

Railway charges per service per hour:

- **Compute:** $0.50 per GB-hour (e.g., 1GB = $0.50/hour = ~$360/month)
- **Storage:** PostgreSQL $0.50 per GB-month
- **Bandwidth:** Egress $0.10 per GB (intra-region free)
- **Network:** Free within Railway project

**Cost Reduction Strategies:**

1. **Right-size Resources:**
   - Node.js: 256-512MB (typical form app)
   - Python: 256-512MB (lightweight pipeline)
   - Database: 1-5GB for development (scale as needed)

2. **Disable Unused Services:**
   - Remove old/test services
   - Delete staging environment if not needed
   - Archive unneeded databases

3. **Monitor Usage:**
   ```bash
   railway usage  # View current costs
   railway resource list  # See all services and their resource allocation
   ```

4. **Optimize Code:**
   - Minified assets reduce bandwidth (already done with build.js)
   - Efficient database queries reduce CPU
   - Connection pooling reduces memory

5. **Consolidate Resources:**
   - Use single PostgreSQL for dev/staging (with different schemas)
   - Share services where possible
   - Use Railway's free tier for testing

### Scaling Considerations

#### Vertical Scaling (Bigger Machines)

Railway lets you allocate more resources per service:

1. Go to Service → Settings → Size
2. Increase GB allocated (0.5GB → 1GB → 2GB, etc.)
3. Service restarts automatically
4. Cost increases proportionally

**When to vertical scale:**
- Memory usage consistently > 80%
- Database grows beyond available storage
- Single-threaded bottleneck in processing

#### Horizontal Scaling (More Instances)

Railway supports multiple instances per service:

```bash
# Via CLI
railway service update --replicas 3

# Via Web Console
Service Settings → Replicas → Set to 3
```

**Load Balancing:**
- Railway automatically load-balances traffic
- Each instance independently connects to database
- Increases availability and capacity

**When to horizontal scale:**
- High concurrent user load
- CPU maxing out on single instance
- Need zero-downtime deployments

**Example Configuration:**

```json
{
  "services": {
    "backend": {
      "replicas": 2,  // 2 instances for redundancy
      "variables": {
        "NODE_ENV": "production"
      }
    },
    "pipeline": {
      "replicas": 1  // Single instance fine for async pipeline
    }
  }
}
```

#### Database Scaling

**Read Replicas (Advanced):**
- Create read-only copy of PostgreSQL
- Direct reporting queries to replica
- Reduces load on primary database

**Connection Pooling:**
- Already configured with max 10 connections
- Prevents connection exhaustion
- Monitor idle connections

**Query Optimization:**
```sql
-- Identify slow queries
SELECT * FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Add indexes
CREATE INDEX idx_party_case ON parties(case_id);
```

### Disaster Recovery

#### Backup and Restore

**Railway Automatic Backups:**
- Daily backups (kept for 7 days)
- Access via Dashboard → Database → Backups
- One-click restore available

**Manual Backup:**
```bash
# Backup locally
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql

# Restore from backup
psql $DATABASE_URL < backup-20251024.sql
```

#### Disaster Recovery Plan

**If primary database fails:**

1. **Restore from recent backup:**
   ```bash
   # Via Railway console
   Dashboard → Database → Backups → Select date → Restore
   ```

2. **Verify restored data:**
   ```bash
   railway env DATABASE
   psql $DATABASE_URL
   SELECT COUNT(*) FROM cases;
   ```

3. **Roll back application if needed:**
   ```bash
   # Redeploy to previous commit
   git revert HEAD
   git push origin main
   railway logs --follow  # Watch deployment
   ```

**If service is completely down:**

1. **Check service status:**
   ```bash
   railway status
   ```

2. **Restart service:**
   ```bash
   railway service restart --service backend
   ```

3. **Redeploy if needed:**
   ```bash
   railway up --service backend
   ```

---

## Troubleshooting

### Common Deployment Issues

#### Issue 1: Build Fails - "npm install" Error

**Symptoms:**
- Deployment fails during build
- Error: "Cannot find module X"
- Error: "Peer dependency conflicts"

**Solutions:**

1. **Check package.json syntax:**
   ```bash
   npm install  # Run locally
   npm test  # Verify dependencies work
   ```

2. **Update package-lock.json:**
   ```bash
   rm package-lock.json
   npm install  # Regenerate lock file
   git add package-lock.json
   git commit -m "Update package-lock.json"
   git push origin main
   ```

3. **Ignore peer dependency warnings:**
   ```
   # Create .npmrc
   legacy-peer-deps=true
   ```

4. **Check Node.js version:**
   - Railway uses Node.js 20+ (default)
   - Verify package.json engines field:
   ```json
   {
     "engines": {
       "node": ">=18.0.0"
     }
   }
   ```

#### Issue 2: Build Fails - "pip install" Error

**Symptoms:**
- Python build fails
- Error: "Could not build wheels for X"
- Error: "No matching distribution"

**Solutions:**

1. **Check requirements.txt syntax:**
   ```bash
   pip install -r requirements.txt  # Test locally
   ```

2. **Verify Python version:**
   - Railway uses Python 3.12+ (default)
   - Update requirements if needed

3. **Add system dependencies:**
   ```bash
   # If binary compilation needed, Railway provides:
   # gcc, libpq-dev (for psycopg), etc.
   ```

4. **Simplify requirements:**
   ```
   # Remove if not essential
   # Check if uvloop is needed (optional performance)
   uvloop==0.20.0  # Remove if failing
   ```

5. **Test requirements locally:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

#### Issue 3: Services Can't Communicate

**Symptoms:**
- Node.js can't reach Python service
- Error: "ECONNREFUSED" or "connection timeout"
- Health check returns "pipeline: unreachable"

**Solutions:**

1. **Verify service names in Railway:**
   ```bash
   railway service list
   # Confirm service name matches PIPELINE_API_URL
   ```

2. **Check environment variables:**
   ```bash
   # Should be set correctly
   PIPELINE_API_URL=http://legal-forms-pipeline:8000

   # NOT: http://localhost:8000 (localhost doesn't work in Railway)
   # NOT: http://127.0.0.1:8000 (same issue)
   ```

3. **Verify port configuration:**
   - Python service must listen on 0.0.0.0:8000
   - Check startCommand: `uvicorn api.main:app --host 0.0.0.0 --port 8000`

4. **Check if Python service is running:**
   ```bash
   railway logs --service pipeline
   # Should show: "Uvicorn running on 0.0.0.0:8000"
   ```

5. **Test connectivity:**
   ```bash
   # From Node.js service, try to access Python
   # (Requires temporary test endpoint)
   ```

#### Issue 4: Database Connection Failed

**Symptoms:**
- Error: "ECONNREFUSED" database
- Error: "password authentication failed"
- Error: "database does not exist"

**Solutions:**

1. **Verify database service exists:**
   ```bash
   railway service list  # Should show database service
   railway env DATABASE
   railway variables list  # Check DATABASE_URL
   ```

2. **Check DATABASE_URL format:**
   ```bash
   # Should be provided by Railway
   # Format: postgresql://user:password@host:port/database

   # Test connection locally (if Railway provides access)
   psql "postgresql://postgres:password@host:5432/railway"
   ```

3. **Verify environment variables:**
   ```bash
   # In Railway console, check:
   DB_USER=postgres
   DB_HOST=<railway-provided>
   DB_PORT=5432
   DB_NAME=railway
   DB_PASSWORD=<railway-provided>
   ```

4. **Check schema exists:**
   ```bash
   psql $DATABASE_URL
   \dt  # List tables

   # If empty, initialize schema (see Database Setup section)
   ```

5. **Wait for database to be ready:**
   - Sometimes it takes 30-60 seconds after creation
   - Retry deployment

#### Issue 5: Service Crashes Immediately

**Symptoms:**
- Service stops after starting
- Health check returns 503
- Logs show immediate exit

**Solutions:**

1. **Check application logs:**
   ```bash
   railway logs --service backend --tail 100
   railway logs --service pipeline --tail 100
   ```

2. **Common Node.js issues:**
   - Missing environment variables
   - Port already in use
   - Module not found
   ```bash
   # Ensure NODE_ENV=production
   # Ensure PORT is set or defaulted to 3000
   # Ensure all require() modules exist
   ```

3. **Common Python issues:**
   - Import error in main.py
   - Database unreachable at startup
   - Invalid configuration
   ```bash
   # Test locally: python -m api.main
   # Check PYTHONUNBUFFERED=1 set
   # Verify requirements.txt installed
   ```

4. **Restart service:**
   ```bash
   railway service restart --service backend
   ```

### Debugging Strategies

#### View Complete Logs

```bash
# Get last 1000 lines of logs
railway logs --tail 1000 --service backend

# Export to file for analysis
railway logs --tail 10000 > logs.txt

# Real-time monitoring
watch -n 1 'railway logs --tail 20 --service backend'
```

#### Check Service Metrics

```bash
# View memory and CPU usage
railway status

# For more detail
railway resource list
```

#### Test Endpoints from Command Line

```bash
# Test Node.js service
curl https://api.example.com/
curl https://api.example.com/health
curl -X POST https://api.example.com/api/submit-form -d '{"data": "test"}'

# Test Python service (must be done from within Railway or with tunnel)
# Setup tunnel (see next section)
curl http://localhost:8000/health
```

#### Create Debug Tunnel

```bash
# SSH tunnel to Railway database
railway tunnel

# This creates local tunnel to services
# Then you can access from localhost:port
```

#### Common Log Messages to Look For

**Node.js Server:**
```
✓ Server running on port 3000
✓ Connected to PostgreSQL
✓ Dropbox service initialized
✗ ECONNREFUSED (database issue)
✗ Cannot find module X (missing dependency)
```

**Python Service:**
```
✓ Uvicorn running on 0.0.0.0:8000
✓ Database pool initialized
✓ POST /api/form-submissions 200 OK
✗ ModuleNotFoundError (missing dependency)
✗ Connection refused (database unreachable)
```

### Rollback Procedures

#### Quick Rollback to Previous Version

If deployment introduces bugs:

```bash
# Option 1: Revert code to previous commit
git log --oneline -5  # See recent commits
git revert <commit-hash>
git push origin main
# Railway auto-deploys new version

# Option 2: Manual rollback to specific commit
git reset --hard <commit-hash>
git push origin main --force
# WARNING: Force push rewrites history

# Option 3: Via Railway (without code changes)
# Deploy specific commit:
railway up --source <git-commit-hash>
```

#### Database Rollback

```bash
# If schema change broke application:

# Option 1: Restore from backup
railway env DATABASE
# Via console: Select backup date and restore

# Option 2: Roll back migrations manually
psql $DATABASE_URL
-- Reverse any schema changes
-- DROP TABLE if created, etc.
```

#### Verify Rollback Success

```bash
# Check service health
curl https://api.example.com/health
# Should show: "status": "healthy"

# Check logs for errors
railway logs --follow

# Verify database connection
psql $DATABASE_URL
SELECT COUNT(*) FROM cases;
```

### Health Checks and Monitoring

#### Regular Health Check Script

```bash
#!/bin/bash
# health-check.sh - Run periodically to verify deployment

API_URL="https://api.example.com"

echo "Checking Node.js service..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/health)

if [ $HTTP_CODE -eq 200 ]; then
    echo "✓ Node.js service healthy"
else
    echo "✗ Node.js service unhealthy (HTTP $HTTP_CODE)"
    exit 1
fi

echo "Checking database..."
RESPONSE=$(curl -s $API_URL/health)
DB_STATUS=$(echo $RESPONSE | grep -o '"database":"[^"]*' | cut -d'"' -f4)

if [ "$DB_STATUS" = "connected" ]; then
    echo "✓ Database connected"
else
    echo "✗ Database disconnected"
    exit 1
fi

echo ""
echo "All checks passed! Deployment is healthy."
```

Use in cron to run periodically:

```bash
# Add to crontab
0 * * * * /path/to/health-check.sh  # Every hour
```

---

## Post-Deployment Checklist

### Immediate Post-Deployment (First 5 minutes)

- [ ] **Verify services are running:**
  ```bash
  railway status
  # All services should show "Running" status
  ```

- [ ] **Check health endpoints:**
  ```bash
  curl https://api.example.com/health
  # Should return status: "healthy"
  ```

- [ ] **Review logs for errors:**
  ```bash
  railway logs --service backend
  railway logs --service pipeline
  # Look for ERROR or WARNING messages
  ```

- [ ] **Verify database connectivity:**
  ```bash
  curl https://api.example.com/health | jq .database
  # Should return: "connected"
  ```

- [ ] **Check public domain resolution:**
  ```bash
  dig api.example.com
  nslookup api.example.com
  ```

### Short-term Post-Deployment (First hour)

- [ ] **Monitor resource usage:**
  ```bash
  watch -n 5 'railway status'
  # Watch for CPU/memory spikes
  ```

- [ ] **Test core functionality:**
  - Submit test form via web interface
  - Verify data saved to database
  - Check Python service processed correctly
  - Verify logs show successful processing

- [ ] **Review metrics:**
  - Go to Railway Dashboard → Project → Metrics
  - Check CPU usage (should be < 50%)
  - Check memory usage (should be < 80% allocated)
  - Check response times

- [ ] **Test error handling:**
  - Submit invalid form data
  - Verify appropriate error messages returned
  - Check error logged correctly

### Medium-term Post-Deployment (First 24 hours)

- [ ] **Monitor stability:**
  ```bash
  # Run health checks periodically
  watch -n 300 'railway logs --service backend --tail 20'
  ```

- [ ] **Check database growth:**
  ```bash
  psql $DATABASE_URL
  SELECT
      tablename,
      pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
  FROM pg_tables
  WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
  ```

- [ ] **Verify backup completion:**
  - Railway → Project → Database → Backups
  - Confirm daily backup completed

- [ ] **Test scaling (if needed):**
  - Simulate load: `ab -n 1000 -c 10 https://api.example.com/`
  - Monitor CPU/memory response
  - Adjust worker count if needed

- [ ] **Validate monitoring setup:**
  - Confirm health checks running
  - Set up alerts (if using external service)
  - Test alert notifications

### Long-term Post-Deployment (Ongoing)

- [ ] **Weekly Reviews:**
  - Review error logs
  - Check cost vs. resource allocation
  - Monitor database size growth
  - Performance metrics trends

- [ ] **Monthly Maintenance:**
  - Update dependencies: `npm update`, `pip install --upgrade -r requirements.txt`
  - Run security audit: `npm audit`
  - Review and rotate API keys
  - Verify backups restorable

- [ ] **Quarterly Tasks:**
  - Performance optimization review
  - Database maintenance (VACUUM, ANALYZE)
  - Security audit
  - Cost optimization review
  - Update documentation

### Performance Baseline Establishment

After deployment, establish performance baselines:

```bash
# Create baseline metrics file
cat > performance-baseline.txt << EOF
Date: $(date)
Node.js Memory: $(railway logs --tail 1 | grep -o 'memory: [0-9]*MB')
Node.js CPU: $(railway status | grep CPU)
Database Connections: $(psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;")
Average Response Time: (measure via curl multiple times)
EOF
```

Monitor against baseline monthly:

```bash
# Compare current metrics to baseline
current_memory=$(railway logs --tail 1 | grep -o 'memory: [0-9]*MB')
baseline_memory="256MB"

if [ current_memory > baseline_memory ]; then
    echo "WARNING: Memory usage increased from $baseline_memory to $current_memory"
fi
```

---

## Conclusion and Next Steps

### Deployment Summary

Your application is now deployed on Railway with:

1. **Node.js Service:** Public facing form handling and API
2. **Python Service:** Internal data normalization pipeline
3. **PostgreSQL Database:** Shared persistent data layer
4. **HTTPS/SSL:** Automatic certificate management
5. **Monitoring:** Built-in logs, metrics, and health checks
6. **Backups:** Automatic daily database backups
7. **Scaling:** Ready to scale vertically or horizontally as needed

### Recommended Next Steps

1. **Set up external monitoring** (Sentry, Datadog, New Relic)
2. **Configure alerting** for errors and performance issues
3. **Implement automated testing** in CI/CD
4. **Set up log aggregation** for long-term analysis
5. **Create runbooks** for common operational tasks
6. **Document API specifications** (Swagger/OpenAPI)
7. **Plan for database scaling** as data grows
8. **Establish SLA targets** and monitor against them

### Support Resources

- **Railway Documentation:** https://docs.railway.app
- **Node.js Best Practices:** https://nodejs.org/en/docs/guides/nodejs-docker-webapp/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **Community Support:** https://discord.gg/railway

### Additional Configuration Files Reference

**Key files created during deployment:**

1. `/Users/ryanhaines/Desktop/Lipton Webserver - Local/railway.json`
   - Service definitions and build/start commands

2. `/Users/ryanhaines/Desktop/Lipton Webserver - Local/.railwayignore`
   - Files excluded from deployment

3. `/Users/ryanhaines/Desktop/Lipton Webserver - Local/nixpacks.toml`
   - Build system configuration

4. `/Users/ryanhaines/Desktop/Lipton Webserver - Local/.env.production`
   - Production environment variables (keep locally, don't commit)

5. `/Users/ryanhaines/Desktop/Lipton Webserver - Local/.npmrc`
   - NPM configuration for production builds

### Final Notes

- Railway provides an excellent developer experience for modern applications
- Auto-scaling and managed infrastructure reduce operational overhead
- Cost-effective for small to medium deployments
- Easy to extend with other Railway services (Redis, MongoDB, etc.)
- Excellent for rapid iteration and deployment workflows

For questions or issues during deployment, refer to the Troubleshooting section or consult Railway's official documentation.

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Oct 24, 2025 | Initial comprehensive deployment plan |

---

**Created:** October 24, 2025
**For:** Legal Forms Application (Node.js + Python + PostgreSQL)
**Platform:** Railway
**Last Updated:** October 24, 2025
