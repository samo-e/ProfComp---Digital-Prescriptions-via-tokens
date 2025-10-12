$(function() {
  // collapse functionality
  $(".btn-collapse").on("click", function () {
    var $btn = $(this);
    var $icon = $btn.find("i");
    $icon.toggleClass("bi-chevron-up bi-chevron-down");
  });

  // Initialize button
  initializeButtonStates();

  // Request Access button
  $("#btn-request-access").on("click", function () {
    // console.log("Request Access clicked");

    if ($(this).prop("disabled")) {
      // console.log("Button is disabled, ignoring click");
      return;
    }

    $(this).prop("disabled", true);

    $.post(`/api/asl/${pt_id}/request-access`)
      .done(function (data) {
        // console.log("Request Access response:", data);
        if (data.success) {
          alert(data.message);
          $("#asl-status").text(data.new_status);

          if (data.should_disable_button) {
            updateButtonStates("PENDING");
          }

          if (data.new_status === "Pending") {
            $("#btn-refresh").show();
          }
        } else {
          alert("Request failed: " + data.error);
          $("#btn-request-access").prop("disabled", false);
        }
      })
      .fail(function (xhr, status, error) {
        console.error("Request Access failed:", status, error);
        alert("Request failed: " + error);
        $("#btn-request-access").prop("disabled", false);
      });
  });

  // Refresh button
  $("#btn-refresh").on("click", function () {
    // console.log("Refresh clicked");

    $(this).prop("disabled", true).text("Refreshing...");

    $.post(`/api/asl/${pt_id}/refresh`)
      .done(function (data) {
        // console.log("Refresh response:", data);
        if (data.success) {
          alert(data.message);

          // Handle consent_status structure
          if (data["consent-status"]) {
            $("#consent-status").text(data["consent-status"].status);
            $("#consent-last-updated").text(
              `(last updated ${data["consent-status"]["last-updated"]})`
            );
          }

          if (data.should_reload) {
            location.reload();
          }
        } else {
          alert("Refresh failed: " + data.error);
        }
      })
      .fail(function (xhr, status, error) {
        console.error("Refresh failed:", status, error);
        if (xhr.status === 403) {
          alert("Cannot refresh: " + xhr.responseJSON.error);
        } else {
          alert("Refresh failed: " + error);
        }
      })
      .always(function () {
        $("#btn-refresh").prop("disabled", false).text("Refresh");
      });
  });

  // Delete Consent button
  $("#btn-delete-consent").on("click", function () {
    // console.log("Delete Consent clicked");

    if (
      !confirm(
        'Delete consent record? This will reset the patient to "No Consent" status.'
      )
    ) {
      return;
    }

    $.ajax({
      url: `/api/patient/${pt_id}/consent`,
      method: "DELETE",
      success: function (data) {
        // console.log("Delete Consent response:", data);
        if (data.success) {
          alert(data.message);

          $("#consent-status")
            .text("No Consent")
            .removeClass("consent-granted consent-pending consent-rejected")
            .addClass("consent-no-consent");
          $("#consent-last-updated").hide();
          $("#btn-delete-consent").hide();
          $("#btn-request-access")
            .removeClass("btn-secondary")
            .addClass("btn-info")
            .prop("disabled", false)
            .text("Request Access")
            .show();
          $("#btn-refresh").show();

          if (data.should_reload) {
            location.reload();
          }
        } else {
          alert("Delete consent failed: " + data.error);
        }
      },
      error: function (xhr, status, error) {
        console.error("Delete Consent failed:", status, error);
        alert("Delete consent failed: " + error);
      },
    });
  });

  // search functionality
  $("#search-input").on("input", function () {
    const query = $(this).val().trim().toLowerCase();
    // console.log("Search query:", query);

    if (query.length === 0) {
      showAllPrescriptions();
      return;
    }

    performFrontendSearch(query);
  });

  function performFrontendSearch(query) {
    let hasResults = false;

    $("#asl-table tbody tr").each(function () {
      const $row = $(this);
      const text = $row.text().toLowerCase();

      if (text.includes(query)) {
        $row.show();
        hasResults = true;
      } else {
        $row.hide();
      }
    });

    $("#alr-table tbody tr").each(function () {
      const $row = $(this);
      const text = $row.text().toLowerCase();

      if (text.includes(query)) {
        $row.show();
        hasResults = true;
      } else {
        $row.hide();
      }
    });

    handleNoResults(hasResults);
  }

  function handleNoResults(hasResults) {
    $("#no-results").remove();

    if (!hasResults) {
      const noResultsRow = `
              <tr id="no-results">
                  <td colspan="7" class="text-center text-muted py-4">
                      <i class="bi bi-search"></i> No matching prescriptions found
                  </td>
              </tr>`;
      $("#asl-table tbody").append(noResultsRow);
    }
  }

  function showAllPrescriptions() {
    $("#asl-table tbody tr").show();
    $("#alr-table tbody tr").show();
    $("#no-results").remove();
  }

  $("#script-print").on("click", function () {
    // console.log("Print button clicked");

    const selectedIds = [];
    $('#asl-table tbody input[type="checkbox"]:checked').each(function () {
      selectedIds.push(parseInt($(this).val()));
    });

    // console.log("Selected prescription IDs:", selectedIds);
  });

  function initializeButtonStates() {
    // consent_status nested structure
    const aslStatus = pt_data["consent-status"]["status"];
    updateButtonStates(aslStatus);
  }

  function updateButtonStates(status) {
    const $requestBtn = $("#btn-request-access");
    const $refreshBtn = $("#btn-refresh");
    const $deleteBtn = $("#btn-delete-consent");

    $requestBtn
      .removeClass("btn-secondary btn-info btn-warning btn-success")
      .prop("disabled", false);
    $refreshBtn.show();
    $deleteBtn.show();

    switch (status.toUpperCase()) {
      case "NO CONSENT":
      case "NO_CONSENT":
        $requestBtn
          .addClass("btn-info")
          .prop("disabled", false)
          .text("Request Access");
        $refreshBtn.show().text("Refresh");
        $deleteBtn.hide();
        break;

      case "PENDING":
        $requestBtn
          .addClass("btn-secondary")
          .prop("disabled", true)
          .text("Request Access");
        $refreshBtn.show().text("Refresh");
        $deleteBtn.show();
        break;

      case "GRANTED":
        $requestBtn.hide();
        $refreshBtn.show().text("Refresh");
        $deleteBtn.show();
        break;

      case "REJECTED":
        $requestBtn
          .addClass("btn-secondary")
          .prop("disabled", true)
          .text("Request Access");
        $refreshBtn.show().text("Refresh");
        $deleteBtn.show();
        break;

      default:
        console.warn("Unknown ASL status:", status);
    }
  }

  // debug info
  console.log("pt_id:", pt_id);
  console.log("pt_data:", pt_data);
  console.log("ASL Status:", pt_data["consent-status"]["status"]);
});

