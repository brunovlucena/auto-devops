# 📊 Jamie AI DevOps Copilot - Observability Guide

Welcome to Jamie's comprehensive observability documentation! This guide covers all the monitoring, tracing, and logging capabilities built into Jamie to help you understand and optimize your AI DevOps copilot.

## 🚀 Overview

Jamie comes with enterprise-grade observability features out of the box:

- **📈 Prometheus Metrics** - Custom metrics for AI operations, chat interactions, and system health
- **🔍 Distributed Tracing** - OpenTelemetry-based tracing with Jaeger integration
- **📝 Enhanced Logging** - Structured logging with correlation IDs and multiple output formats
- **📊 Grafana Dashboards** - Pre-built dashboards for monitoring Jamie's performance
- **🚨 Health Checks** - Comprehensive health monitoring and alerting

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Jamie API     │───▶│   Prometheus    │───▶│    Grafana      │
│   (Port 8000)   │    │   (Port 9090)   │    │   (Port 3000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         ▼                                              │
┌─────────────────┐                                     │
│     Jaeger      │◀────────────────────────────────────┘
│   (Port 16686)  │
└─────────────────┘
```

## 📈 Prometheus Metrics

Jamie exposes custom metrics at `/metrics` endpoint in Prometheus format.

### 🌐 API Metrics

```prometheus
# HTTP request metrics
jamie_http_requests_total{method="POST", endpoint="/chat", status_code="200"}
jamie_http_request_duration_seconds{method="POST", endpoint="/chat"}
```

### 🧠 AI Brain Metrics

```prometheus
# AI operation metrics
jamie_ai_requests_total{model="llama3.1", operation="chat", status="success"}
jamie_ai_response_time_seconds{model="llama3.1", operation="chat"}
jamie_ai_tokens_total{model="llama3.1", type="input"}
```

### 💬 Chat Metrics

```prometheus
# Chat interaction metrics
jamie_chat_sessions_active
jamie_chat_messages_total{user_type="user", intent="query"}
jamie_chat_response_quality_score{intent="troubleshoot"}
```

### 🔧 DevOps Metrics

```prometheus
# DevOps operation metrics
jamie_devops_queries_total{tool="kubernetes", operation="status", status="success"}
jamie_cluster_status_checks_total{cluster="production", status="healthy"}
```

### 🗄️ RAG Memory Metrics

```prometheus
# RAG system metrics
jamie_rag_searches_total{category="devops", status="success"}
jamie_rag_documents_stored{category="kubernetes"}
```

### 🏥 System Health Metrics

```prometheus
# System health metrics
jamie_system_health_score{component="ai_brain"}
jamie_errors_total{component="chat_endpoint", error_type="ValueError", severity="error"}
jamie_user_satisfaction_score{interaction_type="troubleshooting"}
```

## 🔍 Distributed Tracing

Jamie uses OpenTelemetry for distributed tracing with automatic instrumentation.

### Configuration

```bash
# Environment variables
JAMIE_TRACING_ENABLED=true
JAMIE_TRACING_ENDPOINT=http://jaeger:14268/api/traces
JAMIE_SERVICE_NAME=jamie-devops-copilot
JAMIE_TRACING_SAMPLE_RATE=1.0
```

### Traced Operations

- **HTTP Requests** - All FastAPI endpoints automatically traced
- **AI Operations** - LLM calls and response generation
- **Database Operations** - MongoDB and Redis operations
- **Chat Interactions** - Complete conversation flows
- **DevOps Queries** - Tool integrations and responses

### Custom Tracing

Use decorators to add tracing to your functions:

```python
from api.observability import trace_endpoint, measure_time

@trace_endpoint("custom_operation")
@measure_time("custom_operation_time")
async def my_function():
    # Your code here
    pass
```

## 📝 Enhanced Logging

Jamie supports multiple logging formats with structured output and correlation tracking.

### Configuration Options

```bash
# Logging configuration
JAMIE_LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
JAMIE_LOG_FORMAT=json                   # json, colored, text
JAMIE_LOG_STRUCTURED=true               # Enable structured logging
JAMIE_LOG_CORRELATION=true              # Enable correlation IDs
JAMIE_LOG_FILE=/var/log/jamie.log       # Optional log file
```

### Log Formats

#### JSON Format (Production)
```json
{
  "timestamp": "2024-01-15 10:30:45.123",
  "level": "INFO",
  "logger": "api.main",
  "function": "chat_endpoint",
  "line": 42,
  "message": "Generated chat response",
  "correlation_id": "abc123ef",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "user_id": "user123",
  "response_length": 256,
  "confidence": 0.95
}
```

#### Colored Format (Development)
```
2024-01-15 10:30:45 | INFO     | api.main:chat_endpoint:42 | Generated chat response
```

### Correlation IDs

Every request gets a unique correlation ID that flows through all related operations:

- Generated automatically or from `x-correlation-id` header
- Included in all log messages
- Linked to distributed traces
- Available in responses via `x-correlation-id` header

## 📊 Grafana Dashboards

Pre-built dashboards available at `http://localhost:3000` (admin/jamie123):

### 🎯 Jamie Overview Dashboard

- **System Health** - Real-time health scores for all components
- **Request Metrics** - HTTP request rates, latencies, and error rates
- **AI Performance** - LLM response times and success rates
- **Chat Analytics** - Session counts, message rates, quality scores
- **RAG Operations** - Memory searches and document storage
- **Error Tracking** - Error rates by component and type

### 📈 Key Panels

1. **🚀 Jamie System Health** - Health scores (0-1) for all components
2. **📊 HTTP Request Rate** - Requests per second by endpoint
3. **⚡ Response Time P95** - 95th percentile response times
4. **🧠 AI Operation Metrics** - AI request rates by model and status
5. **🤖 AI Response Time** - AI response time percentiles
6. **💬 Chat Sessions & Messages** - Active sessions and message rates
7. **📈 Chat Response Quality** - Response quality score distribution
8. **🗄️ RAG Memory Operations** - RAG search rates and document counts
9. **🚨 Error Rate** - Error rates by component and type
10. **🔧 DevOps Operations** - DevOps tool query rates

## 🏥 Health Checks

Jamie provides multiple health check endpoints:

### Basic Health Check
```bash
curl http://localhost:8000/health
```

### AI Status Check
```bash
curl http://localhost:8000/ai/status
```

### Observability Status
```bash
curl http://localhost:8000/observability/status
```

### Metrics Summary
```bash
curl http://localhost:8000/observability/metrics/summary
```

## 🚀 Quick Start

1. **Start the Stack**
   ```bash
   docker-compose up -d
   ```

2. **Access Services**
   - Jamie API: http://localhost:8000
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (admin/jamie123)
   - Jaeger UI: http://localhost:16686

3. **Generate Some Data**
   ```bash
   # Send a chat message
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "How is my cluster doing?", "user_id": "test"}'
   ```

4. **View Metrics**
   - Raw metrics: http://localhost:8000/metrics
   - Grafana dashboard: http://localhost:3000
   - Traces: http://localhost:16686

## 🔧 Configuration

### Environment Variables

```bash
# Core observability
JAMIE_METRICS_ENABLED=true
JAMIE_TRACING_ENABLED=true
JAMIE_LOG_FORMAT=json

# Prometheus metrics
JAMIE_METRICS_PATH=/metrics
JAMIE_METRICS_PORT=9090

# Distributed tracing
JAMIE_TRACING_ENDPOINT=http://jaeger:14268/api/traces
JAMIE_SERVICE_NAME=jamie-devops-copilot
JAMIE_TRACING_SAMPLE_RATE=1.0

# Enhanced logging
JAMIE_LOG_LEVEL=INFO
JAMIE_LOG_CORRELATION=true
JAMIE_LOG_STRUCTURED=true
JAMIE_LOG_FILE=/var/log/jamie.log

# Alerting (optional)
JAMIE_ALERTS_ENABLED=false
JAMIE_SLACK_WEBHOOK_URL=https://hooks.slack.com/...
JAMIE_ERROR_THRESHOLD=10
```

## 📋 Monitoring Checklist

### Daily Monitoring

- [ ] Check system health scores (should be > 0.8)
- [ ] Monitor error rates (should be < 1%)
- [ ] Verify AI response times (should be < 5s)
- [ ] Check active chat sessions

### Weekly Reviews

- [ ] Review response quality trends
- [ ] Analyze popular chat intents
- [ ] Check RAG memory usage
- [ ] Review trace samples for performance issues

### Monthly Analysis

- [ ] Analyze user satisfaction trends
- [ ] Review capacity planning metrics
- [ ] Optimize AI model performance
- [ ] Update alerting thresholds

## 🚨 Alerting Rules

Example Prometheus alerting rules (add to `prometheus.yml`):

```yaml
groups:
  - name: jamie-alerts
    rules:
      - alert: JamieHighErrorRate
        expr: rate(jamie_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Jamie error rate is high"
          
      - alert: JamieAIDown
        expr: jamie_system_health_score{component="ai_brain"} < 0.5
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Jamie AI brain is unhealthy"
```

## 🔍 Troubleshooting

### Common Issues

1. **No Metrics** - Check if metrics are enabled and endpoint is accessible
2. **Missing Traces** - Verify Jaeger is running and tracing is enabled
3. **Log Issues** - Check log format configuration and permissions
4. **Dashboard Empty** - Ensure Prometheus is scraping Jamie metrics

### Debug Commands

```bash
# Check metrics endpoint
curl http://localhost:8000/metrics | grep jamie_

# Check observability status
curl http://localhost:8000/observability/status | jq

# View logs
docker-compose logs jamie

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

## 🎯 Best Practices

1. **Use Correlation IDs** - Always include correlation IDs in custom logs
2. **Monitor Key Metrics** - Focus on error rates, latencies, and health scores
3. **Set Up Alerts** - Configure alerts for critical failures
4. **Regular Reviews** - Weekly review of dashboards and trends
5. **Capacity Planning** - Monitor resource usage for scaling decisions

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Loguru Documentation](https://loguru.readthedocs.io/)

---

*Happy monitoring! 🚀 Jamie's observability features help you keep your AI DevOps copilot running smoothly and efficiently.* 