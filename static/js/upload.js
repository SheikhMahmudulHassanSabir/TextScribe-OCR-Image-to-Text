/**
 * upload.js - Handles image uploads and OCR processing
 */

document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const convertBtn = document.getElementById('convertBtn');
    const clearBtn = document.getElementById('clearBtn');
    const imagePreview = document.getElementById('imagePreview');
    const previewImage = document.getElementById('previewImage');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const removeImage = document.getElementById('removeImage');
    const resultSection = document.getElementById('resultSection');
    const resultText = document.getElementById('resultText');
    const confidenceValue = document.getElementById('confidenceValue');
    const timeValue = document.getElementById('timeValue');
    const loadingOverlay = document.getElementById('loadingOverlay');

    // Handle drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.add('highlight'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('highlight'), false);
    });

    uploadArea.addEventListener('drop', handleDrop, false);
    uploadArea.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    previewImage.src = e.target.result;
                    uploadPlaceholder.style.display = 'none';
                    imagePreview.style.display = 'block';
                    convertBtn.disabled = false;
                    clearBtn.disabled = false;
                };
                reader.readAsDataURL(file);
            }
        }
    }

    removeImage.addEventListener('click', (e) => {
        e.stopPropagation();
        clearUpload();
    });

    clearBtn.addEventListener('click', clearUpload);

    function clearUpload() {
        fileInput.value = '';
        previewImage.src = '';
        imagePreview.style.display = 'none';
        uploadPlaceholder.style.display = 'block';
        convertBtn.disabled = true;
        clearBtn.disabled = true;
        resultSection.style.display = 'none';
    }

    convertBtn.addEventListener('click', async () => {
        const file = fileInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        loadingOverlay.style.display = 'flex';

        try {
            const response = await fetch('/api/v1/ocr/recognize', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            if (data.success) {
                resultText.value = data.full_text;
                confidenceValue.textContent = (data.results.length > 0 ? (data.results[0].confidence * 100).toFixed(2) : '0') + '%';
                timeValue.textContent = data.processing_time_ms;
                resultSection.style.display = 'block';
                resultSection.scrollIntoView({ behavior: 'smooth' });
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            console.error('Error during OCR:', error);
            alert('An error occurred during processing.');
        } finally {
            loadingOverlay.style.display = 'none';
        }
    });
});
