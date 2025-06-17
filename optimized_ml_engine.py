import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple
import logging

class AdvancedVisitAnalyzer:
    """Advanced patient visit pattern analyzer with peak time detection"""
    
    def __init__(self):
        self.hourly_patterns = defaultdict(int)
        self.daily_patterns = defaultdict(int)
        self.monthly_patterns = defaultdict(int)
        
    def analyze_comprehensive_patterns(self, patients: List) -> Dict[str, Any]:
        """Comprehensive analysis of all patient visit patterns"""
        if not patients:
            return self._empty_analysis()
        
        visit_data = []
        locality_data = defaultdict(list)
        severity_timeline = defaultdict(list)
        
        for patient in patients:
            if hasattr(patient, 'admission_date') and patient.admission_date:
                try:
                    # Parse timestamp with hour information
                    timestamp_str = str(patient.timestamp) if hasattr(patient, 'timestamp') and patient.timestamp else str(patient.admission_date)
                    
                    if 'T' in timestamp_str:
                        date_obj = datetime.fromisoformat(timestamp_str.replace('T', ' ').split('+')[0])
                    else:
                        date_obj = datetime.strptime(timestamp_str.split()[0], '%Y-%m-%d')
                    
                    visit_data.append({
                        'datetime': date_obj,
                        'date': date_obj.strftime('%Y-%m-%d'),
                        'hour': date_obj.hour,
                        'day_of_week': date_obj.weekday(),
                        'month': date_obj.month,
                        'locality': getattr(patient, 'locality', 'Unknown'),
                        'severity': getattr(patient, 'condition_severity', 'Unknown'),
                        'disease': getattr(patient, 'medical_history', 'Unknown')
                    })
                    
                    locality_data[getattr(patient, 'locality', 'Unknown')].append(date_obj)
                    severity_timeline[getattr(patient, 'condition_severity', 'Unknown')].append(date_obj)
                    
                except Exception as e:
                    logging.warning(f"Could not parse date: {patient.admission_date}")
                    continue
        
        if not visit_data:
            return self._empty_analysis()
        
        # Peak time analysis
        peak_analysis = self._analyze_peak_times(visit_data)
        
        # Visit predictions with seasonality
        predictions = self._generate_advanced_predictions(visit_data)
        
        # Locality trends
        locality_trends = self._analyze_locality_trends(locality_data)
        
        # Severity patterns over time
        severity_trends = self._analyze_severity_trends(severity_timeline)
        
        # Capacity planning
        capacity_insights = self._generate_capacity_insights(visit_data, predictions)
        
        return {
            'peak_times': peak_analysis,
            'visit_predictions': predictions,
            'locality_trends': locality_trends,
            'severity_trends': severity_trends,
            'capacity_insights': capacity_insights,
            'data_summary': {
                'total_visits': len(visit_data),
                'date_range': f"{min(v['datetime'] for v in visit_data).strftime('%Y-%m-%d')} to {max(v['datetime'] for v in visit_data).strftime('%Y-%m-%d')}",
                'localities_covered': len(locality_data),
                'analysis_timestamp': datetime.now().isoformat()
            }
        }
    
    def _analyze_peak_times(self, visit_data: List[Dict]) -> Dict[str, Any]:
        """Analyze peak visit times by hour, day, and month"""
        hourly_visits = defaultdict(int)
        daily_visits = defaultdict(int)
        monthly_visits = defaultdict(int)
        weekday_visits = defaultdict(int)
        
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for visit in visit_data:
            hourly_visits[visit['hour']] += 1
            daily_visits[visit['date']] += 1
            monthly_visits[f"{visit['datetime'].year}-{visit['month']:02d}"] += 1
            weekday_visits[weekday_names[visit['day_of_week']]] += 1
        
        # Find peak times
        peak_hour = max(hourly_visits.items(), key=lambda x: x[1]) if hourly_visits else (0, 0)
        peak_day = max(weekday_visits.items(), key=lambda x: x[1]) if weekday_visits else ('Monday', 0)
        peak_month = max(monthly_visits.items(), key=lambda x: x[1]) if monthly_visits else ('2024-01', 0)
        
        # Calculate hourly distribution for 24-hour chart
        hourly_distribution = []
        for hour in range(24):
            count = hourly_visits.get(hour, 0)
            hourly_distribution.append({
                'hour': f"{hour:02d}:00",
                'visits': count,
                'percentage': round((count / len(visit_data)) * 100, 1) if visit_data else 0
            })
        
        # Weekly pattern
        weekly_pattern = []
        for day in weekday_names:
            count = weekday_visits.get(day, 0)
            weekly_pattern.append({
                'day': day,
                'visits': count,
                'percentage': round((count / len(visit_data)) * 100, 1) if visit_data else 0
            })
        
        # Monthly trends
        monthly_trends = []
        for month_key in sorted(monthly_visits.keys()):
            count = monthly_visits[month_key]
            monthly_trends.append({
                'month': month_key,
                'visits': count,
                'year_month': month_key
            })
        
        return {
            'peak_hour': f"{peak_hour[0]:02d}:00 ({peak_hour[1]} visits)",
            'peak_day': f"{peak_day[0]} ({peak_day[1]} visits)",
            'peak_month': f"{peak_month[0]} ({peak_month[1]} visits)",
            'hourly_distribution': hourly_distribution,
            'weekly_pattern': weekly_pattern,
            'monthly_trends': monthly_trends,
            'busiest_hours': sorted(hourly_visits.items(), key=lambda x: x[1], reverse=True)[:5],
            'rush_periods': self._identify_rush_periods(hourly_visits)
        }
    
    def _identify_rush_periods(self, hourly_visits: Dict[int, int]) -> List[Dict[str, Any]]:
        """Identify rush periods during the day"""
        if not hourly_visits:
            return []
        
        avg_visits = np.mean(list(hourly_visits.values()))
        rush_periods = []
        
        current_rush = None
        for hour in range(24):
            visits = hourly_visits.get(hour, 0)
            
            if visits > avg_visits * 1.2:  # 20% above average
                if current_rush is None:
                    current_rush = {'start_hour': hour, 'end_hour': hour, 'total_visits': visits}
                else:
                    current_rush['end_hour'] = hour
                    current_rush['total_visits'] += visits
            else:
                if current_rush is not None:
                    current_rush['period'] = f"{current_rush['start_hour']:02d}:00 - {current_rush['end_hour']:02d}:59"
                    current_rush['intensity'] = 'High' if current_rush['total_visits'] > avg_visits * 2 else 'Medium'
                    rush_periods.append(current_rush)
                    current_rush = None
        
        # Handle rush period that extends to end of day
        if current_rush is not None:
            current_rush['period'] = f"{current_rush['start_hour']:02d}:00 - {current_rush['end_hour']:02d}:59"
            current_rush['intensity'] = 'High' if current_rush['total_visits'] > avg_visits * 2 else 'Medium'
            rush_periods.append(current_rush)
        
        return rush_periods
    
    def _generate_advanced_predictions(self, visit_data: List[Dict]) -> Dict[str, Any]:
        """Generate advanced visit predictions with seasonal patterns"""
        if len(visit_data) < 7:
            return {'daily_forecast': [], 'weekly_forecast': [], 'confidence': 'Low'}
        
        # Group by date for time series
        daily_counts = defaultdict(int)
        for visit in visit_data:
            daily_counts[visit['date']] += 1
        
        # Sort dates and calculate moving averages
        sorted_dates = sorted(daily_counts.keys())
        visit_counts = [daily_counts[date] for date in sorted_dates]
        
        # Calculate trends
        if len(visit_counts) >= 14:
            recent_avg = np.mean(visit_counts[-7:])
            earlier_avg = np.mean(visit_counts[-14:-7])
            trend_factor = recent_avg / earlier_avg if earlier_avg > 0 else 1.0
        else:
            trend_factor = 1.0
            recent_avg = np.mean(visit_counts)
        
        # Weekday patterns
        weekday_multipliers = {}
        weekday_counts = defaultdict(list)
        for i, date_str in enumerate(sorted_dates):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            weekday = date_obj.weekday()
            weekday_counts[weekday].append(visit_counts[i])
        
        for weekday in range(7):
            if weekday in weekday_counts:
                weekday_multipliers[weekday] = np.mean(weekday_counts[weekday]) / recent_avg if recent_avg > 0 else 1.0
            else:
                weekday_multipliers[weekday] = 1.0
        
        # Generate predictions
        last_date = datetime.strptime(sorted_dates[-1], '%Y-%m-%d')
        daily_forecast = []
        weekly_forecast = []
        
        for i in range(1, 15):  # 14-day forecast
            future_date = last_date + timedelta(days=i)
            weekday = future_date.weekday()
            
            # Base prediction with trend and seasonality
            base_prediction = recent_avg * trend_factor * weekday_multipliers.get(weekday, 1.0)
            predicted_visits = max(1, int(round(base_prediction)))
            
            confidence = self._calculate_prediction_confidence(len(visit_data), weekday_counts.get(weekday, []))
            
            forecast_entry = {
                'date': future_date.strftime('%Y-%m-%d'),
                'day_name': future_date.strftime('%A'),
                'predicted_visits': predicted_visits,
                'confidence': confidence,
                'trend_factor': round(trend_factor, 2)
            }
            
            if i <= 7:
                weekly_forecast.append(forecast_entry)
            daily_forecast.append(forecast_entry)
        
        return {
            'daily_forecast': daily_forecast,
            'weekly_forecast': weekly_forecast,
            'trend_analysis': {
                'recent_avg': round(recent_avg, 1),
                'trend_factor': round(trend_factor, 2),
                'trend_direction': 'Increasing' if trend_factor > 1.05 else 'Decreasing' if trend_factor < 0.95 else 'Stable'
            },
            'confidence': self._overall_confidence(len(visit_data))
        }
    
    def _analyze_locality_trends(self, locality_data: Dict[str, List[datetime]]) -> List[Dict[str, Any]]:
        """Analyze visit trends by locality"""
        locality_trends = []
        
        for locality, dates in locality_data.items():
            if locality and locality.lower() != 'unknown' and len(dates) >= 2:
                total_visits = len(dates)
                
                # Calculate recent trend (last 30 days vs previous 30 days)
                cutoff_date = datetime.now() - timedelta(days=30)
                recent_visits = len([d for d in dates if d >= cutoff_date])
                
                # Calculate growth rate
                if len(dates) >= 4:
                    sorted_dates = sorted(dates)
                    mid_point = len(sorted_dates) // 2
                    recent_period = sorted_dates[mid_point:]
                    earlier_period = sorted_dates[:mid_point]
                    
                    recent_rate = len(recent_period) / 30 if recent_period else 0
                    earlier_rate = len(earlier_period) / 30 if earlier_period else 0
                    
                    growth_rate = ((recent_rate - earlier_rate) / earlier_rate * 100) if earlier_rate > 0 else 0
                else:
                    growth_rate = 0
                
                # Peak times for this locality
                hourly_dist = defaultdict(int)
                for date in dates:
                    hourly_dist[date.hour] += 1
                
                peak_hour = max(hourly_dist.items(), key=lambda x: x[1])[0] if hourly_dist else 0
                
                locality_trends.append({
                    'locality': locality.split(',')[0].strip(),  # Clean locality name
                    'total_visits': total_visits,
                    'recent_visits': recent_visits,
                    'growth_rate': round(growth_rate, 1),
                    'trend': 'Increasing' if growth_rate > 5 else 'Decreasing' if growth_rate < -5 else 'Stable',
                    'peak_hour': f"{peak_hour:02d}:00",
                    'avg_daily_visits': round(total_visits / max(1, (max(dates) - min(dates)).days), 1)
                })
        
        return sorted(locality_trends, key=lambda x: x['total_visits'], reverse=True)[:15]
    
    def _analyze_severity_trends(self, severity_timeline: Dict[str, List[datetime]]) -> List[Dict[str, Any]]:
        """Analyze severity trends over time"""
        severity_trends = []
        
        for severity, dates in severity_timeline.items():
            if severity and severity.lower() != 'unknown' and dates:
                total_cases = len(dates)
                
                # Recent trend analysis
                cutoff_date = datetime.now() - timedelta(days=30)
                recent_cases = len([d for d in dates if d >= cutoff_date])
                
                # Calculate urgency score
                urgency_weights = {'Critical': 4, 'High': 3, 'Moderate': 2, 'Mild': 1, 'Low': 1}
                urgency_score = urgency_weights.get(severity, 1)
                
                # Monthly distribution
                monthly_dist = defaultdict(int)
                for date in dates:
                    month_key = f"{date.year}-{date.month:02d}"
                    monthly_dist[month_key] += 1
                
                severity_trends.append({
                    'severity': severity,
                    'total_cases': total_cases,
                    'recent_cases': recent_cases,
                    'urgency_score': urgency_score,
                    'percentage_recent': round((recent_cases / total_cases) * 100, 1) if total_cases > 0 else 0,
                    'monthly_distribution': dict(sorted(monthly_dist.items())),
                    'trend_status': 'Alert' if recent_cases > total_cases * 0.4 and urgency_score >= 3 else 'Stable'
                })
        
        return sorted(severity_trends, key=lambda x: x['urgency_score'], reverse=True)
    
    def _generate_capacity_insights(self, visit_data: List[Dict], predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Generate hospital capacity planning insights"""
        if not visit_data:
            return {}
        
        avg_daily_visits = len(visit_data) / max(1, len(set(v['date'] for v in visit_data)))
        peak_day_visits = max(predictions.get('weekly_forecast', [{'predicted_visits': 0}]), key=lambda x: x['predicted_visits'])
        
        # Resource calculations
        estimated_peak_visits = peak_day_visits.get('predicted_visits', avg_daily_visits)
        
        return {
            'current_avg_daily': round(avg_daily_visits, 1),
            'predicted_peak_daily': estimated_peak_visits,
            'capacity_recommendations': {
                'beds_needed': max(20, int(estimated_peak_visits * 0.4)),
                'doctors_needed': max(3, int(estimated_peak_visits / 8)),
                'nurses_needed': max(5, int(estimated_peak_visits / 5)),
                'admin_staff_needed': max(2, int(estimated_peak_visits / 15))
            },
            'capacity_utilization': {
                'peak_utilization': min(100, round((estimated_peak_visits / max(50, estimated_peak_visits)) * 100, 1)),
                'avg_utilization': round((avg_daily_visits / max(30, avg_daily_visits)) * 100, 1)
            }
        }
    
    def _calculate_prediction_confidence(self, total_data_points: int, weekday_history: List[int]) -> str:
        """Calculate prediction confidence"""
        if total_data_points >= 100 and len(weekday_history) >= 8:
            return 'High'
        elif total_data_points >= 50 and len(weekday_history) >= 4:
            return 'Medium'
        else:
            return 'Low'
    
    def _overall_confidence(self, total_data_points: int) -> str:
        """Calculate overall prediction confidence"""
        if total_data_points >= 500:
            return 'Very High'
        elif total_data_points >= 200:
            return 'High'
        elif total_data_points >= 50:
            return 'Medium'
        else:
            return 'Low'
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'peak_times': {},
            'visit_predictions': {},
            'locality_trends': [],
            'severity_trends': [],
            'capacity_insights': {},
            'data_summary': {'total_visits': 0, 'date_range': 'N/A', 'localities_covered': 0}
        }

class EnhancedDiseaseAnalyzer:
    """Enhanced disease pattern analyzer with visual insights"""
    
    def __init__(self):
        self.disease_categories = {
            'cardiovascular': ['coronary artery disease', 'heart attack', 'stroke', 'hypertension'],
            'respiratory': ['copd', 'asthma', 'pneumonia'],
            'infectious': ['hepatitis', 'tuberculosis', 'covid', 'influenza'],
            'neurological': ['dementia', 'alzheimer', 'parkinson', 'stroke'],
            'oncological': ['cancer', 'lymphoma', 'leukemia', 'tumor'],
            'mental_health': ['depression', 'anxiety', 'schizophrenia', 'bipolar'],
            'gastrointestinal': ['appendicitis', 'cirrhosis', 'gastritis', 'ulcer', 'peptic ulcer'],
            'endocrine': ['diabetes', 'thyroid disorder', 'obesity'],
            'pediatric': ['pediatric fever', 'childhood asthma'],
            'maternal': ['childbirth', 'pregnancy']
        }
    
    def analyze_disease_patterns(self, patients: List) -> Dict[str, Any]:
        """Enhanced disease pattern analysis with visual data"""
        if not patients:
            return self._empty_disease_analysis()
        
        disease_data = []
        for patient in patients:
            if hasattr(patient, 'medical_history') and patient.medical_history:
                condition = str(patient.medical_history).lower().strip()
                if condition and condition not in ['nan', '', 'unknown']:
                    disease_data.append({
                        'disease': condition,
                        'patient_id': getattr(patient, 'patient_id', ''),
                        'age': getattr(patient, 'age', 0),
                        'gender': getattr(patient, 'gender', 'Unknown'),
                        'locality': getattr(patient, 'locality', 'Unknown'),
                        'severity': getattr(patient, 'condition_severity', 'Unknown'),
                        'admission_date': getattr(patient, 'admission_date', ''),
                        'bill_amount': getattr(patient, 'bill_amount', 0)
                    })
        
        if not disease_data:
            return self._empty_disease_analysis()
        
        # Core analysis
        disease_distribution = self._analyze_disease_distribution(disease_data)
        category_analysis = self._categorize_diseases(disease_data)
        geographic_patterns = self._analyze_geographic_patterns(disease_data)
        demographic_patterns = self._analyze_demographic_patterns(disease_data)
        severity_correlation = self._analyze_severity_correlation(disease_data)
        temporal_trends = self._analyze_temporal_trends(disease_data)
        
        return {
            'total_cases': len(disease_data),
            'unique_diseases': len(set(d['disease'] for d in disease_data)),
            'disease_distribution': disease_distribution,
            'category_analysis': category_analysis,
            'geographic_patterns': geographic_patterns,
            'demographic_patterns': demographic_patterns,
            'severity_correlation': severity_correlation,
            'temporal_trends': temporal_trends,
            'visual_data': self._prepare_visual_data(disease_data),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _analyze_disease_distribution(self, disease_data: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze overall disease distribution"""
        disease_counts = Counter(d['disease'] for d in disease_data)
        total_cases = len(disease_data)
        
        distribution = []
        for disease, count in disease_counts.most_common(20):
            prevalence = (count / total_cases) * 100
            
            # Calculate average cost
            disease_cases = [d for d in disease_data if d['disease'] == disease]
            avg_cost = np.mean([d['bill_amount'] for d in disease_cases if d['bill_amount'] > 0])
            
            # Risk assessment
            risk_level = self._assess_disease_risk(disease, count, total_cases)
            
            distribution.append({
                'disease': disease.title(),
                'cases': count,
                'prevalence_rate': round(prevalence, 2),
                'avg_cost': round(avg_cost, 2) if avg_cost > 0 else 0,
                'risk_level': risk_level,
                'trend_indicator': self._calculate_trend_indicator(disease, disease_cases)
            })
        
        return distribution
    
    def _categorize_diseases(self, disease_data: List[Dict]) -> Dict[str, Any]:
        """Categorize diseases by medical specialty"""
        category_counts = defaultdict(lambda: {'count': 0, 'diseases': set(), 'total_cost': 0})
        
        for data in disease_data:
            disease = data['disease']
            category = 'other'
            
            for cat, keywords in self.disease_categories.items():
                if any(keyword in disease for keyword in keywords):
                    category = cat
                    break
            
            category_counts[category]['count'] += 1
            category_counts[category]['diseases'].add(disease)
            category_counts[category]['total_cost'] += data['bill_amount']
        
        categorized = {}
        for category, data in category_counts.items():
            categorized[category] = {
                'case_count': data['count'],
                'unique_diseases': len(data['diseases']),
                'total_cost': round(data['total_cost'], 2),
                'avg_cost_per_case': round(data['total_cost'] / data['count'], 2) if data['count'] > 0 else 0,
                'percentage': round((data['count'] / len(disease_data)) * 100, 1)
            }
        
        return dict(sorted(categorized.items(), key=lambda x: x[1]['case_count'], reverse=True))
    
    def _analyze_geographic_patterns(self, disease_data: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze disease patterns by location"""
        locality_patterns = defaultdict(lambda: defaultdict(int))
        
        for data in disease_data:
            locality = data['locality'].split(',')[0].strip() if data['locality'] else 'Unknown'
            disease = data['disease']
            locality_patterns[locality][disease] += 1
        
        patterns = []
        for locality, diseases in locality_patterns.items():
            if locality.lower() != 'unknown':
                total_cases = sum(diseases.values())
                top_disease = max(diseases.items(), key=lambda x: x[1])
                
                patterns.append({
                    'locality': locality,
                    'total_cases': total_cases,
                    'primary_disease': top_disease[0].title(),
                    'primary_disease_cases': top_disease[1],
                    'disease_diversity': len(diseases),
                    'concentration_rate': round((top_disease[1] / total_cases) * 100, 1)
                })
        
        return sorted(patterns, key=lambda x: x['total_cases'], reverse=True)[:15]
    
    def _analyze_demographic_patterns(self, disease_data: List[Dict]) -> Dict[str, Any]:
        """Analyze disease patterns by demographics"""
        age_groups = {
            'Children (0-17)': (0, 17),
            'Young Adults (18-35)': (18, 35),
            'Middle-aged (36-60)': (36, 60),
            'Seniors (61+)': (61, 120)
        }
        
        age_analysis = {}
        gender_analysis = defaultdict(lambda: defaultdict(int))
        
        # Age group analysis
        for group_name, (min_age, max_age) in age_groups.items():
            group_diseases = defaultdict(int)
            group_data = [d for d in disease_data if min_age <= d['age'] <= max_age]
            
            for data in group_data:
                group_diseases[data['disease']] += 1
            
            if group_diseases:
                top_disease = max(group_diseases.items(), key=lambda x: x[1])
                age_analysis[group_name] = {
                    'total_cases': len(group_data),
                    'top_disease': top_disease[0].title(),
                    'top_disease_cases': top_disease[1],
                    'unique_diseases': len(group_diseases)
                }
        
        # Gender analysis
        for data in disease_data:
            gender_analysis[data['gender']][data['disease']] += 1
        
        gender_patterns = {}
        for gender, diseases in gender_analysis.items():
            if diseases:
                top_disease = max(diseases.items(), key=lambda x: x[1])
                gender_patterns[gender] = {
                    'total_cases': sum(diseases.values()),
                    'top_disease': top_disease[0].title(),
                    'top_disease_cases': top_disease[1],
                    'unique_diseases': len(diseases)
                }
        
        return {
            'age_groups': age_analysis,
            'gender_patterns': gender_patterns
        }
    
    def _analyze_severity_correlation(self, disease_data: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze correlation between diseases and severity"""
        disease_severity = defaultdict(lambda: defaultdict(int))
        
        for data in disease_data:
            disease_severity[data['disease']][data['severity']] += 1
        
        correlations = []
        severity_weights = {'Critical': 4, 'High': 3, 'Moderate': 2, 'Mild': 1, 'Low': 1}
        
        for disease, severities in disease_severity.items():
            total_cases = sum(severities.values())
            weighted_score = sum(severity_weights.get(sev, 1) * count for sev, count in severities.items())
            avg_severity = weighted_score / total_cases if total_cases > 0 else 1
            
            most_common_severity = max(severities.items(), key=lambda x: x[1])[0]
            
            correlations.append({
                'disease': disease.title(),
                'total_cases': total_cases,
                'avg_severity_score': round(avg_severity, 2),
                'most_common_severity': most_common_severity,
                'severity_distribution': dict(severities),
                'risk_category': self._categorize_severity_risk(avg_severity)
            })
        
        return sorted(correlations, key=lambda x: x['avg_severity_score'], reverse=True)[:15]
    
    def _analyze_temporal_trends(self, disease_data: List[Dict]) -> Dict[str, Any]:
        """Analyze disease trends over time"""
        monthly_trends = defaultdict(lambda: defaultdict(int))
        
        for data in disease_data:
            if data['admission_date']:
                try:
                    date_obj = datetime.strptime(data['admission_date'].split()[0], '%Y-%m-%d')
                    month_key = f"{date_obj.year}-{date_obj.month:02d}"
                    monthly_trends[month_key][data['disease']] += 1
                except:
                    continue
        
        trending_diseases = defaultdict(list)
        for month, diseases in monthly_trends.items():
            for disease, count in diseases.items():
                trending_diseases[disease].append({'month': month, 'count': count})
        
        trend_analysis = []
        for disease, monthly_data in trending_diseases.items():
            if len(monthly_data) >= 3:
                sorted_data = sorted(monthly_data, key=lambda x: x['month'])
                recent_avg = np.mean([d['count'] for d in sorted_data[-3:]])
                earlier_avg = np.mean([d['count'] for d in sorted_data[:3]])
                
                trend_direction = 'Increasing' if recent_avg > earlier_avg * 1.1 else 'Decreasing' if recent_avg < earlier_avg * 0.9 else 'Stable'
                
                trend_analysis.append({
                    'disease': disease.title(),
                    'trend_direction': trend_direction,
                    'recent_avg': round(recent_avg, 1),
                    'change_rate': round(((recent_avg - earlier_avg) / earlier_avg * 100), 1) if earlier_avg > 0 else 0
                })
        
        return {
            'monthly_trends': dict(monthly_trends),
            'trending_analysis': sorted(trend_analysis, key=lambda x: abs(x['change_rate']), reverse=True)[:10]
        }
    
    def _prepare_visual_data(self, disease_data: List[Dict]) -> Dict[str, Any]:
        """Prepare data optimized for visual charts"""
        disease_counts = Counter(d['disease'] for d in disease_data)
        
        # Top diseases for pie chart
        top_diseases = disease_counts.most_common(8)
        
        # Age distribution
        age_bins = defaultdict(int)
        for data in disease_data:
            age = data['age']
            if age <= 17:
                age_bins['0-17'] += 1
            elif age <= 35:
                age_bins['18-35'] += 1
            elif age <= 60:
                age_bins['36-60'] += 1
            else:
                age_bins['61+'] += 1
        
        # Severity distribution
        severity_counts = Counter(d['severity'] for d in disease_data)
        
        return {
            'disease_pie_chart': {
                'labels': [d[0].title() for d in top_diseases],
                'data': [d[1] for d in top_diseases]
            },
            'age_distribution': {
                'labels': list(age_bins.keys()),
                'data': list(age_bins.values())
            },
            'severity_distribution': {
                'labels': list(severity_counts.keys()),
                'data': list(severity_counts.values())
            }
        }
    
    def _assess_disease_risk(self, disease: str, count: int, total_cases: int) -> str:
        """Assess disease risk level"""
        prevalence = (count / total_cases) * 100
        
        # High-risk diseases
        high_risk_diseases = ['cancer', 'stroke', 'heart attack', 'cirrhosis']
        if any(keyword in disease for keyword in high_risk_diseases):
            return 'Critical' if prevalence >= 5 else 'High'
        
        if prevalence >= 15:
            return 'Very High'
        elif prevalence >= 10:
            return 'High' 
        elif prevalence >= 5:
            return 'Medium'
        else:
            return 'Low'
    
    def _calculate_trend_indicator(self, disease: str, disease_cases: List[Dict]) -> str:
        """Calculate trend indicator for disease"""
        if len(disease_cases) < 4:
            return 'Stable'
        
        # Simple trend based on case distribution
        total_cases = len(disease_cases)
        recent_cases = len([case for case in disease_cases if '2024' in str(case.get('admission_date', ''))])
        
        recent_rate = recent_cases / total_cases if total_cases > 0 else 0
        
        if recent_rate > 0.6:
            return 'Increasing'
        elif recent_rate < 0.3:
            return 'Decreasing'
        else:
            return 'Stable'
    
    def _categorize_severity_risk(self, severity_score: float) -> str:
        """Categorize severity risk"""
        if severity_score >= 3.5:
            return 'Critical Risk'
        elif severity_score >= 2.5:
            return 'High Risk'
        elif severity_score >= 1.5:
            return 'Medium Risk'
        else:
            return 'Low Risk'
    
    def _empty_disease_analysis(self) -> Dict[str, Any]:
        """Return empty disease analysis"""
        return {
            'total_cases': 0,
            'unique_diseases': 0,
            'disease_distribution': [],
            'category_analysis': {},
            'geographic_patterns': [],
            'demographic_patterns': {},
            'severity_correlation': [],
            'temporal_trends': {},
            'visual_data': {},
            'analysis_timestamp': datetime.now().isoformat()
        }

class OptimizedMLEngine:
    """Optimized ML engine for comprehensive hospital analytics"""
    
    def __init__(self):
        self.visit_analyzer = AdvancedVisitAnalyzer()
        self.disease_analyzer = EnhancedDiseaseAnalyzer()
    
    def generate_insights(self, patients: List) -> Dict[str, Any]:
        """Generate comprehensive optimized insights"""
        if not patients:
            return self._empty_insights()
        
        # Run analyses
        visit_insights = self.visit_analyzer.analyze_comprehensive_patterns(patients)
        disease_insights = self.disease_analyzer.analyze_disease_patterns(patients)
        
        # Generate integrated insights
        integrated_insights = self._generate_integrated_insights(visit_insights, disease_insights)
        
        return {
            'visit_analysis': visit_insights,
            'disease_analysis': disease_insights,
            'integrated_insights': integrated_insights,
            'summary': {
                'total_patients_analyzed': len(patients),
                'analysis_timestamp': datetime.now().isoformat(),
                'data_quality_score': self._calculate_data_quality(patients)
            }
        }
    
    def _generate_integrated_insights(self, visit_insights: Dict, disease_insights: Dict) -> Dict[str, Any]:
        """Generate integrated actionable insights"""
        # Resource planning
        capacity = visit_insights.get('capacity_insights', {})
        peak_times = visit_insights.get('peak_times', {})
        
        # Alert system
        high_risk_diseases = [d for d in disease_insights.get('disease_distribution', []) 
                             if d.get('risk_level') in ['Critical', 'Very High', 'High']]
        
        # Optimization recommendations
        rush_periods = peak_times.get('rush_periods', [])
        
        return {
            'resource_optimization': {
                'peak_staffing_hours': [period['period'] for period in rush_periods],
                'recommended_capacity': capacity.get('capacity_recommendations', {}),
                'utilization_alerts': capacity.get('capacity_utilization', {})
            },
            'medical_alerts': {
                'high_priority_diseases': [d['disease'] for d in high_risk_diseases[:5]],
                'trending_concerns': [t['disease'] for t in disease_insights.get('temporal_trends', {}).get('trending_analysis', [])[:3]]
            },
            'operational_insights': {
                'busiest_day': peak_times.get('peak_day', 'Monday'),
                'busiest_hour': peak_times.get('peak_hour', '09:00'),
                'top_localities': [l['locality'] for l in visit_insights.get('locality_trends', [])[:3]]
            }
        }
    
    def _calculate_data_quality(self, patients: List) -> float:
        """Calculate data quality score"""
        if not patients:
            return 0.0
        
        score = 0
        for patient in patients:
            patient_score = 0
            if hasattr(patient, 'admission_date') and patient.admission_date:
                patient_score += 0.25
            if hasattr(patient, 'medical_history') and patient.medical_history:
                patient_score += 0.25
            if hasattr(patient, 'locality') and patient.locality:
                patient_score += 0.25
            if hasattr(patient, 'age') and patient.age > 0:
                patient_score += 0.25
            score += patient_score
        
        return round((score / len(patients)) * 100, 1)
    
    def _empty_insights(self) -> Dict[str, Any]:
        """Return empty insights structure"""
        return {
            'visit_analysis': {},
            'disease_analysis': {},
            'integrated_insights': {},
            'summary': {
                'total_patients_analyzed': 0,
                'analysis_timestamp': datetime.now().isoformat(),
                'data_quality_score': 0.0
            }
        }