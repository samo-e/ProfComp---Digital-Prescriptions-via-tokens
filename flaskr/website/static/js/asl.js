$(document).ready(function() {
  $('.btn-collapse').on('click', function() {
    var $btn = $(this);
    var $icon = $btn.find('i');

    $icon.toggleClass('bi-chevron-up bi-chevron-down');
  });
});

$(document).ready(function() {
  $('#asl-filter').on('keyup', function() {
    var filter = $(this).val().toUpperCase();

    var tables = [
      { id: "asl-table", col: 2 },
      { id: "alr-table", col: 1 }
    ];

    tables.forEach(function(tableInfo) {
      var table = document.getElementById(tableInfo.id);
      if (!table) return;

      var tr = table.getElementsByTagName("tr");

      // Loop through all table rows
      for (let i = 0; i < tr.length; i++) {
        var td = tr[i].getElementsByTagName("td")[tableInfo.col];
        if (td) {
          var txtValue = td.textContent || td.innerText;
          tr[i].style.display = txtValue.toUpperCase().indexOf(filter) > -1 ? "" : "none";
        }
      }
    });
  });
});


