# MongoDB for RAG Storage

This service deploys MongoDB v7 using Helm for RAG (Retrieval-Augmented Generation) storage in the platform.

## Overview

MongoDB is configured as a document database to store and retrieve vector embeddings and related data for RAG applications. The deployment uses the Bitnami MongoDB Helm chart with custom configurations optimized for RAG workloads.

## Configuration

### Database Details
- **Image**: mongo:7
- **Database**: jamie_rag
- **Username**: jamie
- **Password**: jamie_pass (⚠️ Change for production)

### Resources
- **CPU**: 250m requests, 500m limits
- **Memory**: 512Mi requests, 1Gi limits
- **Storage**: 5Gi persistent volume

### Service
- **Type**: ClusterIP
- **Port**: 27017

## Deployment

### Prerequisites
1. Add Bitnami Helm repository:
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### Install
```bash
cd 20-platform/services/mongodb/deploy
helm dependency update
helm install mongodb . --namespace <your-namespace>
```

### Upgrade
```bash
helm upgrade mongodb . --namespace <your-namespace>
```

### Uninstall
```bash
helm uninstall mongodb --namespace <your-namespace>
```

## Connection

### From within the cluster
```bash
mongodb://jamie:jamie_pass@mongodb:27017/jamie_rag
```

### From outside the cluster (port-forward)
```bash
kubectl port-forward svc/mongodb 27017:27017
mongodb://jamie:jamie_pass@localhost:27017/jamie_rag
```

## Security Considerations

⚠️ **Important**: This configuration uses hardcoded credentials suitable for development/testing. For production deployments:

1. Use Kubernetes secrets for credentials
2. Enable TLS encryption
3. Configure network policies
4. Use strong passwords
5. Consider MongoDB authentication mechanisms

## Customization

To customize the deployment, edit `values.yaml`:

```yaml
mongodb:
  auth:
    rootPassword: "your-secure-password"
    databases:
      - your_database_name
  persistence:
    size: 10Gi  # Increase storage
  resources:
    limits:
      cpu: 1000m  # Increase CPU
      memory: 2Gi # Increase memory
```

## Monitoring

The deployment includes standard Kubernetes labels for monitoring integration. MongoDB metrics can be exposed using the official MongoDB exporter if needed.

## Troubleshooting

### Check pod status
```bash
kubectl get pods -l app.kubernetes.io/name=mongodb
```

### View logs
```bash
kubectl logs -l app.kubernetes.io/name=mongodb
```

### Connect to MongoDB shell
```bash
kubectl exec -it <mongodb-pod> -- mongosh mongodb://jamie:jamie_pass@localhost:27017/jamie_rag
```
