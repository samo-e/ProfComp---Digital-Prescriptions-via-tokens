$(document).ready(function() {
  // collapse button
  $('.btn-collapse').on('click', function() {
    var $btn = $(this);
    var $icon = $btn.find('i');
    $icon.toggleClass('bi-chevron-up bi-chevron-down');
  });
  


  
    // Request Access button
    $('#btn-request-access').on('click', function() {
      console.log('Request Access clicked');
      
      $.post(`/api/asl/${pt_id}/request-access`)
      .done(function(data) {
          console.log('Request Access response:', data);
          if (data.success) {
              alert(data.message);
              $('#asl-status').text(data.new_status);
          } else {
              alert('Request failed: ' + data.error);
          }
      })
      .fail(function(xhr, status, error) {
          console.error('Request Access failed:', status, error);
          alert('Request failed: ' + error);
      });
    });
  
    // Refresh button
    $('#btn-refresh').on('click', function() {
      console.log('Refresh clicked');
      
      $.post(`/api/asl/${pt_id}/refresh`)
      .done(function(data) {
          console.log('Refresh response:', data);
          if (data.success) {
              alert(data.message);
              location.reload();
          } else {
              alert('Refresh failed: ' + data.error);
          }
      })
      .fail(function(xhr, status, error) {
          console.error('Refresh failed:', status, error);
          alert('Refresh failed: ' + error);
      });
    });
  
    // Delete Consent button
    $('#btn-delete-consent').on('click', function() {
      console.log('Delete Consent clicked');
      
      if (!confirm('Are you sure you want to delete consent? This action cannot be undone.')) {
          return;
      }
      
      $.ajax({
          url: `/api/patient/${pt_id}/consent`,
          method: 'DELETE',
          success: function(data) {
              console.log('Delete Consent response:', data);
              if (data.success) {
                  alert(data.message);
                  $('#consent-status').removeClass('granted').addClass('revoked').text(data.consent_status);
                  $('#consent-last-updated').text(`(last updated ${data.last_updated})`);
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
  
    // just use front end search to avoid the conflict (otherwise the table info would disappear)
    $('#search-input').on('input', function() {
      const query = $(this).val().trim().toLowerCase();
      console.log('Search query:', query);
      
      if (query.length === 0) {
          // if the search box is empty, show all things
          showAllPrescriptions();
          return;
      }
      
      // text search in table rows (without filter function (?))
      performFrontendSearch(query);
    });
  
    // front end search function
    function performFrontendSearch(query) {
      let hasResults = false;
      
      // search ASL table
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
      
      // search ALR table
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
      
      // show no results meesage if needed
      handleNoResults(hasResults);
    }
  
    // // back end search
    // function performBackendSearch(query) {
    //   $.get(`/api/asl/${pt_id}/search`, {q: query})
    //   .done(function(data) {
    //       console.log('Backend search results:', data);
    //       if (data.success) {
    //          # if it's more accurate, then use this result
    //           displayBackendSearchResults(data.results);
    //       }
    //   })
    //   .fail(function(xhr, status, error) {
    //       console.error('Backend search failed:', status, error);
    //       
    //   });
    // }
  
    // // show back end search results
    // function displayBackendSearchResults(results) {
    //   // hide all rows first
    //   $('#asl-table tbody tr').hide();
    //   $('#alr-table tbody tr').hide();
      
    //   if (results.length === 0) {
    //       handleNoResults(false);
    //       return;
    //   }
      
    //   // show prescriptions
    //   results.forEach(function(result) {
    //       $(`#asl-table tbody tr[data-prescription-id="${result.prescription_id}"]`).show();
    //       $(`#alr-table tbody tr[data-prescription-id="${result.prescription_id}"]`).show();
    //   });
      
    //   handleNoResults(true);
    // }
  
    // when there's no search result
    function handleNoResults(hasResults) {
      $('#no-results').remove();
      
      if (!hasResults) {
          // show 'no results' in table
          const noResultsRow = `
              <tr id="no-results">
                  <td colspan="7" class="text-center text-muted py-4">
                      <i class="bi bi-search"></i> No matching prescriptions found
                  </td>
              </tr>`;
          $('#asl-table tbody').append(noResultsRow);
      }
    }
  
    // show all the prescription
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
      
      // the function is in the print_script.js
    });
  
    // debuf info
    console.log('pt_id:', pt_id);
    console.log('pt_data:', pt_data);
  });