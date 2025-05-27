document.addEventListener('DOMContentLoaded', function() {
    // Get the form element
    const registrationForm = document.getElementById('patientRegistrationForm');

    // If the form doesn't exist on this page, exit
    if (!registrationForm) return;

    // Add event listener for form submission
    registrationForm.addEventListener('submit', function(event) {
        // Clear previous validation messages
        clearValidationMessages();
        
        // Validate the form
        if (!validateForm()) {
            // Prevent form submission if validation fails
            event.preventDefault();
        }
    });

    // Add listener for changes to insurance coverage radio buttons
    const insuranceCoverageInputs = document.querySelectorAll('input[name="insurance_coverage"]');
    insuranceCoverageInputs.forEach(input => {
        input.addEventListener('change', toggleInsuranceDetails);
    });

    // Add listener for changes to bill amount and amount paid to calculate outstanding amount
    const billAmountInput = document.getElementById('bill_amount');
    const amountPaidInput = document.getElementById('amount_paid');
    const outstandingAmountInput = document.getElementById('outstanding_amount');

    if (billAmountInput && amountPaidInput && outstandingAmountInput) {
        billAmountInput.addEventListener('input', calculateOutstandingAmount);
        amountPaidInput.addEventListener('input', calculateOutstandingAmount);
    }

    // Initialize the insurance details visibility
    toggleInsuranceDetails();
});

/**
 * Toggle visibility of insurance details based on selected insurance coverage
 */
function toggleInsuranceDetails() {
    const insuranceYes = document.getElementById('insurance_coverage_yes');
    const insuranceDetailsContainer = document.getElementById('insurance_details_container');
    
    if (insuranceYes && insuranceDetailsContainer) {
        insuranceDetailsContainer.style.display = insuranceYes.checked ? 'block' : 'none';
    }
}

/**
 * Calculate outstanding amount based on bill amount and amount paid
 */
function calculateOutstandingAmount() {
    const billAmount = parseFloat(document.getElementById('bill_amount').value) || 0;
    const amountPaid = parseFloat(document.getElementById('amount_paid').value) || 0;
    const outstandingAmount = Math.max(0, billAmount - amountPaid).toFixed(2);
    
    document.getElementById('outstanding_amount').value = outstandingAmount;
    
    // Update payment status automatically
    const paymentStatusSelect = document.getElementById('payment_status');
    if (paymentStatusSelect) {
        if (billAmount === 0) {
            paymentStatusSelect.value = 'Not Applicable';
        } else if (outstandingAmount == 0) {
            paymentStatusSelect.value = 'Fully Paid';
        } else if (amountPaid > 0) {
            paymentStatusSelect.value = 'Partially Paid';
        } else {
            paymentStatusSelect.value = 'Unpaid';
        }
    }
}

/**
 * Clear all validation messages from the form
 */
function clearValidationMessages() {
    const invalidFeedbacks = document.querySelectorAll('.invalid-feedback');
    invalidFeedbacks.forEach(feedback => {
        feedback.remove();
    });
    
    const invalidInputs = document.querySelectorAll('.is-invalid');
    invalidInputs.forEach(input => {
        input.classList.remove('is-invalid');
    });
}

/**
 * Validate the entire form and show validation messages
 * @returns {boolean} True if form is valid, false otherwise
 */
function validateForm() {
    let isValid = true;
    
    // Validate required fields
    const requiredFields = [
        { id: 'name', message: 'Patient name is required' },
        { id: 'age', message: 'Age is required' },
        { id: 'gender', message: 'Gender is required' },
        { id: 'condition_severity', message: 'Condition severity is required' },
        { id: 'bill_amount', message: 'Bill amount is required' }
    ];
    
    requiredFields.forEach(field => {
        const input = document.getElementById(field.id);
        if (!input.value.trim()) {
            showValidationError(input, field.message);
            isValid = false;
        }
    });
    
    // Validate age (must be a positive integer between 1-120)
    const ageInput = document.getElementById('age');
    if (ageInput.value.trim()) {
        const age = parseInt(ageInput.value);
        if (isNaN(age) || age <= 0 || age > 120) {
            showValidationError(ageInput, 'Age must be a number between 1 and 120');
            isValid = false;
        }
    }
    
    // Validate monetary values
    const moneyFields = [
        { id: 'bill_amount', message: 'Bill amount must be a positive number' },
        { id: 'amount_paid', message: 'Amount paid must be a positive number' },
        { id: 'outstanding_amount', message: 'Outstanding amount must be a positive number' }
    ];
    
    moneyFields.forEach(field => {
        const input = document.getElementById(field.id);
        if (input.value.trim()) {
            const amount = parseFloat(input.value);
            if (isNaN(amount) || amount < 0) {
                showValidationError(input, field.message);
                isValid = false;
            }
        }
    });
    
    // Validate amount paid is not greater than bill amount
    const billAmount = parseFloat(document.getElementById('bill_amount').value) || 0;
    const amountPaid = parseFloat(document.getElementById('amount_paid').value) || 0;
    
    if (amountPaid > billAmount) {
        showValidationError(document.getElementById('amount_paid'), 'Amount paid cannot exceed the bill amount');
        isValid = false;
    }
    
    // If insurance coverage is Yes, validate insurance details
    const insuranceYes = document.getElementById('insurance_coverage_yes');
    const insuranceDetails = document.getElementById('insurance_details');
    
    if (insuranceYes && insuranceYes.checked && (!insuranceDetails.value.trim())) {
        showValidationError(insuranceDetails, 'Insurance details are required when insurance coverage is selected');
        isValid = false;
    }
    
    return isValid;
}

/**
 * Show validation error message for an input
 * @param {HTMLElement} input - The input element
 * @param {string} message - The error message
 */
function showValidationError(input, message) {
    input.classList.add('is-invalid');
    
    // Create error message element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    // Add error message after the input
    input.parentNode.appendChild(errorDiv);
}
