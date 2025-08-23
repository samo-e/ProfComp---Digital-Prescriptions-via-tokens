$(document).ready(function() {
  $("#script-print").click(print_scripts);
});

const options = {
  filename: 'prescriptions.pdf',
  margin: 10,
  image: { 
    type: 'jpeg',
    quality: 0.98
  },
  html2canvas: { 
    scale: 2,
    logging: false // disable console output
  }, 
  jsPDF: { 
    unit: 'mm',
    format: 'a4',
    orientation: 'portrait'
  },
};

//const blank_prescription = await get_blank_prescription();
async function get_blank_prescription() {
  try {
    // fetch the HTML from the server
    const response = await fetch("/prescription");
    if (!response.ok) throw new Error("Network response was not ok");

    const html = await response.text();

    // create a container for the new content
    const container = document.createElement("div");
    container.innerHTML = html;

    return container;
  } catch (error) {
    console.error("Error fetching content:", error);
  }
}

async function print_scripts() {
  let select_all = ($("#asl-table .asl-paperless .asl-check input:checked").length == 0);
  
  // Temp parent container to store the prescriptions
  let $container = $('<div></div>');
  const prescription_container = await get_blank_prescription();
  // Loop through prescriptions and append them into container
  for (let elem of $("#asl-table .asl-paperless")) {
    if (select_all || $(elem).find(".asl-check input").is(":checked")) {
      let presc = prescription_container.cloneNode(true);
      let this_id = $(elem).attr("id");
      presc = insert_prescription_details(presc, this_id);

      // Add a page break between prescriptions
      let $wrapper = $('<div></div>').append(presc);
      $wrapper.css({'break-after': 'page','margin-top': '10px'});

      $container.append($wrapper[0]);
    }
  }

  if (true) {
    // Below is debug only (disables auto-download)
    $("body").append($container);
    html2pdf().set(options).from($container[0]).outputPdf().get('pdf').then(function (pdfObj) {window.open(pdfObj.output("bloburl"), "F")});
  } else {
    html2pdf().set(options).from($container[0]).save();
  }
}

const id_list = [
  "medicare",
  "pharmaceut-ben-entitlement-no",
  "sfty-net-entitlement-cardholder",
  "rpbs-ben-entitlement-cardholder",
  "pt-name",
  "pt-dob",
  "pt-preferred-contact",
  "pt-address-1",
  "pt-address-2",
  "script-date",
  "pbs",
  "rpbs"
]
const drug_info_ids = [ // prepend `asl_data-X-`
  "prescriber-fname",
  "prescriber-lname",
  "prescriber-title",
  "prescriber-address-1",
  "prescriber-address-2",
  "prescriber-id",
  "prescriber-hpii",
  "prescriber-hpio",
  "prescriber-phone",
  "prescriber-fax",
  "DSPID",
  "status",
  "brand-sub-not-prmt",
  "drug-name" ,
  "drug-code" ,
  "dose-instr",
  "dose-qty"  ,
  "dose-rpt"  ,
  "prescribed-date",
  "paperless"
]

function flatten_dict(dict) {
  let new_dict = {};
  
  for (var key in dict) {
    if (typeof dict[key] === "object") {
      let f = flatten_dict(dict[key]);
      for (var i in f) {
        new_dict[`${key}-${i}`] = f[i];
      }
    } else {
      new_dict[key] = dict[key];
    }
  }

  return new_dict;
}

// Add details of the prescription to the element
// See comment in prescription.html
// data input accessed via `pt_data`: json
function insert_prescription_details(el, drug_id) {
  // Append data
  id_list.forEach(id => {
    const $el = $(el).find(`#${id}`);
    if (pt_data[id] !== undefined) {
      let data_point = pt_data[id];
      if (data_point === true) {
        data_point = 'x';
      } else if (data_point === false){
        return; //continue
      }
      $el.text(data_point);
    }
  });

  // Append ASL specific data
  drug_info_ids.forEach(id => {
    const $el = $(el).find(`#${id}`);
    const new_key = `asl_data-${drug_id.slice(-1)}-${id}`;
    if (flatted_pt_data[new_key] !== undefined) {
      let data_point = flatted_pt_data[new_key];
      if (data_point === true) {
        data_point = 'x';
      } else if (data_point === false){
        return; //continue
      }
      $el.text(data_point);
    }
  });
  return el;
}
