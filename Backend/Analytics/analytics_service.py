"""
Ultra Analytics Service - Business Intelligence Engine
Complete business intelligence system with predictive analytics
"""
import asyncio
import json
import time
import statistics
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from ..Redis.client import get_redis_client


class AnalyticsScope(Enum):
    """Analytics scope enumeration"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class BusinessMetric:
    """Business metric definition"""
    metric_id: str
    name: str
    description: str
    calculation_type: str
    data_source: str
    refresh_interval: int
    target_value: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None


@dataclass
class AnalyticsInsight:
    """Analytics insight"""
    insight_id: str
    metric_id: str
    scope: AnalyticsScope
    value: float
    trend: str
    confidence: float
    impact: str
    recommendation: str
    timestamp: float


class UltraAnalyticsService:
    """Ultra-advanced business intelligence and analytics engine"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.analytics_prefix = "ultra_analytics"

        # Business metrics registry
        self.registered_metrics: Dict[str, BusinessMetric] = {}
        self.metric_values: Dict[str, List[tuple]] = {}  # (timestamp, value)

        # Analytics statistics
        self.stats = {
            "metrics_calculated": 0,
            "insights_generated": 0,
            "predictions_made": 0,
            "anomalies_detected": 0,
            "errors": 0
        }

    async def register_business_metric(
        self,
        metric_id: str,
        name: str,
        description: str,
        calculation_type: str,
        data_source: str,
        refresh_interval: int = 300,
        target_value: Optional[float] = None,
        threshold_warning: Optional[float] = None,
        threshold_critical: Optional[float] = None
    ) -> bool:
        """Register business metric for tracking"""
        try:
            metric = BusinessMetric(
                metric_id=metric_id,
                name=name,
                description=description,
                calculation_type=calculation_type,
                data_source=data_source,
                refresh_interval=refresh_interval,
                target_value=target_value,
                threshold_warning=threshold_warning,
                threshold_critical=threshold_critical
            )

            # Store metric definition
            await self.redis_client.setex(
                f"{self.analytics_prefix}:metric:{metric_id}",
                86400 * 30,  # 30 days
                json.dumps(asdict(metric), default=str)
            )

            self.registered_metrics[metric_id] = metric
            return True

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Metric registration error: {e}")
            return False

    async def calculate_business_metric(self, metric_id: str) -> Dict[str, Any]:
        """Calculate business metric value"""
        try:
            metric = self.registered_metrics.get(metric_id)
            if not metric:
                return {"error": "Metric not found"}

            # Get calculation data based on data source
            raw_data = await self.get_metric_data(metric.data_source)

            # Calculate metric based on type
            calculated_value = await self.calculate_metric_value(metric, raw_data)

            # Store metric value with timestamp
            current_time = time.time()
            if metric_id not in self.metric_values:
                self.metric_values[metric_id] = []
            self.metric_values[metric_id].append((current_time, calculated_value))

            # Keep only recent values (last 1000 points)
            if len(self.metric_values[metric_id]) > 1000:
                self.metric_values[metric_id] = self.metric_values[metric_id][-1000:]

            # Store in Redis
            await self.redis_client.setex(
                f"{self.analytics_prefix}:metric_value:{metric_id}",
                metric.refresh_interval,
                json.dumps({
                    "value": calculated_value,
                    "calculated_at": current_time,
                    "data_points": len(raw_data)
                }, default=str)
            )

            self.stats["metrics_calculated"] += 1

            return {
                "metric_id": metric_id,
                "metric_name": metric.name,
                "value": calculated_value,
                "calculated_at": current_time,
                "status": "calculated",
                "data_source": metric.data_source
            }

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Metric calculation error: {e}")
            return {"error": str(e)}

    async def get_metric_data(self, data_source: str) -> List[Dict[str, Any]]:
        """Get data for metric calculation"""
        # This would connect to actual data sources in production
        # For demo, return simulated data

        if data_source == "user_activity":
            return await self.get_user_activity_data()
        elif data_source == "revenue":
            return await self.get_revenue_data()
        elif data_source == "system_performance":
            return await self.get_system_performance_data()
        else:
            return []

    async def get_user_activity_data(self) -> List[Dict[str, Any]]:
        """Get user activity data"""
        # Simulate user activity data
        return [
            {"user_id": f"user_{i}", "activity_type": "login", "timestamp": time.time() - (i * 3600)}
            for i in range(100)
        ]

    async def get_revenue_data(self) -> List[Dict[str, Any]]:
        """Get revenue data"""
        # Simulate revenue data
        return [
            {"amount": 100.0 + i * 10, "currency": "USD", "timestamp": time.time() - (i * 3600)}
            for i in range(50)
        ]

    async def get_system_performance_data(self) -> List[Dict[str, Any]]:
        """Get system performance data"""
        # Simulate system performance data
        return [
            {
                "cpu_percent": 20 + (i % 70),
                "memory_percent": 30 + (i % 60),
                "timestamp": time.time() - (i * 60)
            }
            for i in range(1440)  # 24 hours of data
        ]

    async def calculate_metric_value(self, metric: BusinessMetric, data: List[Dict[str, Any]]) -> float:
        """Calculate metric value based on type"""
        try:
            if not data:
                return 0.0

            if metric.calculation_type == "count":
                return float(len(data))

            elif metric.calculation_type == "sum":
                values = [float(item.get("amount", item.get("value", 0))) for item in data]
                return sum(values)

            elif metric.calculation_type == "average":
                values = [float(item.get("amount", item.get("value", 0))) for item in data]
                return statistics.mean(values) if values else 0.0

            elif metric.calculation_type == "rate":
                # Calculate rate (e.g., events per hour)
                time_span = max(1, (time.time() - data[0].get("timestamp", time.time())) / 3600)
                return len(data) / time_span

            elif metric.calculation_type == "percentage":
                # Calculate percentage
                total = len(data)
                filtered = len([item for item in data if item.get("status") == "success"])
                return (filtered / total * 100) if total > 0 else 0.0

            else:
                return 0.0

        except Exception as e:
            print(f"Metric calculation error: {e}")
            return 0.0

    async def generate_business_insights(self, metric_id: str) -> List[AnalyticsInsight]:
        """Generate business insights for metric"""
        try:
            metric = self.registered_metrics.get(metric_id)
            if not metric:
                return []

            # Get metric history
            metric_history = self.metric_values.get(metric_id, [])

            if len(metric_history) < 5:
                return []  # Need more data for insights

            # Extract values and timestamps
            values = [value for _, value in metric_history]
            timestamps = [timestamp for timestamp, _ in metric_history]

            # Calculate trends
            trend = await self.calculate_trend(values)

            # Detect anomalies
            anomalies = await self.detect_anomalies(values)

            # Generate insights
            insights = []

            # Trend insight
            if abs(trend) > 0.1:  # Significant trend
                insights.append(AnalyticsInsight(
                    insight_id=f"trend_{metric_id}_{int(time.time())}",
                    metric_id=metric_id,
                    scope=AnalyticsScope.DAILY,
                    value=values[-1],
                    trend="increasing" if trend > 0 else "decreasing",
                    confidence=0.8,
                    impact="medium" if abs(trend) < 0.3 else "high",
                    recommendation=f"Monitor {metric.name.lower()} trend and adjust strategy accordingly",
                    timestamp=time.time()
                ))

            # Anomaly insights
            for anomaly in anomalies:
                insights.append(AnalyticsInsight(
                    insight_id=f"anomaly_{metric_id}_{anomaly['index']}_{int(time.time())}",
                    metric_id=metric_id,
                    scope=AnalyticsScope.REAL_TIME,
                    value=anomaly["value"],
                    trend="anomalous",
                    confidence=anomaly["confidence"],
                    impact="high",
                    recommendation=f"Investigate anomaly in {metric.name.lower()} at data point {anomaly['index']}",
                    timestamp=time.time()
                ))

            # Target comparison insight
            if metric.target_value and values:
                current_value = values[-1]
                deviation = abs(current_value - metric.target_value) / metric.target_value

                if deviation > 0.1:  # More than 10% deviation
                    insights.append(AnalyticsInsight(
                        insight_id=f"target_deviation_{metric_id}_{int(time.time())}",
                        metric_id=metric_id,
                        scope=AnalyticsScope.DAILY,
                        value=current_value,
                        trend="off_target",
                        confidence=0.9,
                        impact="medium" if deviation < 0.2 else "high",
                        recommendation=f"{metric.name} is {deviation*100:.1f}% off target. Review performance.",
                        timestamp=time.time()
                    ))

            self.stats["insights_generated"] += len(insights)
            return insights

        except Exception as e:
            print(f"Business insights generation error: {e}")
            return []

    async def calculate_trend(self, values: List[float]) -> float:
        """Calculate trend in metric values"""
        if len(values) < 3:
            return 0.0

        # Simple linear regression slope
        n = len(values)
        x_values = list(range(n))
        y_values = values

        # Calculate means
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n

        # Calculate slope
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return 0.0

        slope = numerator / denominator

        # Normalize by value range
        value_range = max(values) - min(values) if max(values) != min(values) else 1
        normalized_slope = slope / value_range

        return normalized_slope

    async def detect_anomalies(self, values: List[float]) -> List[Dict[str, Any]]:
        """Detect anomalies in metric values"""
        anomalies = []

        try:
            if len(values) < 10:
                return anomalies

            # Calculate rolling statistics
            window_size = min(10, len(values) // 3)
            rolling_means = []
            rolling_stds = []

            for i in range(window_size, len(values)):
                window = values[i - window_size:i]
                rolling_means.append(statistics.mean(window))
                rolling_stds.append(statistics.stdev(window) if len(window) > 1 else 0)

            # Detect anomalies (values beyond 3 standard deviations)
            for i, (value, mean, std) in enumerate(zip(values[window_size:], rolling_means, rolling_stds)):
                if std > 0:
                    z_score = abs(value - mean) / std

                    if z_score > 3:  # 3 sigma rule
                        anomalies.append({
                            "index": i + window_size,
                            "value": value,
                            "expected": mean,
                            "deviation": z_score,
                            "confidence": min(1.0, z_score / 5)  # Higher deviation = higher confidence
                        })

            return anomalies

        except Exception as e:
            print(f"Anomaly detection error: {e}")
            return []

    async def predict_future_values(
        self,
        metric_id: str,
        prediction_horizon: int = 24,  # hours
        confidence_interval: float = 0.95
    ) -> Dict[str, Any]:
        """Predict future metric values"""
        try:
            metric = self.registered_metrics.get(metric_id)
            if not metric:
                return {"error": "Metric not found"}

            # Get historical data
            metric_history = self.metric_values.get(metric_id, [])

            if len(metric_history) < 10:
                return {"error": "Insufficient data for prediction"}

            values = [value for _, value in metric_history]
            timestamps = [timestamp for timestamp, _ in metric_history]

            # Simple time series prediction (in production, would use ML models)
            recent_values = values[-24:]  # Last 24 data points

            if len(recent_values) < 5:
                return {"error": "Insufficient recent data"}

            # Calculate trend
            trend = await self.calculate_trend(recent_values)

            # Calculate seasonal patterns (simplified)
            hourly_pattern = self.calculate_hourly_pattern(timestamps, values)

            # Generate predictions
            current_time = time.time()
            predictions = []

            for hour in range(1, prediction_horizon + 1):
                prediction_time = current_time + (hour * 3600)

                # Base prediction using trend
                last_value = recent_values[-1]
                predicted_value = last_value + (trend * hour)

                # Add seasonal adjustment
                hour_of_day = time.localtime(prediction_time).tm_hour
                seasonal_adjustment = hourly_pattern.get(hour_of_day, 0)
                predicted_value += seasonal_adjustment

                # Calculate confidence interval
                prediction_std = statistics.stdev(recent_values[-10:]) if len(recent_values) >= 10 else 0
                confidence_range = 1.96 * prediction_std  # 95% confidence

                predictions.append({
                    "timestamp": prediction_time,
                    "predicted_value": predicted_value,
                    "confidence_lower": predicted_value - confidence_range,
                    "confidence_upper": predicted_value + confidence_range,
                    "confidence": confidence_interval
                })

            self.stats["predictions_made"] += 1

            return {
                "metric_id": metric_id,
                "metric_name": metric.name,
                "prediction_horizon_hours": prediction_horizon,
                "predictions": predictions,
                "prediction_method": "trend_seasonal",
                "model_confidence": 0.75,  # Simulated confidence
                "next_prediction_due": current_time + 3600  # Next prediction in 1 hour
            }

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Prediction error: {e}")
            return {"error": str(e)}

    def calculate_hourly_pattern(self, timestamps: List[float], values: List[float]) -> Dict[int, float]:
        """Calculate hourly seasonal patterns"""
        try:
            hourly_values = {}
            for i in range(24):
                hourly_values[i] = []

            for timestamp, value in zip(timestamps, values):
                hour = time.localtime(timestamp).tm_hour
                hourly_values[hour].append(value)

            # Calculate average by hour
            hourly_pattern = {}
            for hour, hour_values in hourly_values.items():
                if hour_values:
                    avg_value = statistics.mean(hour_values)
                    # Calculate deviation from overall mean
                    overall_mean = statistics.mean(values) if values else 0
                    hourly_pattern[hour] = avg_value - overall_mean

            return hourly_pattern

        except Exception:
            return {}

    async def get_business_intelligence_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive business intelligence dashboard"""
        try:
            # Get real-time metrics
            real_time_metrics = await self.get_real_time_metrics()

            # Get predictive insights
            predictive_insights = await self.get_predictive_insights()

            return {
                "dashboard_type": "executive",
                "last_updated": time.time(),
                "real_time_metrics": real_time_metrics,
                "predictive_insights": predictive_insights,
                "key_performance_indicators": await self.get_kpi_summary(),
                "alerts_and_notifications": await self.get_business_alerts(),
                "strategic_recommendations": await self.generate_strategic_recommendations()
            }

        except Exception as e:
            return {"error": str(e)}

    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time business metrics"""
        real_time_data = {}

        try:
            for metric_id, metric in self.registered_metrics.items():
                # Calculate current value
                current_result = await self.calculate_business_metric(metric_id)

                if "error" not in current_result:
                    real_time_data[metric_id] = {
                        "name": metric.name,
                        "current_value": current_result["value"],
                        "last_updated": current_result["calculated_at"],
                        "status": await self.assess_metric_performance(metric_id)
                    }

            return real_time_data

        except Exception as e:
            return {"error": str(e)}

    async def get_predictive_insights(self) -> List[Dict[str, Any]]:
        """Get predictive business insights"""
        insights = []

        try:
            for metric_id in self.registered_metrics.keys():
                # Get predictions for next 24 hours
                predictions = await self.predict_future_values(metric_id, 24)

                if "error" not in predictions and predictions.get("predictions"):
                    latest_prediction = predictions["predictions"][0]

                    # Generate insight based on prediction
                    current_value = self.metric_values.get(metric_id, [])
                    if current_value:
                        last_value = current_value[-1][1]
                        predicted_change = latest_prediction["predicted_value"] - last_value

                        if abs(predicted_change) > last_value * 0.1:  # 10% change
                            insights.append({
                                "metric_id": metric_id,
                                "metric_name": self.registered_metrics[metric_id].name,
                                "predicted_change": predicted_change,
                                "confidence": latest_prediction["confidence"],
                                "timeframe": "24_hours",
                                "impact": "high" if abs(predicted_change) > last_value * 0.2 else "medium"
                            })

            return insights

        except Exception as e:
            return []

    async def get_kpi_summary(self) -> Dict[str, Any]:
        """Get KPI summary for dashboard"""
        try:
            total_metrics = len(self.registered_metrics)
            on_target = 0
            improving = 0
            declining = 0

            for metric_id in self.registered_metrics.keys():
                status = await self.assess_metric_performance(metric_id)

                if status == "on_target":
                    on_target += 1
                elif status == "improving":
                    improving += 1
                elif status == "declining":
                    declining += 1

            return {
                "total_kpis": total_metrics,
                "on_target": on_target,
                "improving": improving,
                "declining": declining,
                "overall_health": round((on_target * 100 + improving * 75 + declining * 25) / total_metrics, 1) if total_metrics > 0 else 0,
                "last_updated": time.time()
            }

        except Exception:
            return {"error": "KPI calculation failed"}

    async def get_business_alerts(self) -> List[Dict[str, Any]]:
        """Get business alerts and notifications"""
        alerts = []

        try:
            for metric_id, metric in self.registered_metrics.items():
                current_value_result = await self.calculate_business_metric(metric_id)

                if "error" in current_result:
                    continue

                current_value = current_value_result["value"]

                # Check thresholds
                if metric.threshold_critical and current_value > metric.threshold_critical:
                    alerts.append({
                        "type": "critical_threshold",
                        "metric_id": metric_id,
                        "metric_name": metric.name,
                        "current_value": current_value,
                        "threshold": metric.threshold_critical,
                        "severity": "critical",
                        "message": f"{metric.name} exceeded critical threshold"
                    })

                elif metric.threshold_warning and current_value > metric.threshold_warning:
                    alerts.append({
                        "type": "warning_threshold",
                        "metric_id": metric_id,
                        "metric_name": metric.name,
                        "current_value": current_value,
                        "threshold": metric.threshold_warning,
                        "severity": "warning",
                        "message": f"{metric.name} exceeded warning threshold"
                    })

                # Check for anomalies
                values = self.metric_values.get(metric_id, [])
                if len(values) >= 10:
                    anomalies = await self.detect_anomalies([value for _, value in values[-10:]])  # Last 10 values

                    for anomaly in anomalies:
                        alerts.append({
                            "type": "anomaly_detected",
                            "metric_id": metric_id,
                            "metric_name": metric.name,
                            "anomaly_value": anomaly["value"],
                            "expected_value": anomaly["expected"],
                            "severity": "medium",
                            "message": f"Anomaly detected in {metric.name}"
                        })

            return alerts

        except Exception as e:
            return []

    async def assess_metric_performance(self, metric_id: str) -> str:
        """Assess metric performance status"""
        try:
            metric = self.registered_metrics.get(metric_id)
            if not metric:
                return "unknown"

            values = self.metric_values.get(metric_id, [])

            if not values:
                return "no_data"

            current_value = values[-1][1]

            # Compare with target
            if metric.target_value:
                deviation = abs(current_value - metric.target_value) / metric.target_value

                if deviation < 0.05:  # Within 5%
                    return "on_target"
                elif deviation < 0.1:  # Within 10%
                    return "near_target"
                else:
                    return "off_target"

            # Compare with historical average
            if len(values) > 5:
                historical_avg = statistics.mean([value for _, value in values[:-1]])  # Exclude current value
                change = (current_value - historical_avg) / historical_avg if historical_avg != 0 else 0

                if change > 0.1:  # 10% improvement
                    return "improving"
                elif change < -0.1:  # 10% decline
                    return "declining"
                else:
                    return "stable"

            return "new_metric"

        except Exception:
            return "unknown"

    async def generate_strategic_recommendations(self) -> List[str]:
        """Generate strategic business recommendations"""
        recommendations = []

        try:
            # Analyze each metric
            for metric_id, data in self.registered_metrics.items():
                performance = await self.assess_metric_performance(metric_id)
                current_value = self.metric_values.get(metric_id, [])
                if current_value:
                    current_value = current_value[-1][1]

                if performance == "off_target" and data.target_value:
                    target = data.target_value
                    deviation = abs(current_value - target) / target

                    if deviation > 0.2:  # More than 20% off target
                        recommendations.append(
                            f"🚨 Critical: {data.name} is {deviation*100:.1f}% off target. Immediate action required."
                        )

                elif performance == "declining":
                    recommendations.append(
                        f"⚠️ Warning: {data.name} showing declining trend. Review strategy."
                    )

                elif performance == "improving":
                    recommendations.append(
                        f"✅ Positive: {data.name} showing improvement. Continue current approach."
                    )

            # General recommendations
            if not recommendations:
                recommendations.append("✅ All metrics performing within acceptable ranges. Continue monitoring.")

            return recommendations[:10]  # Limit to top 10 recommendations

        except Exception as e:
            return ["Review business metrics and performance indicators"]


# Global analytics service instance
ultra_analytics_service = UltraAnalyticsService()