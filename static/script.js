// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadResults = document.getElementById('uploadResults');
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');
const searchResults = document.getElementById('searchResults');
const statusText = document.getElementById('statusText');
const imageCount = document.getElementById('imageCount');
const loadingOverlay = document.getElementById('loadingOverlay');

// State
let isUploading = false;
let isSearching = false;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    updateStatus();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    // Upload area events
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Search events
    searchButton.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });
    
    // Real-time search (debounced)
    let searchTimeout;
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            if (searchInput.value.trim()) {
                handleSearch();
            } else {
                searchResults.innerHTML = '';
            }
        }, 500);
    });
}

// Drag and Drop Handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    handleFiles(files);
}

function handleFileSelect(e) {
    handleFiles(e.target.files);
}

// File Upload Handler
async function handleFiles(files) {
    if (isUploading || files.length === 0) return;
    
    isUploading = true;
    showLoading();
    updateStatus('Uploading files...');
    
    const formData = new FormData();
    Array.from(files).forEach(file => {
        formData.append('files', file);
    });
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            displayUploadResults(result);
            updateStatus(`Upload complete! Processed ${result.total_processed} images.`);
            setTimeout(() => updateStatus(), 3000);
        } else {
            showError(result.error || 'Upload failed');
        }
    } catch (error) {
        showError('Network error during upload');
    } finally {
        isUploading = false;
        hideLoading();
        updateStatus();
    }
}

// Search Handler
async function handleSearch() {
    if (isSearching || !searchInput.value.trim()) return;
    
    isSearching = true;
    searchButton.disabled = true;
    searchButton.textContent = '🔍 Searching...';
    
    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: searchInput.value.trim()
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            displaySearchResults(result);
        } else {
            showError(result.error || 'Search failed');
        }
    } catch (error) {
        showError('Network error during search');
    } finally {
        isSearching = false;
        searchButton.disabled = false;
        searchButton.textContent = '🔍 Search';
    }
}

// Display Functions
function displayUploadResults(result) {
    uploadResults.innerHTML = '';
    
    if (result.results && result.results.length > 0) {
        result.results.forEach(item => {
            const resultDiv = document.createElement('div');
            resultDiv.className = `upload-result ${item.status}`;
            
            const statusIcon = {
                'success': '✅',
                'error': '❌',
                'skipped': '⏭️'
            }[item.status] || '❓';
            
            resultDiv.innerHTML = `
                <span>${statusIcon} ${item.filename}</span>
                <span>${item.message}</span>
            `;
            
            uploadResults.appendChild(resultDiv);
        });
    }
}

function displaySearchResults(result) {
    searchResults.innerHTML = '';
    
    if (result.results && result.results.length > 0) {
        result.results.forEach(item => {
            const resultDiv = document.createElement('div');
            resultDiv.className = 'search-result';
            
            resultDiv.innerHTML = `
                <img src="${item.image_url}" alt="${item.filename}" class="result-image" 
                     onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIwIiBoZWlnaHQ9IjgwIiB2aWV3Qm94PSIwIDAgMTIwIDgwIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cmVjdCB3aWR0aD0iMTIwIiBoZWlnaHQ9IjgwIiBmaWxsPSIjRjdGQUZDIi8+CjxwYXRoIGQ9Ik00MCA0MEw2MCAyMEw4MCA0MEw2MCA2MEw0MCA0MFoiIGZpbGw9IiNFMkU4RjAiLz4KPC9zdmc+Cg=='" />
                <div class="result-content">
                    <div class="result-header">
                        <span class="result-filename">${item.filename}</span>
                        <span class="confidence-score">${item.confidence}%</span>
                    </div>
                    <div class="result-description">${item.description}</div>
                </div>
            `;
            
            searchResults.appendChild(resultDiv);
        });
    } else {
        searchResults.innerHTML = `
            <div class="empty-state">
                <h3>No results found</h3>
                <p>Try adjusting your search query or upload more screenshots</p>
            </div>
        `;
    }
}

// Status Updates
async function updateStatus(message = null) {
    if (message) {
        statusText.textContent = message;
        return;
    }
    
    try {
        const response = await fetch('/status');
        const result = await response.json();
        
        if (response.ok) {
            statusText.textContent = 'Ready to upload and search';
            imageCount.textContent = `${result.total_images} images indexed`;
        } else {
            statusText.textContent = 'Status unavailable';
        }
    } catch (error) {
        statusText.textContent = 'Status unavailable';
    }
}

// Utility Functions
function showLoading() {
    loadingOverlay.classList.add('show');
}

function hideLoading() {
    loadingOverlay.classList.remove('show');
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    // Show error in upload results or search results
    if (uploadResults.children.length === 0) {
        uploadResults.appendChild(errorDiv);
    } else {
        searchResults.innerHTML = '';
        searchResults.appendChild(errorDiv);
    }
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}

// File validation
function validateFiles(files) {
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'];
    const maxSize = 16 * 1024 * 1024; // 16MB
    
    for (let file of files) {
        if (!allowedTypes.includes(file.type)) {
            throw new Error(`Invalid file type: ${file.name}`);
        }
        if (file.size > maxSize) {
            throw new Error(`File too large: ${file.name} (max 16MB)`);
        }
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + U for upload
    if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
        e.preventDefault();
        fileInput.click();
    }
    
    // Ctrl/Cmd + F for search focus
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        searchInput.focus();
    }
});