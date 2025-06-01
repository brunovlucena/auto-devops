# 🎭 The Three Stooges - Distributed Tracing Demo

A microservices demonstration featuring distributed tracing with 3 services that create a complete trace span across different programming languages, named after the classic comedy trio!

## 🏗️ Architecture

The system consists of 3 microservices that create a chain of requests:

**MOE** → **LARRY** → **CURLY**

- **MOE Service** (Go) - Port 8080 🎯
  - The leader of the outfit
  - Written in Golang
  - Exports Prometheus metrics
  - Generates traces with OpenTelemetry
  - Uses Prometheus exemplars
  - Calls LARRY service
  - *"Why, soitenly! I'm the leader!"*

- **LARRY Service** (Python) - Port 8081 🥴
  - The confused middle guy
  - FastAPI-based API service
  - Propagates traces from MOE
  - Generates its own trace spans
  - Uses Prometheus exemplars
  - Calls CURLY service
  - *"Nyuk nyuk nyuk! I'm trying to think, but nothing happens!"*

- **CURLY Service** (Node.js) - Port 8082 🤪
  - The wild card who gets things done
  - Express.js application
  - Final service in the chain
  - Completes the distributed trace
  - Returns processed data
  - *"Soitenly! Nyuk nyuk nyuk!"*

## 🎯 Trace Flow

When you call MOE, you get a trace ID with 3 spans showing the complete journey:

1. **moe-handler** span (MOE service) - The leader organizes
2. **larry-handler** span (LARRY service) - The middle man gets confused
3. **curly-handler** span (CURLY service) - The wild card delivers

Each service adds its own processing and forwards the trace context with their unique personalities!

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Go 1.21+ (for local development)
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)

### Running with Docker Compose

```bash
# Start all services with observability stack
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

This will start:
- ✅ MOE service (port 8080) - The Leader
- ✅ LARRY service (port 8081) - The Middle Guy
- ✅ CURLY service (port 8082) - The Wild Card
- ✅ Jaeger UI (port 16686)
- ✅ Prometheus (port 9090)
- ✅ Grafana (port 3000)

### Testing the Services

```bash
# Call the main endpoint to generate traces
curl http://localhost:8080/moe

# Expected response:
{
  "service": "MOE",
  "message": "Why, soitenly! Hello from MOE, the leader!",
  "timestamp": "2024-01-15T10:30:00Z",
  "trace_id": "1234567890abcdef",
  "data": "moe-organized(larry-confused(curly-woobwoob(raw-data)))"
}
```

### Check Health

```bash
curl http://localhost:8080/health  # MOE - "I'm the leader of this outfit!"
curl http://localhost:8081/health  # LARRY - "I'm trying to think, but nothing happens!"
curl http://localhost:8082/health  # CURLY - "Soitenly! I'm ready to woik!"
```

## 📊 Observability

### Jaeger Tracing
- **URL**: http://localhost:16686
- View distributed traces across all services
- See span relationships and timing
- Analyze performance bottlenecks
- Watch the Stooges work together!

### Prometheus Metrics  
- **URL**: http://localhost:9090
- Custom metrics from each service:
  - Request counters with exemplars
  - Duration histograms
  - Service-specific business metrics

### Grafana Dashboards
- **URL**: http://localhost:3000
- **Login**: admin/admin
- Visualize metrics and traces correlation
- Pre-configured dashboards for each service

## 🛠️ Local Development

### MOE Service (Go)

```bash
cd moe/
go mod tidy
go run main.go
```

### LARRY Service (Python)

```bash
cd larry/
pip install -r requirements.txt
python main.py
```

### CURLY Service (Node.js)

```bash
cd curly/
npm install
npm start
```

## 📈 Metrics Available

### MOE Service Metrics
- `moe_requests_total` - Total requests with labels
- `moe_request_duration_seconds` - Request duration histogram
- `moe_larry_calls_total` - Calls to LARRY service

### LARRY Service Metrics
- `larry_requests_total` - Total requests with labels
- `larry_request_duration_seconds` - Request duration histogram  
- `larry_curly_calls_total` - Calls to CURLY service

### CURLY Service Metrics
- `curly_requests_total` - Total requests with labels
- `curly_request_duration_seconds` - Request duration histogram
- `curly_processed_items_total` - Items processed counter

## 🔍 Example Queries

### Prometheus Queries

```promql
# Request rate across all stooges
sum(rate(moe_requests_total[5m])) + sum(rate(larry_requests_total[5m])) + sum(rate(curly_requests_total[5m]))

