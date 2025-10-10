$(document).ready(function () {
  const $aslContainer = $("#asl-items");
  const $alrContainer = $("#alr-items");

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

    // Expand added items
    const $collapse = $item.find(".accordion-collapse");
    const $button = $item.find(".accordion-button").first();

    // Collapse any currently open items in this container
    $container.find(".accordion-collapse.show").collapse("hide");
    
    // Expand the new one
    $collapse.addClass("show");
    $button.removeClass("collapsed").attr("aria-expanded", "true");
  }

  // Add ASL
  $("#add-asl-item").on("click", function () {
    addItem($aslContainer, "asl-template", "ASL");
  });

  // Add ALR
  $("#add-alr-item").on("click", function () {
    addItem($alrContainer, "alr-template", "ALR");
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
      const $btn = $(this).find(".accordion-button").first();
      if ($btn.length) {
        let itemType = $btn.text().trim().split(" ")[0]; // "ASL" or "ALR"
        $btn.text(`${itemType} Prescription ${idx + 1}`);
        // Re-add remove button if removed accidentally
        if ($btn.siblings(".remove-item-btn").length === 0) {
          $btn.after(
            '<button type="button" class="btn btn-sm btn-outline-danger ms-2 remove-item-btn" data-action="remove">Remove</button>'
          );
        }
      }

      // Update collapse div's parent attribute
      $(this)
        .find(".accordion-collapse")
        .attr("data-bs-parent", `#${$container.attr("id")}`);
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
  });

  // Unsaved changes indicator
  $(document).on("input change", ".item-card :input", function () {
    const $card = $(this).closest(".item-card");

    if ($card.find(".unsaved-changes").length === 0) {
      $card
        .find(".accordion-button")
        .first()
        .append(
          ' <span class="unsaved-changes text-warning fw-bold"><i class="bi bi-exclamation-triangle mx-1"></i>Unsaved Changes</span>'
        );
    }
  });

  // Form validation
  $("#asl-form").on("submit", function (e) {
    console.log("submitting")
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
    }
  });
});


