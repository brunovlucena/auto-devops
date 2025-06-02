"""
📊 Jamie Observability - Metrics, Tracing, and Enhanced Logging

🎯 PURPOSE: Comprehensive observability for Jamie DevOps Copilot
- Prometheus metrics for monitoring performance and health
- OpenTelemetry distributed tracing for request flow visibility  
- Enhanced structured logging with correlation IDs
- Error alerting and notification capabilities

⭐ WHAT THIS MODULE PROVIDES:
- Custom metrics for AI operations, chat interactions, DevOps queries
- Automatic request tracing with context propagation
- Structured JSON logging with correlation tracking
- Health check metrics and SLA monitoring
- Integration with popular observability stacks (Jaeger, Grafana, etc.)
"""

import logging
import time
import uuid
import json
import asyncio
from contextvars import ContextVar
from typing import Dict, Any, Optional, List
from functools import wraps
from datetime import datetime

# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator

# OpenTelemetry tracing
from opentelemetry import trace, baggage
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource

# Enhanced logging
from loguru import logger
import colorlog
import structlog

from ..config import config

# ═══════════════════════════════════════════════════════════════════════════════
# 🌍 GLOBAL CONTEXT AND STATE
# ═══════════════════════════════════════════════════════════════════════════════

# Context variable for correlation ID tracking
correlation_id_ctx: ContextVar[str] = ContextVar('correlation_id', default=None)

# Global registry for custom metrics
METRICS_REGISTRY = CollectorRegistry()

