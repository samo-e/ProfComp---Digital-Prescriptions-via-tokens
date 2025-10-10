// flaskr/website/static/js/assign_scenario.js

/**
 * Select all student checkboxes (only visible ones)
 */
function selectAll() {
    const checkboxes = document.querySelectorAll('.student-checkbox');
    checkboxes.forEach(function(cb) {
        const row = cb.closest('tr');
        if (!row || row.style.display !== 'none') {
            cb.checked = true;
        }
    });
    updateCount();
}

/**
 * Deselect all student checkboxes
 */
function selectNone() {
    const checkboxes = document.querySelectorAll('.student-checkbox');
    checkboxes.forEach(function(cb) {
        cb.checked = false;
    });
    updateCount();
}

/**
 * Select only new (unassigned) students
 */
function selectNew() {
    const checkboxes = document.querySelectorAll('.student-checkbox');
    checkboxes.forEach(function(cb) {
        const row = cb.closest('tr');
        const statusEl = row ? row.querySelector('.status-badge') : null;
        const isVisible = !row || row.style.display !== 'none';
        let isAvailable = false;
        
        if (statusEl && statusEl.textContent) {
            isAvailable = statusEl.textContent.toLowerCase().indexOf('available') !== -1;
        }

        if (isAvailable && isVisible) {
            cb.checked = true;
        } else {
            cb.checked = false;
        }
    });
    updateCount();
}

/**
 * Update the count of selected students and UI elements
 */
function updateCount() {
    const checkboxes = document.querySelectorAll('.student-checkbox');
    let count = 0;
    
    checkboxes.forEach(function(cb) {
        if (cb.checked) {
            count++;
        }
    });
    
    const countElement = document.getElementById('selectedCount');
    const summaryElement = document.getElementById('selectionSummary');
    const btnElement = document.getElementById('assignBtn');
    
    if (countElement) {
        countElement.textContent = count;
    }
    
    if (summaryElement) {
        if (typeof $ !== 'undefined') {
            $(summaryElement).toggleClass('d-none', count === 0);
        } else {
            if (count === 0) {
                summaryElement.classList.add('d-none');
            } else {
                summaryElement.classList.remove('d-none');
            }
        }
    }
    
    if (btnElement) {
        btnElement.disabled = count === 0;
    }
}

/**
 * Search/filter students by name or email
 */
function searchStudents() {
    const searchBox = document.getElementById('searchBox');
    const searchValue = searchBox ? searchBox.value.toLowerCase() : '';
    const rows = document.querySelectorAll('.student-row');
    let visibleCount = 0;
    
    rows.forEach(function(row) {
        const name = row.getAttribute('data-name') || '';
        const email = row.getAttribute('data-email') || '';
        
        if (name.indexOf(searchValue) > -1 || email.indexOf(searchValue) > -1 || searchValue === '') {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    });
    
    const noResults = document.getElementById('noResults');
    if (noResults) {
        if (typeof $ !== 'undefined') {
            $(noResults).toggleClass('d-none', visibleCount !== 0 || searchValue === '');
        } else {
            if (visibleCount !== 0 || searchValue === '') {
                noResults.classList.add('d-none');
            } else {
                noResults.classList.remove('d-none');
            }
        }
    }
}

/**
 * Update patient dropdown availability to prevent duplicate assignments
 */
function updatePatientAvailability() {
    const patientSelects = document.querySelectorAll('select[name^="patient_"]');
    const selectedPatients = {};
    
    // Count selections for each patient
    patientSelects.forEach(function(select) {
        if (select.value) {
            selectedPatients[select.value] = (selectedPatients[select.value] || 0) + 1;
        }
    });
    
    // Update availability indicators
    patientSelects.forEach(function(select) {
        const studentIdMatch = select.name.match(/patient_(\d+)/);
        if (!studentIdMatch) return;
        
        const studentId = studentIdMatch[1];
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

/**
 * Validate and assign selected students
 * @returns {boolean} True if validation passes, false otherwise
 */
function assignSelectedStudents() {
    const selectedCheckboxes = document.querySelectorAll('.student-checkbox:checked');
    
    if (selectedCheckboxes.length === 0) {
        alert('Please select at least one student to assign.');
        return false;
    }
    
    // Verify that all selected students have a patient assigned
    let allHavePatients = true;
    const errorMessages = [];
    
    selectedCheckboxes.forEach(function(checkbox) {
        const row = checkbox.closest('tr');
        const studentNameElement = row.querySelector('.student-name');
        const studentName = studentNameElement ? studentNameElement.textContent.trim() : `Student ${checkbox.value}`;
        const patientSelect = row.querySelector('select[name^="patient_"]');
        
        if (!patientSelect || !patientSelect.value) {
            allHavePatients = false;
            errorMessages.push(`${studentName} is selected but has no patient assigned`);
        }
    });
    
    if (!allHavePatients) {
        alert('Error:\n' + errorMessages.join('\n'));
        return false;
    }
    
    return true;
}

/**
 * Toggle student selection when clicking on a row
 * @param {number} studentId - The ID of the student
 */
function toggleStudent(studentId) {
    let checkbox = document.getElementById('student_' + studentId);
    
    if (!checkbox) {
        const inputs = document.querySelectorAll('.student-checkbox');
        inputs.forEach(function(input) {
            if (input.value == studentId) {
                checkbox = input;
            }
        });
    }
    
    if (checkbox) {
        checkbox.checked = !checkbox.checked;
        updateCount();
    }
}

/**
 * Setup unassign button handler
 */
function setupUnassignButton() {
    const unassignBtn = document.getElementById('unassignBtn');
    
    if (unassignBtn) {
        unassignBtn.addEventListener('click', function() {
            const selectedCheckboxes = document.querySelectorAll('.student-checkbox:checked');
            
            if (selectedCheckboxes.length === 0) {
                alert('Please select students to unassign.');
                return;
            }
            
            if (!confirm('Are you sure you want to unassign the selected students? This will remove their access.')) {
                return;
            }
            
            const formAction = document.getElementById('formAction');
            const assignForm = document.getElementById('assignForm');
            
            if (formAction) {
                formAction.value = 'unassign';
            }
            
            if (assignForm) {
                assignForm.submit();
            }
        });
    }
}

/**
 * Initialize all event listeners and functionality when page loads
 */
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
        searchBox.addEventListener('keyup', searchStudents);
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
    const studentCheckboxes = document.querySelectorAll('.student-checkbox');
    studentCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            updateCount();
            
            // Update master checkbox state
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
    });
    
    // Set up patient dropdown change handlers for availability checking
    const patientSelects = document.querySelectorAll('select[name^="patient_"]');
    patientSelects.forEach(function(select) {
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
    
    // Initialize counts and availability on page load
    updateCount();
    updatePatientAvailability();
};