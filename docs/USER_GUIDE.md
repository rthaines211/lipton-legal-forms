# User Guide - Legal Form Application

## Table of Contents
- [Getting Started](#getting-started)
- [Accessing the Application](#accessing-the-application)
- [Filling Out the Form](#filling-out-the-form)
- [Common Workflows](#common-workflows)
- [Tips & Best Practices](#tips--best-practices)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

## Getting Started

The Legal Form Application is a web-based tool for collecting comprehensive legal case information, including property details, plaintiff information, defendant information, and detailed issue tracking across 19 categories.

### What You'll Need

- ✅ A modern web browser (Chrome, Firefox, Safari, Edge)
- ✅ Internet connection
- ✅ Case information (address, parties, issues)
- ⏱️ Approximately 10-20 minutes to complete the form

### Before You Begin

Gather the following information:
1. **Property Details**: Full address, filing location
2. **Plaintiff Information**: Names, ages, household status
3. **Defendant Information**: Names, entity types, roles
4. **Issues Documentation**: List of housing issues experienced

---

## Accessing the Application

### Local Development
```
http://localhost:3000
```

### Production (if deployed)
```
https://your-production-domain.com
```

**Note:** In production, you may need an access token. Contact your administrator if you receive an "Unauthorized" message.

---

## Filling Out the Form

### Step 1: Property Information

![Form Header Section]

1. **Property Address**
   - Enter the complete street address
   - Example: `1331 Yorkshire Place NW`

2. **City**
   - Enter the city name
   - Example: `Concord`

3. **State**
   - Enter the full state name
   - Example: `North Carolina`

4. **ZIP Code**
   - Enter the 5-digit postal code
   - Example: `28027`

5. **Filing Location** (Optional)
   - Enter the city where the case will be filed
   - Example: `Los Angeles`

6. **Filing County** (Optional)
   - Enter the county for filing
   - Example: `Los Angeles County`

**💡 Tip:** All fields marked with an asterisk (*) are required.

---

### Step 2: Adding Plaintiffs

Plaintiffs are the individuals or organizations filing the legal action.

#### Adding Your First Plaintiff

1. **Click** the "Plaintiff 1" accordion to expand it

2. **Enter Name Information:**
   - First Name: `Clark`
   - Last Name: `Kent`
   - Full Name: `Clark Kent` (auto-filled)

3. **Select Type:**
   - Choose `Individual` or `Organization`

4. **Select Age Category:**
   - Check `Minor` and/or `Adult` as applicable

5. **Head of Household:**
   - Check this box if the plaintiff is the head of household
   - **Important:** Only ONE plaintiff per unit can be head of household

6. **Unit Number:**
   - Enter the unit/apartment number
   - Example: `1`, `2A`, `Apartment 5`

#### Tracking Issues (Discovery Section)

The discovery section contains 19 comprehensive issue categories. For each applicable category:

##### Vermin Issues
- Check "I am experiencing vermin issues" if applicable
- Select all types: Rats/Mice, Bedbugs, Squirrels, Bats, etc.

##### Insect Issues
- Check "I am experiencing insect issues" if applicable
- Select all types: Roaches, Ants, Flies, Spiders, etc.

##### Environmental Hazards
- Check if experiencing environmental hazards
- Select: Lead paint, Asbestos, Mold, Chemical exposure, etc.

##### Health Hazards
- Select all applicable: Mold, Mildew, Mushrooms, Raw sewage, Toxic water, etc.

##### Structure Issues
- Select all applicable: Broken windows, Holes in walls, Damaged floors, etc.

##### Plumbing Problems
- Select: Clogged fixtures, Leaking pipes, No hot water, etc.

##### Weatherproofing
- Select: Broken windows/doors, Damaged roof, Missing insulation, etc.

##### HVAC Issues
- Select: Broken heating, Broken AC, Poor ventilation, etc.

##### Fire Hazards
- Select: Faulty wiring, Blocked exits, Smoke alarm issues, etc.

##### Safety Issues
- Select: Broken locks, Broken security gates, Poor lighting, etc.

##### Common Area Issues
- Select: Broken elevators, Trash accumulation, Poor maintenance, etc.

##### Trash Problems
- Select: Overflowing receptacles, Inadequate containers, Improper servicing, etc.

##### Notice Issues
- Select: No rent receipts, No payment methods posted, etc.

##### Utility Interruptions
- Select: Water, Gas, Electricity, Heat interruptions

##### Accessibility Issues
- Select: No wheelchair access, Missing grab bars, etc.

##### Tenant Harassment
- Select: Threats, Verbal abuse, Retaliation, etc.

##### Lease Violations
- Select: Illegal fees, Improper notices, etc.

##### Habitability Defects
- Select: Structural damage, Code violations, etc.

##### Other Issues
- Enter free-form text for issues not covered above

**💡 Tip:** Select ALL issues that apply. The more detailed your documentation, the better.

#### Adding Additional Plaintiffs

To add more plaintiffs:

1. **Click** "Add Another Plaintiff" button at the bottom of the plaintiff section
2. A new accordion "Plaintiff 2" will appear
3. Fill out the same information as Plaintiff 1
4. Repeat for all plaintiffs in the household/case

**Maximum:** No limit on number of plaintiffs

#### Removing a Plaintiff

1. **Click** the "Remove Plaintiff X" button within that plaintiff's section
2. Confirm the deletion
3. Remaining plaintiffs will be automatically renumbered

---

### Step 3: Adding Defendants

Defendants are the individuals or entities being sued.

#### Adding Your First Defendant

1. **Click** the "Defendant 1" accordion to expand it

2. **Enter Name Information:**
   - First Name: `Jane`
   - Last Name: `Smith`
   - Full Name: `Jane Smith` (auto-filled)

3. **Select Entity Type:**
   - Individual
   - LLC (Limited Liability Company)
   - Corporation
   - Government
   - Trust
   - Other

4. **Select Role:**
   - Manager
   - Owner

#### Adding Additional Defendants

1. **Click** "Add Another Defendant" button
2. A new accordion "Defendant 2" will appear
3. Fill out the defendant information
4. Repeat for all defendants

**💡 Tip:** Common defendants include property managers, property owners, and management companies.

#### Removing a Defendant

1. **Click** the "Remove Defendant X" button
2. Confirm the deletion
3. Remaining defendants will be automatically renumbered

---

### Step 4: Review Your Submission

Before submitting, review the "At a Glance" summary panel:

- ✅ **Filing Location:** Verify city and county
- ✅ **Property Address:** Confirm complete address
- ✅ **Plaintiff Count:** Check number of plaintiffs
- ✅ **Defendant Count:** Check number of defendants
- ✅ **Head of Household:** Verify only one per unit

**To make changes:**
1. Scroll to the section you want to edit
2. Open the accordion
3. Make your changes
4. The summary updates automatically

---

### Step 5: Email Notification (Optional)

After clicking "Submit", you'll see an email notification modal:

#### Option 1: Receive Notifications
1. **Enter Your Name:** `John Doe`
2. **Enter Your Email:** `john.doe@example.com`
3. **Click** "Submit with Notification"
4. You'll receive email updates when documents are processed

#### Option 2: Submit Anonymously
1. **Click** "Skip & Submit"
2. Form will be submitted without email tracking
3. Submitter name will be recorded as "Anonymous"

**💡 Tip:** Providing email allows you to track processing status and receive notifications.

---

### Step 6: Confirmation

After successful submission, you'll see:

✅ **Success Page** with:
- Confirmation message
- Unique Entry ID (save this for reference)
- Timestamp of submission

**What happens next:**
1. Your form is saved as a JSON file
2. Data is stored in the database
3. Optional: Uploaded to Dropbox cloud backup
4. Optional: Normalization pipeline processes the data
5. You receive email confirmation (if you provided email)

---

## Common Workflows

### Workflow 1: Single Plaintiff, Single Issue

**Scenario:** One tenant with a single plumbing problem

1. Fill out property information
2. Add Plaintiff 1
   - Enter name and details
   - Mark as Head of Household
   - Expand "Plumbing" category
   - Select applicable issue (e.g., "Clogged bath/shower/sink/toilet")
3. Add Defendant 1 (property manager)
4. Review and submit

⏱️ **Estimated Time:** 5 minutes

---

### Workflow 2: Multiple Plaintiffs, Multiple Issues

**Scenario:** Family of 4 with various housing issues

1. Fill out property information
2. Add Plaintiff 1 (Adult, Head of Household)
   - Select all applicable issues
3. Add Plaintiff 2 (Adult)
   - Select their specific issues
4. Add Plaintiff 3 (Minor)
   - Parent selects issues affecting the child
5. Add Plaintiff 4 (Minor)
   - Parent selects issues affecting the child
6. Add Defendant 1 (Property Owner)
7. Add Defendant 2 (Management Company)
8. Review all entries carefully
9. Submit with email notification

⏱️ **Estimated Time:** 15-20 minutes

---

### Workflow 3: Organizational Plaintiff

**Scenario:** Tenant organization filing on behalf of multiple units

1. Fill out property information for building
2. Add Plaintiff 1
   - Enter organization name in First Name field
   - Leave Last Name blank or repeat org name
   - Select "Organization" as type
   - Mark as Head of Household
   - Select building-wide issues
3. Add additional plaintiffs for each affected unit
4. Add all relevant defendants
5. Review and submit

⏱️ **Estimated Time:** 20-30 minutes

---

### Workflow 4: Updating a Previous Submission

**Note:** Form updates must be done via API or by administrator.

**If you need to update a submission:**
1. Contact your administrator
2. Provide your Entry ID
3. Describe the changes needed
4. Administrator will use the API to update the record

**Alternative:** Submit a new form with corrected information and note in "Other Issues" that it supersedes a previous submission.

---

## Tips & Best Practices

### ✅ DO:
- **Save your Entry ID** - You'll need this for follow-up
- **Be thorough** - Select ALL applicable issues
- **Provide email** - Get notifications on processing status
- **Review before submit** - Use the "At a Glance" panel
- **Document everything** - Include details in "Other Issues" field
- **Use proper capitalization** - Makes records easier to read

### ❌ DON'T:
- **Rush** - Take time to be thorough and accurate
- **Skip issues** - Document everything, even minor problems
- **Mark multiple HOH** - Only one Head of Household per unit
- **Submit duplicates** - Check if you already submitted for this address
- **Use abbreviations** - Spell out full names and addresses

### 💡 Pro Tips:
- **Take photos** - Document issues with photos (save separately)
- **Keep receipts** - Any rent receipts, repair requests, correspondence
- **Note dates** - When issues started, when reported, etc. (use "Other Issues")
- **Print confirmation** - Save or print the success page with Entry ID
- **Check email** - Watch for processing notifications

---

## Troubleshooting

### Issue: Form won't submit

**Possible Causes:**
- Missing required fields
- Network connection issues
- Server errors

**Solutions:**
1. Check for red error messages on the form
2. Ensure all required fields (*) are filled
3. Check your internet connection
4. Try refreshing the page (data may be saved in session)
5. Contact support if problem persists

---

### Issue: "Unauthorized" error in production

**Cause:** Missing or invalid access token

**Solution:**
1. Check with your administrator for the correct access URL
2. Ensure you're using the provided link with token
3. Try the alternative URL format: `?token=YOUR_TOKEN`

---

### Issue: Can't add another plaintiff/defendant

**Possible Causes:**
- JavaScript error
- Browser compatibility

**Solutions:**
1. Refresh the page
2. Try a different browser (Chrome recommended)
3. Clear browser cache
4. Disable browser extensions temporarily

---

### Issue: Issues not saving when selecting checkboxes

**Cause:** JavaScript not loading properly

**Solutions:**
1. Refresh the page
2. Check browser console for errors (F12)
3. Ensure JavaScript is enabled
4. Try a different browser

---

### Issue: "At a Glance" panel not updating

**Cause:** State management issue

**Solutions:**
1. Close and reopen accordions
2. Refresh the page
3. Data should still save correctly on submit

---

### Issue: Email notification not received

**Possible Causes:**
- Email in spam folder
- Processing delay
- Incorrect email address

**Solutions:**
1. Check spam/junk folder
2. Wait 5-10 minutes (processing time)
3. Verify email address was entered correctly
4. Contact administrator with your Entry ID

---

### Issue: Lost my Entry ID

**Solution:**
1. Check your email (if you provided one)
2. Contact administrator with:
   - Property address
   - Submission date/time
   - Plaintiff names
3. Administrator can look up your submission in the database

---

## FAQ

### Q: How long does it take to complete the form?
**A:** Typically 10-20 minutes, depending on the number of plaintiffs, defendants, and issues.

---

### Q: Can I save my progress and come back later?
**A:** Currently, no. The form must be completed in one session. However, your browser may save some data in session storage if you accidentally close the tab.

---

### Q: Can I edit my submission after submitting?
**A:** Not directly through the form. Contact your administrator with your Entry ID to request updates.

---

### Q: What happens to my data?
**A:** Your submission is:
1. Saved as a JSON file on the server
2. Stored in a PostgreSQL database
3. Optionally backed up to Dropbox
4. Optionally processed through a normalization pipeline

All data is handled securely and confidentially.

---

### Q: Is my information secure?
**A:** Yes. In production:
- HTTPS encryption for all data transmission
- Token-based authentication
- Secure database storage
- Access controls and logging

---

### Q: How many plaintiffs can I add?
**A:** There is no limit. Add as many plaintiffs as needed for your case.

---

### Q: How many defendants can I add?
**A:** There is no limit. Add all relevant defendants.

---

### Q: Can multiple plaintiffs be Head of Household?
**A:** No. Only ONE plaintiff per unit can be marked as Head of Household. This is a database constraint.

---

### Q: What if my issue isn't listed in the categories?
**A:** Use the "Other Issues" field at the bottom of the discovery section to describe additional issues in free-form text.

---

### Q: Do I need to fill out every category?
**A:** No. Only fill out the categories that apply to your situation. However, be thorough—document all applicable issues.

---

### Q: What is the difference between "Individual" and "Organization" for plaintiffs?
**A:**
- **Individual**: A single person
- **Organization**: A group or entity (e.g., tenant association, non-profit)

---

### Q: What does "Manager" vs "Owner" mean for defendants?
**A:**
- **Manager**: Person/entity managing the property (property manager, management company)
- **Owner**: Person/entity who owns the property (landlord, property owner)

Note: Some defendants may be both manager and owner.

---

### Q: Can I submit the form multiple times?
**A:** Yes, but avoid submitting duplicate entries for the same case. If you need to update information, contact your administrator rather than resubmitting.

---

### Q: What browsers are supported?
**A:** Modern versions of:
- Google Chrome (recommended)
- Mozilla Firefox
- Apple Safari
- Microsoft Edge

Internet Explorer is NOT supported.

---

### Q: Is there a mobile version?
**A:** The form is responsive and works on mobile devices, but a desktop/laptop is recommended for easier data entry.

---

### Q: Who can I contact for help?
**A:** Contact your legal aid organization or administrator. Provide:
- Your Entry ID (if you have it)
- Description of the issue
- Screenshots (if applicable)

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Tab | Navigate to next field |
| Shift + Tab | Navigate to previous field |
| Enter | (in text field) Move to next field |
| Space | (on checkbox) Toggle selection |
| Click heading | Expand/collapse accordion |

---

## Accessibility Features

- ✅ Keyboard navigation support
- ✅ Screen reader compatible (ARIA labels)
- ✅ High contrast mode support
- ✅ Zoom support (up to 200%)
- ✅ Clear focus indicators

**For screen reader users:**
- Form sections are clearly labeled
- Accordions announce expanded/collapsed state
- Required fields are announced
- Error messages are associated with fields

---

## Data Privacy

Your information is:
- ✅ Stored securely
- ✅ Used only for legal case processing
- ✅ Not shared with third parties (except as required for your case)
- ✅ Protected by access controls
- ✅ Logged for security and audit purposes

In production mode, all actions are logged with timestamps and IP addresses for security.

---

## Getting Additional Help

### Documentation
- **README.md** - Quick start and overview
- **API_REFERENCE.md** - For developers/administrators
- **ARCHITECTURE.md** - Technical system details

### Support Contacts
- Legal Aid Organization: [Contact info]
- Technical Support: [Contact info]
- Administrator: [Contact info]

---

**User Guide Version:** 1.0.0
**Last Updated:** 2025-10-21
**Application Version:** 1.0.0
