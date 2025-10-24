/**
 * Progress State Management Module
 * 
 * Handles localStorage persistence for job progress state.
 * Provides TTL (Time To Live) for abandoned jobs and state recovery.
 * 
 * @module ProgressState
 */

/**
 * Save job state to localStorage with TTL
 * @param {string} jobId - Unique job identifier
 * @param {number} current - Current progress count
 * @param {number} total - Total progress count
 * @param {string} status - Job status (pending, in_progress, complete, error)
 * @param {string} outputUrl - Output URL for completed jobs (optional)
 */
function saveJobState(jobId, current, total, status, outputUrl = null) {
    const state = {
        jobId,
        current,
        total,
        status,
        outputUrl,
        timestamp: Date.now(),
        ttl: 15 * 60 * 1000 // 15 minutes TTL
    };
    
    try {
        const key = `job_${jobId}`;
        localStorage.setItem(key, JSON.stringify(state));
        console.log(`💾 Saved job state for ${jobId}: ${current}/${total} (${status})`);
    } catch (error) {
        console.warn('Failed to save job state to localStorage:', error);
    }
}

/**
 * Get job state from localStorage
 * @param {string} jobId - Unique job identifier
 * @returns {Object|null} Job state object or null if not found/expired
 */
function getJobState(jobId) {
    try {
        const key = `job_${jobId}`;
        const stored = localStorage.getItem(key);
        
        if (!stored) {
            return null;
        }
        
        const state = JSON.parse(stored);
        
        // Check if expired
        if (Date.now() - state.timestamp > state.ttl) {
            console.log(`⏰ Job state expired for ${jobId}, removing from localStorage`);
            localStorage.removeItem(key);
            return null;
        }
        
        return state;
    } catch (error) {
        console.warn('Failed to get job state from localStorage:', error);
        return null;
    }
}

/**
 * Clear job state from localStorage
 * @param {string} jobId - Unique job identifier
 */
function clearJobState(jobId) {
    try {
        const key = `job_${jobId}`;
        localStorage.removeItem(key);
        console.log(`🗑️ Cleared job state for ${jobId}`);
    } catch (error) {
        console.warn('Failed to clear job state from localStorage:', error);
    }
}

/**
 * Get all active jobs from localStorage
 * @returns {Array} Array of active job states
 */
function getActiveJobs() {
    const activeJobs = [];
    
    try {
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            
            if (key && key.startsWith('job_')) {
                const jobId = key.replace('job_', '');
                const state = getJobState(jobId);
                
                if (state && (state.status === 'pending' || state.status === 'in_progress')) {
                    activeJobs.push(state);
                }
            }
        }
    } catch (error) {
        console.warn('Failed to get active jobs from localStorage:', error);
    }
    
    return activeJobs;
}

/**
 * Clean up expired jobs from localStorage
 */
function cleanupExpiredJobs() {
    const cleaned = [];
    
    try {
        for (let i = localStorage.length - 1; i >= 0; i--) {
            const key = localStorage.key(i);
            
            if (key && key.startsWith('job_')) {
                const jobId = key.replace('job_', '');
                const state = getJobState(jobId);
                
                if (!state) {
                    // State was expired and removed by getJobState
                    cleaned.push(jobId);
                }
            }
        }
    } catch (error) {
        console.warn('Failed to cleanup expired jobs:', error);
    }
    
    if (cleaned.length > 0) {
        console.log(`🧹 Cleaned up ${cleaned.length} expired jobs:`, cleaned);
    }
    
    return cleaned;
}

/**
 * Update job progress
 * @param {string} jobId - Unique job identifier
 * @param {number} current - Current progress count
 * @param {number} total - Total progress count
 * @param {string} message - Progress message
 */
function updateJobProgress(jobId, current, total, message = '') {
    const existingState = getJobState(jobId);
    const status = existingState ? existingState.status : 'in_progress';
    
    saveJobState(jobId, current, total, status, existingState?.outputUrl);
}

/**
 * Mark job as complete
 * @param {string} jobId - Unique job identifier
 * @param {number} total - Total progress count
 * @param {string} outputUrl - Output URL
 */
function markJobComplete(jobId, total, outputUrl = '') {
    saveJobState(jobId, total, total, 'complete', outputUrl);
}

/**
 * Mark job as failed
 * @param {string} jobId - Unique job identifier
 * @param {string} errorCode - Error code
 * @param {string} errorMessage - Error message
 */
function markJobFailed(jobId, errorCode, errorMessage) {
    const existingState = getJobState(jobId);
    const current = existingState ? existingState.current : 0;
    const total = existingState ? existingState.total : 0;
    
    saveJobState(jobId, current, total, 'error', null);
}

// Clean up expired jobs on module load
cleanupExpiredJobs();

// Make available globally
if (typeof window !== 'undefined') {
    console.log('📦 Loading progress-state.js');
    window.saveJobState = saveJobState;
    window.getJobState = getJobState;
    window.clearJobState = clearJobState;
    window.getActiveJobs = getActiveJobs;
    window.cleanupExpiredJobs = cleanupExpiredJobs;
    window.updateJobProgress = updateJobProgress;
    window.markJobComplete = markJobComplete;
    window.markJobFailed = markJobFailed;
    console.log('✅ progress-state.js loaded successfully');
}
