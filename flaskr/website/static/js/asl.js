$(document).ready(function() {
    $('.btn-collapse').on('click', function() {
      var $btn = $(this);
      var $icon = $btn.find('i');
      $icon.toggleClass('bi-chevron-up bi-chevron-down');
    });
    
    // Initialize button states based on ASL status
    //initializeButtonStates();
    
    // Request Access button
    // search function
    $('#search-input').on('input', function() {
        const query = $(this).val().trim().toLowerCase();
        let hasResults = false;
        
        $('#alr-table tbody tr, #asl-table tbody tr').each(function() {
            const $row = $(this);
            const text = $row.text().toLowerCase();
            
            if (text.includes(query)) {
                $row.removeClass("d-none");
                hasResults = true;
            } else {
                $row.addClass("d-none");
            }
        });
        
        if (!hasResults) {
            $('#no-results').addClass('visible');
            $('#no-results').removeClass('invisible');
        } else {
            $('#no-results').removeClass('visible');
            $('#no-results').addClass('invisible');
        }
    });
});

function delete_consent() {
  let res = confirm("Are you sure you wish to delete this consent request? Once the consent has been deleted, you will need to request access from the customer again.");
  if (res) {
    $.ajax({
        url: `/api/patient/${pt_id}/consent`,
        method: 'DELETE',
        success: function(data) {
            console.log('Delete Consent response:', data);
            if (data.success) {
                // Update UI to reflect NO_CONSENT state
                $('#consent-status').text('No Consent').removeClass('granted').addClass('revoked');
                $('#consent-last-updated').hide(); 
                $('#btn-delete-consent').hide(); 
                $('#btn-request-access').removeClass('btn-secondary').addClass('btn-info')
                    .prop('disabled', false).text('Request Access').show();
                $('#btn-refresh').show(); // Show refresh button
                
                // Reload page
                if (data.should_reload) {
                    location.reload();
                }
            } else {
                alert('Delete consent failed: ' + data.error);
            }
        },
        error: function(xhr, status, error) {
            alert('Delete consent failed: ' + error);
        }
    });
  }
}

function refresh_consent() {
  // Disable button during refresh
  $(this).prop('disabled', true).text('Refreshing...');
  
  $.post(`/api/asl/${pt_id}/refresh`)
  .done(function(data) {
      if (data.success) {
          // Reload page if status or prescriptions updated
          if (data.should_reload) {
              location.reload();
          }
      } else {
          alert('Refresh failed: ' + data.error);
      }
  })
  .fail(function(xhr, status, error) {
      console.error('Refresh failed:', status, error);
      if (xhr.status === 403) {
          alert('Cannot refresh: ' + xhr.responseJSON.error);
      } else {
          alert('Refresh failed: ' + error);
      }
  })
  .always(function() {
      // Reset button state
      $('#btn-refresh').prop('disabled', false).text('Refresh');
  });
}

function request_access() {
    // Check if button should be disabled (e.g. for pending status, 'request access' would be disabled)
    if ($(this).prop('disabled')) {
        console.log('Button is disabled, ignoring click');
        return;
    }

    // disable button during request
    $(this).prop('disabled', true);

    $.post(`/api/asl/${pt_id}/request-access`)
    .done(function(data) {
        console.log('Request Access response:', data);
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert('Request failed: ' + data.error);
            // Re-enable button on failure
            $('#btn-request-access').prop('disabled', false);
        }
    })
    .fail(function(xhr, status, error) {
        console.error('Request Access failed:', status, error);
        alert('Request failed: ' + error);
        // Re-enable button on failure
        $('#btn-request-access').prop('disabled', false);
    });
}

function update_patient() {

}
