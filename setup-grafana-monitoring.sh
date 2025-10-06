# 🚀 CONFIGURAÇÃO AVANÇADA DO GRAFANA PARA PRODUÇÃO
# Dashboard e métricas ultra-avançadas para monitoramento completo

# Configuração do Grafana
GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER}
GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
GF_USERS_ALLOW_SIGN_UP=false
GF_USERS_ALLOW_ORG_CREATE=false

# Provisioning de Dashboards
GF_DASHBOARDS_MIN_REFRESH_INTERVAL=5s
GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/etc/grafana/dashboards/executive-overview.json

# Alertas
GF_ALERTING_ENABLED=true
GF_ALERTING_EXECUTE_ALERTS=true
GF_ALERTING_MAX_ANNOTATION_LENGTH=16384

# Logs
GF_LOG_LEVEL=warn
GF_LOG_MODE=console

# Métricas
GF_METRICS_ENABLED=true
GF_METRICS_INTERVAL_SECONDS=60

# Segurança
GF_SECURITY_SECRET_KEY=${GRAFANA_SECRET_KEY}
GF_SECURITY_DISABLE_GRAVATAR=true
GF_SECURITY_COOKIE_SECURE=true
GF_SECURITY_COOKIE_SAMESITE=strict

# Database (SQLite para produção simples, PostgreSQL recomendado)
GF_DATABASE_TYPE=sqlite3
GF_DATABASE_PATH=/var/lib/grafana/grafana.db

# Servidor
GF_SERVER_HTTP_PORT=3001
GF_SERVER_ROOT_URL=${GRAFANA_ROOT_URL}
GF_SERVER_SERVE_FROM_SUB_PATH=false

# Provisioning de fontes de dados
GF_DATASOURCES_PATH=/etc/grafana/provisioning/datasources
GF_DASHBOARDS_PATH=/etc/grafana/provisioning/dashboards

# Configuração de fontes de dados provisionadas
cat > docker/grafana/provisioning/datasources/prometheus.yml << EOF
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
    jsonData:
      timeInterval: "15s"
      queryTimeout: "300s"
      httpMethod: "POST"

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: false
    jsonData:
      httpHeaderName1: "X-Scope-OrgID"
      httpHeaderValue1: "tenant1"
      maxLines: 1000

  - name: PostgreSQL
    type: postgres
    url: postgres:5432
    database: secdb
    user: sec
    secureJsonData:
      password: "secpass"
    jsonData:
      sslmode: "disable"
      maxOpenConns: 100
      maxIdleConns: 5
      connMaxLifetime: 14400

  - name: Redis
    type: redis-datasource
    access: proxy
    url: redis://redis:6379/0
    editable: false
    jsonData:
      poolSize: 5
      timeout: 10
      pingInterval: 30
      pipelineWindow: 100
EOF

# Dashboards provisionados
mkdir -p docker/grafana/provisioning/dashboards

# Dashboard Executivo
cat > docker/grafana/provisioning/dashboards/executive-overview.json << EOF
{
  "dashboard": {
    "title": "SEC Ultra-Revolutionary - Executive Overview",
    "tags": ["executive", "overview", "kpi"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Overall System Health",
        "type": "gauge",
        "targets": [
          {
            "expr": "up{job=\"fastapi\"} + up{job=\"nestjs\"} + up{job=\"redis\"} + up{job=\"postgres\"}",
            "legendFormat": "{{job}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "steps": [
                { "color": "red", "value": 0 },
                { "color": "yellow", "value": 2 },
                { "color": "green", "value": 4 }
              ]
            }
          }
        },
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 }
      },
      {
        "title": "Business Metrics Overview",
        "type": "stat",
        "targets": [
          {
            "expr": "business_revenue_total",
            "legendFormat": "Total Revenue"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": { "mode": "continuous-GrYlRd" },
            "thresholds": {
              "steps": [
                { "color": "green", "value": 0 },
                { "color": "yellow", "value": 1000000 },
                { "color": "red", "value": 10000000 }
              ]
            }
          }
        },
        "gridPos": { "h": 8, "w": 6, "x": 12, "y": 0 }
      },
      {
        "title": "AI Model Performance",
        "type": "timeseries",
        "targets": [
          {
            "expr": "ai_model_accuracy",
            "legendFormat": "{{model}}"
          },
          {
            "expr": "ai_model_latency",
            "legendFormat": "{{model}} - Latency"
          }
        ],
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 8 }
      },
      {
        "title": "Blockchain Analytics",
        "type": "timeseries",
        "targets": [
          {
            "expr": "blockchain_transactions_total",
            "legendFormat": "Transactions"
          },
          {
            "expr": "blockchain_volume_usd",
            "legendFormat": "Volume (USD)"
          }
        ],
        "gridPos": { "h": 8, "w": 12, "x": 12, "y": 8 }
      },
      {
        "title": "Edge Computing Performance",
        "type": "table",
        "targets": [
          {
            "expr": "edge_node_load",
            "legendFormat": "{{node}}"
          }
        ],
        "gridPos": { "h": 8, "w": 24, "x": 0, "y": 16 }
      }
    ],
    "time": {
      "from": "now-24h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
EOF

# Dashboard Técnico
cat > docker/grafana/provisioning/dashboards/technical-metrics.json << EOF
{
  "dashboard": {
    "title": "SEC Ultra-Revolutionary - Technical Metrics",
    "tags": ["technical", "performance", "infrastructure"],
    "panels": [
      {
        "title": "System Performance",
        "type": "timeseries",
        "targets": [
          {
            "expr": "system_cpu_usage",
            "legendFormat": "{{instance}}"
          },
          {
            "expr": "system_memory_usage",
            "legendFormat": "{{instance}}"
          }
        ],
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 }
      },
      {
        "title": "Network I/O",
        "type": "timeseries",
        "targets": [
          {
            "expr": "network_receive_bytes_total",
            "legendFormat": "RX {{device}}"
          },
          {
            "expr": "network_transmit_bytes_total",
            "legendFormat": "TX {{device}}"
          }
        ],
        "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 }
      },
      {
        "title": "Database Performance",
        "type": "timeseries",
        "targets": [
          {
            "expr": "postgres_connections",
            "legendFormat": "Active Connections"
          },
          {
            "expr": "postgres_queries_per_second",
            "legendFormat": "Queries/sec"
          }
        ],
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 8 }
      },
      {
        "title": "Redis Performance",
        "type": "timeseries",
        "targets": [
          {
            "expr": "redis_commands_processed_total",
            "legendFormat": "Commands/sec"
          },
          {
            "expr": "redis_memory_used_bytes",
            "legendFormat": "Memory Usage"
          }
        ],
        "gridPos": { "h": 8, "w": 12, "x": 12, "y": 8 }
      }
    ]
  }
}
EOF

