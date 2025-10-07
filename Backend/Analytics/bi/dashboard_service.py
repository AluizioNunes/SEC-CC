"""
Business Intelligence Dashboard Service
Advanced dashboard and visualization service for business metrics
"""
import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from ..analytics_service import ultra_analytics_service
from ..ml import ml_predictions
from ..realtime import realtime_reporting


class DashboardType(Enum):
    """Dashboard type enumeration"""
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    CUSTOM = "custom"


class VisualizationType(Enum):
    """Visualization type enumeration"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    GAUGE = "gauge"
    TABLE = "table"
    KPI_CARD = "kpi_card"
    HEATMAP = "heatmap"
    SCATTER_PLOT = "scatter_plot"


@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    widget_id: str
    title: str
    description: str
    visualization_type: VisualizationType
    data_source: str
    refresh_interval: int
    size: str  # "small", "medium", "large"
    position: Dict[str, int]  # x, y coordinates
    config: Dict[str, Any]  # Additional configuration


@dataclass
class BusinessDashboard:
    """Business dashboard configuration"""
    dashboard_id: str
    name: str
    description: str
    dashboard_type: DashboardType
    widgets: List[DashboardWidget]
    owner: str
    is_public: bool
    created_at: float
    updated_at: float


class BusinessIntelligenceDashboardService:
    """Business intelligence dashboard service"""

    def __init__(self):
        self.dashboards: Dict[str, BusinessDashboard] = {}
        self.widgets: Dict[str, DashboardWidget] = {}
        self.dashboard_prefix = "bi_dashboard"

    async def create_dashboard(
        self,
        name: str,
        description: str,
        dashboard_type: DashboardType,
        owner: str,
        is_public: bool = False
    ) -> str:
        """Create a new business dashboard"""
        try:
            dashboard_id = f"dashboard_{int(time.time() * 1000)}"

            dashboard = BusinessDashboard(
                dashboard_id=dashboard_id,
                name=name,
                description=description,
                dashboard_type=dashboard_type,
                widgets=[],
                owner=owner,
                is_public=is_public,
                created_at=time.time(),
                updated_at=time.time()
            )

            self.dashboards[dashboard_id] = dashboard
            return dashboard_id

        except Exception as e:
            print(f"Dashboard creation error: {e}")
            return ""

    async def add_widget_to_dashboard(
        self,
        dashboard_id: str,
        title: str,
        description: str,
        visualization_type: VisualizationType,
        data_source: str,
        refresh_interval: int = 300,
        size: str = "medium",
        position: Optional[Dict[str, int]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add widget to dashboard"""
        try:
            if dashboard_id not in self.dashboards:
                return ""

            widget_id = f"widget_{int(time.time() * 1000)}"

            if position is None:
                position = {"x": 0, "y": 0}

            if config is None:
                config = {}

            widget = DashboardWidget(
                widget_id=widget_id,
                title=title,
                description=description,
                visualization_type=visualization_type,
                data_source=data_source,
                refresh_interval=refresh_interval,
                size=size,
                position=position,
                config=config
            )

            self.widgets[widget_id] = widget

            # Add widget to dashboard
            dashboard = self.dashboards[dashboard_id]
            dashboard.widgets.append(widget)
            dashboard.updated_at = time.time()

            return widget_id

        except Exception as e:
            print(f"Widget addition error: {e}")
            return ""

    async def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get dashboard data with all widget information"""
        try:
            if dashboard_id not in self.dashboards:
                return {"error": "Dashboard not found"}

            dashboard = self.dashboards[dashboard_id]
            widget_data = []

            for widget in dashboard.widgets:
                data = await self.get_widget_data(widget)
                widget_data.append({
                    "widget_id": widget.widget_id,
                    "title": widget.title,
                    "description": widget.description,
                    "visualization_type": widget.visualization_type.value,
                    "data": data,
                    "refresh_interval": widget.refresh_interval,
                    "size": widget.size,
                    "position": widget.position
                })

            return {
                "dashboard_id": dashboard.dashboard_id,
                "name": dashboard.name,
                "description": dashboard.description,
                "dashboard_type": dashboard.dashboard_type.value,
                "widgets": widget_data,
                "owner": dashboard.owner,
                "is_public": dashboard.is_public,
                "created_at": dashboard.created_at,
                "updated_at": dashboard.updated_at
            }

        except Exception as e:
            return {"error": str(e)}

    async def get_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for specific widget"""
        try:
            data_source = widget.data_source

            # Handle different data sources
            if data_source == "business_metrics":
                return await self.get_business_metrics_data()
            elif data_source == "ml_predictions":
                return await self.get_ml_predictions_data()
            elif data_source == "realtime_reports":
                return await self.get_realtime_reports_data()
            elif data_source == "kpi_summary":
                return await self.get_kpi_summary_data()
            elif data_source == "alerts":
                return await self.get_alerts_data()
            else:
                return await self.get_custom_data(data_source)

        except Exception as e:
            return {"error": str(e)}

    async def get_business_metrics_data(self) -> Dict[str, Any]:
        """Get business metrics data"""
        try:
            # Get data from analytics service
            dashboard_data = await ultra_analytics_service.get_business_intelligence_dashboard()
            return {
                "type": "business_metrics",
                "data": dashboard_data.get("real_time_metrics", {}),
                "timestamp": time.time()
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_ml_predictions_data(self) -> Dict[str, Any]:
        """Get machine learning predictions data"""
        try:
            # This would connect to ML service in production
            return {
                "type": "ml_predictions",
                "data": {
                    "status": "operational",
                    "models_trained": 5,
                    "predictions_made": ultra_analytics_service.stats.get("predictions_made", 0)
                },
                "timestamp": time.time()
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_realtime_reports_data(self) -> Dict[str, Any]:
        """Get real-time reports data"""
        try:
            # This would connect to real-time reporting service in production
            return {
                "type": "realtime_reports",
                "data": {
                    "status": "operational",
                    "reports_generated": ultra_analytics_service.stats.get("insights_generated", 0)
                },
                "timestamp": time.time()
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_kpi_summary_data(self) -> Dict[str, Any]:
        """Get KPI summary data"""
        try:
            kpi_data = await ultra_analytics_service.get_kpi_summary()
            return {
                "type": "kpi_summary",
                "data": kpi_data,
                "timestamp": time.time()
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_alerts_data(self) -> Dict[str, Any]:
        """Get alerts data"""
        try:
            alerts = await ultra_analytics_service.get_business_alerts()
            return {
                "type": "alerts",
                "data": {
                    "alerts": alerts,
                    "total_alerts": len(alerts),
                    "critical_alerts": len([a for a in alerts if a.get("severity") == "critical"])
                },
                "timestamp": time.time()
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_custom_data(self, data_source: str) -> Dict[str, Any]:
        """Get custom data from specified source"""
        try:
            # This would handle custom data sources
            return {
                "type": "custom",
                "data_source": data_source,
                "data": {"message": f"Data from {data_source}"},
                "timestamp": time.time()
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_executive_dashboard(self) -> Dict[str, Any]:
        """Get executive dashboard with key business metrics"""
        try:
            # Create executive dashboard if it doesn't exist
            dashboard_id = None
            for dash_id, dashboard in self.dashboards.items():
                if dashboard.dashboard_type == DashboardType.EXECUTIVE:
                    dashboard_id = dash_id
                    break

            if not dashboard_id:
                dashboard_id = await self.create_dashboard(
                    name="Executive Dashboard",
                    description="High-level business overview for executives",
                    dashboard_type=DashboardType.EXECUTIVE,
                    owner="system"
                )

                # Add key widgets
                await self.add_widget_to_dashboard(
                    dashboard_id=dashboard_id,
                    title="KPI Summary",
                    description="Key performance indicators overview",
                    visualization_type=VisualizationType.KPI_CARD,
                    data_source="kpi_summary",
                    size="large",
                    position={"x": 0, "y": 0}
                )

                await self.add_widget_to_dashboard(
                    dashboard_id=dashboard_id,
                    title="Business Alerts",
                    description="Critical business alerts and notifications",
                    visualization_type=VisualizationType.TABLE,
                    data_source="alerts",
                    size="medium",
                    position={"x": 2, "y": 0}
                )

                await self.add_widget_to_dashboard(
                    dashboard_id=dashboard_id,
                    title="Business Metrics",
                    description="Real-time business metrics",
                    visualization_type=VisualizationType.LINE_CHART,
                    data_source="business_metrics",
                    size="large",
                    position={"x": 0, "y": 1}
                )

            # Get dashboard data
            return await self.get_dashboard_data(dashboard_id)

        except Exception as e:
            return {"error": str(e)}

    async def get_operational_dashboard(self) -> Dict[str, Any]:
        """Get operational dashboard with detailed metrics"""
        try:
            # Create operational dashboard if it doesn't exist
            dashboard_id = None
            for dash_id, dashboard in self.dashboards.items():
                if dashboard.dashboard_type == DashboardType.OPERATIONAL:
                    dashboard_id = dash_id
                    break

            if not dashboard_id:
                dashboard_id = await self.create_dashboard(
                    name="Operational Dashboard",
                    description="Detailed operational metrics and performance",
                    dashboard_type=DashboardType.OPERATIONAL,
                    owner="system"
                )

                # Add operational widgets
                await self.add_widget_to_dashboard(
                    dashboard_id=dashboard_id,
                    title="ML Predictions",
                    description="Machine learning model predictions",
                    visualization_type=VisualizationType.LINE_CHART,
                    data_source="ml_predictions",
                    size="medium",
                    position={"x": 0, "y": 0}
                )

                await self.add_widget_to_dashboard(
                    dashboard_id=dashboard_id,
                    title="Real-time Reports",
                    description="Current real-time reporting status",
                    visualization_type=VisualizationType.BAR_CHART,
                    data_source="realtime_reports",
                    size="medium",
                    position={"x": 1, "y": 0}
                )

                await self.add_widget_to_dashboard(
                    dashboard_id=dashboard_id,
                    title="Detailed Metrics",
                    description="Detailed business metrics breakdown",
                    visualization_type=VisualizationType.TABLE,
                    data_source="business_metrics",
                    size="large",
                    position={"x": 0, "y": 1}
                )

            # Get dashboard data
            return await self.get_dashboard_data(dashboard_id)

        except Exception as e:
            return {"error": str(e)}


# Global business intelligence dashboard service instance
bi_dashboard_service = BusinessIntelligenceDashboardService()