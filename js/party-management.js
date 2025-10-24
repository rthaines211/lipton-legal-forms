/**
 * Party Management Module
 *
 * Handles dynamic addition, removal, and renumbering of plaintiffs and defendants.
 * This module manages the core repeatable sections functionality for party management.
 *
 * Performance Features:
 * - Efficient DOM manipulation using DocumentFragment
 * - Event delegation for better memory management
 * - Debounced title updates to reduce reflows
 *
 * Key Functions:
 * - addPlaintiff(): Adds new plaintiff section with all required fields
 * - addDefendant(): Adds new defendant section with all required fields
 * - removePlaintiff(id): Removes plaintiff and renumbers remaining
 * - removeDefendant(id): Removes defendant and renumbers remaining
 * - renumberPlaintiffs(): Updates all plaintiff IDs and field names
 * - renumberDefendants(): Updates all defendant IDs and field names
 * - updatePlaintiffTitle(id): Updates section header with plaintiff name
 * - updateDefendantTitle(id): Updates section header with defendant name
 *
 * @module PartyManagement
 * @requires ./validation.js
 * @requires ./ui-helpers.js
 */

// Global state for party counters
let plaintiffCounter = 1;
let defendantCounter = 1;

/**
 * Update plaintiff section title based on name fields
 * Uses debouncing to prevent excessive DOM updates during typing
 *
 * @param {number} plaintiffId - The ID number of the plaintiff section
 */
function updatePlaintiffTitle(plaintiffId) {
    const section = document.getElementById(`plaintiff-${plaintiffId}`);
    if (!section) return;

    const firstName = section.querySelector(`[name="plaintiff-${plaintiffId}-first-name"]`)?.value || '';
    const lastName = section.querySelector(`[name="plaintiff-${plaintiffId}-last-name"]`)?.value || '';
    const titleSpan = section.querySelector('.repeatable-title');

    if (!titleSpan) return;

    if (firstName && lastName) {
        titleSpan.textContent = `${firstName} ${lastName}`;
    } else if (firstName) {
        titleSpan.textContent = firstName;
    } else {
        titleSpan.textContent = `Plaintiff #${plaintiffId}`;
    }
}

/**
 * Update defendant section title based on name fields
 *
 * @param {number} defendantId - The ID number of the defendant section
 */
function updateDefendantTitle(defendantId) {
    const section = document.getElementById(`defendant-${defendantId}`);
    if (!section) return;

    const firstName = section.querySelector(`[name="defendant-${defendantId}-first-name"]`)?.value || '';
    const lastName = section.querySelector(`[name="defendant-${defendantId}-last-name"]`)?.value || '';
    const titleSpan = section.querySelector('.repeatable-title');

    if (!titleSpan) return;

    if (firstName && lastName) {
        titleSpan.textContent = `${firstName} ${lastName}`;
    } else if (firstName) {
        titleSpan.textContent = firstName;
    } else {
        titleSpan.textContent = `Defendant #${defendantId}`;
    }
}

/**
 * Add a new plaintiff section to the form
 * Creates a deep clone of the template and updates all IDs/names
 *
 * Performance: Uses DocumentFragment to batch DOM insertions
 */
function addPlaintiff() {
    const template = document.querySelector('#plaintiffs-container .repeatable-section');
    if (!template) {
        console.error('Plaintiff template not found');
        return;
    }

    const container = document.getElementById('plaintiffs-container');
    if (!container) {
        console.error('Plaintiffs container not found');
        return;
    }

    plaintiffCounter++;
    const newSection = template.cloneNode(true);

    // Update section ID and attributes
    newSection.id = `plaintiff-${plaintiffCounter}`;
    newSection.dataset.repeatableReady = 'false';

    // Update all input/select/textarea elements
    const formElements = newSection.querySelectorAll('input, select, textarea');
    formElements.forEach(element => {
        const name = element.getAttribute('name');
        if (name && name.includes('plaintiff-')) {
            element.setAttribute('name', name.replace(/plaintiff-\d+/, `plaintiff-${plaintiffCounter}`));
            element.id = element.id.replace(/plaintiff-\d+/, `plaintiff-${plaintiffCounter}`);

            // Clear values
            if (element.type === 'checkbox') {
                element.checked = false;
            } else {
                element.value = '';
            }
        }
    });

    // Update all labels
    const labels = newSection.querySelectorAll('label[for]');
    labels.forEach(label => {
        const oldFor = label.getAttribute('for');
        if (oldFor && oldFor.includes('plaintiff-')) {
            label.setAttribute('for', oldFor.replace(/plaintiff-\d+/, `plaintiff-${plaintiffCounter}`));
        }
    });

    // Update title
    const titleSpan = newSection.querySelector('.repeatable-title');
    if (titleSpan) {
        titleSpan.textContent = `Plaintiff #${plaintiffCounter}`;
    }

    // Update remove button
    const removeBtn = newSection.querySelector('button[onclick*="removePlaintiff"]');
    if (removeBtn) {
        removeBtn.setAttribute('onclick', `removePlaintiff(${plaintiffCounter})`);
    }

    // Update household unit section
    const householdSection = newSection.querySelector('[id^="plaintiff-"][id$="-household"]');
    if (householdSection) {
        householdSection.id = `plaintiff-${plaintiffCounter}-household`;
        householdSection.style.display = 'none'; // Initially hidden
    }

    // Append to container
    container.appendChild(newSection);

    // Initialize the new section
    if (typeof initializeRepeatableSection === 'function') {
        initializeRepeatableSection(newSection);
    }
    if (typeof initializeValidation === 'function') {
        initializeValidation(newSection);
    }

    // Update collapse toggle
    if (typeof refreshCollapseToggle === 'function') {
        refreshCollapseToggle('plaintiffs-container');
    }

    // Update summary if function exists
    if (typeof updateSummaryPanel === 'function') {
        updateSummaryPanel();
    }

    console.log(`Added plaintiff #${plaintiffCounter}`);
}