# 95th percentile latency for MOE (the leader)
histogram_quantile(0.95, rate(moe_request_duration_seconds_bucket[5m]))

# Error rate across the whole gang
sum(rate(moe_requests_total{status!="200"}[5m])) / sum(rate(moe_requests_total[5m]))
```

### Generating Load

```bash
# Generate some load for testing the stooges
for i in {1..100}; do
  curl -s http://localhost:8080/moe > /dev/null
  sleep 0.1
done
```

## 🏗️ Project Structure

```
stooges/
├── moe/                     # Go service - The Leader
│   ├── main.go
│   ├── go.mod
│   └── Dockerfile
├── larry/                   # Python service - The Middle Guy
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── curly/                   # Node.js service - The Wild Card
│   ├── app.js
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml       # Full stack setup
├── prometheus.yml          # Prometheus config
└── README.md              # This file
```

## 🎛️ Configuration

### Service Ports
- MOE: 8080 (The Leader)
- LARRY: 8081 (The Middle Guy)
- CURLY: 8082 (The Wild Card)

### Observability Ports
- Jaeger UI: 16686
- Prometheus: 9090
- Grafana: 3000

### Environment Variables

**MOE Service:**
- `JAEGER_ENDPOINT` - Jaeger collector endpoint
- `LARRY_SERVICE_URL` - LARRY service URL

**LARRY Service:**
- `JAEGER_AGENT_HOST` - Jaeger agent host
- `JAEGER_AGENT_PORT` - Jaeger agent port  
- `CURLY_SERVICE_URL` - CURLY service URL

**CURLY Service:**
- `JAEGER_ENDPOINT` - Jaeger collector endpoint
- `PORT` - Service port (default 8082)

## 🔧 Troubleshooting

### Common Issues

1. **Services not connecting**
   - Check Docker network connectivity
   - Verify service URLs in environment variables
   - Make sure the stooges are talking to each other!

2. **Traces not appearing**  
   - Ensure Jaeger is running and accessible
   - Check service logs for OpenTelemetry errors
   - MOE might not be leading properly

3. **Metrics not scraped**
   - Verify Prometheus configuration
   - Check `/metrics` endpoints are accessible
   - CURLY might be causing chaos

### Logs

```bash
# View service logs
docker-compose logs moe-service
docker-compose logs larry-service  
docker-compose logs curly-service

# View all logs
docker-compose logs -f
```

## 🎭 The Stooges' Personalities

### MOE (The Leader)
- **Personality**: Bossy, organized, tries to keep order
- **Quotes**: "Why, soitenly!", "I'm the leader of this outfit!"
- **Role**: Initiates requests, organizes the workflow

### LARRY (The Middle Guy)
- **Personality**: Confused, tries to help but often makes things worse
- **Quotes**: "Nyuk nyuk nyuk!", "I'm trying to think, but nothing happens!"
- **Role**: Processes requests, gets confused but passes things along

### CURLY (The Wild Card)
- **Personality**: Energetic, chaotic, but somehow gets the job done
- **Quotes**: "Soitenly!", "Woob woob woob!", "Nyuk nyuk nyuk!"
- **Role**: Final processor, delivers results with flair

## 🚀 Next Steps

- Add more complex business logic
- Implement error scenarios for testing (classic stooge mishaps!)
- Add database interactions
- Create custom Grafana dashboards with stooge themes
- Implement chaos engineering scenarios (perfect for the stooges!)
- Add performance testing scripts
- Create stooge-themed error pages

## 📝 License

MIT License - Feel free to use and modify as needed.

---

🎭 **The Three Stooges**: Demonstrating distributed tracing, metrics, and observability across polyglot microservices with classic comedy flair!

*"Nyuk nyuk nyuk! Soitenly the best way to learn about distributed systems!"*
