/**
 * Form Submission Module
 *
 * Handles form submission, validation, and API communication with the backend.
 * Implements optimized fetch requests with proper error handling and retry logic.
 *
 * Updated: 2025-10-20
 * - Removed success page redirect - form now resets immediately after submission
 * - Added inline success alert notification with case ID
 * - Form resets to clean state with 1 plaintiff and 1 defendant
 * - Background document generation continues without blocking user
 * - Maintains SSE progress tracking for document generation status
 *
 * Performance Features:
 * - Async/await for non-blocking operations
 * - Request timeout handling
 * - Exponential backoff for retries
 * - Optimistic UI updates
 * - Non-blocking form reset (documents generate in background)
 *
 * Key Functions:
 * - submitForm(notificationEmail, optedIn): Main submission handler
 * - showReviewScreen(): Displays confirmation modal
 * - confirmSubmission(): Validates and submits after confirmation
 * - handleSubmissionSuccess(data): Handles successful submission and triggers form reset
 * - resetFormAfterSubmission(result): Resets form to initial state
 * - handleSubmissionError(error): Handles submission failures
 *
 * User Flow:
 * 1. User fills out form
 * 2. Clicks "Submit Form" → Confirmation modal appears
 * 3. Clicks "Confirm & Submit" → Email notification modal appears
 * 4. User provides email or skips → Form submits to server
 * 5. Success alert displays with case ID
 * 6. Form immediately resets to clean state
 * 7. Documents generate in background (non-blocking)
 * 8. User can start new submission immediately
 *
 * @module FormSubmission
 * @requires ./validation.js
 * @requires ./sse-client.js (optional - for progress tracking)
 * @requires ./toast-notifications.js (optional - for progress updates)
 */

/**
 * Show the confirmation modal before form submission
 * Performs pre-submission validation and displays review data
 */
function showReviewScreen() {
    const form = document.getElementById('main-form');

    // Run full validation before showing review
    if (typeof runFullValidation === 'function') {
        const isValid = runFullValidation(form);
        if (!isValid) {
            alert('Please fix all validation errors before submitting.');
            return;
        }
    }

    // Get the confirmation modal
    const modal = document.getElementById('confirmationModal');
    if (!modal) {
        console.error('Confirmation modal not found');
        return;
    }

    // Display the modal using the show class
    modal.classList.add('show');

    // Add click handler to close modal when clicking outside
    modal.onclick = function(event) {
        if (event.target === modal) {
            closeConfirmationModal();
        }
    };

    console.log('Showing confirmation modal');
}

/**
 * Close the confirmation modal
 */
function closeConfirmationModal() {
    const modal = document.getElementById('confirmationModal');
    if (modal) {
        modal.classList.remove('show');
        modal.onclick = null;
    }
}

/**
 * User confirmed submission - show email notification modal
 */
function confirmSubmission() {
    closeConfirmationModal();
    showEmailNotificationModal();
}

/**
 * Show email notification opt-in modal
 */
function showEmailNotificationModal() {
    const modal = document.getElementById('emailNotificationModal');
    if (!modal) {
        console.error('Email notification modal not found');
        // Fallback: submit without email
        submitForm(null, false);
        return;
    }

    modal.classList.add('show');

    // Add click handler to close modal when clicking outside
    modal.onclick = function(event) {
        if (event.target === modal) {
            skipEmailNotification();
        }
    };

    console.log('Showing email notification modal');
}

/**
 * Close email notification modal
 */
function closeEmailNotificationModal() {
    const modal = document.getElementById('emailNotificationModal');
    if (modal) {
        modal.classList.remove('show');
        modal.onclick = null;
    }
}

/**
 * User chose to skip email notification
 */
async function skipEmailNotification() {
    closeEmailNotificationModal();
    await submitForm(null, false);
}

/**
 * User provided email for notification
 */
async function submitEmailNotification() {
    const emailInput = document.getElementById('notification-email-input');
    const nameInput = document.getElementById('notification-name-input');

    if (!emailInput || !nameInput) {
        console.error('Email input fields not found');
        return;
    }

    const email = emailInput.value.trim();
    const name = nameInput.value.trim();

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (email && !emailRegex.test(email)) {
        alert('Please enter a valid email address');
        return;
    }

    closeEmailNotificationModal();
    await submitForm(email || null, !!email, name || null);
}

