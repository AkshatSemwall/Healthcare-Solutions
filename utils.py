import pandas as pd
import csv
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models import Patient, EmergencyCase

# CSV file path
CSV_FILE = 'patient_records_with_timestamp.csv'

def load_patients_from_csv() -> List[Patient]:
    """Load all patients from CSV file with proper comma delimiter handling"""
    patients = []
    
    if not os.path.exists(CSV_FILE):
        logging.warning(f"CSV file {CSV_FILE} not found. Creating empty file.")
        create_sample_csv()
        return patients
    
    try:
        # Use pandas for robust CSV reading
        df = pd.read_csv(CSV_FILE, delimiter=',')
        
        # Handle missing values
        df = df.fillna('')
        
        for _, row in df.iterrows():
            try:
                patient = Patient(
                    patient_id=str(row.get('patient_id', '')),
                    name=str(row.get('name', '')),
                    age=int(row.get('age', 0)) if pd.notna(row.get('age')) else 0,
                    gender=str(row.get('gender', '')),
                    locality=str(row.get('locality', '')),
                    condition_severity=str(row.get('condition_severity', '')),
                    priority_level=str(row.get('priority_level', '')),
                    medical_history=str(row.get('medical_history', '')),
                    bill_amount=float(row.get('bill_amount', 0)) if pd.notna(row.get('bill_amount')) else 0.0,
                    amount_paid=float(row.get('amount_paid', 0)) if pd.notna(row.get('amount_paid')) else 0.0,
                    outstanding_amount=float(row.get('outstanding_amount', 0)) if pd.notna(row.get('outstanding_amount')) else 0.0,
                    payment_status=str(row.get('payment_status', 'Unpaid')),
                    insurance_coverage=str(row.get('insurance_coverage', 'No')),
                    insurance_details=str(row.get('insurance_details', '')),
                    admission_date=str(row.get('admission_date', '')),
                    discharge_date=str(row.get('discharge_date', '')) if pd.notna(row.get('discharge_date')) and str(row.get('discharge_date', '')) != '' else None,
                    timestamp=str(row.get('timestamp', ''))
                )
                patients.append(patient)
            except Exception as e:
                logging.error(f"Error processing row: {e}")
                continue
                
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        create_sample_csv()
    
    return patients

def save_patient_to_csv(patient: Patient) -> bool:
    """Save a single patient to CSV file"""
    try:
        # Check if file exists and has data
        file_exists = os.path.exists(CSV_FILE)
        has_data = False
        
        if file_exists:
            with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                has_data = sum(1 for _ in reader) > 1  # More than just header
        
        # Write header if file is new or empty
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if not file_exists or not has_data:
                # Write header
                writer.writerow([
                    'patient_id', 'name', 'age', 'gender', 'locality',
                    'condition_severity', 'priority_level', 'medical_history',
                    'bill_amount', 'amount_paid', 'outstanding_amount',
                    'payment_status', 'insurance_coverage', 'insurance_details',
                    'admission_date', 'discharge_date', 'timestamp'
                ])
            
            # Write patient data
            writer.writerow([
                patient.patient_id, patient.name, patient.age, patient.gender,
                patient.locality, patient.condition_severity, patient.priority_level,
                patient.medical_history, patient.bill_amount, patient.amount_paid,
                patient.outstanding_amount, patient.payment_status,
                patient.insurance_coverage, patient.insurance_details,
                patient.admission_date, patient.discharge_date or '',
                patient.timestamp or datetime.now().isoformat()
            ])
        
        return True
    except Exception as e:
        logging.error(f"Error saving patient to CSV: {e}")
        return False

def generate_patient_id() -> str:
    """Generate a unique patient ID"""
    timestamp = datetime.now()
    year = timestamp.year
    # Create a unique 8-character identifier
    unique_part = f"{timestamp.month:02d}{timestamp.day:02d}{timestamp.hour:02d}{timestamp.minute:02d}"
    return f"HMS-{year}-{unique_part}"