# Tracer instance
tracer = trace.get_tracer(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# 📈 PROMETHEUS METRICS - Custom metrics for Jamie
# ═══════════════════════════════════════════════════════════════════════════════

class JamieMetrics:
    """
    📊 Custom Prometheus metrics for Jamie DevOps Copilot
    
    METRIC CATEGORIES:
    - API Performance: Request latency, throughput, errors
    - AI Operations: LLM calls, token usage, response quality
    - Chat Interactions: Sessions, messages, user engagement
    - DevOps Queries: Tool calls, cluster status, error rates
    - System Health: Memory usage, AI model availability
    """
    
    def __init__(self, registry: CollectorRegistry = METRICS_REGISTRY):
        """Initialize all custom metrics"""
        
        # 🌐 API METRICS
        self.http_requests_total = Counter(
            'jamie_http_requests_total',
            'Total HTTP requests processed by Jamie',
            ['method', 'endpoint', 'status_code'],
            registry=registry
        )
        
        self.http_request_duration = Histogram(
            'jamie_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            registry=registry
        )
        
        # 🧠 AI BRAIN METRICS
        self.ai_requests_total = Counter(
            'jamie_ai_requests_total',
            'Total AI/LLM requests made by Jamie',
            ['model', 'operation', 'status'],
            registry=registry
        )
        
        self.ai_response_time = Histogram(
            'jamie_ai_response_time_seconds',
            'AI response generation time',
            ['model', 'operation'],
            registry=registry
        )
        
        self.ai_tokens_used = Counter(
            'jamie_ai_tokens_total',
            'Total tokens consumed by AI operations',
            ['model', 'type'],  # type: input/output
            registry=registry
        )
        
        # 💬 CHAT METRICS
        self.chat_sessions_active = Gauge(
            'jamie_chat_sessions_active',
            'Number of active chat sessions',
            registry=registry
        )
        
        self.chat_messages_total = Counter(
            'jamie_chat_messages_total',
            'Total chat messages processed',
            ['user_type', 'intent'],
            registry=registry
        )
        
        self.chat_response_quality = Histogram(
            'jamie_chat_response_quality_score',
            'Quality score of chat responses (0-1)',
            ['intent'],
            registry=registry
        )
        
        # 🔧 DEVOPS METRICS
        self.devops_queries_total = Counter(
            'jamie_devops_queries_total',
            'Total DevOps tool queries',
            ['tool', 'operation', 'status'],
            registry=registry
        )
        
        self.cluster_status_checks = Counter(
            'jamie_cluster_status_checks_total',
            'Total cluster status checks performed',
            ['cluster', 'status'],
            registry=registry
        )
        
        # 🗄️ MEMORY & RAG METRICS
        self.rag_searches_total = Counter(
            'jamie_rag_searches_total',
            'Total RAG memory searches',
            ['category', 'status'],
            registry=registry
        )
        
        self.rag_documents_stored = Gauge(
            'jamie_rag_documents_stored',
            'Number of documents in RAG memory',
            ['category'],
            registry=registry
        )
        
        # 🏥 SYSTEM HEALTH METRICS
        self.system_health = Gauge(
            'jamie_system_health_score',
            'Overall system health score (0-1)',
            ['component'],
            registry=registry
        )
        
        self.errors_total = Counter(
            'jamie_errors_total',
            'Total errors encountered',
            ['component', 'error_type', 'severity'],
            registry=registry
        )
        
        # 📊 BUSINESS METRICS
        self.user_satisfaction = Histogram(
            'jamie_user_satisfaction_score',
            'User satisfaction scores',
            ['interaction_type'],
            registry=registry
        )

# Global metrics instance
jamie_metrics = JamieMetrics()

# ═══════════════════════════════════════════════════════════════════════════════
# 🔍 DISTRIBUTED TRACING - OpenTelemetry setup
# ═══════════════════════════════════════════════════════════════════════════════

class JamieTracing:
    """
    🔍 Distributed tracing setup for Jamie
    
    FEATURES:
    - Automatic FastAPI request tracing
    - Custom spans for AI operations
    - Context propagation across services
    - Integration with Tempo/OTLP collectors
    """
    
    def __init__(self):
        self.initialized = False
        self.instrumentor = None
        
    def initialize(self):
        """Initialize OpenTelemetry tracing"""
        if not config.TRACING_ENABLED or self.initialized:
            return
            
        try:
            # 🏷️ Configure resource information
            resource = Resource.create({
                "service.name": config.TRACING_SERVICE_NAME,
                "service.version": "2.0.0",
                "deployment.environment": "production" if not config.DEBUG else "development"
            })
            
            # 📡 Set up tracer provider
            trace.set_tracer_provider(TracerProvider(resource=resource))
            
            # 🚀 Configure OTLP exporter for Tempo
            exporter = OTLPSpanExporter(
                endpoint=config.TRACING_ENDPOINT,
                insecure=True
            )
            
            # 🔄 Add batch span processor
            span_processor = BatchSpanProcessor(exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
            
            # 🔌 Initialize auto-instrumentation
            HTTPXClientInstrumentor().instrument()
            PymongoInstrumentor().instrument()
            RedisInstrumentor().instrument()
            LoggingInstrumentor().instrument()
            
            self.initialized = True
            logger.info("🔍 Distributed tracing initialized", 
                       service=config.TRACING_SERVICE_NAME,
                       endpoint=config.TRACING_ENDPOINT)
                       
        except Exception as e:
            logger.error(f"Failed to initialize tracing: {e}")
    
    def instrument_fastapi(self, app):
        """Instrument FastAPI application"""
        if not config.TRACING_ENABLED:
            return
            
        try:
            self.instrumentor = FastAPIInstrumentor.instrument_app(
                app,
                tracer_provider=trace.get_tracer_provider(),
                excluded_urls="/health,/metrics"
            )
            logger.info("🚀 FastAPI tracing instrumentation enabled")
        except Exception as e:
            logger.error(f"Failed to instrument FastAPI: {e}")

# Global tracing instance
jamie_tracing = JamieTracing()

# ═══════════════════════════════════════════════════════════════════════════════
# 📝 ENHANCED LOGGING - Structured logging with correlation
# ═══════════════════════════════════════════════════════════════════════════════

class JamieLogger:
    """
    📝 Enhanced logging system for Jamie
    
    FEATURES:
    - Structured JSON logging
    - Correlation ID tracking
    - Multiple output formats (JSON, colored, plain)
    - Integration with distributed tracing
    - Contextual information injection
    """
    
    def __init__(self):
        self.configured = False
        
    def configure(self):
        """Configure enhanced logging system"""
        if self.configured:
            return
            
        try:
            # 🗑️ Remove default loguru handler
            logger.remove()
            
            # 📊 Configure based on format preference
            if config.LOG_FORMAT == "json":
                self._configure_json_logging()
            elif config.LOG_FORMAT == "colored":
                self._configure_colored_logging()
            else:
                self._configure_plain_logging()
            
            # 📁 Add file logging if specified
            if config.LOG_FILE:
                logger.add(
                    config.LOG_FILE,
                    format=self._get_json_format(),
                    level=config.LOG_LEVEL,
                    rotation="100 MB",
                    retention="30 days",
                    compression="gz"
                )
            
            # 🔗 Configure correlation ID injection
            if config.LOG_CORRELATION_ID:
                logger.configure(
                    patcher=self._add_correlation_id
                )
            
            self.configured = True
            logger.info("📝 Enhanced logging configured",
                       format=config.LOG_FORMAT,
                       level=config.LOG_LEVEL,
                       structured=config.LOG_STRUCTURED)
                       
        except Exception as e:
            print(f"Failed to configure logging: {e}")
    
    def _configure_json_logging(self):
        """Configure structured JSON logging"""
        logger.add(
            sink=lambda msg: print(msg, end=''),
            format=self._get_json_format(),
            level=config.LOG_LEVEL,
            serialize=True
        )
    
    def _configure_colored_logging(self):
        """Configure colored console logging"""
        color_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        logger.add(
            sink=lambda msg: print(msg, end=''),
            format=color_format,
            level=config.LOG_LEVEL,
            colorize=True
        )
    
    def _configure_plain_logging(self):
        """Configure plain text logging"""
        plain_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} | {message}"
        )
        
        logger.add(
            sink=lambda msg: print(msg, end=''),
            format=plain_format,
            level=config.LOG_LEVEL
        )
    
    def _get_json_format(self):
        """Get JSON format string for structured logging"""
        return json.dumps({
            "timestamp": "{time:YYYY-MM-DD HH:mm:ss.SSS}",
            "level": "{level}",
            "logger": "{name}",
            "function": "{function}",
            "line": "{line}",
            "message": "{message}",
            "correlation_id": "{extra[correlation_id]}",
            "trace_id": "{extra[trace_id]}",
            "span_id": "{extra[span_id]}"
        })
    
    def _add_correlation_id(self, record):
        """Add correlation ID and tracing info to log records"""
        # Get correlation ID from context
        correlation_id = correlation_id_ctx.get()
        if not correlation_id:
            correlation_id = str(uuid.uuid4())[:8]
            correlation_id_ctx.set(correlation_id)
        
        record["extra"]["correlation_id"] = correlation_id
        
        # Add tracing context if available
        current_span = trace.get_current_span()
        if current_span and current_span.is_recording():
            span_context = current_span.get_span_context()
            record["extra"]["trace_id"] = format(span_context.trace_id, '032x')
            record["extra"]["span_id"] = format(span_context.span_id, '016x')
        else:
            record["extra"]["trace_id"] = ""
            record["extra"]["span_id"] = ""

