"""
Advanced Monitoring and Observability Module
Complete monitoring stack with Prometheus, Jaeger, and custom metrics
"""
import time
import asyncio
from typing import Dict, List, Any, Optional
import structlog
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
import prometheus_client as prom

# Jaeger tracing
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource

# Initialize logger
logger = structlog.get_logger()

# Custom Prometheus registry
monitoring_registry = CollectorRegistry()

@dataclass
class BusinessMetrics:
    """Business-specific metrics for monitoring"""
    api_requests_total: Counter
    api_response_time: Histogram
    active_users: Gauge
    business_transactions: Counter
    error_rate: Counter
    cache_hit_rate: Gauge
    database_query_time: Histogram
    memory_usage: Gauge
    cpu_usage: Gauge

class MetricsCollector:
    """Advanced metrics collection for business intelligence"""

    def __init__(self):
        self.business_metrics = BusinessMetrics(
            api_requests_total=Counter(
                'api_requests_total',
                'Total number of API requests',
                ['endpoint', 'method', 'status_code'],
                registry=monitoring_registry
            ),
            api_response_time=Histogram(
                'api_response_time_seconds',
                'API response time in seconds',
                ['endpoint', 'method'],
                buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
                registry=monitoring_registry
            ),
            active_users=Gauge(
                'active_users',
                'Number of currently active users',
                registry=monitoring_registry
            ),
            business_transactions=Counter(
                'business_transactions_total',
                'Total number of business transactions',
                ['transaction_type', 'status'],
                registry=monitoring_registry
            ),
            error_rate=Counter(
                'error_rate_total',
                'Total number of errors',
                ['error_type', 'endpoint'],
                registry=monitoring_registry
            ),
            cache_hit_rate=Gauge(
                'cache_hit_rate',
                'Cache hit rate percentage',
                registry=monitoring_registry
            ),
            database_query_time=Histogram(
                'database_query_time_seconds',
                'Database query execution time',
                ['query_type', 'table'],
                buckets=[0.01, 0.1, 0.5, 1.0, 2.0, 5.0],
                registry=monitoring_registry
            ),
            memory_usage=Gauge(
                'memory_usage_bytes',
                'Memory usage in bytes',
                ['component'],
                registry=monitoring_registry
            ),
            cpu_usage=Gauge(
                'cpu_usage_percent',
                'CPU usage percentage',
                ['component'],
                registry=monitoring_registry
            )
        )

        self.start_time = time.time()
        self._start_background_tasks()

    def _start_background_tasks(self):
        """Start background tasks for metrics collection"""
        asyncio.create_task(self._collect_system_metrics())
        asyncio.create_task(self._collect_business_metrics())

    async def _collect_system_metrics(self):
        """Collect system-level metrics periodically"""
        while True:
            try:
                # Memory usage
                import psutil
                process = psutil.Process()
                memory_info = process.memory_info()

                self.business_metrics.memory_usage.labels(component="fastapi").set(memory_info.rss)
                self.business_metrics.cpu_usage.labels(component="fastapi").set(process.cpu_percent())

                # Database connections (mock for now)
                self.business_metrics.memory_usage.labels(component="postgresql").set(memory_info.rss * 0.3)
                self.business_metrics.memory_usage.labels(component="redis").set(memory_info.rss * 0.2)

            except Exception as e:
                logger.error("System metrics collection failed", error=str(e))

            await asyncio.sleep(30)  # Collect every 30 seconds

    async def _collect_business_metrics(self):
        """Collect business-specific metrics"""
        while True:
            try:
                # Update active users (mock data)
                self.business_metrics.active_users.set(150)  # Mock active users count

                # Update cache hit rate (mock data)
                self.business_metrics.cache_hit_rate.set(85.5)  # Mock cache hit rate

            except Exception as e:
                logger.error("Business metrics collection failed", error=str(e))

            await asyncio.sleep(60)  # Collect every minute

    def record_api_request(self, endpoint: str, method: str, status_code: int, response_time: float):
        """Record API request metrics"""
        self.business_metrics.api_requests_total.labels(
            endpoint=endpoint,
            method=method,
            status_code=str(status_code)
        ).inc()

        self.business_metrics.api_response_time.labels(
            endpoint=endpoint,
            method=method
        ).observe(response_time)

    def record_business_transaction(self, transaction_type: str, status: str):
        """Record business transaction metrics"""
        self.business_metrics.business_transactions.labels(
            transaction_type=transaction_type,
            status=status
        ).inc()

    def record_error(self, error_type: str, endpoint: str):
        """Record error metrics"""
        self.business_metrics.error_rate.labels(
            error_type=error_type,
            endpoint=endpoint
        ).inc()

    def record_database_query(self, query_type: str, table: str, execution_time: float):
        """Record database query metrics"""
        self.business_metrics.database_query_time.labels(
            query_type=query_type,
            table=table
        ).observe(execution_time)

    def get_all_metrics(self) -> str:
        """Get all metrics in Prometheus format"""
        return generate_latest(monitoring_registry).decode('utf-8')

