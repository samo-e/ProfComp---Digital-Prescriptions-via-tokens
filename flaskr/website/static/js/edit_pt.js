$(document).ready(function () {
  $('a[data-bs-toggle="tab"]').on("shown.bs.tab", function (e) {
    const activeHref = $(e.target).attr("href");
    const activeText = $(e.target).text();

    const $dropdownItem = $(
      `#dropdownMenu .dropdown-item[href="${activeHref}"]`
    );
    if ($dropdownItem.length) {
      $("#dropdownMenuLink").text(activeText);
      $("#dropdownMenu .dropdown-item").removeClass("d-none");
      $dropdownItem.addClass("d-none");
    }
  });

  const $addressInput = $("#address");
  const $addressDropdown = $("#address-suggestions");
  const $suburbInput = $("#suburb");
  const $postcodeInput = $("#postcode");
  const $stateInput = $("#state");

  let debounceTimer;
  let currentRequest = null;
  let selectedIndex = -1;

  $addressInput.on("input", function () {
    const text = $(this).val();
    clearTimeout(debounceTimer);

    debounceTimer = setTimeout(function () {
      if (text.length < 2) {
        $addressDropdown.removeClass("show");
        return;
      }

      if (currentRequest) currentRequest.abort();

      currentRequest = $.getJSON("/ac", { text: text })
        .done(function (results) {
          renderSuggestions(results, $addressInput, $addressDropdown);
        })
        .fail(function (jqXHR, textStatus) {
          if (textStatus !== "abort") {
            console.error("Error:", jqXHR.responseJSON || jqXHR.statusText);
          }
        })
        .always(function () {
          currentRequest = null;
        });
    }, 250);
  });

  $addressInput.on("keydown", function (e) {
    const $items = $addressDropdown.find("a.dropdown-item");
    if (!$items.length) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      selectedIndex = (selectedIndex + 1) % $items.length;
      highlightItem($items, selectedIndex);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      selectedIndex = (selectedIndex - 1 + $items.length) % $items.length;
      highlightItem($items, selectedIndex);
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (selectedIndex >= 0) {
        $items.eq(selectedIndex).click();
      }
    }
  });

  $(document).on("click", function (e) {
    if (
      !$(e.target).closest($addressInput).length &&
      !$(e.target).closest($addressDropdown).length
    ) {
      $addressDropdown.removeClass("show");
      selectedIndex = -1;
    }
  });

  function highlightItem($items, index) {
    $items.removeClass("active");
    $items.eq(index).addClass("active");
  }

  function renderSuggestions(results, $addressInput, $addressDropdown) {
    $addressDropdown.empty();
    selectedIndex = -1;

    if (!results || results.length === 0) {
      $addressDropdown.removeClass("show");
      return;
    }

    results.forEach((place, index) => {
      const $item = $('<li><a class="dropdown-item" href="#"></a></li>');
      $item
        .find("a")
        .text(place.formatted)
        .on("click", function (e) {
          e.preventDefault();
          $addressInput.val(place.address_line1);
          $addressDropdown.removeClass("show");
          selectedIndex = -1;

          // Fill the other form elements
          $suburbInput.val(place.suburb);
          $postcodeInput.val(place.postcode);
          let stateCode = place.state_code;

          // If missing, infer from postcode
          if (!stateCode) {
            const postcode = parseInt(place.postcode, 10);

            if (postcode >= 2600 && postcode <= 2618) {
              stateCode = "act";
            } else if (postcode >= 800 && postcode <= 899) {
              // between 0800 and 0899
              stateCode = "nt";
            }
          }
          $stateInput.val(stateCode.toLowerCase());
        });
      $addressDropdown.append($item);
    });

    $addressDropdown.addClass("show");
  }

  const medicareInput = $("#medicare");
  const irnInput = $("#medicareIssue");

  medicareInput.on("input", function () {
    if (medicareInput.val().length === 9) {
      irnInput.focus();
    }
  });

  $("#safetyNet-family_name").on("input", function () {
    showFamilySafetyNet($(this));
  });
});

function addTableRow(tableId, columnNames) {
  const $tableBody = $(`#${tableId} tbody`);
  if (!$tableBody.length) return;

  const $newRow = $("<tr></tr>").attr("onclick", `activateTableRow(this)`);

  columnNames.forEach((col) => {
    const $td = $("<td></td>");
    const $input = $("<input>")
      .attr("type", "text")
      .attr("name", `${tableId}[]`)
      .addClass("form-control form-control-sm");
    $td.append($input);
    $newRow.append($td);
  });

  // Insert before the last row if it is the empty placeholder
  const $lastRow = $tableBody.find("tr:last-child");
  if ($lastRow.find("td[colspan]").length) {
    $newRow.insertBefore($lastRow);
  } else {
    $tableBody.append($newRow);
  }
}

function activateTableRow(row) {
  var $row = $(row);

  $row.siblings().removeClass("table-active");

  $row.toggleClass("table-active");
}

function addNote() {
  const $notesContainer = $("#patient-notes-container");
  const index = $notesContainer.children().length;
  let templateHtml = $("#note-template").html();
  templateHtml = templateHtml.replace(/__index__/g, index);
  const $newNote = $(templateHtml);

  // Set last_edited to today in DD/MM/YYYY
  const now = new Date();
  const formatted =
    String(now.getDate()).padStart(2, "0") +
    "/" +
    String(now.getMonth() + 1).padStart(2, "0") +
    "/" +
    now.getFullYear();
  $newNote.find("input[name*='last_edited']").val(formatted);

  $notesContainer.append($newNote);
}

function showFamilySafetyNet($e) {
  if ($e.val().trim() !== "") {
    $("#prf-gen-fam, #prf-con-fam, #fam-safety-net").removeClass("d-none");
  }
}