/**
 * Submit form data to the server
 * Implements retry logic and error handling for robust submission
 *
 * Performance Optimizations:
 * - Uses fetch API with AbortController for timeout
 * - Implements exponential backoff for retries
 * - Compresses payload using JSON.stringify
 *
 * @param {string|null} notificationEmail - Optional email for notifications
 * @param {boolean} optedIn - Whether user opted in to notifications
 * @param {string|null} notificationName - Optional name for notifications
 * @param {number} retryCount - Current retry attempt (internal use)
 */
async function submitForm(notificationEmail = null, optedIn = false, notificationName = null, retryCount = 0) {
    const form = document.getElementById('main-form');
    if (!form) {
        console.error('Form not found');
        return;
    }

    try {
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';
        }

        // Collect form data
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Add metadata
        data.id = Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        data.submittedAt = new Date().toISOString();
        data.notificationEmail = notificationEmail;
        data.notificationEmailOptIn = optedIn;
        data.notificationName = notificationName;

        console.log('Submitting form data:', data);

        // Create AbortController for timeout (10 second timeout)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);

        // Submit to server
        const response = await fetch('/api/form-entries', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Server returned ${response.status}`);
        }

        const result = await response.json();
        console.log('Form submitted successfully:', result);

        // Handle success
        handleSubmissionSuccess(result);

    } catch (error) {
        console.error('Form submission error:', error);

        // Retry logic with exponential backoff
        if (retryCount < 3 && error.name !== 'AbortError') {
            const delay = Math.pow(2, retryCount) * 1000; // 1s, 2s, 4s
            console.log(`Retrying submission in ${delay}ms... (attempt ${retryCount + 1}/3)`);

            setTimeout(() => {
                submitForm(notificationEmail, optedIn, notificationName, retryCount + 1);
            }, delay);

            return;
        }

        // Handle error after retries exhausted
        handleSubmissionError(error);
    }
}

/**
 * Handle successful form submission
 * Resets form to initial state and shows success notification
 * Documents are generated in the background without blocking the form
 *
 * @param {Object} result - Server response data
 */
async function handleSubmissionSuccess(result) {
    // Store submission ID for reference
    if (result.id) {
        sessionStorage.setItem('lastSubmissionId', result.id);
    }

    // DEBUG: Log what we received from server
    console.log('📦 Server response:', {
        id: result.id,
        dbCaseId: result.dbCaseId,
        dbCaseId_type: typeof result.dbCaseId
    });

    // Get case ID for progress tracking (background process)
    const caseId = result.dbCaseId || result.id;

    console.log(`📍 Case submitted: ${caseId}`);

    // Only show progress tracking if document generation is enabled
    // Check if the server indicated that document generation is happening
    const pipelineEnabled = result.pipelineEnabled || result.pipeline_enabled || false;

    // NOTE: Document generation now happens automatically within the form submission
    // request to Python. No separate SSE progress tracking needed.
    if (pipelineEnabled && caseId) {
        console.log(`✅ Form submitted successfully. Documents will be generated automatically.`);
        console.log(`📄 Case ID: ${caseId}`);
    } else {
        console.log(`ℹ️ Pipeline not enabled - form saved to database only`);
    }

    // Reset form immediately - documents generate in background
    resetFormAfterSubmission(result);
}

/**
 * Reset form to initial state after successful submission
 * Clears all fields and reinitializes with one plaintiff and defendant
 *
 * @param {Object} result - Server response data (for success message)
 */
function resetFormAfterSubmission(result) {
    const form = document.getElementById('main-form');
    if (!form) {
        console.error('Form not found');
        return;
    }

    console.log('✅ Form submitted successfully - Case ID:', result.dbCaseId || result.id);

    // Show success toast ONLY if pipeline is not enabled (to avoid overlap with progress toast)
    const pipelineEnabled = result.pipelineEnabled || result.pipeline_enabled || false;
    if (!pipelineEnabled && typeof Notyf !== 'undefined') {
        const notyf = new Notyf({
            duration: 5000,
            position: { x: 'right', y: 'bottom' },
            dismissible: true
        });
        notyf.success({
            message: `✓ Form submitted successfully!`,
            duration: 5000
        });
    }

    // Reset button state
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Form';
    }

    // Clear the form
    form.reset();

    // Reset plaintiff and defendant sections
    const plaintiffsContainer = document.getElementById('plaintiffs-container');
    const defendantsContainer = document.getElementById('defendants-container');

    if (plaintiffsContainer) {
        plaintiffsContainer.innerHTML = '';
    }

    if (defendantsContainer) {
        defendantsContainer.innerHTML = '';
    }

    // Reset counters (access global variables from index.html)
    if (typeof window.plaintiffCounter !== 'undefined') {
        window.plaintiffCounter = 0;
    }

    if (typeof window.defendantCounter !== 'undefined') {
        window.defendantCounter = 0;
    }

    // Reinitialize with one plaintiff and defendant
    if (typeof window.addPlaintiff === 'function') {
        window.addPlaintiff();
    }

    if (typeof window.addDefendant === 'function') {
        window.addDefendant();
    }

    // Scroll to top of form
    window.scrollTo({ top: 0, behavior: 'smooth' });

    console.log('🔄 Form reset complete - ready for new submission');
}

/**
 * Handle form submission error
 * Displays error message and restores form state
 *
 * @param {Error} error - The error that occurred
 */
function handleSubmissionError(error) {
    const form = document.getElementById('main-form');

    // Restore submit button
    const submitBtn = form?.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Form';
    }

    // Display error message
    let errorMessage = 'Failed to submit form. Please try again.';

    if (error.name === 'AbortError') {
        errorMessage = 'Request timed out. Please check your connection and try again.';
    } else if (error.message) {
        errorMessage = `Error: ${error.message}`;
    }

    alert(errorMessage);
}

/**
 * Extract plaintiff data from form for preview
 * Used by confirmation modal to display summary
 *
 * @param {Object} data - Form data object
 * @returns {Array} Array of plaintiff objects
 */
function extractPlaintiffs(data) {
    const plaintiffs = [];
    const plaintiffIds = new Set();

    // Find all plaintiff IDs from form field names
    Object.keys(data).forEach(key => {
        const match = key.match(/plaintiff-(\d+)-/);
        if (match) {
            plaintiffIds.add(parseInt(match[1]));
        }
    });

    // Build plaintiff objects
    plaintiffIds.forEach(id => {
        const plaintiff = {
            id: id,
            firstName: data[`plaintiff-${id}-first-name`] || '',
            lastName: data[`plaintiff-${id}-last-name`] || '',
            type: data[`plaintiff-${id}-type`] || 'Individual',
            age: data[`plaintiff-${id}-age`] || 'adult',
            head: data[`plaintiff-${id}-head`] || 'no',
            unit: data[`plaintiff-${id}-unit`] || ''
        };
        plaintiffs.push(plaintiff);
    });

    return plaintiffs;
}

/**
 * Extract defendant data from form for preview
 *
 * @param {Object} data - Form data object
 * @returns {Array} Array of defendant objects
 */
function extractDefendants(data) {
    const defendants = [];
    const defendantIds = new Set();

    Object.keys(data).forEach(key => {
        const match = key.match(/defendant-(\d+)-/);
        if (match) {
            defendantIds.add(parseInt(match[1]));
        }
    });

    defendantIds.forEach(id => {
        const defendant = {
            id: id,
            firstName: data[`defendant-${id}-first-name`] || '',
            lastName: data[`defendant-${id}-last-name`] || '',
            entity: data[`defendant-${id}-entity`] || 'Individual',
            role: data[`defendant-${id}-role`] || 'owner'
        };
        defendants.push(defendant);
    });

    return defendants;
}

// Make functions available globally
if (typeof window !== 'undefined') {
    window.showReviewScreen = showReviewScreen;
    window.closeConfirmationModal = closeConfirmationModal;
    window.confirmSubmission = confirmSubmission;
    window.showEmailNotificationModal = showEmailNotificationModal;
    window.closeEmailNotificationModal = closeEmailNotificationModal;
    window.skipEmailNotification = skipEmailNotification;
    window.submitEmailNotification = submitEmailNotification;
    window.submitForm = submitForm;
    window.extractPlaintiffs = extractPlaintiffs;
    window.extractDefendants = extractDefendants;
}
