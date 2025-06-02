# Redis for Session Management

This service deploys Redis v7-alpine using Helm for session management and caching in the platform.

## Overview

Redis is configured as an in-memory data store for session management, caching, and real-time data processing. The deployment uses the Bitnami Redis Helm chart in standalone mode optimized for session storage.

## Configuration

### Redis Details
- **Image**: redis:7-alpine
- **Architecture**: Standalone (no clustering)
- **Authentication**: Disabled (internal cluster use)
- **Persistence**: Enabled

### Resources
- **CPU**: 100m requests, 200m limits
- **Memory**: 128Mi requests, 256Mi limits
- **Storage**: 1Gi persistent volume

### Service
- **Type**: ClusterIP
- **Port**: 6379

## Deployment

### Prerequisites
1. Add Bitnami Helm repository:
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### Install
```bash
cd 20-platform/services/redis/deploy
helm dependency update
helm install redis . --namespace <your-namespace>
```

### Upgrade
```bash
helm upgrade redis . --namespace <your-namespace>
```

### Uninstall
```bash
helm uninstall redis --namespace <your-namespace>
```

## Connection

### From within the cluster
```bash
redis://redis-master:6379
```

### From outside the cluster (port-forward)
```bash
kubectl port-forward svc/redis-master 6379:6379
redis://localhost:6379
```

### Using redis-cli
```bash
# From within cluster
kubectl exec -it <redis-pod> -- redis-cli

# From outside cluster (after port-forward)
redis-cli -h localhost -p 6379
```

## Usage Examples

### Session Storage
```bash
# Set session data
redis-cli SET "session:user123" '{"user_id":"123","name":"John","login_time":"2024-01-01T10:00:00Z"}'

# Get session data
redis-cli GET "session:user123"

# Set with expiration (1 hour)
redis-cli SETEX "session:user456" 3600 '{"user_id":"456","name":"Jane"}'
```

### Caching
```bash
# Cache API response
redis-cli SET "cache:api:/users/123" '{"id":123,"name":"John Doe"}' EX 300

# Check cache
redis-cli GET "cache:api:/users/123"
```

## Performance Tuning

For high-traffic session management, consider:

1. **Increase memory allocation**:
```yaml
redis:
  master:
    resources:
      limits:
        memory: 512Mi
      requests:
        memory: 256Mi
```

2. **Adjust maxmemory policy**:
```yaml
redis:
  commonConfiguration: |-
    maxmemory-policy allkeys-lru
    maxmemory 200mb
```

3. **Enable compression** for large session data:
```yaml
redis:
  commonConfiguration: |-
    rdbcompression yes
```

## Security Considerations

⚠️ **Current Setup**: Authentication is disabled for simplicity in internal cluster communication.

For production deployments, consider:

1. **Enable authentication**:
```yaml
redis:
  auth:
    enabled: true
    password: "your-secure-password"
```

2. **Network policies** to restrict access
3. **TLS encryption** for data in transit
4. **Regular security updates**

## Monitoring and Health Checks

### Check Redis status
```bash
kubectl exec -it <redis-pod> -- redis-cli ping
```

### Monitor memory usage
```bash
kubectl exec -it <redis-pod> -- redis-cli info memory
```

### Check connected clients
```bash
kubectl exec -it <redis-pod> -- redis-cli info clients
```

## Customization

To customize the deployment, edit `values.yaml`:

```yaml
redis:
  # Enable authentication
  auth:
    enabled: true
    password: "your-password"
  
  # Increase storage
  master:
    persistence:
      size: 5Gi
  
  # Add Redis configuration
  commonConfiguration: |-
    maxmemory-policy allkeys-lru
    maxmemory 200mb
    timeout 300
```

## Data Persistence

- **Enabled**: Yes, using 1Gi PVC
- **Storage Class**: Default (can be customized)
- **Backup**: Consider implementing regular Redis snapshots for important session data

## Troubleshooting

### Check pod status
```bash
kubectl get pods -l app.kubernetes.io/name=redis
```

### View logs
```bash
kubectl logs -l app.kubernetes.io/name=redis
```

### Debug connection issues
```bash
# Test connection from another pod
kubectl run redis-test --rm -it --image=redis:7-alpine -- redis-cli -h redis-master -p 6379 ping
```

### Monitor performance
```bash
# Check slow queries
kubectl exec -it <redis-pod> -- redis-cli slowlog get 10

# Monitor operations per second
kubectl exec -it <redis-pod> -- redis-cli --latency-history -i 1
```
