$(document).ready(function() {
  $("#script-print").click(print_scripts);
});


function print_scripts() {
  let asls_to_print = [];

  let select_all = ($("#asl-table .asl-paperless .asl-check input:checked").length == 0);
  
  $("#asl-table .asl-paperless").each(function() {
    if ((select_all) || ($(this).find(".asl-check input").is(":checked"))) {
      let this_id = $(this).attr("id")
      //console.log();
      asls_to_print.push(this_id);
    }
  });

  create_prescription();
  //printIdToPDF(asls_to_print);
}

function printIdToPDF(rowIds) {
  const { jsPDF } = window.jspdf;
  const pdf = new jsPDF();
  let title = 'Active Script Lists for <pt_id> on <todays date>'; // TODO

  // Set metadata
  pdf.setProperties({
    title: title,
    subject: 'List of selected rows',
    // author: '',
    // creator: 'My Company'
  });

  // Create a container for all rows
  const tempDiv = document.createElement("div");

  rowIds.forEach(id => {
    const element = $(`#${id}`)[0];
    if (element) {
      const wrapper = document.createElement("div");
      wrapper.style.marginBottom = "4px";       // spacing
      wrapper.style.maxWidth = "180mm";         // limit width
      wrapper.style.fontSize = "10px";          // smaller font
      wrapper.style.lineHeight = "1.2";         // tighter lines
      wrapper.style.overflowWrap = "break-word";
      wrapper.style.display = "inline-block";
      wrapper.innerHTML = element.innerHTML;

      tempDiv.appendChild(wrapper);
    }
  });
  tempDiv.style.color = "red";
  console.log(tempDiv);

  // Render all content to PDF and open in new tab
  pdf.html(tempDiv, {
    x: 10,
    y: 10,
    autoPaging: true,
    callback: function(doc) {
      const newTab = window.open('', '_blank');
      if (!newTab) return;

      const iframe = newTab.document.createElement('iframe');
      iframe.src = doc.output('datauristring');
      Object.assign(iframe.style, { // Set display options for the opened PDF tab
        position: 'absolute',
        top: '0',
        left: '0',
        width: '100%',
        height: '100%',
        border: 'none'
      });

      newTab.document.body.innerHTML = '';
      newTab.document.body.appendChild(iframe);
    }
  });
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

    // append to body
    document.body.appendChild(container);
  } catch (error) {
    console.error("Error fetching content:", error);
  }
}
