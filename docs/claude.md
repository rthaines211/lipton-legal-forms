# Claude Project Memory - Legal Form Application

## Project Overview
This is a comprehensive legal form application for collecting plaintiff and defendant information with detailed issue tracking. The application transforms user input into structured JSON format suitable for legal document processing and integrates with a Python normalization pipeline for advanced document generation.

## Technical Stack
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Backend**: Node.js with Express.js
- **Database**: PostgreSQL (`legal_forms_db`)
- **External Services**: Python FastAPI normalization pipeline (5-phase processing)
- **Testing**: Playwright for automated end-to-end testing
- **Data Storage**: Dual storage system - JSON files AND PostgreSQL database
- **Planned Integration**: Dropbox API for cloud document storage

## Key Files and Structure

### Main Application Files
- **[index.html](index.html)** - Main form interface (very large file ~180KB, ~45k tokens)
- **[server.js](server.js)** - Express server handling API endpoints, data transformation, and pipeline integration
- **[review.html](review.html)** - Pre-submission review page for users to verify data before final submission
- **[success.html](success.html)** - Form submission success page
- **[script.js](script.js)** - Original form logic (currently unused)
- **[styles.css](styles.css)** - Form styling

### Documentation Files
- **[README.md](README.md)** - Comprehensive project documentation
- **[formdesign.md](formdesign.md)** - Form design specifications
- **[goalOutput.md](goalOutput.md)** - Target JSON output structure specification
- **[Transformationinstructions.md](Transformationinstructions.md)** - Data transformation guidelines
- **[styleguide.md](styleguide.md)** - UI/UX styling guidelines
- **[Dropbox Feature](Dropbox Feature)** - Planned feature specification for Dropbox integration

### Configuration & Assets
- **[package.json](package.json)** - Node.js dependencies and scripts
- **[playwright.config.js](playwright.config.js)** - Playwright test configuration
- **[logo.png](logo.png)** - Application logo

### Directories
- **[data/](data/)** - Form submission storage (JSON files)
- **[tests/](tests/)** - Playwright test files
- **[node_modules/](node_modules/)** - NPM dependencies
- **[playwright-report/](playwright-report/)** - Test execution reports
- **[test-results/](test-results/)** - Test artifacts

## Core Features

### 1. Dynamic Form Sections
- Add/remove multiple plaintiffs dynamically
- Add/remove multiple defendants dynamically
- Each plaintiff has comprehensive issue tracking

### 2. Data Collection Categories

#### Property Information
- Address, city, state, ZIP code
- Filing location details

#### Plaintiff Information
- Name (first, last)
- Type (Individual, Organization, etc.)
- Age category
- Head of household status
- **Comprehensive Discovery/Issue Tracking**:
  - Vermin issues (Rats/Mice, Bedbugs, etc.)
  - Insect issues (Roaches, Ants, etc.)
  - Environmental hazards (Mold, Lead Paint, etc.)
  - Housing conditions (Heat/AC, Plumbing, etc.)
  - Safety issues (Locks, Smoke Detectors, etc.)
  - Legal issues (Retaliation, Discrimination, etc.)

#### Defendant Information
- Name (first, last)
- Entity type (Individual, LLC, Corporation, etc.)
- Role (Manager/Owner)

### 3. Data Transformation
The application performs two-stage transformation of form data:
- **Stage 1**: Raw HTML form → normalized structured format with PascalCase keys
- **Stage 2**: Normalized format → human-readable format (e.g., "FireHazard" → "Fire Hazard")
- Generates unique IDs for each party
- Creates nested objects for discovery information
- Structures full address details
- Formats names (First, Last, FirstAndLast)
- Converts boolean checkboxes to proper data types
- Arrays for multi-select fields (vermin, insects, etc.)
- Array deduplication to prevent duplicate values
- Removed Has_ prefix flags for cleaner output

