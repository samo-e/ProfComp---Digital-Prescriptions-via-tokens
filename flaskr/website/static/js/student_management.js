// Utility functions
function showLoading() {
  $("#loadingOverlay").show();
}

function hideLoading() {
  $("#loadingOverlay").hide();
}

function showAlert(message, type = "success") {
  const alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
  alertDiv.style.zIndex = "9999";
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
  document.body.appendChild(alertDiv);

  setTimeout(() => {
    alertDiv.remove();
  }, 5000);
}

// Get CSRF token from meta tag
function getCSRFToken() {
  return document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute("content");
}

// Search functionality
function searchStudents() {
  const input = document.getElementById("searchInput").value.toLowerCase();
  const rows = document.querySelectorAll(".student-row");

  rows.forEach((row) => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(input) ? "" : "none";
  });
}

// Add student
async function addStudent() {
  const firstName = document.getElementById("newFirstName").value.trim();
  const lastName = document.getElementById("newLastName").value.trim();
  const email = document.getElementById("newEmail").value.trim();
  const password = document.getElementById("newPassword").value;

  if (!firstName || !lastName || !email || !password) {
    showAlert("Please fill in all required fields", "danger");
    return;
  }

  if (password.length < 8) {
    showAlert("Password must be at least 8 characters long", "danger");
    return;
  }

  showLoading();

  try {
    const response = await fetch("/students/add", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        email: email,
        password: password,
      }),
    });

    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      throw new Error("Server returned non-JSON response");
    }

    const result = await response.json();

    if (result.success) {
      showAlert("Student added successfully!", "success");
      bootstrap.Modal.getInstance(
        document.getElementById("addStudentModal")
      ).hide();
      setTimeout(() => location.reload(), 1500);
    } else {
      showAlert(result.message || "Failed to add student", "danger");
    }
  } catch (error) {
    showAlert(
      "An error occurred. Please try again. " + error.message,
      "danger"
    );
    console.error("Error:", error);
  } finally {
    hideLoading();
  }
}

// View student details
async function viewStudent(id) {
  showLoading();

  try {
    const response = await fetch(`/students/${id}/view`);
    const result = await response.json();

    if (result.success) {
      const student = result.student;
      const modalBody = document.getElementById("studentDetailsBody");

      modalBody.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6>Personal Information</h6>
                        <table class="table table-sm">
                            <tr><td><strong>Name:</strong></td><td>${
                              student.first_name
                            } ${student.last_name}</td></tr>
                            <tr><td><strong>Email:</strong></td><td>${
                              student.email
                            }</td></tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h6>Statistics</h6>
                        <table class="table table-sm">
                            <tr><td><strong>Total Scenarios:</strong></td><td>${
                              student.total_scenarios || 0
                            }</td></tr>
                            <tr><td><strong>Completed:</strong></td><td>${
                              student.completed_scenarios || 0
                            }</td></tr>
                        </table>
                    </div>
                </div>
                ${
                  student.assigned_scenarios &&
                  student.assigned_scenarios.length > 0
                    ? `
                <div class="mt-3">
                    <h6>Assigned Scenarios</h6>
                    <div class="list-group">
                        ${student.assigned_scenarios
                          .map(
                            (s) => `
                            <div class="list-group-item">
                                <div class="d-flex justify-content-between align-items-center">
                                    <strong>${s.name}</strong>
                                    <span class="badge bg-${
                                      s.status === "completed"
                                        ? "success"
                                        : "warning"
                                    }">${s.status}</span>
                                </div>
                            </div>
                        `
                          )
                          .join("")}
                    </div>
                </div>
                `
                    : '<p class="text-muted mt-3">No scenarios assigned yet.</p>'
                }
            `;
    } else {
      showAlert(result.message || "Failed to load student details", "danger");
    }
  } catch (error) {
    showAlert("An error occurred. Please try again.", "danger");
    console.error("Error:", error);
  } finally {
    hideLoading();
  }
}

// Delete student
async function deleteStudent(id) {
  if (
    !confirm(
      "Are you sure you want to delete this student? This action cannot be undone."
    )
  ) {
    return;
  }

  showLoading();

  try {
    const response = await fetch(`/students/${id}/delete`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
    });

    const result = await response.json();

    if (result.success) {
      showAlert("Student deleted successfully!", "success");
      setTimeout(() => location.reload(), 1500);
    } else {
      showAlert(result.message || "Failed to delete student", "danger");
    }
  } catch (error) {
    showAlert("An error occurred. Please try again.", "danger");
    console.error("Error:", error);
  } finally {
    hideLoading();
  }
}

(function () {
  // Reset form when modal is closed
  const addStudentModal = $("#addStudentModal");
  if (addStudentModal.length) {
    addStudentModal.on("hidden.bs.modal", function () {
      $("#addStudentForm")[0].reset();
    });
  }
})();

function toggle_all_students_check_boxes(is_main) {
  let main_check = $("#select-all");
  let other_checks = $(".student-checkbox");

  if (is_main) {
    let is_checked = main_check.prop("checked");
    main_check.prop("indeterminate", false);
    other_checks.prop("checked", is_checked);
  } else {
    let total = other_checks.length;
    let checked = other_checks.filter(":checked").length;

    if (checked === 0) {
      main_check.prop({ checked: false, indeterminate: false });
    } else if (checked === total) {
      main_check.prop({ checked: true, indeterminate: false });
    } else {
      main_check.prop({ checked: false, indeterminate: true });
    }
  }
}
