"""
Advanced Message Analytics
Throughput monitoring, latency tracking, and performance analytics
"""
import asyncio
import json
import time
import statistics
from typing import Dict, Any, List, Optional, DefaultDict
from collections import defaultdict, deque
from dataclasses import dataclass, asdict

from .client import get_redis_client


@dataclass
class MessageMetrics:
    """Message metrics data structure"""
    message_id: str
    timestamp: float
    routing_key: str
    priority: int
    size_bytes: int
    processing_time_ms: Optional[float] = None
    status: str = "sent"
    broker_type: str = "unknown"
    error_message: Optional[str] = None


class MessageAnalytics:
    """Advanced message analytics and monitoring"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.analytics_prefix = "message_analytics"

        # Metrics storage
        self.message_history: deque = deque(maxlen=10000)  # Keep last 10k messages
        self.routing_key_stats: DefaultDict[str, List[float]] = defaultdict(list)
        self.broker_stats: DefaultDict[str, List[float]] = defaultdict(list)
        self.hourly_throughput: DefaultDict[str, int] = defaultdict(int)

        # Performance tracking
        self.stats = {
            "total_messages": 0,
            "successful_messages": 0,
            "failed_messages": 0,
            "total_latency_ms": 0,
            "errors": 0
        }

    async def track_message(
        self,
        message_id: str,
        routing_key: str,
        priority: int,
        size_bytes: int,
        broker_type: str = "unknown"
    ) -> None:
        """Track message for analytics"""
        metrics = MessageMetrics(
            message_id=message_id,
            timestamp=time.time(),
            routing_key=routing_key,
            priority=priority,
            size_bytes=size_bytes,
            broker_type=broker_type
        )

        try:
            # Store message metrics
            await self.redis_client.setex(
                f"{self.analytics_prefix}:message:{message_id}",
                86400 * 7,  # 7 days
                json.dumps(asdict(metrics), default=str)
            )

            # Update statistics
            self.stats["total_messages"] += 1

            # Update hourly throughput
            current_hour = time.strftime("%Y-%m-%d-%H")
            self.hourly_throughput[current_hour] += 1

            # Store in recent history
            self.message_history.append(metrics)

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Message tracking error: {e}")

    async def update_message_status(
        self,
        message_id: str,
        status: str,
        processing_time_ms: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Update message processing status"""
        try:
            # Get existing metrics
            metrics_key = f"{self.analytics_prefix}:message:{message_id}"
            metrics_data = await self.redis_client.get(metrics_key)

            if metrics_data:
                metrics = MessageMetrics(**json.loads(metrics_data))
                metrics.status = status
                metrics.processing_time_ms = processing_time_ms
                metrics.error_message = error_message

                # Update statistics
                if status == "processed":
                    self.stats["successful_messages"] += 1
                    if processing_time_ms:
                        self.stats["total_latency_ms"] += processing_time_ms
                        self.routing_key_stats[metrics.routing_key].append(processing_time_ms)
                        self.broker_stats[metrics.broker_type].append(processing_time_ms)
                elif status == "failed":
                    self.stats["failed_messages"] += 1

                # Update stored metrics
                await self.redis_client.setex(
                    metrics_key,
                    86400 * 7,
                    json.dumps(asdict(metrics), default=str)
                )

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Message status update error: {e}")

    async def get_throughput_analytics(self) -> Dict[str, Any]:
        """Get message throughput analytics"""
        try:
            current_hour = time.strftime("%Y-%m-%d-%H")

            # Calculate throughput for last 24 hours
            throughput_data = {}
            for hour in range(24):
                hour_key = time.strftime("%Y-%m-%d-%H", time.localtime(time.time() - (hour * 3600)))
                throughput_data[hour_key] = self.hourly_throughput.get(hour_key, 0)

            # Calculate trends
            recent_hours = list(throughput_data.values())[-12:]  # Last 12 hours
            trend = "stable"
            if len(recent_hours) >= 2:
                if recent_hours[-1] > recent_hours[0] * 1.2:
                    trend = "increasing"
                elif recent_hours[-1] < recent_hours[0] * 0.8:
                    trend = "decreasing"

            return {
                "current_throughput_per_hour": self.hourly_throughput.get(current_hour, 0),
                "hourly_throughput": dict(list(throughput_data.items())[-24:]),  # Last 24 hours
                "trend": trend,
                "peak_hour": max(throughput_data.items(), key=lambda x: x[1]) if throughput_data else None,
                "total_messages_last_24h": sum(throughput_data.values()),
                "average_throughput": sum(throughput_data.values()) / max(1, len(throughput_data))
            }

        except Exception as e:
            print(f"Throughput analytics error: {e}")
            return {"error": str(e)}

    async def get_latency_analytics(self) -> Dict[str, Any]:
        """Get message latency analytics"""
        try:
            # Calculate latency statistics
            all_latencies = []
            for latencies in self.routing_key_stats.values():
                all_latencies.extend(latencies)

            if not all_latencies:
                return {"message": "No latency data available"}

            # Calculate statistics
            avg_latency = statistics.mean(all_latencies)
            median_latency = statistics.median(all_latencies)
            p95_latency = statistics.quantiles(all_latencies, n=20)[18] if len(all_latencies) >= 20 else max(all_latencies)
            p99_latency = statistics.quantiles(all_latencies, n=100)[98] if len(all_latencies) >= 100 else max(all_latencies)

            # Latency by routing key
            routing_key_latency = {}
            for routing_key, latencies in self.routing_key_stats.items():
                if latencies:
                    routing_key_latency[routing_key] = {
                        "avg_ms": statistics.mean(latencies),
                        "count": len(latencies),
                        "p95_ms": statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
                    }

            # Latency by broker type
            broker_latency = {}
            for broker_type, latencies in self.broker_stats.items():
                if latencies:
                    broker_latency[broker_type] = {
                        "avg_ms": statistics.mean(latencies),
                        "count": len(latencies),
                        "p95_ms": statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
                    }

            return {
                "overall_latency": {
                    "average_ms": avg_latency,
                    "median_ms": median_latency,
                    "p95_ms": p95_latency,
                    "p99_ms": p99_latency,
                    "total_measurements": len(all_latencies)
                },
                "by_routing_key": routing_key_latency,
                "by_broker_type": broker_latency,
                "performance_rating": self.get_performance_rating(avg_latency)
            }

        except Exception as e:
            print(f"Latency analytics error: {e}")
            return {"error": str(e)}

    def get_performance_rating(self, avg_latency: float) -> str:
        """Get performance rating based on latency"""
        if avg_latency < 50:
            return "excellent"
        elif avg_latency < 100:
            return "good"
        elif avg_latency < 200:
            return "fair"
        elif avg_latency < 500:
            return "poor"
        else:
            return "critical"

    async def get_routing_key_analytics(self) -> Dict[str, Any]:
        """Get analytics by routing key"""
        try:
            routing_analytics = {}

            for routing_key, latencies in self.routing_key_stats.items():
                if latencies:
                    routing_analytics[routing_key] = {
                        "message_count": len(latencies),
                        "avg_latency_ms": statistics.mean(latencies),
                        "min_latency_ms": min(latencies),
                        "max_latency_ms": max(latencies),
                        "success_rate": await self.get_routing_key_success_rate(routing_key)
                    }

            # Sort by message count
            sorted_routing = sorted(
                routing_analytics.items(),
                key=lambda x: x[1]["message_count"],
                reverse=True
            )

            return {
                "routing_keys": dict(sorted_routing),
                "most_active": sorted_routing[0] if sorted_routing else None,
                "total_routing_keys": len(routing_analytics)
            }

        except Exception as e:
            print(f"Routing key analytics error: {e}")
            return {"error": str(e)}

    async def get_routing_key_success_rate(self, routing_key: str) -> float:
        """Get success rate for routing key"""
        try:
            # Get message IDs for routing key
            pattern = f"{self.analytics_prefix}:message:*"
            message_keys = await self.redis_client.keys(pattern)

            successful = 0
            total = 0

            for key in message_keys[:100]:  # Sample for performance
                message_data = await self.redis_client.get(key)
                if message_data:
                    metrics = json.loads(message_data)
                    if metrics.get("routing_key") == routing_key:
                        total += 1
                        if metrics.get("status") == "processed":
                            successful += 1

            return (successful / total * 100) if total > 0 else 0

        except Exception:
            return 0

    async def get_error_analytics(self) -> Dict[str, Any]:
        """Get error analytics and patterns"""
        try:
            error_pattern = f"{self.analytics_prefix}:message:*"
            message_keys = await self.redis_client.keys(error_pattern)

            errors_by_type = defaultdict(int)
            errors_by_routing_key = defaultdict(int)
            recent_errors = []

            for key in message_keys[:200]:  # Sample for performance
                message_data = await self.redis_client.get(key)
                if message_data:
                    metrics = json.loads(message_data)

                    if metrics.get("status") == "failed" and metrics.get("error_message"):
                        error_msg = metrics["error_message"]
                        routing_key = metrics.get("routing_key", "unknown")

                        # Categorize errors
                        if "timeout" in error_msg.lower():
                            errors_by_type["timeout"] += 1
                        elif "connection" in error_msg.lower():
                            errors_by_type["connection"] += 1
                        elif "parse" in error_msg.lower():
                            errors_by_type["parse"] += 1
                        else:
                            errors_by_type["other"] += 1

                        errors_by_routing_key[routing_key] += 1

                        # Track recent errors
                        if len(recent_errors) < 10:
                            recent_errors.append({
                                "message_id": metrics["message_id"],
                                "routing_key": routing_key,
                                "error": error_msg,
                                "timestamp": metrics["timestamp"]
                            })

            return {
                "error_counts_by_type": dict(errors_by_type),
                "error_counts_by_routing_key": dict(errors_by_routing_key),
                "recent_errors": recent_errors,
                "total_errors": sum(errors_by_type.values()),
                "error_rate_percent": (sum(errors_by_type.values()) / max(1, self.stats["total_messages"])) * 100
            }

        except Exception as e:
            print(f"Error analytics error: {e}")
            return {"error": str(e)}

    async def predict_bottlenecks(self) -> Dict[str, Any]:
        """Predict potential bottlenecks based on current patterns"""
        try:
            # Analyze throughput trends
            throughput_data = []
            for hour in range(24):
                hour_key = time.strftime("%Y-%m-%d-%H", time.localtime(time.time() - (hour * 3600)))
                throughput_data.append(self.hourly_throughput.get(hour_key, 0))

            # Simple trend analysis
            if len(throughput_data) >= 6:
                recent_avg = sum(throughput_data[-6:]) / 6
                previous_avg = sum(throughput_data[-12:-6]) / 6 if len(throughput_data) >= 12 else recent_avg

                trend_percentage = ((recent_avg - previous_avg) / max(1, previous_avg)) * 100

                bottlenecks = []

                if trend_percentage > 50:  # Rapid increase
                    bottlenecks.append({
                        "type": "throughput_spike",
                        "severity": "high",
                        "description": f"Throughput increased {trend_percentage:.1f}% recently",
                        "recommendation": "Monitor system capacity and consider scaling"
                    })

                if recent_avg > 1000:  # High throughput
                    bottlenecks.append({
                        "type": "high_throughput",
                        "severity": "medium",
                        "description": f"High message throughput: {recent_avg:.0f} messages/hour",
                        "recommendation": "Consider load balancing and performance optimization"
                    })

                # Check latency trends
                all_latencies = []
                for latencies in self.routing_key_stats.values():
                    all_latencies.extend(latencies)

                if all_latencies:
                    avg_latency = statistics.mean(all_latencies)
                    if avg_latency > 200:  # High latency
                        bottlenecks.append({
                            "type": "high_latency",
                            "severity": "high",
                            "description": f"Average latency: {avg_latency:.0f}ms",
                            "recommendation": "Investigate message processing bottlenecks"
                        })

                return {
                    "bottlenecks_detected": len(bottlenecks),
                    "bottlenecks": bottlenecks,
                    "throughput_trend": f"{trend_percentage:+.1f}%",
                    "current_throughput": recent_avg,
                    "recommendations": [
                        "Monitor throughput trends continuously",
                        "Implement auto-scaling based on load",
                        "Optimize message processing for high-latency routes",
                        "Consider message batching for high-throughput scenarios"
                    ]
                }

            return {"message": "Insufficient data for bottleneck prediction"}

        except Exception as e:
            print(f"Bottleneck prediction error: {e}")
            return {"error": str(e)}

    async def get_queue_depth_analytics(self) -> Dict[str, Any]:
        """Get queue depth analytics"""
        try:
            # Get queue information from Redis Streams
            pattern = "message_streams:*"
            stream_keys = await self.redis_client.keys(pattern)

            queue_info = {}

            for stream_key in stream_keys:
                length = await self.redis_client.xlen(stream_key)
                groups = await self._get_stream_groups(stream_key)

                queue_info[stream_key] = {
                    "length": length,
                    "groups": groups,
                    "status": "healthy" if length < 1000 else "backlog" if length < 5000 else "critical"
                }

            # Identify problematic queues
            problematic_queues = [
                {"queue": queue, "length": info["length"], "status": info["status"]}
                for queue, info in queue_info.items()
                if info["status"] in ["backlog", "critical"]
            ]

            return {
                "total_queues": len(queue_info),
                "queue_info": queue_info,
                "problematic_queues": problematic_queues,
                "recommendations": [
                    "Monitor queue depths regularly",
                    "Implement dead letter queues for failed messages",
                    "Consider horizontal scaling for high-throughput queues",
                    "Implement queue partitioning for better distribution"
                ]
            }

        except Exception as e:
            print(f"Queue depth analytics error: {e}")
            return {"error": str(e)}

    async def _get_stream_groups(self, stream: str) -> Dict[str, Any]:
        """Get consumer groups for a stream"""
        try:
            groups = await self.redis_client.xinfo_groups(stream)
            return {group["name"]: group for group in groups}
        except Exception:
            return {}

    async def get_comprehensive_analytics(self) -> Dict[str, Any]:
        """Get comprehensive message analytics"""
        try:
            throughput = await self.get_throughput_analytics()
            latency = await self.get_latency_analytics()
            routing = await self.get_routing_key_analytics()
            errors = await self.get_error_analytics()
            bottlenecks = await self.predict_bottlenecks()
            queues = await self.get_queue_depth_analytics()

            return {
                "throughput_analytics": throughput,
                "latency_analytics": latency,
                "routing_key_analytics": routing,
                "error_analytics": errors,
                "bottleneck_prediction": bottlenecks,
                "queue_analytics": queues,
                "summary": {
                    "total_messages": self.stats["total_messages"],
                    "success_rate": (self.stats["successful_messages"] / max(1, self.stats["total_messages"])) * 100,
                    "average_latency_ms": self.stats["total_latency_ms"] / max(1, self.stats["successful_messages"]),
                    "error_rate": (self.stats["failed_messages"] / max(1, self.stats["total_messages"])) * 100
                }
            }

        except Exception as e:
            print(f"Comprehensive analytics error: {e}")
            return {"error": str(e)}


# Global message analytics instance
message_analytics = MessageAnalytics()
