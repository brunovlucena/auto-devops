package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/jaeger"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.17.0"
	"go.opentelemetry.io/otel/trace"
)

var (
	// Prometheus metrics
	requestsTotal = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "moe_requests_total",
			Help: "Total number of requests to MOE service",
		},
		[]string{"method", "endpoint", "status"},
	)

	requestDuration = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "moe_request_duration_seconds",
			Help:    "Request duration in seconds",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"method", "endpoint"},
	)

	larryCallsTotal = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "moe_larry_calls_total",
			Help: "Total number of calls to LARRY service",
		},
		[]string{"status"},
	)

	tracer trace.Tracer
)

type Response struct {
	Service   string    `json:"service"`
	Message   string    `json:"message"`
	Timestamp time.Time `json:"timestamp"`
	TraceID   string    `json:"trace_id"`
	Data      string    `json:"data"`
}

func init() {
	// Register Prometheus metrics
	prometheus.MustRegister(requestsTotal)
	prometheus.MustRegister(requestDuration)
	prometheus.MustRegister(larryCallsTotal)
}

func initTracer() (*sdktrace.TracerProvider, error) {
	// Create Jaeger exporter
	exp, err := jaeger.New(jaeger.WithCollectorEndpoint(jaeger.WithEndpoint("http://localhost:14268/api/traces")))
	if err != nil {
		return nil, err
	}

	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exp),
		sdktrace.WithResource(resource.NewWithAttributes(
			semconv.SchemaURL,
			semconv.ServiceNameKey.String("moe-service"),
			semconv.ServiceVersionKey.String("1.0.0"),
		)),
	)

	otel.SetTracerProvider(tp)
	otel.SetTextMapPropagator(propagation.TraceContext{})

	tracer = tp.Tracer("moe-service")

	return tp, nil
}

func callLarryService(ctx context.Context, traceID string) (string, error) {
	ctx, span := tracer.Start(ctx, "call-larry-service")
	defer span.End()

	span.SetAttributes(
		attribute.String("service.name", "larry"),
		attribute.String("trace.id", traceID),
	)

	client := &http.Client{Timeout: 30 * time.Second}
	req, err := http.NewRequestWithContext(ctx, "GET", "http://localhost:8081/larry", nil)
	if err != nil {
		larryCallsTotal.WithLabelValues("error").Inc()
		span.SetAttributes(attribute.String("error", err.Error()))
		return "", err
	}

	// Inject trace context into headers
	otel.GetTextMapPropagator().Inject(ctx, propagation.HeaderCarrier(req.Header))

	resp, err := client.Do(req)
	if err != nil {
		larryCallsTotal.WithLabelValues("error").Inc()
		span.SetAttributes(attribute.String("error", err.Error()))
		return "", err
	}
	defer resp.Body.Close()

	larryCallsTotal.WithLabelValues(fmt.Sprintf("%d", resp.StatusCode)).Inc()

	var larryResponse Response
	if err := json.NewDecoder(resp.Body).Decode(&larryResponse); err != nil {
		span.SetAttributes(attribute.String("error", err.Error()))
		return "", err
	}

	span.SetAttributes(
		attribute.String("larry.response", larryResponse.Message),
		attribute.String("larry.data", larryResponse.Data),
	)

	return larryResponse.Data, nil
}

func moeHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	ctx := r.Context()

	// Start tracing span
	ctx, span := tracer.Start(ctx, "moe-handler")
	defer span.End()

	traceID := span.SpanContext().TraceID().String()

	span.SetAttributes(
		attribute.String("http.method", r.Method),
		attribute.String("http.url", r.URL.String()),
		attribute.String("service.name", "moe"),
	)

	// Call LARRY service
	larryData, err := callLarryService(ctx, traceID)
	if err != nil {
		log.Printf("Error calling LARRY service: %v", err)
		larryData = "error-calling-larry"
		span.SetAttributes(attribute.String("error", err.Error()))
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		requestsTotal.WithLabelValues(r.Method, "/moe", "500").Inc()
		return
	}

	response := Response{
		Service:   "MOE",
		Message:   "Why, soitenly! Hello from MOE, the leader!",
		Timestamp: time.Now(),
		TraceID:   traceID,
		Data:      fmt.Sprintf("moe-organized(%s)", larryData),
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(response); err != nil {
		span.SetAttributes(attribute.String("error", err.Error()))
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		requestsTotal.WithLabelValues(r.Method, "/moe", "500").Inc()
		return
	}

	// Record metrics with exemplar (trace ID)
	duration := time.Since(start).Seconds()
	requestDuration.WithLabelValues(r.Method, "/moe").Observe(duration)
	requestsTotal.WithLabelValues(r.Method, "/moe", "200").Inc()

	span.SetAttributes(
		attribute.Float64("http.response_time", duration),
		attribute.String("response.data", response.Data),
	)

	log.Printf("MOE: Processed request with trace ID: %s", traceID)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	ctx, span := tracer.Start(r.Context(), "health-check")
	defer span.End()

	response := map[string]string{
		"status":  "healthy",
		"service": "MOE",
		"quote":   "I'm the leader of this outfit!",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)

	requestsTotal.WithLabelValues(r.Method, "/health", "200").Inc()
}

func main() {
	// Initialize tracing
	tp, err := initTracer()
	if err != nil {
		log.Fatal("Failed to initialize tracer:", err)
	}
	defer func() {
		if err := tp.Shutdown(context.Background()); err != nil {
			log.Printf("Error shutting down tracer: %v", err)
		}
	}()

	// Setup HTTP handlers
	http.HandleFunc("/moe", moeHandler)
	http.HandleFunc("/health", healthHandler)
	http.Handle("/metrics", promhttp.Handler())

	log.Println("MOE service starting on :8080")
	log.Println("🎭 Why, soitenly! I'm the leader!")
	log.Println("Endpoints:")
	log.Println("  - GET /moe (main endpoint)")
	log.Println("  - GET /health (health check)")
	log.Println("  - GET /metrics (Prometheus metrics)")

	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal("Server failed to start:", err)
	}
}
