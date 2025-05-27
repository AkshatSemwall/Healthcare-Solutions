from flask import render_template, request, redirect, url_for, flash
from app import app
from utils import get_emergency_cases, load_patients_from_csv, save_patient_to_csv, generate_patient_id, save_emergency_case_to_csv, remove_emergency_case_from_csv, get_next_emergency_case
from models import Patient, EmergencyCase
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
        
        # If no patient ID provided, generate one
        if not patient_id:
            patient_id = generate_patient_id()
        
        # Priority level mapping
        priority_levels = {
            'Emergency': 1,
            'Urgent': 2, 
            'Standard': 3,
            'Routine': 4
        }
        
        priority_level = priority_levels.get(priority, 4)
        
        # Create emergency case
        emergency_case = EmergencyCase(
            patient_id=patient_id,
            name=name,
            condition=condition,
            priority=priority,
            priority_level=priority_level,
            priority_name=priority,
            time_added=datetime.now().isoformat(),
            formatted_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Save to emergency CSV
        if save_emergency_case_to_csv(emergency_case):
            flash(f'Emergency case for {name} added successfully to the queue.', 'success')
        else:
            flash('Error adding emergency case to the queue.', 'error')
        
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
        
        # Remove the case from emergency queue
        if remove_emergency_case_from_csv(next_case.patient_id):
            flash(f'Emergency case for {next_case.name} ({next_case.condition}) has been processed and removed from the queue.', 'success')
        else:
            flash('Error processing emergency case.', 'error')
        
        return redirect(url_for('emergency'))
        
    except Exception as e:
        logging.error(f"Error processing emergency case: {e}")
        flash('An error occurred while processing the emergency case.', 'error')
        return redirect(url_for('emergency'))
