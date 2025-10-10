$(document).ready(function () {
  const $aslContainer = $("#asl-items");
  const $alrContainer = $("#alr-items");

  function collapseAll($container) {
    $container.find(".accordion-collapse").removeClass("show");
    $container.find(".accordion-button").addClass("collapsed").attr("aria-expanded", "false");
  }

  // Add new item
  function addItem($container, templateId, type) {
    const index = $container.children().length;
    let $template = $(`#${templateId}`).html();

    // Replace __INDEX__ placeholders
    $template = $template.replace(/__INDEX__/g, index);

    // Wrap in jQuery object
    const $item = $($template);

    // Append to container
    $container.append($item);

    // Re-index all items
    indexItems($container);

    // Expand added item
    const $collapse = $item.find(".accordion-collapse");
    const $button = $item.find(".accordion-button").first();

    // Expand the new one
    $collapse.addClass("show");
    $button.removeClass("collapsed").attr("aria-expanded", "true");

    // Update the counter based on type
    const counterId = type.toLowerCase() + '-counter'; // "asl-counter" or "alr-counter"
    $(`#${counterId}`).text($container.children().length);

    // Dirty form
    $("#asl-form").trigger("dirty");
    unhideUnsavedChanges($item);

    const $newItem = $item.find(".accordion-button .new-item").first();
    if ($newItem.length) $newItem.removeClass("d-none");
  }

  // Add ASL
  $("#add-asl-item").on("click", function () {
    addItem($aslContainer, "asl-template", "ASL");
  });
  // Add ALR
  $("#add-alr-item").on("click", function () {
    addItem($alrContainer, "alr-template", "ALR");
  });

  // Collpase ASL
  $("#collapse-asl-items").on("click", function () {
    collapseAll($aslContainer);
  });
  // Collpase ALR
  $("#collapse-alr-items").on("click", function () {
    collapseAll($alrContainer);
  });

  // Re-index items after add/remove
  function indexItems($container) {
    $container.children(".item-card").each(function (idx) {
      // Update attributes
      $(this)
        .find("[name], [id], [for], [aria-labelledby], [data-bs-target]")
        .each(function () {
          const attrs = [
            "name",
            "id",
            "for",
            "aria-labelledby",
            "data-bs-target",
          ];
          attrs.forEach((attr) => {
            let val = $(this).attr(attr);
            if (val) {
              val = val.replace(/\[\d+\]/g, `[${idx}]`);
              val = val.replace(/-(\d+)$/g, `-${idx}`);
              val = val.replace(/__INDEX__/g, idx);
              $(this).attr(attr, val);
            }
          });
        });

      // Update accordion button text
      const $btnTextSpan = $(this).find(".accordion-button > span:first-child");
      if ($btnTextSpan.length) {
        let itemType = $(this).find(".accordion-button").first().text().trim().split(" ")[0];
        $btnTextSpan.text(`${itemType} Prescription ${idx + 1}`);
      }
    });
  }

  // Initial indexing on page load
  indexItems($aslContainer);
  indexItems($alrContainer);

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
    indexItems($container);

    // Dirty form
    $("#asl-form").trigger("dirty");
  });

  function unhideUnsavedChanges(elem) {
    const $card = elem.closest(".item-card");

    const $unsaved = $card.find(".accordion-button .unsaved-changes").first();
    if ($unsaved.length) {
      $unsaved.removeClass("d-none");
    }
  }

  // Unsaved changes indicator
  $(document).on("input change", ".item-card :input", function () {
    unhideUnsavedChanges($(this));
  });

  // Form validation
  $("#asl-form").on("submit", function (e) {
    console.log("submitting");
    let hasError = false;

    $(".error-message").text("");

    $(this)
      .find("input[required], select[required], textarea[required]")
      .each(function () {
        if ($(this).val().trim() === "") {
          hasError = true;
          $(this).next(".error-message").text("This field is required.");
          console.log(this, "This field is required.");
        }
      });

    if (hasError) {
      e.preventDefault();
    } else {
      $(this).dirty("setAsClean");
    }
  });

  $("#asl-form").dirty({
    preventLeaving: true,
    leavingMessage: "You have unsaved changes. Are you sure you want to leave?",
  });

  $("form").on("dirty", function () {
    $("#edits-made").removeClass("d-none");
  });
});
