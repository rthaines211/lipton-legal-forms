TITLE: Agentic AI Coder Briefing – React Hot Toast Integration Plan (ASCII-ONLY)

OBJECTIVE
Design and implement a single updating toast (react-hot-toast) showing async doc generation progress:
- Text: "Generating documents... (n/total)"
- Progress bar + percentage
- Auto-dismiss on success; sticky on error

FLOW (SEQUENCE)
1) User clicks "Generate"
2) POST /api/jobs -> { jobId, total }
3) Frontend opens progress stream to :8000
4) Worker emits absolute progress every 2-3 seconds
5) Toast updates (n/total, %)
6) On complete -> show Dropbox link; auto-dismiss (~6s)
7) On error -> stop; show sticky error toast

ENDPOINTS (CONTRACT)
- POST /api/jobs -> { jobId: string, total: number|null }
- GET /api/jobs/:jobId/stream (SSE)
  Events (absolute values, not deltas):
    progress: { jobId, current, total|null, message? }
    complete: { jobId, total, outputUrl }    // Dropbox link
    error: { jobId, code, message }

SSE NOTES
- Headers: Content-Type: text/event-stream; Cache-Control: no-cache
- Heartbeat: send a comment every 15-30s
- Reverse proxy: disable buffering; allow idle > 60s
- If job finishes between ticks: emit a final "complete"

TOAST UX SPEC
- One toast per jobId (update in place using a stable toast ID)
- Progress text: "Generating documents... (n/total)"; if total unknown, show indeterminate bar
- Success text: "All documents generated (total/total)" + [Open in Dropbox]; auto-dismiss ~6s (configurable)
- Error text: "Generation failed: <reason>"; sticky (manual close)
- Accessibility: polite live region; announce start, every 5 increments, and completion/error (throttled)

STATE / PERSISTENCE / RESILIENCE
- Client state per jobId: { jobId, current, total, status: in_progress|complete|error, outputUrl? }
- Persist minimal state in localStorage; on reload, rehydrate and re-subscribe
- Reconnect backoff: 1s -> 2s -> 4s -> 8s -> 10s (cap)
- Show "Reconnecting..." after 10s silence; give up at 2 minutes with error
- Idempotency: only increase "current"; ignore duplicates/regressions

ERROR HANDLING
- First "error" event: stop stream; show sticky error toast
- Unknown totals: start indeterminate; switch to determinate when total arrives (do not reset current)
- Transport silence > 20s: show "Connection lost, attempting to reconnect..."

PERFORMANCE & OPERATIONS TARGETS
- UI update latency after event: < 200ms
- No memory leaks (clean up EventSource)
- Event throughput tolerance: ~10k/hour
- SSE heartbeat: every 15-30s
- Max concurrent toasts visible: 5
- No PII in events

TESTING PLAN (SCENARIOS)
- Happy path: updates every 2-3s -> complete -> auto-dismiss
- Error mid-run: sticky error toast; stream stops
- Unknown->known total: indeterminate->determinate transition; percent correct
- Page refresh mid-job: rehydrate and resume within 2s
- Multiple jobs: independent toasts, keyed by jobId
- Transport drop: reconnect idempotently; no double counts
- Out-of-order and duplicate progress events: ignored; regressions ignored
- Instant completion (no interim events): show success then auto-dismiss

NON-FUNCTIONAL ACCEPTANCE CRITERIA
- First visible progress <= 3s after start
- Completion reflected in UI <= 2s after final event
- Success auto-dismiss ~6s (configurable)
- Error toast persists until dismissed
- Refresh recovery <= 2s
- Accessibility: polite live region; throttled announcements

ERROR TAXONOMY (CODES)
- GENERATOR_TIMEOUT          // worker took too long
- TEMPLATE_ERROR             // invalid or missing template
- STORAGE_WRITE_FAIL         // could not save output
- STREAM_DISCONNECTED        // progress stream lost
- UNKNOWN_TOTAL_TIMEOUT      // total never received
- UNEXPECTED                 // generic fallback
