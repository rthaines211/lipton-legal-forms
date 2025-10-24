# Legal Form Application - Architecture Documentation

## Table of Contents
- [System Overview](#system-overview)
- [Architecture Diagrams](#architecture-diagrams)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Scalability & Performance](#scalability--performance)

## System Overview

The Legal Form Application is a full-stack web application that collects, processes, and stores legal form submissions with a comprehensive data transformation pipeline. The system features dual storage (JSON files + PostgreSQL), optional cloud backup, and automated data normalization.

### Key Features
- 🎯 Dynamic multi-party form (plaintiffs/defendants)
- 📊 19 comprehensive issue tracking categories
- 💾 Dual storage: JSON files + PostgreSQL database
- ☁️ Optional Dropbox cloud backup
- 🔄 Python normalization pipeline integration
- 📈 Prometheus metrics & monitoring
- 🔒 Token-based authentication (production)
- 🚀 Real-time Server-Sent Events (SSE) for progress tracking

## Architecture Diagrams

### System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        MobileApp[Mobile Browser]
    end

    subgraph "Frontend (Static)"
        HTML[index.html<br/>Form Interface]
        CSS[styles.css<br/>Styling]
        JS1[form-submission.js<br/>Form Logic]
        JS2[party-management.js<br/>Dynamic Parties]
        JS3[sse-client.js<br/>Real-time Updates]
        JS4[toast-notifications.js<br/>User Feedback]
        JS5[progress-state.js<br/>State Management]
    end

    subgraph "Backend (Node.js/Express)"
        Express[Express Server<br/>Port 3000]
        Auth[Authentication<br/>Middleware]
        Monitoring[Monitoring & Metrics<br/>Middleware]
        Logger[Winston Logger<br/>Structured Logging]
        Routes[API Routes]
    end

    subgraph "Storage Layer"
        FileSystem[JSON Files<br/>data/ directory]
        PostgreSQL[(PostgreSQL<br/>legal_forms_db)]
        Dropbox[Dropbox Cloud<br/>Optional Backup]
    end

    subgraph "Processing Layer"
        Pipeline[Python FastAPI<br/>Normalization Pipeline<br/>Port 8000]
        ETL[ETL Service<br/>5-Phase Processing]
    end

    subgraph "Monitoring"
        Prometheus[Prometheus Metrics<br/>/metrics endpoint]
        HealthChecks[Health Checks<br/>/health endpoints]
    end

    Browser --> HTML
    MobileApp --> HTML
    HTML --> JS1
    HTML --> JS2
    JS1 --> JS3
    JS1 --> JS4
    JS1 --> JS5

    JS1 --> Express
    JS2 --> Express
    JS3 --> Express

    Express --> Auth
    Auth --> Monitoring
    Monitoring --> Routes
    Routes --> Logger

    Routes --> FileSystem
    Routes --> PostgreSQL
    Routes --> Dropbox
    Routes --> Pipeline

    Pipeline --> ETL
    ETL --> PostgreSQL

    Express --> Prometheus
    Express --> HealthChecks
```

### Data Flow - Form Submission

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Express
    participant FileSystem
    participant PostgreSQL
    participant Dropbox
    participant Pipeline

    User->>Browser: Fill out form
    User->>Browser: Click Submit
    Browser->>Browser: Validate form data
    Browser->>Express: POST /api/form-entries

    Express->>Express: Authenticate (if production)
    Express->>Express: Transform data structure
    Express->>Express: Generate unique ID

    par Parallel Storage
        Express->>FileSystem: Save JSON file
        FileSystem-->>Express: File saved
    and
        Express->>PostgreSQL: Insert case record
        Express->>PostgreSQL: Insert plaintiffs
        Express->>PostgreSQL: Insert defendants
        Express->>PostgreSQL: Insert issue selections
        PostgreSQL-->>Express: Database records created
    and
        Express->>Dropbox: Upload to cloud (if enabled)
        Dropbox-->>Express: Upload confirmation
    end

    Express->>Pipeline: Trigger normalization (if enabled)
    Pipeline->>Pipeline: Execute 5-phase processing
    Pipeline->>PostgreSQL: Update normalized data
    Pipeline-->>Express: Processing status

    Express-->>Browser: Success response + ID
    Browser->>Browser: Show success page
    Browser-->>User: Display confirmation
```

### Component Interaction - Frontend

```mermaid
graph LR
    subgraph "Form Management"
        FormSub[form-submission.js<br/>Main Controller]
        PartyMgmt[party-management.js<br/>Add/Remove Parties]
        Progress[progress-state.js<br/>Form State]
    end

    subgraph "User Feedback"
        SSE[sse-client.js<br/>Real-time Events]
        Toast[toast-notifications.js<br/>Alerts & Messages]
    end

    subgraph "UI Layer"
        HTML[index.html<br/>Form Structure]
        CSS[styles.css<br/>Presentation]
    end

    HTML --> FormSub
    HTML --> PartyMgmt

    FormSub --> Progress
    FormSub --> SSE
    FormSub --> Toast

    PartyMgmt --> Progress
    PartyMgmt --> Toast

    SSE --> Toast

    CSS --> HTML
```

### Database Schema

```mermaid
erDiagram
    cases ||--o{ parties : contains
    parties ||--o{ party_issue_selections : has
    issue_categories ||--o{ issue_options : contains
    issue_options ||--o{ party_issue_selections : selected_in

    cases {
        uuid id PK
        timestamp created_at
        varchar property_address
        varchar city
        varchar state
        varchar zip_code
        varchar filing_location
        varchar filing_county
        varchar submitter_name
        varchar submitter_email
        jsonb raw_payload
        jsonb latest_payload
        varchar pipeline_status
        timestamp pipeline_last_run
        text pipeline_error
    }

    parties {
        uuid id PK
        uuid case_id FK
        varchar party_type
        int party_number
        varchar first_name
        varchar last_name
        varchar full_name
        varchar plaintiff_type
        varchar age_category
        boolean is_head_of_household
        varchar defendant_type
        varchar defendant_role
        varchar unit_number
    }

    party_issue_selections {
        uuid id PK
        uuid party_id FK
        uuid issue_option_id FK
        timestamp created_at
    }

    issue_categories {
        uuid id PK
        varchar category_code
        varchar category_name
        int category_order
        boolean is_multi_select
    }

    issue_options {
        uuid id PK
        uuid category_id FK
        varchar option_code
        varchar option_name
        int option_order
    }
```

## Component Details

### 1. Frontend Components

#### **index.html** - Main Form Interface
- Dynamic form with repeatable sections (plaintiffs/defendants)
- 19 comprehensive issue tracking categories
- Accordion-based UI for better organization
- Real-time validation and "At a Glance" summary
- Responsive design for mobile/desktop

#### **form-submission.js** - Form Controller
```javascript
/**
 * Core Responsibilities:
 * - Form validation and submission
 * - Data transformation to JSON format
 * - API communication
 * - Error handling
 * - Success/failure navigation
 */
```

#### **party-management.js** - Dynamic Party Management
```javascript
/**
 * Core Responsibilities:
 * - Add/remove plaintiff sections dynamically
 * - Add/remove defendant sections dynamically
 * - Unique ID generation for parties
 * - Party numbering and reindexing
 */
```

#### **sse-client.js** - Server-Sent Events
```javascript
/**
 * Core Responsibilities:
 * - Establish SSE connection to server
 * - Receive real-time pipeline updates
 * - Handle connection errors and reconnection
 * - Emit events to toast notifications
 */
```

#### **toast-notifications.js** - User Feedback
```javascript
/**
 * Core Responsibilities:
 * - Display success/error/info messages
 * - Auto-dismiss notifications
 * - Stacking multiple notifications
 * - Accessibility features
 */
```

#### **progress-state.js** - State Management
```javascript
/**
 * Core Responsibilities:
 * - Track form completion state
 * - Manage party counts
 * - Update "At a Glance" summary
 * - Persist state to sessionStorage
 */
```

### 2. Backend Components

#### **server.js** - Express Application
```javascript
/**
 * Main Server Features:
 * - Express web server (port 3000)
 * - CORS configuration
 * - Authentication middleware
 * - Request logging (Morgan + Winston)
 * - Compression middleware
 * - PostgreSQL connection pooling
 * - Dropbox integration
 * - Pipeline integration
 * - Health checks & metrics
 */
```

**Key Middleware Stack:**
1. CORS - Cross-origin resource sharing
2. Authentication - Token validation (production)
3. Compression - Gzip compression
4. Morgan - HTTP request logging
5. Metrics - Prometheus metrics collection
6. Body Parser - JSON request parsing

#### **monitoring/logger.js** - Structured Logging
```javascript
/**
 * Winston Logger Configuration:
 * - Daily rotating log files
 * - Console output with colors
 * - JSON format for structured logging
 * - Log levels: error, warn, info, debug
 * - Separate error log file
 */
```

#### **monitoring/metrics.js** - Prometheus Metrics
```javascript
/**
 * Tracked Metrics:
 * - HTTP request duration histogram
 * - HTTP request counter
 * - Database connection pool stats
 * - Active requests gauge
 * - Custom business metrics
 */
```

#### **monitoring/health-checks.js** - Health Monitoring
```javascript
/**
 * Health Check Types:
 * - Liveness: Is the app running?
 * - Readiness: Can it serve requests?
 * - Detailed: Full dependency status
 *
 * Checked Dependencies:
 * - PostgreSQL database
 * - File system (data/ directory)
 * - Dropbox API (if enabled)
 * - Pipeline API (if enabled)
 */
```

#### **dropbox-service.js** - Cloud Backup
```javascript
/**
 * Dropbox Integration:
 * - Upload JSON files to Dropbox
 * - Preserve folder structure
 * - Error handling and retry logic
 * - Optional/configurable via env vars
 */
```

### 3. Python Normalization Pipeline

#### **api/main.py** - FastAPI Application
```python
"""
FastAPI Server Features:
- Port 8000
- RESTful endpoints
- Form submission ingestion
- ETL processing coordination
- Health checks
- CORS configuration
"""
```

#### **api/etl_service.py** - ETL Processing
```python
"""
5-Phase Normalization Pipeline:
1. Case extraction & validation
2. Party normalization
3. Issue taxonomy mapping
4. Data quality checks
5. Database persistence

All operations wrapped in transactions for atomicity.
"""
```

#### **api/json_builder.py** - Output Generation
```python
"""
Responsibilities:
- Query normalized database data
- Reconstruct JSON in original format
- Apply formatting rules
- Generate compliant output
"""
```

### 4. Database Layer

#### **PostgreSQL Database: legal_forms_db**

**Tables:**
- `cases` - Form submission metadata
- `parties` - Plaintiffs and defendants
- `party_issue_selections` - Selected issues per party
- `issue_categories` - Master issue categories
- `issue_options` - Available issue options

**Key Indexes:**
```sql
-- Performance indexes
CREATE INDEX idx_cases_created_at ON cases(created_at DESC);
CREATE INDEX idx_parties_case_id ON parties(case_id);
CREATE INDEX idx_parties_type ON parties(party_type);
CREATE INDEX idx_issue_selections_party ON party_issue_selections(party_id);
CREATE INDEX idx_issue_options_category ON issue_options(category_id);
```

## Data Flow

### Form Submission Flow

1. **User Input** → Browser form validation
2. **Client-Side Processing**:
   - Collect form data
   - Structure JSON payload
   - Validate required fields
3. **HTTP POST** → Express server
4. **Authentication** → Token validation (production)
5. **Data Transformation**:
   - Generate unique IDs
   - Transform field names
   - Structure nested objects
6. **Parallel Storage**:
   - **JSON File**: Save to `data/form-entry-{timestamp}-{id}.json`
   - **PostgreSQL**: Insert into `cases`, `parties`, `party_issue_selections`
   - **Dropbox**: Upload to cloud (if enabled)
7. **Pipeline Trigger** (if enabled):
   - Call Python FastAPI endpoint
   - Execute 5-phase normalization
   - Update database with normalized data
8. **Response** → Success confirmation with entry ID
9. **Client Redirect** → Success page

### Data Retrieval Flow

1. **HTTP GET** → Express endpoint
2. **Authentication** → Token validation
3. **Query Database** → PostgreSQL query
4. **Data Enrichment**:
   - Join tables (cases, parties, issues)
   - Format timestamps
   - Calculate aggregates
5. **Response** → JSON payload
6. **Client Rendering** → Display in UI

## Technology Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with flexbox/grid
- **Vanilla JavaScript (ES6+)** - No framework dependencies
- **Notyf** - Toast notifications library

### Backend
- **Node.js v14+** - Runtime environment
- **Express 4.x** - Web framework
- **PostgreSQL 12+** - Relational database
- **Winston** - Structured logging
- **Morgan** - HTTP request logging
- **Prometheus Client** - Metrics collection
- **pg** - PostgreSQL driver
- **Dropbox SDK** - Cloud storage integration
- **Axios** - HTTP client for pipeline calls

### Python Pipeline
- **Python 3.8+** - Runtime
- **FastAPI** - Modern async web framework
- **Uvicorn** - ASGI server
- **Psycopg 3** - PostgreSQL driver
- **Pydantic** - Data validation

### Development Tools
- **Playwright** - End-to-end testing
- **Nodemon** - Development auto-reload
- **Terser** - JavaScript minification
- **html-minifier-terser** - HTML minification

### Infrastructure
- **Docker** - Containerization (optional)
- **Google Cloud Platform** - Deployment target
- **Prometheus** - Metrics aggregation
- **Grafana** - Metrics visualization (optional)

## Scalability & Performance

### Current Optimizations

#### 1. Database Connection Pooling
```javascript
// PostgreSQL pool configuration
{
  max: 20,                          // Max concurrent connections
  idleTimeoutMillis: 30000,         // Close idle connections
  connectionTimeoutMillis: 2000,    // Fast failure
  maxUses: 7500,                    // Connection rotation
  allowExitOnIdle: true             // Graceful shutdown
}
```

#### 2. Response Compression
- Gzip compression for all responses
- Reduces payload size by 60-80%
- Configured via Express compression middleware

#### 3. Database Indexes
- Optimized indexes on frequently queried columns
- Composite indexes for common query patterns
- See `db_performance_indexes.sql`

#### 4. Caching Strategies
- Static asset caching (HTML, CSS, JS)
- Database query result caching (future enhancement)
- CDN for static resources (production)

#### 5. Asynchronous Processing
- Non-blocking I/O for all operations
- Parallel storage writes (JSON + DB + Dropbox)
- Background pipeline processing
- SSE for real-time updates without polling

### Scaling Recommendations

#### Horizontal Scaling
```mermaid
graph TB
    LB[Load Balancer<br/>nginx/HAProxy]

    subgraph "Application Tier"
        App1[Express Server 1<br/>Port 3000]
        App2[Express Server 2<br/>Port 3001]
        App3[Express Server 3<br/>Port 3002]
    end

    subgraph "Data Tier"
        Primary[(PostgreSQL<br/>Primary)]
        Replica1[(PostgreSQL<br/>Replica 1)]
        Replica2[(PostgreSQL<br/>Replica 2)]
    end

    LB --> App1
    LB --> App2
    LB --> App3

    App1 --> Primary
    App2 --> Primary
    App3 --> Primary

    Primary --> Replica1
    Primary --> Replica2
```

**Implementation Steps:**
1. Deploy multiple Express instances
2. Add load balancer (nginx, ALB, GCP Load Balancer)
3. Configure PostgreSQL replication
4. Implement session affinity (if needed)
5. Add Redis for shared session storage

#### Vertical Scaling
- Increase PostgreSQL server resources (CPU, RAM, disk)
- Optimize database queries (EXPLAIN ANALYZE)
- Add read replicas for heavy read workloads
- Partition large tables by date range

#### Caching Layer
```mermaid
graph LR
    Client[Client Request]
    Cache[Redis Cache]
    App[Express Server]
    DB[(PostgreSQL)]

    Client --> Cache
    Cache -->|Cache Miss| App
    App --> DB
    DB --> App
    App --> Cache
    Cache --> Client
```

**Redis Integration:**
- Cache frequently accessed form entries
- Store session data
- Implement rate limiting
- Queue background jobs

### Performance Metrics

**Current Performance (Single Instance):**
- Form submission: ~200ms (without pipeline)
- Form submission: ~2-5s (with pipeline)
- List entries: ~50ms
- Get single entry: ~30ms
- Health check: ~10ms

**Performance Targets (with scaling):**
- 1000+ concurrent users
- <100ms API response times (p95)
- 99.9% uptime SLA
- <3s end-to-end form submission

### Monitoring & Observability

#### Metrics Collection
```javascript
// Prometheus metrics
- http_request_duration_seconds (histogram)
- http_requests_total (counter)
- database_connections_active (gauge)
- database_query_duration_seconds (histogram)
- pipeline_processing_duration_seconds (histogram)
```

#### Logging Strategy
```javascript
// Winston log levels
- ERROR: Critical failures requiring immediate attention
- WARN: Important issues that don't stop execution
- INFO: Business events (form submissions, etc.)
- DEBUG: Detailed diagnostic information
```

#### Health Checks
- **Liveness**: `/health` - Is the app alive?
- **Readiness**: `/health/ready` - Can it serve traffic?
- **Detailed**: `/health/detailed` - Full dependency status

### Security Considerations

1. **Authentication**: Token-based in production
2. **Input Validation**: Server-side validation of all inputs
3. **SQL Injection**: Parameterized queries only
4. **XSS Protection**: Content-Type headers, CSP
5. **CORS**: Configured allowed origins
6. **Rate Limiting**: TODO - implement rate limiting
7. **HTTPS**: Required in production
8. **Secrets Management**: Environment variables, never committed

## Deployment Architecture (GCP)

```mermaid
graph TB
    subgraph "Internet"
        Users[Users]
        CDN[Cloud CDN]
    end

    subgraph "Google Cloud Platform"
        LB[Cloud Load Balancer<br/>HTTPS]

        subgraph "Compute"
            GCE1[Compute Engine<br/>Express App 1]
            GCE2[Compute Engine<br/>Express App 2]
            CloudRun[Cloud Run<br/>Python Pipeline]
        end

        subgraph "Data"
            CloudSQL[(Cloud SQL<br/>PostgreSQL)]
            FileStore[Cloud Storage<br/>JSON Files]
        end

        subgraph "Monitoring"
            CloudMonitor[Cloud Monitoring]
            CloudLog[Cloud Logging]
        end
    end

    subgraph "External Services"
        DropboxCloud[Dropbox API]
    end

    Users --> CDN
    CDN --> LB
    LB --> GCE1
    LB --> GCE2

    GCE1 --> CloudSQL
    GCE2 --> CloudSQL
    GCE1 --> FileStore
    GCE2 --> FileStore
    GCE1 --> CloudRun
    GCE2 --> CloudRun
    GCE1 --> DropboxCloud
    GCE2 --> DropboxCloud

    CloudRun --> CloudSQL

    GCE1 --> CloudMonitor
    GCE2 --> CloudMonitor
    CloudRun --> CloudMonitor

    GCE1 --> CloudLog
    GCE2 --> CloudLog
    CloudRun --> CloudLog
```

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-21
**Maintained By:** Development Team
