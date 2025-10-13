// flaskr/website/static/js/asl_form.js

(function () {
  const aslContainer = $("#asl-items");
  const alrContainer = $("#alr-items");
  const aslTemplate = $("#asl-item-template");
  const alrTemplate = $("#alr-item-template");
  const addAslBtn = $("#add-asl-item");
  const addAlrBtn = $("#add-alr-item");

  function addItem(container, templateEl, data = null, index = null) {
    const itemIndex = index !== null ? index : container.children.length;
    const clone = templateEl.content.cloneNode(true);

    // Replace placeholder indices in name attributes
    clone.querySelectorAll("[name]").forEach((el) => {
      el.name = el.name.replaceAll("__INDEX__", itemIndex.toString());
    });

    container.appendChild(clone);

    // If data is provided, populate the fields immediately after adding to DOM
    if (data) {
      setTimeout(() => {
        // Get the last added item (the one we just added)
        const addedItem = container.lastElementChild;

        // Populate prescription fields
        Object.entries(data).forEach(([key, value]) => {
          if (value !== null && value !== undefined && value !== "") {
            // Find field by exact name match in the added item
            const fieldName = `pt_data[${
              container.id === "asl-items" ? "asl" : "alr"
            }-data][${itemIndex}][${key}]`;
            const field = addedItem.querySelector(`[name="${fieldName}"]`);
            if (field) {
              if (field.tagName === "SELECT") {
                field.value = value.toString();
              } else if (field.tagName === "TEXTAREA") {
                field.textContent = value;
              } else {
                field.value = value;
              }
              // Trigger validation check after setting value
              field.dispatchEvent(new Event("input", { bubbles: true }));
              // console.log(`Pre-populated ${key}:`, value);
            } else {
              // console.log(`Field not found: ${fieldName}`);
            }
          }
        });

        // Populate prescriber fields
        if (data.prescriber) {
          Object.entries(data.prescriber).forEach(([key, value]) => {
            if (value !== null && value !== undefined && value !== "") {
              const fieldName = `pt_data[${
                container.id === "asl-items" ? "asl" : "alr"
              }-data][${itemIndex}][prescriber][${key}]`;
              const field = addedItem.querySelector(`[name="${fieldName}"]`);
              if (field) {
                field.value = value;
                // Trigger validation check after setting value
                field.dispatchEvent(new Event("input", { bubbles: true }));
                // console.log(`Pre-populated prescriber ${key}:`, value);
              } else {
                // console.log(`Prescriber field not found: ${fieldName}`);
              }
            }
          });
        }
      }, 10);
    }

    return clone;
  }

  function handleRemove(e) {
    const btn = e.target.closest('[data-action="remove"]');
    if (!btn) return;
    const card = btn.closest(".item-card");
    if (card && card.parentElement) {
      const container = card.parentElement;
      card.remove();
      // Reindex remaining items to keep names sequential
      Array.from(container.children).forEach((child, idx) => {
        child.querySelectorAll("[name]").forEach((el) => {
          el.name = el.name.replace(
            /\[(asl-data|alr-data)\]\[\d+\]/,
            "[$1][" + idx + "]"
          );
        });
      });
    }
  }

  addAslBtn.addEventListener("click", () => addItem(aslContainer, aslTemplate));
  addAlrBtn.addEventListener("click", () => addItem(alrContainer, alrTemplate));
  document.addEventListener("click", handleRemove);

  // Pre-populate with existing data if available
  const ptData = window.pt_data || {};
  // console.log('Pre-population data:', ptData);

  // Populate ASL prescriptions
  if (ptData && ptData["asl-data"] && ptData["asl-data"].length > 0) {
    // console.log('Found existing ASL data, populating', ptData['asl-data'].length, 'items');
    ptData["asl-data"].forEach((aslItem, index) => {
      addItem(aslContainer, aslTemplate, aslItem, index);
    });
  } else {
    // console.log('No existing ASL data found, adding empty form');
    addItem(aslContainer, aslTemplate);
  }

  // Populate ALR prescriptions
  if (ptData && ptData["alr-data"] && ptData["alr-data"].length > 0) {
    // console.log('Found existing ALR data, populating', ptData['alr-data'].length, 'items');
    ptData["alr-data"].forEach((alrItem, index) => {
      addItem(alrContainer, alrTemplate, alrItem, index);
    });
  } else {
    // console.log('No existing ALR data found, adding empty form');
    addItem(alrContainer, alrTemplate);
  }
})();

// Form validation handler
(function () {
  const form = document.querySelector("form.needs-validation");
  // console.log("form element:", form);

  function assignNested(obj, path, value) {
    let cur = obj;
    for (let i = 0; i < path.length - 1; i++) {
      const k = path[i];
      if (!(k in cur)) cur[k] = /^\d+$/.test(path[i + 1]) ? [] : {};
      cur = cur[k];
    }
    const last = path[path.length - 1];
    if (Array.isArray(cur)) {
      cur[parseInt(last, 10)] = value;
    } else {
      cur[last] = value;
    }
  }

  function formDataToNestedJSON(form) {
    const fd = new FormData(form);
    const out = {};
    for (const [name, value] of fd.entries()) {
      const parts = name.replace(/\]/g, "").split("[");
      assignNested(out, parts, value);
    }
    return out.pt_data || out;
  }

  if (form) {
    form.addEventListener("submit", function (e) {
      // console.log("submit handler triggered");

      // Bootstrap validation
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
        form.classList.add("was-validated");
        return;
      }

      // Allow normal form submission to Flask route
      // console.log("Form is valid, submitting to Flask route");
    });
  }
})();
