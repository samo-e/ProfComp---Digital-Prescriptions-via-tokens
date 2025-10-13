// flaskr/website/static/js/patient_dashboard.js

/**
 * Initialize patient dashboard functionality
 */
document.addEventListener("DOMContentLoaded", function () {
  initializeSearch();
  initializeSelectAll();
  initializeIndividualCheckboxes();
  initializeBulkDelete();
  initializeDeleteButtons();
});

/**
 * Initialize search functionality for patient table
 */
function initializeSearch() {
  const searchInput = document.getElementById("patientSearch");

  if (searchInput) {
    searchInput.addEventListener("input", function () {
      const searchTerm = this.value.toLowerCase();
      const rows = document.querySelectorAll("#patientsTable tbody tr");

      rows.forEach(function (row) {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? "" : "none";
      });
    });
  }
}

/**
 * Initialize select all checkbox functionality
 */
function initializeSelectAll() {
  const selectAllCheckbox = document.getElementById("select-all");

  if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener("change", function () {
      const checkboxes = document.querySelectorAll(".patient-checkbox");
      checkboxes.forEach(function (cb) {
        cb.checked = selectAllCheckbox.checked;
      });
      toggleBulkActions();
    });
  }
}

/**
 * Initialize individual checkbox handling
 */
function initializeIndividualCheckboxes() {
  const checkboxes = document.querySelectorAll(".patient-checkbox");

  checkboxes.forEach(function (cb) {
    cb.addEventListener("change", toggleBulkActions);
  });
}

/**
 * Toggle visibility of bulk action buttons based on selection
 */
function toggleBulkActions() {
  const checked = document.querySelectorAll(".patient-checkbox:checked");
  const bulkActions = document.querySelector(".bulk-actions");

  if (bulkActions) {
    if (typeof $ !== "undefined") {
      $(bulkActions).toggleClass("d-none", checked.length === 0);
    } else {
      if (checked.length === 0) {
        bulkActions.classList.add("d-none");
      } else {
        bulkActions.classList.remove("d-none");
      }
    }
  }
}

/**
 * Initialize bulk delete functionality
 */
function initializeBulkDelete() {
  const bulkDeleteBtn = document.getElementById("bulk-delete");

  if (bulkDeleteBtn) {
    bulkDeleteBtn.addEventListener("click", handleBulkDelete);
  }
}

/**
 * Handle bulk delete action
 */
function handleBulkDelete() {
  const checked = document.querySelectorAll(".patient-checkbox:checked");

  if (checked.length === 0) {
    alert("Please select patients to delete.");
    return;
  }

  // Get patient names for confirmation message
  const patientNames = Array.from(checked).map(function (cb) {
    const row = cb.closest("tr");
    const nameCell = row.querySelector("td:nth-child(2)");
    return nameCell.textContent.trim().split("\n")[0];
  });

  const confirmMessage =
    "Are you sure you want to delete " +
    checked.length +
    " patient(s)?\n\n" +
    "This will permanently delete:\n" +
    patientNames.join("\n") +
    "\n\n" +
    "This action cannot be undone and will also delete all related prescriptions, ASL records, and submissions.";

  if (confirm(confirmMessage)) {
    const form = document.getElementById("bulk-delete-form");

    // Clear any existing hidden inputs
    const existingInputs = form.querySelectorAll('input[name="patient_ids"]');
    existingInputs.forEach(function (input) {
      input.remove();
    });

    // Add patient IDs to the form
    checked.forEach(function (cb) {
      const input = document.createElement("input");
      input.type = "hidden";
      input.name = "patient_ids";
      input.value = cb.value;
      form.appendChild(input);
    });

    form.submit();
  }
}

/**
 * Initialize individual delete buttons with confirmation
 */
function initializeDeleteButtons() {
  const deleteBtns = document.querySelectorAll(".delete-btn");

  deleteBtns.forEach(function (btn) {
    const form = btn.closest("form");
    if (form) {
      form.addEventListener("submit", function (e) {
        const patientName =
          form.getAttribute("data-patient-name") || "this patient";
        const confirmed = confirm(
          "Are you sure you want to delete " +
            patientName +
            "?\n\n" +
            "This action cannot be undone and will also delete all related data."
        );

        if (!confirmed) {
          e.preventDefault();
        }
      });
    }
  });
}
