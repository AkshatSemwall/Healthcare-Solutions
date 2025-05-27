import os
import logging
import json
import csv
import io
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, jsonify, Response, make_response
from app import app
from utils import generate_patient_id, save_to_csv, validate_form_data, read_patients_from_csv
from emergency_handler import emergency_handler
from billing import billing_system
from reports_simplified import report_generator
from ml_insights import ml_insights

# Optional: try to import reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Route for the main page that displays the patient registration form."""
    logger.debug("Rendering index page")
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    """Handle the patient registration form submission."""
    logger.debug("Processing registration form")
    
    # Extract form data
    form_data = {
        'name': request.form.get('name', ''),
        'age': request.form.get('age', ''),
        'gender': request.form.get('gender', ''),
        'condition_severity': request.form.get('condition_severity', ''),
        'medical_history': request.form.get('medical_history', ''),
        'bill_amount': request.form.get('bill_amount', ''),
        'priority_level': request.form.get('priority_level', ''),
        'locality': request.form.get('locality', ''),
        'insurance_coverage': request.form.get('insurance_coverage', 'No'),
        'insurance_details': request.form.get('insurance_details', ''),
        'amount_paid': request.form.get('amount_paid', ''),
        'outstanding_amount': request.form.get('outstanding_amount', ''),
        'payment_status': request.form.get('payment_status', '')
    }
    
    # Validate form data
    errors = validate_form_data(form_data)
    if errors:
        for error in errors:
            flash(error, 'danger')
        logger.warning(f"Form validation failed: {errors}")
        return render_template('register.html', form_data=form_data)
    
    # Generate patient ID and timestamps
    patient_id = generate_patient_id()
    admission_date = datetime.now().strftime('%Y-%m-%d')
    admission_time = datetime.now().strftime('%H:%M:%S')
    
    # Add additional fields to form data
    form_data['patient_id'] = patient_id
    form_data['admission_date'] = admission_date
    form_data['admission_time'] = admission_time
    
    try:
        # Save to CSV
        save_to_csv(form_data)
        logger.info(f"Successfully registered patient: {patient_id}")
        
        # Store patient info in session for the success page
        session['patient_id'] = patient_id
        session['patient_name'] = form_data['name']
        
        return redirect(url_for('registration_success'))
    except Exception as e:
        logger.error(f"Error saving patient data: {str(e)}")
        flash(f"An error occurred while registering the patient: {str(e)}", 'danger')
        return render_template('error.html', error=str(e)), 500

@app.route('/success')
def registration_success():
    """Display the registration success page."""
    patient_id = session.get('patient_id')
    patient_name = session.get('patient_name')
    
    if not patient_id or not patient_name:
        logger.warning("Accessed success page without valid patient information")
        return redirect(url_for('index'))
    
    logger.debug(f"Displaying success page for patient: {patient_id}")
    return render_template('success.html', patient_id=patient_id, patient_name=patient_name)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    logger.warning(f"404 error: {request.path}")
    return render_template('error.html', error="Page not found"), 404

@app.route('/emergency')
def emergency_queue():
    """Display the emergency queue management page."""
    logger.debug("Rendering emergency queue page")
    
    # Get all emergency cases
    cases = emergency_handler.get_all_cases()
    
    # Get the next case to process
    next_case = emergency_handler.get_next_case() if emergency_handler.get_queue_size() > 0 else None
    if next_case is not None:
        # Put it back in the queue since we're just viewing it
        emergency_handler.add_case(
            next_case['patient_id'],
            next_case['name'],
            next_case['priority_name'],
            next_case['condition']
        )
    
    return render_template('emergency.html', cases=cases, next_case=next_case)

@app.route('/emergency/add', methods=['POST'])
def add_emergency():
    """Handle adding a new emergency case to the queue."""
    logger.debug("Processing emergency case addition")
    
    # Extract form data
    patient_id = request.form.get('patient_id', '')
    name = request.form.get('name', '')
    priority = request.form.get('priority', '')
    condition = request.form.get('condition', '')
    
    # Validate required data
    if not all([patient_id, name, priority, condition]):
        flash("All fields are required for emergency cases", 'danger')
        return redirect(url_for('emergency_queue'))
    
    # Add the emergency case
    success = emergency_handler.add_case(patient_id, name, priority, condition)
    
    if success:
        flash(f"Emergency case for {name} added successfully with {priority} priority", 'success')
    else:
        flash("Failed to add emergency case", 'danger')
    
    return redirect(url_for('emergency_queue'))

@app.route('/emergency/process', methods=['POST'])
def process_next_emergency():
    """Process the next emergency case in the queue."""
    logger.debug("Processing next emergency case")
    
    # Get the next case to process
    next_case = emergency_handler.get_next_case()
    
    if next_case:
        flash(f"Processing emergency case for {next_case['name']} with {next_case['priority_name']} priority", 'success')
    else:
        flash("No emergency cases in the queue", 'info')
    
    return redirect(url_for('emergency_queue'))

@app.route('/patients/search', methods=['GET'])
def search_patients():
    """API endpoint to search for patients by ID or name."""
    search_term = request.args.get('term', '')
    
    if not search_term or len(search_term) < 3:
        return jsonify([])
    
    # Read all patients from CSV
    patients = read_patients_from_csv()
    
    # Filter patients by ID or name
    results = []
    for patient in patients:
        if (search_term.lower() in patient.get('patient_id', '').lower() or 
            search_term.lower() in patient.get('name', '').lower()):
            results.append({
                'id': patient.get('patient_id', ''),
                'name': patient.get('name', ''),
                'age': patient.get('age', ''),
                'gender': patient.get('gender', '')
            })
    
    return jsonify(results[:10])  # Limit to 10 results

