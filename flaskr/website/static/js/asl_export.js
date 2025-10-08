// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeExportFunctionality();
});

/**
 * Initialize export functionality
 */
function initializeExportFunctionality() {
    // Select All ASL checkbox handler
    const selectAllASL = document.getElementById('selectAllASL');
    if (selectAllASL) {
        selectAllASL.addEventListener('change', function() {
            const aslCheckboxes = document.querySelectorAll('#asl-table .prescription-select');
            aslCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateExportButtonState();
        });
    }

    // Select All ALR checkbox handler
    const selectAllALR = document.getElementById('selectAllALR');
    if (selectAllALR) {
        selectAllALR.addEventListener('change', function() {
            const alrCheckboxes = document.querySelectorAll('#alr-table .prescription-select');
            alrCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateExportButtonState();
        });
    }

    // Individual checkbox handlers
    const prescriptionCheckboxes = document.querySelectorAll('.prescription-select');
    prescriptionCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateExportButtonState);
    });

    // Update button state on load
    updateExportButtonState();
}

/**
 * Update the state of the export selected button based on selection
 */
function updateExportButtonState() {
    const selectedCheckboxes = document.querySelectorAll('.prescription-select:checked');
    const exportSelectedBtn = document.getElementById('exportSelectedBtn');
    
    if (exportSelectedBtn) {
        if (selectedCheckboxes.length > 0) {
            exportSelectedBtn.disabled = false;
            exportSelectedBtn.classList.remove('btn-outline-success');
            exportSelectedBtn.classList.add('btn-success');
            exportSelectedBtn.title = `Export ${selectedCheckboxes.length} selected prescription(s)`;
        } else {
            exportSelectedBtn.disabled = true;
            exportSelectedBtn.classList.remove('btn-success');
            exportSelectedBtn.classList.add('btn-outline-success');
            exportSelectedBtn.title = 'Select prescriptions to export';
        }
    }
}

/**
 * Export selected prescriptions as CSV
 * @param {number} patientId - The patient ID
 */
function exportSelectedPrescriptions(patientId) {
    const selectedCheckboxes = document.querySelectorAll('.prescription-select:checked');
    
    if (selectedCheckboxes.length === 0) {
        alert('Please select at least one prescription to export');
        return;
    }

    // Collect selected prescription IDs
    const prescriptionIds = Array.from(selectedCheckboxes).map(cb => cb.value);
    
    // Get CSRF token
    const csrfToken = document.querySelector('input[name="csrf_token"]').value;
    
    // Create and submit form
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/api/export-asl-selected/${patientId}`;
    
    // Add CSRF token
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrf_token';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);
    
    // Add prescription IDs
    const idsInput = document.createElement('input');
    idsInput.type = 'hidden';
    idsInput.name = 'prescription_ids';
    idsInput.value = prescriptionIds.join(',');
    form.appendChild(idsInput);
    
    // Submit form
    document.body.appendChild(form);
    form.submit();
    
    // Clean up
    setTimeout(() => {
        document.body.removeChild(form);
    }, 1000);
}

/**
 * Get count of selected prescriptions
 * @returns {number} Count of selected prescriptions
 */
function getSelectedCount() {
    return document.querySelectorAll('.prescription-select:checked').length;
}

/**
 * Clear all selections
 */
function clearAllSelections() {
    document.querySelectorAll('.prescription-select').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    const selectAllASL = document.getElementById('selectAllASL');
    const selectAllALR = document.getElementById('selectAllALR');
    
    if (selectAllASL) selectAllASL.checked = false;
    if (selectAllALR) selectAllALR.checked = false;
    
    updateExportButtonState();
}

/**
 * Select all prescriptions (both ASL and ALR)
 */
function selectAllPrescriptions() {
    document.querySelectorAll('.prescription-select').forEach(checkbox => {
        checkbox.checked = true;
    });
    
    const selectAllASL = document.getElementById('selectAllASL');
    const selectAllALR = document.getElementById('selectAllALR');
    
    if (selectAllASL) selectAllASL.checked = true;
    if (selectAllALR) selectAllALR.checked = true;
    
    updateExportButtonState();
}

// Make functions available globally
window.exportSelectedPrescriptions = exportSelectedPrescriptions;
window.clearAllSelections = clearAllSelections;
window.selectAllPrescriptions = selectAllPrescriptions;
window.getSelectedCount = getSelectedCount;