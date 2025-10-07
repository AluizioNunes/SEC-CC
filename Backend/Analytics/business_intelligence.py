"""
Business Intelligence Service
Orchestrates all analytics services for comprehensive business intelligence
"""
import asyncio
import time
from typing import Dict, Any, List, Optional

from .analytics_service import ultra_analytics_service
from .ml import initialize_ml_predictions, ml_predictions
from .realtime import initialize_realtime_reporting, realtime_reporting
from .bi import bi_dashboard_service
from ..Redis.client import get_redis_client


class BusinessIntelligenceService:
    """Orchestrates all business intelligence services"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.bi_prefix = "business_intelligence"
        self.is_initialized = False

    async def initialize_services(self) -> bool:
        """Initialize all business intelligence services"""
        try:
            if self.is_initialized:
                return True

            # Initialize ML predictions service
            if ml_predictions is None:
                await initialize_ml_predictions(ultra_analytics_service)

            # Initialize real-time reporting service
            if realtime_reporting is None:
                await initialize_realtime_reporting(ultra_analytics_service)

            # Mark as initialized
            self.is_initialized = True

            # Start background tasks
            asyncio.create_task(self.start_background_processing())

            return True

        except Exception as e:
            print(f"Business intelligence service initialization error: {e}")
            return False

    async def start_background_processing(self):
        """Start background processing tasks"""
        try:
            # Start dashboard updates
            asyncio.create_task(self.update_dashboards_periodically())
            
            # Start business metrics calculation
            asyncio.create_task(self.calculate_business_metrics_periodically())
            
        except Exception as e:
            print(f"Background processing startup error: {e}")

    async def update_dashboards_periodically(self):
        """Periodically update dashboards"""
        try:
            while True:
                try:
                    # Update executive dashboard
                    await bi_dashboard_service.get_executive_dashboard()
                    
                    # Update operational dashboard
                    await bi_dashboard_service.get_operational_dashboard()
                    
                    # Wait 5 minutes before next update
                    await asyncio.sleep(300)
                    
                except Exception as e:
                    print(f"Dashboard update error: {e}")
                    await asyncio.sleep(60)  # Wait 1 minute before retrying

        except Exception as e:
            print(f"Dashboard update task error: {e}")

    async def calculate_business_metrics_periodically(self):
        """Periodically calculate business metrics"""
        try:
            while True:
                try:
                    # Calculate all registered metrics
                    for metric_id in ultra_analytics_service.registered_metrics.keys():
                        await ultra_analytics_service.calculate_business_metric(metric_id)
                    
                    # Wait 5 minutes before next calculation
                    await asyncio.sleep(300)
                    
                except Exception as e:
                    print(f"Business metrics calculation error: {e}")
                    await asyncio.sleep(60)  # Wait 1 minute before retrying

        except Exception as e:
            print(f"Business metrics calculation task error: {e}")

    async def get_comprehensive_business_intelligence(self) -> Dict[str, Any]:
        """Get comprehensive business intelligence data"""
        try:
            # Ensure services are initialized
            await self.initialize_services()

            # Get ML statistics if service is available
            ml_stats = {"status": "not_initialized"}
            if ml_predictions:
                ml_stats = await ml_predictions.get_ml_statistics()

            # Get reporting statistics if service is available
            reporting_stats = {"status": "not_initialized"}
            if realtime_reporting:
                reporting_stats = await realtime_reporting.get_reporting_statistics()

            return {
                "timestamp": time.time(),
                "business_dashboard": await bi_dashboard_service.get_executive_dashboard(),
                "operational_dashboard": await bi_dashboard_service.get_operational_dashboard(),
                "analytics_insights": await ultra_analytics_service.get_business_intelligence_dashboard(),
                "ml_statistics": ml_stats,
                "reporting_statistics": reporting_stats
            }

        except Exception as e:
            return {"error": str(e)}

    async def register_default_business_metrics(self):
        """Register default business metrics"""
        try:
            # Register key business metrics
            await ultra_analytics_service.register_business_metric(
                metric_id="user_engagement",
                name="User Engagement",
                description="Overall user engagement score",
                calculation_type="average",
                data_source="user_activity",
                refresh_interval=300,
                target_value=85.0,
                threshold_warning=70.0,
                threshold_critical=50.0
            )

            await ultra_analytics_service.register_business_metric(
                metric_id="revenue_growth",
                name="Revenue Growth",
                description="Monthly revenue growth percentage",
                calculation_type="percentage",
                data_source="revenue",
                refresh_interval=3600,
                target_value=15.0,
                threshold_warning=5.0,
                threshold_critical=0.0
            )

            await ultra_analytics_service.register_business_metric(
                metric_id="system_performance",
                name="System Performance",
                description="Overall system performance score",
                calculation_type="average",
                data_source="system_performance",
                refresh_interval=60,
                target_value=95.0,
                threshold_warning=80.0,
                threshold_critical=60.0
            )

            await ultra_analytics_service.register_business_metric(
                metric_id="customer_satisfaction",
                name="Customer Satisfaction",
                description="Customer satisfaction score",
                calculation_type="average",
                data_source="user_activity",  # Would be actual survey data in production
                refresh_interval=86400,  # Daily
                target_value=90.0,
                threshold_warning=75.0,
                threshold_critical=60.0
            )

            return True

        except Exception as e:
            print(f"Default business metrics registration error: {e}")
            return False

    async def get_business_intelligence_status(self) -> Dict[str, Any]:
        """Get business intelligence service status"""
        try:
            # Get ML statistics if service is available
            ml_stats = {"status": "not_initialized"}
            if ml_predictions:
                ml_stats = await ml_predictions.get_ml_statistics()

            # Get reporting statistics if service is available
            reporting_stats = {"status": "not_initialized"}
            if realtime_reporting:
                reporting_stats = await realtime_reporting.get_reporting_statistics()

            return {
                "status": "operational" if self.is_initialized else "initializing",
                "services": {
                    "analytics": "operational",
                    "ml_predictions": "operational" if ml_predictions else "not_initialized",
                    "realtime_reporting": "operational" if realtime_reporting else "not_initialized",
                    "dashboard_service": "operational"
                },
                "statistics": {
                    "registered_metrics": len(ultra_analytics_service.registered_metrics),
                    "calculated_metrics": ultra_analytics_service.stats.get("metrics_calculated", 0),
                    "generated_insights": ultra_analytics_service.stats.get("insights_generated", 0),
                    "predictions_made": ultra_analytics_service.stats.get("predictions_made", 0),
                    "ml_stats": ml_stats,
                    "reporting_stats": reporting_stats
                },
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": str(e)}


# Global business intelligence service instance
business_intelligence_service = BusinessIntelligenceService()