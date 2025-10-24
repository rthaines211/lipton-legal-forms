#!/bin/bash
# Script to reorder phases in PIPELINE_INTEGRATION_PLAN.md
# Based on "Option 1: Stabilize & Polish First" strategy

echo "🔄 Reordering PIPELINE_INTEGRATION_PLAN.md phases..."

# Create backup
cp PIPELINE_INTEGRATION_PLAN.md PIPELINE_INTEGRATION_PLAN.md.backup
echo "✅ Backup created: PIPELINE_INTEGRATION_PLAN.md.backup"

# Create a new comprehensive integration plan with reordered phases
cat > PIPELINE_INTEGRATION_PLAN_REORDERED.md << 'EOF'
# Pipeline Integration Plan: Auto-Execute on Form Submission

**Status**: Phases 1 & 2 Complete ✅ | In Progress
**Created**: 2025-10-17
**Updated**: 2025-10-17 (Reordered based on "Stabilize & Polish First" strategy)
**Target**: Integrate Python normalization pipeline (phases 1-5) to auto-execute when forms are submitted

## Implementation Status

| Phase | Status | Completion Date |
|-------|--------|-----------------|
| Phase 1: Python API Service | ✅ **COMPLETE** | 2025-10-17 |
| Phase 2: Node.js Integration | ✅ **COMPLETE** | 2025-10-17 |
| **Phase 3: Frontend Status Indicator** | ⬜ **NEXT** | - |
| Phase 4: Testing & Validation | ⬜ Not Started | - |
| Phase 5: Monitoring & Logging | ⬜ Not Started | - |
| Phase 6: Documentation Cleanup | ⬜ Not Started | - |
| Phase 7: Environment & Security | ⬜ Not Started | - |
| Phase 8: Docker & GCP Configuration | ⬜ Not Started | - |
| Phase 9: Deployment | ⬜ Not Started | - |

> **Note**: Phases have been reordered to prioritize user experience and stability before deployment.
> Original Phase 5 (Frontend) moved to Phase 3, Docker/GCP deferred to Phase 8.

---

## Why This Order?

**Rationale for Reordering:**

1. **Phase 3: Frontend Status Indicator (was Phase 5)** - NEXT
   - Users currently wait 6+ seconds with no feedback
   - Simple frontend-only changes, no infrastructure complexity
   - Immediate improvement to user experience
   - Validates pipeline integration works correctly

2. **Phase 4: Testing & Validation (was Phase 7)**
   - Fix missing database issue options
   - Validate webhook delivery
   - Ensure system stability before deployment
   - Easier to debug locally than in containers

3. **Phase 5: Monitoring & Logging (was Phase 8)**
   - Add observability before deploying
   - Track metrics and errors
   - Essential for production readiness

4. **Phase 6: Documentation Cleanup (unchanged)**
   - Archive old documentation
   - Update guides while implementation is fresh

5. **Phase 7: Environment & Security (was Phase 4)**
   - Prepare for production deployment
   - Secret management
   - Security hardening

6. **Phase 8: Docker & GCP Configuration (was Phase 3)**
   - Deferred until system is stable and tested
   - Containerize working, validated system
   - Reduces deployment risk

7. **Phase 9: Deployment (unchanged)**
   - Deploy fully tested, monitored system
   - Lower risk with all validation complete