@app.route('/billing')
def billing_dashboard():
    """Display the billing dashboard."""
    logger.debug("Rendering billing dashboard")
    
    billing_data = billing_system.get_all_billing_data()
    summary = billing_system.get_billing_summary()
    
    return render_template('billing.html', billing_data=billing_data, summary=summary)

@app.route('/billing/update', methods=['POST'])
def update_payment():
    """Handle updating a patient's payment information."""
    logger.debug("Processing payment update")
    
    patient_id = request.form.get('patient_id', '')
    amount_paid = request.form.get('amount_paid', '0')
    payment_status = request.form.get('payment_status', '')
    
    if not patient_id:
        flash("Patient ID is required", 'danger')
        return redirect(url_for('billing_dashboard'))
    
    try:
        amount_paid_float = float(amount_paid)
        if amount_paid_float < 0:
            flash("Amount paid cannot be negative", 'danger')
            return redirect(url_for('billing_dashboard'))
            
        success = billing_system.update_payment(patient_id, amount_paid_float, payment_status)
        
        if success:
            flash(f"Payment information updated successfully for patient {patient_id}", 'success')
        else:
            flash("Failed to update payment information", 'danger')
    except ValueError:
        flash("Amount paid must be a valid number", 'danger')
    
    return redirect(url_for('billing_dashboard'))

@app.route('/billing/report/<type>')
def generate_report(type):
    """Generate and display a financial report."""
    logger.debug(f"Generating {type} financial report")
    
    if type not in ['daily', 'monthly']:
        type = 'daily'
    
    report = billing_system.generate_financial_report(type)
    
    return render_template('financial_report.html', report=report, report_type=type)

@app.route('/billing/report/<type>/download')
def download_report_csv(type):
    """Download financial report as CSV."""
    logger.debug(f"Downloading {type} financial report as CSV")
    
    if type not in ['daily', 'monthly']:
        type = 'daily'
    
    report = billing_system.generate_financial_report(type)
    
    # Create a CSV string
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Patient ID', 'Name', 'Admission Date', 'Bill Amount', 
                     'Amount Paid', 'Outstanding Amount', 'Payment Status', 'Insurance'])
    
    # Write data rows
    for bill in report['data']:
        writer.writerow([
            bill['patient_id'],
            bill['name'],
            bill['admission_date'],
            bill['bill_amount'],
            bill['amount_paid'],
            bill['outstanding_amount'],
            bill['payment_status'],
            bill['insurance_coverage']
        ])
    
    # Create response
    current_date = datetime.now().strftime('%Y%m%d')
    filename = f"{type}_financial_report_{current_date}.csv"
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

@app.route('/reports')
def reports_dashboard():
    """Display the reports dashboard."""
    logger.debug("Rendering reports dashboard")
    
    # Generate daily report data
    report = report_generator.generate_daily_report()
    
    # Get historical data for trend charts
    historical_data = report_generator.get_historical_data(days=30)
    
    return render_template('reports_dashboard.html', report=report, historical_data=historical_data)

@app.route('/reports/pdf')
def download_report_pdf():
    """Generate and download a PDF report."""
    logger.debug("Generating PDF report")
    
    # This is a simplified version without actual PDF generation
    flash("PDF generation is coming soon", 'info')
    return redirect(url_for('reports_dashboard'))

@app.route('/reports/data_csv')
def download_report_data_csv():
    """Download report data as CSV."""
    logger.debug("Downloading report data as CSV")
    
    # Get report data
    report = report_generator.generate_daily_report()
    
    # Create CSV string
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write basic stats
    writer.writerow(['Report Title', report['title']])
    writer.writerow(['Generated At', report['generated_at']])
    writer.writerow([])
    
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Patients', report['total_patients']])
    writer.writerow(['Emergency Cases', report['total_emergency_cases']])
    writer.writerow(['Average Bill', f"${report['avg_bill']:.2f}"])
    writer.writerow(['Total Revenue', f"${report['total_revenue']:.2f}"])
    writer.writerow([])
    
    # Write age distribution
    writer.writerow(['Age Distribution'])
    writer.writerow(['Age Group', 'Count'])
    for age_group, count in report['age_distribution'].items():
        writer.writerow([age_group, count])
    writer.writerow([])
    
    # Write condition distribution
    writer.writerow(['Condition Severity'])
    writer.writerow(['Severity', 'Count'])
    for severity, count in report['condition_distribution'].items():
        writer.writerow([severity, count])
    writer.writerow([])
    
    # Write ML predictions
    writer.writerow(['ML Predictions'])
    writer.writerow(['Next Day Visits', report['ml_predictions']['next_day_visits']])
    writer.writerow([])
    
    writer.writerow(['Trending Diseases'])
    writer.writerow(['Disease', 'Cases', 'Trend'])
    for disease in report['ml_predictions']['trending_diseases']:
        writer.writerow([disease['name'], disease['cases'], disease['trend']])
    
    # Create response
    response = Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=hospital_report_{report['date']}.csv"}
    )
    
    return response

@app.route('/ml-insights')
def ml_insights_dashboard():
    """Display the ML insights dashboard."""
    logger.debug("Rendering ML insights dashboard")
    
    # Get ML predictions and insights
    insights = ml_insights.get_predictions()
    
    return render_template('ml_insights.html', insights=insights)

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    logger.error(f"500 error: {str(e)}")
    return render_template('error.html', error="Internal server error"), 500



@app.route('/home')
def home():
    """Render the home page with all dashboard data"""
    # [Keep all your existing dummy data generation code from original index()]
    return render_template('home.html')
