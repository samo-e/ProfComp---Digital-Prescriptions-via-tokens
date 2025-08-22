$(document).ready(function() {
  $('.btn-collapse').on('click', function() {
    var $btn = $(this);
    var $icon = $btn.find('i');

    $icon.toggleClass('bi-chevron-up bi-chevron-down');
  });
});
