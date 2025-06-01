const express = require('express');
const promClient = require('prom-client');
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { JaegerExporter } = require('@opentelemetry/exporter-jaeger');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { trace, context } = require('@opentelemetry/api');

// Initialize OpenTelemetry
const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'curly-service',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
  }),
  traceExporter: new JaegerExporter({
    endpoint: 'http://localhost:14268/api/traces',
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();

const app = express();
const PORT = process.env.PORT || 8082;

// Middleware
app.use(express.json());

// Prometheus metrics
const register = new promClient.Register();

const requestsTotal = new promClient.Counter({
  name: 'curly_requests_total',
  help: 'Total number of requests to CURLY service',
  labelNames: ['method', 'endpoint', 'status'],
  registers: [register],
});

const requestDuration = new promClient.Histogram({
  name: 'curly_request_duration_seconds',
  help: 'Request duration in seconds',
  labelNames: ['method', 'endpoint'],
  registers: [register],
});

const processedItems = new promClient.Counter({
  name: 'curly_processed_items_total',
  help: 'Total number of items processed by CURLY service',
  registers: [register],
});

// Business logic simulation
const processData = (inputData) => {
  // Simulate some data processing
  const processed = `curly-woobwoob(${inputData || 'default'})`;
  processedItems.inc();
  return processed;
};

// Curly's famous phrases
const curlyPhrases = [
  "Nyuk nyuk nyuk!",
  "Soitenly!",
  "Woob woob woob!",
  "I'm a victim of soicumstance!",
  "Why I oughta..."
];

const getRandomPhrase = () => {
  return curlyPhrases[Math.floor(Math.random() * curlyPhrases.length)];
};

// Routes
app.get('/curly', (req, res) => {
  const startTime = Date.now();
  
  // Get the current span
  const span = trace.getActiveSpan();
  const traceId = span ? span.spanContext().traceId : 'no-trace';
  
  if (span) {
    span.setAttributes({
      'http.method': req.method,
      'http.url': req.url,
      'service.name': 'curly'
    });
  }

  try {
    // Simulate some processing time
    const processingDelay = Math.random() * 100; // 0-100ms
    
    setTimeout(() => {
      const processedData = processData('raw-data');
      const phrase = getRandomPhrase();
      
      const response = {
        service: 'CURLY',
        message: `${phrase} Curly here, ready to work!`,
        timestamp: new Date().toISOString(),
        trace_id: traceId,
        data: processedData
      };

      // Record metrics
      const duration = (Date.now() - startTime) / 1000;
      requestDuration.labels(req.method, '/curly').observe(duration);
      requestsTotal.labels(req.method, '/curly', '200').inc();

      if (span) {
        span.setAttributes({
          'http.response_time': duration,
          'response.data': processedData,
          'processing.delay': processingDelay,
          'curly.phrase': phrase
        });
      }

      console.log(`CURLY: ${phrase} Processed request with trace ID: ${traceId}`);
      res.json(response);
    }, processingDelay);

  } catch (error) {
    if (span) {
      span.setAttributes({
        'error': error.message
      });
    }
    
    requestsTotal.labels(req.method, '/curly', '500').inc();
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.get('/health', (req, res) => {
  const span = trace.getActiveSpan();
  
  if (span) {
    span.setAttributes({
      'health.check': 'ok'
    });
  }

  requestsTotal.labels(req.method, '/health', '200').inc();
  res.json({ 
    status: 'healthy', 
    service: 'CURLY',
    quote: 'Soitenly! I\'m ready to woik!',
    timestamp: new Date().toISOString()
  });
});

app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  const metrics = await register.metrics();
  res.end(metrics);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  sdk.shutdown().then(() => {
    console.log('OpenTelemetry terminated');
    process.exit(0);
  }).catch((error) => {
    console.log('Error terminating OpenTelemetry', error);
    process.exit(1);
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully');
  sdk.shutdown().then(() => {
    console.log('OpenTelemetry terminated');
    process.exit(0);
  }).catch((error) => {
    console.log('Error terminating OpenTelemetry', error);
    process.exit(1);
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`CURLY service starting on :${PORT}`);
  console.log('🎭 Nyuk nyuk nyuk! Curly here!');
  console.log('Endpoints:');
  console.log('  - GET /curly (main endpoint)');
  console.log('  - GET /health (health check)');
  console.log('  - GET /metrics (Prometheus metrics)');
}); 