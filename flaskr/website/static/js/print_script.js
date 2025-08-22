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

async function print_scripts() {
  let select_all = ($("#asl-table .asl-paperless .asl-check input:checked").length == 0);
  
  // Temp parent container to store the prescriptions
  let container = document.createElement("div");
  
  // Loop through prescriptions and append them into container
  for (let elem of $("#asl-table .asl-paperless")) {
    if (select_all || $(elem).find(".asl-check input").is(":checked")) {
      let this_id = $(elem).attr("id");
      let presc = await create_prescription();
      presc = insert_prescription_details(presc, this_id);

      // Add a page break between prescriptions
      let wrapper = document.createElement("div");
      wrapper.appendChild(presc);
      wrapper.style.breakAfter = "page";  

      container.appendChild(wrapper);
    }
  }

  if (true) {
    // Below is debug only (disables auto-download)
    $("body").append(container); // jQuery appends the DOM element
    html2pdf().set(options).from(container).outputPdf().get('pdf').then(function (pdfObj) {pdfObj.autoPrint();window.open(pdfObj.output("bloburl"), "F")});;
  } else {
    html2pdf().set(options).from(container).save();
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
