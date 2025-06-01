# 🏗️ System Architecture

## 🎯 **Overview**

Auto-DevOps implements a **dual-agent architecture** where two AI agents work together to provide complete DevOps automation:

- **Jamie** 🤖: Human-computer interface layer
- **Scarlet** 🔴: Autonomous operations layer

---

## 🧩 **Core Architecture**

```
┌─────────────────┬─────────────────┐
│   Human Layer   │  Automation     │
│                 │  Layer          │
├─────────────────┼─────────────────┤
│  🤖 Jamie       │  🔴 Scarlet     │
│  Chat Portal    │  Background     │
│  Slack Bot      │  Monitoring     │
│  Q&A Interface  │  Auto-Fixes     │
└─────────────────┴─────────────────┘
           │           │
           ▼           ▼
┌─────────────────────────────────────┐
│      🔌 MCP Integration Layer       │
│  (Model Context Protocol)           │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│     🛠️ DevOps Infrastructure       │
│  K8s │ Prometheus │ Loki │ Tempo    │
└─────────────────────────────────────┘
```

---

## 🤖 **Jamie Architecture**

### **Core Components**
```yaml
🧠 AI Brain:
  - LLM Engine: Ollama + Llama 4 (local)
  - Memory: MongoDB Vector Search
  - Personality: British DevOps mate
  - Context: Conversation history + tool results

💬 Interfaces:
  - Web Portal: Next.js chat interface
  - Slack Bot: Team collaboration
  - API: RESTful + WebSocket endpoints

🔌 Tool Integration:
  - MCP Client: Orchestrates tool calls
  - Real-time Data: Live infrastructure queries
  - Knowledge Base: DevOps best practices
```

### **Jamie's Data Flow**
```
User Question → Context Retrieval → Tool Selection → 
MCP Execution → Response Generation → Personality Layer → User
```

### **Jamie's MCP Tools**
- **Kubernetes MCP**: Pod status, deployments, scaling
- **Prometheus MCP**: Metrics, alerts, performance data  
- **Loki MCP**: Log streaming, error analysis
- **Tempo MCP**: Trace analysis, performance bottlenecks
- **GitHub MCP**: Repository data, deployment correlation

---

## 🔴 **Scarlet Architecture**

### **Core Components**
```yaml
🧠 Autonomous Engine:
  - Agent Framework: LangGraph state machines
  - Decision Engine: Multi-factor analysis
  - Learning System: Pattern recognition + adaptation
  - Action Library: Safe automation procedures

📊 Sensing Layer:
  - Metrics: Prometheus + custom collectors
  - Logs: Loki + structured log analysis
  - Events: Kubernetes + webhook integrations
  - Traces: Tempo + performance monitoring

⚡ Action Layer:
  - Safe Actions: Immediate execution (restart pods)
  - Approval Actions: Require human confirmation
  - Escalation: Complex issues → human operators
```

### **Scarlet's Decision Matrix**
```
High Confidence + Low Risk → ⚡ Immediate Action
Medium Confidence/Risk → ⏳ Seek Approval  
Low Confidence + High Risk → 🚨 Escalate
```

### **Scarlet's Learning Loop**
```
Monitor → Detect → Analyze → Decide → Act → Learn → Improve
```

---

## 🔌 **MCP Integration Layer**

**What is MCP?**
- **Model Context Protocol**: Standardized way for AI to use tools
- **Real-time Data**: Live infrastructure access for both agents
- **Unified Interface**: Same tools for Jamie (reactive) and Scarlet (proactive)

### **MCP Server Architecture**
```yaml
Kubernetes MCP Server:
  - Endpoint: cluster.local:8001
  - Capabilities: CRUD operations, status queries
  - Auth: Service account + RBAC

Prometheus MCP Server:
  - Endpoint: prometheus:9090
  - Capabilities: PromQL queries, alert status
  - Data: Metrics, time series, alerting rules

Loki MCP Server:
  - Endpoint: loki:3100  
  - Capabilities: LogQL queries, streaming
  - Data: Application + system logs

Tempo MCP Server:
  - Endpoint: tempo:3200
  - Capabilities: Trace queries, span analysis
  - Data: Distributed traces, performance data

GitHub MCP Server:
  - Endpoint: api.github.com
  - Capabilities: Repository data, PR/issue tracking
  - Data: Code changes, deployment correlation
```

---

