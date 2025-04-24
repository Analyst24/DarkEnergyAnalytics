document.addEventListener('DOMContentLoaded', function() {
    // Mobile sidebar toggle
    const toggleButton = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (toggleButton && sidebar) {
        toggleButton.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
    
    // Close alert buttons
    const closeButtons = document.querySelectorAll('.close-alert');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.parentElement;
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        });
    });
    
    // File input handling for custom data upload
    const fileInput = document.querySelector('input[type="file"]');
    const fileNameDisplay = document.querySelector('.file-name');
    
    if (fileInput && fileNameDisplay) {
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileNameDisplay.textContent = this.files[0].name;
            } else {
                fileNameDisplay.textContent = 'No file selected';
            }
        });
    }
    
    // Dataset selection change handler for anomaly detection
    const datasetSelect = document.getElementById('dataset');
    const algorithmSelect = document.getElementById('algorithm');
    
    if (datasetSelect && algorithmSelect) {
        // Update algorithm recommendations based on dataset size
        datasetSelect.addEventListener('change', function() {
            const datasetId = this.value;
            if (datasetId) {
                // You could fetch dataset info here and recommend algorithms
                // For now, we'll just reset the algorithm selection
                algorithmSelect.value = 'isolation_forest';
            }
        });
    }
    
    // Toggle between upload and manual data entry sections
    const dataEntryToggle = document.querySelectorAll('.data-entry-toggle');
    if (dataEntryToggle.length > 0) {
        const uploadSection = document.getElementById('upload-section');
        const manualSection = document.getElementById('manual-section');
        
        dataEntryToggle.forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                const target = this.getAttribute('data-target');
                
                dataEntryToggle.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                if (target === 'upload' && uploadSection && manualSection) {
                    uploadSection.style.display = 'block';
                    manualSection.style.display = 'none';
                } else if (target === 'manual' && uploadSection && manualSection) {
                    uploadSection.style.display = 'none';
                    manualSection.style.display = 'block';
                }
            });
        });
    }
    
    // Date range validation for generate data form
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const numPointsInput = document.getElementById('num_data_points');
    
    if (startDateInput && endDateInput && numPointsInput) {
        const validateDates = function() {
            const startDate = new Date(startDateInput.value);
            const endDate = new Date(endDateInput.value);
            
            if (startDate && endDate && startDate > endDate) {
                endDateInput.setCustomValidity('End date must be after start date');
            } else {
                endDateInput.setCustomValidity('');
                
                // Suggest appropriate number of data points based on date range
                if (startDate && endDate) {
                    const daysDiff = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
                    const suggestedPoints = daysDiff * 24; // Hourly data
                    numPointsInput.placeholder = `Suggested: ${suggestedPoints}`;
                }
            }
        };
        
        startDateInput.addEventListener('change', validateDates);
        endDateInput.addEventListener('change', validateDates);
    }
    
    // Handle include anomalies toggle in generate data form
    const includeAnomaliesSelect = document.getElementById('include_anomalies');
    const anomalyPercentageField = document.getElementById('anomaly_percentage_field');
    
    if (includeAnomaliesSelect && anomalyPercentageField) {
        const toggleAnomalyPercentage = function() {
            if (includeAnomaliesSelect.value === 'yes') {
                anomalyPercentageField.style.display = 'block';
            } else {
                anomalyPercentageField.style.display = 'none';
            }
        };
        
        includeAnomaliesSelect.addEventListener('change', toggleAnomalyPercentage);
        toggleAnomalyPercentage(); // Initial state
    }
    
    // Tooltips for information icons
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseover', function() {
            const tooltipText = this.querySelector('.tooltip-text');
            tooltipText.style.visibility = 'visible';
            tooltipText.style.opacity = '1';
        });
        
        tooltip.addEventListener('mouseout', function() {
            const tooltipText = this.querySelector('.tooltip-text');
            tooltipText.style.visibility = 'hidden';
            tooltipText.style.opacity = '0';
        });
    });
});

// Function to confirm deletion actions
function confirmDelete(message, formId) {
    if (confirm(message || 'Are you sure you want to delete this item?')) {
        document.getElementById(formId).submit();
    }
    return false;
}

// Function to toggle password visibility
function togglePasswordVisibility(inputId, iconId) {
    const passwordInput = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}
