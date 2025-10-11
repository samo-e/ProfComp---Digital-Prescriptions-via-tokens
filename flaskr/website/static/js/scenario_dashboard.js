// flaskr/website/static/js/scenario_dashboard.js

/**
 * Toggle scenario name edit mode
 */
function toggleNameEdit() {
    if (typeof $ !== 'undefined') {
        $("#name-display").toggleClass("d-none");
        $("#name-edit").toggleClass("d-none");
        $("#edit-name-btn").toggleClass("d-none");
    } else {
        const nameDisplay = document.getElementById('name-display');
        const nameEdit = document.getElementById('name-edit');
        const editBtn = document.getElementById('edit-name-btn');
        
        if (nameDisplay) nameDisplay.classList.toggle('d-none');
        if (nameEdit) nameEdit.classList.toggle('d-none');
        if (editBtn) editBtn.classList.toggle('d-none');
    }
}

/**
 * Cancel name edit and revert to display mode
 */
function cancelNameEdit() {
    if (typeof $ !== 'undefined') {
        $("#name-display, #edit-name-btn").removeClass("d-none");
        $("#name-edit").addClass("d-none");
    } else {
        const nameDisplay = document.getElementById('name-display');
        const nameEdit = document.getElementById('name-edit');
        const editBtn = document.getElementById('edit-name-btn');
        
        if (nameDisplay) nameDisplay.classList.remove('d-none');
        if (nameEdit) nameEdit.classList.add('d-none');
        if (editBtn) editBtn.classList.remove('d-none');
    }
}

/**
 * Toggle question/instructions edit mode
 */
function toggleQuestionEdit() {
    if (typeof $ !== 'undefined') {
        $("#question-display, #question-edit").toggleClass("d-none");
    } else {
        const questionDisplay = document.getElementById('question-display');
        const questionEdit = document.getElementById('question-edit');
        
        if (questionDisplay) questionDisplay.classList.toggle('d-none');
        if (questionEdit) questionEdit.classList.toggle('d-none');
    }
}

/**
 * Cancel question edit and revert to display mode
 */
function cancelQuestionEdit() {
    if (typeof $ !== 'undefined') {
        $("#question-display").removeClass("d-none");
        $("#question-edit").addClass("d-none");
    } else {
        const questionDisplay = document.getElementById('question-display');
        const questionEdit = document.getElementById('question-edit');
        
        if (questionDisplay) questionDisplay.classList.remove('d-none');
        if (questionEdit) questionEdit.classList.add('d-none');
    }
}

/**
 * Toggle description edit mode
 */
function toggleDescriptionEdit() {
    if (typeof $ !== 'undefined') {
        $("#description-edit").toggleClass("d-none");
    } else {
        const descEdit = document.getElementById('description-edit');
        if (descEdit) descEdit.classList.toggle('d-none');
    }
}

/**
 * Cancel description edit and hide edit form
 */
function cancelDescriptionEdit() {
    if (typeof $ !== 'undefined') {
        $("#description-edit").addClass("d-none");
    } else {
        const descEdit = document.getElementById('description-edit');
        if (descEdit) descEdit.classList.add('d-none');
    }
}

/**
 * Toggle patient selection mode
 */
function togglePatientSelection() {
    if (typeof $ !== 'undefined') {
        $("#patient-display, #patient-selection").toggleClass("d-none");
    } else {
        const patientDisplay = document.getElementById('patient-display');
        const patientSelection = document.getElementById('patient-selection');
        
        if (patientDisplay) patientDisplay.classList.toggle('d-none');
        if (patientSelection) patientSelection.classList.toggle('d-none');
    }
}

/**
 * Cancel patient selection and revert to display mode
 */
function cancelPatientSelection() {
    if (typeof $ !== 'undefined') {
        $("#patient-display").removeClass("d-none");
        $("#patient-selection").addClass("d-none");
    } else {
        const patientDisplay = document.getElementById('patient-display');
        const patientSelection = document.getElementById('patient-selection');
        
        if (patientDisplay) patientDisplay.classList.remove('d-none');
        if (patientSelection) patientSelection.classList.add('d-none');
    }
}

/**
 * Initialize the scenario dashboard page
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add any initialization code here if needed
    console.log('Scenario dashboard loaded');
});