#!/usr/bin/env python3

import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any

import httpx
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace, propagate
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Initialize tracing
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({"service.name": "larry-service", "service.version": "1.0.0"})
    )
)

tracer = trace.get_tracer(__name__)

# Configure Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Set up propagation
propagate.set_global_textmap(B3MultiFormat())

# Create FastAPI app
app = FastAPI(title="LARRY Service", description="Middle stooge in the chain", version="1.0.0")

# Instrument FastAPI and HTTPX
FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()

# Prometheus metrics
REQUEST_COUNT = Counter(
    'larry_requests_total', 
    'Total number of requests to LARRY service',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'larry_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

CURLY_CALLS_TOTAL = Counter(
    'larry_curly_calls_total',
    'Total number of calls to CURLY service',
    ['status']
)

class ResponseModel:
    def __init__(self, service: str, message: str, trace_id: str, data: str):
        self.service = service
        self.message = message
        self.timestamp = datetime.now().isoformat()
        self.trace_id = trace_id
        self.data = data
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "service": self.service,
            "message": self.message,
            "timestamp": self.timestamp,
            "trace_id": self.trace_id,
            "data": self.data
        }

async def call_curly_service(trace_id: str) -> str:
    """Call CURLY service and return its response data"""
    
    with tracer.start_as_current_span("call-curly-service") as span:
        span.set_attribute("service.name", "curly")
        span.set_attribute("trace.id", trace_id)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get current context and inject into headers
                headers = {}
                propagate.inject(headers)
                
                response = await client.get(
                    "http://localhost:8082/curly",
                    headers=headers
                )
                
                CURLY_CALLS_TOTAL.labels(status=str(response.status_code)).inc()
                
                if response.status_code == 200:
                    curly_response = response.json()
                    span.set_attribute("curly.response", curly_response.get("message", ""))
                    span.set_attribute("curly.data", curly_response.get("data", ""))
                    return curly_response.get("data", "curly-no-data")
                else:
                    span.set_attribute("error", f"HTTP {response.status_code}")
                    CURLY_CALLS_TOTAL.labels(status="error").inc()
                    return "curly-error"
                    
        except Exception as e:
            span.set_attribute("error", str(e))
            CURLY_CALLS_TOTAL.labels(status="error").inc()
            return "curly-connection-error"

@app.get("/larry")
async def larry_handler(request: Request):
    """Main LARRY service endpoint"""
    start_time = time.time()
    
    with tracer.start_as_current_span("larry-handler") as span:
        # Extract trace context from incoming request
        ctx = propagate.extract(dict(request.headers))
        
        trace_id = span.get_span_context().trace_id
        trace_id_hex = format(trace_id, '032x') if trace_id else str(uuid.uuid4())
        
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", str(request.url))
        span.set_attribute("service.name", "larry")
        
        try:
            # Call CURLY service
            curly_data = await call_curly_service(trace_id_hex)
            
            response_data = ResponseModel(
                service="LARRY",
                message="Nyuk nyuk nyuk! Larry here, in the middle!",
                trace_id=trace_id_hex,
                data=f"larry-confused({curly_data})"
            )
            
            # Record metrics
            duration = time.time() - start_time
            REQUEST_DURATION.labels(method=request.method, endpoint="/larry").observe(duration)
            REQUEST_COUNT.labels(method=request.method, endpoint="/larry", status="200").inc()
            
            span.set_attribute("http.response_time", duration)
            span.set_attribute("response.data", response_data.data)
            
            return JSONResponse(content=response_data.to_dict())
            
        except Exception as e:
            span.set_attribute("error", str(e))
            REQUEST_COUNT.labels(method=request.method, endpoint="/larry", status="500").inc()
            raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    with tracer.start_as_current_span("health-check"):
        REQUEST_COUNT.labels(method="GET", endpoint="/health", status="200").inc()
        return {
            "status": "healthy", 
            "service": "LARRY",
            "quote": "I'm trying to think, but nothing happens!"
        }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

if __name__ == "__main__":
    print("LARRY service starting on :8081")
    print("🎭 Nyuk nyuk nyuk! Larry here!")
    print("Endpoints:")
    print("  - GET /larry (main endpoint)")
    print("  - GET /health (health check)")
    print("  - GET /metrics (Prometheus metrics)")
    
    uvicorn.run(app, host="0.0.0.0", port=8081, log_level="info") 