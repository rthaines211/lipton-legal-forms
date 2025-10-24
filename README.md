# Legal Form Application

This application provides a comprehensive legal form for collecting plaintiff and defendant information, along with detailed issue tracking. The form generates structured output that matches a specific JSON format suitable for legal document processing.

## Features

- **Dynamic Form Sections**: Add/remove multiple plaintiffs and defendants
- **Comprehensive Issue Tracking**: Detailed categories for housing, safety, and legal issues
- **Form Submitter Tracking**: Optional submitter name and email capture with notification opt-in
- **Review Before Submit**: Users can review their submission and make changes before finalizing
- **Structured Data Output**: Generates JSON output matching the goalOutput.md specification
- **At a Glance Summary**: Real-time case overview with filing details, party metadata, and household indicators
- **Accessible Accordions**: Repeatable sections and issue categories use aria-synced accordion controls with collapse-all shortcuts
- **Dual Storage System**: JSON files and PostgreSQL database storage
- **Dropbox Integration**: Automatic cloud backup with folder structure preservation (see [DROPBOX_SETUP.md](DROPBOX_SETUP.md))
- **REST API**: Backend API for managing form submissions
- **Automated Testing**: Playwright tests for form functionality

## Quick Start

### Prerequisites

- Node.js (v14 or higher)
- npm

### Installation

```bash
npm install
```

### Running the Application

1. Start the server:
```bash
npm start
```

2. Open your browser and navigate to:
```
http://localhost:3000
```

### Running Tests

The application includes comprehensive Playwright tests that verify form functionality and output structure.

#### Run all tests:
```bash
npm test
```

#### Run tests with browser visible:
```bash
npm run test:headed
```

#### Debug tests:
```bash
npm run test:debug
```

#### View test results:
```bash
npm run test:report
```

#### Run specific test files:
```bash
npx playwright test tests/simple-form-test.spec.js
```

## Application Workflow

1. **Fill Out Form**: Users complete the legal form with property, plaintiff, and defendant information
2. **Email Notification Modal**: After clicking submit, users are presented with an optional notification opt-in
   - Enter submitter name and email to receive notifications when documents are processed
   - Click "Skip & Submit" to submit anonymously (submitter_name='Anonymous', submitter_email='')
3. **Data Storage**: Form data is saved to both:
   - JSON file in the `data/` directory
   - PostgreSQL database with relational structure
4. **Success Confirmation**: Upon successful submission, users see a confirmation with their entry ID

## API Endpoints

- `GET /` - Main form page
- `GET /review.html` - Review page for submission preview
- `GET /success` - Success confirmation page
- `POST /api/form-entries` - Submit form data
- `GET /api/form-entries` - List all form entries
- `GET /api/form-entries/:id` - Get specific form entry
- `PUT /api/form-entries/:id` - Update form entry
- `DELETE /api/form-entries/:id` - Delete form entry
- `DELETE /api/form-entries/clear-all` - Delete all entries
- `GET /api/health` - Health check

## Form Structure

The form collects:

1. **Property Information**: Address, city, state, ZIP code, filing details
2. **Plaintiff Details**: Name, type, age category, head of household status, comprehensive issue tracking
3. **Defendant Details**: Name, entity type, role (manager/owner)

## Output Format

The application transforms raw form data into a structured JSON format that includes:

- Form metadata
- Plaintiff details with comprehensive discovery information
- Defendant details
- Full address information
- Filing location details

### Example Output Structure

```json
{
  "Form": {
    "Id": "1",
    "InternalName": "AutoPopulationForm",
    "Name": "Auto-Population Form"
  },
  "PlaintiffDetails": [
    {
      "Id": "unique-id",
      "PlaintiffItemNumberName": {
        "First": "John",
        "Last": "Doe",
        "FirstAndLast": "John Doe"
      },
      "PlaintiffItemNumberType": "Individual",
      "PlaintiffItemNumberDiscovery": {
        "VerminIssue": false,
        "Vermin": [],
        "InsectIssues": false,
        "Insects": []
        // ... extensive issue tracking fields
      }
    }
  ],
  "DefendantDetails2": [
    {
      "Id": "unique-id",
      "DefendantItemNumberName": {
        "First": "Jane",
        "Last": "Smith",
        "FirstAndLast": "Jane Smith"
      },
      "DefendantItemNumberType": "LLC",
      "DefendantItemNumberManagerOwner": "Manager"
    }
  ],
  "Full_Address": {
    "Country": "United States",
    "CountryCode": "US"
    // ... complete address information
  }
}
```

## Data Storage

The application uses a dual storage system for comprehensive data management:

### JSON File Storage
- Form submissions are stored as JSON files in the `data/` directory
- Each submission gets a unique timestamp-based ID
- Files are named: `form-entry-{timestamp}-{random}.json`

