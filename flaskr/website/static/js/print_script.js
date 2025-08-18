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

  printIdToPDF(asls_to_print);
}

function printIdToPDF(rowIds) {
  const { jsPDF } = window.jspdf;
  const pdf = new jsPDF();
  let title = 'Active Script Lists for <pt_id> on <todays date>';

  // Set metadata
  pdf.setProperties({
    title: title, // TODO
    subject: 'List of selected rows',
    //author: '',
    //creator: 'My Company' // maybe make this as the student's id?
  });

  // Format PDF
  // Add title
  pdf.setFontSize(16);
  pdf.text(title, 10, 10);

  // Add each asl row
  pdf.setFontSize(12);
  rowIds.forEach((id, index) => {
    pdf.text(id, 10, 20 + index * 10);
  });

  // Open a new tab
  const newTab = window.open('', '_blank');
  if (!newTab) return;

  // Add content to new tab
  const iframe = newTab.document.createElement('iframe');
  iframe.src = pdf.output('datauristring');
  Object.assign(iframe.style, {
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
