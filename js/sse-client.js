/**
 * SSE Client Module
 * 
 * Manages Server-Sent Events connections with automatic reconnection,
 * error handling, and state persistence for job progress tracking.
 * 
 * @module SSEClient
 */

// Use global variables instead of ES6 imports
// These will be available after the scripts are loaded

/**
 * Job Progress Stream Manager
 * Handles SSE connections with reconnection logic and error handling
 */
class JobProgressStream {
    constructor(jobId, sseUrl = 'http://localhost:8000') {
        this.jobId = jobId;
        this.sseUrl = `${sseUrl}/api/jobs/${jobId}/stream`;
        this.eventSource = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 6; // 1s, 2s, 4s, 8s, 10s, 10s = ~2 minutes
        this.reconnectDelays = [1000, 2000, 4000, 8000, 10000, 10000];
        this.silenceTimeout = null;
        this.silenceThreshold = 20000; // 20 seconds
        this.lastEventTime = Date.now();
        this.isDestroyed = false;
        
        // Event handlers
        this.onProgress = null;
        this.onComplete = null;
        this.onError = null;
        this.onReconnect = null;
        
        console.log(`🔌 Initializing SSE stream for job: ${jobId}`);
    }
    
    /**
     * Connect to SSE stream
     */
    connect() {
        if (this.isDestroyed) {
            console.warn(`SSE stream for ${this.jobId} is destroyed, cannot connect`);
            return;
        }
        
        try {
            this.eventSource = new EventSource(this.sseUrl);
            this.setupEventHandlers();
            this.startSilenceDetection();
            console.log(`📡 Connected to SSE stream: ${this.sseUrl}`);
        } catch (error) {
            console.error(`Failed to create SSE connection for ${this.jobId}:`, error);
            this.handleConnectionError();
        }
    }
    
    /**
     * Setup SSE event handlers
     */
    setupEventHandlers() {
        if (!this.eventSource) return;
        
        // Handle connection open
        this.eventSource.onopen = (event) => {
            console.log(`✅ SSE connection opened for ${this.jobId}`);
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.lastEventTime = Date.now();
            
            // Show reconnecting toast if we were reconnecting
            if (this.reconnectAttempts > 0) {
                progressToast.dismissProgress(this.jobId);
                progressToast.showProgress(this.jobId, 0, 0, 'Reconnected - resuming progress...');
            }
            
            if (this.onReconnect) {
                this.onReconnect();
            }
        };
        
        // Handle progress events
        this.eventSource.addEventListener('progress', (event) => {
            this.handleProgressEvent(event);
        });
        
        // Handle completion events
        this.eventSource.addEventListener('complete', (event) => {
            this.handleCompleteEvent(event);
        });
        
        // Handle error events
        this.eventSource.addEventListener('error', (event) => {
            this.handleErrorEvent(event);
        });
        
        // Handle connection errors
        this.eventSource.onerror = (event) => {
            console.error(`SSE connection error for ${this.jobId}:`, event);
            this.handleConnectionError();
        };
        
        // Handle connection close
        this.eventSource.onclose = (event) => {
            console.log(`SSE connection closed for ${this.jobId}`);
            this.isConnected = false;
        };
    }
    
    /**
     * Handle progress events
     * @param {MessageEvent} event - SSE progress event
     */
    handleProgressEvent(event) {
        try {
            const data = JSON.parse(event.data);
            console.log(`📊 Progress update for ${this.jobId}:`, data);
            
            this.lastEventTime = Date.now();
            
            // Update progress state
            if (typeof updateJobProgress === 'function') {
                updateJobProgress(this.jobId, data.current, data.total, data.message);
            }
            
            // Show progress toast
            if (typeof progressToast !== 'undefined' && progressToast.showProgress) {
                progressToast.showProgress(this.jobId, data.current, data.total, data.message);
            }
            
            // Call custom progress handler
            if (this.onProgress) {
                this.onProgress(data);
            }
        } catch (error) {
            console.error(`Failed to parse progress event for ${this.jobId}:`, error);
        }
    }
    
    /**
     * Handle completion events
     * @param {MessageEvent} event - SSE completion event
     */
    handleCompleteEvent(event) {
        try {
            const data = JSON.parse(event.data);
            console.log(`✅ Job completed for ${this.jobId}:`, data);
            
            // Update progress state
            if (typeof markJobComplete === 'function') {
                markJobComplete(this.jobId, data.total, data.outputUrl);
            }
            
            // Show success toast
            if (typeof progressToast !== 'undefined' && progressToast.showSuccess) {
                progressToast.showSuccess(this.jobId, data.total, data.outputUrl);
            }
            
            // Call custom completion handler
            if (this.onComplete) {
                this.onComplete(data);
            }
            
            // Close connection after completion
            this.close();
        } catch (error) {
            console.error(`Failed to parse completion event for ${this.jobId}:`, error);
        }
    }
    
