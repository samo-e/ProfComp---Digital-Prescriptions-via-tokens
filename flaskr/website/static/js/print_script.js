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
  let asls_to_print = [];

  let select_all = ($("#asl-table .asl-paperless .asl-check input:checked").length == 0);
  
  $("#asl-table .asl-paperless").each(function() {
    if ((select_all) || ($(this).find(".asl-check input").is(":checked"))) {
      let this_id = $(this).attr("id")
      asls_to_print.push(this_id);
    }
  });

  appendPrescription();
}

async function appendPrescription() {
  let element = await create_prescription();
  $("body").append(element); // jQuery appends the DOM element
  const el = document.querySelector(".prescription-container");
  html2pdf().set(options).from(el).save();
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
