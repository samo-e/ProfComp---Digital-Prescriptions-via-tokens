/**
 * Toggle select all checkboxes for scenarios
 */
function selectAllToggle() {
  const selectAll = document.getElementById("select-all");
  const checkboxes = document.getElementsByTagName("input");

  for (let i = 0; i < checkboxes.length; i++) {
    if (
      checkboxes[i].type === "checkbox" &&
      checkboxes[i].id &&
      checkboxes[i].id.indexOf("scenario-") === 0
    ) {
      checkboxes[i].checked = selectAll.checked;
    }
  }
}

/**
 * Archive selected scenarios in bulk
 */
function bulkArchive() {
  const checkboxes = document.getElementsByTagName("input");
  let selected = 0;

  for (let i = 0; i < checkboxes.length; i++) {
    if (
      checkboxes[i].type === "checkbox" &&
      checkboxes[i].id &&
      checkboxes[i].id.indexOf("scenario-") === 0 &&
      checkboxes[i].checked
    ) {
      selected++;
    }
  }

  if (selected === 0) {
    alert("Please select scenarios to archive");
    return;
  }

  if (
    confirm(
      "Are you sure you want to archive " + selected + " selected scenario(s)?"
    )
  ) {
    alert("Bulk archive functionality to be implemented");
    // TODO: Implement actual bulk archive functionality
    // This would require a backend endpoint to handle bulk operations
  }
}

/**
 * Export selected scenarios marks in bulk
 * Downloads a separate CSV file for each selected scenario
 */
function bulkExport() {
  const checkboxes = document.getElementsByTagName("input");
  const selectedScenarioIds = [];

  // Collect all selected scenario IDs
  for (let i = 0; i < checkboxes.length; i++) {
    if (
      checkboxes[i].type === "checkbox" &&
      checkboxes[i].id &&
      checkboxes[i].id.indexOf("scenario-") === 0 &&
      checkboxes[i].checked
    ) {
      // Extract scenario ID from checkbox id (format: scenario-123)
      const scenarioId = checkboxes[i].id.replace("scenario-", "");
      selectedScenarioIds.push(scenarioId);
    }
  }

  if (selectedScenarioIds.length === 0) {
    alert("Please select scenarios to export");
    return;
  }

  // Show confirmation with count
  if (
    !confirm(
      `Export marks for ${selectedScenarioIds.length} selected scenario(s)?\nA separate CSV file will be downloaded for each scenario.`
    )
  ) {
    return;
  }

  // Download CSV for each selected scenario with a small delay between downloads
  // to prevent browser blocking multiple simultaneous downloads
  selectedScenarioIds.forEach((scenarioId, index) => {
    setTimeout(() => {
      // Create a temporary link and trigger download
      const downloadUrl = `/api/export-marks/${scenarioId}`;
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = ""; // Let the server specify the filename
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }, index * 500); // 500ms delay between each download
  });

  // Show success message
  setTimeout(() => {
    alert(
      `Started downloading ${selectedScenarioIds.length} CSV file(s). Check your downloads folder.`
    );
  }, selectedScenarioIds.length * 500 + 100);
}

/**
 * Confirm deletion of a single scenario
 * @param {number} scenarioId - The ID of the scenario to delete
 */
function confirmDelete(scenarioId) {
  if (confirm("Are you sure you want to archive this scenario?")) {
    const form = document.getElementById("delete-form-" + scenarioId);
    if (form) {
      form.submit();
    }
  }
}

/**
 * Initialize the page when DOM is loaded
 */