    /**
     * Handle error events
     * @param {MessageEvent} event - SSE error event
     */
    handleErrorEvent(event) {
        try {
            const data = JSON.parse(event.data);
            console.error(`❌ Job failed for ${this.jobId}:`, data);
            
            // Update progress state
            if (typeof markJobFailed === 'function') {
                markJobFailed(this.jobId, data.code, data.message);
            }
            
            // Show error toast
            if (typeof progressToast !== 'undefined' && progressToast.showError) {
                progressToast.showError(this.jobId, data.code, data.message);
            }
            
            // Call custom error handler
            if (this.onError) {
                this.onError(data);
            }
            
            // Close connection after error
            this.close();
        } catch (error) {
            console.error(`Failed to parse error event for ${this.jobId}:`, error);
        }
    }
    
    /**
     * Handle connection errors with reconnection logic
     */
    handleConnectionError() {
        this.isConnected = false;
        
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error(`Max reconnection attempts reached for ${this.jobId}`);
            this.showConnectionFailed();
            return;
        }
        
        const delay = this.reconnectDelays[this.reconnectAttempts];
        this.reconnectAttempts++;
        
        console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        // Show reconnecting toast
        if (typeof progressToast !== 'undefined' && progressToast.showProgress) {
            progressToast.showProgress(this.jobId, 0, 0, 'Connection lost, attempting to reconnect...');
        }
        
        setTimeout(() => {
            if (!this.isDestroyed) {
                this.connect();
            }
        }, delay);
    }
    
    /**
     * Start silence detection to detect connection issues
     */
    startSilenceDetection() {
        this.clearSilenceTimeout();
        
        this.silenceTimeout = setInterval(() => {
            const timeSinceLastEvent = Date.now() - this.lastEventTime;
            
            if (timeSinceLastEvent > this.silenceThreshold && this.isConnected) {
                console.warn(`SSE silence detected for ${this.jobId} (${timeSinceLastEvent}ms)`);
                this.handleConnectionError();
            }
        }, 5000); // Check every 5 seconds
    }
    
    /**
     * Clear silence detection timeout
     */
    clearSilenceTimeout() {
        if (this.silenceTimeout) {
            clearInterval(this.silenceTimeout);
            this.silenceTimeout = null;
        }
    }
    
    /**
     * Show connection failed error
     */
    showConnectionFailed() {
        if (typeof progressToast !== 'undefined' && progressToast.showError) {
            progressToast.showError(
                this.jobId,
                'STREAM_DISCONNECTED',
                'Unable to maintain connection. Please refresh the page to retry.'
            );
        }
    }
    
    /**
     * Close SSE connection
     */
    close() {
        console.log(`🔌 Closing SSE connection for ${this.jobId}`);
        this.isDestroyed = true;
        this.clearSilenceTimeout();
        
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
        
        this.isConnected = false;
    }
    
    /**
     * Reconnect to SSE stream
     */
    reconnect() {
        console.log(`🔄 Manual reconnect requested for ${this.jobId}`);
        this.close();
        this.reconnectAttempts = 0;
        this.isDestroyed = false;
        this.connect();
    }
    
    /**
     * Check if connection is active
     * @returns {boolean} True if connected
     */
    isActive() {
        return this.isConnected && !this.isDestroyed;
    }
    
    /**
     * Get connection status
     * @returns {Object} Connection status information
     */
    getStatus() {
        return {
            jobId: this.jobId,
            isConnected: this.isConnected,
            reconnectAttempts: this.reconnectAttempts,
            lastEventTime: this.lastEventTime,
            isDestroyed: this.isDestroyed
        };
    }
}

/**
 * Create and manage SSE connection for a job
 * @param {string} jobId - Unique job identifier
 * @param {string} sseUrl - SSE server URL (optional)
 * @returns {JobProgressStream} SSE stream instance
 */
function createJobStream(jobId, sseUrl = 'http://localhost:8000') {
    return new JobProgressStream(jobId, sseUrl);
}

// Make available globally
if (typeof window !== 'undefined') {
    console.log('📡 Loading sse-client.js');
    window.JobProgressStream = JobProgressStream;
    window.createJobStream = createJobStream;
    console.log('✅ sse-client.js loaded successfully');
}
