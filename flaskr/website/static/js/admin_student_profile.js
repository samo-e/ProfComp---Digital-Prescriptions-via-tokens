// DEBUG: Student profile assign/unassign teacher modal logic
document.addEventListener("DOMContentLoaded", function () {
  // DEBUG: Modal and button element references
  var modal = document.getElementById("assignTeacherModal");
  var btn = document.getElementById("assign-teachers-btn");
  var closeBtn = document.getElementById("closeTeacherModal");
  var searchInput = document.getElementById("teacher-search");
  var teachersList = document.getElementById("teachers-list");

  // DEBUG: Modal open/close handlers
  if (btn) {
    btn.onclick = function () {
      // DEBUG: Open assign teacher modal
      modal.style.display = "block";
    };
  }

  if (closeBtn) {
    closeBtn.onclick = function () {
      // DEBUG: Close assign teacher modal
      modal.style.display = "none";
    };
  }

  window.onclick = function (event) {
    if (event.target == modal) {
      // DEBUG: Click outside modal closes it
      modal.style.display = "none";
    }
  };

  // DEBUG: Teacher search filter
  if (searchInput && teachersList) {
    searchInput.addEventListener("keyup", function () {
      var filter = searchInput.value.toLowerCase();
      var teachers = teachersList.getElementsByTagName("li");
      Array.from(teachers).forEach(function (teacher) {
        var text = teacher.textContent || teacher.innerText;
        teacher.style.display =
          text.toLowerCase().indexOf(filter) > -1 ? "" : "none";
      });
    });
  }

  // --- AJAX assign teacher logic ---
  // DEBUG: Setup assign-teacher-form AJAX handlers
  const submitting = new WeakSet();
  document.querySelectorAll(".assign-teacher-form").forEach(function (form) {
    form.addEventListener(
      "submit",
      function (e) {
        e.preventDefault();
        if (submitting.has(form)) return;
        submitting.add(form);
        // DEBUG: Assign teacher form submitted
        const formData = new FormData(form);
        const button = form.querySelector('button[type="submit"]');
        const originalText = button ? button.textContent : "";
        const li = form.closest("li");
        const teacherNameEl = li ? li.querySelector("span.teacher-name") : null;
        const teacherName = teacherNameEl ? teacherNameEl.textContent : "";
        const teacherId = form.querySelector('input[name="teacher_id"]').value;
        const studentId = form.querySelector('input[name="student_id"]').value;
        if (button) {
          button.disabled = true;
          button.textContent = "Assigning...";
        }
        fetch(form.action, {
          method: "POST",
          body: formData,
          headers: { "X-Requested-With": "XMLHttpRequest" },
        })
          .then((r) => r.json())
          .then((data) => {
            if (data && data.success && data.student) {
              // DEBUG: Assign teacher success
              if (button) {
                button.textContent = "Assigned";
                button.disabled = true;
                button.style.opacity = "0.5";
              }
              if (li) {
                li.style.opacity = "0.5";
              }
              // Update assigned teachers list live
              const assignedList = document.getElementById(
                "assigned-teachers-list"
              );
              if (assignedList) {
                const firstLi = assignedList.querySelector("li");
                if (
                  firstLi &&
                  firstLi.textContent.includes("No teachers assigned")
                ) {
                  assignedList.removeChild(firstLi);
                }
                // DEBUG: Add teacher to assigned list
                const newLi = document.createElement("li");
                // Use teacher name/email from response if available, else fallback to teacherName
                const teacherNameResp =
                  data.teacher && data.teacher.name
                    ? data.teacher.name
                    : teacherName;
                const teacherEmailResp =
                  data.teacher && data.teacher.email ? data.teacher.email : "";
                const teacherIdResp =
                  data.teacher && data.teacher.id ? data.teacher.id : teacherId;
                newLi.className =
                  "list-group-item d-flex justify-content-between align-items-center";
                newLi.innerHTML = `
<span>${teacherNameResp} ${
                  teacherEmailResp ? "(" + teacherEmailResp + ")" : ""
                }</span>
<form class="unassign-teacher-form" method="post" action="/admin/unassign_student" style="display:inline;">
    <input type="hidden" name="csrf_token" value="${data.csrf_token}">
    <input type="hidden" name="student_id" value="${studentId}">
    <input type="hidden" name="teacher_id" value="${teacherIdResp}">
    <button type="submit" class="btn btn-sm btn-outline-danger">Unassign</button>
</form>`;
                assignedList.appendChild(newLi);
              }
            } else {
              // DEBUG: Assign teacher failed
              if (button) {
                button.disabled = false;
                button.textContent = originalText || "Assign";
              }
            }
          })
          .catch((err) => {
            console.error("[Assign] AJAX error:", err);
            if (button) {
              button.disabled = false;
              button.textContent = originalText || "Assign";
            }
          })
          .finally(() => {
            submitting.delete(form);
          });
      },
      { once: false }
    );
  });

  // --- AJAX unassign teacher logic (event delegation) ---
  // DEBUG: Setup unassign-teacher-form AJAX handler (event delegation)
  const unassignSubmitting = new WeakSet();
  document.addEventListener("submit", function (e) {
    const form = e.target.closest(".unassign-teacher-form");
    if (!form) return;
    e.preventDefault();
    if (unassignSubmitting.has(form)) return;
    unassignSubmitting.add(form);
    // DEBUG: Unassign teacher form submitted
    const formData = new FormData(form);
    const li = form.closest("li");
    const button = form.querySelector('button[type="submit"]');
    const originalText = button ? button.textContent : "";
    const teacherId = form.querySelector('input[name="teacher_id"]').value;
    // Show loading state
    if (button) {
      button.disabled = true;
      button.textContent = "Unassigning...";
    }
    fetch(form.action, {
      method: "POST",
      body: formData,
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((r) => r.json())
      .then((data) => {
        if (data && data.success) {
          // DEBUG: Unassign teacher success
          if (li) li.remove();
          // Always get the assignedList after removal
          const assignedList = document.getElementById(
            "assigned-teachers-list"
          );
          if (assignedList && assignedList.children.length === 0) {
            const placeholder = document.createElement("li");
            placeholder.className = "list-group-item text-muted";
            placeholder.innerHTML = "<span>No teachers assigned.</span>";
            assignedList.appendChild(placeholder);
          }
          // Always update the assign button in the modal for this teacher
          document
            .querySelectorAll("#teachers-list .assign-teacher-form")
            .forEach(function (assignForm) {
              const assignTeacherId = assignForm.querySelector(
                'input[name="teacher_id"]'
              ).value;
              if (assignTeacherId === teacherId) {
                const assignButton = assignForm.querySelector(
                  'button[type="submit"]'
                );
                if (assignButton) {
                  // DEBUG: Reset assign button after unassign
                  assignButton.disabled = false;
                  assignButton.innerHTML = "Assign";
                  assignButton.style.opacity = "1";
                }
                const assignLi = assignForm.closest("li");
                if (assignLi) {
                  assignLi.style.opacity = "1";
                }
              }
            });
        } else {
          // DEBUG: Unassign teacher failed
          if (button) {
            button.disabled = false;
            button.textContent = originalText || "Unassign";
          }
        }
      })
      .catch((err) => {
        console.error("[Unassign] AJAX error:", err);
        if (button) {
          button.disabled = false;
          button.textContent = originalText || "Unassign";
        }
      })
      .finally(() => {
        unassignSubmitting.delete(form);
      });
  });
});

function confirmDelete(userName, userRole) {
  if (
    confirm(
      "Are you sure you want to delete this account?\n\nUser: " +
        userName +
        "\nRole: " +
        userRole +
        "\n\nThis action cannot be undone!"
    )
  ) {
    $("#delete-user-form").submit();
  }
}
