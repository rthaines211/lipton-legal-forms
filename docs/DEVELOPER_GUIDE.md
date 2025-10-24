# Developer Guide - Legal Form Application

## Table of Contents
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Style & Standards](#code-style--standards)
- [Testing](#testing)
- [Debugging](#debugging)
- [Building & Deployment](#building--deployment)
- [Contributing](#contributing)
- [Common Development Tasks](#common-development-tasks)

## Development Setup

### Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** v14+ ([Download](https://nodejs.org/))
- **npm** v6+ (comes with Node.js)
- **PostgreSQL** 12+ ([Download](https://www.postgresql.org/download/))
- **Python** 3.8+ (optional, for normalization pipeline)
- **Git** ([Download](https://git-scm.com/downloads))
- **Code Editor** (VS Code recommended)

### Initial Setup

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Lipton Webserver"
```

#### 2. Install Dependencies
```bash
npm install
```

#### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=legal_forms_db
DB_USER=your_username
DB_PASSWORD=your_password

# Server Configuration
PORT=3000
NODE_ENV=development

# Authentication (Production Only)
ACCESS_TOKEN=your-secret-token-here

# Dropbox Integration (Optional)
DROPBOX_ENABLED=false
DROPBOX_ACCESS_TOKEN=your_dropbox_token
DROPBOX_BASE_PATH=/Apps/LegalFormApp

# Python Pipeline Integration (Optional)
PIPELINE_API_URL=http://localhost:8000
PIPELINE_API_ENABLED=true
PIPELINE_API_KEY=your_pipeline_api_key
PIPELINE_API_TIMEOUT=300000
EXECUTE_PIPELINE_ON_SUBMIT=true
CONTINUE_ON_PIPELINE_FAILURE=true
```

#### 4. Set Up PostgreSQL Database

```bash
# Create database
createdb legal_forms_db

# Run schema migrations
psql legal_forms_db < database/schema.sql

# Seed taxonomy data (optional)
psql legal_forms_db < database/official_baseline_taxonomy.sql

# Add performance indexes
psql legal_forms_db < db_performance_indexes.sql
```

Verify database setup:
```bash
psql legal_forms_db -c "SELECT COUNT(*) FROM issue_categories;"
```

Should return 19 categories.

#### 5. Create Data Directory

```bash
mkdir -p data
chmod 755 data
```

#### 6. Start Development Server

```bash
npm run dev
```

Visit: http://localhost:3000

#### 7. Set Up Python Pipeline (Optional)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Start Python API (in separate terminal)
cd api
python main.py
```

Python API will run on: http://localhost:8000

### Verify Installation

1. **Check server:** http://localhost:3000 - Should show the form
2. **Check health:** http://localhost:3000/health - Should return `{"status":"healthy"}`
3. **Check database:** Submit a test form and verify data in PostgreSQL
4. **Check pipeline:** http://localhost:8000/health (if enabled)

---

## Project Structure

```
Lipton Webserver/
├── api/                          # Python normalization pipeline
│   ├── __init__.py
│   ├── config.py                 # Pipeline configuration
│   ├── database.py               # DB connection management
│   ├── etl_service.py            # ETL transformation logic
│   ├── json_builder.py           # JSON output generation
│   ├── main.py                   # FastAPI application
│   ├── models.py                 # Pydantic data models
│   └── README.md                 # Pipeline documentation
├── data/                         # JSON file storage
│   └── form-entry-*.json         # Submitted forms
├── database/                     # Database schemas & migrations
│   ├── schema.sql                # Main database schema
│   ├── official_baseline_taxonomy.sql  # Taxonomy seed data
│   └── *.sql                     # Other migrations
├── docs/                         # Documentation
│   ├── api/
│   │   └── openapi.yaml          # OpenAPI specification
│   ├── ARCHITECTURE.md           # System architecture
│   ├── API_REFERENCE.md          # API documentation
│   ├── USER_GUIDE.md             # End-user guide
│   └── DEVELOPER_GUIDE.md        # This file
├── js/                           # Frontend JavaScript modules
│   ├── form-submission.js        # Form submission logic
│   ├── party-management.js       # Add/remove parties
│   ├── progress-state.js         # State management
│   ├── sse-client.js             # Server-sent events
│   └── toast-notifications.js   # User notifications
├── logs/                         # Application logs (generated)
│   ├── application-*.log         # Rotating application logs
│   └── error-*.log               # Error logs
├── monitoring/                   # Monitoring & observability
│   ├── health-checks.js          # Health check logic
│   ├── log-middleware.js         # Logging middleware
│   ├── logger.js                 # Winston logger config
│   ├── metrics.js                # Prometheus metrics
│   └── middleware.js             # Metrics middleware
├── tests/                        # Playwright E2E tests
│   └── *.spec.js                 # Test specifications
├── .env                          # Environment variables (not committed)
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── build.js                      # Production build script
├── db_performance_indexes.sql    # Database performance indexes
├── dropbox-service.js            # Dropbox integration
├── index.html                    # Main form page
├── package.json                  # Node.js dependencies
├── playwright.config.js          # Playwright configuration
├── README.md                     # Project overview
├── requirements.txt              # Python dependencies
├── server.js                     # Express server (main)
├── styles.css                    # Form styling
└── success.html                  # Success confirmation page
```

### Key Files Explained

#### **server.js** (3100+ lines)
- Main Express application
- API route definitions
- Database connection pooling
- Authentication middleware
- Logging and monitoring
- Data transformation logic

#### **index.html**
- Main form interface
- Accordion-based UI
- Dynamic plaintiff/defendant sections
- 19 issue tracking categories

#### **js/form-submission.js**
- Form validation
- API communication
- Data collection and structuring
- Success/error handling

#### **js/party-management.js**
- Add/remove plaintiffs
- Add/remove defendants
- Unique ID generation
- Party numbering

#### **dropbox-service.js**
- Dropbox API integration
- File upload with folder structure
- Error handling and retry logic

#### **monitoring/***
- Winston logging configuration
- Prometheus metrics collection
- Health check implementations
- Request/error logging middleware

#### **api/*** (Python)
- FastAPI application
- ETL data processing
- Database normalization
- JSON output generation

---

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Edit files in your preferred editor. For VS Code:

```bash
code .
```

### 3. Test Locally

```bash
# Start development server with auto-reload
npm run dev

# In another terminal, run tests
npm test
```

### 4. Check for Errors

```bash
# Check server logs
tail -f logs/application-$(date +%Y-%m-%d).log

# Check error logs
tail -f logs/error-$(date +%Y-%m-%d).log
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub/GitLab.

---

## Code Style & Standards

### JavaScript Style Guide

#### Use Modern ES6+ Syntax
```javascript
// ✅ Good
const formData = { name, email };
const results = items.map(item => item.value);

// ❌ Avoid
var formData = { name: name, email: email };
var results = items.map(function(item) { return item.value; });
```

#### Use Async/Await
```javascript
// ✅ Good
async function saveFormEntry(data) {
  try {
    const result = await database.query('INSERT INTO ...');
    return result;
  } catch (error) {
    logger.error('Save failed:', error);
    throw error;
  }
}

// ❌ Avoid callback hell
function saveFormEntry(data, callback) {
  database.query('INSERT INTO ...', function(err, result) {
    if (err) return callback(err);
    callback(null, result);
  });
}
```

#### Use Descriptive Variable Names
```javascript
// ✅ Good
const plaintiffCount = plaintiffs.length;
const isHeadOfHousehold = plaintiff.HeadOfHousehold === true;

// ❌ Avoid
const pc = plaintiffs.length;
const hoh = plaintiff.HeadOfHousehold === true;
```

#### Error Handling
```javascript
// ✅ Good - Always handle errors
try {
  const data = await fetchData();
  return data;
} catch (error) {
  logger.error('Fetch failed:', { error: error.message, stack: error.stack });
  throw new Error('Failed to fetch data');
}

// ❌ Avoid swallowing errors
try {
  const data = await fetchData();
} catch (error) {
  // Silent failure
}
```

### Logging Standards

#### Use Appropriate Log Levels
```javascript
// ERROR - Critical failures
logger.error('Database connection failed', { error: err.message });

// WARN - Important but not critical
logger.warn('Dropbox upload failed, continuing anyway', { filename });

// INFO - Business events
logger.info('Form submission received', { entryId, plaintiffCount });

// DEBUG - Detailed diagnostic info
logger.debug('Processing plaintiff data', { plaintiff });
```

#### Include Context
```javascript
// ✅ Good - Structured logging with context
logger.info('Form submitted', {
  entryId: entry.id,
  plaintiffCount: plaintiffs.length,
  defendantCount: defendants.length,
  hasDropboxBackup: dropboxEnabled
});

// ❌ Avoid - Unstructured logging
logger.info('Form submitted with id ' + entry.id);
```

### Database Query Standards

#### Always Use Parameterized Queries
```javascript
// ✅ Good - Safe from SQL injection
const result = await pool.query(
  'SELECT * FROM cases WHERE id = $1',
  [caseId]
);

// ❌ NEVER - SQL injection vulnerability
const result = await pool.query(
  `SELECT * FROM cases WHERE id = '${caseId}'`
);
```

#### Use Transactions for Multi-Step Operations
```javascript
const client = await pool.connect();
try {
  await client.query('BEGIN');

  const caseResult = await client.query('INSERT INTO cases...');
  const partyResult = await client.query('INSERT INTO parties...');

  await client.query('COMMIT');
} catch (error) {
  await client.query('ROLLBACK');
  throw error;
} finally {
  client.release();
}
```

### API Response Standards

#### Consistent Response Format
```javascript
// Success response
res.status(200).json({
  success: true,
  message: 'Operation completed',
  data: { ... }
});

// Error response
res.status(400).json({
  error: 'Bad Request',
  message: 'Invalid form data',
  details: { field: 'property_address', reason: 'Required' }
});
```

---

## Testing

### Running Tests

```bash
# Run all tests
npm test

# Run in headed mode (see browser)
npm run test:headed

# Run specific test file
npx playwright test tests/simple-form-test.spec.js

# Debug tests
npm run test:debug

# View test report
npm run test:report
```

### Writing Tests

Tests are located in the `tests/` directory using Playwright.

#### Example Test Structure
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Form Submission', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('should submit form with single plaintiff', async ({ page }) => {
    // Fill property information
    await page.fill('#property-address', '123 Main St');
    await page.fill('#city', 'Los Angeles');

    // Fill plaintiff information
    await page.fill('#plaintiff-1-first-name', 'John');
    await page.fill('#plaintiff-1-last-name', 'Doe');

    // Submit form
    await page.click('#submit-button');

    // Verify success
    await expect(page).toHaveURL(/.*success/);
    await expect(page.locator('.entry-id')).toBeVisible();
  });
});
```

### Test Coverage Goals
- ✅ Form validation
- ✅ Dynamic party addition/removal
- ✅ Issue selection
- ✅ API endpoint responses
- ✅ Database operations
- ✅ Error handling

---

## Debugging

### Server-Side Debugging

#### View Logs in Real-Time
```bash
# Application logs
tail -f logs/application-$(date +%Y-%m-%d).log

# Error logs
tail -f logs/error-$(date +%Y-%m-%d).log
```

#### Debug with Node Inspector
```bash
node --inspect server.js
```

Then open Chrome DevTools: `chrome://inspect`

#### Add Debug Logging
```javascript
logger.debug('Processing form data', {
  plaintiffs: plaintiffs.length,
  defendants: defendants.length
});
```

### Client-Side Debugging

#### Browser Console
1. Open DevTools (F12)
2. Check Console tab for errors
3. Check Network tab for API calls
4. Check Application tab for localStorage/sessionStorage

#### Add Console Debugging
```javascript
console.log('Form data:', formData);
console.table(plaintiffs);
```

### Database Debugging

#### Query Database Directly
```bash
psql legal_forms_db

-- Check recent submissions
SELECT id, property_address, created_at
FROM cases
ORDER BY created_at DESC
LIMIT 10;

-- Check plaintiff issues
SELECT p.full_name, ic.category_name, COUNT(*) as issue_count
FROM parties p
JOIN party_issue_selections pis ON p.id = pis.party_id
JOIN issue_options io ON pis.issue_option_id = io.id
JOIN issue_categories ic ON io.category_id = ic.id
GROUP BY p.full_name, ic.category_name;
```

#### Enable Query Logging
Add to PostgreSQL `postgresql.conf`:
```
log_statement = 'all'
log_duration = on
```

### Common Issues & Solutions

#### Port Already in Use
```bash
# Find process using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>
```

#### Database Connection Failed
```bash
# Check PostgreSQL is running
pg_isready

# Verify connection string
psql "postgresql://user:password@localhost:5432/legal_forms_db"
```

#### Dropbox Upload Failed
```javascript
// Check logs for details
logger.error('Dropbox upload failed', {
  error: err.message,
  path: filePath
});

// Test Dropbox token
node -e "
const { Dropbox } = require('dropbox');
const dbx = new Dropbox({ accessToken: 'YOUR_TOKEN' });
dbx.usersGetCurrentAccount()
  .then(console.log)
  .catch(console.error);
"
```

---

## Building & Deployment

### Production Build

```bash
# Run production build
npm run build:prod

# This minifies:
# - JavaScript files (Terser)
# - HTML files (html-minifier-terser)
# - CSS files (clean-css)
```

Output files go to `dist/` directory.

### Environment Configuration

#### Development
```env
NODE_ENV=development
PORT=3000
ACCESS_TOKEN=  # Authentication disabled in dev
```

#### Production
```env
NODE_ENV=production
PORT=80
ACCESS_TOKEN=your-secure-token-here  # Authentication REQUIRED
```

### Deployment Checklist

- [ ] Set `NODE_ENV=production`
- [ ] Configure `ACCESS_TOKEN` securely
- [ ] Enable HTTPS
- [ ] Set up database backups
- [ ] Configure log rotation
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure CORS allowed origins
- [ ] Enable rate limiting (TODO)
- [ ] Test health check endpoints
- [ ] Configure Dropbox (if using)
- [ ] Set up Python pipeline (if using)

### Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM node:14-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["node", "server.js"]
```

Build and run:
```bash
docker build -t legal-form-app .
docker run -p 3000:3000 --env-file .env legal-form-app
```

### GCP Deployment

See `GCP_DEPLOYMENT_PLAN.md` for detailed GCP deployment instructions.

---

## Contributing

### Contribution Workflow

1. **Fork the repository** (if external contributor)
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature
   ```
3. **Make your changes**
4. **Write/update tests**
5. **Ensure tests pass**
   ```bash
   npm test
   ```
6. **Update documentation** (if needed)
7. **Commit with descriptive message**
   ```bash
   git commit -m "feat: add feature description"
   ```
8. **Push to your branch**
   ```bash
   git push origin feature/your-feature
   ```
9. **Create pull request**
10. **Respond to code review feedback**

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Build process or tooling changes

**Examples:**
```
feat(api): add pipeline retry endpoint

fix(form): prevent duplicate head of household

docs(readme): update installation instructions

refactor(server): extract data transformation to separate module
```

### Code Review Guidelines

**Reviewers should check:**
- ✅ Code follows style guidelines
- ✅ Tests are included and pass
- ✅ Documentation is updated
- ✅ No sensitive data in commits
- ✅ Error handling is appropriate
- ✅ Logging is sufficient
- ✅ Performance implications considered
- ✅ Security implications considered

---

## Common Development Tasks

### Adding a New Issue Category

1. **Add to database taxonomy**
   ```sql
   INSERT INTO issue_categories (id, category_code, category_name, category_order, is_multi_select)
   VALUES (gen_random_uuid(), 'new_category', 'New Category', 20, true);

   INSERT INTO issue_options (id, category_id, option_code, option_name, option_order)
   VALUES (gen_random_uuid(),
           (SELECT id FROM issue_categories WHERE category_code = 'new_category'),
           'option1', 'Option 1', 1);
   ```

2. **Update frontend HTML** (`index.html`)
   - Add new accordion section
   - Add checkboxes for options

3. **Update data transformation** (`server.js`)
   - Add to issue mapping logic
   - Add to `revertToOriginalFormat()` if needed

4. **Update Python models** (`api/models.py`)
   - Add to `PlaintiffDiscovery` schema

5. **Test thoroughly**

### Adding a New API Endpoint

1. **Define route in server.js**
   ```javascript
   app.get('/api/new-endpoint', requireAuth, async (req, res) => {
     try {
       // Implementation
       res.json({ success: true, data: result });
     } catch (error) {
       logger.error('Endpoint failed', { error });
       res.status(500).json({ error: 'Internal Server Error' });
     }
   });
   ```

2. **Update OpenAPI spec** (`docs/api/openapi.yaml`)

3. **Add tests** (`tests/`)

4. **Update API documentation** (`docs/API_REFERENCE.md`)

### Modifying Database Schema

1. **Create migration SQL file**
   ```sql
   -- database/migration_001_add_column.sql
   ALTER TABLE cases ADD COLUMN new_field VARCHAR(255);
   ```

2. **Apply migration**
   ```bash
   psql legal_forms_db < database/migration_001_add_column.sql
   ```

3. **Update server code** to use new field

4. **Update Python models** (if applicable)

5. **Test with existing data**

### Adding Frontend Validation

```javascript
// In js/form-submission.js
function validateForm() {
  const errors = [];

  // Add new validation
  const newField = document.getElementById('new-field').value;
  if (!newField) {
    errors.push('New field is required');
  }

  if (errors.length > 0) {
    showErrors(errors);
    return false;
  }

  return true;
}
```

### Adding Prometheus Metrics

```javascript
// In monitoring/metrics.js
const newCounter = new promClient.Counter({
  name: 'new_metric_total',
  help: 'Description of new metric',
  labelNames: ['label1', 'label2']
});

// Use in code
newCounter.labels('value1', 'value2').inc();
```

---

## Resources

### Documentation
- [Express.js](https://expressjs.com/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Winston Logger](https://github.com/winstonjs/winston)
- [Prometheus Client](https://github.com/simmonds/node-prometheus-client)
- [Playwright](https://playwright.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)

### Tools
- [VS Code](https://code.visualstudio.com/)
- [Postman](https://www.postman.com/) - API testing
- [DBeaver](https://dbeaver.io/) - Database GUI
- [Insomnia](https://insomnia.rest/) - API client

---

**Developer Guide Version:** 1.0.0
**Last Updated:** 2025-10-21
**Maintained By:** Development Team