# Global logger instance
jamie_logger = JamieLogger()

# ═══════════════════════════════════════════════════════════════════════════════
# 🎭 DECORATORS - Easy observability for functions
# ═══════════════════════════════════════════════════════════════════════════════

def trace_endpoint(operation_name: str = None):
    """
    🔍 Decorator to add tracing to functions
    
    Usage:
    @trace_endpoint("ai_chat_response")
    async def generate_response(message: str):
        ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(name) as span:
                # Add function metadata to span
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("function.success", True)
                    return result
                except Exception as e:
                    span.set_attribute("function.success", False)
                    span.set_attribute("function.error", str(e))
                    jamie_metrics.errors_total.labels(
                        component=func.__module__,
                        error_type=type(e).__name__,
                        severity="error"
                    ).inc()
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(name) as span:
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("function.success", True)
                    return result
                except Exception as e:
                    span.set_attribute("function.success", False)
                    span.set_attribute("function.error", str(e))
                    jamie_metrics.errors_total.labels(
                        component=func.__module__,
                        error_type=type(e).__name__,
                        severity="error"
                    ).inc()
                    raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def measure_time(metric_name: str, labels: Dict[str, str] = None):
    """
    ⏱️ Decorator to measure execution time
    
    Usage:
    @measure_time("ai_response_time", {"model": "llama3.1"})
    async def generate_ai_response():
        ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Find the appropriate metric
                metric = getattr(jamie_metrics, metric_name, None)
                if metric and hasattr(metric, 'observe'):
                    if labels:
                        metric.labels(**labels).observe(duration)
                    else:
                        metric.observe(duration)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Function {func.__name__} failed after {duration:.2f}s: {e}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                metric = getattr(jamie_metrics, metric_name, None)
                if metric and hasattr(metric, 'observe'):
                    if labels:
                        metric.labels(**labels).observe(duration)
                    else:
                        metric.observe(duration)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Function {func.__name__} failed after {duration:.2f}s: {e}")
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 INITIALIZATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def initialize_observability():
    """
    🚀 Initialize all observability components
    
    Call this during application startup to set up:
    - Enhanced logging
    - Distributed tracing  
    - Custom metrics
    """
    logger.info("🚀 Initializing Jamie observability...")
    
    # 📝 Configure enhanced logging first
    jamie_logger.configure()
    
    # 🔍 Initialize distributed tracing
    if config.TRACING_ENABLED:
        jamie_tracing.initialize()
    
    # 📊 Metrics are already initialized via global instance
    logger.info("✅ Jamie observability initialized successfully",
               tracing_enabled=config.TRACING_ENABLED,
               metrics_enabled=config.METRICS_ENABLED)

def setup_fastapi_observability(app):
    """
    🔌 Set up FastAPI-specific observability
    
    Args:
        app: FastAPI application instance
    """
    if config.METRICS_ENABLED:
        # 📊 Set up Prometheus metrics endpoint
        instrumentator = Instrumentator()
        instrumentator.instrument(app).expose(app, endpoint=config.METRICS_PATH)
        
        logger.info(f"📊 Metrics endpoint available at {config.METRICS_PATH}")
    
    if config.TRACING_ENABLED:
        # 🔍 Instrument FastAPI for tracing
        jamie_tracing.instrument_fastapi(app)

def get_correlation_id() -> str:
    """Get current correlation ID"""
    correlation_id = correlation_id_ctx.get()
    if not correlation_id:
        correlation_id = str(uuid.uuid4())[:8]
        correlation_id_ctx.set(correlation_id)
    return correlation_id

def set_correlation_id(correlation_id: str):
    """Set correlation ID for current context"""
    correlation_id_ctx.set(correlation_id) 