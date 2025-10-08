// flaskr/website/static/js/submit_work.js

// File upload preview and validation
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('pdf_file');
    const filePreview = document.getElementById('file-preview');
    const fileList = document.getElementById('file-list');
    const submitForm = document.querySelector('form');
    const maxSize = 10 * 1024 * 1024; // 10MB in bytes

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const files = e.target.files;
            
            // Clear previous list
            fileList.innerHTML = '';
            
            if (files.length > 0) {
                $(filePreview).removeClass('d-none');
                
                Array.from(files).forEach(function(file, index) {
                    const listItem = document.createElement('li');
                    listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                    
                    // Validate file size
                    const isValidSize = file.size <= maxSize;
                    const sizeText = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
                    
                    // Get file icon based on type
                    let icon = 'bi-file-earmark';
                    if (file.type.includes('pdf')) {
                        icon = 'bi-file-earmark-pdf text-danger';
                    } else if (file.type.includes('word') || file.name.endsWith('.doc') || file.name.endsWith('.docx')) {
                        icon = 'bi-file-earmark-word text-primary';
                    } else if (file.type.includes('text')) {
                        icon = 'bi-file-earmark-text text-info';
                    }
                    
                    listItem.innerHTML = `
                        <div>
                            <i class="bi ${icon} me-2"></i>
                            <span class="${isValidSize ? '' : 'text-danger'}">${file.name}</span>
                            <small class="text-muted ms-2">(${sizeText})</small>
                            ${!isValidSize ? '<br><small class="text-danger">File too large - maximum 10MB</small>' : ''}
                        </div>
                        <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeFile(${index})">
                            <i class="bi bi-x"></i>
                        </button>
                    `;
                    
                    fileList.appendChild(listItem);
                });
            } else {
                filePreview.style.display = 'none';
            }
        });
    }

    // Form validation
    if (submitForm) {
        submitForm.addEventListener('submit', function(e) {
            const files = document.getElementById('pdf_file').files;
            let hasInvalidFile = false;
            
            Array.from(files).forEach(function(file) {
                if (file.size > maxSize) {
                    hasInvalidFile = true;
                }
            });
            
            if (hasInvalidFile) {
                e.preventDefault();
                alert('Some files are too large. Please remove files larger than 10MB before submitting.');
                return false;
            }
        });
    }
});

function removeFile(index) {
    const fileInput = document.getElementById('pdf_file');
    const dt = new DataTransfer();
    
    // Add all files except the one to remove
    Array.from(fileInput.files).forEach((file, i) => {
        if (i !== index) {
            dt.items.add(file);
        }
    });
    
    fileInput.files = dt.files;
    
    // Trigger change event to update preview
    fileInput.dispatchEvent(new Event('change'));
}