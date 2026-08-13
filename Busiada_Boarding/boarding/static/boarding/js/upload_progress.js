/**
 * Media Upload Progress Tracker for Django Admin
 * Shows real-time upload percentage for media files
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find all file input fields
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        // Create container for progress display
        const container = document.createElement('div');
        container.className = 'file-upload-container';
        container.style.marginTop = '10px';
        
        // Progress bar
        const progressBar = document.createElement('div');
        progressBar.className = 'upload-progress-bar';
        progressBar.style.display = 'none';
        progressBar.style.width = '100%';
        progressBar.style.height = '20px';
        progressBar.style.backgroundColor = '#f0f0f0';
        progressBar.style.borderRadius = '4px';
        progressBar.style.overflow = 'hidden';
        progressBar.style.border = '1px solid #ddd';
        
        const progressFill = document.createElement('div');
        progressFill.className = 'upload-progress-fill';
        progressFill.style.height = '100%';
        progressFill.style.backgroundColor = '#417690';
        progressFill.style.width = '0%';
        progressFill.style.transition = 'width 0.3s ease';
        progressBar.appendChild(progressFill);
        
        // Progress text
        const progressText = document.createElement('div');
        progressText.className = 'upload-progress-text';
        progressText.style.display = 'none';
        progressText.style.marginTop = '8px';
        progressText.style.fontSize = '12px';
        progressText.style.color = '#666';
        progressText.textContent = '0%';
        
        // File size display
        const fileSizeDisplay = document.createElement('div');
        fileSizeDisplay.className = 'upload-file-size';
        fileSizeDisplay.style.marginTop = '5px';
        fileSizeDisplay.style.fontSize = '12px';
        fileSizeDisplay.style.color = '#999';
        
        container.appendChild(progressBar);
        container.appendChild(progressText);
        container.appendChild(fileSizeDisplay);
        
        input.parentNode.insertBefore(container, input.nextSibling);
        
        // Listen for file selection
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Display file size
                const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                fileSizeDisplay.textContent = `File: ${file.name} (${sizeMB} MB)`;
                fileSizeDisplay.style.color = getSizeColor(file.size);
                
                // Show progress
                progressBar.style.display = 'block';
                progressText.style.display = 'block';
                
                // Simulate upload progress (real progress comes from form submission)
                simulateProgress(progressFill, progressText, file.size);
            }
        });
    });
    
    // Handle form submission with real progress
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const fileInput = form.querySelector('input[type="file"]');
            if (fileInput && fileInput.files.length > 0) {
                trackFormUpload(fileInput, form);
            }
        });
    });
});

function getSizeColor(bytes) {
    const mb = bytes / (1024 * 1024);
    if (mb > 5) return '#d9534f'; // Red for too large
    if (mb > 3) return '#f0ad4e'; // Orange for large
    if (mb > 1) return '#5bc0de'; // Blue for medium
    return '#5cb85c'; // Green for small
}

function simulateProgress(progressFill, progressText, fileSize) {
    let currentProgress = 0;
    const interval = setInterval(() => {
        if (currentProgress < 90) {
            currentProgress += Math.random() * 30;
            if (currentProgress > 90) currentProgress = 90;
        } else {
            clearInterval(interval);
            return;
        }
        
        progressFill.style.width = currentProgress + '%';
        progressText.textContent = Math.round(currentProgress) + '%';
    }, 300);
}

function trackFormUpload(fileInput, form) {
    const file = fileInput.files[0];
    const container = fileInput.parentNode.querySelector('.file-upload-container');
    
    if (container) {
        const progressFill = container.querySelector('.upload-progress-fill');
        const progressText = container.querySelector('.upload-progress-text');
        
        // Reset and start actual upload
        progressFill.style.width = '0%';
        progressText.textContent = '0%';
        
        // This will be handled by Django's form submission
        // The server should send progress updates via XMLHttpRequest
        // For now, we simulate it
        let progress = 0;
        const uploadInterval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress > 95) progress = 95;
            
            progressFill.style.width = progress + '%';
            progressText.textContent = Math.round(progress) + '%';
            
            if (form.classList.contains('submitted')) {
                progress = 100;
                progressFill.style.width = '100%';
                progressText.textContent = '100% - Processing...';
                clearInterval(uploadInterval);
            }
        }, 200);
    }
}

// Add CSS styles dynamically
const style = document.createElement('style');
style.textContent = `
    .file-upload-container {
        margin-top: 10px;
        margin-bottom: 15px;
    }
    
    .upload-progress-bar {
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .upload-progress-fill {
        transition: width 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 11px;
        font-weight: bold;
    }
    
    .upload-progress-text {
        font-weight: 500;
        margin-top: 8px;
    }
    
    .upload-file-size {
        padding: 8px;
        background-color: #f9f9f9;
        border-radius: 3px;
        border-left: 3px solid #417690;
    }
`;
document.head.appendChild(style);