$(function() {
  // Handle prescription selection for dispensing
  const checkboxes = document.querySelectorAll(
    '#asl-table input[type="checkbox"]'
  );
  const dispenseButton = document.getElementById("dispense-selected");

  // Show/hide dispense button based on selection
  function toggleDispenseButton() {
    const checkedBoxes = document.querySelectorAll(
      '#asl-table input[type="checkbox"]:checked'
    );
    $(dispenseButton).toggleClass("d-none", checkedBoxes.length === 0);
  }

  // Add event listeners to checkboxes
  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", toggleDispenseButton);
  });

  // Handle dispense button click
  dispenseButton.addEventListener("click", function () {
    const checkedBoxes = document.querySelectorAll(
      '#asl-table input[type="checkbox"]:checked'
    );
    const selectedPrescriptions = Array.from(checkedBoxes).map((cb) => {
      const row = cb.closest("tr");
      const cells = row.querySelectorAll("td");
      return {
        id: cb.value,
        prescribed_date: cells[1].textContent.trim(),
        drug_name: cells[2].querySelector("p")
          ? cells[2].textContent.split("\n")[0].trim()
          : cells[2].textContent.trim(),
        dspid: cells[2].querySelector("p")
          ? cells[2].querySelector("p").textContent.trim()
          : "",
        quantity: cells[3].textContent.trim(),
        prescriber: cells[4].textContent.split("\n")[0].trim(),
        repeats: cells[5].textContent.trim(),
      };
    });

    // Populate modal with selected prescriptions
    populateDispensingModal(selectedPrescriptions);

    // Show modal
    const modal = new bootstrap.Modal(
      document.getElementById("dispensingModal")
    );
    modal.show();
  });

  function populateDispensingModal(prescriptions) {
    const container = document.getElementById("selected-prescriptions");
    const prescriptionIds = document.getElementById("prescription-ids");

    // Set prescription IDs
    prescriptionIds.value = prescriptions.map((p) => p.id).join(",");

    // Create prescription cards
    container.innerHTML = prescriptions
      .map(
        (prescription) => `
            <div class="card mb-2">
                <div class="card-body p-3">
                    <div class="row">
                        <div class="col-md-6">
                            <h6 class="card-title mb-1">${prescription.drug_name}</h6>
                            <small class="text-muted">DSPID: ${prescription.dspid}</small>
                        </div>
                        <div class="col-md-3">
                            <small class="text-muted">Quantity:</small><br>
                            <strong>${prescription.quantity}</strong>
                        </div>
                        <div class="col-md-3">
                            <small class="text-muted">Repeats:</small><br>
                            <strong>${prescription.repeats}</strong>
                        </div>
                    </div>
                    <hr class="my-2">
                    <div class="row">
                        <div class="col-md-6">
                            <small class="text-muted">Prescriber: ${prescription.prescriber}</small>
                        </div>
                        <div class="col-md-6">
                            <small class="text-muted">Prescribed: ${prescription.prescribed_date}</small>
                        </div>
                    </div>
                </div>
            </div>
        `
      )
      .join("");
  }

  // Handle confirm dispensing
  document
    .getElementById("confirm-dispense")
    .addEventListener("click", function () {
      const form = document.getElementById("dispensing-form");
      const formData = new FormData(form);

      // Submit dispensing request
      fetch(`/api/dispense/${pt_id}`, {
        method: "POST",
        body: formData,
        headers: {
          "X-CSRFToken": formData.get("csrf_token"),
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // Close modal
            bootstrap.Modal.getInstance(
              document.getElementById("dispensingModal")
            ).hide();

            // Show success message
            showAlert("success", "Prescriptions dispensed successfully!");

            // Remove dispensed prescriptions from table
            document.querySelectorAll('#asl-table input[type="checkbox"]:checked').forEach(cb => {
              const row = cb.closest("tr");
              if (row) row.remove();
            });

            // Hide dispense button
            document.getElementById("dispense-selected").classList.add("d-none");

            // Refresh page to show updated status
            setTimeout(() => {
              window.location.reload();
            }, 1500);
          } else {
            showAlert(
              "error",
              data.message || "Error dispensing prescriptions"
            );
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          showAlert(
            "error",
            "An error occurred while dispensing prescriptions"
          );
        });
    });

  // Set current date in dispensed_date field
  const today = new Date();
  const formattedDate = today.toLocaleDateString("en-GB"); // DD/MM/YYYY format
  document.getElementById("dispensed_date").value = formattedDate;

  function showAlert(type, message) {
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${
      type === "success" ? "success" : "danger"
    } alert-dismissible fade show`;
    alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

    // Insert at top of container
    const container = document.querySelector(".container");
    container.insertBefore(alertDiv, container.firstChild);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      alertDiv.remove();
    }, 5000);
  }
});
