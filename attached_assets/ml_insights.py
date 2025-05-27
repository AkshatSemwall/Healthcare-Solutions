"""
ML Insights Module - Integrate machine learning predictions
"""
import logging
from ml.visit_forecast import visit_forecast_model
from ml.disease_predictor import disease_prediction_model

logger = logging.getLogger(__name__)

class MLInsights:
    """Combine insights from multiple ML models"""
    
    @staticmethod
    def get_predictions():
        """Get all ML predictions in a single response"""
        logger.debug("Generating ML insights")
        
        try:
            # Get visit predictions
            next_day_visits = visit_forecast_model.predict_next_day()
            visit_trends = visit_forecast_model.get_recent_trends(days=14)
            
            # Get disease predictions
            trending_diseases = disease_prediction_model.predict_trending_diseases(top_n=5)
            disease_distribution = disease_prediction_model.get_disease_distribution()
            
            insights = {
                'visit_predictions': {
                    'next_day_visits': next_day_visits,
                    'trends': visit_trends
                },
                'disease_predictions': {
                    'trending_diseases': trending_diseases,
                    'distribution': disease_distribution
                }
            }
            
            logger.info("Successfully generated ML insights")
            return insights
        except Exception as e:
            logger.error(f"Error generating ML insights: {str(e)}")
            return {
                'visit_predictions': {
                    'next_day_visits': 0,
                    'trends': {'dates': [], 'actual_visits': [], 'trend_line': []}
                },
                'disease_predictions': {
                    'trending_diseases': [],
                    'distribution': {'diseases': [], 'counts': []}
                }
            }


# Create singleton instance
ml_insights = MLInsights()