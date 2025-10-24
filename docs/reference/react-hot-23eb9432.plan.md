<!-- 23eb9432-5e31-41db-be44-8b43daf32d94 4a691ba5-ead9-4f3b-88f1-255f00ad79d5 -->
# React Hot Toast SSE Integration Plan

## Overview

Implement real-time document generation progress notifications using Server-Sent Events (SSE) and Notyf toast library. This replaces the current HTTP polling mechanism with a streaming architecture for better UX and reduced server load.

## Architecture Changes

### Current Flow

```
Browser → Node.js :3000 → Python :8000 (pipeline)
   ↑         ↓
   └─ Poll every 2s ─┘
```

### New Flow (SSE)

```
Browser ──SSE──→ Python :8000 (direct stream)
   ↓
Node.js :3000 (form submission only)
```

## Implementation Steps

### Phase 1: Python API - SSE Endpoint (Port 8000)

**File**: `/normalization work/api/routes.py`

Add SSE streaming endpoint:

- Create `@router.get("/api/jobs/{job_id}/stream")` endpoint
- Use `StreamingResponse` from FastAPI with `media_type="text/event-stream"`
- Stream progress events from `_progress_cache` in real-time
- Emit events: `progress`, `complete`, `error`
- Add heartbeat comments every 15-30s to keep connection alive
- Handle client disconnection gracefully

**Event Format**:

```
event: progress
data: {"jobId":"case-123","current":5,"total":32,"message":"Generating SROGS 1/3"}

event: complete
data: {"jobId":"case-123","total":32,"outputUrl":"https://dropbox.com/..."}

event: error
data: {"jobId":"case-123","code":"TEMPLATE_ERROR","message":"..."}
```

**File**: `/normalization work/src/phase5/webhook_sender.py`

Enhance progress tracking:

- Modify `update_progress()` to support event broadcasting
- Add event queue mechanism for SSE consumers
- Store Dropbox URL in progress cache on completion
- Add error event support with taxonomy codes

### Phase 2: Frontend - Notyf Toast Integration

**File**: `package.json`

Add Notyf dependency:

```json
"dependencies": {
  "notyf": "^3.10.0"
}
```

**File**: `js/toast-notifications.js` (NEW)

Create toast notification module:

- Initialize Notyf with custom configuration (duration, position, ripple)
- Create `ProgressToast` class to manage single updating toast per job
- Implement `showProgress(jobId, current, total, message)` method
- Implement `showSuccess(jobId, total, dropboxUrl)` with auto-dismiss (6s)
- Implement `showError(jobId, code, message)` as sticky toast
- Add progress bar rendering (HTML injection into toast)
- Implement accessibility: ARIA live regions, throttled announcements

**File**: `js/sse-client.js` (NEW)

Create SSE client module:

- Implement `JobProgressStream` class
- Connect to `http://localhost:8000/api/jobs/{jobId}/stream`
- Handle `progress`, `complete`, `error` events
- Implement reconnection with exponential backoff (1s, 2s, 4s, 8s, 10s cap)
- Implement silence detection (20s timeout → show reconnecting toast)
- Implement max retry limit (2 minutes → show error toast)
- Persist state in `localStorage` for page refresh recovery
- Implement idempotency: ignore duplicate/regressed progress values

**File**: `js/form-submission.js`

Update form submission flow:

- After successful POST to `/api/form-entries`, extract `dbCaseId`
- Initialize `JobProgressStream` with `dbCaseId`
- Initialize `ProgressToast` for the job
- Wire SSE events to toast methods
- Clean up EventSource on completion/error
- Handle page refresh: rehydrate from localStorage and reconnect

**File**: `index.html`

Add Notyf CSS and module imports:

```html
<link rel="stylesheet" href="node_modules/notyf/notyf.min.css">
<script type="module" src="js/toast-notifications.js"></script>
<script type="module" src="js/sse-client.js"></script>
```

### Phase 3: Node.js Server - Remove Polling

**File**: `server.js`

Simplify progress tracking:

- **Remove**: `progressInterval` polling code (lines 994-1032)
- **Keep**: Pipeline status cache for backward compatibility
- **Keep**: `/api/pipeline-status/:caseId` endpoint for legacy support
- Update response to include SSE endpoint URL in metadata
- Add CORS headers for SSE requests from browser

