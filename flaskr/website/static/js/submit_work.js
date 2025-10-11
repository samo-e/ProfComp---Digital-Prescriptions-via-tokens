// flaskr/website/static/js/submit_work.js

/**
 * Initialize file upload preview and validation
 */
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('pdf_file');
    
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelection);
    }
});

/**
 * Handle file selection and preview
 * @param {Event} e - The change event from file input
 */
function handleFileSelection(e) {
    const files = e.target.files;
    const filePreview = document.getElementById('file-preview');
    const fileList = document.getElementById('file-list');
    const maxSize = 10 * 1024 * 1024; // 10MB in bytes
    
    // Clear previous list
    fileList.innerHTML = '';
    
    if (files.length > 0) {
        // Show the preview section using jQuery (if available) or vanilla JS
        if (typeof $ !== 'undefined') {
            $(filePreview).removeClass('d-none');
        } else {
            filePreview.classList.remove('d-none');
        }
        
        let hasErrors = false;
        
        // Process each file
        Array.from(files).forEach(function(file, index) {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center';
            
            // File info
            const fileInfo = document.createElement('div');
            fileInfo.innerHTML = '<strong>' + escapeHtml(file.name) + '</strong><br>' +
                                '<small class="text-muted">' + formatFileSize(file.size) + '</small>';
            
            // File status
            const fileStatus = document.createElement('span');
            
            if (file.size > maxSize) {
                fileStatus.className = 'badge bg-danger';
                fileStatus.textContent = 'Too Large';
                hasErrors = true;
            } else {
                fileStatus.className = 'badge bg-success';
                fileStatus.textContent = 'Valid';
            }
            
            li.appendChild(fileInfo);
            li.appendChild(fileStatus);
            fileList.appendChild(li);
        });
        
        // Disable submit button if there are errors
        const submitBtn = document.getElementById('submit-btn');
        if (submitBtn) {
            submitBtn.disabled = hasErrors;
        }
        
        // Show error message if files are too large
        if (hasErrors) {
            const errorMsg = document.createElement('div');
            errorMsg.className = 'alert alert-danger mt-2';
            errorMsg.textContent = 'Some files exceed the 10MB limit. Please remove them before submitting.';
            filePreview.appendChild(errorMsg);
        }
    } else {
        // Hide preview if no files selected
        if (typeof $ !== 'undefined') {
            $(filePreview).addClass('d-none');
        } else {
            filePreview.classList.add('d-none');
        }
    }
}

/**
 * Format file size to human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}