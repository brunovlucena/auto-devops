# 🎭 Three Stooges Helm Charts

Complete Helm charts for deploying the Three Stooges microservices demo to Kubernetes.

## 📋 Overview

The Three Stooges consists of three microservices that demonstrate distributed tracing, metrics collection, and service communication:

- **🎯 MOE** (Go) - Port 8080 - The Leader
- **🥴 LARRY** (Python) - Port 8081 - The Middle Guy  
- **🤪 CURLY** (Node.js) - Port 8082 - The Wild Card

## 🚀 Quick Deployment

### Deploy All Services

```bash
# Deploy MOE (The Leader)
helm install moe ./moe/deploy \
  --namespace stooges \
  --create-namespace

# Deploy LARRY (The Middle Guy)
helm install larry ./larry/deploy \
  --namespace stooges

# Deploy CURLY (The Wild Card)
helm install curly ./curly/deploy \
  --namespace stooges
```

### Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n stooges

# Check services
kubectl get svc -n stooges

# Check service monitors (if Prometheus operator is installed)
kubectl get servicemonitor -n stooges
```

## 🔧 Configuration

### MOE Service Configuration

```yaml
# moe-values.yaml
replicaCount: 2

image:
  repository: your-registry/moe-service
  tag: "v1.0.0"

service:
  type: LoadBalancer  # Expose MOE externally

ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: moe.example.com
      paths:
        - path: /
          pathType: Prefix

env:
  - name: LARRY_SERVICE_URL
    value: "http://larry-service:8081"
  - name: JAEGER_ENDPOINT
    value: "http://jaeger-collector:14268/api/traces"

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 200m
    memory: 256Mi
```

### LARRY Service Configuration

```yaml
# larry-values.yaml
replicaCount: 2

image:
  repository: your-registry/larry-service
  tag: "v1.0.0"

env:
  - name: CURLY_SERVICE_URL
    value: "http://curly-service:8082"
  - name: JAEGER_ENDPOINT
    value: "http://jaeger-collector:14268/api/traces"

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

### CURLY Service Configuration

```yaml
# curly-values.yaml
replicaCount: 3  # Scale the wild card

image:
  repository: your-registry/curly-service
  tag: "v1.0.0"

env:
  - name: JAEGER_ENDPOINT
    value: "http://jaeger-collector:14268/api/traces"

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

## 🎯 Advanced Deployment

### With Custom Values

```bash
# Deploy with custom configuration
helm install moe ./moe/deploy \
  --namespace stooges \
  --create-namespace \
  --values moe-values.yaml

helm install larry ./larry/deploy \
  --namespace stooges \
  --values larry-values.yaml

helm install curly ./curly/deploy \
  --namespace stooges \
  --values curly-values.yaml
```

### With Ingress Enabled

```bash
# Enable ingress for external access
helm install moe ./moe/deploy \
  --namespace stooges \
  --create-namespace \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=moe.local \
  --set ingress.hosts[0].paths[0].path=/ \
  --set ingress.hosts[0].paths[0].pathType=Prefix
```

### Production Deployment

```bash
# Production-ready deployment with scaling and resources
helm install moe ./moe/deploy \
  --namespace stooges-prod \
  --create-namespace \
  --set replicaCount=3 \
  --set resources.limits.cpu=1000m \
  --set resources.limits.memory=1Gi \
  --set resources.requests.cpu=200m \
  --set resources.requests.memory=256Mi \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10
```

## 📊 Monitoring & Observability

### Prometheus Integration

All services include ServiceMonitor resources for Prometheus scraping:

```yaml
serviceMonitor:
  enabled: true
  interval: 30s
  path: /metrics
  labels:
    team: stooges
    environment: production
```

### Available Metrics

**MOE Service:**
- `moe_requests_total` - Total requests
- `moe_request_duration_seconds` - Request duration
- `moe_larry_calls_total` - Calls to LARRY service

**LARRY Service:**
- `larry_requests_total` - Total requests  
- `larry_request_duration_seconds` - Request duration
- `larry_curly_calls_total` - Calls to CURLY service

**CURLY Service:**
- `curly_requests_total` - Total requests
- `curly_request_duration_seconds` - Request duration
- `curly_processed_items_total` - Items processed

### Jaeger Tracing

Configure distributed tracing by setting the Jaeger endpoint:

```yaml
env:
  - name: JAEGER_ENDPOINT
    value: "http://jaeger-collector.observability:14268/api/traces"
