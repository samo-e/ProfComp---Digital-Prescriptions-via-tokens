$(document).ready(function() {
    $('.btn-collapse').on('click', function() {
      var $btn = $(this);
      var $icon = $btn.find('i');
      $icon.toggleClass('bi-chevron-up bi-chevron-down');
    });
    
    // Initialize button states based on ASL status
    initializeButtonStates();
    
    // Request Access button
    $('#btn-request-access').on('click', function() {
      console.log('Request Access clicked');
      
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
              $('#asl-status').text(data.new_status);
              
              // Update button state based on response
              if (data.should_disable_button) {
                updateButtonStates('PENDING');
              }
              
              // Show refresh button
              if (data.new_status === 'Pending') {
                $('#btn-refresh').show();
              }
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
    });
    
    // search function
    $('#search-input').on('input', function() {
        const query = $(this).val().trim().toLowerCase();
        let hasResults = false;
        
        $('#alr-table tbody tr, #asl-table tbody tr').each(function() {
            const $row = $(this);
            const text = $row.text().toLowerCase();
            
            if (text.includes(query)) {
                $row.show();
                hasResults = true;
            } else {
                $row.hide();
            }
        });
        
        if (!hasResults) {
            $('#no-results').removeClass('d-none');
        } else {
            $('#no-results').addClass('d-none');
        }
    });
    
    // printing function
    $('#script-print').on('click', function() {
      const selectedIds = [];
      $('#asl-table tbody input[type="checkbox"]:checked').each(function() {
          selectedIds.push(parseInt($(this).val()));
      });
      
      console.log('Selected prescription IDs:', selectedIds);
    });
  
    // initialize button states based on ASL status
    function initializeButtonStates() {
      const aslStatus = pt_data.asl_status;
      updateButtonStates(aslStatus);
    }
    
    // update button states based on ASL status
    function updateButtonStates(status) {
      const $requestBtn = $('#btn-request-access');
      const $refreshBtn = $('#btn-refresh');
      const $deleteBtn = $('#btn-delete-consent');
      
      // Reset all buttons first
      $requestBtn.removeClass('btn-secondary btn-info btn-warning btn-success').prop('disabled', false);
      $refreshBtn.show();
      $deleteBtn.show();
      
      switch(status.toUpperCase()) {
        case 'NO CONSENT':
        case 'NO_CONSENT':
          $requestBtn.addClass('btn-info').prop('disabled', false).text('Request Access');
          $refreshBtn.show().text('Refresh');
          $deleteBtn.hide(); // No delete button
          break;
          
        case 'PENDING':
          $requestBtn.addClass('btn-secondary').prop('disabled', true).text('Request Access');
          $refreshBtn.show().text('Refresh');
          $deleteBtn.show();
          break;
          
        case 'GRANTED':
          // Hide Request Access
          $requestBtn.hide();
          $refreshBtn.show().text('Refresh');
          $deleteBtn.show();
          break;
          
        case 'REJECTED':
          $requestBtn.addClass('btn-secondary').prop('disabled', true).text('Request Access');
          $refreshBtn.show().text('Refresh');
          $deleteBtn.show();
          break;
          
        default:
          console.warn('Unknown ASL status:', status);
      }
    }

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

function refresh_consent(ptid) {
  // Disable button during refresh
  $(this).prop('disabled', true).text('Refreshing...');
  
  $.post(`/api/asl/${ptid}/refresh`)
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