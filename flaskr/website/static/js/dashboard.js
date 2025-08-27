function downloadScenario(id, name) {
  fetch(`/export-scenario/${id}`)
    .then(res => res.json())
    .then(data => {
      // Convert data to CSV
      const csvRows = [];
      const headers = Object.keys(data[0]);
      csvRows.push(headers.join(','));

      for (const row of data) {
            csvRows.push(Object.values(row).join(','));
      }

      const csvString = csvRows.join('\n');
      const blob = new Blob([csvString], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);

      // download CSV
      const a = document.createElement('a');
      a.href = url;
      a.download = `${name} Results.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
}

let currentScenarioId = null;

// When modal is opened, capture the ID
window.onload = function() {
    const exampleModal = document.getElementById('delete-scenario-menu');
    exampleModal.addEventListener('show.bs.modal', event => {
        const button = $(event.relatedTarget); // Button that triggered the modal
        currentScenarioId = button.data('scenario-id');
        $("#modal-scenario-name").text(button.data('scenario-name'));
    });
}

function deleteScenario() {
    let res = confirm("Are you sure you wish to delete this scenario? Once a scenario has been deleted, it cannot be recovered.");
    if (res) {
        $.ajax({
            url: `/delete-scenario/${currentScenarioId}`,
            type: 'DELETE',
            success: function () {
                // Reload page. TODO: remove row instead
                location.reload();
            },
            error: function () {
                alert("Failed to delete scenario");
            }
        });
    }
}
