# 🤖 auto-devops
> **Your K8s Development Co-Pilot**

[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

---

## 🎯 **Quick Overview**

**What is this?** An AI agent that helps you manage Kubernetes clusters through intelligent automation.

**Why use it?** Faster incident resolution + Better developer experience + Smart automation

---

## 🚀 **Core Features**

### 🔍 **Jamie Agent**
*Connected to: Prometheus, Loki, Tempo, K8s*

**What it does:**
- 📊 **Log Analysis** → Parse, format, correlate logs
- 📈 **Metrics** → Analyze and predict trends  
- 📄 **Reports** → Generate AWS, K8s, Service reports
- 🔮 **Anomaly Detection** → Spot issues before they happen

### ⚡ **Scalet Agent**

**What it does:**
- 🤖 **Automation** → Routine checks and commands
- 📋 **Reports** → Operational insights
- 🎙️ **Voice Control** → Execute with voice commands

---

## 💡 **Why Choose auto-devops?**

| Benefit | Impact |
|---------|--------|
| ⚡ **Faster MTTR** | Resolve incidents quickly |
| 🧠 **Less Cognitive Load** | Reduce stress during incidents |
| 🔒 **Secure** | Facial recognition for commands |
| 🔧 **Extensible** | Integrates with your tools |

---

## 🛠️ **Quick Start**

### ✅ **Prerequisites**
- [ ] Kubernetes cluster (v1.32+)
- [ ] [kubectl](https://kubernetes.io/docs/tasks/tools/) 
- [ ] [Pulumi](https://www.pulumi.com/docs/install/)
- [ ] [Go](https://golang.org/doc/install) (v1.24+)
- [ ] [ArgoCD CLI](https://argo-cd.readthedocs.io/en/stable/cli_installation/) *(optional)*

### 🚀 **Installation**

**Step 1:** Clone the repo
```bash
git clone https://github.com/brunovlucena/auto-devops.git
cd auto-devops
```

**Step 2:** Bootstrap
```bash
cd 40-bootstrap
pulumi up --stack local
```

**Step 3:** Access dashboard
*URL provided in installation output*

---

## 🏗️ **Architecture**

### **Core Components**
- 🐳 **Kind** → Local K8s
- ☸️ **Kubernetes** → Container orchestration
- 📊 **Observability** → Loki, Tempo, Alloy, Prometheus
- 🧠 **AI/ML** → Opik, MongoDB (Vector DB), Llama 4
- 🔄 **Automation** → Pulumi, ArgoCD, LangGraph
- 🌐 **API** → FastAPI, WebSocket
- 🔗 **Service Mesh** → Linkerd

### **MCP Servers**
- ArgoCD MCP server
- Grafana MCP server  
- GitHub MCP server
- MongoDB MCP server
- Cursor MCP client

---

## 📱 **Mobile App** *(Coming Soon)*

**Features:**
- 🔔 Push notifications for alerts
- 👤 Facial recognition security
- 🎙️ Voice-activated queries  
- 📊 Mobile dashboard

*Download links available in my lifetime 😄*

---

## 🤝 **Contributing**

**Want to help?**

1. 🍴 Fork the repo
2. 🌟 Create feature branch: `git checkout -b feature/amazing-feature`  
3. ✅ Commit: `git commit -m 'Add amazing feature'`
4. 📤 Push: `git push origin feature/amazing-feature`
5. 🔄 Open Pull Request

📖 **More details:** [Contributing Guide](00-docs/CONTRIBUTING.md)

---

## 📞 **Contact & Support**

**Need help?**
- 📧 Email: [bruno@lucena.cloud](mailto:bruno@lucena.cloud)
- 📄 License: [MIT License](LICENSE)

---

**⭐ Star this repo if it helps you!**