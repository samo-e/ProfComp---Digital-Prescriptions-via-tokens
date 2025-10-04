$(function () {
  // Search functionality
  document
    .getElementById("studentSearch")
    .addEventListener("input", function () {
      const searchTerm = this.value.toLowerCase();
      const rows = document.querySelectorAll("#studentsTable tbody tr");

      rows.forEach((row) => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? "" : "none";
      });
    });

  // Select all functionality
  document.getElementById("select-all").addEventListener("change", function () {
    const checkboxes = document.querySelectorAll(".student-checkbox");
    checkboxes.forEach((cb) => (cb.checked = this.checked));
    toggleBulkActions();
  });

  // Individual checkbox handling
  document.querySelectorAll(".student-checkbox").forEach((cb) => {
    cb.addEventListener("change", toggleBulkActions);
  });
});

function toggleBulkActions() {
  var $checked = $(".student-checkbox:checked");
  var $bulkActions = $(".bulk-actions");

  $bulkActions.toggleClass("d-none", $checked.length === 0);
}

// Action functions
function viewStudent(id) {
  // Implement view student details
  console.log("View student:", id);
}

function assignScenario(id) {
  // Implement assign scenario
  console.log("Assign scenario to student:", id);
}

function editStudent(id) {
  // Implement edit student
  console.log("Edit student:", id);
}

function removeStudent(id) {
  // Implement remove student
  if (confirm("Are you sure you want to remove this student?")) {
    console.log("Remove student:", id);
  }
}

function addStudent() {
  // Implement add student
  const form = document.getElementById("addStudentForm");
  if (form.checkValidity()) {
    console.log("Add new student");
    // Close modal after success
    bootstrap.Modal.getInstance(
      document.getElementById("addStudentModal")
    ).hide();
  }
}
