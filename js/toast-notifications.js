/**
 * Toast Notifications Module
 *
 * Provides beautiful toast notifications using Notyf library.
 * Manages progress toasts with real-time updates and accessibility features.
 *
 * Updated: 2025-10-20
 * - Enhanced progress toast to show granular document generation details
 * - Now displays: document name, processing phase, and status message
 * - Added percentage display for better progress visibility
 * - Supports both simple string messages and detailed status objects
 * - Format: "📄 Document Name • ⚙️ Phase Name • Status Message"
 * - Added Dropbox folder link in success notification (if available)
 * - Clickable link to view all generated documents at address level
 * - Example: "📁 View documents in Dropbox →" opens /Current Clients/{address}
 *
 * Progress Message Formats Supported:
 * 1. Simple string: "Processing documents..."
 * 2. Detailed object: { current_doc: "SROG Set 1", phase: "Formatting", message: "Applying styles" }
 *
 * Success Notification:
 * - Displays completion count: "All documents generated! (4/4)"
 * - If Dropbox link provided: Shows clickable link to address-level folder
 * - Auto-dismisses after 12 seconds (with link) or 6 seconds (without link)
 *
 * @module ToastNotifications
 */

// Use Notyf from CDN (loaded via script tag)
// Notyf is already available globally from the CDN script

/**
 * Progress Toast Manager
 * Handles single updating toast per job with progress bar and status
 */
class ProgressToast {
    constructor() {
        // Initialize Notyf with custom configuration
        this.notyf = new window.Notyf({
            duration: 0, // Don't auto-dismiss progress toasts
            position: {
                x: 'right',
                y: 'bottom'
            },
            types: [
                {
                    type: 'progress',
                    background: '#00AEEF',
                    icon: {
                        className: 'fas fa-spinner fa-spin',
                        tagName: 'i'
                    }
                },
                {
                    type: 'success',
                    background: '#059669',
                    icon: {
                        className: 'fas fa-check-circle',
                        tagName: 'i'
                    }
                },
                {
                    type: 'error',
                    background: '#DC2626',
                    icon: {
                        className: 'fas fa-exclamation-circle',
                        tagName: 'i'
                    }
                }
            ],
            dismissible: true,
            ripple: true
        });
        
        // Track active toasts by job ID
        this.activeToasts = new Map();
        
        // Accessibility: Create live region for screen readers
        this.createLiveRegion();
        
        // Throttled announcements for screen readers
        this.lastAnnouncement = 0;
        this.announcementThrottle = 5000; // 5 seconds
    }
    
    /**
     * Create ARIA live region for screen reader announcements
     */
    createLiveRegion() {
        if (!document.getElementById('toast-live-region')) {
            const liveRegion = document.createElement('div');
            liveRegion.id = 'toast-live-region';
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.setAttribute('aria-atomic', 'true');
            liveRegion.style.position = 'absolute';
            liveRegion.style.left = '-10000px';
            liveRegion.style.width = '1px';
            liveRegion.style.height = '1px';
            liveRegion.style.overflow = 'hidden';
            document.body.appendChild(liveRegion);
        }
    }
    
    /**
     * Announce progress to screen readers (throttled)
     * @param {string} message - Message to announce
     */
    announceToScreenReader(message) {
        const now = Date.now();
        if (now - this.lastAnnouncement < this.announcementThrottle) {
            return;
        }
        
        const liveRegion = document.getElementById('toast-live-region');
        if (liveRegion) {
            liveRegion.textContent = message;
            this.lastAnnouncement = now;
        }
    }
    
