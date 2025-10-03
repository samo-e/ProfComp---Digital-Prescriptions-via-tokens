$(document).ready(function() {
  // collapse functionality
  $('.btn-collapse').on('click', function() {
      var $btn = $(this);
      var $icon = $btn.find('i');
      $icon.toggleClass('bi-chevron-up bi-chevron-down');
  });
  
  // Initialize button
  initializeButtonStates();
  
  // Request Access button
  $('#btn-request-access').on('click', function() {
      console.log('Request Access clicked');
      
      if ($(this).prop('disabled')) {
          console.log('Button is disabled, ignoring click');
          return;
      }
      
      $(this).prop('disabled', true);
      
      const token = $('meta[name="csrf-token"]').attr('content');
      $.ajax({ url: `/api/asl/${pt_id}/request-access`, method: 'POST', headers: { 'X-CSRFToken': token } })
      .done(function(data) {
          console.log('Request Access response:', data);
          if (data.success) {
              alert(data.message);
              $('#asl-status').text(data.new_status);
              
              if (data.should_disable_button) {
                  updateButtonStates('PENDING');
              }
              
              if (data.new_status === 'Pending') {
                  $('#btn-refresh').show();
              }
          } else {
              alert('Request failed: ' + data.error);
              $('#btn-request-access').prop('disabled', false);
          }
      })
      .fail(function(xhr, status, error) {
          console.error('Request Access failed:', status, error);
          alert('Request failed: ' + error);
          $('#btn-request-access').prop('disabled', false);
      });
  });

  // Refresh button
  $('#btn-refresh').on('click', function() {
      console.log('Refresh clicked');
      
      $(this).prop('disabled', true).text('Refreshing...');
      
      const token = $('meta[name="csrf-token"]').attr('content');
      $.ajax({ url: `/api/asl/${pt_id}/refresh`, method: 'POST', headers: { 'X-CSRFToken': token } })
      .done(function(data) {
          console.log('Refresh response:', data);
          if (data.success) {
              alert(data.message);
              
              // Handle consent_status structure
              if (data['consent-status']) {
                $('#consent-status').text(data['consent-status'].status);
                $('#consent-last-updated').text(`(last updated ${data['consent-status']['last-updated']})`);
              }
              
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
          $('#btn-refresh').prop('disabled', false).text('Refresh');
      });
  });

  // Delete Consent button
  $('#btn-delete-consent').on('click', function() {
      console.log('Delete Consent clicked');
      
      if (!confirm('Delete consent record? This will reset the patient to "No Consent" status.')) {
          return;
      }
      
      const token = $('meta[name="csrf-token"]').attr('content');
      $.ajax({
          url: `/api/patient/${pt_id}/consent`,
          method: 'DELETE',
          headers: { 'X-CSRFToken': token },
          success: function(data) {
              console.log('Delete Consent response:', data);
              if (data.success) {
                  alert(data.message);
                  
                  $('#consent-status').text('No Consent').removeClass('consent-granted consent-pending consent-rejected').addClass('consent-no-consent');
                  $('#consent-last-updated').hide();
                  $('#btn-delete-consent').hide();
                  $('#btn-request-access').removeClass('btn-secondary').addClass('btn-info')
                      .prop('disabled', false).text('Request Access').show();
                  $('#btn-refresh').show();
                  
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

  // search functionality
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

  function showAllPrescriptions() {
      $('#asl-table tbody tr').show();
      $('#alr-table tbody tr').show();
      $('#no-results').remove();
  }

  $('#script-print').on('click', function() {
      console.log('Print button clicked');
      
      const selectedIds = [];
      $('#asl-table tbody input[type="checkbox"]:checked').each(function() {
          selectedIds.push(parseInt($(this).val()));
      });
      
      console.log('Selected prescription IDs:', selectedIds);
  });

  // Dispense selected (students only)
  $('#script-dispense').on('click', function() {
      const selectedIds = [];
      $('#asl-table tbody input[type="checkbox"]:checked').each(function() {
          selectedIds.push(parseInt($(this).val()));
      });
      if (selectedIds.length === 0) {
          alert('Select at least one prescription to dispense');
          return;
      }
      $(this).prop('disabled', true).text('Dispensing...');
      const token = $('meta[name="csrf-token"]').attr('content');
      $.ajax({
          url: '/api/prescriptions/dispense',
          method: 'POST',
          contentType: 'application/json',
          headers: { 'X-CSRFToken': token },
          data: JSON.stringify({ prescription_ids: selectedIds }),
          success: function(data) {
              if (data.success) {
                  alert(`Dispensed ${data.updated} prescription(s)`);
                  if (data.should_reload) {
                      location.reload();
                  }
              } else {
                  alert(data.error || 'Dispense failed');
              }
          },
          error: function(xhr) {
              if (xhr.status === 403) {
                  alert(xhr.responseJSON?.error || 'Not permitted');
              } else {
                  alert('Dispense failed');
              }
          },
          complete: () => $('#script-dispense').prop('disabled', false).text('Dispense Selected')
      });
  });

  function initializeButtonStates() {
      // consent_status nested structure
      const aslStatus = pt_data['consent-status']['status'];
      updateButtonStates(aslStatus);
  }
  
  function updateButtonStates(status) {
      const $requestBtn = $('#btn-request-access');
      const $refreshBtn = $('#btn-refresh');
      const $deleteBtn = $('#btn-delete-consent');
      
      $requestBtn.removeClass('btn-secondary btn-info btn-warning btn-success').prop('disabled', false);
      $refreshBtn.show();
      $deleteBtn.show();
      
      switch(status.toUpperCase()) {
          case 'NO CONSENT':
          case 'NO_CONSENT':
              $requestBtn.addClass('btn-info').prop('disabled', false).text('Request Access');
              $refreshBtn.show().text('Refresh');
              $deleteBtn.hide();
              break;
              
          case 'PENDING':
              $requestBtn.addClass('btn-secondary').prop('disabled', true).text('Request Access');
              $refreshBtn.show().text('Refresh');
              $deleteBtn.show();
              break;
              
          case 'GRANTED':
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
    console.log('ASL Status:', pt_data['consent-status']['status']);
  });