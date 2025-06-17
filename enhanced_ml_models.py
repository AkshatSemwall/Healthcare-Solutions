import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple
import logging
import warnings
warnings.filterwarnings('ignore')

class RealTimePatientAnalyzer:
    """Enhanced ML analyzer for real patient data patterns"""
    
    def __init__(self):
        self.last_analysis_time = None
        self.cached_insights = None
        
    def analyze_visit_patterns(self, patients: List) -> Dict[str, Any]:
        """Analyze real patient visit patterns using time series analysis"""
        if not patients:
            return self._empty_visit_analysis()
        
        # Extract admission dates and create time series
        daily_visits = defaultdict(int)
        locality_visits = defaultdict(lambda: defaultdict(int))
        severity_trends = defaultdict(lambda: defaultdict(int))
        
        valid_dates = []
        
        for patient in patients:
            if hasattr(patient, 'admission_date') and patient.admission_date:
                try:
                    # Parse admission date
                    date_str = str(patient.admission_date).split('T')[0]
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    date_key = date_obj.strftime('%Y-%m-%d')
                    
                    daily_visits[date_key] += 1
                    valid_dates.append(date_obj)
                    
                    # Track locality patterns
                    locality = getattr(patient, 'locality', 'Unknown')
                    locality_visits[locality][date_key] += 1
                    
                    # Track severity patterns
                    severity = getattr(patient, 'condition_severity', 'Unknown')
                    severity_trends[severity][date_key] += 1
                    
                except Exception as e:
                    logging.warning(f"Could not parse date: {patient.admission_date}")
                    continue
        
        if not valid_dates:
            return self._empty_visit_analysis()
        
        # Generate predictions using moving average and seasonal patterns
        predictions = self._generate_visit_predictions(daily_visits)
        
        # Analyze patterns
        patterns = self._analyze_temporal_patterns(daily_visits, valid_dates)
        
        # Locality-based insights
        locality_insights = self._analyze_locality_patterns(locality_visits)
        
        # Severity trends
        severity_insights = self._analyze_severity_trends(severity_trends)
        
        return {
            'daily_predictions': predictions,
            'temporal_patterns': patterns,
            'locality_insights': locality_insights,
            'severity_trends': severity_insights,
            'data_quality': {
                'total_patients': len(patients),
                'valid_dates': len(valid_dates),
                'date_range': f"{min(valid_dates).strftime('%Y-%m-%d')} to {max(valid_dates).strftime('%Y-%m-%d')}"
            }
        }
    
    def _generate_visit_predictions(self, daily_visits: Dict[str, int]) -> List[Dict[str, Any]]:
        """Generate visit predictions using time series analysis"""
        if len(daily_visits) < 7:
            return []
        
        # Sort dates and get visit counts
        sorted_dates = sorted(daily_visits.keys())
        visit_counts = [daily_visits[date] for date in sorted_dates]
        
        # Calculate moving averages
        window_size = min(7, len(visit_counts) // 2)
        moving_avg = []
        
        for i in range(len(visit_counts)):
            start_idx = max(0, i - window_size + 1)
            avg = sum(visit_counts[start_idx:i+1]) / (i - start_idx + 1)
            moving_avg.append(avg)
        
        # Identify day-of-week patterns
        weekday_pattern = defaultdict(list)
        for i, date_str in enumerate(sorted_dates):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            weekday = date_obj.weekday()
            weekday_pattern[weekday].append(visit_counts[i])
        
        # Calculate average visits per weekday
        weekday_avg = {}
        for weekday, counts in weekday_pattern.items():
            weekday_avg[weekday] = sum(counts) / len(counts) if counts else 0
        
        # Generate predictions for next 7 days
        predictions = []
        last_date = datetime.strptime(sorted_dates[-1], '%Y-%m-%d')
        recent_trend = moving_avg[-1] if moving_avg else np.mean(visit_counts)
        
        for i in range(1, 8):
            future_date = last_date + timedelta(days=i)
            weekday = future_date.weekday()
            
            # Combine trend and seasonal factors
            weekday_factor = weekday_avg.get(weekday, recent_trend) / recent_trend if recent_trend > 0 else 1
            predicted_visits = max(1, int(round(recent_trend * weekday_factor)))
            
            predictions.append({
                'date': future_date.strftime('%Y-%m-%d'),
                'day_name': future_date.strftime('%A'),
                'predicted_visits': predicted_visits,
                'confidence': self._calculate_confidence(len(daily_visits), weekday_pattern[weekday])
            })
        
        return predictions
    
    def _analyze_temporal_patterns(self, daily_visits: Dict[str, int], valid_dates: List[datetime]) -> Dict[str, Any]:
        """Analyze temporal patterns in patient visits"""
        # Monthly patterns
        monthly_visits = defaultdict(int)
        for date_obj in valid_dates:
            month_key = date_obj.strftime('%Y-%m')
            monthly_visits[month_key] += 1
        
        # Weekday patterns
        weekday_visits = defaultdict(int)
        for date_obj in valid_dates:
            weekday = date_obj.strftime('%A')
            weekday_visits[weekday] += 1
        
        # Seasonal patterns
        seasonal_visits = defaultdict(int)
        for date_obj in valid_dates:
            month = date_obj.month
            if month in [12, 1, 2]:
                season = 'Winter'
            elif month in [3, 4, 5]:
                season = 'Spring'
            elif month in [6, 7, 8]:
                season = 'Summer'
            else:
                season = 'Fall'
            seasonal_visits[season] += 1
        
        return {
            'monthly_trends': dict(monthly_visits),
            'weekday_distribution': dict(weekday_visits),
            'seasonal_patterns': dict(seasonal_visits),
            'peak_day': max(weekday_visits.items(), key=lambda x: x[1])[0] if weekday_visits else 'Monday',
            'peak_season': max(seasonal_visits.items(), key=lambda x: x[1])[0] if seasonal_visits else 'Spring'
        }
    
    def _analyze_locality_patterns(self, locality_visits: Dict[str, Dict[str, int]]) -> List[Dict[str, Any]]:
        """Analyze visit patterns by locality"""
        locality_insights = []
        
        for locality, daily_counts in locality_visits.items():
            total_visits = sum(daily_counts.values())
            avg_daily = total_visits / len(daily_counts) if daily_counts else 0
            
            # Calculate growth trend
            sorted_dates = sorted(daily_counts.keys())
            if len(sorted_dates) >= 2:
                recent_avg = np.mean([daily_counts[date] for date in sorted_dates[-7:]])
                earlier_avg = np.mean([daily_counts[date] for date in sorted_dates[:7]])
                growth_rate = ((recent_avg - earlier_avg) / earlier_avg * 100) if earlier_avg > 0 else 0
            else:
                growth_rate = 0
            
            locality_insights.append({
                'locality': locality,
                'total_visits': total_visits,
                'average_daily_visits': round(avg_daily, 1),
                'growth_rate': round(growth_rate, 1),
                'trend': 'Increasing' if growth_rate > 5 else 'Decreasing' if growth_rate < -5 else 'Stable'
            })
        
        return sorted(locality_insights, key=lambda x: x['total_visits'], reverse=True)[:10]
    
    def _analyze_severity_trends(self, severity_trends: Dict[str, Dict[str, int]]) -> List[Dict[str, Any]]:
        """Analyze trends in condition severity"""
        severity_insights = []
        
        for severity, daily_counts in severity_trends.items():
            total_cases = sum(daily_counts.values())
            
            # Calculate recent trend
            sorted_dates = sorted(daily_counts.keys())
            if len(sorted_dates) >= 14:
                recent_period = sorted_dates[-7:]
                earlier_period = sorted_dates[-14:-7]
                
                recent_avg = np.mean([daily_counts.get(date, 0) for date in recent_period])
                earlier_avg = np.mean([daily_counts.get(date, 0) for date in earlier_period])
                
                trend_direction = ((recent_avg - earlier_avg) / earlier_avg * 100) if earlier_avg > 0 else 0
            else:
                trend_direction = 0
            
            severity_insights.append({
                'severity': severity,
                'total_cases': total_cases,
                'trend_percentage': round(trend_direction, 1),
                'trend_direction': 'Increasing' if trend_direction > 3 else 'Decreasing' if trend_direction < -3 else 'Stable',
                'priority_level': self._get_severity_priority(severity)
            })
        
        return sorted(severity_insights, key=lambda x: x['priority_level'], reverse=True)
    
    def _calculate_confidence(self, data_points: int, weekday_history: List[int]) -> str:
        """Calculate prediction confidence based on data availability"""
        if data_points >= 30 and len(weekday_history) >= 4:
            return 'High'
        elif data_points >= 14 and len(weekday_history) >= 2:
            return 'Medium'
        else:
            return 'Low'
    
    def _get_severity_priority(self, severity: str) -> int:
        """Get numeric priority for severity levels"""
        severity_map = {
            'Critical': 4,
            'High': 3,
            'Medium': 2,
            'Mild': 1,
            'Low': 1
        }
        return severity_map.get(severity, 1)
    
    def _empty_visit_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'daily_predictions': [],
            'temporal_patterns': {},
            'locality_insights': [],
            'severity_trends': [],
            'data_quality': {'total_patients': 0, 'valid_dates': 0, 'date_range': 'N/A'}
        }

