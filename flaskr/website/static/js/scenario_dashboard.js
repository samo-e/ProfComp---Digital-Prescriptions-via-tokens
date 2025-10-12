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

// Condition chooser for small toolbar: initialize from DOM and wire clicks
$(document).ready(function() {
  try {
    const $assignmentBtn = $("#condAssignmentSmall");
    const $examBtn = $("#condExamSmall");
    const $controls = $("#smallExamControls");
    const $hidden = $("#small_assignment_condition");

    function setMode(mode) {
      if (mode === 'exam') {
        $assignmentBtn.removeClass('active');
        $examBtn.addClass('active');
        // Show controls for exam
        $controls.removeClass('d-none');
        $hidden.val('exam');
        // update help text if provided
        try {
          var help = $controls.data('help-exam');
          if (help && $('#modeHelp').length) $('#modeHelp').text(help);
        } catch(e) {}
      } else {
        $examBtn.removeClass('active');
        $assignmentBtn.addClass('active');
        // For assignments we also want teachers to be able to set start/due times
        $controls.removeClass('d-none');
        $hidden.val('assignment');
        try {
          var help = $controls.data('help-assignment');
          if (help && $('#modeHelp').length) $('#modeHelp').text(help);
        } catch(e) {}
      }
    }

    // Wire clicks
    $assignmentBtn.on('click', function() { setMode('assignment'); });
    $examBtn.on('click', function() { setMode('exam'); });

    // Prefill mode based on initial hidden value or data attributes
    const initial = $hidden.val() || ($controls.length && $controls.data('exam-start') ? 'exam' : 'assignment');
    setMode(initial);

    // Prefill datetime inputs from data attributes if present and empty
    const startAttr = $controls.data('exam-start');
    const endAttr = $controls.data('exam-end');
    const $startInput = $('#small_exam_start');
    const $endInput = $('#small_exam_end');
    if (startAttr && $startInput && !$startInput.val()) {
      // startAttr is ISO like 'YYYY-MM-DDTHH:MM:SS' or 'YYYY-MM-DDTHH:MM'
      // Take the first 16 chars to match datetime-local format (YYYY-MM-DDTHH:MM)
      $startInput.val(String(startAttr).slice(0,16));
    }
    if (endAttr && $endInput && !$endInput.val()) {
      $endInput.val(String(endAttr).slice(0,16));
    }
    // If teacher previously saved, apply the persistent Saved UI
    try {
      var $modeForm = $('#modeForm');
      var $assignBtn = $('#assignMoreBtn');
      // helper to set assign button enabled/disabled (anchor)
      function setAssignEnabled(enabled) {
        try {
          if (!$assignBtn || !$assignBtn.length) return;
          if (enabled) {
            var href = $assignBtn.data('origHref');
            if (href) $assignBtn.attr('href', href);
            $assignBtn.removeClass('disabled');
            $assignBtn.data('disabled', false);
          } else {
            // store href then remove it to prevent navigation
            if (!$assignBtn.data('origHref')) $assignBtn.data('origHref', $assignBtn.attr('href'));
            try { $assignBtn.removeAttr('href'); } catch(e) {}
            $assignBtn.addClass('disabled');
            $assignBtn.data('disabled', true);
          }
        } catch(e) {}
      }
      // Save an explicit "editable snapshot" for the Save button so Edit reliably restores
      var $saveBtn = $('#modeSaveBtn');
      if ($saveBtn && $saveBtn.length) {
        try {
          if (!$saveBtn.data('editableClass')) {
            $saveBtn.data('editableClass', $saveBtn.attr('class'));
          }
          if (!$saveBtn.data('editableHtml')) {
            $saveBtn.data('editableHtml', $saveBtn.html());
          }
        } catch(e) {}
      }
  if ($modeForm && $modeForm.data('teacher-saved') && $modeForm.data('teacher-saved') == '1') {
        // remove any Saved/Edit elements that might have been inserted by inline template scripts
        try { $('#modeSavedBtn').remove(); } catch(e) {}
        try { $('#inlineEditBtn').remove(); } catch(e) {}
        // if the original Save button has already been transformed into a Saved look by inline script, hide it
        try {
          if ($saveBtn && $saveBtn.length) {
            var txt = ($saveBtn.html() || '').toString();
            var cls = ($saveBtn.attr('class') || '').toString();
            if (txt.indexOf('Saved') !== -1 || cls.indexOf('btn-warning') !== -1) {
              $saveBtn.hide();
            }
          }
        } catch(e) {}
  // visually disable chooser buttons and disable datetime inputs so clicking the time cannot edit them
  try { $assignmentBtn.addClass('disabled'); $examBtn.addClass('disabled'); } catch(e) {}
  try { if ($startInput && $startInput.length) $startInput.prop('disabled', true); } catch(e) {}
  try { if ($endInput && $endInput.length) $endInput.prop('disabled', true); } catch(e) {}
  try { if ($hidden && $hidden.length) $hidden.prop('readOnly', true); } catch(e) {}
        // create a separate Saved indicator button (so Saved and Save are different DOM elements)
        if (!$('#modeSavedBtn').length) {
          try {
            var $savedBtn = $('<button/>', { type: 'button', id: 'modeSavedBtn', class: 'btn btn-sm btn-warning ms-2' });
            $savedBtn.html('<i class="bi bi-check-lg"></i> Saved');
            // try to preserve the original Save button width and display to avoid layout shifts
            try {
              if ($saveBtn && $saveBtn.length) {
                var w = $saveBtn.outerWidth();
                if (w && w > 0) {
                  $savedBtn.css({'min-width': w + 'px', 'display': 'inline-block'});
                }
              }
            } catch(e) {}
            // Replace the original Save button in-place to preserve layout
            if ($saveBtn && $saveBtn.length) {
              $saveBtn.replaceWith($savedBtn);
            } else {
              $modeForm.append($savedBtn);
            }
          } catch(e) {}
        }
  // enable Assign Students when saved
  try { setAssignEnabled(true); } catch(e) {}
  // create inline Edit if not present
        if (!$('#inlineEditBtn').length) {
          var $edit = $('<button/>', { type: 'button', id: 'inlineEditBtn', class: 'btn btn-sm btn-outline-secondary ms-2', text: 'Edit' });
          // place Edit after the Saved indicator if present
          if ($('#modeSavedBtn').length) $('#modeSavedBtn').after($edit); else if ($saveBtn && $saveBtn.length) $saveBtn.after($edit); else $modeForm.append($edit);
          $edit.on('click', function(e) {
            try {
              // prevent any default form submit or event propagation
              try { e.preventDefault(); e.stopPropagation(); } catch(err) {}
              // re-enable chooser buttons visually
              $assignmentBtn.removeClass('disabled');
              $examBtn.removeClass('disabled');
              // re-enable datetime inputs and make hidden input editable
              try { if ($startInput && $startInput.length) $startInput.prop('disabled', false).focus(); } catch(e) {}
              try { if ($endInput && $endInput.length) $endInput.prop('disabled', false); } catch(e) {}
              try { if ($hidden && $hidden.length) $hidden.prop('readOnly', false); } catch(e) {}
              // remove the Saved indicator
              try { $('#modeSavedBtn').remove(); } catch(e) {}
              // disable Assign until the teacher saves again
              try { setAssignEnabled(false); } catch(e) {}
              // create a fresh Save button (so we don't reuse the same DOM element)
              try {
                var editableClass = ($saveBtn && $saveBtn.length && $saveBtn.data('editableClass')) ? $saveBtn.data('editableClass') : 'btn btn-sm btn-success ms-2';
                var editableHtml = ($saveBtn && $saveBtn.length && $saveBtn.data('editableHtml')) ? $saveBtn.data('editableHtml') : 'Save';
                // remove any existing element with that id to avoid duplicates
                $('#modeSaveBtn').remove();
                var $newSave = $('<button/>', { type: 'submit', id: 'modeSaveBtn', class: editableClass });
                $newSave.html(editableHtml);
                // insert the new Save where the Edit button is currently (Edit will be removed below)
                $edit.before($newSave);
                // ensure the form submit handler will pick up the new button normally (no extra binding required)
              } catch(e) {}
              // remove edit button
              $edit.remove();
              return false;
            } catch(e) {}
          });
        }
      }
      else {
        // not saved -> ensure Assign is disabled to force teacher to save first
        try { setAssignEnabled(false); } catch(e) {}
      }
    } catch(e) {}
    // Optimistic UI: when the mode form is submitted, immediately show Saved state and lock inputs
    try {
      var $modeForm = $('#modeForm');
      if ($modeForm && $modeForm.length) {
        $modeForm.on('submit', function() {
          try {
            var $saveBtn = $('#modeSaveBtn');
            if ($saveBtn && $saveBtn.length) {
              // store original only if not already stored (don't overwrite)
              if (!$saveBtn.data('origClass')) {
                $saveBtn.data('origClass', $saveBtn.attr('class'));
              }
              if (!$saveBtn.data('origHtml')) {
                $saveBtn.data('origHtml', $saveBtn.html());
              }
              // visually mark as pending-saved. Do NOT disable inputs here because disabled inputs are not sent in form POST.
              $saveBtn.attr('class', 'btn btn-sm btn-warning ms-2');
              $saveBtn.html('<i class="bi bi-hourglass-split"></i> Saving...');
              $saveBtn.prop('disabled', true);
            }
          } catch (e) {}
          // Allow the form to submit normally (no preventDefault)
        });
      }
    } catch (e) {
      console.warn('modeForm submit handler init failed', e);
    }
  } catch (e) {
    // fail silently
    console.warn('Chooser init failed', e);
  }
});
/**
 * Initialize the scenario dashboard page
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add any initialization code here if needed
    console.log('Scenario dashboard loaded');
});