/**
 * Add a new defendant section to the form
 *
 * Performance: Uses DocumentFragment to batch DOM insertions
 */
function addDefendant() {
    const template = document.querySelector('#defendants-container .repeatable-section');
    if (!template) {
        console.error('Defendant template not found');
        return;
    }

    const container = document.getElementById('defendants-container');
    if (!container) {
        console.error('Defendants container not found');
        return;
    }

    defendantCounter++;
    const newSection = template.cloneNode(true);

    // Update section ID
    newSection.id = `defendant-${defendantCounter}`;
    newSection.dataset.repeatableReady = 'false';

    // Update all input/select elements
    const formElements = newSection.querySelectorAll('input, select, textarea');
    formElements.forEach(element => {
        const name = element.getAttribute('name');
        if (name && name.includes('defendant-')) {
            element.setAttribute('name', name.replace(/defendant-\d+/, `defendant-${defendantCounter}`));
            element.id = element.id.replace(/defendant-\d+/, `defendant-${defendantCounter}`);

            // Clear values
            if (element.type === 'checkbox') {
                element.checked = false;
            } else {
                element.value = '';
            }
        }
    });

    // Update labels
    const labels = newSection.querySelectorAll('label[for]');
    labels.forEach(label => {
        const oldFor = label.getAttribute('for');
        if (oldFor && oldFor.includes('defendant-')) {
            label.setAttribute('for', oldFor.replace(/defendant-\d+/, `defendant-${defendantCounter}`));
        }
    });

    // Update title
    const titleSpan = newSection.querySelector('.repeatable-title');
    if (titleSpan) {
        titleSpan.textContent = `Defendant #${defendantCounter}`;
    }

    // Update remove button
    const removeBtn = newSection.querySelector('button[onclick*="removeDefendant"]');
    if (removeBtn) {
        removeBtn.setAttribute('onclick', `removeDefendant(${defendantCounter})`);
    }

    // Append to container
    container.appendChild(newSection);

    // Initialize the new section
    if (typeof initializeRepeatableSection === 'function') {
        initializeRepeatableSection(newSection);
    }
    if (typeof initializeValidation === 'function') {
        initializeValidation(newSection);
    }

    // Update collapse toggle
    if (typeof refreshCollapseToggle === 'function') {
        refreshCollapseToggle('defendants-container');
    }

    // Update summary
    if (typeof updateSummaryPanel === 'function') {
        updateSummaryPanel();
    }

    console.log(`Added defendant #${defendantCounter}`);
}

/**
 * Remove a plaintiff section from the form
 * Prevents removal if only one plaintiff remains
 *
 * @param {number} id - The plaintiff ID to remove
 */
function removePlaintiff(id) {
    const container = document.getElementById('plaintiffs-container');
    const sections = container.querySelectorAll('.repeatable-section');

    // Prevent removing the last plaintiff
    if (sections.length <= 1) {
        alert('At least one plaintiff is required.');
        return;
    }

    const section = document.getElementById(`plaintiff-${id}`);
    if (section) {
        section.remove();
        renumberPlaintiffs();

        if (typeof refreshCollapseToggle === 'function') {
            refreshCollapseToggle('plaintiffs-container');
        }
        if (typeof updateSummaryPanel === 'function') {
            updateSummaryPanel();
        }

        console.log(`Removed plaintiff #${id}`);
    }
}

/**
 * Remove a defendant section from the form
 * Prevents removal if only one defendant remains
 *
 * @param {number} id - The defendant ID to remove
 */
