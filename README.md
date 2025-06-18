                     Hospital Management System
This is a complete web-based Hospital Management System built using Flask. It manages everything from patient registration and emergency handling to billing, reporting, and basic machine learning insights — all using CSV files as the data store.

Main Features
Core Modules
Patient Registration – Add and manage patient details easily.

Emergency Queue – Prioritized emergency case handling using a custom queue.

Billing Dashboard – Tracks payments, outstanding balances, and billing records.

ML Insights – Basic ML models provide predictions for patient visits and disease trends.

Reports Dashboard – Visual and tabular reports for hospital analytics.

Healthcare-Solutions/
├── app.py                          # Flask initialization
├── main.py                         # App entry point
├── models.py                       # Data structures for patients and emergencies
├── routes.py                       # Flask routes
├── billing.py                      # Billing-related routes and logic
├── emergency.py                    # Emergency queue system
├── ml_insights.py                  # ML-based analysis
├── utils.py                        # Helper functions for reading/writing CSV
├── patient_records_with_timestamp.csv  # Main patient data file (1200+ entries)
├── emergency_cases.csv             # Emergency case data
├── templates/                      # HTML templates (Bootstrap-based)
│   ├── base.html                   # Layout template
│   ├── index.html                  # Dashboard
│   ├── register.html               # Register new patients
│   ├── patients.html               # View patient list
│   ├── patient_detail.html         # View individual patient info
│   ├── emergency.html              # Emergency case handling
│   ├── billing_dashboard.html      # Billing overview
│   ├── ml_insights.html            # Analytics and predictions
│   └── reports_dashboard.html      # Reports view
└── static/
    ├── css/
    │   └── style.css               # Custom styles
    └── js/
        └── validation.js           # Client-side form validation


Data is stored in CSV files for simplicity and transparency.

Files:
patient_records_with_timestamp.csv – Stores patient data and history

emergency_cases.csv – Maintains the emergency queue

Each patient record includes:

ID, name, age, gender, locality

Medical history and current condition

Severity and priority level

Billing info: total amount, payment status

Admission/discharge dates

Insurance status

Emergency Handling
Prioritizes patients based on severity

Works through a CSV-based queue

Automatically removes cases once handled

Billing System
Shows total revenue and dues

Tracks paid vs unpaid cases

Visual financial reports

ML Insights
Analyzes common diseases and trends

Predicts patient volume

Highlights high-risk patients using case data

Hospital Reports
Age/gender/locality distributions

Peak hours and case load trends

Disease frequency analytics

🧬 Medical Conditions Covered
The system accounts for 50+ medical conditions such as:

Cardiac: Heart failure, hypertension

Respiratory: Asthma, pneumonia

Metabolic: Diabetes, thyroid issues

Cancer: Basic oncology records

Emergency: Fractures, burns, acute trauma

🛠 Tech Stack
Backend: Python (Flask)

Data: CSV files

Frontend: HTML5, Bootstrap 5, JavaScript

ML/Analytics: Pandas, NumPy, Matplotlib

🔐 Data Privacy & Validation
Form validation and secure input handling

Discharge/admission timestamps for audit logs

Basic safeguards around sensitive data

⚡ Performance
Optimized for handling 1000+ records

Instant CSV-based read/write operations

Real-time dashboard and queue updates

Emergency Handling
Prioritizes patients based on severity

Works through a CSV-based queue

Automatically removes cases once handled

Billing System
Shows total revenue and dues

Tracks paid vs unpaid cases

Visual financial reports

ML Insights
Analyzes common diseases and trends

Predicts patient volume

Highlights high-risk patients using case data

Hospital Reports
Age/gender/locality distributions

Peak hours and case load trends

Disease frequency analytics

🧬 Medical Conditions Covered
The system accounts for 50+ medical conditions such as:

Cardiac: Heart failure, hypertension

Respiratory: Asthma, pneumonia

Metabolic: Diabetes, thyroid issues

Cancer: Basic oncology records

Emergency: Fractures, burns, acute trauma

🛠 Tech Stack
Backend: Python (Flask)

Data: CSV files

Frontend: HTML5, Bootstrap 5, JavaScript

ML/Analytics: Pandas, NumPy, Matplotlib

🔐 Data Privacy & Validation
Form validation and secure input handling

Discharge/admission timestamps for audit logs

Basic safeguards around sensitive data

⚡ Performance
Optimized for handling 1000+ records

Instant CSV-based read/write operations

Real-time dashboard and queue updates

