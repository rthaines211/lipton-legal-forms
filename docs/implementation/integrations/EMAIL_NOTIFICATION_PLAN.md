# Email Notification Implementation Plan

## Overview
Implement automated email notifications that send users a Dropbox shared folder link when their legal form documents are generated and uploaded.

## Feature Requirements

### Email Trigger Conditions
- ✅ User must provide email address in the submitter email field
- ✅ Email sends ONLY when final document is uploaded to Dropbox
- ✅ Email contains Dropbox shared folder link for the specific street address

### Email Template
- **From**: Gmail account (to be configured)
- **To**: Submitter email from form
- **Subject**: `<Street Name> - Documents Generated`
- **Body**: `Link to <Street Address> discovery documents can be found here: [hyperlinked share folder link]`

## Technical Implementation Plan

### Phase 1: Dependencies & Setup

#### 1.1 Install Required NPM Packages
```bash
npm install nodemailer
```

**Purpose**:
- `nodemailer` - Email sending library with Gmail integration

#### 1.2 Environment Variables
Add to `.env` file:
```env
# Gmail Configuration
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-specific-password

# Email Feature Toggles
EMAIL_NOTIFICATIONS_ENABLED=true
CONTINUE_ON_EMAIL_FAILURE=true
```

**Gmail App Password Setup**:
1. Enable 2-Factor Authentication on Gmail account
2. Go to Google Account Settings → Security → 2-Step Verification
3. Scroll to "App passwords" section
4. Generate app password for "Mail" application
5. Use generated password in `GMAIL_APP_PASSWORD`

### Phase 2: Dropbox Share Link Generation

#### 2.1 Extend Dropbox Service (`dropbox-service.js`)
Add new methods:
```javascript
/**
 * Creates a shared link for a Dropbox folder
 * @param {string} folderPath - Dropbox folder path (e.g., "/Apps/LegalFormApp/Clients/123MainSt")
 * @returns {Promise<string>} - Shared folder URL
 */
async createSharedFolderLink(folderPath)

/**
 * Gets existing shared link or creates new one
 * @param {string} folderPath - Dropbox folder path
 * @returns {Promise<string>} - Shared folder URL
 */
async getOrCreateSharedLink(folderPath)
```

