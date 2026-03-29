// upload.js - Restored baseline frontend
document.addEventListener('DOMContentLoaded', () => {
    console.log('[DEBUG] Upload.js loaded');

    const fileInput = document.getElementById('fileInput');
    const convertBtn = document.getElementById('convertBtn');
    const clearBtn = document.getElementById('clearBtn');
    const resultSection = document.getElementById('resultSection');
    const resultText = document.getElementById('resultText');
    const uploadArea = document.getElementById('uploadArea');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const imagePreview = document.getElementById('imagePreview');
    const previewImage = document.getElementById('previewImage');
    const removeImage = document.getElementById('removeImage');
    const newUploadBtn = document.getElementById('newUploadBtn'); // declared once, in outer scope

    console.log('[DEBUG] Elements found:', {
        fileInput: !!fileInput,
        convertBtn: !!convertBtn,
        resultSection: !!resultSection,
        resultText: !!resultText,
        newUploadBtn: !!newUploadBtn
    });

    // Make the upload area clickable
    uploadArea.addEventListener('click', () => {
        if (imagePreview.style.display === 'none' || imagePreview.style.display === '') {
            fileInput.click();
        }
    });

    // Handle file selection
    fileInput.addEventListener('change', function(e) {
        if (this.files && this.files[0]) {
            console.log('[DEBUG] File selected:', this.files[0].name);
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                uploadPlaceholder.style.display = 'none';
                imagePreview.style.display = 'block';
                convertBtn.disabled = false;
                clearBtn.disabled = false;
            };
            reader.readAsDataURL(this.files[0]);
        }
    });

    // Clear / reset the upload area
    clearBtn.addEventListener('click', () => {
        fileInput.value = '';
        previewImage.src = '';
        uploadPlaceholder.style.display = 'block';
        imagePreview.style.display = 'none';
        convertBtn.disabled = true;
        clearBtn.disabled = true;
        resultSection.style.display = 'none';

        // Reset badges
        const confidenceValueEl = document.getElementById('confidenceValue');
        const timeValueEl = document.getElementById('timeValue');
        if (confidenceValueEl) confidenceValueEl.textContent = '--';
        if (timeValueEl) timeValueEl.textContent = '--';

        // Disable Upload New button after reset
        if (newUploadBtn) newUploadBtn.disabled = true;
    });

    removeImage.addEventListener('click', (e) => {
        e.stopPropagation();
        clearBtn.click();
    });

    // Handle form submission / OCR conversion
    convertBtn.addEventListener('click', async () => {
        console.log('[DEBUG] Convert button clicked');
        
        // Request required notification permissions interactively
        if (typeof requestNotificationPermission !== 'undefined') {
            requestNotificationPermission();
        }

        if (!fileInput.files || !fileInput.files[0]) {
            console.log('[DEBUG] No file selected');
            return;
        }

        convertBtn.disabled = true;
        convertBtn.textContent = 'Processing...';

        try {
            console.log('[DEBUG] Starting Tesseract.js OCR');
            
            // Show loading if there is a global function
            if (typeof showLoading === 'function') {
                showLoading('Initializing OCR Engine...');
            }

            const startTime = performance.now();
            
            // Run Tesseract
            const { data } = await Tesseract.recognize(
                fileInput.files[0],
                'eng',
                {
                    logger: m => {
                        console.log(m);
                        if (m.status === 'recognizing text' && typeof showLoading === 'function') {
                            showLoading(`Recognizing text: ${Math.round(m.progress * 100)}%`);
                        }
                    }
                }
            );

            console.log('[DEBUG] Tesseract result:', data);

            const processingTimeMs = Math.round(performance.now() - startTime);

            console.log('[DEBUG] Success, showing results');
            resultSection.style.display = 'block';

            // Update recognized text
            resultText.value = data.text || 'No text recognized';

            // Update badges
            const confidenceValueEl = document.getElementById('confidenceValue');
            const timeValueEl = document.getElementById('timeValue');

            let avgConfidence = Math.round(data.confidence || 0);

            if (confidenceValueEl) confidenceValueEl.textContent = avgConfidence + '%';
            if (timeValueEl) timeValueEl.textContent = processingTimeMs;

            // Enable new upload
            if (newUploadBtn) newUploadBtn.disabled = false;

        } catch (error) {
            console.error('[DEBUG] OCR error:', error);
            
            if (typeof showSystemError !== 'undefined') {
                showSystemError('Conversion Failed', error.message);
            } else {
                alert('Failed to process image: ' + error.message);
            }
        } finally {
            if (typeof hideLoading === 'function') {
                hideLoading();
            }
            convertBtn.disabled = false;
            convertBtn.textContent = 'Convert to Text';
        }
    });

    // Handle "Upload New" button — resets UI for a fresh upload
    if (newUploadBtn) {
        newUploadBtn.addEventListener('click', () => {
            clearBtn.click();
            resultSection.style.display = 'none';
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
            // Optionally trigger the file upload dialog immediately
            setTimeout(() => fileInput.click(), 100);
        });
    }

    // Handle Copy Button
    const copyBtn = document.getElementById('copyBtn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            if (resultText && resultText.value) {
                if (typeof copyToClipboard === 'function') {
                    copyToClipboard(resultText.value);
                } else {
                    navigator.clipboard.writeText(resultText.value);
                    alert('Text copied to clipboard!');
                }
            }
        });
    }

    // Handle Download Button
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            if (resultText && resultText.value) {
                if (typeof downloadTextFile === 'function') {
                    downloadTextFile(resultText.value, 'recognized_text.txt');
                } else {
                    const blob = new Blob([resultText.value], { type: 'text/plain;charset=utf-8' });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = 'recognized_text.txt';
                    link.click();
                    URL.revokeObjectURL(url);
                }
            }
        });
    }
});
