// flaskr/website/static/js/patient_dashboard.js

document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    const searchInput = document.getElementById('patientSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('#patientsTable tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }
    
    // Select all checkbox functionality
    const selectAllCheckbox = document.getElementById('selectAllPatients');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.patient-checkbox');
            checkboxes.forEach(cb => {
                cb.checked = this.checked;
            });
            updateBulkActionsVisibility();
        });
    }
    
    // Individual patient checkboxes
    const patientCheckboxes = document.querySelectorAll('.patient-checkbox');
    patientCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectAllCheckbox();
            updateBulkActionsVisibility();
        });
    });
    
    // Bulk delete button
    const bulkDeleteBtn = document.getElementById('bulk-delete');
    if (bulkDeleteBtn) {
        bulkDeleteBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const selectedCheckboxes = document.querySelectorAll('.patient-checkbox:checked');
            
            if (selectedCheckboxes.length === 0) {
                alert('Please select patients to delete');
                return;
            }
            
            if (confirm(`Are you sure you want to delete ${selectedCheckboxes.length} patient(s)?`)) {
                const form = document.getElementById('bulk-delete-form');
                if (form) {
                    // Add selected patient IDs to form
                    selectedCheckboxes.forEach(cb => {
                        const input = document.createElement('input');
                        input.type = 'hidden';
                        input.name = 'patient_ids[]';
                        input.value = cb.value;
                        form.appendChild(input);
                    });
                    form.submit();
                }
            }
        });
    }
});

function updateSelectAllCheckbox() {
    const selectAllCheckbox = document.getElementById('selectAllPatients');
    const patientCheckboxes = document.querySelectorAll('.patient-checkbox');
    const checkedCount = document.querySelectorAll('.patient-checkbox:checked').length;
    
    if (selectAllCheckbox) {
        if (checkedCount === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        } else if (checkedCount === patientCheckboxes.length) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        }
    }
}

function updateBulkActionsVisibility() {
    const bulkActions = document.querySelector('.bulk-actions');
    const checkedCount = document.querySelectorAll('.patient-checkbox:checked').length;
    
    if (bulkActions) {
        if (checkedCount > 0) {
            bulkActions.classList.remove('d-none');
        } else {
            bulkActions.classList.add('d-none');
        }
    }
}