    /**
     * Show progress toast for a job with granular detail
     * @param {string} jobId - Unique job identifier
     * @param {number} current - Current progress count
     * @param {number} total - Total progress count
     * @param {string|object} message - Progress message or detailed status object
     */
    showProgress(jobId, current, total, message) {
        const percentage = total > 0 ? Math.round((current / total) * 100) : 0;
        const progressText = total > 0 ? `${current}/${total}` : 'Processing...';

        // Parse detailed progress information if available
        let detailedMessage = message;
        let currentDocument = '';
        let currentPhase = '';

        // If message is an object with detailed info, extract it
        if (typeof message === 'object' && message !== null) {
            currentDocument = message.current_doc || message.document || '';
            currentPhase = message.phase || message.step || '';
            detailedMessage = message.message || message.status || '';
        } else if (typeof message === 'string') {
            detailedMessage = message;
        }

        // Create granular status display
        const statusDetails = [];
        if (currentDocument) {
            statusDetails.push(`📄 ${currentDocument}`);
        }
        if (currentPhase) {
            statusDetails.push(`⚙️ ${currentPhase}`);
        }
        if (detailedMessage && detailedMessage !== currentDocument) {
            statusDetails.push(detailedMessage);
        }

        const statusText = statusDetails.length > 0
            ? statusDetails.join(' • ')
            : 'Processing your request...';

        // Create progress bar HTML
        const progressBar = total > 0 ?
            `<div class="progress-bar-container" style="
                width: 100%;
                height: 4px;
                background-color: rgba(255,255,255,0.3);
                border-radius: 2px;
                margin-top: 8px;
                overflow: hidden;
            ">
                <div class="progress-bar-fill" style="
                    width: ${percentage}%;
                    height: 100%;
                    background-color: #ffffff;
                    border-radius: 2px;
                    transition: width 0.3s ease;
                "></div>
            </div>` : '';

        const toastContent = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="flex: 1;">
                    <div style="font-weight: 600; margin-bottom: 4px;">
                        Documents (${progressText})${percentage > 0 ? ` - ${percentage}%` : ''}
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.9; line-height: 1.4;">
                        ${statusText}
                    </div>
                    ${progressBar}
                </div>
            </div>
        `;
        
        // Update existing toast or create new one
        if (this.activeToasts.has(jobId)) {
            const existingToast = this.activeToasts.get(jobId);
            // Update the toast content
            const toastElement = document.querySelector(`[data-job-id="${jobId}"]`);
            if (toastElement) {
                const contentElement = toastElement.querySelector('.notyf__message');
                if (contentElement) {
                    contentElement.innerHTML = toastContent;
                }
            }
        } else {
            // Create new toast
            const toast = this.notyf.open({
                type: 'progress',
                message: toastContent,
                duration: 0 // Don't auto-dismiss
            });
            
            // Add job ID to toast element for updates
            setTimeout(() => {
                const toastElement = document.querySelector('.notyf__toast:last-child');
                if (toastElement) {
                    toastElement.setAttribute('data-job-id', jobId);
                }
            }, 100);
            
            this.activeToasts.set(jobId, toast);
        }
        
        // Announce to screen readers (throttled)
        if (current % 5 === 0 || current === total) {
            this.announceToScreenReader(`Document generation progress: ${progressText} (${percentage}%)`);
        }
    }
    
    /**
     * Show success toast for completed job
     * @param {string} jobId - Unique job identifier
     * @param {number} total - Total documents generated
     * @param {string} outputUrl - Output URL (optional)
     */
    showSuccess(jobId, total, outputUrl = '') {
        // Dismiss progress toast
        this.dismissProgress(jobId);

        // Build Dropbox link section if URL provided
        const dropboxLinkHtml = outputUrl ? `
            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.2);">
                <a href="${outputUrl}"
                   target="_blank"
                   rel="noopener noreferrer"
                   style="
                       color: white;
                       text-decoration: none;
                       display: inline-flex;
                       align-items: center;
                       gap: 6px;
                       font-weight: 500;
                   "
                   onmouseover="this.style.textDecoration='underline'"
                   onmouseout="this.style.textDecoration='none'">
                    <span style="font-size: 1.1em;">📁</span>
                    <span>View documents in Dropbox</span>
                    <span style="font-size: 0.9em;">→</span>
                </a>
            </div>
        ` : '';

        const successMessage = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="flex: 1;">
                    <div style="font-weight: 600; margin-bottom: 4px;">
                        All documents generated! (${total}/${total})
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.9;">
                        Your legal documents are ready for review.
                    </div>
                    ${dropboxLinkHtml}
                </div>
            </div>
        `;

        // Longer duration if link provided (to give time to click)
        const duration = outputUrl ? 12000 : 6000;

        const toast = this.notyf.open({
            type: 'success',
            message: successMessage,
            duration: duration
        });

        // Announce completion to screen readers
        const announcement = outputUrl
            ? `Document generation complete: ${total} documents generated successfully. Dropbox link available.`
            : `Document generation complete: ${total} documents generated successfully`;
        this.announceToScreenReader(announcement);

        // Clean up after auto-dismiss
        setTimeout(() => {
            this.activeToasts.delete(jobId);
        }, duration);
    }
    
    /**
     * Show error toast for failed job
     * @param {string} jobId - Unique job identifier
     * @param {string} errorCode - Error code
     * @param {string} errorMessage - Error message
     */
    showError(jobId, errorCode, errorMessage) {
        // Dismiss progress toast
        this.dismissProgress(jobId);
        
        const errorMessages = {
            'GENERATOR_TIMEOUT': 'Document generation timed out',
            'TEMPLATE_ERROR': 'Template processing error',
            'STORAGE_WRITE_FAIL': 'Failed to save documents',
            'STREAM_DISCONNECTED': 'Connection lost',
            'UNKNOWN_TOTAL_TIMEOUT': 'Progress tracking timeout',
            'UNEXPECTED': 'Unexpected error occurred'
        };
        
        const friendlyMessage = errorMessages[errorCode] || 'Document generation failed';
        
        const errorToastMessage = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="flex: 1;">
                    <div style="font-weight: 600; margin-bottom: 4px;">
                        Generation failed: ${friendlyMessage}
                    </div>
                    <div style="font-size: 0.9em; opacity: 0.9;">
                        ${errorMessage || 'Please try again or contact support.'}
                    </div>
                </div>
            </div>
        `;
        
        const toast = this.notyf.open({
            type: 'error',
            message: errorToastMessage,
            duration: 0 // Sticky - don't auto-dismiss
        });
        
        // Announce error to screen readers
        this.announceToScreenReader(`Document generation failed: ${friendlyMessage}`);
        
        // Keep error toast active
        this.activeToasts.set(jobId, toast);
    }
    
    /**
     * Dismiss progress toast for a job
     * @param {string} jobId - Unique job identifier
     */
    dismissProgress(jobId) {
        if (this.activeToasts.has(jobId)) {
            const toast = this.activeToasts.get(jobId);
            this.notyf.dismiss(toast);
            this.activeToasts.delete(jobId);
        }
    }
    
    /**
     * Dismiss all toasts for a job
     * @param {string} jobId - Unique job identifier
     */
    dismissAll(jobId) {
        this.dismissProgress(jobId);
    }
    
    /**
     * Get active toast count
     * @returns {number} Number of active toasts
     */
    getActiveCount() {
        return this.activeToasts.size;
    }
    
    /**
     * Check if job has active toast
     * @param {string} jobId - Unique job identifier
     * @returns {boolean} True if job has active toast
     */
    hasActiveToast(jobId) {
        return this.activeToasts.has(jobId);
    }
}

// Create global instance
const progressToast = new ProgressToast();

// Make available globally
if (typeof window !== 'undefined') {
    console.log('🍞 Loading toast-notifications.js');
    window.ProgressToast = ProgressToast;
    window.progressToast = progressToast;
    console.log('✅ toast-notifications.js loaded successfully');
}
