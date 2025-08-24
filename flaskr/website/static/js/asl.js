$(document).ready(function() {
  $('.btn-collapse').on('click', function() {
    var $btn = $(this);
    var $icon = $btn.find('i');

    $icon.toggleClass('bi-chevron-up bi-chevron-down');
  });
});

function delete_consent() {
  //#conf-del-consent
  let res = confirm("Are you sure you wish to delete this consent request? Once the consent has been deleted, you will need to request access from the customer again.");
  console.log(res);
  if (res) {
    $('#delete-consent-menu').modal('hide');
    location.reload();
  }
}