### Phase 4: Progress State Management

**File**: `js/progress-state.js` (NEW)

Create state persistence module:

- `saveJobState(jobId, current, total, status, outputUrl?)`
- `getJobState(jobId)` - retrieve from localStorage
- `clearJobState(jobId)` - cleanup on completion
- `getActiveJobs()` - list all in-progress jobs
- Implement TTL (15 minutes) for abandoned jobs

### Phase 5: Error Handling & Resilience

**Error Taxonomy** (as per spec):

- `GENERATOR_TIMEOUT` - Worker timeout
- `TEMPLATE_ERROR` - Invalid/missing template
- `STORAGE_WRITE_FAIL` - Dropbox/storage error
- `STREAM_DISCONNECTED` - SSE connection lost
- `UNKNOWN_TOTAL_TIMEOUT` - Total never received
- `UNEXPECTED` - Generic fallback

**Reconnection Logic**:

- Exponential backoff: 1s → 2s → 4s → 8s → 10s (cap)
- Show "Reconnecting..." toast after 10s silence
- Give up after 2 minutes with error toast
- Resume from last known progress (idempotent)

### Phase 6: Testing

**File**: `tests/test-sse-integration.spec.js` (NEW)

Playwright tests:

1. Happy path: Submit form → progress updates → complete → auto-dismiss
2. Error mid-run: Progress updates → error event → sticky toast
3. Unknown total: Indeterminate → determinate transition
4. Page refresh: Reload during progress → rehydrate → resume
5. Multiple jobs: Submit 2 forms → independent toasts
6. Connection drop: Kill Python server → reconnect → resume
7. Duplicate events: Send same progress twice → no UI flash
8. Instant completion: Complete before first progress → show success

## Key Files to Modify/Create

### New Files

- `js/toast-notifications.js` - Notyf wrapper with progress support
- `js/sse-client.js` - EventSource manager with reconnection
- `js/progress-state.js` - localStorage persistence
- `tests/test-sse-integration.spec.js` - E2E tests

### Modified Files

- `normalization work/api/routes.py` - Add SSE endpoint
- `normalization work/src/phase5/webhook_sender.py` - Enhanced progress tracking
- `server.js` - Remove polling, add SSE metadata
- `js/form-submission.js` - Wire SSE to form flow
- `index.html` - Add Notyf CSS and scripts
- `package.json` - Add Notyf dependency

## Performance Targets (per spec)

- UI update latency: < 200ms after event
- First visible progress: ≤ 3s after start
- Completion reflected: ≤ 2s after final event
- Success auto-dismiss: ~6s (configurable)
- Refresh recovery: ≤ 2s
- Event throughput: ~10k/hour tolerance
- Max concurrent toasts: 5

## Accessibility Requirements

- ARIA live regions with `aria-live="polite"`
- Announce: start, every 5 increments, completion/error
- Throttle announcements to avoid spam
- Keyboard dismissible (ESC key)
- High contrast mode compatible

## Non-Functional Requirements

- No memory leaks (clean up EventSource)
- No PII in SSE events
- Graceful degradation if SSE unavailable
- Support for multiple simultaneous jobs
- Browser compatibility: Chrome, Firefox, Safari, Edge (modern)

## Rollout Strategy

1. Deploy Python SSE endpoint first (backward compatible)
2. Deploy frontend changes with feature flag
3. Test with small user group
4. Monitor error rates and connection stability
5. Full rollout after 1 week observation
6. Deprecate polling after 2 weeks (remove in next release)

### To-dos

- [ ] Add SSE streaming endpoint to Python FastAPI (/api/jobs/{job_id}/stream)
- [ ] Enhance webhook_sender.py progress tracking with event broadcasting and Dropbox URL storage
- [ ] Add Notyf dependency to package.json and install
- [ ] Create js/toast-notifications.js with ProgressToast class and Notyf integration
- [ ] Create js/sse-client.js with JobProgressStream class, reconnection logic, and error handling
- [ ] Create js/progress-state.js for localStorage persistence and state recovery
- [ ] Update js/form-submission.js to initialize SSE connection and wire toast events
- [ ] Add Notyf CSS and module script imports to index.html
- [ ] Remove polling code from server.js and add SSE metadata to responses
- [ ] Create tests/test-sse-integration.spec.js with 8 test scenarios