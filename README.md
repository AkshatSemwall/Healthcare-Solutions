# Hospital Management System

A comprehensive web-based Hospital Management System built with Flask and CSV data storage.

## Features

### 🏥 Core Modules
- **Patient Registration** - Register and manage patient records
- **Emergency Queue** - Priority-based emergency case management
- **Billing Dashboard** - Financial tracking and payment management
- **ML Insights** - Predictive analytics for patient visits and disease trends
- **Reports Dashboard** - Comprehensive hospital analytics and reporting

### 📊 Key Capabilities
- **1200+ Patient Records** - Real patient data with medical conditions
- **Priority-based Emergency Queue** - Separate CSV-based emergency management
- **Financial Analytics** - Revenue tracking, collection rates, outstanding amounts
- **Disease Trend Analysis** - Real medical condition tracking and predictions
- **Visit Forecasting** - ML-powered patient visit predictions

## Project Structure

```
hospital-management-system/
├── app.py                              # Flask application setup
├── main.py                             # Application entry point
├── models.py                           # Data models (Patient, EmergencyCase, etc.)
├── utils.py                            # Utility functions for CSV operations
├── routes.py                           # Main application routes
├── emergency.py                        # Emergency queue management
├── billing.py                          # Billing and financial routes
├── ml_insights.py                      # ML insights and predictions
├── patient_records_with_timestamp.csv  # Main patient database (1200+ records)
├── emergency_cases.csv                 # Emergency queue data
├── templates/                          # HTML templates
│   ├── base.html                       # Base template
│   ├── index.html                      # Dashboard
│   ├── register.html                   # Patient registration
│   ├── patients.html                   # Patient listing
│   ├── patient_detail.html             # Patient details
│   ├── emergency.html                  # Emergency queue
│   ├── billing_dashboard.html          # Billing dashboard
│   ├── ml_insights.html                # ML insights
│   └── reports_dashboard.html          # Reports
└── static/                             # Static assets
    ├── css/
    │   └── style.css                   # Healthcare-themed styling
    └── js/
        └── validation.js               # Form validation
```

## Data Storage

### CSV Files
- **patient_records_with_timestamp.csv** - Main patient database
- **emergency_cases.csv** - Emergency queue management

### Patient Data Fields
- Patient ID, Name, Age, Gender, Locality
- Medical History (actual medical conditions)
- Condition Severity, Priority Level
- Billing Information (amounts, payment status)
- Insurance Coverage and Details
- Admission/Discharge Dates

## Installation & Setup

1. **Install Dependencies**
   ```bash
   pip install flask flask-sqlalchemy gunicorn matplotlib numpy pandas psycopg2-binary seaborn werkzeug email-validator
   ```

2. **Run the Application**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

3. **Access the Application**
   - Open your browser to `http://localhost:5000`

## Key Features

### Emergency Queue Management
- Priority-based queue (Emergency → Urgent → Standard → Routine)
- Separate CSV file for queue operations
- Real-time case processing and removal

### Billing & Financial Analytics
- Revenue tracking and collection rates
- Outstanding amount management
- Payment status monitoring
- Financial report generation

### ML Insights & Predictions
- Disease trend analysis using actual medical conditions
- Patient visit volume forecasting
- Risk assessment based on case severity

### Reports Dashboard
- Comprehensive hospital statistics
- Historical data trends
- Patient demographics and analytics

## Medical Conditions Tracked

The system tracks 50+ real medical conditions including:
- Cardiovascular: Heart Failure, Coronary Artery Disease, Hypertension
- Respiratory: Asthma, COPD, Pneumonia
- Metabolic: Diabetes, Thyroid Disorders
- Oncology: Various cancer types
- Emergency: Fractures, Burns, Acute conditions
- And many more...

## Technology Stack

- **Backend**: Flask (Python)
- **Data Storage**: CSV files
- **Frontend**: Bootstrap 5, HTML5, JavaScript
- **Styling**: Healthcare-themed CSS
- **Analytics**: Matplotlib, Pandas, NumPy

## Healthcare Compliance

- Patient data privacy considerations
- Secure form validation
- Proper error handling
- Audit trail through timestamps

## Performance

- Handles 1200+ patient records efficiently
- Optimized CSV operations
- Fast emergency queue processing
- Real-time dashboard updates