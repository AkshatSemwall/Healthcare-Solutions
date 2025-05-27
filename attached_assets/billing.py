"""
Billing Module - Manage patient billing information
"""

import os
import csv
import logging
from datetime import datetime
from utils import read_patients_from_csv

logger = logging.getLogger(__name__)

# Path to the real patient data CSV file
PATIENT_DATA_PATH = os.path.join('attached_assets', 'patient_records_with_timestamp.csv')

class BillingSystem:
    """Class to handle billing operations and reporting"""
    
    @staticmethod
    def get_all_billing_data():
        """
        Get billing data for all patients
        
        Returns:
            list: List of dictionaries containing patient billing information
        """
        patients = read_patients_from_csv(PATIENT_DATA_PATH)
        
        billing_data = []
        for patient in patients:
            try:
                # Get patient ID - handle possible key variations
                patient_id = patient.get('patient_id', patient.get('PatientID', ''))
                
                # Parse billing amounts safely
                bill_amount_str = patient.get('bill_amount', patient.get('BillAmount', '0'))
                amount_paid_str = patient.get('amount_paid', patient.get('AmountPaid', '0'))
                outstanding_amount_str = patient.get('outstanding_amount', patient.get('OutstandingAmount', '0'))
                
                try:
                    bill_amount = float(bill_amount_str) if bill_amount_str else 0
                except ValueError:
                    bill_amount = 0
                
                try:
                    amount_paid = float(amount_paid_str) if amount_paid_str else 0
                except ValueError:
                    amount_paid = 0
                
                try:
                    outstanding_amount = float(outstanding_amount_str) if outstanding_amount_str else 0
                except ValueError:
                    outstanding_amount = 0
                
                payment_status = patient.get('payment_status', patient.get('PaymentStatus', 'Unknown'))
                
                billing_info = {
                    'patient_id': patient_id,
                    'name': patient.get('name', patient.get('Name', '')),
                    'admission_date': patient.get('admission_date', patient.get('AdmissionDate', '')),
                    'discharge_date': patient.get('discharge_date', patient.get('DischargeDate', '')),
                    'bill_amount': bill_amount,
                    'amount_paid': amount_paid,
                    'outstanding_amount': outstanding_amount,
                    'payment_status': payment_status,
                    'insurance_coverage': patient.get('insurance_coverage', patient.get('InsuranceCoverage', 'No')),
                    'insurance_details': patient.get('insurance_details', patient.get('InsuranceCoverageDetail', ''))
                }
                
                # Calculate outstanding_amount if zero but bill_amount exists
                if billing_info['outstanding_amount'] == 0 and billing_info['bill_amount'] > 0:
                    billing_info['outstanding_amount'] = billing_info['bill_amount'] - billing_info['amount_paid']
                
                billing_data.append(billing_info)
            except Exception as e:
                logger.error(f"Error processing billing data for patient {patient.get('PatientID', 'unknown')}: {str(e)}")
        
        logger.info(f"Retrieved billing data for {len(billing_data)} patients")
        return billing_data
    
    @staticmethod
    def get_billing_summary():
        """
        Get a summary of billing information
        
        Returns:
            dict: Dictionary containing billing summary information
        """
        billing_data = BillingSystem.get_all_billing_data()
        
        # Only consider patients with bill_amount > 0 for financial calculations
        billed_patients = [bill for bill in billing_data if bill['bill_amount'] > 0] 
        total_billed = sum(bill['bill_amount'] for bill in billed_patients)
        total_paid = sum(bill['amount_paid'] for bill in billed_patients)
        total_outstanding = sum(bill['outstanding_amount'] for bill in billed_patients)
        
        average_bill = total_billed / len(billed_patients) if billed_patients else 0
        
        # Count patients by payment status across all billing data
        payment_status_counts = {}
        for bill in billing_data:
            status = bill['payment_status']
            payment_status_counts[status] = payment_status_counts.get(status, 0) + 1
        
        # Count insured vs non-insured patients (all patients)
        insured_count = sum(1 for bill in billing_data if bill['insurance_coverage'] == 'Yes')
        non_insured_count = len(billing_data) - insured_count
        
        summary = {
            'total_patients': len(billing_data),
            'total_billed': total_billed,
            'average_bill': average_bill,
            'total_paid': total_paid,
            'total_outstanding': total_outstanding,
            'collection_rate': (total_paid / total_billed * 100) if total_billed > 0 else 0,
            'payment_status_counts': payment_status_counts,
            'insured_count': insured_count,
            'non_insured_count': non_insured_count
        }
        
        logger.info(f"Generated billing summary report: Total billed={total_billed}, Patients={len(billing_data)}, Average bill={average_bill:.2f}")
        return summary
    
    @staticmethod
    def update_payment(patient_id, amount_paid, new_status=None):
        """
        Update payment information for a patient
        
        Args:
            patient_id (str): Patient ID
            amount_paid (float): New amount paid
            new_status (str, optional): New payment status
            
        Returns:
            bool: True if successful, False otherwise
        """
        patients = read_patients_from_csv(PATIENT_DATA_PATH)
        updated = False
        
        for patient in patients:
            if patient.get('patient_id') == patient_id or patient.get('PatientID') == patient_id:
                try:
                    bill_amount = float(patient.get('bill_amount', patient.get('BillAmount', 0)))
                    original_amount_paid = float(patient.get('amount_paid', patient.get('AmountPaid', 0)))
                    
                    new_amount_paid = float(amount_paid)
                    patient['amount_paid'] = str(new_amount_paid)
                    
                    outstanding = max(0, bill_amount - new_amount_paid)
                    patient['outstanding_amount'] = str(outstanding)
                    
                    if new_status:
                        patient['payment_status'] = new_status
                    else:
                        if bill_amount == 0:
                            patient['payment_status'] = 'Not Applicable'
                        elif outstanding == 0:
                            patient['payment_status'] = 'Fully Paid'
                        elif new_amount_paid > 0:
                            patient['payment_status'] = 'Partially Paid'
                        else:
                            patient['payment_status'] = 'Unpaid'
                    
                    updated = True
                    logger.info(f"Updated payment for patient {patient_id}: Amount paid ${new_amount_paid}, Status: {patient['payment_status']}")
                    break
                except Exception as e:
                    logger.error(f"Error updating payment: {str(e)}")
                    return False
        
        if not updated:
            logger.warning(f"Patient {patient_id} not found for payment update")
            return False
        
        try:
            csv_file = os.path.join('data', 'patients.csv')
            csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), csv_file)
            
            # Extract all keys from patient dicts to handle flexible CSV structure
            field_names = set()
            for p in patients:
                field_names.update(p.keys())
            field_names = list(field_names)
            
            with open(csv_path, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=field_names, delimiter='\t')
                writer.writeheader()
                writer.writerows(patients)
            
            logger.info("Successfully saved updated billing information to CSV")
            return True
        except Exception as e:
            logger.error(f"Error saving updated billing data: {str(e)}")
            return False
    
    @staticmethod
    def generate_financial_report(report_type='daily'):
        """
        Generate a financial report
        
        Args:
            report_type (str): Type of report ('daily' or 'monthly')
            
        Returns:
            dict: Report data
        """
        billing_data = BillingSystem.get_all_billing_data()
        summary = BillingSystem.get_billing_summary()
        
        current_date = datetime.now()
        
        if report_type == 'daily':
            report_data = [bill for bill in billing_data if bill['admission_date'] == current_date.strftime('%Y-%m-%d')]
            report_title = f"Daily Financial Report - {current_date.strftime('%Y-%m-%d')}"
        else:
            current_month = current_date.strftime('%Y-%m')
            report_data = [bill for bill in billing_data if bill['admission_date'].startswith(current_month)]
            report_title = f"Monthly Financial Report - {current_date.strftime('%B %Y')}"
        
        total_billed = sum(bill['bill_amount'] for bill in report_data)
        total_paid = sum(bill['amount_paid'] for bill in report_data)
        total_outstanding = sum(bill['outstanding_amount'] for bill in report_data)
        
        report = {
            'title': report_title,
            'generated_at': current_date.strftime('%Y-%m-%d %H:%M:%S'),
            'data': report_data,
            'total_patients': len(report_data),
            'total_billed': total_billed,
            'total_paid': total_paid,
            'total_outstanding': total_outstanding,
            'collection_rate': (total_paid / total_billed * 100) if total_billed > 0 else 0,
            'overall_summary': summary
        }
        
        logger.info(f"Generated {report_type} financial report with {len(report_data)} records")
        return report


# Create singleton instance
billing_system = BillingSystem()