// flaskr/website/static/js/assign_scenario.js

function selectAll() {
    const checkboxes = document.querySelectorAll('.student-checkbox');
    checkboxes.forEach(cb => cb.checked = true);
    updateCount();
}

function selectNone() {
    const checkboxes = document.querySelectorAll('.student-checkbox');
    checkboxes.forEach(cb => cb.checked = false);
    updateCount();
}

function selectNew() {
    const checkboxes = document.querySelectorAll('.student-checkbox');
    checkboxes.forEach(cb => {
        if (!cb.closest('tr').querySelector('.badge-success')) {
            cb.checked = true;
        } else {
            cb.checked = false;
        }
    });
    updateCount();
}

function updateCount() {
    const checked = document.querySelectorAll('.student-checkbox:checked').length;
    const counterElement = document.getElementById('selected-count');
    if (counterElement) {
        counterElement.textContent = checked;
    }
}

function searchStudents() {
    const input = document.getElementById('searchBox');
    const filter = input.value.toLowerCase();
    const rows = document.querySelectorAll('.student-row');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
    });
}

function updatePatientAvailability() {
    const patientSelects = document.querySelectorAll('select[name^="patient_"]');
    const selectedPatients = {};
    
    // Count selections for each patient
    patientSelects.forEach(select => {
        if (select.value) {
            selectedPatients[select.value] = (selectedPatients[select.value] || 0) + 1;
        }
    });
    
    // Update availability indicators
    patientSelects.forEach(select => {
        const studentId = select.name.match(/patient_(\d+)/)[1];
        const row = document.querySelector(`tr[data-student-id="${studentId}"]`);
        if (row) {
            const indicator = row.querySelector('.patient-availability');
            if (indicator && select.value) {
                const count = selectedPatients[select.value];
                if (count > 1) {
                    indicator.textContent = `(${count} students assigned)`;
                    indicator.className = 'patient-availability text-warning small';
                } else {
                    indicator.textContent = '';
                    indicator.className = 'patient-availability small';
                }
            }
        }
    });
}

function assignSelectedStudents() {
    const selectedCheckboxes = document.querySelectorAll('.student-checkbox:checked');
    
    if (selectedCheckboxes.length === 0) {
        alert('Please select at least one student to assign.');
        return false;
    }
    
    // Verify that all selected students have a patient assigned
    let allHavePatients = true;
    selectedCheckboxes.forEach(checkbox => {
        const row = checkbox.closest('tr');
        const patientSelect = row.querySelector('select[name^="patient_"]');
        if (!patientSelect || !patientSelect.value) {
            allHavePatients = false;
        }
    });
    
    if (!allHavePatients) {
        alert('Please assign a patient to all selected students.');
        return false;
    }
    
    return true;
}

function setupUnassignButton() {
    const unassignBtn = document.getElementById('unassignBtn');
    if (unassignBtn) {
        unassignBtn.addEventListener('click', function() {
            const formAction = document.getElementById('formAction');
            const assignForm = document.getElementById('assignForm');
            
            if (!confirm('Are you sure you want to unassign the selected students? This will remove their access.')) return;
            formAction.value = 'unassign';
            assignForm.submit();
        });
    }
}

window.onload = function() {
    // Set up button event handlers
    const selectAllBtn = document.getElementById('selectAllBtn');
    if (selectAllBtn) {
        selectAllBtn.onclick = selectAll;
    }
    
    const selectNoneBtn = document.getElementById('selectNoneBtn');
    if (selectNoneBtn) {
        selectNoneBtn.onclick = selectNone;
    }
    
    const selectNewBtn = document.getElementById('selectNewBtn');
    if (selectNewBtn) {
        selectNewBtn.onclick = selectNew;
    }
    
    // Set up search functionality
    const searchBox = document.getElementById('searchBox');
    if (searchBox) {
        if (searchBox.addEventListener) {
            searchBox.addEventListener('keyup', searchStudents);
        } else {
            searchBox.onkeyup = searchStudents;
        }
    }
    
    // Set up select all checkbox in table header
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            if (this.checked) {
                selectAll();
            } else {
                selectNone();
            }
        });
    }
    
    // Set up individual checkboxes
    const studentCheckboxes = document.getElementsByClassName('student-checkbox');
    for (let i = 0; i < studentCheckboxes.length; i++) {
        studentCheckboxes[i].addEventListener('change', function() {
            updateCount();
            
            // Update master checkbox
            const checkedCount = document.querySelectorAll('.student-checkbox:checked').length;
            const totalCount = document.querySelectorAll('.student-checkbox').length;
            const masterCheckbox = document.getElementById('selectAllCheckbox');
            
            if (masterCheckbox) {
                if (checkedCount === 0) {
                    masterCheckbox.indeterminate = false;
                    masterCheckbox.checked = false;
                } else if (checkedCount === totalCount) {
                    masterCheckbox.indeterminate = false;
                    masterCheckbox.checked = true;
                } else {
                    masterCheckbox.indeterminate = true;
                }
            }
        });
    }
    
    // Set up patient dropdown change handlers for availability checking
    const patientSelects = document.querySelectorAll('select[name^="patient_"]');
    patientSelects.forEach(select => {
        select.addEventListener('change', updatePatientAvailability);
    });
    
    // Initialize unassign button handler
    setupUnassignButton();
    
    // Set up form submission handler
    const assignForm = document.getElementById('assignForm');
    if (assignForm) {
        assignForm.addEventListener('submit', function(e) {
            console.log('Form submission triggered');
            e.preventDefault();
            
            // Debug: Check what's selected
            const checkedBoxes = document.querySelectorAll('.student-checkbox:checked');
            console.log('Checked students:', checkedBoxes.length);
            
            if (assignSelectedStudents()) {
                console.log('Validation passed, submitting form');
                this.submit();
            } else {
                console.log('Validation failed');
            }
        });
    } else {
        console.error('assignForm not found');
    }
    
    // Initialize
    updateCount();
    updatePatientAvailability();
};