```

## 🔄 Service Communication

The services communicate in a chain:

```
External Request → MOE → LARRY → CURLY
                   ↓      ↓       ↓
                Response ← Response ← Response
```

### Service URLs

Configure service communication:

```yaml
# MOE configuration
env:
  - name: LARRY_SERVICE_URL
    value: "http://larry-service.stooges:8081"

# LARRY configuration  
env:
  - name: CURLY_SERVICE_URL
    value: "http://curly-service.stooges:8082"
```

## 🛠️ Development & Testing

### Local Development

```bash
# Port forward for local testing
kubectl port-forward svc/moe-service 8080:8080 -n stooges &
kubectl port-forward svc/larry-service 8081:8081 -n stooges &
kubectl port-forward svc/curly-service 8082:8082 -n stooges &

# Test the chain
curl http://localhost:8080/moe
```

### Health Checks

```bash
# Check service health
curl http://localhost:8080/health  # MOE
curl http://localhost:8081/health  # LARRY  
curl http://localhost:8082/health  # CURLY
```

### Load Testing

```bash
# Generate load for testing
for i in {1..100}; do
  curl -s http://localhost:8080/moe > /dev/null
  sleep 0.1
done
```

## 🔧 Troubleshooting

### Common Issues

1. **Services can't communicate:**
   ```bash
   # Check service discovery
   kubectl get svc -n stooges
   kubectl get endpoints -n stooges
   ```

2. **Pods not starting:**
   ```bash
   # Check pod logs
   kubectl logs -l app.kubernetes.io/name=moe-service -n stooges
   kubectl logs -l app.kubernetes.io/name=larry-service -n stooges
   kubectl logs -l app.kubernetes.io/name=curly-service -n stooges
   ```

3. **Metrics not appearing:**
   ```bash
   # Check ServiceMonitor
   kubectl get servicemonitor -n stooges
   
   # Check Prometheus targets
   kubectl port-forward svc/prometheus-server 9090:80 -n monitoring
   # Visit http://localhost:9090/targets
   ```

### Debug Commands

```bash
# Get all resources
kubectl get all -n stooges

# Describe problematic pods
kubectl describe pod <pod-name> -n stooges

# Check events
kubectl get events -n stooges --sort-by='.lastTimestamp'

# Test service connectivity
kubectl run debug --image=busybox -it --rm --restart=Never -- sh
# Inside the pod:
# wget -qO- http://moe-service.stooges:8080/health
```

## 🚀 Upgrade & Rollback

### Upgrade Services

```bash
# Upgrade with new image
helm upgrade moe ./moe/deploy \
  --namespace stooges \
  --set image.tag=v2.0.0

# Upgrade with new values
helm upgrade larry ./larry/deploy \
  --namespace stooges \
  --values larry-values-v2.yaml
```

### Rollback

```bash
# Check release history
helm history moe -n stooges

# Rollback to previous version
helm rollback moe 1 -n stooges
```

## 🧹 Cleanup

```bash
# Uninstall all services
helm uninstall moe -n stooges
helm uninstall larry -n stooges  
helm uninstall curly -n stooges

# Delete namespace
kubectl delete namespace stooges
```

## 📚 Chart Values Reference

### Common Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Image repository | `<service>-service` |
| `image.tag` | Image tag | `""` (uses appVersion) |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | Service-specific |
| `ingress.enabled` | Enable ingress | `false` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `128Mi` |
| `autoscaling.enabled` | Enable HPA | `false` |
| `serviceMonitor.enabled` | Enable Prometheus monitoring | `true` |
| `healthCheck.enabled` | Enable health checks | `true` |

---

**🎭 "Why, soitenly! Now you can deploy the Three Stooges with style!"** - MOE, LARRY & CURLY 