### 3b. Python Normalization Pipeline Integration
The server integrates with an external Python FastAPI service for advanced document processing:
- **API URL**: Configurable via `PIPELINE_API_URL` (default: http://localhost:8000)
- **Execution**: Runs automatically on form submission (configurable via `EXECUTE_PIPELINE_ON_SUBMIT`)
- **Timeout**: 300 seconds (5 minutes) for complex processing
- **Failure Handling**: Continues on failure (configurable via `CONTINUE_ON_PIPELINE_FAILURE`)
- **Purpose**: 5-phase normalization pipeline for legal document generation

### 4. REST API Endpoints
- `GET /` - Serve main form page
- `GET /review.html` - Review page for submission preview
- `GET /success` - Success confirmation page
- `POST /api/form-entries` - Submit form data (triggers pipeline if enabled)
- `GET /api/form-entries` - List all submissions
- `GET /api/form-entries/:id` - Get specific entry
- `PUT /api/form-entries/:id` - Update form entry
- `DELETE /api/form-entries/:id` - Delete entry
- `DELETE /api/form-entries/clear-all` - Delete all entries (file system + database)
- `GET /api/health` - Health check

### 5. Submitter Tracking & Notifications
- Optional email notification opt-in modal after form submission
- Captures submitter name and email for document processing notifications
- Skip option available (submits as 'Anonymous' with empty email)
- Stored in database `cases` table (`submitter_name`, `submitter_email` columns)

### 6. Testing Infrastructure
- Comprehensive Playwright test suite
- Tests cover form loading, submission, multi-party addition
- Validates output structure against goalOutput.md specification
- API endpoint testing

## Form Field Naming Conventions
- Property: `property-address`, `city`, `state`, `zip`, etc.
- Plaintiff: `plaintiff-{number}-{field}` (e.g., `plaintiff-1-first-name`)
- Defendant: `defendant-{number}-{field}` (e.g., `defendant-1-entity`)
- Issue checkboxes: `{category}-{item}-{plaintiff-number}` (e.g., `vermin-RatsMice-1`)

## NPM Scripts
- `npm start` - Start the Express server
- `npm run dev` - Start with nodemon (auto-reload)
- `npm run build` - Build optimized production files
- `npm run build:prod` - Production build with NODE_ENV=production
- `npm test` - Run Playwright tests
- `npm run test:headed` - Run tests with visible browser
- `npm run test:debug` - Debug tests interactively
- `npm run test:report` - View test results report

## Data Storage Pattern

### Dual Storage System
The application uses both file-based and database storage:

#### 1. JSON File Storage (`data/` directory)
- Form submissions saved as JSON files in `data/` directory
- Filename format: `form-entry-{timestamp}-{random}.json`
- Each submission gets unique ID based on timestamp
- Contains complete form data in structured JSON format

#### 2. PostgreSQL Database (`legal_forms_db`)
- **Database Name**: `legal_forms_db`
- **Schema**: Relational structure for querying and reporting

**Database Tables**:
- **`cases`**: Stores case-level information (property address, filing location, etc.)
  - Primary key: `id`
  - Contains: address, city, state, zip, filing location details

- **`parties`**: Stores plaintiff and defendant information
  - Primary key: `id`
  - Foreign key: `case_id` → references `cases(id)`
  - Fields: `full_name`, `party_type` (plaintiff/defendant), `party_number`, `role`, `entity_type`, `unit_number`, `is_head_of_household`, `age_category`

- **`party_issue_selections`**: Tracks issue/discovery selections for plaintiffs
  - Primary key: `id`
  - Foreign key: `party_id` → references `parties(id)`
  - Links plaintiffs to their selected issues (vermin, insects, environmental hazards, etc.)

**Database Usage**:
- Enables relational queries (e.g., "Find all plaintiffs with mold issues")
- Supports reporting and analytics
- Provides normalized data structure vs. nested JSON
- Facilitates multi-case comparison and aggregation

**Clearing Database**:
```sql
TRUNCATE TABLE party_issue_selections CASCADE;
TRUNCATE TABLE parties CASCADE;
TRUNCATE TABLE cases CASCADE;
```

## Development Notes
- Not a git repository (as of 2025-10-06)
- Running on macOS (Darwin 25.0.0)
- Server runs on port 3000 (configurable via PORT env variable)
- Uses CORS for cross-origin requests
- Morgan for HTTP request logging
- Compression middleware for optimized responses
- PostgreSQL connection pooling optimized: 20 max connections, 30s idle timeout, connection rotation at 7500 uses

## Implemented Features

### Dropbox Integration
**Status**: ✅ Implemented (2025-10-20)

The application automatically uploads form submissions to Dropbox for cloud backup and storage:

**Implementation Details**:
- **Module**: `dropbox-service.js` - Comprehensive Dropbox API wrapper
- **Integration Point**: `server.js:1378-1392` - Non-blocking upload after file save
- **Test Script**: `test-dropbox-upload.js` - Verification and diagnostics
- **Documentation**: `DROPBOX_SETUP.md` - Complete setup guide

**Features**:
- ✅ Uses official Dropbox SDK (`dropbox` npm package)
- ✅ Automatic folder creation in Dropbox
- ✅ Path mapping preserves local folder structure
- ✅ Non-blocking uploads (doesn't delay responses)
- ✅ Error resilient with configurable failure handling
- ✅ Comprehensive logging for local and Dropbox paths
- ✅ Cloud-ready with environment variable configuration
- ✅ File overwriting with version preservation in Dropbox

**Configuration**:
- `DROPBOX_ACCESS_TOKEN` - OAuth token for API authentication
- `DROPBOX_ENABLED` - Enable/disable uploads (default: false)
- `DROPBOX_BASE_PATH` - Base folder in Dropbox (default: `/Apps/LegalFormApp`)
- `LOCAL_OUTPUT_PATH` - Local output directory to mirror (default: `/output`)
- `CONTINUE_ON_DROPBOX_FAILURE` - Continue on failure (default: true)

**Example Path Mapping**:
- Local: `/output/Clients/SmithCase/SROGs/Set1.docx`
- Dropbox: `/Apps/LegalFormApp/Clients/SmithCase/SROGs/Set1.docx`

**Testing**:
```bash
node test-dropbox-upload.js
```

See [DROPBOX_SETUP.md](DROPBOX_SETUP.md) for complete setup instructions.

## Output Structure
The application generates JSON matching a specific legal document format with:
- Form metadata (Id, InternalName, Name)
- PlaintiffDetails array with comprehensive discovery objects
- DefendantDetails2 array
- Full_Address object with country, state, city, postal code details
- All plaintiff issues tracked as boolean flags and arrays

## Known Facts
- The main HTML file (index.html) is very large (~180KB)
- There's a backup of index.html from an earlier version
- The application has gone through iterations (index.html.backup exists)
- Script.js exists but is currently unused (functionality moved to inline scripts or server)

## Testing Coverage
- Form element visibility and interaction
- Dynamic plaintiff/defendant addition functionality
- Form validation and submission workflow
- Data transformation accuracy
- API response validation
- Output structure compliance with specifications

---

*This document serves as a knowledge base for Claude to maintain context about the Legal Form Application project. Last updated: 2025-10-20*