---

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Implementation Phases](#implementation-phases)
4. [Success Criteria](#success-criteria)

---

## Overview

### Current State (After Phases 1 & 2)
- ✅ **Python API Service**: FastAPI running on port 8000, executes full pipeline
- ✅ **Node.js Integration**: Automatically calls Python API after form submission
- ✅ **Webhooks Enabled**: Documents sent to Docmosis for generation
- ✅ **End-to-End Flow Working**: Form → DB → Pipeline → Webhooks
- ⚠️ **No User Feedback**: 6-second wait with no progress indicator
- ⚠️ **Incomplete Testing**: Some DB issue options missing
- ⚠️ **No Monitoring**: Limited observability into pipeline health

### Target State
- ✅ **User Feedback**: Real-time progress during pipeline execution
- ✅ **Thoroughly Tested**: All scenarios validated, data complete
- ✅ **Observable**: Logging and metrics in place
- ✅ **Production Ready**: Containerized and deployed to GCP
- ✅ **Secure**: Secrets managed properly, authentication in place

---

## Architecture

### System Diagram (Current)

\`\`\`
┌─────────────┐
│   Browser   │
│  (User)     │
└──────┬──────┘
       │ 1. POST /api/form-entries (form data)
       │    ⚠️ No feedback during 6s wait
       ↓
┌─────────────────────────────────────┐
│  Node.js Server (Port 3000) ✅      │
│  - Receives form submission         │
│  - Saves to PostgreSQL database     │
│  - Saves JSON file to data/         │
│  - Calls Python API                 │
└──────┬──────────────────────────────┘
       │ 2. HTTP POST /api/normalize
       │    (sends structured JSON)
       ↓
┌─────────────────────────────────────┐
│  Python API (Port 8000) ✅          │
│  - Phase 1: Normalize input         │
│  - Phase 2: Build datasets          │
│  - Phase 3: Flag processors         │
│  - Phase 4: Document profiles       │
│  - Phase 5: Set splitting           │
└──────┬──────────────────────────────┘
       │ 3. For each set...
       │    HTTP POST to webhook
       ↓
┌─────────────────────────────────────┐
│   Docmosis Webhook ✅               │
│   https://docs.liptonlegal.com      │
│  - Receives discovery sets          │
│  - Generates Word documents         │
└─────────────────────────────────────┘
\`\`\`

---

## Implementation Phases

### **Phase 1: Python API Service** ✅ COMPLETE
**Completed**: 2025-10-17
**Actual Time**: 2.5 hours

See [PHASE1_COMPLETE.md](normalization work/PHASE1_COMPLETE.md) for full details.

**What Was Built:**
- FastAPI application with `/api/normalize`, `/health`, `/api/status` endpoints
- Complete pipeline integration (phases 1-5)
- Environment-based configuration
- Automated testing script
- Comprehensive documentation

**Files Created:**
- \`normalization work/api/main.py\` - FastAPI app
- \`normalization work/api/routes.py\` - API endpoints
- \`normalization work/api/README.md\` - API documentation
- \`normalization work/.env\` - Configuration
- \`normalization work/test_api.sh\` - Test script

---

### **Phase 2: Node.js Integration** ✅ COMPLETE
**Completed**: 2025-10-17
**Actual Time**: 1.5 hours

See [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md) for full details.

**What Was Built:**
- Installed axios and dotenv dependencies
- Updated \`.env\` with pipeline configuration
- Modified \`server.js\` to call Python API after database save
- Added \`callNormalizationPipeline()\` function with error handling
- Updated API response to include pipeline results
- Created automated integration script

**Files Created/Modified:**
- \`server.js\` - Added pipeline integration
- \`.env\` - Added PIPELINE_API_* configuration
- \`package.json\` - Added axios, dotenv
- \`apply_phase2_integration.js\` - Automation script
- \`PHASE2_COMPLETE.md\` - Documentation

**Configuration Added:**
\`\`\`bash
PIPELINE_API_URL=http://localhost:8000
PIPELINE_API_ENABLED=true
PIPELINE_API_TIMEOUT=60000
EXECUTE_PIPELINE_ON_SUBMIT=true
CONTINUE_ON_PIPELINE_FAILURE=true
\`\`\`

**Testing Results:**
- ✅ Form submission works end-to-end
- ✅ Pipeline executes all 5 phases successfully
- ✅ Execution time: ~6 seconds
- ✅ Webhooks deliver documents to Docmosis
- ⚠️ Some DB issue options missing (non-blocking)

---

### **Phase 3: Frontend Status Indicator** ⬜ NEXT
**Status**: Not Started
**Estimated Time**: 1-2 hours
**Priority**: HIGH - Immediate user value

#### Problem
Users submit form and wait 6+ seconds with no feedback. They don't know:
- If the form was submitted successfully
- If documents are being generated
- How long to wait
- If something went wrong

#### Solution
Add real-time progress indicator showing:
1. Form submission status
2. Pipeline execution progress
3. Document generation status
4. Success/error messages

#### Tasks
- [ ] Add loading spinner/progress indicator
- [ ] Display pipeline phase progress
- [ ] Show execution time
- [ ] Display success confirmation with details
- [ ] Show error messages if pipeline fails
- [ ] Add optional "View Details" section

#### Implementation

**HTML Addition** (\`index.html\` or create \`pipeline-status.html\`):
\`\`\`html
<div id="pipeline-status-modal" class="modal" style="display:none;">
    <div class="modal-content">
        <h2>Processing Your Discovery Documents</h2>

        <div id="pipeline-progress">
            <div class="progress-step" data-phase="submit">
                <span class="spinner">⏳</span>
                <span>Submitting form...</span>
            </div>
            <div class="progress-step" data-phase="database">
                <span class="icon">⏳</span>
                <span>Saving to database...</span>
            </div>
            <div class="progress-step" data-phase="pipeline">
                <span class="icon">⏳</span>
                <span>Running normalization pipeline...</span>
            </div>
            <div class="progress-step" data-phase="documents">
                <span class="icon">⏳</span>
                <span>Generating documents...</span>
            </div>
        </div>

        <div id="pipeline-result" style="display:none;">
            <h3 class="success">✅ Success!</h3>
            <p>Your discovery documents have been generated.</p>
            <div id="pipeline-details">
                <p>Pipeline completed in <span id="execution-time"></span>ms</p>
                <p><span id="sets-generated"></span> document sets created</p>
            </div>
            <button onclick="location.href='/success'">Continue</button>
        </div>

        <div id="pipeline-error" style="display:none;">
            <h3 class="error">⚠️ Processing Issue</h3>
            <p>Your form was saved successfully, but document generation encountered an issue.</p>
            <p class="error-message" id="error-details"></p>
            <button onclick="location.href='/success'">Continue</button>
        </div>
    </div>
</div>
\`\`\`

**JavaScript** (update form submission handler):
\`\`\`javascript
// In form submission handler
async function submitForm(formData) {
    // Show progress modal
    document.getElementById('pipeline-status-modal').style.display = 'block';

    // Step 1: Submit form
    updateProgress('submit', 'complete');

    try {
        const response = await fetch('/api/form-entries', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        // Step 2: Database save
        updateProgress('database', 'complete');

        // Step 3: Pipeline execution
        if (result.pipeline) {
            updateProgress('pipeline', 'in-progress');

            // Simulate progress (or poll for real progress if available)
            await simulatePipelineProgress();

            if (result.pipeline.success) {
                updateProgress('pipeline', 'complete');
                updateProgress('documents', 'complete');

                // Show success
                showPipelineResult(result.pipeline);
            } else {
                updateProgress('pipeline', 'error');
                showPipelineError(result.pipeline.error);
            }
        }

    } catch (error) {
        showPipelineError(error.message);
    }
}

function updateProgress(phase, status) {
    const step = document.querySelector(\`[data-phase="\${phase}"]\`);
    const icon = step.querySelector('.icon');

    if (status === 'complete') {
        icon.textContent = '✅';
        step.classList.add('complete');
    } else if (status === 'error') {
        icon.textContent = '❌';
        step.classList.add('error');
    } else if (status === 'in-progress') {
        icon.textContent = '⏳';
        step.classList.add('in-progress');
    }
}

function showPipelineResult(pipeline) {
    document.getElementById('pipeline-progress').style.display = 'none';
    document.getElementById('pipeline-result').style.display = 'block';
    document.getElementById('execution-time').textContent = pipeline.executionTime;

    if (pipeline.phase_results && pipeline.phase_results.phase5) {
        document.getElementById('sets-generated').textContent =
            pipeline.phase_results.phase5.total_sets;
    }
}

function showPipelineError(error) {
    document.getElementById('pipeline-progress').style.display = 'none';
    document.getElementById('pipeline-error').style.display = 'block';
    document.getElementById('error-details').textContent = error;
}
\`\`\`

**CSS** (\`styles.css\`):
\`\`\`css
.modal {
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.7);
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-content {
    background-color: white;
    padding: 30px;
    border-radius: 10px;
    max-width: 500px;
    width: 90%;
}

.progress-step {
    padding: 15px;
    margin: 10px 0;
    border-left: 4px solid #ddd;
    transition: all 0.3s;
}

.progress-step.complete {
    border-left-color: #4CAF50;
    background-color: #f1f8f4;
}

.progress-step.error {
    border-left-color: #f44336;
    background-color: #fef1f0;
}

.progress-step.in-progress {
    border-left-color: #2196F3;
    background-color: #e3f2fd;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

#pipeline-details {
    background-color: #f5f5f5;
    padding: 15px;
    border-radius: 5px;
    margin: 15px 0;
}

.error-message {
    color: #f44336;
    font-family: monospace;
    background-color: #fef1f0;
    padding: 10px;
    border-radius: 5px;
}
\`\`\`

#### Testing
- [ ] Test with successful pipeline execution
- [ ] Test with pipeline timeout
- [ ] Test with pipeline error
- [ ] Test with webhook failure
- [ ] Verify on mobile devices
- [ ] Verify accessibility (screen readers)

---

### **Phase 4: Testing & Validation**
**Status**: Not Started
**Estimated Time**: 2-3 hours
**Dependencies**: Phase 3

#### Tasks
- [ ] Fix missing database issue options
- [ ] Test end-to-end form submission flow
- [ ] Test error scenarios
- [ ] Validate webhook delivery
- [ ] Performance testing
- [ ] Data integrity validation

#### Missing Database Options
Fix these missing issue options causing warnings:
\`\`\`sql
-- Add missing vermin options
INSERT INTO issue_options (category_id, option_name)
SELECT id, 'Skunks' FROM issue_categories WHERE category_code = 'vermin'
ON CONFLICT DO NOTHING;

INSERT INTO issue_options (category_id, option_name)
SELECT id, 'Bats' FROM issue_categories WHERE category_code = 'vermin'
ON CONFLICT DO NOTHING;

-- Add other missing options...
\`\`\`

---

### **Phase 5: Monitoring & Logging**
**Status**: Not Started
**Estimated Time**: 1-2 hours
**Dependencies**: Phase 4

#### Tasks
- [ ] Add structured logging to Python service
- [ ] Add structured logging to Node.js service
- [ ] Log pipeline metrics
- [ ] Track success/failure rates
- [ ] Add metrics endpoint
- [ ] Set up error alerting (optional)

---

### **Phase 6: Documentation Cleanup**
**Status**: Not Started
**Estimated Time**: 30 minutes
**Dependencies**: None (can be done anytime)

#### Tasks
- [ ] Create \`docs/archive/\` directory
- [ ] Archive old documentation files
- [ ] Update main README.md
- [ ] Create DEPLOYMENT.md
- [ ] Update CLAUDE.md project context

---

### **Phase 7: Environment & Security**
**Status**: Not Started
**Estimated Time**: 1 hour
**Dependencies**: Phase 4, 5

#### Tasks
- [ ] Move webhook credentials to environment variables
- [ ] Set up Secret Manager (for GCP)
- [ ] Add API key authentication between services
- [ ] Configure CORS properly
- [ ] Security audit

---

### **Phase 8: Docker & GCP Configuration**
**Status**: Not Started
**Estimated Time**: 1-2 hours
**Dependencies**: Phase 7

#### Tasks
- [ ] Create Dockerfile for Python service
- [ ] Create Dockerfile for Node.js service (if needed)
- [ ] Test Docker builds locally
- [ ] Create Cloud Run configuration
- [ ] Test containers locally

---

### **Phase 9: Deployment**
**Status**: Not Started
**Estimated Time**: 2-3 hours
**Dependencies**: Phase 8

#### Tasks
- [ ] Deploy Python service to Cloud Run
- [ ] Deploy Node.js service (or update existing)
- [ ] Configure Cloud SQL connection
- [ ] Test production deployment
- [ ] Configure DNS (if needed)

---

## Success Criteria

**Phase 3 Success:**
- ✅ Users see progress during form submission
- ✅ Pipeline status visible in UI
- ✅ Success/error messages clear
- ✅ Mobile-friendly design

**Overall Success:**
- ✅ Complete end-to-end flow working
- ✅ All tests passing
- ✅ Monitoring in place
- ✅ Deployed to production
- ✅ Documentation complete

---

## Timeline Estimate (Updated)

| Phase | Estimated Time | Dependencies |
|-------|---------------|--------------|
| ✅ Phase 1: Python API | 2.5 hours | None |
| ✅ Phase 2: Node.js Integration | 1.5 hours | Phase 1 |
| Phase 3: Frontend Status | 1-2 hours | Phase 2 |
| Phase 4: Testing & Validation | 2-3 hours | Phase 3 |
| Phase 5: Monitoring & Logging | 1-2 hours | Phase 4 |
| Phase 6: Documentation | 30 minutes | None |
| Phase 7: Environment & Security | 1 hour | Phase 4, 5 |
| Phase 8: Docker & GCP | 1-2 hours | Phase 7 |
| Phase 9: Deployment | 2-3 hours | Phase 8 |

**Completed**: 4 hours
**Remaining**: 10-16 hours
**Total**: 14-20 hours

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-17 | Initial plan created | Claude |
| 2025-10-17 | Phase 1 completed - FastAPI service | Claude |
| 2025-10-17 | Phase 2 completed - Node.js integration | Claude |
| 2025-10-17 | **Phases reordered** - "Stabilize & Polish First" strategy | Claude |

---

**Next**: Proceed with Phase 3 - Frontend Status Indicator
EOF

echo "✅ Created PIPELINE_INTEGRATION_PLAN_REORDERED.md"
echo ""
echo "📋 Summary of changes:"
echo "  - Updated Phase 2 status to COMPLETE"
echo "  - Added Phase 2 implementation details"
echo "  - Reordered phases 3-9 (Frontend moved up, Docker/GCP moved down)"
echo "  - Added rationale section explaining the reordering"
echo "  - Updated dependencies and timeline"
echo ""
echo "To apply changes:"
echo "  mv PIPELINE_INTEGRATION_PLAN_REORDERED.md PIPELINE_INTEGRATION_PLAN.md"
