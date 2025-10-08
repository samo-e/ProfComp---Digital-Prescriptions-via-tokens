// flaskr/website/static/js/teacher_dashboard.js

function selectAllToggle() {
    const selectAll = document.getElementById('select-all');
    const checkboxes = document.getElementsByTagName('input');
    
    for (let i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].type === 'checkbox' && checkboxes[i].id && checkboxes[i].id.indexOf('scenario-check-') === 0) {
            checkboxes[i].checked = selectAll.checked;
        }
    }
}

function bulkArchive() {
    const checkboxes = document.getElementsByTagName('input');
    let selected = 0;
    
    for (let i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].type === 'checkbox' && checkboxes[i].id && checkboxes[i].id.indexOf('scenario-check-') === 0 && checkboxes[i].checked) {
            selected++;
        }
    }
    
    if (selected === 0) {
        alert('Please select scenarios to archive');
        return;
    }
    
    if (confirm('Are you sure you want to archive ' + selected + ' selected scenario(s)?')) {
        alert('Bulk archive functionality to be implemented');
    }
}

function bulkExport() {
    const checkboxes = document.getElementsByTagName('input');
    let selected = 0;
    
    for (let i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].type === 'checkbox' && checkboxes[i].id && checkboxes[i].id.indexOf('scenario-check-') === 0 && checkboxes[i].checked) {
            selected++;
        }
    }
    
    if (selected === 0) {
        alert('Please select scenarios to export');
        return;
    }
    
    alert('Bulk export functionality to be implemented');
}

function confirmDelete(scenarioId) {
    if (confirm('Are you sure you want to archive this scenario?')) {
        const form = document.getElementById('delete-form-' + scenarioId);
        if (form) {
            form.submit();
        }
    }
}

window.onload = function() {
    // Set up select all checkbox
    const selectAllBox = document.getElementById('select-all');
    if (selectAllBox) {
        selectAllBox.onchange = selectAllToggle;
    }
    
    // Set up bulk action buttons
    const deleteBtn = document.getElementById('bulk-delete');
    if (deleteBtn) {
        deleteBtn.onclick = bulkArchive;
    }
    
    const exportBtn = document.getElementById('bulk-export');
    if (exportBtn) {
        exportBtn.onclick = bulkExport;
    }
    
    // Set up individual delete buttons
    const deleteBtns = document.getElementsByClassName('delete-btn');
    for (let i = 0; i < deleteBtns.length; i++) {
        (function(btn) {
            btn.onclick = function() {
                const scenarioId = btn.getAttribute('data-scenario-id');
                confirmDelete(scenarioId);
            };
        })(deleteBtns[i]);
    }
    
    // Set up create first scenario link
    const createLink = document.getElementById('create-first-scenario');
    if (createLink) {
        createLink.onclick = function(e) {
            e.preventDefault();
            const form = document.querySelector('form[action="{{ url_for("views.create_scenario") }}"]');
            if (form) {
                const button = form.querySelector('button[type="submit"]');
                if (button) {
                    button.click();
                }
            }
        };
    }
};