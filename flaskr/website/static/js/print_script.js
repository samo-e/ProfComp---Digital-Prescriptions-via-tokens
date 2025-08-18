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

  console.log(asls_to_print);
}