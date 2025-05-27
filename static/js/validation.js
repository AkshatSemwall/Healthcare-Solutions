// Hospital Management System - Form Validation and Interactivity

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize billing calculations
    initializeBillingCalculations();
    
    // Initialize insurance toggle
    initializeInsuranceToggle();
    
    // Initialize search functionality
    initializeSearch();
    
    // Initialize tooltips
    initializeTooltips();
});

function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(this)) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            // Add loading state to submit button
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('btn-loading');
                submitBtn.disabled = true;
            }
        });
        
        // Real-time validation for required fields
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            field.addEventListener('blur', function() {
                validateField(this);
            });
            
            field.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    // Clear all previous errors
    clearAllErrors(form);
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    // Special validations
    const patientRegistrationForm = document.getElementById('patientRegistrationForm');
    if (form === patientRegistrationForm) {
        isValid = validatePatientRegistration(form) && isValid;
    }
    
    const emergencyForm = document.getElementById('emergencyForm');
    if (form === emergencyForm) {
        isValid = validateEmergencyForm(form) && isValid;
    }
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    const fieldName = getFieldLabel(field);
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, `${fieldName} is required`);
        return false;
    }
    
    // Type-specific validations
    if (value) {
        switch (field.type) {
            case 'email':
                if (!validateEmail(value)) {
                    showFieldError(field, 'Please enter a valid email address');
                    return false;
                }
                break;
                
            case 'number':
                const min = field.getAttribute('min');
                const max = field.getAttribute('max');
                const numValue = parseFloat(value);
                
                if (isNaN(numValue)) {
                    showFieldError(field, `${fieldName} must be a valid number`);
                    return false;
                }
                
                if (min !== null && numValue < parseFloat(min)) {
                    showFieldError(field, `${fieldName} must be at least ${min}`);
                    return false;
                }
                
                if (max !== null && numValue > parseFloat(max)) {
                    showFieldError(field, `${fieldName} must not exceed ${max}`);
                    return false;
                }
                break;
        }
    }
    
    // Custom validations
    if (field.id === 'patient_id' && value) {
        if (!validatePatientId(value)) {
            showFieldError(field, 'Patient ID must be in format HMS-YYYY-XXXXXXXX');
            return false;
        }
    }
    
    clearFieldError(field);
    return true;
}

function validatePatientRegistration(form) {
    let isValid = true;
    
    // Validate age
    const ageField = form.querySelector('#age');
    if (ageField && ageField.value) {
        const age = parseInt(ageField.value);
        if (age < 0 || age > 150) {
            showFieldError(ageField, 'Please enter a valid age between 0 and 150');
            isValid = false;
        }
    }
    
    // Validate bill amounts
    const billAmount = form.querySelector('#bill_amount');
    const amountPaid = form.querySelector('#amount_paid');
    
    if (billAmount && amountPaid && billAmount.value && amountPaid.value) {
        const bill = parseFloat(billAmount.value);
        const paid = parseFloat(amountPaid.value);
        
        if (paid > bill) {
            showFieldError(amountPaid, 'Amount paid cannot exceed bill amount');
            isValid = false;
        }
    }
    
    return isValid;
}

function validateEmergencyForm(form) {
    let isValid = true;
    
    // Validate patient ID format
    const patientIdField = form.querySelector('#patient_id');
    if (patientIdField && patientIdField.value) {
        if (!validatePatientId(patientIdField.value)) {
            showFieldError(patientIdField, 'Patient ID must be in format HMS-YYYY-XXXXXXXX');
            isValid = false;
        }
    }
    
    return isValid;
}

function validatePatientId(patientId) {
    const pattern = /^HMS-\d{4}-[A-Za-z0-9]{8}$/;
    return pattern.test(patientId);
}

