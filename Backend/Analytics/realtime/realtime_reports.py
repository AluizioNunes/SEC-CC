"""
Real-Time Reporting Service
Advanced real-time reporting with live dashboards and streaming analytics
"""
import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from ...Redis.client import get_redis_client
from ..analytics_service import UltraAnalyticsService, AnalyticsScope


class ReportType(Enum):
    """Report type enumeration"""
    DASHBOARD = "dashboard"
    ALERT = "alert"
    SUMMARY = "summary"
    TREND = "trend"


class ReportFrequency(Enum):
    """Report frequency enumeration"""
    REAL_TIME = "real_time"  # Every second
    NEAR_REAL_TIME = "near_real_time"  # Every 5 seconds
    FREQUENT = "frequent"  # Every 30 seconds
    PERIODIC = "periodic"  # Every minute


@dataclass
class ReportDefinition:
    """Report definition"""
    report_id: str
    name: str
    description: str
    report_type: ReportType
    frequency: ReportFrequency
    metrics: List[str]  # List of metric IDs to include
    filters: Optional[Dict[str, Any]] = None
    recipients: Optional[List[str]] = None  # Email addresses or webhook URLs
    created_at: float = time.time()


@dataclass
class ReportData:
    """Report data container"""
    report_id: str
    data: Dict[str, Any]
    generated_at: float
    next_generation: float


