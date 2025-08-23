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
    logging: false // disable consol output
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
  
  let $container = $('<div></div>')
  // Loop through prescriptions and append them into container
  for (let elem of $("#asl-table .asl-paperless")) {
    if (select_all || $(elem).find(".asl-check input").is(":checked")) {
      let this_id = $(elem).attr("id");
      let presc = await create_prescription();
      presc = insert_prescription_details(presc, this_id);

      // Add a page break between prescriptions
      let $wrapper = $('<div></div>').append(presc);
      $wrapper.css({'break-after': 'page',});

      $container.append(presc);
    }
  }

  if (true) {
    // Below is debug only (disables auto-download)
    $("body").append($container);
    html2pdf().set(options).from($container[0]).outputPdf().get('pdf').then(function (pdfObj) {pdfObj.autoPrint();window.open(pdfObj.output("bloburl"), "F")});;
  } else {
    html2pdf().set(options).from($container[0]).save();
  }
}

const id_list = [
  "clinician-name-and-title",
  "clinician-address-1",
  "clinician-address-2",  
  "DSPID",
  "status",
  "clinician-id",
  "hpii",
  "hpio",
  "clinician-phone",
  "clinician-fax",
  "medicare",
  "pharmaceut-ben-entitlement-no",
  "sfty-net-entitlement-cardholder",
  "rpbs-ben-entitlement-cardholder",
  "pt-name",
  "pt-address-1",
  "pt-address-2",
  "script-date",
  "pbs",
  "rpbs",
  "brand-sub-not-prmt"
]
const drug_class_list = [
  "drug-name",
  "drug-code",
  "dose-freq",
  "dose-qty",
  "dose-rpt"
]

// Add details of the prescription to the element
// See comment in prescription.html
// data input accessed via `asl_data`: json
function insert_prescription_details(el, drug_id) {
  // Append data
  id_list.forEach(id => {
    const $el = $(el).find("#" + id);   // scoped inside el
    if ($el.length && asl_data[id] !== undefined) {
      let data_point = asl_data[id];
      if (data_point === true) {
        data_point = 'x';
      } else if (data_point === false){
        return; //continue
      }
      $el.text(data_point);
    }
  });

  // Append drug data
  return el;
}