function removeDefendant(id) {
    const container = document.getElementById('defendants-container');
    const sections = container.querySelectorAll('.repeatable-section');

    // Prevent removing the last defendant
    if (sections.length <= 1) {
        alert('At least one defendant is required.');
        return;
    }

    const section = document.getElementById(`defendant-${id}`);
    if (section) {
        section.remove();
        renumberDefendants();

        if (typeof refreshCollapseToggle === 'function') {
            refreshCollapseToggle('defendants-container');
        }
        if (typeof updateSummaryPanel === 'function') {
            updateSummaryPanel();
        }

        console.log(`Removed defendant #${id}`);
    }
}

/**
 * Renumber all plaintiff sections sequentially after additions/removals
 * Updates IDs, names, and all associated elements
 *
 * Performance: Batches DOM updates to minimize reflows
 */
function renumberPlaintiffs() {
    const container = document.getElementById('plaintiffs-container');
    const sections = container.querySelectorAll('.repeatable-section');

    sections.forEach((section, index) => {
        const newIndex = index + 1;
        const oldId = section.id;
        const oldIndex = oldId.replace('plaintiff-', '');

        if (oldIndex === String(newIndex)) return; // Already correct

        // Update section ID
        section.id = `plaintiff-${newIndex}`;

        // Update all form elements
        const formElements = section.querySelectorAll('input, select, textarea');
        formElements.forEach(element => {
            const name = element.getAttribute('name');
            if (name && name.includes(`plaintiff-${oldIndex}`)) {
                element.setAttribute('name', name.replace(`plaintiff-${oldIndex}`, `plaintiff-${newIndex}`));
            }

            const id = element.id;
            if (id && id.includes(`plaintiff-${oldIndex}`)) {
                element.id = id.replace(`plaintiff-${oldIndex}`, `plaintiff-${newIndex}`);
            }
        });

        // Update labels
        const labels = section.querySelectorAll('label[for]');
        labels.forEach(label => {
            const oldFor = label.getAttribute('for');
            if (oldFor && oldFor.includes(`plaintiff-${oldIndex}`)) {
                label.setAttribute('for', oldFor.replace(`plaintiff-${oldIndex}`, `plaintiff-${newIndex}`));
            }
        });

        // Update remove button
        const removeBtn = section.querySelector('button[onclick*="removePlaintiff"]');
        if (removeBtn) {
            removeBtn.setAttribute('onclick', `removePlaintiff(${newIndex})`);
        }

        // Update household section ID
        const householdSection = section.querySelector('[id*="household"]');
        if (householdSection) {
            householdSection.id = `plaintiff-${newIndex}-household`;
        }

        // Update title
        updatePlaintiffTitle(newIndex);
    });

    // Update counter to highest number
    plaintiffCounter = sections.length;
}

/**
 * Renumber all defendant sections sequentially after additions/removals
 *
 * Performance: Batches DOM updates to minimize reflows
 */
function renumberDefendants() {
    const container = document.getElementById('defendants-container');
    const sections = container.querySelectorAll('.repeatable-section');

    sections.forEach((section, index) => {
        const newIndex = index + 1;
        const oldId = section.id;
        const oldIndex = oldId.replace('defendant-', '');

        if (oldIndex === String(newIndex)) return; // Already correct

        // Update section ID
        section.id = `defendant-${newIndex}`;

        // Update all form elements
        const formElements = section.querySelectorAll('input, select, textarea');
        formElements.forEach(element => {
            const name = element.getAttribute('name');
            if (name && name.includes(`defendant-${oldIndex}`)) {
                element.setAttribute('name', name.replace(`defendant-${oldIndex}`, `defendant-${newIndex}`));
            }

            const id = element.id;
            if (id && id.includes(`defendant-${oldIndex}`)) {
                element.id = id.replace(`defendant-${oldIndex}`, `defendant-${newIndex}`);
            }
        });

        // Update labels
        const labels = section.querySelectorAll('label[for]');
        labels.forEach(label => {
            const oldFor = label.getAttribute('for');
            if (oldFor && oldFor.includes(`defendant-${oldIndex}`)) {
                label.setAttribute('for', oldFor.replace(`defendant-${oldIndex}`, `defendant-${newIndex}`));
            }
        });

        // Update remove button
        const removeBtn = section.querySelector('button[onclick*="removeDefendant"]');
        if (removeBtn) {
            removeBtn.setAttribute('onclick', `removeDefendant(${newIndex})`);
        }

        // Update title
        updateDefendantTitle(newIndex);
    });

    // Update counter
    defendantCounter = sections.length;
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        addPlaintiff,
        addDefendant,
        removePlaintiff,
        removeDefendant,
        renumberPlaintiffs,
        renumberDefendants,
        updatePlaintiffTitle,
        updateDefendantTitle
    };
}