def get_emergency_cases() -> List[EmergencyCase]:
    """Get all emergency cases (High/Critical severity with no discharge date)"""
    patients = load_patients_from_csv()
    emergency_cases = []
    
    priority_mapping = {
        'Emergency': (1, 'Emergency'),
        'Critical': (1, 'Emergency'),
        'High': (2, 'Urgent'),
        'Urgent': (2, 'Urgent'),
        'Severe': (2, 'Urgent'),
        'Moderate': (3, 'Standard'),
        'Standard': (3, 'Standard'),
        'Mild': (4, 'Routine'),
        'Routine': (4, 'Routine')
    }
    
    for patient in patients:
        if patient.is_emergency:
            priority_info = priority_mapping.get(patient.condition_severity, (4, 'Routine'))
            
            case = EmergencyCase(
                patient_id=patient.patient_id,
                name=patient.name,
                condition=patient.medical_history or f"{patient.condition_severity} condition",
                priority=patient.condition_severity,
                priority_level=priority_info[0],
                priority_name=priority_info[1],
                time_added=patient.timestamp or patient.admission_date,
                formatted_time=format_timestamp(patient.timestamp or patient.admission_date)
            )
            emergency_cases.append(case)
    
    # Sort by priority level (1 = highest priority)
    emergency_cases.sort(key=lambda x: x.priority_level)
    return emergency_cases

def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp for display"""
    if not timestamp_str:
        return "Unknown"
    
    try:
        # Try different timestamp formats
        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                return dt.strftime("%m/%d/%Y %I:%M %p")
            except ValueError:
                continue
        
        # If no format works, return as-is
        return timestamp_str
    except Exception:
        return "Unknown"

def create_sample_csv():
    """Create a sample CSV file with proper headers"""
    try:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'patient_id', 'name', 'age', 'gender', 'locality',
                'condition_severity', 'priority_level', 'medical_history',
                'bill_amount', 'amount_paid', 'outstanding_amount',
                'payment_status', 'insurance_coverage', 'insurance_details',
                'admission_date', 'discharge_date', 'timestamp'
            ])
        logging.info(f"Created new CSV file: {CSV_FILE}")
    except Exception as e:
        logging.error(f"Error creating sample CSV: {e}")

def calculate_dashboard_stats() -> Dict[str, Any]:
    """Calculate dashboard statistics from patient data"""
    patients = load_patients_from_csv()
    
    if not patients:
        return {
            'total_patients': 0,
            'emergency_cases': 0,
            'total_revenue': 0.0,
            'avg_bill': 0.0,
            'collection_rate': 0.0
        }
    
    total_patients = len(patients)
    emergency_cases = len([p for p in patients if p.is_emergency])
    total_billed = sum(p.bill_amount for p in patients)
    total_paid = sum(p.amount_paid for p in patients)
    total_revenue = total_paid
    avg_bill = total_billed / total_patients if total_patients > 0 else 0.0
    collection_rate = (total_paid / total_billed * 100) if total_billed > 0 else 0.0
    
    return {
        'total_patients': total_patients,
        'emergency_cases': emergency_cases,
        'total_revenue': total_revenue,
        'avg_bill': avg_bill,
        'collection_rate': collection_rate,
        'total_billed': total_billed,
        'total_paid': total_paid,
        'total_outstanding': total_billed - total_paid
    }

def search_patients(query: str = "", severity_filter: str = "", status_filter: str = "") -> List[Patient]:
    """Search and filter patients"""
    patients = load_patients_from_csv()
    
    if query:
        query = query.lower()
        patients = [p for p in patients if 
                   query in p.name.lower() or 
                   query in p.patient_id.lower() or
                   query in p.medical_history.lower()]
    
    if severity_filter:
        patients = [p for p in patients if p.condition_severity == severity_filter]
    
    if status_filter:
        if status_filter == "Active":
            patients = [p for p in patients if not p.discharge_date]
        elif status_filter == "Discharged":
            patients = [p for p in patients if p.discharge_date]
    
    return patients