## 🗄️ **Data Architecture**

### **Jamie's Data Stores**
```yaml
MongoDB (Conversations):
  - User sessions and preferences
  - Conversation history with vector embeddings
  - Context retrieval for follow-up questions
  - Learning from user feedback

Redis (Cache):
  - MCP response caching
  - Session management
  - Real-time data buffering
```

### **Scarlet's Data Stores**
```yaml
PostgreSQL (Operations):
  - Action history and outcomes
  - Decision patterns and confidence scores
  - Learning data and performance metrics
  - Audit trails for compliance

TimescaleDB (Metrics):
  - High-frequency monitoring data
  - Pattern analysis for predictions
  - Performance trends and baselines
```

---

## 🚦 **Security Architecture**

### **Authentication & Authorization**
```yaml
Jamie (Human Access):
  - Web Portal: JWT tokens + session management
  - Slack: OAuth 2.0 + workspace verification
  - API Access: API keys + rate limiting

Scarlet (System Access):
  - Kubernetes: Service accounts + RBAC
  - Monitoring: Service-to-service auth
  - Actions: Graduated permissions by confidence
```

### **Security Boundaries**
```yaml
Network Isolation:
  - Jamie: User-facing, DMZ deployment
  - Scarlet: Internal cluster, restricted access
  - MCP: Service mesh with mTLS

Data Protection:
  - Encryption: At rest and in transit
  - Secrets: Kubernetes secrets + rotation
  - Audit: All actions logged and traceable
```

---

## 🔄 **Deployment Architecture**

### **Environment Strategy**
```yaml
Development:
  - Local: Docker Compose for quick testing
  - Minikube: Full K8s simulation
  - Mock Data: Synthetic metrics and logs

Staging:
  - K8s Cluster: Production-like environment  
  - Real Data: Staging infrastructure monitoring
  - Safety: Limited action permissions

Production:
  - Multi-AZ: High availability deployment
  - Full Permissions: Complete automation capabilities
  - Monitoring: Comprehensive observability
```

### **GitOps Integration**
```yaml
Configuration:
  - ArgoCD: Declarative deployments
  - Helm Charts: Parameterized configurations
  - Git: Source of truth for all configs

CI/CD Pipeline:
  - Build: Docker images + testing
  - Test: Automated validation + integration tests
  - Deploy: Staged rollouts with canary deployments
```

---

## 📊 **Monitoring & Observability**

### **System Health**
```yaml
Jamie Health:
  - Response Time: Query processing latency
  - Accuracy: Response quality metrics
  - Usage: Active users and question types
  - Satisfaction: User feedback scores

Scarlet Health:
  - Detection Rate: Issues found vs missed
  - Resolution Time: Auto-fix speed
  - Success Rate: Actions completed successfully
  - Learning Progress: Pattern discovery metrics
```

### **Infrastructure Monitoring**
```yaml
Application Metrics:
  - Performance: Response times, throughput
  - Errors: Exception rates, failure modes
  - Resources: CPU, memory, disk usage

Business Metrics:
  - Automation Rate: Manual vs automatic actions
  - Time Savings: Developer productivity gains
  - Cost Impact: Infrastructure optimization
  - Reliability: Uptime improvements
```

---

## 🔮 **Future Architecture**

### **Planned Enhancements**
```yaml
Multi-Cluster:
  - Federated Scarlet: Cross-cluster coordination
  - Global Jamie: Unified interface across regions
  - Disaster Recovery: Automated failover

Advanced AI:
  - Custom Models: Fine-tuned for specific environments
  - Federated Learning: Knowledge sharing between deployments
  - Predictive Analytics: ML-powered capacity planning

Integration Expansion:
  - Cloud Providers: AWS, GCP, Azure native tools
  - Security Tools: SIEM, vulnerability scanners
  - Business Tools: Jira, ServiceNow, PagerDuty
```

---

## 🎯 **Design Principles**

### **Core Values**
- **🔒 Safety First**: Multiple validation layers before actions
- **🧠 Learn Constantly**: Every interaction improves the system
- **👥 Human-Centric**: AI augments humans, doesn't replace them
- **📈 Scale Gradually**: Start small, expand capabilities over time
- **🔍 Transparency**: All decisions and actions are auditable

---

**Architecture in Action**: Jamie answers your questions using real data, while Scarlet silently keeps everything running smoothly. 🚀