### PostgreSQL Database Storage
The application stores data in the `legal_forms_db` PostgreSQL database with the following structure:

#### Cases Table
Stores case-level information including:
- Property address, city, state, zip code
- Filing location and county
- **submitter_name**: Name of person who submitted the form (defaults to 'Anonymous' if skipped)
- **submitter_email**: Email address for notifications (defaults to '' if skipped)
- Form metadata and raw payload

#### Parties Table
Stores plaintiff and defendant information:
- Full name, party type (plaintiff/defendant)
- Plaintiff-specific fields: type, age category, head of household
- Defendant-specific fields: entity type, role

#### Party Issue Selections Table
Tracks all issues selected by plaintiffs:
- Links parties to their selected issues (vermin, insects, environmental hazards, etc.)

### Viewing Database Data

To view submitter information from the database:
```bash
psql legal_forms_db -c "SELECT id, submitter_name, submitter_email, property_address, created_at FROM cases ORDER BY created_at DESC LIMIT 10;"
```

For complete form submission details, see the SQL queries section in the project documentation.

## Dropbox Integration (Optional)

The application supports automatic upload of form submissions to Dropbox for cloud backup and storage. When enabled, all form submissions are uploaded to Dropbox while preserving the local folder structure.

### Quick Setup

1. Create a Dropbox app at [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. Generate an access token
3. Add to `.env` file:
   ```env
   DROPBOX_ACCESS_TOKEN=your_token_here
   DROPBOX_ENABLED=true
   DROPBOX_BASE_PATH=/Apps/LegalFormApp
   ```
4. Test the integration:
   ```bash
   node test-dropbox-upload.js
   ```

### Features

- ✅ Automatic upload on form submission
- ✅ Preserves local folder structure in Dropbox
- ✅ Non-blocking (doesn't delay form submission)
- ✅ Error resilient (continues if upload fails)
- ✅ Comprehensive logging

**For complete setup instructions, see [DROPBOX_SETUP.md](DROPBOX_SETUP.md)**

## Testing

The test suite includes:

1. **Form Loading Tests**: Verify all required form elements are present
2. **Form Submission Tests**: Test complete form workflow and data transformation
3. **Multi-Party Tests**: Verify adding multiple plaintiffs and defendants
4. **API Tests**: Validate backend endpoints and data structure
5. **Structure Validation**: Ensure output matches goalOutput.md specification

### Test Coverage

- Form element visibility and interaction
- Dynamic plaintiff/defendant addition
- Form validation and submission
- Data transformation accuracy
- API response validation
- Output structure compliance

## Development

### Project Structure

```
├── index.html          # Main form page
├── server.js           # Express server and data transformation
├── script.js           # (Unused) - original form logic
├── styles.css          # Form styling
├── tests/              # Playwright test files
├── data/               # Form submission storage
├── playwright.config.js # Test configuration
└── package.json        # Dependencies and scripts
```

### Form Field Naming Convention

- Property fields: `property-address`, `city`, `state`, etc.
- Plaintiff fields: `plaintiff-{number}-{field}` (e.g., `plaintiff-1-first-name`)
- Defendant fields: `defendant-{number}-{field}` (e.g., `defendant-1-entity`)
- Issue checkboxes: `{category}-{item}-{plaintiff-number}` (e.g., `vermin-RatsMice-1`)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests as needed
5. Ensure all tests pass: `npm test`
6. Submit a pull request

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[📖 Documentation Index](docs/README.md)** - Start here for all documentation
- **[👤 User Guide](docs/USER_GUIDE.md)** - How to fill out and submit forms
- **[💻 Developer Guide](docs/DEVELOPER_GUIDE.md)** - Development setup and best practices
- **[🏗️ Architecture](docs/ARCHITECTURE.md)** - System design and technical architecture
- **[🔌 API Reference](docs/API_REFERENCE.md)** - Complete REST API documentation
- **[📋 OpenAPI Spec](docs/api/openapi.yaml)** - Machine-readable API specification

### Quick Links

**For Users:**
- [How to Submit a Form](docs/USER_GUIDE.md#filling-out-the-form)
- [Troubleshooting](docs/USER_GUIDE.md#troubleshooting)
- [FAQ](docs/USER_GUIDE.md#faq)

**For Developers:**
- [Development Setup](docs/DEVELOPER_GUIDE.md#development-setup)
- [Running Tests](docs/DEVELOPER_GUIDE.md#testing)
- [Contributing](docs/DEVELOPER_GUIDE.md#contributing)
- [API Examples](docs/API_REFERENCE.md#code-examples)

**For Architects:**
- [System Architecture](docs/ARCHITECTURE.md#system-architecture)
- [Data Flow](docs/ARCHITECTURE.md#data-flow)
- [Scalability](docs/ARCHITECTURE.md#scalability--performance)

## License

MIT License