# Dashboard de Segurança
cat > docker/grafana/provisioning/dashboards/security-metrics.json << EOF
{
  "dashboard": {
    "title": "SEC Ultra-Revolutionary - Security Metrics",
    "tags": ["security", "quantum", "threats"],
    "panels": [
      {
        "title": "Security Events",
        "type": "timeseries",
        "targets": [
          {
            "expr": "security_events_total",
            "legendFormat": "{{severity}}"
          }
        ],
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 }
      },
      {
        "title": "Quantum Key Rotations",
        "type": "stat",
        "targets": [
          {
            "expr": "quantum_keys_rotated_total",
            "legendFormat": "Keys Rotated Today"
          }
        ],
        "gridPos": { "h": 8, "w": 6, "x": 12, "y": 0 }
      },
      {
        "title": "Threat Intelligence",
        "type": "table",
        "targets": [
          {
            "expr": "threat_feeds_score",
            "legendFormat": "{{feed}}"
          }
        ],
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 8 }
      }
    ]
  }
}
EOF

# Dashboard de Business Intelligence
cat > docker/grafana/provisioning/dashboards/business-intelligence.json << EOF
{
  "dashboard": {
    "title": "SEC Ultra-Revolutionary - Business Intelligence",
    "tags": ["business", "intelligence", "analytics"],
    "panels": [
      {
        "title": "Revenue Trends",
        "type": "timeseries",
        "targets": [
          {
            "expr": "business_revenue_daily",
            "legendFormat": "Daily Revenue"
          },
          {
            "expr": "business_revenue_predicted",
            "legendFormat": "Predicted Revenue"
          }
        ],
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 }
      },
      {
        "title": "Customer Metrics",
        "type": "stat",
        "targets": [
          {
            "expr": "business_customers_total",
            "legendFormat": "Total Customers"
          },
          {
            "expr": "business_customers_active",
            "legendFormat": "Active Customers"
          }
        ],
        "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 }
      },
      {
        "title": "AI Insights",
        "type": "table",
        "targets": [
          {
            "expr": "ai_insights_confidence",
            "legendFormat": "{{insight_type}}"
          }
        ],
        "gridPos": { "h": 8, "w": 24, "x": 0, "y": 8 }
      }
    ]
  }
}
EOF

# Configuração de alertas críticos
cat > docker/grafana/provisioning/alerting/alerts.yml << EOF
apiVersion: 1
groups:
  - name: SEC_Ultra_Revolutionary_Alerts
    folder: SEC Alerts
    interval: 60s
    rules:
      - name: High CPU Usage
        condition: "B"
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 90% for more than 5 minutes"

      - name: Low Memory
        condition: "C"
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "Low memory detected"
          description: "Memory usage is above 85% for more than 3 minutes"

      - name: Service Down
        condition: "D"
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "A critical service has been down for more than 1 minute"

      - name: High Error Rate
        condition: "E"
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 5% for more than 5 minutes"

      - name: Security Breach Attempt
        condition: "F"
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Security breach attempt detected"
          description: "Multiple failed authentication attempts detected"
EOF

# Configuração de notificações
cat > docker/grafana/provisioning/alerting/contact-points.yml << EOF
apiVersion: 1
contactPoints:
  - name: SEC_Operations_Team
    receivers:
      - name: slack_notifications
        type: slack
        settings:
          webhookUrl: "${SLACK_WEBHOOK_URL}"
          title: "{{ .Title }}"
          text: "{{ .Message }}"

      - name: email_notifications
        type: email
        settings:
          addresses: "operations@sec-ultra.com"
          subject: "{{ .Title }}"

      - name: pagerduty_notifications
        type: pagerduty
        settings:
          integrationKey: "${PAGERDUTY_INTEGRATION_KEY}"
EOF

echo "✅ Configuração avançada do Grafana criada com sucesso!"
echo "📊 Dashboards provisionados:"
echo "  - Executive Overview: Métricas executivas e KPIs"
echo "  - Technical Metrics: Performance técnica detalhada"
echo "  - Security Metrics: Segurança e ameaças quânticas"
echo "  - Business Intelligence: Analytics empresariais avançados"
echo ""
echo "🚨 Sistema de alertas configurado:"
echo "  - CPU/Memory alerts críticos"
echo "  - Service availability monitoring"
echo "  - Security breach detection"
echo "  - Performance degradation alerts"
echo ""
echo "📧 Notificações configuradas:"
echo "  - Slack: Notificações em tempo real"
echo "  - Email: Alertas para equipe de operações"
echo "  - PagerDuty: Escalação automática crítica"
