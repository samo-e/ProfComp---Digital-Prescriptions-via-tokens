$(document).ready(function() {
  $("#script-print").click(print_scripts);
});

const options = {
  filename: 'my-document.pdf',
  margin: 1,
  image: { type: 'jpeg', quality: 0.98 },
  html2canvas: { scale: 2 },
  jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' },
};

function print_scripts() {
  let select_all = ($("#asl-table .asl-paperless .asl-check input:checked").length == 0);
  
  $("#asl-table .asl-paperless").each(function() {
    if ((select_all) || ($(this).find(".asl-check input").is(":checked"))) {
      let this_id = $(this).attr("id")
      appendPrescription(this_id);
    }
  });

  appendPrescription();
}

async function appendPrescription(asl_id) {
  let element = await create_prescription();
  element = insert_prescription_details(element, asl_id);
  if (true) {
    // Below is debug only (disables auto-download)
    $("body").append(element); // jQuery appends the DOM element
    element = document.querySelector(".prescription-container");
    //html2pdf().set(options).from(element).outputPdf().get('pdf').then(function (pdfObj) {pdfObj.autoPrint();window.open(pdfObj.output("bloburl"), "F")});;
  } else {
    html2pdf().set(options).from(element).save();
  }
}

async function create_prescription() {
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


function insert_prescription_details(el, asl_id) {
  // Add details of the prescription to the element
  // See comment in prescription.html
  return el;
}
