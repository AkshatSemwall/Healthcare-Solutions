from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app
from utils import (
    load_patients_from_csv, save_patient_to_csv, generate_patient_id,
    calculate_dashboard_stats, search_patients
)
from models import Patient
from datetime import datetime
import logging

@app.route('/')
def index():
    """Dashboard page"""
    try:
        stats = calculate_dashboard_stats()
        patients = load_patients_from_csv()
        
        # Get recent patients (last 10)
        recent_patients = patients[-10:] if patients else []
        
        return render_template('index.html', 
                             stats=stats, 
                             recent_patients=recent_patients)
    except Exception as e:
        logging.error(f"Error loading dashboard: {e}")
        return render_template('error.html', error="Error loading dashboard data")

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Patient registration"""
    if request.method == 'POST':
        try:
            # Extract form data
            name = request.form.get('name', '').strip()
            age = int(request.form.get('age', 0))
            gender = request.form.get('gender', '')
            locality = request.form.get('locality', '').strip()
            condition_severity = request.form.get('condition_severity', '')
            priority_level = request.form.get('priority_level', '')
            medical_history = request.form.get('medical_history', '').strip()
            bill_amount = float(request.form.get('bill_amount', 0))
            amount_paid = float(request.form.get('amount_paid', 0))
            payment_status = request.form.get('payment_status', 'Unpaid')
            insurance_coverage = request.form.get('insurance_coverage', 'No')
            insurance_details = request.form.get('insurance_details', '').strip()
            
            # Validate required fields
            if not all([name, age, gender, condition_severity, bill_amount]):
                flash('Please fill in all required fields.', 'error')
                return render_template('register.html', form_data=request.form)
            
            # Generate patient ID and calculate outstanding amount
            patient_id = generate_patient_id()
            outstanding_amount = bill_amount - amount_paid
            
            # Update payment status based on amounts
            if amount_paid >= bill_amount:
                payment_status = 'Fully Paid'
                outstanding_amount = 0
            elif amount_paid > 0:
                payment_status = 'Partially Paid'
            else:
                payment_status = 'Unpaid'
            
            # Create patient object
            patient = Patient(
                patient_id=patient_id,
                name=name,
                age=age,
                gender=gender,
                locality=locality,
                condition_severity=condition_severity,
                priority_level=priority_level,
                medical_history=medical_history,
                bill_amount=bill_amount,
                amount_paid=amount_paid,
                outstanding_amount=outstanding_amount,
                payment_status=payment_status,
                insurance_coverage=insurance_coverage,
                insurance_details=insurance_details,
                admission_date=datetime.now().strftime('%Y-%m-%d'),
                discharge_date=None,
                timestamp=datetime.now().isoformat()
            )
            
            # Save to CSV
            if save_patient_to_csv(patient):
                return render_template('success.html', 
                                     patient_name=name, 
                                     patient_id=patient_id)
            else:
                flash('Error saving patient data. Please try again.', 'error')
                return render_template('register.html', form_data=request.form)
                
        except ValueError as e:
            flash('Please enter valid numeric values for age and bill amounts.', 'error')
            return render_template('register.html', form_data=request.form)
        except Exception as e:
            logging.error(f"Error registering patient: {e}")
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('register.html', form_data=request.form)
    
    return render_template('register.html')

@app.route('/patients')
def patients():
    """Patient listing with search and filter"""
    try:
        query = request.args.get('search', '')
        severity_filter = request.args.get('severity', '')
        status_filter = request.args.get('status', '')
        sort_by = request.args.get('sort', 'name')
        sort_order = request.args.get('order', 'asc')
        
        patients = search_patients(query, severity_filter, status_filter)
        
        # Sort patients based on sort_by parameter
        if patients:
            reverse_order = sort_order == 'desc'
            
            if sort_by == 'name':
                patients.sort(key=lambda p: p.name.lower(), reverse=reverse_order)
            elif sort_by == 'patient_id':
                patients.sort(key=lambda p: p.patient_id, reverse=reverse_order)
            elif sort_by == 'age':
                patients.sort(key=lambda p: p.age, reverse=reverse_order)
            elif sort_by == 'admission_date':
                patients.sort(key=lambda p: p.admission_date, reverse=reverse_order)
            elif sort_by == 'condition_severity':
                # Custom sort for severity levels (Critical > High > Moderate > Mild)
                severity_priority = {'Critical': 4, 'High': 3, 'Moderate': 2, 'Mild': 1}
                patients.sort(key=lambda p: severity_priority.get(p.condition_severity, 0), reverse=reverse_order)
            elif sort_by == 'outstanding_amount':
                patients.sort(key=lambda p: p.outstanding_amount, reverse=reverse_order)
            elif sort_by == 'locality':
                patients.sort(key=lambda p: p.locality.lower() if p.locality else '', reverse=reverse_order)
        
        # Get unique severity levels for filter dropdown
        all_patients = load_patients_from_csv()
        severity_levels = list(set(p.condition_severity for p in all_patients if p.condition_severity))
        
        return render_template('patients.html', 
                             patients=patients, 
                             severity_levels=severity_levels,
                             current_search=query,
                             current_severity=severity_filter,
                             current_status=status_filter,
                             current_sort=sort_by,
                             current_order=sort_order)
    except Exception as e:
        logging.error(f"Error loading patients: {e}")
        return render_template('error.html', error="Error loading patient data")

@app.route('/patient/<patient_id>')
def patient_detail(patient_id):
    """Patient detail view"""
    try:
        patients = load_patients_from_csv()
        patient = next((p for p in patients if p.patient_id == patient_id), None)
        
        if not patient:
            return render_template('error.html', error="Patient not found")
        
        return render_template('patient_detail.html', patient=patient)
    except Exception as e:
        logging.error(f"Error loading patient detail: {e}")
        return render_template('error.html', error="Error loading patient data")

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500