window.onload = function () {
  // Set up select all checkbox
  const selectAllBox = document.getElementById("select-all");
  if (selectAllBox) {
    selectAllBox.onchange = selectAllToggle;
  }

  // Set up bulk action buttons
  const deleteBtn = document.getElementById("bulk-delete");
  if (deleteBtn) {
    deleteBtn.onclick = bulkArchive;
  }

  const exportBtn = document.getElementById("bulk-export");
  if (exportBtn) {
    exportBtn.onclick = bulkExport;
  }

  // Set up individual delete buttons
  const deleteBtns = document.getElementsByClassName("delete-btn");
  for (let i = 0; i < deleteBtns.length; i++) {
    (function (btn) {
      btn.onclick = function () {
        const scenarioId = btn.getAttribute("data-scenario-id");
        confirmDelete(scenarioId);
      };
    })(deleteBtns[i]);
  }

  // Set up create first scenario link
  const createLink = document.getElementById("create-first-scenario");
  if (createLink) {
    createLink.onclick = function (e) {
      e.preventDefault();
      const forms = document.querySelectorAll(
        'form[action*="create_scenario"]'
      );
      if (forms.length > 0) {
        const button = forms[0].querySelector('button[type="submit"]');
        if (button) {
          button.click();
        }
      }
    };
  }
};

// Use the scenario-checkbox class so selectors are robust against id/name changes
function selectAllToggle() {
  let selectAll = document.getElementById("select-all");
  let boxes = document.querySelectorAll(".scenario-checkbox");
  boxes.forEach(function (cb) {
    cb.checked = selectAll.checked;
  });
  updateSelectAllState();
}

function updateSelectAllState() {
  let selectAll = document.getElementById("select-all");
  if (!selectAll) return;
  let boxes = document.querySelectorAll(".scenario-checkbox");
  let total = boxes.length;
  let checked = Array.prototype.filter.call(boxes, function (b) {
    return b.checked;
  }).length;
  selectAll.checked = total > 0 && checked === total;
  selectAll.indeterminate = checked > 0 && checked < total;
}

function countSelected() {
  let boxes = document.querySelectorAll(".scenario-checkbox");
  return Array.prototype.filter.call(boxes, function (b) {
    return b.checked;
  }).length;
}

function bulkArchive() {
  let selected = countSelected();
  if (selected === 0) {
    alert("Please select scenarios to archive");
    return;
  }
  if (
    confirm(
      "Are you sure you want to archive " + selected + " selected scenario(s)?"
    )
  ) {
    alert("Bulk archive functionality to be implemented");
  }
}

function bulkExport() {
  let selected = countSelected();
  if (selected === 0) {
    alert("Please select scenarios to export");
    return;
  }
  alert("Bulk export functionality to be implemented");
}

function confirmDelete(scenarioId) {
  if (confirm("Are you sure you want to archive this scenario?")) {
    let form = document.getElementById("delete-form-" + scenarioId);
    if (form) {
      form.submit();
    }
  }
}

window.onload = function () {
  // Set up select all checkbox
  let selectAllBox = document.getElementById("select-all");
  if (selectAllBox) {
    selectAllBox.addEventListener("change", selectAllToggle);
  }

  // Keep select-all state in sync when individual boxes change
  let scenarioBoxes = document.querySelectorAll(".scenario-checkbox");
  scenarioBoxes.forEach(function (cb) {
    cb.addEventListener("change", updateSelectAllState);
  });

  // Set up bulk action buttons
  let deleteBtn = document.getElementById("bulk-delete");
  if (deleteBtn) {
    deleteBtn.addEventListener("click", bulkArchive);
  }

  let exportBtn = document.getElementById("bulk-export");
  if (exportBtn) {
    exportBtn.addEventListener("click", bulkExport);
  }

  // Set up individual delete buttons
  let deleteBtns = document.getElementsByClassName("delete-btn");
  for (let i = 0; i < deleteBtns.length; i++) {
    (function (btn) {
      btn.onclick = function () {
        let scenarioId = btn.getAttribute("data-scenario-id");
        confirmDelete(scenarioId);
      };
    })(deleteBtns[i]);
  }

  // Set up create first scenario link
  let createLink = document.getElementById("create-first-scenario");
  if (createLink) {
    createLink.onclick = function (e) {
      e.preventDefault();
      let form = document.querySelector(
        'form[action="{{ url_for("views.create_scenario") }}"]'
      );
      if (form) {
        let button = form.querySelector('button[type="submit"]');
        if (button) {
          button.click();
        }
      }
    };
  }
};
