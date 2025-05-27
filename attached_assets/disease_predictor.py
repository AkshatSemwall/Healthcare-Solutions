"""
Disease Prediction Module - Predict trending diseases
"""
import os
import csv
import logging
import random
from collections import Counter, defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DiseasePredictionModel:
    """Predict trending diseases based on historical patient data"""
    
    def __init__(self, csv_path=None):
        """Initialize the disease prediction model with data path"""
        if csv_path is None:
            default_path = os.path.join('data', 'patients.csv')
            alt_path = os.path.join('attached_assets', 'patient_records_with_timestamp.csv')
            
            # Try using the real data file if it exists
            if os.path.exists(alt_path):
                self.csv_path = alt_path
                logger.info(f"Using real patient data from {alt_path}")
            else:
                self.csv_path = default_path
        else:
            self.csv_path = csv_path
        
        # Common disease keywords to look for in medical history
        self.disease_keywords = {
            'Hypertension': ['hypertension', 'high blood pressure', 'hbp'],
            'Diabetes': ['diabetes', 'type 1', 'type 2', 'insulin'],
            'Asthma': ['asthma', 'respiratory', 'breathing difficulty'],
            'Heart Disease': ['heart disease', 'cardiac', 'arrhythmia', 'atrial fibrillation'],
            'Influenza': ['flu', 'influenza', 'fever', 'cough'],
            'COVID-19': ['covid', 'coronavirus', 'sars-cov-2'],
            'Gastroenteritis': ['gastroenteritis', 'stomach flu', 'diarrhea', 'vomiting'],
            'Pneumonia': ['pneumonia', 'lung infection'],
            'Allergies': ['allergy', 'allergic reaction', 'hay fever'],
            'Arthritis': ['arthritis', 'joint pain', 'rheumatoid']
        }
        
        self.historical_data = None
        self.disease_counts = None
        self.load_data()
    
    def load_data(self):
        """Load patient data from CSV file and analyze disease patterns"""
        try:
            if not os.path.exists(self.csv_path):
                logger.warning(f"Patient data file not found at {self.csv_path}")
                # Create simulated disease data
                self.generate_simulated_data()
                return
            
            # Extract medical history from patient data
            patient_records = []
            with open(self.csv_path, mode='r', newline='') as file:
                # Determine the delimiter by examining the first line
                first_line = file.readline().strip()
                file.seek(0)  # Reset file pointer to beginning
                
                delimiter = '\t' if '\t' in first_line else ','
                
                reader = csv.DictReader(file, delimiter=delimiter)
                for row in reader:
                    medical_history = None
                    admission_date = None
                    
                    # Check for medical history in either format (camelCase or snake_case)
                    if 'MedicalHistory' in row and row['MedicalHistory']:
                        medical_history = row['MedicalHistory'].lower()
                    elif 'medical_history' in row and row['medical_history']:
                        medical_history = row['medical_history'].lower()
                    
                    # Check for admission date in either format
                    if 'AdmissionDate' in row:
                        admission_date = row['AdmissionDate']
                    elif 'admission_date' in row:
                        admission_date = row['admission_date']
                    
                    if medical_history:
                        patient_records.append({
                            'medical_history': medical_history,
                            'admission_date': admission_date or ''
                        })
            
            # Extract diseases from medical history
            self.disease_counts = defaultdict(int)
            for record in patient_records:
                # Direct disease mentions (when diseases are explicitly listed)
                diseases_found = set()
                for disease, keywords in self.disease_keywords.items():
                    if any(keyword in record['medical_history'] for keyword in keywords):
                        self.disease_counts[disease] += 1
                        diseases_found.add(disease)
                
                # Check for direct disease mentions in the medical history string
                medical_history = record['medical_history']
                for disease_name in self.disease_keywords.keys():
                    if disease_name.lower() in medical_history and disease_name not in diseases_found:
                        self.disease_counts[disease_name] += 1
            
            logger.info(f"Analyzed {len(patient_records)} patient records for disease trends")
            
            if not self.disease_counts:
                logger.warning("No disease data found in patient records")
                self.generate_simulated_data()
        except Exception as e:
            logger.error(f"Error loading patient data for disease prediction: {str(e)}")
            # Create simulated disease data as fallback
            self.generate_simulated_data()
    
    def generate_simulated_data(self):
        """Generate simulated disease data"""
        disease_counts = {}
        
        # Generate realistic disease distribution
        for disease in self.disease_keywords.keys():
            # Simulate some diseases being more common than others
            if disease in ['Hypertension', 'Diabetes', 'Allergies']:
                # Common diseases
                count = random.randint(15, 30)
            elif disease in ['Influenza', 'Gastroenteritis', 'Arthritis']:
                # Moderately common
                count = random.randint(8, 20)
            else:
                # Less common
                count = random.randint(2, 15)
            
            disease_counts[disease] = count
        
        self.disease_counts = disease_counts
        logger.info("Generated simulated disease data")
    
    def predict_trending_diseases(self, top_n=5):
        """Predict the top N trending diseases"""
        if self.disease_counts is None or not self.disease_counts:
            self.generate_simulated_data()
        
        # Sort diseases by count
        disease_items = list(self.disease_counts.items()) if self.disease_counts else []
        sorted_diseases = sorted(disease_items, key=lambda x: x[1], reverse=True)
        
        # Get top N diseases
        top_diseases = sorted_diseases[:top_n]
        
        # Add trend indicators (simulated for demo)
        trending_diseases = []
        for disease, count in top_diseases:
            # Simulate trend direction (up, down, or stable)
            trend_value = random.uniform(0.8, 1.2)
            
            trending_diseases.append({
                'name': disease,
                'cases': count,
                'trend': trend_value  # > 1 means increasing, < 1 means decreasing
            })
        
        logger.debug(f"Predicted top {len(trending_diseases)} trending diseases")
        return trending_diseases
    
    def get_disease_distribution(self):
        """Get overall disease distribution for visualization"""
        # Ensure we have disease data
        if self.disease_counts is None or not self.disease_counts:
            self.generate_simulated_data()
        
        # Sort diseases by count for visualization
        disease_items = list(self.disease_counts.items()) if self.disease_counts else []
        sorted_diseases = sorted(disease_items, key=lambda x: x[1], reverse=True)
        
        # Limit to top 10 diseases for better visualization
        top_diseases = sorted_diseases[:10] if len(sorted_diseases) > 10 else sorted_diseases
        
        return {
            'diseases': [d[0] for d in top_diseases],
            'counts': [d[1] for d in top_diseases]
        }


# Create singleton instance
disease_prediction_model = DiseasePredictionModel()