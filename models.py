from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Patient:
    patient_id: str
    name: str
    age: int
    gender: str
    locality: str
    condition_severity: str
    priority_level: str
    medical_history: str
    bill_amount: float
    amount_paid: float
    outstanding_amount: float
    payment_status: str
    insurance_coverage: str
    insurance_details: str
    admission_date: str
    discharge_date: Optional[str] = None
    timestamp: Optional[str] = None
    
    @property
    def is_emergency(self) -> bool:
        """Check if patient is an emergency case (High severity, no discharge date)"""
        return (self.condition_severity == 'Critical' or self.condition_severity == 'High') and not self.discharge_date

@dataclass
class EmergencyCase:
    patient_id: str
    name: str
    condition: str
    priority: str
    priority_level: int
    priority_name: str
    time_added: str
    formatted_time: str

@dataclass
class ReportData:
    title: str
    generated_at: str
    total_patients: int
    total_billed: float
    total_paid: float
    total_outstanding: float
    collection_rate: float
    data: list

@dataclass
class MLInsights:
    visit_predictions: dict
    disease_predictions: dict