# Initialize metrics collector
metrics_collector = MetricsCollector()

class JaegerTracerManager:
    """Advanced distributed tracing with Jaeger"""

    def __init__(self):
        self._setup_tracing()

    def _setup_tracing(self):
        """Setup OpenTelemetry tracing with Jaeger exporter"""
        # Set up resource
        resource = Resource.create({
            "service.name": "sec-fastapi",
            "service.version": "4.0.0",
            "environment": "production"
        })

        # Set up tracer provider
        trace.set_tracer_provider(TracerProvider(resource=resource))

        # Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name="jaeger",
            agent_port=6831,
        )

        # Add span processor
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)

        # Console exporter for debugging
        console_exporter = ConsoleSpanExporter()
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(console_exporter)
        )

    def start_span(self, name: str, context: Optional[Dict[str, Any]] = None) -> trace.Span:
        """Start a new tracing span"""
        tracer = trace.get_tracer(__name__)
        span = tracer.start_span(name)

        if context:
            for key, value in context.items():
                span.set_attribute(key, value)

        return span

    def add_span_event(self, span: trace.Span, name: str, attributes: Dict[str, Any] = None):
        """Add event to span"""
        span.add_event(name, attributes or {})

    def set_span_attribute(self, span: trace.Span, key: str, value: Any):
        """Set span attribute"""
        span.set_attribute(key, value)

class LogAggregationManager:
    """Advanced log aggregation for structured logging and analysis"""

    def __init__(self):
        self.log_buffer = []
        self.max_buffer_size = 1000
        self._start_log_processing()

    def _start_log_processing(self):
        """Start background log processing"""
        asyncio.create_task(self._process_log_buffer())

    async def _process_log_buffer(self):
        """Process log buffer periodically"""
        while True:
            try:
                if self.log_buffer:
                    # Process logs for aggregation
                    await self._aggregate_logs(self.log_buffer.copy())
                    self.log_buffer.clear()

            except Exception as e:
                logger.error("Log processing failed", error=str(e))

            await asyncio.sleep(10)  # Process every 10 seconds

    async def _aggregate_logs(self, logs: List[Dict[str, Any]]):
        """Aggregate logs for analysis"""
        # Group logs by type and level
        aggregated = {}

        for log in logs:
            log_type = log.get('logger', 'unknown')
            level = log.get('level', 'info')

            if log_type not in aggregated:
                aggregated[log_type] = {}

            if level not in aggregated[log_type]:
                aggregated[log_type][level] = []

            aggregated[log_type][level].append(log)

        # Log aggregation summary
        logger.info(
            "Log aggregation completed",
            total_logs=len(logs),
            log_types=len(aggregated),
            aggregated_summary=aggregated
        )

    def add_structured_log(self, log_entry: Dict[str, Any]):
        """Add structured log entry to buffer"""
        log_entry.update({
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'sec-fastapi',
            'version': '4.0.0'
        })

        self.log_buffer.append(log_entry)

        if len(self.log_buffer) >= self.max_buffer_size:
            # Process immediately if buffer is full
            asyncio.create_task(self._process_log_buffer())

    def create_security_log(self, action: str, user_id: str, resource: str, details: Dict[str, Any]):
        """Create security-specific structured log"""
        security_log = {
            'type': 'security',
            'action': action,
            'user_id': user_id,
            'resource': resource,
            'details': details,
            'severity': self._determine_severity(action)
        }

        self.add_structured_log(security_log)

        # Also log immediately for security events
        logger.info(
            "Security event logged",
            action=action,
            user_id=user_id,
            resource=resource,
            **details
        )

    def _determine_severity(self, action: str) -> str:
        """Determine log severity based on action"""
        high_severity_actions = [
            'unauthorized_access',
            'suspicious_activity',
            'data_breach',
            'privilege_escalation'
        ]

        medium_severity_actions = [
            'login',
            'logout',
            'password_change',
            'token_refresh'
        ]

        if action in high_severity_actions:
            return 'HIGH'
        elif action in medium_severity_actions:
            return 'MEDIUM'
        else:
            return 'LOW'

