$(document).ready(function () {
  const $aslContainer = $("#asl-items");
  const $alrContainer = $("#alr-items");

  function addItem($container, templateId) {
    const index = $container.children().length;
    const $template = $(`#${templateId}`).html();
    const $item = $($template.replace(/__INDEX__/g, index));
    $container.append($item);
  }

  // Add ASL
  $("#add-asl-item").on("click", function () {
    addItem($aslContainer, "asl-template");
  });

  // Add ALR
  $("#add-alr-item").on("click", function () {
    addItem($alrContainer, "alr-template");
  });

  // Remove item
  $(document).on("click", ".remove-item-btn", function () {
    if (
      !confirm(
        "Are you sure you want to remove this item?\nThis action cannot be undone once you submit."
      )
    ) {
      return;
    }

    const $card = $(this).closest(".item-card");
    const $container = $card.parent();
    $card.remove();

    // Re-index remaining items
    $container.children(".item-card").each(function (idx) {
      $(this)
        .find("[name]")
        .each(function () {
          const name = $(this).attr("name");
          const newName = name.replace(/\[\d+\]/, `[${idx}]`);
          $(this).attr("name", newName);
        });
    });
  });
});

$(document).ready(function () {
  $("#asl-form").on("submit", function (e) {
    let hasError = false;

    // Clear previous errors
    $(".error-message").text("");

    // Check required fields
    $("#asl-form input[required]").each(function () {
      if ($(this).val().trim() === "") {
        hasError = true;
        $(this).next(".error-message").text("This field is required.");
      }
    });

    // Prevent submission if there are errors
    if (hasError) {
      e.preventDefault();
    }
  });
});

$(document).ready(function () {
  // Watch for changes on inputs, selects, and textareas inside item-card
  $(document).on("input change", ".item-card :input", function () {
    const $card = $(this).closest(".item-card");

    // Check if the indicator already exists
    if ($card.find(".unsaved-changes").length === 0) {
      // Append "Unsaved Changes" next to each legend in the card
      $card
        .find("legend")
        .first()
        .append(
          ' <span class="unsaved-changes text-warning fw-bold"><i class="bi bi-exclamation-triangle mx-1"></i>Unsaved Changes</span>'
        );
    }
  });
});
