import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple
import logging
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import LabelEncoder
    from sklearn.cluster import KMeans
except ImportError:
    # Fallback for environments without sklearn
    class LinearRegression:
        def __init__(self): pass
        def fit(self, X, y): pass
        def predict(self, X): return [1] * len(X)
    
    class LabelEncoder:
        def __init__(self): pass
    
    class KMeans:
        def __init__(self, **kwargs): pass
        def fit_predict(self, X): return [0] * len(X)
from models import Patient
import warnings
warnings.filterwarnings('ignore')

class PatientVisitPredictor:
    """ML model for predicting patient visit patterns"""
    
    def __init__(self):
        self.model = LinearRegression()
        self.is_trained = False
        self.feature_columns = ['day_of_week', 'month', 'season', 'week_of_year']
        
    def prepare_features(self, dates: List[str]) -> pd.DataFrame:
        """Prepare time-based features from dates"""
        df = pd.DataFrame({'date': pd.to_datetime(dates)})
        
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['week_of_year'] = df['date'].dt.isocalendar().week
        
        # Season encoding (0=Winter, 1=Spring, 2=Summer, 3=Fall)
        df['season'] = ((df['month'] % 12) // 3)
        
        return df[self.feature_columns].copy()
    
    def train(self, patients: List[Patient]) -> Dict[str, Any]:
        """Train the visit prediction model using historical patient data"""
        if not patients:
            return {'status': 'error', 'message': 'No patient data available for training'}
        
        # Extract admission dates and create daily visit counts
        daily_visits = defaultdict(int)
        
        for patient in patients:
            if patient.admission_date:
                try:
                    # Parse various date formats
                    date_str = patient.admission_date.split()[0]  # Remove time if present
                    
                    # Try different date formats
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                        try:
                            date_obj = datetime.strptime(date_str, fmt)
                            date_key = date_obj.strftime('%Y-%m-%d')
                            daily_visits[date_key] += 1
                            break
                        except ValueError:
                            continue
                except Exception as e:
                    logging.warning(f"Could not parse admission date: {patient.admission_date}")
                    continue
        
        if len(daily_visits) < 7:  # Need at least a week of data
            return {'status': 'error', 'message': 'Insufficient historical data for training (need at least 7 days)'}
        
        # Create training dataset
        dates = sorted(daily_visits.keys())
        visit_counts = [daily_visits[date] for date in dates]
        
        # Prepare features
        X = self.prepare_features(dates)
        y = np.array(visit_counts)
        
        # Train the model
        self.model.fit(X, y)
        self.is_trained = True
        
        # Calculate model performance metrics
        predictions = self.model.predict(X)
        mse = np.mean((y - predictions) ** 2)
        mae = np.mean(np.abs(y - predictions))
        
        return {
            'status': 'success',
            'training_days': len(dates),
            'mse': round(mse, 2),
            'mae': round(mae, 2),
            'date_range': f"{dates[0]} to {dates[-1]}"
        }
    
    def predict_next_days(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Predict patient visits for the next N days"""
        if not self.is_trained:
            return []
        
        predictions = []
        today = datetime.now()
        
        for i in range(1, days_ahead + 1):
            future_date = today + timedelta(days=i)
            date_str = future_date.strftime('%Y-%m-%d')
            
            # Prepare features for this date
            X = self.prepare_features([date_str])
            
            # Make prediction
            predicted_visits = max(1, int(round(self.model.predict(X)[0])))
            
            predictions.append({
                'date': date_str,
                'day_name': future_date.strftime('%A'),
                'predicted_visits': predicted_visits,
                'confidence': 'high' if future_date.weekday() < 5 else 'medium'  # Weekdays vs weekends
            })
        
        return predictions
    
    def get_historical_trends(self, patients: List[Patient], days: int = 30) -> Dict[str, Any]:
        """Get historical visit trends for visualization"""
        daily_visits = defaultdict(int)
        
        for patient in patients:
            if patient.admission_date:
                try:
                    date_str = patient.admission_date.split()[0]
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                        try:
                            date_obj = datetime.strptime(date_str, fmt)
                            date_key = date_obj.strftime('%Y-%m-%d')
                            daily_visits[date_key] += 1
                            break
                        except ValueError:
                            continue
                except:
                    continue
        
        # Get last N days
        today = datetime.now()
        dates = []
        visit_counts = []
        
        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            dates.append(date_str)
            visit_counts.append(daily_visits.get(date_str, 0))
        
        return {
            'dates': dates,
            'visit_counts': visit_counts,
            'average_daily_visits': np.mean(visit_counts) if visit_counts else 0,
            'peak_day': dates[np.argmax(visit_counts)] if visit_counts else None
        }

class DiseasePatternAnalyzer:
    """ML model for analyzing disease patterns and trends"""
    
    def __init__(self):
        self.label_encoder = LabelEncoder()
        self.kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
        self.is_trained = False
        
    def analyze_disease_patterns(self, patients: List[Patient]) -> Dict[str, Any]:
        """Analyze disease patterns and identify trends"""
        if not patients:
            return self._empty_analysis()
        
        # Extract medical conditions and localities
        conditions = []
        localities = []
        ages = []
        
        for patient in patients:
            if patient.medical_history and patient.medical_history.strip():
                conditions.append(patient.medical_history.strip().lower())
                localities.append(patient.locality.strip().lower() if patient.locality else 'unknown')
                ages.append(patient.age if patient.age > 0 else 30)  # Default age if missing
        
        if not conditions:
            return self._empty_analysis()
        
        # Disease frequency analysis
        condition_counts = Counter(conditions)
        top_diseases = condition_counts.most_common(10)
        
        # Geographic disease distribution
        geo_disease_map = defaultdict(lambda: defaultdict(int))
        for i, condition in enumerate(conditions):
            locality = localities[i] if i < len(localities) else 'unknown'
            geo_disease_map[locality][condition] += 1
        
        # Age-based disease analysis
        age_disease_map = defaultdict(list)
        for i, condition in enumerate(conditions):
            age = ages[i] if i < len(ages) else 30
            age_disease_map[condition].append(age)
        
        # Calculate disease trends and risk factors
        disease_insights = []
        total_patients = len(patients)
        
        for disease, count in top_diseases:
            ages_affected = age_disease_map.get(disease, [])
            avg_age = np.mean(ages_affected) if ages_affected else 0
            
            # Find most affected localities
            affected_localities = []
            for locality, diseases in geo_disease_map.items():
                if disease in diseases:
                    affected_localities.append({
                        'locality': locality.title(),
                        'cases': diseases[disease]
                    })
            
            affected_localities.sort(key=lambda x: x['cases'], reverse=True)
            
            prevalence_rate = (count / total_patients) * 100
            
            disease_insights.append({
                'disease': disease.title(),
                'total_cases': count,
                'prevalence_rate': round(prevalence_rate, 2),
                'average_age': round(avg_age, 1),
                'most_affected_localities': affected_localities[:3],
                'risk_level': self._calculate_risk_level(prevalence_rate),
                'trend': self._determine_trend(count, total_patients)
            })
        
        # Clustering analysis for pattern detection
        clusters = self._perform_clustering_analysis(patients)
        
        return {
            'disease_insights': disease_insights,
            'geographic_patterns': self._analyze_geographic_patterns(geo_disease_map),
            'age_patterns': self._analyze_age_patterns(age_disease_map),
            'clustering_insights': clusters,
            'total_diseases_tracked': len(condition_counts),
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _calculate_risk_level(self, prevalence_rate: float) -> str:
        """Calculate risk level based on prevalence rate"""
        if prevalence_rate >= 15:
            return 'High'
        elif prevalence_rate >= 8:
            return 'Medium'
        elif prevalence_rate >= 3:
            return 'Low'
        else:
            return 'Minimal'
    
    def _determine_trend(self, count: int, total_patients: int) -> str:
        """Determine disease trend"""
        prevalence = (count / total_patients) * 100
        if prevalence >= 10:
            return 'Increasing'
        elif prevalence >= 5:
            return 'Stable'
        else:
            return 'Decreasing'
    
    def _analyze_geographic_patterns(self, geo_disease_map: Dict) -> List[Dict]:
        """Analyze disease patterns by geographic location"""
        patterns = []
        
        for locality, diseases in geo_disease_map.items():
            if locality != 'unknown':
                total_cases = sum(diseases.values())
                top_disease = max(diseases.items(), key=lambda x: x[1])
                
                patterns.append({
                    'locality': locality.title(),
                    'total_cases': total_cases,
                    'primary_concern': top_disease[0].title(),
                    'primary_concern_cases': top_disease[1],
                    'disease_diversity': len(diseases)
                })
        
        patterns.sort(key=lambda x: x['total_cases'], reverse=True)
        return patterns[:10]
    
    def _analyze_age_patterns(self, age_disease_map: Dict) -> List[Dict]:
        """Analyze disease patterns by age groups"""
        age_groups = {
            'Children (0-17)': (0, 17),
            'Young Adults (18-35)': (18, 35),
            'Middle-aged (36-55)': (36, 55),
            'Seniors (56+)': (56, 120)
        }
        
        patterns = []
        
        for group_name, (min_age, max_age) in age_groups.items():
            group_diseases = defaultdict(int)
            
            for disease, ages in age_disease_map.items():
                for age in ages:
                    if min_age <= age <= max_age:
                        group_diseases[disease] += 1
            
            if group_diseases:
                top_disease = max(group_diseases.items(), key=lambda x: x[1])
                total_cases = sum(group_diseases.values())
                
                patterns.append({
                    'age_group': group_name,
                    'total_cases': total_cases,
                    'primary_concern': top_disease[0].title(),
                    'primary_concern_cases': top_disease[1],
                    'case_percentage': round((top_disease[1] / total_cases) * 100, 1)
                })
        
        return patterns
    
    def _perform_clustering_analysis(self, patients: List[Patient]) -> Dict[str, Any]:
        """Perform clustering analysis to identify patient groups"""
        try:
            # Prepare data for clustering
            data = []
            for patient in patients:
                age = patient.age if patient.age > 0 else 30
                severity_score = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}.get(patient.condition_severity, 2)
                bill_amount = patient.bill_amount if patient.bill_amount > 0 else 1000
                
                data.append([age, severity_score, np.log(bill_amount)])
            
            if len(data) < 5:  # Need at least 5 patients for clustering
                return {'status': 'insufficient_data'}
            
            data_array = np.array(data)
            
            # Perform clustering
            n_clusters = min(5, len(data) // 2)  # Adaptive cluster count
            self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = self.kmeans.fit_predict(data_array)
            
            # Analyze clusters
            cluster_analysis = []
            for i in range(n_clusters):
                cluster_patients = [p for j, p in enumerate(patients) if clusters[j] == i]
                
                if cluster_patients:
                    avg_age = np.mean([p.age for p in cluster_patients if p.age > 0])
                    avg_bill = np.mean([p.bill_amount for p in cluster_patients if p.bill_amount > 0])
                    common_conditions = Counter([p.medical_history for p in cluster_patients if p.medical_history])
                    
                    cluster_analysis.append({
                        'cluster_id': i,
                        'patient_count': len(cluster_patients),
                        'average_age': round(avg_age, 1),
                        'average_bill': round(avg_bill, 2),
                        'common_condition': common_conditions.most_common(1)[0][0] if common_conditions else 'Mixed',
                        'characteristics': self._describe_cluster(cluster_patients)
                    })
            
            return {
                'status': 'success',
                'clusters': cluster_analysis,
                'total_clusters': n_clusters
            }
            
        except Exception as e:
            logging.error(f"Clustering analysis failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _describe_cluster(self, patients: List[Patient]) -> str:
        """Generate a description for a patient cluster"""
        if not patients:
            return "No patients"
        
        avg_age = np.mean([p.age for p in patients if p.age > 0])
        high_severity_count = sum(1 for p in patients if p.condition_severity in ['High', 'Critical'])
        severity_rate = (high_severity_count / len(patients)) * 100
        
        if avg_age < 25:
            age_desc = "Young patients"
        elif avg_age < 50:
            age_desc = "Middle-aged patients"
        else:
            age_desc = "Older patients"
        
        if severity_rate > 60:
            severity_desc = "with high severity conditions"
        elif severity_rate > 30:
            severity_desc = "with moderate severity conditions"
        else:
            severity_desc = "with mild conditions"
        
        return f"{age_desc} {severity_desc}"
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'disease_insights': [],
            'geographic_patterns': [],
            'age_patterns': [],
            'clustering_insights': {'status': 'no_data'},
            'total_diseases_tracked': 0,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

class RealTimeMLEngine:
    """Main ML engine that combines visit prediction and disease analysis"""
    
    def __init__(self):
        self.visit_predictor = PatientVisitPredictor()
        self.disease_analyzer = DiseasePatternAnalyzer()
        self.last_training_time = None
        self.training_interval = timedelta(hours=6)  # Retrain every 6 hours
        
    def should_retrain(self) -> bool:
        """Check if models should be retrained"""
        if self.last_training_time is None:
            return True
        return datetime.now() - self.last_training_time > self.training_interval
    
    def train_models(self, patients: List[Patient]) -> Dict[str, Any]:
        """Train all ML models with current patient data"""
        results = {}
        
        # Train visit predictor
        visit_training = self.visit_predictor.train(patients)
        results['visit_predictor'] = visit_training
        
        # Disease analyzer doesn't need explicit training
        results['disease_analyzer'] = {'status': 'ready'}
        
        if visit_training.get('status') == 'success':
            self.last_training_time = datetime.now()
        
        return results
    
    def generate_comprehensive_insights(self, patients: List[Patient]) -> Dict[str, Any]:
        """Generate comprehensive ML insights"""
        # Check if retraining is needed
        if self.should_retrain():
            training_results = self.train_models(patients)
        else:
            training_results = {'status': 'using_cached_models'}
        
        # Generate visit predictions
        next_day_prediction = self.visit_predictor.predict_next_days(1)
        weekly_predictions = self.visit_predictor.predict_next_days(7)
        historical_trends = self.visit_predictor.get_historical_trends(patients)
        
        # Generate disease analysis
        disease_patterns = self.disease_analyzer.analyze_disease_patterns(patients)
        
        # Combine insights
        return {
            'visit_predictions': {
                'next_day': next_day_prediction[0] if next_day_prediction else {'predicted_visits': 0},
                'weekly_forecast': weekly_predictions,
                'historical_trends': historical_trends,
                'model_status': training_results.get('visit_predictor', {}).get('status', 'unknown')
            },
            'disease_patterns': disease_patterns,
            'training_info': training_results,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_quality': {
                'total_patients': len(patients),
                'patients_with_dates': len([p for p in patients if p.admission_date]),
                'patients_with_conditions': len([p for p in patients if p.medical_history])
            }
        }