**Implementation Notes**:
- Use Dropbox SDK's `sharingCreateSharedLinkWithSettings()` method
- Check for existing links first with `sharingListSharedLinks()`
- Handle edge cases (folder doesn't exist, permissions issues)
- Return shareable URL (not preview URL)

#### 2.2 Determine Street Address Folder Path
Logic to construct folder path from form submission:
```javascript
// Example: "123 Main St" → "/Apps/LegalFormApp/Clients/123MainSt"
const streetAddress = formData.Property.Address;
const sanitizedAddress = streetAddress.replace(/[^a-zA-Z0-9]/g, '');
const folderPath = `${DROPBOX_BASE_PATH}/Clients/${sanitizedAddress}`;
```

### Phase 3: Email Service Implementation

#### 3.1 Create Email Service (`email-service.js`)
New module structure:
```javascript
const nodemailer = require('nodemailer');

class EmailService {
  constructor() {
    this.transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: process.env.GMAIL_USER,
        pass: process.env.GMAIL_APP_PASSWORD
      }
    });
  }

  /**
   * Sends document notification email with Dropbox link
   * @param {Object} params
   * @param {string} params.recipientEmail
   * @param {string} params.streetAddress - Full street address
   * @param {string} params.streetName - Street name only for subject
   * @param {string} params.dropboxShareLink
   */
  async sendDocumentNotification({ recipientEmail, streetAddress, streetName, dropboxShareLink })

  /**
   * Validates email configuration
   */
  async verifyConfiguration()
}

module.exports = new EmailService();
```

#### 3.2 Email Template
HTML email body:
```html
<p>Hello,</p>
<p>Your legal discovery documents have been generated and are ready for review.</p>
<p>Link to <strong>${streetAddress}</strong> discovery documents can be found here:</p>
<p><a href="${dropboxShareLink}" style="color: #0066cc; text-decoration: none;">${dropboxShareLink}</a></p>
<p>This link will remain active and accessible.</p>
<br>
<p>Best regards,<br>Legal Form Application</p>
```

Plain text fallback:
```text
Hello,

Your legal discovery documents have been generated and are ready for review.

Link to ${streetAddress} discovery documents can be found here:
${dropboxShareLink}

This link will remain active and accessible.

Best regards,
Legal Form Application
```

### Phase 4: Integration with Existing Workflow

#### 4.1 Update Server Pipeline (`server.js`)
Modify the form submission workflow:

**Current Flow**:
1. Receive form submission
2. Transform data
3. Save to database
4. Save JSON file locally
5. Upload to Dropbox (if enabled)
6. Execute Python normalization pipeline (if enabled)
7. Return response

**Updated Flow**:
1. Receive form submission
2. Transform data
3. Save to database
4. Save JSON file locally
5. Upload to Dropbox (if enabled)
6. Execute Python normalization pipeline (if enabled)
7. **[NEW] Wait for pipeline completion & final document upload**
8. **[NEW] Generate Dropbox share link for street address folder**
9. **[NEW] Send email notification (if email provided)**
10. Return response

#### 4.2 Determine "Final Document" Trigger
**Options**:
- **Option A**: Pipeline completion callback (requires pipeline modification)
- **Option B**: Polling/watching output directory for completion marker
- **Option C**: Manual trigger via new API endpoint
- **Option D**: Time-based delay after pipeline start

**Recommended**: Option A with fallback to Option D
- Modify Python pipeline to POST to `/api/pipeline-complete` webhook
- Include case ID and output folder path
- Server generates share link and sends email on webhook receipt
- Fallback: 30-second delay if webhook not received

#### 4.3 Server Integration Code Location
Add to `server.js` around line 1400 (after pipeline execution):

```javascript
// After pipeline execution completes
if (EMAIL_NOTIFICATIONS_ENABLED && submitterEmail && submitterEmail !== '') {
  try {
    // Wait for pipeline completion
    await waitForPipelineCompletion(caseId, timeout = 300000); // 5 min

    // Determine street address folder path
    const streetAddress = transformedData.Property.Address;
    const folderPath = getDropboxFolderPath(streetAddress);

    // Generate shared link
    const shareLink = await dropboxService.getOrCreateSharedLink(folderPath);

    // Send email
    const streetName = extractStreetName(streetAddress);
    await emailService.sendDocumentNotification({
      recipientEmail: submitterEmail,
      streetAddress,
      streetName,
      dropboxShareLink: shareLink
    });

    console.log(`✅ Email sent to ${submitterEmail} with Dropbox link`);
  } catch (error) {
    console.error('❌ Email notification failed:', error);
    if (!CONTINUE_ON_EMAIL_FAILURE) {
      throw error;
    }
  }
}
```

### Phase 5: Testing & Validation

#### 5.1 Unit Tests
Create `tests/email-service.test.js`:
- Test email configuration validation
- Test email sending with mock transporter
- Test HTML and plain text rendering
- Test error handling

#### 5.2 Integration Tests
Create `tests/email-integration.test.js`:
- Test end-to-end flow with test Gmail account
- Test Dropbox share link generation
- Test pipeline completion detection
- Test email opt-out (no email provided)

#### 5.3 Manual Testing Checklist
- [ ] Submit form WITH email address → verify email received
- [ ] Submit form WITHOUT email address → verify no email sent
- [ ] Verify Dropbox share link is accessible
- [ ] Verify email subject contains correct street name
- [ ] Verify email body contains correct street address
- [ ] Test with invalid email address → verify error handling
- [ ] Test with Dropbox upload disabled → verify graceful handling
- [ ] Test with pipeline failure → verify email still sends (if docs exist)

### Phase 6: Documentation & Configuration

#### 6.1 Update Documentation Files
- **README.md**: Add email notification feature description
- **CLAUDE.md**: Document email integration
- **DROPBOX_SETUP.md**: Add section on email + Dropbox integration

#### 6.2 Create Email Setup Guide
New file: `EMAIL_SETUP.md`
- Gmail app password setup instructions
- Environment variable configuration
- Troubleshooting common issues
- Testing email functionality

#### 6.3 Update Environment Template
Create `.env.example`:
```env
# Gmail Configuration (required for email notifications)
GMAIL_USER=
GMAIL_APP_PASSWORD=

# Email Feature Toggles
EMAIL_NOTIFICATIONS_ENABLED=true
CONTINUE_ON_EMAIL_FAILURE=true
```

## Implementation Timeline

### Estimated Effort
- **Phase 1** (Setup): 30 minutes
- **Phase 2** (Dropbox sharing): 1-2 hours
- **Phase 3** (Email service): 1-2 hours
- **Phase 4** (Integration): 2-3 hours
- **Phase 5** (Testing): 1-2 hours
- **Phase 6** (Documentation): 1 hour

**Total**: 6-10 hours

### Development Order
1. ✅ Phase 1: Install dependencies and configure environment
2. ✅ Phase 2: Extend Dropbox service for share links
3. ✅ Phase 3: Build email service module
4. ✅ Phase 4: Integrate into server workflow
5. ✅ Phase 5: Test thoroughly
6. ✅ Phase 6: Document everything

## Security Considerations

### Email Security
- ✅ Use app-specific passwords (never account password)
- ✅ Store credentials in environment variables only
- ✅ Never commit `.env` file to version control
- ✅ Add `.env` to `.gitignore` if using git

### Dropbox Security
- ✅ Share links are read-only by default
- ✅ Consider link expiration settings (optional)
- ✅ Limit sharing to specific folder only
- ✅ Audit shared links periodically

### Privacy Considerations
- ✅ Email opt-in required (user must provide email)
- ✅ No emails sent without explicit consent
- ✅ Store submitter email securely in database
- ✅ Consider GDPR/privacy policy implications

## Error Handling Strategy

### Email Failures
- Log detailed error messages
- Continue processing unless `CONTINUE_ON_EMAIL_FAILURE=false`
- Store failed email attempts for retry (future enhancement)
- Notify admin of persistent failures

### Dropbox Failures
- Gracefully handle missing folders
- Handle rate limiting (429 errors)
- Retry share link generation with exponential backoff
- Fall back to base folder link if specific folder fails

### Pipeline Failures
- Send email even if pipeline partially fails (if docs exist)
- Include warning in email if processing incomplete
- Provide support contact for issues

## Future Enhancements
- Email templates with branding/logo
- Multiple recipient support (CC/BCC)
- Email delivery status tracking
- Retry queue for failed emails
- SMS notifications (Twilio integration)
- In-app notification dashboard
- Email preferences (frequency, types)

---

## GCP Deployment Considerations

### Overview
The current Gmail + Nodemailer approach works locally but has several challenges for GCP production deployment. This section outlines cloud-native alternatives and best practices.

### Gmail SMTP Limitations in Cloud Environments

#### Issues with Gmail SMTP on GCP
1. **Port Restrictions**: GCP blocks outbound SMTP traffic on ports 25, 465, and 587 from Compute Engine instances
2. **Rate Limiting**: Gmail SMTP has sending limits (500 emails/day for personal accounts, 2000/day for Google Workspace)
3. **Authentication Complexity**: App passwords require manual setup and rotation
4. **Reliability**: Not designed for automated, high-volume sending
5. **Monitoring**: Limited visibility into delivery status and failures

#### GCP Compute Engine Port Blocking
From [GCP Documentation](https://cloud.google.com/compute/docs/tutorials/sending-mail):
> "Compute Engine does not allow outbound connections on ports 25, 465, and 587 by default to prevent abuse and spam."

**Impact**: Direct Gmail SMTP will NOT work on:
- ✅ App Engine Standard/Flexible (uses different networking)
- ❌ Compute Engine VMs
- ✅ Cloud Run (uses different networking)
- ❌ GKE (Kubernetes Engine) without special network configuration

### Recommended Solutions for GCP

#### Option 1: SendGrid (RECOMMENDED for Production)
**Pros**:
- ✅ Free tier: 100 emails/day forever (sufficient for this use case)
- ✅ Works on all GCP services (uses port 443/2525)
- ✅ Better deliverability and spam reputation
- ✅ Email analytics and tracking
- ✅ Transactional email templates
- ✅ Easy integration with Nodemailer
- ✅ Dedicated IPs available for scaling

**Cons**:
- Requires SendGrid account setup
- Additional third-party dependency

**Implementation**:
```bash
npm install @sendgrid/mail
```

```javascript
// email-service.js (SendGrid version)
const sgMail = require('@sendgrid/mail');

class EmailService {
  constructor() {
    sgMail.setApiKey(process.env.SENDGRID_API_KEY);
  }

  async sendDocumentNotification({ recipientEmail, streetAddress, streetName, dropboxShareLink }) {
    const msg = {
      to: recipientEmail,
      from: process.env.SENDGRID_VERIFIED_SENDER, // must be verified in SendGrid
      subject: `${streetName} - Documents Generated`,
      text: `Link to ${streetAddress} discovery documents can be found here: ${dropboxShareLink}`,
      html: `
        <p>Hello,</p>
        <p>Your legal discovery documents have been generated and are ready for review.</p>
        <p>Link to <strong>${streetAddress}</strong> discovery documents can be found here:</p>
        <p><a href="${dropboxShareLink}">${dropboxShareLink}</a></p>
      `,
    };

    return await sgMail.send(msg);
  }
}
```

**Environment Variables**:
```env
SENDGRID_API_KEY=SG.xxxxxxxxxxxxx
SENDGRID_VERIFIED_SENDER=noreply@yourdomain.com
EMAIL_PROVIDER=sendgrid
```

**Setup Steps**:
1. Create SendGrid account: https://sendgrid.com/
2. Generate API key (Settings → API Keys)
3. Verify sender email address (Settings → Sender Authentication)
4. Add API key to GCP Secret Manager
5. Update email-service.js to use SendGrid

#### Option 2: Gmail via Google Workspace (Alternative)
**Pros**:
- ✅ Works if using Google Workspace (not personal Gmail)
- ✅ Higher sending limits (2000 emails/day)
- ✅ Native Google integration

**Cons**:
- ❌ Requires paid Google Workspace subscription ($6-18/user/month)
- ❌ Still hits port blocking on Compute Engine
- ❌ Still limited compared to transactional email services

**Only use if**:
- Already have Google Workspace
- Deploying to App Engine or Cloud Run (not Compute Engine)
- Low volume usage (<100 emails/day)

#### Option 3: Mailgun
**Pros**:
- ✅ Free tier: 1000 emails/month
- ✅ Works on all GCP services
- ✅ Good deliverability
- ✅ Nodemailer integration

**Environment Variables**:
```env
MAILGUN_API_KEY=xxxxxxxxxxxxx
MAILGUN_DOMAIN=mg.yourdomain.com
EMAIL_PROVIDER=mailgun
```

#### Option 4: Google Cloud Email Relay (SendGrid Partnership)
**Pros**:
- ✅ Native GCP integration
- ✅ Billed through GCP account
- ✅ Uses SendGrid infrastructure

**Cons**:
- More expensive than direct SendGrid
- Requires GCP billing setup

### GCP Secret Management

#### DO NOT Use Environment Variables for Secrets
**Bad (insecure)**:
```yaml
# app.yaml - NEVER DO THIS
env_variables:
  GMAIL_APP_PASSWORD: "abcd-efgh-ijkl-mnop"
  SENDGRID_API_KEY: "SG.xxxxxxxxxxxxxx"
```

#### DO Use Secret Manager
**Good (secure)**:

**1. Create Secrets in GCP Console**:
```bash
# Create secret for SendGrid API key
gcloud secrets create sendgrid-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Create secret for verified sender
echo -n "noreply@yourdomain.com" | gcloud secrets create email-sender \
  --data-file=-
```

**2. Grant Access to Service Account**:
```bash
# Grant secret accessor role to App Engine service account
gcloud secrets add-iam-policy-binding sendgrid-api-key \
  --member="serviceAccount:PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

**3. Update email-service.js to Load Secrets**:
```javascript
const { SecretManagerServiceClient } = require('@google-cloud/secret-manager');

class EmailService {
  constructor() {
    this.secretClient = new SecretManagerServiceClient();
    this.apiKey = null;
  }

  async initialize() {
    // Load secret from Secret Manager
    const [version] = await this.secretClient.accessSecretVersion({
      name: 'projects/PROJECT_ID/secrets/sendgrid-api-key/versions/latest',
    });

    this.apiKey = version.payload.data.toString();
    sgMail.setApiKey(this.apiKey);
  }
}

// Usage
const emailService = new EmailService();
await emailService.initialize();
```

**4. Install Secret Manager Client**:
```bash
npm install @google-cloud/secret-manager
```

### GCP Deployment Configurations

#### App Engine (app.yaml)
```yaml
runtime: nodejs20
instance_class: F1

env_variables:
  NODE_ENV: production
  EMAIL_PROVIDER: sendgrid
  EMAIL_NOTIFICATIONS_ENABLED: "true"
  CONTINUE_ON_EMAIL_FAILURE: "true"

# Secrets loaded from Secret Manager
beta_settings:
  cloud_sql_instances: PROJECT_ID:REGION:INSTANCE_NAME

automatic_scaling:
  min_idle_instances: 0
  max_idle_instances: 1
  min_pending_latency: 1000ms
  max_pending_latency: 5000ms
```

#### Cloud Run (cloudbuild.yaml)
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/PROJECT_ID/legal-form-app', '.']

  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/PROJECT_ID/legal-form-app']

  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'legal-form-app'
      - '--image'
      - 'gcr.io/PROJECT_ID/legal-form-app'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--set-secrets'
      - 'SENDGRID_API_KEY=sendgrid-api-key:latest,EMAIL_SENDER=email-sender:latest'
```

#### Dockerfile for Cloud Run
```dockerfile
FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["node", "server.js"]
```

### Environment-Aware Configuration

#### Updated email-service.js (Multi-Provider Support)
```javascript
class EmailService {
  constructor() {
    this.provider = process.env.EMAIL_PROVIDER || 'gmail';
    this.transporter = null;
  }

  async initialize() {
    switch (this.provider) {
      case 'sendgrid':
        await this.initializeSendGrid();
        break;
      case 'gmail':
        this.initializeGmail();
        break;
      case 'mailgun':
        await this.initializeMailgun();
        break;
      default:
        throw new Error(`Unknown email provider: ${this.provider}`);
    }
  }

  async initializeSendGrid() {
    const sgMail = require('@sendgrid/mail');

    // Try Secret Manager first (GCP), fall back to env var (local)
    let apiKey;
    if (process.env.GCP_PROJECT) {
      const { SecretManagerServiceClient } = require('@google-cloud/secret-manager');
      const client = new SecretManagerServiceClient();
      const [version] = await client.accessSecretVersion({
        name: `projects/${process.env.GCP_PROJECT}/secrets/sendgrid-api-key/versions/latest`,
      });
      apiKey = version.payload.data.toString();
    } else {
      apiKey = process.env.SENDGRID_API_KEY;
    }

    sgMail.setApiKey(apiKey);
    this.transporter = sgMail;
  }

  initializeGmail() {
    const nodemailer = require('nodemailer');
    this.transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: process.env.GMAIL_USER,
        pass: process.env.GMAIL_APP_PASSWORD
      }
    });
  }
}
```

### Testing Strategy for GCP

#### Local Development (Gmail)
```env
EMAIL_PROVIDER=gmail
GMAIL_USER=test@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

#### GCP Staging (SendGrid with test credentials)
```env
EMAIL_PROVIDER=sendgrid
GCP_PROJECT=my-project-staging
```

#### GCP Production (SendGrid with production credentials)
```env
EMAIL_PROVIDER=sendgrid
GCP_PROJECT=my-project-prod
```

### Monitoring & Logging

#### Cloud Logging
```javascript
// Add structured logging for GCP
const { Logging } = require('@google-cloud/logging');
const logging = new Logging();
const log = logging.log('email-notifications');

class EmailService {
  async sendDocumentNotification(params) {
    const metadata = {
      severity: 'INFO',
      resource: { type: 'cloud_run_revision' }
    };

    try {
      await this.send(params);

      const entry = log.entry(metadata, {
        message: 'Email sent successfully',
        recipient: params.recipientEmail,
        streetAddress: params.streetAddress,
        timestamp: new Date().toISOString()
      });

      await log.write(entry);
    } catch (error) {
      const errorEntry = log.entry({ ...metadata, severity: 'ERROR' }, {
        message: 'Email send failed',
        error: error.message,
        recipient: params.recipientEmail
      });

      await log.write(errorEntry);
      throw error;
    }
  }
}
```

#### Cloud Monitoring Alerts
Create alerts for:
- Email send failures (error rate > 5%)
- High email volume (> 50 emails/hour)
- Secret access failures
- API quota exhaustion

### Cost Estimation

#### SendGrid Costs
- **Free Tier**: 100 emails/day = 3000 emails/month (FREE)
- **Essentials**: $19.95/month = 50,000 emails/month ($0.0004/email)
- **Pro**: $89.95/month = 100,000 emails/month ($0.0009/email)

**Estimated Usage**: ~10-50 emails/day = FREE tier sufficient

#### GCP Secret Manager Costs
- **Secret versions**: $0.06 per secret per month
- **Access operations**: $0.03 per 10,000 accesses
- **Estimated**: ~$0.20/month (2 secrets + access)

#### Total Monthly Cost (Production)
- SendGrid: $0 (free tier)
- Secret Manager: $0.20
- **Total: ~$0.20/month**

### Migration Checklist

#### Phase 1: Add SendGrid Support (Local)
- [ ] Create SendGrid account
- [ ] Verify sender email address
- [ ] Generate API key
- [ ] Add SendGrid to package.json
- [ ] Update email-service.js with multi-provider support
- [ ] Test locally with SendGrid
- [ ] Update .env.example

#### Phase 2: GCP Secret Manager Setup
- [ ] Create GCP project (if not exists)
- [ ] Enable Secret Manager API
- [ ] Create secrets for API keys
- [ ] Grant IAM permissions to service account
- [ ] Update email-service.js to load from Secret Manager
- [ ] Test with GCP local credentials

#### Phase 3: Deployment Configuration
- [ ] Choose deployment target (App Engine/Cloud Run/Compute Engine)
- [ ] Create app.yaml or Dockerfile
- [ ] Configure environment variables
- [ ] Set up Cloud Build (if using CI/CD)
- [ ] Deploy to staging environment
- [ ] Run integration tests

#### Phase 4: Production Deployment
- [ ] Review security settings
- [ ] Configure monitoring and alerts
- [ ] Set up error reporting
- [ ] Deploy to production
- [ ] Verify email sending works
- [ ] Monitor for 24 hours

### Deployment Target Recommendations

#### Recommended: Cloud Run
**Why**:
- ✅ Pay per use (cost-effective for low traffic)
- ✅ Auto-scaling (0 to N instances)
- ✅ No port blocking issues
- ✅ Easy container deployment
- ✅ Built-in HTTPS
- ✅ Secret Manager integration

**Pricing**:
- Free tier: 2 million requests/month
- $0.00002400 per request after free tier
- Estimated: <$5/month for typical usage

#### Alternative: App Engine Standard
**Why**:
- ✅ Fully managed (no container management)
- ✅ Auto-scaling
- ✅ Built-in cron jobs
- ✅ Free tier available

**Cons**:
- Less flexible than Cloud Run
- Higher minimum costs if traffic is very low

#### NOT Recommended: Compute Engine
**Why**:
- ❌ Port blocking requires workarounds
- ❌ Manual scaling and management
- ❌ Higher costs for always-on VM
- ❌ More complex deployment

**Only use if**: Need persistent file system or specific VM requirements

### Final Recommendations

#### For Local Development
```javascript
// .env
EMAIL_PROVIDER=gmail
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

#### For GCP Production
```javascript
// Environment variables in Cloud Run/App Engine
EMAIL_PROVIDER=sendgrid
GCP_PROJECT=your-project-id
EMAIL_NOTIFICATIONS_ENABLED=true
CONTINUE_ON_EMAIL_FAILURE=true

// Secrets in Secret Manager
sendgrid-api-key: SG.xxxxxxxxxxxxxx
sendgrid-verified-sender: noreply@yourdomain.com
```

#### Deployment Command (Cloud Run)
```bash
gcloud run deploy legal-form-app \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars EMAIL_PROVIDER=sendgrid,EMAIL_NOTIFICATIONS_ENABLED=true \
  --set-secrets SENDGRID_API_KEY=sendgrid-api-key:latest,EMAIL_SENDER=sendgrid-verified-sender:latest \
  --max-instances 10 \
  --memory 512Mi
```

### Summary: GCP Translation

**Answer: Will it translate easily to GCP?**

**With Gmail SMTP**: ❌ NO
- Port blocking on Compute Engine
- Rate limits too restrictive
- Not production-ready

**With SendGrid + Recommended Changes**: ✅ YES
- Minimal code changes (~50 lines)
- Works on all GCP services
- Production-ready and scalable
- Cost-effective (<$1/month)
- Better deliverability
- Easy monitoring and logging

**Recommended Path Forward**:
1. Implement Gmail version for local development (keep it simple)
2. Add SendGrid support with provider switching
3. Use GCP Secret Manager for production credentials
4. Deploy to Cloud Run for best cost/performance
5. Total migration effort: +2-3 hours

---

**Created**: 2025-10-20
**Updated**: 2025-10-21 (Added GCP deployment considerations)
**Status**: Planning Phase
**Priority**: High
**Assignee**: Development Team
