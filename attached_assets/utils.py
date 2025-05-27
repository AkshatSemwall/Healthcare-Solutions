import os
import csv
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_patient_id():
    """Generate a unique patient ID."""
    # Create a UUID and use part of it for the patient ID
    # Format: HMS-{current_year}-{UUID first 8 characters}
    current_year = datetime.now().year
    unique_id = str(uuid.uuid4()).split('-')[0]
    patient_id = f"HMS-{current_year}-{unique_id}"
    logger.debug(f"Generated patient ID: {patient_id}")
    return patient_id

def save_to_csv(patient_data):
    """
    Save patient data to a CSV file.
    
    Args:
        patient_data (dict): Dictionary containing patient information
    
    Returns:
        bool: True if saving was successful
    """
    # Define CSV file path
    csv_file = os.path.join('data', 'patients.csv')
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), csv_file)
    
    # Define the column order for the CSV file
    field_names = [
        'patient_id', 'name', 'age', 'gender', 'admission_date', 'admission_time',
        'condition_severity', 'medical_history', 'bill_amount', 'priority_level',
        'locality', 'insurance_coverage', 'insurance_details', 'amount_paid',
        'outstanding_amount', 'payment_status'
    ]
    
    file_exists = os.path.isfile(csv_path)
    
    try:
        with open(csv_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=field_names, delimiter='\t')
            
            # Write header if file doesn't exist
            if not file_exists:
                writer.writeheader()
                logger.info(f"Created new CSV file at {csv_path}")
            
            # Filter the data to only include fields defined in field_names
            filtered_data = {k: patient_data.get(k, '') for k in field_names}
            writer.writerow(filtered_data)
            logger.info(f"Added patient record to CSV for ID: {patient_data['patient_id']}")
        
        return True
    except Exception as e:
        logger.error(f"Error saving to CSV: {str(e)}")
        raise

def validate_form_data(form_data):
    """
    Validate the form data.
    
    Args:
        form_data (dict): Dictionary containing form data
    
    Returns:
        list: List of error messages, empty if no errors
    """
    errors = []
    
    # Check required fields
    required_fields = ['name', 'age', 'gender', 'condition_severity', 'bill_amount']
    for field in required_fields:
        if not form_data.get(field):
            errors.append(f"{field.replace('_', ' ').title()} is required")
    
    # Validate age (must be a positive integer)
    if form_data.get('age'):
        try:
            age = int(form_data['age'])
            if age <= 0 or age > 120:
                errors.append("Age must be a positive number between 1 and 120")
        except ValueError:
            errors.append("Age must be a number")
    
    # Validate monetary values
    money_fields = ['bill_amount', 'amount_paid', 'outstanding_amount']
    for field in money_fields:
        if form_data.get(field):
            try:
                amount = float(form_data[field])
                if amount < 0:
                    errors.append(f"{field.replace('_', ' ').title()} cannot be negative")
            except ValueError:
                errors.append(f"{field.replace('_', ' ').title()} must be a valid monetary value")
    
    # If insurance_coverage is "Yes", insurance_details should be provided
    if form_data.get('insurance_coverage') == 'Yes' and not form_data.get('insurance_details'):
        errors.append("Insurance details are required when insurance coverage is selected")
    
    logger.debug(f"Form validation completed with {len(errors)} errors")
    return errors


def read_patients_from_csv(csv_path=None):
    """
    Read all patient records from the CSV file.
    
    Args:
        csv_path (str, optional): Path to CSV file. If not provided, uses default path.
    
    Returns:
        list: List of dictionaries containing patient data
    """
    if csv_path is None:
        csv_file = os.path.join('data', 'patients.csv')
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), csv_file)
    
    patients = []
    
    # Check if the specific file exists, if not, try using the attached assets file
    if not os.path.isfile(csv_path):
        alternative_path = os.path.join('attached_assets', 'patient_records_with_timestamp.csv')
        if os.path.isfile(alternative_path):
            csv_path = alternative_path
            logger.info(f"Using patient data from: {csv_path}")
        else:
            logger.warning(f"Patient CSV file not found at {csv_path} or in attached_assets")
            return patients
    
    try:
        with open(csv_path, mode='r', newline='') as file:
            # Determine the delimiter by examining the first line
            first_line = file.readline().strip()
            file.seek(0)  # Reset file pointer to beginning
            
            delimiter = '\t' if '\t' in first_line else ','
            
            reader = csv.DictReader(file, delimiter=delimiter)
            for row in reader:
                # Create a standardized dictionary from the CSV row
                patient = dict(row)
                
                # Perform field name standardization if needed (to handle differences between CSV formats)
                field_mappings = {
                    'PatientID': 'patient_id',
                    'Name': 'name',
                    'Age': 'age',
                    'Gender': 'gender',
                    'ConditionSeverity': 'condition_severity',
                    'AdmissionDate': 'admission_date',
                    'DischargeDate': 'discharge_date',
                    'AdmissionTimestamp': 'admission_timestamp',
                    'MedicalHistory': 'medical_history', 
                    'BillAmount': 'bill_amount',
                    'PriorityLevel': 'priority_level',
                    'Locality': 'locality',
                    'InsuranceCoverage': 'insurance_coverage',
                    'InsuranceCoverageDetail': 'insurance_details',
                    'AmountPaid': 'amount_paid',
                    'OutstandingAmount': 'outstanding_amount',
                    'PaymentStatus': 'payment_status'
                }
                
                standardized_patient = {}
                for orig_key, value in patient.items():
                    # Use the mapped field name if it exists, otherwise keep the original
                    new_key = field_mappings.get(orig_key, orig_key.lower())
                    standardized_patient[new_key] = value
                
                patients.append(standardized_patient)
        
        logger.info(f"Successfully read {len(patients)} patient records from CSV")
        return patients
    except Exception as e:
        logger.error(f"Error reading patients from CSV: {str(e)}")
        return patients
