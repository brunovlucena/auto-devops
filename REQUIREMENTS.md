# 📋 auto-devops Requirements

> **Complete hardware, software, and infrastructure requirements for deploying auto-devops with AI agents Jamie & Scarlet**

[![Kubernetes](https://img.shields.io/badge/kubernetes-v1.32+-blue.svg)]()
[![Go](https://img.shields.io/badge/go-v1.24+-00ADD8.svg)]()
[![Pulumi](https://img.shields.io/badge/pulumi-latest-blueviolet.svg)]()
[![Kamaji](https://img.shields.io/badge/kamaji-latest-orange.svg)]()
[![AI Agents](https://img.shields.io/badge/ai-jamie%20%26%20scarlet-purple.svg)]()

---

## 🎯 **Overview**

This document outlines the complete requirements for deploying the auto-devops Kubernetes management platform with integrated AI agents **Jamie** (British DevOps Copilot) and **Scarlet** (Advanced AI Agent), including development (laptop), production (server), and multi-cluster Kamaji environments.

**New in this version**: AI/ML requirements for LLM inference, vector databases, and intelligent automation agents.

---

## 💻 **Hardware Requirements**

### 🖥️ **Laptop Workstation (Development)**

#### **Minimum Configuration** *(Basic Jamie + local development)*
| Component | Specification | Purpose |
|-----------|---------------|---------|
| **CPU** | 12 cores (Intel i7/AMD Ryzen 7) | Kind cluster + Llama inference |
| **RAM** | 64GB | Container workloads + 8B LLM model |
| **Storage** | 1TB NVMe SSD | Container images + AI models + data |
| **GPU** | Integrated or RTX 4060 | Optional: faster LLM inference |
| **Network** | Gigabit Ethernet/Wi-Fi 6 | Cluster communication + model downloads |

#### **Recommended Configuration** *(Full AI stack + Jamie + Scarlet)*
| Component | Specification | Purpose |
|-----------|---------------|---------|
| **CPU** | 16+ cores (Intel i9/AMD Ryzen 9) | Multi-agent AI workloads |
| **RAM** | 128GB | Full stack + multiple AI models |
| **Storage** | 2TB+ NVMe SSD | Extended model storage + vectors |
| **GPU** | RTX 4080/4090 | Fast LLM inference + fine-tuning |
| **Network** | Gigabit Ethernet/Wi-Fi 6E | High-throughput AI telemetry |

### 🖥️ **Single Server (Production)**

#### **Minimum Configuration** *(Basic production + Jamie)*
| Component | Specification | Purpose |
|-----------|---------------|---------|
| **CPU** | 24 cores @ 2.4GHz+ | Multi-replica + AI inference |
| **RAM** | 128GB ECC | Production workloads + AI models |
| **Storage** | 2TB NVMe SSD + 4TB HDD | Fast AI access + archival |
| **GPU** | RTX 4070/4080 (Required) | LLM inference acceleration |
| **Network** | 10Gbps | High-volume telemetry + AI data |

#### **Recommended Configuration** *(Full AI stack + Jamie + Scarlet)*
| Component | Specification | Purpose |
|-----------|---------------|---------|
| **CPU** | 48+ cores @ 2.8GHz+ | Multi-agent AI + auto-scaling |
| **RAM** | 256GB+ ECC | Full AI/ML stack + caching |
| **Storage** | 4TB NVMe SSD + 8TB NVMe/SSD | High-performance AI storage |
| **GPU** | RTX 4090/A100/H100 (Required) | Enterprise AI acceleration |
| **Network** | 25Gbps+ | Enterprise telemetry + AI |

### 🏗️ **Kamaji Multi-Cluster Setup with AI** *(Enhanced)*

#### **Management Cluster Server**
| Component | Specification | Purpose |
|-----------|---------------|---------|
| **CPU** | 64+ cores @ 3.0GHz+ | Control planes + central AI brain |
| **RAM** | 512GB+ ECC | Control planes + shared AI models |
| **Storage** | 8TB NVMe SSD + 16TB NVMe/SSD | High IOPS + AI model storage |
| **GPU** | 2x RTX 4090/A100 | Centralized AI inference cluster |
| **Network** | 50Gbps+ with redundancy | AI model distribution |

#### **AI-Enhanced Worker Nodes** *(per tenant cluster)*
| Component | Minimum | Recommended | Purpose |
|-----------|---------|-------------|---------|
| **CPU** | 24 cores @ 2.4GHz+ | 48+ cores @ 2.8GHz+ | Tenant workloads + edge AI |
| **RAM** | 128GB ECC | 256GB+ ECC | Apps + local AI agents |
| **Storage** | 2TB NVMe SSD | 4TB+ NVMe SSD | Pod storage + AI cache |
| **GPU** | RTX 4060/4070 | RTX 4080/4090 | Local AI inference |
| **Network** | 25Gbps | 50Gbps | AI model sync + telemetry |

---

## 🔧 **Software Prerequisites**

### **Required Tools**
```bash
# Core Infrastructure
✅ Kubernetes v1.32+
✅ kubectl (latest)
✅ Kind (for local development)
✅ Docker/Podman

# Infrastructure as Code
✅ Pulumi (latest)
✅ Go v1.24+

# AI/ML Stack (NEW)
✅ Ollama (LLM serving)
✅ Python 3.11+
✅ FastAPI v0.104+
✅ LangChain v0.1+
✅ LangGraph v0.1+
✅ MongoDB 7.0+ (Vector Search)
✅ sentence-transformers
✅ Opik (LLM observability)

# Multi-Cluster Management
✅ Kamaji (latest)
✅ Konnectivity (for network isolation)

# Integration APIs
✅ Slack Bot API
✅ ArgoCD CLI
✅ Grafana API
✅ GitHub API

# Optional but Recommended
✅ Helm v3.12+
✅ Linkerd CLI
✅ Cluster API (for Kamaji integration)
```

### **Python Dependencies for AI Agents**
```bash
# Core AI stack
pip install fastapi uvicorn motor asyncio
pip install langchain langgraph langsmith
pip install sentence-transformers torch
pip install openai anthropic ollama-python
pip install opik-python

# Slack integration
pip install slack-bolt slack-sdk

# Monitoring & observability
pip install prometheus-client structlog
pip install pydantic pydantic-settings

# Development tools
pip install pytest pytest-asyncio black isort
```

### **Operating System Support**
- **Linux:** Ubuntu 22.04+, RHEL 9+, Rocky Linux 9+ *(Recommended for AI workloads)*
- **macOS:** 13.0+ with Apple Silicon M2+ *(Good for development)*
- **Windows:** WSL2 with Ubuntu 22.04+ *(Development only)*

---

## ☸️ **Kubernetes Cluster Requirements**

### **Development (Kind)**
```yaml
Cluster Configuration:
  Control Plane: 1 node
  Worker Nodes: 4 nodes  # Increased for AI workloads
  Node Resources: 8GB RAM, 4 CPU each  # Increased
  Storage Classes: local-path
  Networking: Kind default CNI
  
AI Namespace:
  - jamie-dev: DevOps copilot
  - scarlet-dev: AI agent workflows
  - ai-models: Shared model storage
```

### **Production (Single Cluster)**
```yaml
Cluster Configuration:
  Control Plane: 3 nodes (HA)
  Worker Nodes: 8+ nodes  # Increased for AI workloads
  Node Resources: 32GB+ RAM, 8+ CPU each  # Increased
  Storage Classes: SSD/NVMe backed, GPU-optimized
  Networking: Cilium/Calico recommended
  Load Balancer: MetalLB/Cloud LB
  
AI Configuration:
  GPU Operator: NVIDIA GPU support
  Node Affinity: AI workloads on GPU nodes
  Resource Quotas: Prevent AI workload resource exhaustion
```

### **Kamaji Multi-Cluster with AI** *(Enhanced)*
```yaml
Management Cluster:
  Control Plane: 3 nodes (HA)
  Worker Nodes: 12+ nodes  # Increased
  Node Resources: 64GB+ RAM, 16+ CPU each  # Increased
  Purpose: Host tenant control planes + central AI
  
AI Management Services:
  - Centralized model serving
  - Cross-cluster AI coordination
  - Shared knowledge base
  - AI observability stack
  
Tenant Clusters (per cluster):
  Control Plane: Hosted as pods in management cluster
  Worker Nodes: 6+ dedicated nodes  # Increased
  Node Resources: 32GB+ RAM, 8+ CPU each  # Increased
  Local AI: Edge Jamie agents per cluster
```

---

## 🗄️ **Storage Requirements**

### **📊 Data Retention & Sizing** *(Updated for AI)*

#### **AI/ML Components**
| Component | Purpose | Storage Size | Growth Rate | Type |
|-----------|---------|--------------|-------------|------|
| **Llama 4 Models** | AI inference | 8-16GB per model | Static | NVMe |
| **MongoDB Vector DB** | Embeddings & memory | 100GB-1TB | 5-20GB/week | SSD |
| **Conversation History** | Jamie/Scarlet memory | 50-200GB | 2-10GB/week | SSD |
| **Fine-tuning Data** | Custom model training | 100GB-500GB | Variable | NVMe |
| **Opik Traces** | LLM observability | 20-100GB | 1-5GB/day | SSD |
| **Model Cache** | Inference optimization | 50-200GB | Dynamic | NVMe |

#### **Traditional Observability Stack**
| Component | Retention | Storage Size | Growth Rate |
|-----------|-----------|--------------|-------------|
| **Prometheus** | 15-30 days | 100-500GB | 5-20GB/day |
| **Loki** | 7-14 days | 50-200GB | 2-10GB/day |
| **Tempo** | 2-7 days | 20-100GB | 1-5GB/day |
| **Grafana** | N/A | 10GB | Static |

### **📁 Storage Classes Required**
```yaml
Development:
  - local-path (Kind default)
  - hostpath (for testing)
  - gpu-local (GPU node storage)

Production:
  - ai-fast (NVMe for AI models and inference)
  - ai-vector (SSD for vector databases)
  - fast-ssd (NVMe/SSD for databases)
  - standard (SSD for applications)
  - archival (slower storage for long-term retention)
```

---

## 🌐 **Network Requirements**

### **Bandwidth** *(Updated for AI workloads)*
- **Development:** 1Gbps+ internet (model downloads), Gigabit internal
- **Production:** 5Gbps+ internet (AI model updates), 25Gbps+ internal
- **Kamaji Multi-Cluster:** 10Gbps+ internet, 100Gbps+ internal

### **Ports & Connectivity**
```yaml
External Access:
  - 443/tcp: HTTPS (Grafana, ArgoCD, Slack webhooks)
  - 80/tcp: HTTP (redirects)
  - 8080/tcp: Alternative HTTP
  - 6443/tcp: Kubernetes API (per tenant)
  - 8132/tcp: Konnectivity proxy
  - 11434/tcp: Ollama API (development only)

AI/ML Services:
  - 8000/tcp: FastAPI (Jamie/Scarlet APIs)
  - 8001/tcp: Jamie WebSocket
  - 8002/tcp: Scarlet Agent API
  - 27017/tcp: MongoDB (internal)
  - 6379/tcp: Redis (internal)
  - 5432/tcp: PostgreSQL (Opik)

Internal Cluster:
  - 9090/tcp: Prometheus
  - 9093/tcp: Alertmanager
  - 3100/tcp: Loki
  - 3200/tcp: Tempo
  - 4317/tcp: OTLP gRPC
  - 4318/tcp: OTLP HTTP
  - 2379-2380/tcp: etcd (management cluster)
  - 8191/tcp: Konnectivity agent
```

### **AI-Specific Networking**
- **Model Distribution**: High-bandwidth channels for distributing AI models
- **Real-time Inference**: Low-latency connections for AI API calls  
- **Slack Integration**: Reliable webhooks for chat interfaces
- **Cross-Cluster AI**: Secure channels for multi-tenant AI coordination

---

## 🤖 **AI/ML Requirements** *(Detailed)*

### **Hardware for AI Components**

#### **Jamie (DevOps Copilot)**
```yaml
Minimum Requirements:
  CPU: 4-8 cores
  Memory: 16-32GB
  GPU: 4-8GB VRAM (RTX 4060+)
  Storage: 100GB NVMe

Recommended:
  CPU: 8-16 cores
  Memory: 32-64GB
  GPU: 12-24GB VRAM (RTX 4080+)
  Storage: 200GB NVMe
```

#### **Scarlet (Advanced AI Agent)**
```yaml
Minimum Requirements:
  CPU: 8-16 cores
  Memory: 32-64GB
  GPU: 8-16GB VRAM (RTX 4070+)
  Storage: 200GB NVMe

Recommended:
  CPU: 16-32 cores
  Memory: 64-128GB
  GPU: 16-48GB VRAM (RTX 4090/A100)
  Storage: 500GB NVMe
```

#### **MongoDB Vector Database**
```yaml
Configuration:
  CPU: 4-8 cores
  Memory: 16-32GB
  Storage: 500GB-2TB SSD
  IOPS: 10,000+ (for vector operations)
  Network: Low-latency for vector search

Atlas Vector Search Features:
  - Automatic indexing
  - Similarity search
  - Hybrid search (vector + text)
  - Real-time updates
```

### **Model Requirements**

#### **Llama 4 Models**
```yaml
Model Variants:
  - llama3.1:8b (8GB VRAM) - Jamie development
  - llama3.1:70b (40GB VRAM) - Scarlet production
  - llama3.1:8b-instruct (8GB VRAM) - Instruction following
  - custom-jamie-8b (8GB VRAM) - Fine-tuned personality

Serving Infrastructure:
  - Ollama: Local development and small production
  - vLLM: High-performance production serving
  - TensorRT-LLM: Optimized NVIDIA GPU serving
```

#### **Embedding Models**
```yaml
sentence-transformers models:
  - all-MiniLM-L6-v2 (22MB) - Fast, general purpose
  - all-mpnet-base-v2 (420MB) - High quality
  - multi-qa-mpnet-base-dot-v1 (420MB) - Q&A optimized

Custom embeddings:
  - kubernetes-docs-v1 - Fine-tuned on K8s docs
  - devops-troubleshooting-v1 - Domain-specific
```

---

## 📱 **Slack Integration Requirements**

### **Slack App Configuration**
```yaml
OAuth Scopes:
  - chat:write: Send messages as Jamie
  - channels:read: Access channel information
  - groups:read: Access private channel info
  - im:read: Access direct message info
  - users:read: Get user information
  - files:write: Upload logs/charts
  - commands: Handle slash commands

Event Subscriptions:
  - message.channels: Monitor channel messages
  - message.groups: Monitor private channels
  - message.im: Monitor direct messages
  - app_mention: Respond to @jamie mentions

Interactive Components:
  - Buttons: Quick actions (restart, deploy, etc.)
  - Dropdowns: Select namespaces, applications
  - Modals: Complex forms and confirmations
```

### **Bot Capabilities**
- **Natural Language**: Understand DevOps queries in plain English
- **Context Awareness**: Remember conversation history
- **Proactive Alerts**: Send notifications for critical issues
- **Interactive UI**: Buttons and forms for complex operations
- **File Sharing**: Upload logs, charts, and reports

---

## 🔍 **Monitoring & Observability** *(AI-Enhanced)*

### **AI-Specific Monitoring**

#### **LLM Observability (Opik)**
```yaml
Metrics Tracked:
  - Token usage and costs
  - Response latency and quality
  - Model performance metrics
  - Conversation success rates
  - Fine-tuning effectiveness

Dashboards:
  - Jamie conversation analytics
  - Scarlet decision tracking
  - Model performance trends
  - Cost optimization insights
```

#### **AI Agent Health Checks**
- **Model Availability**: LLM endpoint health
- **Response Quality**: Automated evaluation scores
- **Memory Systems**: Vector database performance
- **Integration Health**: Slack, ArgoCD, Grafana connectivity
- **Resource Usage**: GPU utilization, memory consumption

### **Enhanced Alerting Thresholds**
```yaml
Critical (AI-specific):
  - LLM response time > 10 seconds
  - Model API failure rate > 5%
  - Vector search latency > 1 second
  - Jamie/Scarlet agent crash loops
  - Slack webhook failures

Warning (AI-specific):
  - LLM response time > 5 seconds
  - High GPU memory usage > 90%
  - Vector database storage > 80%
  - Conversation success rate < 85%
  - Model evaluation score decline
```

---

## 📚 **Additional AI Resources**

### **Documentation**
- [Ollama Documentation](https://ollama.ai/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [MongoDB Vector Search](https://www.mongodb.com/docs/atlas/atlas-vector-search/)
- [Slack Bot API](https://api.slack.com/bot-users)
- [Opik Documentation](https://opik.comet.com/docs/)

### **Community & Support**
- [LangChain Discord](https://discord.gg/langchain)
- [Ollama GitHub](https://github.com/ollama/ollama)
- [MongoDB Community Forums](https://www.mongodb.com/community/forums/)
- [Slack Developers Community](https://api.slack.com/community)

---

## 🔧 **Resource Allocation by Environment** *(Updated)*

### **Development Environment**
```yaml
Total Resource Budget:
  CPU: 16 cores
  Memory: 128GB
  Storage: 2TB
  GPU: RTX 4080 (16GB VRAM)
  
Component Allocation:
  Kubernetes Base: 4 cores, 16GB, 100GB
  Observability: 3 cores, 16GB, 300GB
  AI Stack (Jamie): 6 cores, 64GB, 500GB
  AI Models & Cache: 2 cores, 16GB, 800GB
  Service Mesh: 0.5 cores, 4GB, 50GB
  System Overhead: 0.5 cores, 12GB, 250GB
```

### **Production Environment (Single Cluster)**
```yaml
Total Resource Budget:
  CPU: 48+ cores
  Memory: 256GB+
  Storage: 4TB+
  GPU: RTX 4090 or A100 (24-48GB VRAM)
  
Component Allocation:
  Kubernetes Base: 8 cores, 32GB, 200GB
  Observability: 12 cores, 64GB, 1.5TB
  AI Stack (Jamie + Scarlet): 20 cores, 128GB, 1.5TB
  AI Models & Vector DB: 8 cores, 64GB, 1TB
  Service Mesh: 4 cores, 16GB, 100GB
  System Overhead: 4 cores, 16GB, 200GB
```

### **Kamaji Multi-Cluster with AI** *(Enhanced)*
```yaml
Management Cluster + Central AI:
  CPU: 64+ cores
  Memory: 512GB+
  Storage: 8TB+
  GPU: 2x RTX 4090 or A100
  
Allocation:
  Kubernetes Base: 12 cores, 64GB, 400GB
  Kamaji Operator: 8 cores, 32GB, 200GB
  Tenant Control Planes: 24 cores, 256GB, 3TB
  Central AI (Scarlet): 16 cores, 128GB, 2TB
  Shared Observability: 12 cores, 64GB, 1.5TB
  System Overhead: 8 cores, 32GB, 400GB

Per-Tenant Cluster with Local AI:
  CPU: 48+ cores
  Memory: 256GB+
  Storage: 4TB+
  GPU: RTX 4080 (16GB VRAM)
  
Allocation:
  Application Workloads: 32 cores, 192GB, 2.5TB
  Local Jamie Agent: 8 cores, 32GB, 500GB
  Local Observability: 4 cores, 16GB, 500GB
  Service Mesh: 2 cores, 8GB, 200GB
  System Overhead: 2 cores, 8GB, 300GB
```

---

**📝 Note:** AI/ML requirements significantly increase resource needs. GPU acceleration is highly recommended for production deployments. Consider starting with smaller models (8B parameters) and scaling up based on performance requirements.

**⚠️ Important:** The addition of Jamie and Scarlet AI agents transforms this from a traditional DevOps platform into an intelligent, AI-powered system. Plan for additional complexity in deployment, monitoring, and maintenance, but expect significant improvements in operational efficiency and user experience. 