class RealTimeReportingService:
    """Advanced real-time reporting service"""

    def __init__(self, analytics_service: UltraAnalyticsService):
        self.redis_client = get_redis_client()
        self.analytics_service = analytics_service
        self.reporting_prefix = "realtime_reporting"

        # Report definitions
        self.report_definitions: Dict[str, ReportDefinition] = {}

        # Active reports
        self.active_reports: Dict[str, ReportData] = {}

        # Reporting statistics
        self.stats = {
            "reports_generated": 0,
            "reports_scheduled": 0,
            "alerts_sent": 0,
            "errors": 0
        }

        # Start report generation tasks
        asyncio.create_task(self.start_report_generation())

    async def create_report_definition(
        self,
        name: str,
        description: str,
        report_type: ReportType,
        frequency: ReportFrequency,
        metrics: List[str],
        filters: Optional[Dict[str, Any]] = None,
        recipients: Optional[List[str]] = None
    ) -> str:
        """Create report definition"""
        try:
            report_id = f"report_{int(time.time() * 1000)}"

            report_def = ReportDefinition(
                report_id=report_id,
                name=name,
                description=description,
                report_type=report_type,
                frequency=frequency,
                metrics=metrics,
                filters=filters,
                recipients=recipients
            )

            # Store report definition in Redis
            await self.redis_client.setex(
                f"{self.reporting_prefix}:definition:{report_id}",
                86400 * 30,  # 30 days
                json.dumps(asdict(report_def), default=str)
            )

            # Add to local cache
            self.report_definitions[report_id] = report_def

            # Schedule report generation
            asyncio.create_task(self.schedule_report_generation(report_id))

            self.stats["reports_scheduled"] += 1

            return report_id

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Report definition creation error: {e}")
            raise

    async def generate_report(self, report_id: str) -> ReportData:
        """Generate report data"""
        try:
            # Get report definition
            report_def = self.report_definitions.get(report_id)
            if not report_def:
                # Try to get from Redis
                report_data = await self.redis_client.get(f"{self.reporting_prefix}:definition:{report_id}")
                if not report_data:
                    raise ValueError(f"Report definition not found: {report_id}")
                report_def = ReportDefinition(**json.loads(report_data))
                self.report_definitions[report_id] = report_def

            # Generate report data based on type
            if report_def.report_type == ReportType.DASHBOARD:
                report_content = await self.generate_dashboard_report(report_def)
            elif report_def.report_type == ReportType.ALERT:
                report_content = await self.generate_alert_report(report_def)
            elif report_def.report_type == ReportType.SUMMARY:
                report_content = await self.generate_summary_report(report_def)
            elif report_def.report_type == ReportType.TREND:
                report_content = await self.generate_trend_report(report_def)
            else:
                raise ValueError(f"Unsupported report type: {report_def.report_type}")

            # Create report data
            report_data = ReportData(
                report_id=report_id,
                data=report_content,
                generated_at=time.time(),
                next_generation=self.calculate_next_generation_time(report_def.frequency)
            )

            # Store in Redis
            await self.redis_client.setex(
                f"{self.reporting_prefix}:data:{report_id}",
                3600,  # 1 hour
                json.dumps(asdict(report_data), default=str)
            )

            # Update active reports
            self.active_reports[report_id] = report_data

            self.stats["reports_generated"] += 1

            return report_data

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Report generation error: {e}")
            raise

    async def generate_dashboard_report(self, report_def: ReportDefinition) -> Dict[str, Any]:
        """Generate dashboard report"""
        try:
            metrics_data = {}
            
            # Get data for each metric
            for metric_id in report_def.metrics:
                metric_result = await self.analytics_service.calculate_business_metric(metric_id)
                if "error" not in metric_result:
                    metrics_data[metric_id] = metric_result

            return {
                "report_type": "dashboard",
                "title": report_def.name,
                "description": report_def.description,
                "metrics": metrics_data,
                "timestamp": time.time(),
                "generated_at": time.time()
            }

        except Exception as e:
            print(f"Dashboard report generation error: {e}")
            return {"error": str(e)}

    async def generate_alert_report(self, report_def: ReportDefinition) -> Dict[str, Any]:
        """Generate alert report"""
        try:
            alerts = []
            
            # Check each metric for threshold violations
            for metric_id in report_def.metrics:
                metric_result = await self.analytics_service.calculate_business_metric(metric_id)
                if "error" not in metric_result:
                    # Get metric definition to check thresholds
                    metric = self.analytics_service.registered_metrics.get(metric_id)
                    if metric and "value" in metric_result:
                        value = metric_result["value"]
                        
                        # Check critical threshold
                        if metric.threshold_critical and value > metric.threshold_critical:
                            alerts.append({
                                "type": "critical",
                                "metric_id": metric_id,
                                "metric_name": metric.name,
                                "value": value,
                                "threshold": metric.threshold_critical,
                                "message": f"{metric.name} exceeded critical threshold of {metric.threshold_critical}"
                            })
                        
                        # Check warning threshold
                        elif metric.threshold_warning and value > metric.threshold_warning:
                            alerts.append({
                                "type": "warning",
                                "metric_id": metric_id,
                                "metric_name": metric.name,
                                "value": value,
                                "threshold": metric.threshold_warning,
                                "message": f"{metric.name} exceeded warning threshold of {metric.threshold_warning}"
                            })

            return {
                "report_type": "alert",
                "title": report_def.name,
                "description": report_def.description,
                "alerts": alerts,
                "timestamp": time.time(),
                "generated_at": time.time()
            }

        except Exception as e:
            print(f"Alert report generation error: {e}")
            return {"error": str(e)}

    async def generate_summary_report(self, report_def: ReportDefinition) -> Dict[str, Any]:
        """Generate summary report"""
        try:
            summary_data = {}
            
            # Get summary data for each metric
            for metric_id in report_def.metrics:
                metric_result = await self.analytics_service.calculate_business_metric(metric_id)
                if "error" not in metric_result and "value" in metric_result:
                    metric = self.analytics_service.registered_metrics.get(metric_id)
                    if metric:
                        summary_data[metric.name] = {
                            "value": metric_result["value"],
                            "data_source": metric_result.get("data_source", "unknown"),
                            "calculated_at": metric_result.get("calculated_at", time.time())
                        }

            # Calculate overall health
            total_metrics = len(summary_data)
            healthy_metrics = sum(1 for data in summary_data.values() 
                                if data.get("value", 0) > 0)  # Simplified health check
            
            overall_health = (healthy_metrics / total_metrics * 100) if total_metrics > 0 else 0

            return {
                "report_type": "summary",
                "title": report_def.name,
                "description": report_def.description,
                "summary": summary_data,
                "overall_health": round(overall_health, 2),
                "total_metrics": total_metrics,
                "healthy_metrics": healthy_metrics,
                "timestamp": time.time(),
                "generated_at": time.time()
            }

        except Exception as e:
            print(f"Summary report generation error: {e}")
            return {"error": str(e)}

    async def generate_trend_report(self, report_def: ReportDefinition) -> Dict[str, Any]:
        """Generate trend report"""
        try:
            trend_data = {}
            
            # Get trend data for each metric
            for metric_id in report_def.metrics:
                # Get historical data
                metric_history = self.analytics_service.metric_values.get(metric_id, [])
                
                if len(metric_history) >= 2:
                    # Calculate trend (simple difference between last two values)
                    last_value = metric_history[-1][1]
                    previous_value = metric_history[-2][1]
                    trend = last_value - previous_value
                    
                    metric = self.analytics_service.registered_metrics.get(metric_id)
                    if metric:
                        trend_data[metric.name] = {
                            "current_value": last_value,
                            "previous_value": previous_value,
                            "trend": trend,
                            "trend_percentage": round((trend / previous_value * 100) if previous_value != 0 else 0, 2),
                            "data_points": len(metric_history)
                        }

            return {
                "report_type": "trend",
                "title": report_def.name,
                "description": report_def.description,
                "trends": trend_data,
                "timestamp": time.time(),
                "generated_at": time.time()
            }

        except Exception as e:
            print(f"Trend report generation error: {e}")
            return {"error": str(e)}

    def calculate_next_generation_time(self, frequency: ReportFrequency) -> float:
        """Calculate next report generation time"""
        current_time = time.time()
        
        if frequency == ReportFrequency.REAL_TIME:
            return current_time + 1  # Every second
        elif frequency == ReportFrequency.NEAR_REAL_TIME:
            return current_time + 5  # Every 5 seconds
        elif frequency == ReportFrequency.FREQUENT:
            return current_time + 30  # Every 30 seconds
        else:  # PERIODIC
            return current_time + 60  # Every minute

    async def schedule_report_generation(self, report_id: str):
        """Schedule report generation based on frequency"""
        try:
            report_def = self.report_definitions.get(report_id)
            if not report_def:
                return

            while True:
                try:
                    # Generate report
                    await self.generate_report(report_id)
                    
                    # Wait until next generation time
                    next_time = self.calculate_next_generation_time(report_def.frequency)
                    current_time = time.time()
                    wait_time = max(0, next_time - current_time)
                    
                    await asyncio.sleep(wait_time)
                    
                except Exception as e:
                    print(f"Report scheduling error for {report_id}: {e}")
                    await asyncio.sleep(60)  # Wait 1 minute before retrying

        except Exception as e:
            print(f"Report scheduling setup error: {e}")

    async def start_report_generation(self):
        """Start report generation for all scheduled reports"""
        try:
            # Get all report definitions from Redis
            pattern = f"{self.reporting_prefix}:definition:*"
            report_keys = await self.redis_client.keys(pattern)
            
            for report_key in report_keys:
                report_id = report_key.split(":")[-1]
                report_data = await self.redis_client.get(report_key)
                if report_data:
                    report_def = ReportDefinition(**json.loads(report_data))
                    self.report_definitions[report_id] = report_def
                    
                    # Schedule report generation
                    asyncio.create_task(self.schedule_report_generation(report_id))

        except Exception as e:
            print(f"Report generation startup error: {e}")

    async def get_report_data(self, report_id: str) -> Optional[ReportData]:
        """Get latest report data"""
        try:
            # Check active reports first
            if report_id in self.active_reports:
                return self.active_reports[report_id]
            
            # Get from Redis
            report_data = await self.redis_client.get(f"{self.reporting_prefix}:data:{report_id}")
            if report_data:
                return ReportData(**json.loads(report_data))
            
            return None

        except Exception as e:
            print(f"Report data retrieval error: {e}")
            return None

    async def get_reporting_statistics(self) -> Dict[str, Any]:
        """Get reporting service statistics"""
        try:
            return {
                "reporting_stats": self.stats.copy(),
                "active_reports": len(self.active_reports),
                "scheduled_reports": len(self.report_definitions),
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": str(e)}


# Global real-time reporting service instance
realtime_reporting = None


async def initialize_realtime_reporting(analytics_service: UltraAnalyticsService):
    """Initialize real-time reporting service"""
    global realtime_reporting
    if realtime_reporting is None:
        realtime_reporting = RealTimeReportingService(analytics_service)
    return realtime_reporting