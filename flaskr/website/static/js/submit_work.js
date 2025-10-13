// flaskr/website/static/js/submit_work.js

/**
 * Initialize file upload preview and validation
 */
$(function () {
  const fileInput = $("#pdf_file");

  if (fileInput.length) {
    fileInput.on("change", handleFileSelection);
  }
});

/**
 * Handle file selection and preview
 * @param {Event} e - The change event from file input
 */
function handleFileSelection(e) {
  const files = e.target.files;
  const $filePreview = $("#file-preview");
  const $fileList = $("#file-list");
  const maxSize = 10 * 1024 * 1024; // 10MB in bytes

  // Clear previous list
  $fileList.empty();

  if (files.length > 0) {
    // Show the preview section using jQuery (if available) or vanilla JS
    $filePreview.removeClass("d-none");

    let hasErrors = false;

    // Process each file
    $.each(files, function (index, file) {
      const $li = $("<li>", {
        class:
          "list-group-item d-flex justify-content-between align-items-center",
      });
      const $fileInfo = $("<div>").html(
        "<strong>" +
          escapeHtml(file.name) +
          "</strong><br>" +
          '<small class="text-muted">' +
          formatFileSize(file.size) +
          "</small>"
      );
      const $fileStatus = $("<span>");
      if (file.size > maxSize) {
        $fileStatus.addClass("badge bg-danger").text("Too Large");
        hasErrors = true;
      } else {
        $fileStatus.addClass("badge bg-success").text("Valid");
      }
      $li.append($fileInfo, $fileStatus);
      $fileList.append($li);
    });

    // Disable submit button if there are errors
    $("#submit-btn").prop("disabled", hasErrors);

    // Show error message if files are too large
    if (hasErrors) {
      const $errorMsg = $("<div>", {
        class: "alert alert-danger mt-2",
        text: "Some files exceed the 10MB limit. Please remove them before submitting.",
      });
      $filePreview.append($errorMsg);
    }
  } else {
    $filePreview.addClass("d-none");
  }
}

/**
 * Format file size to human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
  return $("<div>").text(text).html();
}
