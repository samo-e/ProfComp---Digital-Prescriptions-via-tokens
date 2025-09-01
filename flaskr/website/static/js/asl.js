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
  
    // Refresh button function
    $('#btn-refresh').on('click', function() {
      console.log('Refresh clicked');
      
      // Disable button during refresh
      $(this).prop('disabled', true).text('Refreshing...');
      
      $.post(`/api/asl/${pt_id}/refresh`)
      .done(function(data) {
          console.log('Refresh response:', data);
          if (data.success) {
              alert(data.message);
              
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
    });
  
    // Delete Consent button
    $('#btn-delete-consent').on('click', function() {
      console.log('Delete Consent clicked');
      
      // confirmation message before deleting
      if (!confirm('Delete consent record? This will reset the patient to "No Consent" status.')) {
          return;
      }
      
      $.ajax({
          url: `/api/patient/${pt_id}/consent`,
          method: 'DELETE',
          success: function(data) {
              console.log('Delete Consent response:', data);
              if (data.success) {
                  alert(data.message);
                  
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
              console.error('Delete Consent failed:', status, error);
              alert('Delete consent failed: ' + error);
          }
      });
    });
  
    // search function
    $('#search-input').on('input', function() {
      const query = $(this).val().trim().toLowerCase();
      console.log('Search query:', query);
      
      if (query.length === 0) {
          showAllPrescriptions();
          return;
      }
      
      performFrontendSearch(query);
    });
  
    function performFrontendSearch(query) {
      let hasResults = false;
      
      $('#asl-table tbody tr').each(function() {
          const $row = $(this);
          const text = $row.text().toLowerCase();
          
          if (text.includes(query)) {
              $row.show();
              hasResults = true;
          } else {
              $row.hide();
          }
      });
      
      $('#alr-table tbody tr').each(function() {
          const $row = $(this);
          const text = $row.text().toLowerCase();
          
          if (text.includes(query)) {
              $row.show();
              hasResults = true;
          } else {
              $row.hide();
          }
      });
      
      handleNoResults(hasResults);
    }
  
    //no results handling
    function handleNoResults(hasResults) {
      $('#no-results').remove();
      
      if (!hasResults) {
          const noResultsRow = `
              <tr id="no-results">
                  <td colspan="7" class="text-center text-muted py-4">
                      <i class="bi bi-search"></i> No matching prescriptions found
                  </td>
              </tr>`;
          $('#asl-table tbody').append(noResultsRow);
      }
    }
  
    //show all prescriptions 
    function showAllPrescriptions() {
      $('#asl-table tbody tr').show();
      $('#alr-table tbody tr').show();
      $('#no-results').remove();
    }
  
    // printing function
    $('#script-print').on('click', function() {
      console.log('Print button clicked');
      
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
  
    // debug info
    console.log('pt_id:', pt_id);
    console.log('pt_data:', pt_data);
    console.log('ASL Status:', pt_data.asl_status);
  });