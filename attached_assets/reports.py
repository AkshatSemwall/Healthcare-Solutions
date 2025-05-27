"""
Reports Module - Generate comprehensive hospital reports
"""
import os
import csv
import logging
import random
from datetime import datetime, timedelta
import numpy as np
from utils import read_patients_from_csv
from emergency_handler import emergency_handler
from billing import billing_system

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Class to handle report generation and analytics"""
    
    @staticmethod
    def generate_daily_report():
        """
        Generate a comprehensive daily report with all hospital statistics
        
        Returns:
            dict: Report data containing all statistics
        """
        # Get current date
        current_date = datetime.now()
        yesterday = current_date - timedelta(days=1)
        
        # Get patient data
        patients = read_patients_from_csv()
        
        # Get billing data and summary
        billing_data = billing_system.get_all_billing_data()
        billing_summary = billing_system.get_billing_summary()
        
        # Get emergency data
        emergency_cases = emergency_handler.get_all_cases()
        
        # Calculate basic stats
        total_patients = len(patients)
        total_emergency_cases = len(emergency_cases)
        avg_bill = billing_summary.get('total_billed', 0) / max(1, total_patients)
        total_revenue = billing_summary.get('total_paid', 0)
        
        # Get age distribution
        age_groups = {
            "0-18": 0,
            "19-35": 0,
            "36-50": 0,
            "51-65": 0,
            "65+": 0
        }
        
        for patient in patients:
            try:
                age = int(patient.get('age', 0))
                if age <= 18:
                    age_groups["0-18"] += 1
                elif age <= 35:
                    age_groups["19-35"] += 1
                elif age <= 50:
                    age_groups["36-50"] += 1
                elif age <= 65:
                    age_groups["51-65"] += 1
                else:
                    age_groups["65+"] += 1
            except (ValueError, TypeError):
                pass
        
        # Get condition distribution (using severity as proxy)
        condition_distribution = {
            "Critical": 0,
            "Severe": 0,
            "Moderate": 0,
            "Mild": 0
        }
        
        for patient in patients:
            severity = patient.get('condition_severity', '')
            if severity in condition_distribution:
                condition_distribution[severity] += 1
        
        # Calculate ICU usage (for demo purposes)
        # In a real system, this would come from actual ICU data
        icu_beds_total = 50
        icu_beds_used = sum(1 for patient in patients if patient.get('condition_severity') == 'Critical')
        icu_usage_percentage = (icu_beds_used / icu_beds_total) * 100 if icu_beds_total > 0 else 0
        
        # Calculate staff usage (for demo purposes)
        staff_total = 200
        staff_utilization = min(95, max(60, 60 + (total_patients / 10)))  # Simulate higher utilization with more patients
        
        # Generate ML predictions (simulated for demo)
        # In a real system, this would come from actual ML models
        next_day_visits_prediction = total_patients + random.randint(-5, 5)
        next_day_visits_prediction = max(0, next_day_visits_prediction)
        
        trending_diseases = [
            {"name": "Influenza", "trend": random.uniform(0.8, 1.2), "cases": random.randint(5, 15)},
            {"name": "COVID-19", "trend": random.uniform(0.7, 1.3), "cases": random.randint(2, 10)},
            {"name": "Gastroenteritis", "trend": random.uniform(0.9, 1.1), "cases": random.randint(3, 12)},
            {"name": "Hypertension", "trend": random.uniform(0.95, 1.05), "cases": random.randint(8, 20)},
            {"name": "Diabetes", "trend": random.uniform(0.98, 1.02), "cases": random.randint(6, 18)}
        ]
        
        # Sort trending diseases by cases
        trending_diseases.sort(key=lambda x: x["cases"], reverse=True)
        
        # Generate financial forecast (simulated for demo)
        # In a real system, this would come from actual forecasting models
        revenue_forecast = total_revenue * random.uniform(0.95, 1.15)
        expense_forecast = total_revenue * random.uniform(0.7, 0.9)
        profit_forecast = revenue_forecast - expense_forecast
        
        # Compile report data
        report = {
            "title": f"Daily Hospital Operations Report",
            "date": current_date.strftime('%Y-%m-%d'),
            "generated_at": current_date.strftime('%Y-%m-%d %H:%M:%S'),
            
            # Basic stats
            "total_patients": total_patients,
            "total_emergency_cases": total_emergency_cases,
            "avg_bill": avg_bill,
            "total_revenue": total_revenue,
            
            # Patient demographics
            "age_distribution": age_groups,
            "condition_distribution": condition_distribution,
            
            # Resource utilization
            "icu_usage": {
                "total_beds": icu_beds_total,
                "beds_used": icu_beds_used,
                "usage_percentage": icu_usage_percentage
            },
            "staff_utilization": {
                "total_staff": staff_total,
                "utilization_percentage": staff_utilization
            },
            
            # ML insights
            "ml_predictions": {
                "next_day_visits": next_day_visits_prediction,
                "trending_diseases": trending_diseases
            },
            
            # Financial summary
            "financial_summary": billing_summary,
            "financial_forecast": {
                "revenue_forecast": revenue_forecast,
                "expense_forecast": expense_forecast,
                "profit_forecast": profit_forecast
            }
        }
        
        logger.info(f"Generated daily report for {current_date.strftime('%Y-%m-%d')}")
        return report
    
    @staticmethod
    def get_historical_data(days=30):
        """
        Get historical patient and revenue data for trend analysis
        
        Args:
            days (int): Number of days of historical data to generate
            
        Returns:
            dict: Historical data for trending
        """
        current_date = datetime.now()
        
        # Generate simulated historical data for demo purposes
        # In a real system, this would come from the actual database
        dates = [(current_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
        dates.reverse()  # Oldest to newest
        
        # Generate patient counts with a slight upward trend and weekend dips
        base_patient_count = 15
        patient_counts = []
        
        for i in range(days):
            # Add trend (slight increase over time)
            trend_factor = 1 + (i * 0.01)
            
            # Add seasonality (weekend dips)
            day_of_week = (current_date - timedelta(days=days-i-1)).weekday()
            weekend_factor = 0.7 if day_of_week >= 5 else 1.0  # Weekend factor
            
            # Add noise
            noise = np.random.normal(0, 2)
            
            # Calculate patient count
            count = max(0, int((base_patient_count * trend_factor * weekend_factor) + noise))
            patient_counts.append(count)
        
        # Generate revenue data based on patient counts
        avg_revenue_per_patient = 500
        revenues = [count * avg_revenue_per_patient * random.uniform(0.9, 1.1) for count in patient_counts]
        
        # Generate emergency cases
        emergency_counts = [max(0, int(count * random.uniform(0.1, 0.3))) for count in patient_counts]
        
        historical_data = {
            "dates": dates,
            "patient_counts": patient_counts,
            "revenues": revenues,
            "emergency_counts": emergency_counts
        }
        
        logger.info(f"Generated historical data for the past {days} days")
        return historical_data

# Create singleton instance
report_generator = ReportGenerator()