class DashboardManager:
    """Advanced dashboard management for service-specific monitoring"""

    def __init__(self):
        self.dashboards = {}
        self._initialize_default_dashboards()

    def _initialize_default_dashboards(self):
        """Initialize default monitoring dashboards"""
        self.dashboards = {
            'api_performance': {
                'title': 'API Performance Dashboard',
                'metrics': [
                    'api_requests_total',
                    'api_response_time_seconds',
                    'error_rate_total',
                    'cache_hit_rate'
                ],
                'refresh_interval': 30
            },
            'database_health': {
                'title': 'Database Health Dashboard',
                'metrics': [
                    'database_query_time_seconds',
                    'memory_usage_bytes',
                    'cpu_usage_percent'
                ],
                'refresh_interval': 60
            },
            'business_metrics': {
                'title': 'Business Metrics Dashboard',
                'metrics': [
                    'active_users',
                    'business_transactions_total',
                    'cache_hit_rate'
                ],
                'refresh_interval': 120
            },
            'security_monitoring': {
                'title': 'Security Monitoring Dashboard',
                'metrics': [
                    'error_rate_total',
                    'api_requests_total'
                ],
                'refresh_interval': 30
            }
        }

    def get_dashboard_data(self, dashboard_name: str) -> Dict[str, Any]:
        """Get dashboard data and metrics"""
        if dashboard_name not in self.dashboards:
            raise ValueError(f"Dashboard '{dashboard_name}' not found")

        dashboard = self.dashboards[dashboard_name]

        # Get current metrics for dashboard
        metrics_data = {}
        for metric_name in dashboard['metrics']:
            # This would integrate with actual Prometheus metrics
            metrics_data[metric_name] = self._get_metric_value(metric_name)

        return {
            'dashboard': dashboard,
            'metrics': metrics_data,
            'last_updated': datetime.utcnow().isoformat(),
            'status': 'healthy'
        }

    def _get_metric_value(self, metric_name: str) -> Any:
        """Get current value for a metric (mock implementation)"""
        # This would integrate with actual Prometheus registry
        mock_values = {
            'api_requests_total': 15420,
            'api_response_time_seconds': 0.234,
            'error_rate_total': 45,
            'cache_hit_rate': 87.3,
            'active_users': 156,
            'business_transactions_total': 8934,
            'database_query_time_seconds': 0.045,
            'memory_usage_bytes': 134217728,  # 128MB
            'cpu_usage_percent': 23.4
        }

        return mock_values.get(metric_name, 0)

    def create_custom_dashboard(self, name: str, title: str, metrics: List[str], refresh_interval: int = 60):
        """Create a custom monitoring dashboard"""
        self.dashboards[name] = {
            'title': title,
            'metrics': metrics,
            'refresh_interval': refresh_interval,
            'created_at': datetime.utcnow().isoformat(),
            'type': 'custom'
        }

        logger.info(
            "Custom dashboard created",
            dashboard_name=name,
            title=title,
            metrics_count=len(metrics)
        )

# Initialize global managers
jaeger_tracer = JaegerTracerManager()
log_aggregator = LogAggregationManager()
dashboard_manager = DashboardManager()

# Helper functions for integration
def record_api_metrics(endpoint: str, method: str, status_code: int, response_time: float):
    """Record API request metrics"""
    metrics_collector.record_api_request(endpoint, method, status_code, response_time)

def create_tracing_span(name: str, context: Dict[str, Any] = None):
    """Create a tracing span"""
    return jaeger_tracer.start_span(name, context)

def log_security_event(action: str, user_id: str, resource: str, details: Dict[str, Any]):
    """Log security event"""
    log_aggregator.create_security_log(action, user_id, resource, details)

def get_dashboard(dashboard_name: str) -> Dict[str, Any]:
    """Get dashboard data"""
    return dashboard_manager.get_dashboard_data(dashboard_name)

def get_all_metrics() -> str:
    """Get all Prometheus metrics"""
    return metrics_collector.get_all_metrics()
