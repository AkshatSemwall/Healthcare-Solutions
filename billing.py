from flask import render_template, request, redirect, url_for, flash, make_response
from app import app
from utils import load_patients_from_csv, calculate_dashboard_stats
from models import ReportData
from datetime import datetime
import csv
import io
import logging

@app.route('/billing_dashboard')
def billing_dashboard():
    """Billing dashboard with financial overview"""
    try:
        patients = load_patients_from_csv()
        stats = calculate_dashboard_stats()
        
        # Calculate additional billing metrics
        unpaid_patients = [p for p in patients if p.payment_status == 'Unpaid']
        partially_paid_patients = [p for p in patients if p.payment_status == 'Partially Paid']
        fully_paid_patients = [p for p in patients if p.payment_status == 'Fully Paid']
        
        billing_stats = {
            **stats,
            'unpaid_count': len(unpaid_patients),
            'partially_paid_count': len(partially_paid_patients),
            'fully_paid_count': len(fully_paid_patients),
            'unpaid_amount': sum(p.outstanding_amount for p in unpaid_patients),
            'overdue_amount': sum(p.outstanding_amount for p in patients if p.outstanding_amount > 0)
        }
        
        return render_template('billing_dashboard.html', 
                             stats=billing_stats,
                             patients=patients[:20])  # Show recent 20 for performance
    except Exception as e:
        logging.error(f"Error loading billing dashboard: {e}")
        return render_template('error.html', error="Error loading billing data")

@app.route('/financial_report')
def financial_report():
    """Generate financial report"""
    try:
        patients = load_patients_from_csv()
        stats = calculate_dashboard_stats()
        
        # Create report data
        report = ReportData(
            title="Hospital Financial Report",
            generated_at=datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            total_patients=stats['total_patients'],
            total_billed=stats['total_billed'],
            total_paid=stats['total_paid'],
            total_outstanding=stats['total_outstanding'],
            collection_rate=stats['collection_rate'],
            data=patients
        )
        
        return render_template('financial_report.html', report=report)
    except Exception as e:
        logging.error(f"Error generating financial report: {e}")
        return render_template('error.html', error="Error generating financial report")

@app.route('/download_report_data_csv')
def download_report_data_csv():
    """Download billing data as CSV"""
    try:
        patients = load_patients_from_csv()
        
        # Create CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Patient ID', 'Name', 'Admission Date', 'Bill Amount',
            'Amount Paid', 'Outstanding Amount', 'Payment Status', 'Insurance Coverage'
        ])
        
        # Write data
        for patient in patients:
            writer.writerow([
                patient.patient_id,
                patient.name,
                patient.admission_date,
                f"{patient.bill_amount:.2f}",
                f"{patient.amount_paid:.2f}",
                f"{patient.outstanding_amount:.2f}",
                patient.payment_status,
                patient.insurance_coverage
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=billing_report_{datetime.now().strftime("%Y%m%d")}.csv'
        
        return response
    except Exception as e:
        logging.error(f"Error downloading CSV: {e}")
        return render_template('error.html', error="Error generating CSV download")

@app.route('/download_report_pdf')
def download_report_pdf():
    """Download report as PDF - placeholder for future implementation"""
    flash('PDF download feature will be implemented in a future update.', 'info')
    return redirect(url_for('financial_report'))

@app.route('/update_payment/<patient_id>', methods=['POST'])
def update_payment(patient_id):
    """Update patient payment information"""
    try:
        patients = load_patients_from_csv()
        patient = next((p for p in patients if p.patient_id == patient_id), None)
        
        if not patient:
            flash('Patient not found.', 'error')
            return redirect(url_for('billing_dashboard'))
        
        # Get payment amount from form
        payment_amount = float(request.form.get('payment_amount', 0))
        
        if payment_amount <= 0:
            flash('Please enter a valid payment amount.', 'error')
            return redirect(url_for('billing_dashboard'))
        
        # Update payment information
        patient.amount_paid += payment_amount
        patient.outstanding_amount = patient.bill_amount - patient.amount_paid
        
        # Update payment status
        if patient.outstanding_amount <= 0:
            patient.payment_status = 'Fully Paid'
            patient.outstanding_amount = 0
        elif patient.amount_paid > 0:
            patient.payment_status = 'Partially Paid'
        else:
            patient.payment_status = 'Unpaid'
        
        # Save updated data (recreate CSV for simplicity)
        import os
        with open('patient_records_with_timestamp.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'patient_id', 'name', 'age', 'gender', 'locality',
                'condition_severity', 'priority_level', 'medical_history',
                'bill_amount', 'amount_paid', 'outstanding_amount',
                'payment_status', 'insurance_coverage', 'insurance_details',
                'admission_date', 'discharge_date', 'timestamp'
            ])
            
            for p in patients:
                writer.writerow([
                    p.patient_id, p.name, p.age, p.gender,
                    p.locality, p.condition_severity, p.priority_level,
                    p.medical_history, p.bill_amount, p.amount_paid,
                    p.outstanding_amount, p.payment_status,
                    p.insurance_coverage, p.insurance_details,
                    p.admission_date, p.discharge_date or '',
                    p.timestamp or datetime.now().isoformat()
                ])
        
        flash(f'Payment of ₹{payment_amount:.2f} recorded successfully.', 'success')
        return redirect(url_for('billing_dashboard'))
        
    except ValueError:
        flash('Please enter a valid payment amount.', 'error')
        return redirect(url_for('billing_dashboard'))
    except Exception as e:
        logging.error(f"Error updating payment: {e}")
        flash('Error updating payment. Please try again.', 'error')
        return redirect(url_for('billing_dashboard'))
