/**
 * Toggle select all checkboxes for scenarios
 */
function selectAllToggle() {
  const selectAll = $("#select-all").prop("checked"); // true/false
  const checkboxes = $("input[type=checkbox][id^='scenario-']");

  checkboxes.prop("checked", selectAll);
}

/**
 * Archive selected scenarios in bulk
 */
function bulkArchive() {
  const checkboxes = $("input[type=checkbox][id^='scenario-']:checked");
  const selected = checkboxes.length;

  if (selected === 0) {
    alert("Please select scenarios to archive");
    return;
  }

  if (
    !confirm(
      `Are you sure you want to archive ${selected} selected scenario(s)?`
    )
  ) {
    return;
  }

  // submit each corresponding delete form
  checkboxes.each(function () {
    const scenarioId = $(this).attr("id").replace("scenario-", "");
    const form = $("#delete-form-" + scenarioId);
    if (form.length) {
      form.submit();
    }
  });
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
    const form = $("#delete-form-" + scenarioId);
    if (form.length) {
      form.submit();
    }
  }
}

/**
 * Initialize the page when DOM is loaded
 */
$(function () {
  // Set up select all checkbox
  $("#select-all").on("change", selectAllToggle);

  // Set up bulk action buttons
  $("#bulk-delete").on("click", bulkArchive);
  $("#bulk-export").on("click", bulkExport);

  // Set up individual delete buttons
  $(".delete-btn").each(function () {
    const btn = $(this);
    btn.on("click", function () {
      confirmDelete(btn.data("scenario-id"));
    });
  });

  // Set up create first scenario link
  $("#create-first-scenario").on("click", function (e) {
    e.preventDefault();
    const form = $('form[action*="create_scenario"]').first();
    const button = form.find('button[type="submit"]').first();
    if (button.length) {
      button.click();
    }
  });
});

function updateSelectAllState() {
  const selectAll = $("#select-all");
  if (!selectAll.length) return;

  const boxes = $(".scenario-checkbox");
  const total = boxes.length;
  const checked = boxes.filter(":checked").length;

  selectAll.prop("checked", total > 0 && checked === total);
  selectAll.prop("indeterminate", checked > 0 && checked < total);
}

function countSelected() {
  return $(".scenario-checkbox:checked").length;
}