function validateEmail(email) {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function clearAllErrors(form) {
    const invalidFields = form.querySelectorAll('.is-invalid');
    invalidFields.forEach(field => {
        clearFieldError(field);
    });
}

function getFieldLabel(field) {
    const label = field.parentNode.querySelector('label');
    if (label) {
        return label.textContent.replace('*', '').trim();
    }
    return field.name || field.id || 'Field';
}

function initializeBillingCalculations() {
    const billAmountField = document.getElementById('bill_amount');
    const amountPaidField = document.getElementById('amount_paid');
    const outstandingField = document.getElementById('outstanding_amount');
    const paymentStatusField = document.getElementById('payment_status');
    
    if (billAmountField && amountPaidField && outstandingField) {
        function calculateOutstanding() {
            const billAmount = parseFloat(billAmountField.value) || 0;
            const amountPaid = parseFloat(amountPaidField.value) || 0;
            const outstanding = Math.max(0, billAmount - amountPaid);
            
            outstandingField.value = outstanding.toFixed(2);
            
            // Update payment status
            if (paymentStatusField) {
                if (outstanding === 0 && billAmount > 0) {
                    paymentStatusField.value = 'Fully Paid';
                } else if (amountPaid > 0 && outstanding > 0) {
                    paymentStatusField.value = 'Partially Paid';
                } else if (amountPaid === 0) {
                    paymentStatusField.value = 'Unpaid';
                }
            }
        }
        
        billAmountField.addEventListener('input', calculateOutstanding);
        amountPaidField.addEventListener('input', calculateOutstanding);
        
        // Initial calculation
        calculateOutstanding();
    }
}

function initializeInsuranceToggle() {
    const insuranceYes = document.getElementById('insurance_coverage_yes');
    const insuranceNo = document.getElementById('insurance_coverage_no');
    const insuranceDetails = document.getElementById('insurance_details_container');
    
    if (insuranceYes && insuranceNo && insuranceDetails) {
        function toggleInsuranceDetails() {
            if (insuranceYes.checked) {
                insuranceDetails.style.display = 'block';
                document.getElementById('insurance_details').setAttribute('required', 'required');
            } else {
                insuranceDetails.style.display = 'none';
                document.getElementById('insurance_details').removeAttribute('required');
                document.getElementById('insurance_details').value = '';
            }
        }
        
        insuranceYes.addEventListener('change', toggleInsuranceDetails);
        insuranceNo.addEventListener('change', toggleInsuranceDetails);
        
        // Initial state
        toggleInsuranceDetails();
    }
}

function initializeSearch() {
    // Patient search functionality
    const searchForm = document.querySelector('form[method="GET"]');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[name="search"]');
        if (searchInput) {
            // Debounced search
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    if (this.value.length >= 3 || this.value.length === 0) {
                        searchForm.submit();
                    }
                }, 500);
            });
        }
    }
    
    // Patient ID search button
    const searchPatientBtn = document.getElementById('searchPatientBtn');
    if (searchPatientBtn) {
        searchPatientBtn.addEventListener('click', function() {
            const patientIdField = document.getElementById('patient_id');
            const patientId = patientIdField ? patientIdField.value.trim() : '';
            
            if (!patientId) {
                showNotification('Please enter a Patient ID to search', 'warning');
                return;
            }
            
            if (!validatePatientId(patientId)) {
                showNotification('Please enter a valid Patient ID format (HMS-YYYY-XXXXXXXX)', 'error');
                return;
            }
            
            // In a real implementation, this would make an AJAX call to search for the patient
            showNotification('Patient search functionality will be enhanced in a future update', 'info');
        });
    }
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2
    }).format(amount);
}

// Utility function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Utility function to format time
function formatDateTime(dateTimeString) {
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Patient ID generator helper
function generatePatientId() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    
    return `HMS-${year}-${month}${day}${hours}${minutes}`;
}

// Export functions for use in other scripts
window.HospitalMS = {
    validatePatientId,
    validateEmail,
    showNotification,
    formatCurrency,
    formatDate,
    formatDateTime,
    generatePatientId
};
