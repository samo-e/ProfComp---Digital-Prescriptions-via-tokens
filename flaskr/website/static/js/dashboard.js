function downloadScenario(id) {
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
      a.download = `scenario-${data.id}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
}
