// flaskr/website/static/js/asl_init.js
// This file initializes patient data for the ASL page
// Note: pt_id, pt_data, and user_role are set from the HTML template

// Flatten dictionary function (if needed by other scripts)
function flatten_dict(dict) {
  let new_dict = {};

  for (var key in dict) {
    const value = dict[key];

    if (Array.isArray(value)) {
      value.forEach((item, index) => {
        if (typeof item === "object" && item !== null) {
          const flattened = flatten_dict(item);
          for (var subkey in flattened) {
            new_dict[`${key}-${index}-${subkey}`] = flattened[subkey];
          }
        } else {
          new_dict[`${key}-${index}`] = item;
        }
      });
    } else if (typeof value === "object" && value !== null) {
      const flattened = flatten_dict(value);
      for (var subkey in flattened) {
        new_dict[`${key}-${subkey}`] = flattened[subkey];
      }
    } else {
      new_dict[key] = value;
    }
  }

  return new_dict;
}

// Initialize flattened data if pt_data exists
if (typeof pt_data !== 'undefined') {
  const flatted_pt_data = flatten_dict(pt_data);
  // Make it globally available for other scripts
  window.flatted_pt_data = flatted_pt_data;
}