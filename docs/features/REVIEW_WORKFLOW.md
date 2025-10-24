# Review Workflow Documentation

## Overview
The Legal Form Application now includes a comprehensive review workflow that allows users to preview their submission and make changes before finalizing. This ensures data accuracy and gives users confidence in their submission.

## User Flow

### Step 1: Fill Out the Form
Users complete the legal form at `http://localhost:3000/` with:
- Property information (address, city, state, ZIP, filing details)
- Plaintiff information (name, type, age, head of household status, reported issues)
- Defendant information (name, entity type, role)

### Step 2: Submit for Review
When the user clicks the **"Submit Form"** button:
1. Form data is validated
2. Data is converted from FormData to a JavaScript object
3. A unique ID and timestamp are added
4. All data is stored in **localStorage** as JSON
5. User is redirected to `/review.html`

### Step 3: Review Page
The review page (`review.html`) displays all submitted information in an organized, easy-to-read format:

#### Property Information Section
- Displays all property fields in a grid layout
- Shows address, city, state, ZIP, filing location

#### Plaintiff Information Section
- Each plaintiff is shown in a separate card
- Basic information displayed: name, type, age category, head of household status
- **Reported Issues** are organized by category:
  - Vermin (Rats/Mice, Bedbugs, etc.)
  - Insects (Roaches, Ants, etc.)
  - HVAC (Air Conditioner, Heater, etc.)
  - Electrical, Plumbing, Windows, Doors
  - Structure, Common Areas, Safety
  - Health Hazards, Harassment, Notices
  - And many more categories...

#### Defendant Information Section
- Each defendant shown in a card
- Displays: name, entity type, role (Manager/Owner)

#### Action Buttons (Sticky Footer)
Two primary actions are available:

1. **Edit Form** (Left button)
   - Returns user to the form with `?edit=true` parameter
   - All form data is preserved in localStorage
   - Form automatically restores all entered data

2. **Submit Form** (Right button, primary action)
   - Finalizes the submission
   - Sends data to server via POST to `/api/form-entries`
   - Shows loading overlay during submission
   - On success, redirects to success page

### Step 4A: Edit Form (Optional)
If user clicks **"Edit Form"**:

1. User returns to `/?edit=true`
2. `restoreFormData()` function is triggered
3. Form restoration process:
   - Property fields are repopulated
   - All plaintiffs are recreated with their data
   - All defendants are recreated with their data
   - All checkbox selections are restored
   - Issue sections are shown for head of household plaintiffs
4. User can make any necessary changes
5. When ready, user can submit again to return to review page

### Step 4B: Finalize Submission
If user clicks **"Submit Form"**:

1. Loading overlay is displayed
2. Form data is sent to server
3. Server transforms data into structured JSON format
4. Data is saved to `data/` directory as a JSON file
5. User is redirected to `/success?id={entryId}&timestamp={timestamp}`
6. Success page displays:
   - Entry ID
   - Submission timestamp
   - Confirmation message
   - Next steps information

## Technical Implementation

### Data Storage
- **localStorage** is used for temporary storage between pages
- Key: `formData`
- Data is automatically cleared after successful submission
- Data persists during edit workflow

### Form Data Structure
The data stored in localStorage follows this structure:
```javascript
{
  "id": "unique-id-12345",
  "timestamp": "2025-10-06T18:30:00.000Z",
  "submittedAt": "10/6/2025, 2:30:00 PM",
  "property-address": "123 Main St",
  "city": "Los Angeles",
  "state": "CA",
  "zip-code": "90001",
  "plaintiff-1-first-name": "John",
  "plaintiff-1-last-name": "Doe",
  "plaintiff-1-type": "Individual",
  "plaintiff-1-age": "adult",
  "plaintiff-1-head": "yes",
  "plaintiff-1-unit": "Apt 5",
  "vermin-RatsMice-1": "on",
  "plumbing-Leaks-1": "on",
  "defendant-1-first-name": "Jane",
  "defendant-1-last-name": "Smith",
  "defendant-1-entity": "LLC",
  "defendant-1-role": "owner",
  // ... more fields
}
```

### Key Functions

#### In index.html

**`showReviewScreen()`**
- Collects form data from FormData
- Converts to plain JavaScript object
- Adds ID and timestamp
- Stores in localStorage
- Redirects to review page

**`restoreFormData()`**
- Reads data from localStorage
- Clears existing form sections
- Recreates plaintiffs and defendants
- Repopulates all fields including checkboxes
- Shows issue sections for head of household plaintiffs

#### In review.html

**`populatePropertyData()`**
- Extracts property fields from stored data
- Creates grid layout of label-value pairs

**`populatePlaintiffData()`**
- Finds all plaintiff numbers
- Creates card for each plaintiff
- Extracts and displays reported issues by category

**`populateDefendantData()`**
- Finds all defendant numbers
- Creates card for each defendant

**`extractPlaintiffIssues(num)`**
- Parses checkbox data for specific plaintiff
- Groups issues by category
- Formats issue names for display

**`editForm()`**
- Redirects to `/?edit=true`
- Data remains in localStorage

**`submitForm()`**
- Shows loading overlay
- POSTs data to `/api/form-entries`
- Handles success/error responses
- Redirects to success page

### Server Routes

**`GET /review.html`**
- Serves the review page HTML file

**`POST /api/form-entries`**
- Receives form data
- Transforms to structured JSON format
- Saves to `data/` directory
- Returns success response with entry ID

## Styling & User Experience

### Brand Consistency
- Matches Lipton Legal brand colors:
  - Primary Navy (#1F2A44) for headers
  - Secondary Teal (#00AEEF) for accents
  - Neutral Gray (#F5F5F5) for backgrounds
- Consistent typography with Open Sans font
- Professional gradient headers

### Interactive Elements
- Hover effects on buttons
- Loading spinner during submission
- Sticky action bar for easy access
- Responsive design for mobile devices
- Clear visual hierarchy

### User Feedback
- Info banner explaining review purpose
- Clear labeling of all data
- Visual separation of sections
- Empty state messages when data is missing
- Loading overlay with status message
- Success confirmation after submission
- Alert when form data is restored

## Benefits

1. **Data Accuracy**: Users can verify all information before submission
2. **Error Prevention**: Catch mistakes before finalizing
3. **User Confidence**: Clear visibility into what will be submitted
4. **Flexibility**: Easy to return and make changes
5. **Professional Experience**: Polished workflow matching modern web standards
6. **No Data Loss**: Form data preserved during edit workflow

## Comments & Documentation

All code includes comprehensive inline comments explaining:
- Purpose of each function
- Data flow and transformations
- User interaction handling
- Technical implementation details
- Edge cases and error handling

Key areas with documentation:
- HTML file headers describe page purpose and features
- JavaScript functions have JSDoc-style comments
- Complex logic includes inline explanations
- Server endpoints have descriptive comments
- README and CLAUDE.md files updated with workflow details

---

*Last Updated: October 6, 2025*
