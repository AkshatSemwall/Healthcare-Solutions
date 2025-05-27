from flask import render_template, request, redirect, url_for, flash
from app import app
from utils import get_emergency_cases, load_patients_from_csv, save_patient_to_csv, generate_patient_id
from models import Patient
from datetime import datetime
import logging

@app.route('/emergency')
def emergency():
    """Emergency queue management page"""
    try:
        cases = get_emergency_cases()
        next_case = cases[0] if cases else None
        
        return render_template('emergency.html', 
                             cases=cases, 
                             next_case=next_case)
    except Exception as e:
        logging.error(f"Error loading emergency cases: {e}")
        return render_template('error.html', error="Error loading emergency data")

@app.route('/add_emergency', methods=['POST'])
def add_emergency():
    """Add new emergency case"""
    try:
        # Extract form data
        patient_id = request.form.get('patient_id', '').strip()
        name = request.form.get('name', '').strip()
        priority = request.form.get('priority', '')
        condition = request.form.get('condition', '').strip()
        
        # Validate required fields
        if not all([patient_id, name, priority, condition]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('emergency'))
        
        # Validate patient ID format
        if not patient_id.startswith('HMS-'):
            flash('Invalid Patient ID format. Use HMS-YYYY-XXXXXXXX format.', 'error')
            return redirect(url_for('emergency'))
        
        # Check if patient already exists
        patients = load_patients_from_csv()
        existing_patient = next((p for p in patients if p.patient_id == patient_id), None)
        
        if existing_patient:
            # Update existing patient for emergency
            existing_patient.condition_severity = priority
            existing_patient.medical_history = condition
            existing_patient.discharge_date = None  # Mark as not discharged
            existing_patient.timestamp = datetime.now().isoformat()
            
            # Re-save all patients (simple approach for CSV)
            # In production, this would be more efficient with database updates
            flash('Patient updated and added to emergency queue.', 'success')
        else:
            # Create new emergency patient
            patient = Patient(
                patient_id=patient_id,
                name=name,
                age=0,  # Will be updated later
                gender='',
                locality='',
                condition_severity=priority,
                priority_level=priority,
                medical_history=condition,
                bill_amount=0.0,
                amount_paid=0.0,
                outstanding_amount=0.0,
                payment_status='Unpaid',
                insurance_coverage='No',
                insurance_details='',
                admission_date=datetime.now().strftime('%Y-%m-%d'),
                discharge_date=None,
                timestamp=datetime.now().isoformat()
            )
            
            if save_patient_to_csv(patient):
                flash('Emergency case added successfully.', 'success')
            else:
                flash('Error adding emergency case.', 'error')
        
        return redirect(url_for('emergency'))
        
    except Exception as e:
        logging.error(f"Error adding emergency case: {e}")
        flash('An error occurred while adding the emergency case.', 'error')
        return redirect(url_for('emergency'))

@app.route('/process_next_emergency', methods=['POST'])
def process_next_emergency():
    """Process the next emergency case"""
    try:
        cases = get_emergency_cases()
        
        if not cases:
            flash('No emergency cases to process.', 'info')
            return redirect(url_for('emergency'))
        
        # Get the highest priority case
        next_case = cases[0]
        
        # Load all patients and find the one to update
        patients = load_patients_from_csv()
        patient_to_update = next((p for p in patients if p.patient_id == next_case.patient_id), None)
        
        if patient_to_update:
            # Mark as discharged (processed)
            patient_to_update.discharge_date = datetime.now().strftime('%Y-%m-%d')
            
            # For simplicity, we'll recreate the CSV file
            # In production, use a database for better performance
            import os
            import csv
            
            # Backup and rewrite CSV
            with open('patient_records_with_timestamp.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'patient_id', 'name', 'age', 'gender', 'locality',
                    'condition_severity', 'priority_level', 'medical_history',
                    'bill_amount', 'amount_paid', 'outstanding_amount',
                    'payment_status', 'insurance_coverage', 'insurance_details',
                    'admission_date', 'discharge_date', 'timestamp'
                ])
                
                for patient in patients:
                    writer.writerow([
                        patient.patient_id, patient.name, patient.age, patient.gender,
                        patient.locality, patient.condition_severity, patient.priority_level,
                        patient.medical_history, patient.bill_amount, patient.amount_paid,
                        patient.outstanding_amount, patient.payment_status,
                        patient.insurance_coverage, patient.insurance_details,
                        patient.admission_date, patient.discharge_date or '',
                        patient.timestamp or datetime.now().isoformat()
                    ])
            
            flash(f'Emergency case for {next_case.name} has been processed.', 'success')
        else:
            flash('Error finding patient to process.', 'error')
        
        return redirect(url_for('emergency'))
        
    except Exception as e:
        logging.error(f"Error processing emergency case: {e}")
        flash('An error occurred while processing the emergency case.', 'error')
        return redirect(url_for('emergency'))