class RealTimeDiseaseAnalyzer:
    """Enhanced disease pattern analyzer for real medical data"""
    
    def __init__(self):
        self.disease_categories = {
            'cardiovascular': ['coronary artery disease', 'heart attack', 'stroke', 'hypertension'],
            'respiratory': ['copd', 'asthma', 'pneumonia', 'lung cancer'],
            'infectious': ['hepatitis', 'tuberculosis', 'covid-19', 'influenza'],
            'neurological': ['dementia', 'alzheimer', 'parkinson', 'stroke'],
            'oncological': ['cancer', 'lymphoma', 'leukemia', 'tumor'],
            'mental_health': ['depression', 'anxiety', 'schizophrenia', 'bipolar'],
            'gastrointestinal': ['appendicitis', 'cirrhosis', 'gastritis', 'ulcer'],
            'endocrine': ['diabetes', 'thyroid disorder', 'obesity'],
            'pediatric': ['pediatric fever', 'childhood asthma', 'developmental delays'],
            'maternal': ['childbirth', 'pregnancy complications', 'postpartum']
        }
    
    def analyze_disease_patterns(self, patients: List) -> Dict[str, Any]:
        """Comprehensive disease pattern analysis"""
        if not patients:
            return self._empty_disease_analysis()
        
        # Extract medical conditions
        diseases = []
        disease_patient_map = defaultdict(list)
        
        for patient in patients:
            if hasattr(patient, 'medical_history') and patient.medical_history:
                condition = str(patient.medical_history).lower().strip()
                if condition and condition != 'nan':
                    diseases.append(condition)
                    disease_patient_map[condition].append(patient)
        
        if not diseases:
            return self._empty_disease_analysis()
        
        # Disease frequency analysis
        disease_counts = Counter(diseases)
        
        # Categorize diseases
        categorized_diseases = self._categorize_diseases(disease_counts)
        
        # Geographic disease mapping
        geographic_patterns = self._analyze_geographic_disease_patterns(disease_patient_map)
        
        # Age-based disease analysis
        age_patterns = self._analyze_age_disease_patterns(disease_patient_map)
        
        # Severity correlation
        severity_correlation = self._analyze_severity_correlation(disease_patient_map)
        
        # Risk assessment
        risk_assessment = self._assess_disease_risks(disease_counts, len(patients))
        
        # Trending diseases
        trending_diseases = self._identify_trending_diseases(disease_patient_map)
        
        return {
            'disease_distribution': dict(disease_counts.most_common(15)),
            'categorized_diseases': categorized_diseases,
            'geographic_patterns': geographic_patterns,
            'age_patterns': age_patterns,
            'severity_correlation': severity_correlation,
            'risk_assessment': risk_assessment,
            'trending_diseases': trending_diseases,
            'total_unique_diseases': len(disease_counts),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _categorize_diseases(self, disease_counts: Counter) -> Dict[str, Dict[str, int]]:
        """Categorize diseases into medical specialties"""
        categorized = defaultdict(lambda: defaultdict(int))
        
        for disease, count in disease_counts.items():
            category_found = False
            for category, keywords in self.disease_categories.items():
                if any(keyword in disease for keyword in keywords):
                    categorized[category][disease] = count
                    category_found = True
                    break
            
            if not category_found:
                categorized['other'][disease] = count
        
        # Convert to regular dict and sort by total cases
        result = {}
        for category, diseases in categorized.items():
            total_cases = sum(diseases.values())
            result[category] = {
                'diseases': dict(diseases),
                'total_cases': total_cases,
                'disease_count': len(diseases)
            }
        
        return dict(sorted(result.items(), key=lambda x: x[1]['total_cases'], reverse=True))
    
    def _analyze_geographic_disease_patterns(self, disease_patient_map: Dict) -> List[Dict[str, Any]]:
        """Analyze disease patterns by geographic location"""
        locality_disease_map = defaultdict(lambda: defaultdict(int))
        
        for disease, patient_list in disease_patient_map.items():
            for patient in patient_list:
                locality = getattr(patient, 'locality', 'Unknown')
                locality_disease_map[locality][disease] += 1
        
        geographic_patterns = []
        for locality, diseases in locality_disease_map.items():
            if locality and locality.lower() != 'unknown':
                total_cases = sum(diseases.values())
                top_disease = max(diseases.items(), key=lambda x: x[1])
                
                # Calculate disease diversity (Shannon index approximation)
                diversity_score = len(diseases) / total_cases if total_cases > 0 else 0
                
                geographic_patterns.append({
                    'locality': locality,
                    'total_cases': total_cases,
                    'primary_disease': top_disease[0],
                    'primary_disease_cases': top_disease[1],
                    'disease_diversity': round(diversity_score, 3),
                    'unique_diseases': len(diseases),
                    'top_diseases': dict(sorted(diseases.items(), key=lambda x: x[1], reverse=True)[:5])
                })
        
        return sorted(geographic_patterns, key=lambda x: x['total_cases'], reverse=True)[:10]
    
    def _analyze_age_disease_patterns(self, disease_patient_map: Dict) -> Dict[str, Dict[str, Any]]:
        """Analyze disease patterns across age groups"""
        age_groups = {
            'pediatric': (0, 17),
            'young_adult': (18, 35),
            'middle_aged': (36, 55),
            'senior': (56, 75),
            'elderly': (76, 120)
        }
        
        age_disease_analysis = {}
        
        for age_group, (min_age, max_age) in age_groups.items():
            group_diseases = defaultdict(int)
            group_patients = []
            
            for disease, patient_list in disease_patient_map.items():
                for patient in patient_list:
                    age = getattr(patient, 'age', 0)
                    if min_age <= age <= max_age:
                        group_diseases[disease] += 1
                        group_patients.append(patient)
            
            if group_diseases:
                total_cases = sum(group_diseases.values())
                top_disease = max(group_diseases.items(), key=lambda x: x[1])
                avg_age = np.mean([getattr(p, 'age', 0) for p in group_patients])
                
                age_disease_analysis[age_group] = {
                    'total_cases': total_cases,
                    'average_age': round(avg_age, 1),
                    'primary_disease': top_disease[0],
                    'primary_disease_cases': top_disease[1],
                    'disease_distribution': dict(sorted(group_diseases.items(), key=lambda x: x[1], reverse=True)[:5])
                }
        
        return age_disease_analysis
    
    def _analyze_severity_correlation(self, disease_patient_map: Dict) -> List[Dict[str, Any]]:
        """Analyze correlation between diseases and severity levels"""
        severity_correlation = []
        
        for disease, patient_list in disease_patient_map.items():
            severity_counts = defaultdict(int)
            total_patients = len(patient_list)
            
            for patient in patient_list:
                severity = getattr(patient, 'condition_severity', 'Unknown')
                severity_counts[severity] += 1
            
            # Calculate severity score (weighted average)
            severity_weights = {'Critical': 4, 'High': 3, 'Medium': 2, 'Mild': 1, 'Low': 1}
            weighted_score = sum(severity_weights.get(sev, 1) * count for sev, count in severity_counts.items())
            avg_severity_score = weighted_score / total_patients if total_patients > 0 else 1
            
            most_common_severity = max(severity_counts.items(), key=lambda x: x[1])[0] if severity_counts else 'Unknown'
            
            severity_correlation.append({
                'disease': disease,
                'total_cases': total_patients,
                'average_severity_score': round(avg_severity_score, 2),
                'most_common_severity': most_common_severity,
                'severity_distribution': dict(severity_counts),
                'risk_category': self._categorize_disease_risk(avg_severity_score)
            })
        
        return sorted(severity_correlation, key=lambda x: x['average_severity_score'], reverse=True)[:15]
    
    def _assess_disease_risks(self, disease_counts: Counter, total_patients: int) -> List[Dict[str, Any]]:
        """Assess disease risks and prevalence"""
        risk_assessment = []
        
        for disease, count in disease_counts.most_common(10):
            prevalence_rate = (count / total_patients) * 100
            
            # Risk level based on prevalence and severity
            if prevalence_rate >= 15:
                risk_level = 'Very High'
            elif prevalence_rate >= 10:
                risk_level = 'High'
            elif prevalence_rate >= 5:
                risk_level = 'Medium'
            elif prevalence_rate >= 2:
                risk_level = 'Low'
            else:
                risk_level = 'Very Low'
            
            risk_assessment.append({
                'disease': disease,
                'cases': count,
                'prevalence_rate': round(prevalence_rate, 2),
                'risk_level': risk_level,
                'recommended_action': self._get_recommended_action(disease, risk_level)
            })
        
        return risk_assessment
    
    def _identify_trending_diseases(self, disease_patient_map: Dict) -> List[Dict[str, Any]]:
        """Identify trending diseases based on recent admission patterns"""
        trending_diseases = []
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for disease, patient_list in disease_patient_map.items():
            recent_cases = 0
            total_cases = len(patient_list)
            
            for patient in patient_list:
                if hasattr(patient, 'admission_date') and patient.admission_date:
                    try:
                        admission_date = datetime.strptime(str(patient.admission_date).split('T')[0], '%Y-%m-%d')
                        if admission_date >= cutoff_date:
                            recent_cases += 1
                    except:
                        continue
            
            if total_cases >= 3:  # Only consider diseases with enough data
                recent_rate = (recent_cases / total_cases) * 100
                
                trending_diseases.append({
                    'disease': disease,
                    'total_cases': total_cases,
                    'recent_cases': recent_cases,
                    'recent_rate': round(recent_rate, 1),
                    'trend_status': 'Emerging' if recent_rate > 50 else 'Stable' if recent_rate > 20 else 'Declining'
                })
        
        return sorted(trending_diseases, key=lambda x: x['recent_rate'], reverse=True)[:10]
    
    def _categorize_disease_risk(self, severity_score: float) -> str:
        """Categorize disease risk based on severity score"""
        if severity_score >= 3.5:
            return 'Critical Risk'
        elif severity_score >= 2.5:
            return 'High Risk'
        elif severity_score >= 1.5:
            return 'Medium Risk'
        else:
            return 'Low Risk'
    
    def _get_recommended_action(self, disease: str, risk_level: str) -> str:
        """Get recommended action based on disease and risk level"""
        if risk_level in ['Very High', 'High']:
            return f"Immediate attention required. Increase {disease} screening and prevention programs."
        elif risk_level == 'Medium':
            return f"Monitor {disease} trends closely. Consider preventive measures."
        else:
            return f"Maintain current {disease} monitoring protocols."
    
    def _empty_disease_analysis(self) -> Dict[str, Any]:
        """Return empty disease analysis structure"""
        return {
            'disease_distribution': {},
            'categorized_diseases': {},
            'geographic_patterns': [],
            'age_patterns': {},
            'severity_correlation': [],
            'risk_assessment': [],
            'trending_diseases': [],
            'total_unique_diseases': 0,
            'analysis_timestamp': datetime.now().isoformat()
        }

class ComprehensiveMLEngine:
    """Main ML engine combining visit and disease analysis"""
    
    def __init__(self):
        self.visit_analyzer = RealTimePatientAnalyzer()
        self.disease_analyzer = RealTimeDiseaseAnalyzer()
        self.last_full_analysis = None
        
    def generate_comprehensive_insights(self, patients: List) -> Dict[str, Any]:
        """Generate comprehensive ML insights from real patient data"""
        try:
            # Analyze visit patterns
            visit_insights = self.visit_analyzer.analyze_visit_patterns(patients)
            
            # Analyze disease patterns
            disease_insights = self.disease_analyzer.analyze_disease_patterns(patients)
            
            # Generate integrated insights
            integrated_insights = self._generate_integrated_insights(visit_insights, disease_insights, patients)
            
            self.last_full_analysis = datetime.now()
            
            return {
                'visit_patterns': visit_insights,
                'disease_patterns': disease_insights,
                'integrated_insights': integrated_insights,
                'data_summary': {
                    'total_patients': len(patients),
                    'analysis_timestamp': datetime.now().isoformat(),
                    'data_quality_score': self._calculate_data_quality_score(patients)
                }
            }
            
        except Exception as e:
            logging.error(f"Error in comprehensive ML analysis: {e}")
            return self._empty_comprehensive_analysis()
    
    def _generate_integrated_insights(self, visit_insights: Dict, disease_insights: Dict, patients: List) -> Dict[str, Any]:
        """Generate integrated insights combining visit and disease patterns"""
        # Hospital capacity planning
        next_week_predictions = visit_insights.get('daily_predictions', [])
        total_predicted_visits = sum(pred.get('predicted_visits', 0) for pred in next_week_predictions)
        
        # Disease severity planning
        severity_trends = visit_insights.get('severity_trends', [])
        critical_cases_trend = next(
            (trend for trend in severity_trends if trend.get('severity') == 'Critical'),
            {'total_cases': 0, 'trend_direction': 'Stable'}
        )
        
        # Resource allocation recommendations
        top_diseases = list(disease_insights.get('disease_distribution', {}).keys())[:5]
        geographic_hotspots = [loc['locality'] for loc in disease_insights.get('geographic_patterns', [])[:3]]
        
        return {
            'capacity_planning': {
                'predicted_weekly_visits': total_predicted_visits,
                'recommended_bed_capacity': max(20, int(total_predicted_visits * 0.3)),
                'staff_scaling_factor': round(total_predicted_visits / 50, 1),
                'critical_care_demand': critical_cases_trend.get('total_cases', 0)
            },
            'resource_allocation': {
                'focus_diseases': top_diseases,
                'priority_localities': geographic_hotspots,
                'specialist_requirements': self._determine_specialist_needs(top_diseases),
                'medication_stocking': self._recommend_medication_stocking(top_diseases)
            },
            'risk_alerts': {
                'high_risk_diseases': [
                    risk['disease'] for risk in disease_insights.get('risk_assessment', [])
                    if risk.get('risk_level') in ['Very High', 'High']
                ][:3],
                'trending_concerns': [
                    trend['disease'] for trend in disease_insights.get('trending_diseases', [])
                    if trend.get('trend_status') == 'Emerging'
                ][:3]
            }
        }
    
    def _determine_specialist_needs(self, top_diseases: List[str]) -> Dict[str, int]:
        """Determine specialist staffing needs based on disease patterns"""
        specialist_map = {
            'cardiologist': ['coronary artery disease', 'heart attack', 'stroke', 'hypertension'],
            'pulmonologist': ['copd', 'asthma', 'pneumonia'],
            'oncologist': ['cancer', 'lymphoma', 'leukemia'],
            'neurologist': ['dementia', 'alzheimer', 'stroke'],
            'psychiatrist': ['depression', 'anxiety', 'schizophrenia'],
            'gastroenterologist': ['appendicitis', 'cirrhosis'],
            'endocrinologist': ['diabetes', 'thyroid disorder'],
            'pediatrician': ['pediatric fever']
        }
        
        specialist_needs = defaultdict(int)
        for disease in top_diseases:
            for specialist, conditions in specialist_map.items():
                if any(condition in disease.lower() for condition in conditions):
                    specialist_needs[specialist] += 1
        
        return dict(specialist_needs)
    
    def _recommend_medication_stocking(self, top_diseases: List[str]) -> List[str]:
        """Recommend medication stocking based on disease patterns"""
        medication_map = {
            'coronary artery disease': ['aspirin', 'statins', 'beta-blockers'],
            'diabetes': ['insulin', 'metformin'],
            'hypertension': ['ace inhibitors', 'diuretics'],
            'depression': ['ssri antidepressants'],
            'copd': ['bronchodilators', 'corticosteroids'],
            'appendicitis': ['antibiotics', 'pain relievers'],
            'thyroid disorder': ['levothyroxine'],
            'pediatric fever': ['acetaminophen', 'ibuprofen']
        }
        
        recommended_medications = set()
        for disease in top_diseases:
            for condition, medications in medication_map.items():
                if condition in disease.lower():
                    recommended_medications.update(medications)
        
        return list(recommended_medications)[:10]
    
    def _calculate_data_quality_score(self, patients: List) -> float:
        """Calculate data quality score based on completeness"""
        if not patients:
            return 0.0
        
        complete_records = 0
        for patient in patients:
            score = 0
            if hasattr(patient, 'admission_date') and patient.admission_date:
                score += 0.3
            if hasattr(patient, 'medical_history') and patient.medical_history:
                score += 0.3
            if hasattr(patient, 'locality') and patient.locality:
                score += 0.2
            if hasattr(patient, 'age') and patient.age > 0:
                score += 0.2
            
            complete_records += score
        
        return round((complete_records / len(patients)) * 100, 1)
    
    def _empty_comprehensive_analysis(self) -> Dict[str, Any]:
        """Return empty comprehensive analysis structure"""
        return {
            'visit_patterns': {},
            'disease_patterns': {},
            'integrated_insights': {},
            'data_summary': {
                'total_patients': 0,
                'analysis_timestamp': datetime.now().isoformat(),
                'data_quality_score': 0.0
            }
        }