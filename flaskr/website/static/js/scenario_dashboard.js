function toggleNameEdit() {
  $("#name-display").toggleClass("d-none");
  $("#name-edit").toggleClass("d-none");
  $("#edit-name-btn").toggleClass("d-none");
}

function cancelNameEdit() {
  $("#name-display, #edit-name-btn").removeClass("d-none");
  $("#name-edit").addClass("d-none");
}

// Toggle question edit
function toggleQuestionEdit() {
  $("#question-display, #question-edit").toggleClass("d-none");
}

function cancelQuestionEdit() {
  $("#question-display").removeClass("d-none");
  $("#question-edit").addClass("d-none");
}

// Toggle description edit
function toggleDescriptionEdit() {
  $("#description-edit").toggleClass("d-none");
}

function cancelDescriptionEdit() {
  $("#description-edit").addClass("d-none");
}

// Toggle patient selection
function togglePatientSelection() {
  $("#patient-display, #patient-selection").toggleClass("d-none");
}

function cancelPatientSelection() {
  $("#patient-display").removeClass("d-none");
  $("#patient-selection").addClass("d-none");
}
